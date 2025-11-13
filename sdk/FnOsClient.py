from abc import ABC, abstractmethod
import websockets
import json
import logging
import signal
from typing import Optional, List
import asyncio
from .exceptions import WebSocketConnectionError
from .handlers import *
from .utils import *
from .encryption import login_encrypt, get_signature_req, get_signature


class BaseClient(ABC):
    def __init__(self, ping_interval=30, logger=None):
        self.websocket = None
        self.handlers = {}
        self.pending_requests = {}
        self.req_mapping = {}
        self.ping_interval = ping_interval

        self._listen_task = None
        self._ping_task = None
        self.__url = None

        # 下面数据自动初始化
        self.sign_key = None
        self.key = generate_random_string(32)
        self.iv = os.urandom(16)

        # 网站数据, 不用赋值，自动赋值
        self.si = None
        self.pub = None
        # 以下登录返回
        self.backId = '0000000000000000'
        self.token = None
        self.secret = None
        self.uid = None
        self.admin = None

        # 设置日志
        if not logger:
            self.logger = logging.getLogger(self.__class__.__name__)
            self.logger.setLevel(logging.DEBUG)
            handler = logging.StreamHandler()
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
        else:
            self.logger = logger

        # 确保日志被正确传播
        # self.logger.propagate = True

    @property
    async def connected(self):
        """检查连接是否活跃"""
        if self.websocket is None or self.websocket.closed:
            return False
        try:
            # 快速发送 Ping 测试
            await asyncio.wait_for(self.websocket.ping(), timeout=2)
            return True
        except (websockets.ConnectionClosed, asyncio.TimeoutError):
            return False

    @abstractmethod
    async def _init(self, *args, **kwargs):
        "传递给connect方法的参数，会全部传递给_init方法"
        raise NotImplementedError("子类必须实现 _init 方法")

    async def connect(self, url: str = None, *args, **kwargs):
        if url is not None:
            self.__url = url
        try:
            # 坑 服务器不会响应ping，他是使用消息进行ping测活， 所以关闭框架的自动ping
            self.websocket = await websockets.connect(self.__url, ping_interval=None)
            # 创建监听任务
            self._listen_task = asyncio.create_task(self._listen())
            # 创建心跳任务
            self._ping_task = asyncio.create_task(self._ping_loop())

            # 初始化， 继承的类实现
            await self._init(*args, **kwargs)
        except websockets.WebSocketException as e:
            raise WebSocketConnectionError(f"Failed to connect: {str(e)}")

    async def _listen(self):
        while True:
            try:
                message = await self.websocket.recv()
                data = json.loads(message)
                self.logger.debug(f"Received: {message}")
                if 'reqid' in data:
                    reqid = data['reqid']
                    # 返回响应
                    if reqid in self.pending_requests:
                        handler = self.pending_requests.pop(reqid)
                        handler(data)
                    # TODO：尝试使用默认处理器抛出错误
                    # 检查错误放在这里，放在前面request一直卡
                    # check_response(data)
                    # 处理响应
                    if reqid in self.req_mapping:
                        req_type = self.req_mapping.pop(reqid)
                        handler = self.handlers.get(req_type, HandlerDefault)
                        await handler(self, data)
                else:
                    pass
                    # 处理没有reqid的消息
                    # self.logger.info(f"Received message without reqid: {data}")
            except asyncio.CancelledError:
                break
            except websockets.ConnectionClosed as e:
                self.logger.exception(e)
                self.logger.debug(f"Websocket connection closed")
                break
            # 如果不except Exception程序会停止吗？？  会 但是主进程不会抛出错误 卡死
            except Exception as e:
                self.logger.exception(e)
        self.logger.debug(f"_listen end...")

    async def _ping_loop(self):
        while True:
            try:
                await self.send_ping()
                await asyncio.sleep(self.ping_interval)
            except asyncio.CancelledError:
                break
            except websockets.ConnectionClosedError:
                await self.connect()
                # if not await self.connected:  self.logger.error(f"Error in ping loop: {str(e)}")
                break
            except Exception as e:
                self.logger.exception(e)
        self.logger.debug(f"_ping_loop end...")

    async def send_ping(self):
        try:
            await self.websocket.send(json.dumps({"req": "ping"}))
            self.logger.debug("Sent ping to server")
        except Exception as e:
            self.logger.error(f"Failed to send ping: {str(e)}")
            raise

    async def send_request(self, req, **kwargs):
        reqid = get_reqid(self.backId)
        data = {'req': req, 'reqid': reqid, **kwargs}
        if req in ['user.login', 'user.add']:
            # 加密
            data = json.dumps(data, separators=(',', ':'))
            data = login_encrypt(data, self.pub, self.key, self.iv)

        # 签名
        message = get_signature_req(data, self.sign_key)

        await self.websocket.send(message)
        self.req_mapping[reqid] = req
        self.logger.debug(f"Sent: {req} {message}")
        return reqid

    def add_handler(self, req, handler):
        self.handlers[req] = handler

    async def request(self, req, **kwargs):
        reqid = await self.send_request(req, **kwargs)
        future = asyncio.Future()
        self.pending_requests[reqid] = lambda data: future.set_result(data)
        return await future

    async def close(self, timeout: float = 5.0):
        """关闭连接并取消所有任务"""
        tasks = []
        if self._ping_task:
            self._ping_task.cancel()
            tasks.append(self._ping_task)
        if self._listen_task:
            self._listen_task.cancel()
            tasks.append(self._listen_task)
        self.logger.info("Connection closed.")

    def run_polling(
        self,
        *,
        stop_signals: Optional[List[int]] = None,
        close_timeout: float = 5.0,
    ):
        """
        同步方法：启动事件循环并运行 WebSocket 监听，直到收到停止信号。
        用法：
            client = BaseClient(url)
            client.run_polling()  # 阻塞直到 Ctrl+C
        """
        if stop_signals is None:
            stop_signals = [signal.SIGINT, signal.SIGTERM]  # 默认监听 Ctrl+C 和 kill

        # 定义异步主逻辑
        async def _async_main():
            await self.connect()
            stop_event = asyncio.Event()
            # 注册信号处理器
            loop = asyncio.get_running_loop()
            for sig in stop_signals:
                loop.add_signal_handler(sig, stop_event.set)

            self.logger.info("Client started. Press Ctrl+C to stop...")
            await stop_event.wait()  # 阻塞直到收到信号
            await self.close(timeout=close_timeout)

        # 启动事件循环
        try:
            asyncio.run(_async_main())
        except KeyboardInterrupt:
            self.logger.info("User interrupted, shutting down...")
        finally:
            self.logger.info("Client stopped.")


class MainClient(BaseClient):
    async def _init(self):
        await super()._init()
        # 这里注册回调函数，如果要给MainClient加处理请求，在这里加
        self.add_handler('util.crypto.getRSAPub', HandlerGetRSAPub)
        self.add_handler('user.login', HandlerLogin)
        # 连接后执行的方法
        await self.request(req='util.crypto.getRSAPub')

    async def login(self, username, password, *, deviceType='Browser', deviceName='Windows-Google Chrome',
                    stay=False):
        data = {
            "user": username,
            "password": password,
            "deviceType": deviceType,
            "deviceName": deviceName,
            "stay": stay,
            "si": self.si
        }
        response = await self.request('user.login', **data)
        return response

    async def user_info(self):
        response = await self.request('user.info')
        return response

    async def setting_port(self, force_https=False, redirect=True, http_port=5666, https_port=5667):
        "修改端口"
        data = {
            "data": {
                "force_https": force_https,  # 强制Https
                "redirect": redirect,  # 80和443跳转
                "schema": {
                    "http": {
                        "port": http_port
                    },
                    "https": {
                        "port": https_port
                    }
                }
            }
        }
        response = await self.request('appcgi.network.gw.setting', **data)
        return response

    async def get_user_storage(self):
        "获取磁盘信息"
        data = {
            "quotaInfo": True,
            "spaceInfo": True,
            "storInfo": True
        }
        response = await self.request("stor.getUserStorage", **data)
        return response


class FileClient(BaseClient):
    async def _init(self):
        await super()._init()
        self.add_handler('util.getSI', HandlerGetSI)
        self.add_handler('user.authToken', HandlerAuthToken)
        # self.add_handler('file.ls', HandlerFileList)
        self.file_update_queue = asyncio.Queue()

        # 创建更新文件的任务
        update_file_task = asyncio.create_task(self._update_file())

    async def getSI(self):
        await self.request(req='util.getSI')

    async def authToken(self):
        await self.getSI()
        data = {
            "si": self.si,
            "token": self.token,
        }
        await self.request(req='user.authToken', **data)

    async def fileList(self, path=None):
        data = {
            "path": path,
        }
        return await self.request(req='file.ls', **data)

    async def upload(self, local_path, nas_path, overwrite=2):
        """
        :param local_path: 本地文件路径（绝对或相对路径）
        :param nas_path:  NAS文件绝对路径
        :param overwrite: 0跳过 1上传并覆盖 2保留两者
        :return:
        """
        from pathlib import Path
        nas_path = Path(nas_path)
        folder = nas_path.parent.as_posix()
        file_name = nas_path.name
        # 获取修改时间
        mtim = str(get_mtime(local_path))
        # checkUpload
        res = await self._checkUpload(local_path, nas_path.as_posix(), overwrite)
        uploadName = res.get('uploadName')

        url = 'http://172.22.182.150:5666/upload'
        headers = {
            'Referer': 'http://172.22.182.150:5666/p/assets/upload.worker-CPfLJtMs.js',
            'Trim-Overwrite': str(overwrite),
            'Trim-Token': self.token,
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36',
            'Accept': 'application/json, text/plain, */*',
            'Trim-Mtim': mtim,
            'Trim-Path': f'{folder}/{uploadName}',
            # 'origin': 'http://192.168.1.4:5666',
            # 'referer': 'http://192.168.1.4:5666/',
        }
        headers['Trim-Sign'] = get_signature(headers['Trim-Path'], self.sign_key)
        import requests
        import mimetypes
        mime_type, encoding = mimetypes.guess_type(local_path)
        files = {
            "trim-upload-file": (file_name, open(local_path, 'rb'), mime_type)
        }
        res = requests.post(url=url, headers=headers, files=files)
        print(res.status_code, file_name)

    async def download(self):
        # http://192.168.1.4:5666/multiple-download?token=90855a94e419e9cc0c751479ca933411
        pass

    async def _checkUpload(self, local_path, nas_path, overwrite=2):
        size = os.path.getsize(local_path)
        data = {
            "size": size,
            "path": nas_path,
            "overwrite": overwrite,  # 重写规则   0跳过 1上传并覆盖 2保留两者
        }
        res = await self.request(req='file.checkUpload', **data)
        return res

    async def _update_file(self):
        "这是一个内部方法，用来更新文件，服务于start_observer"
        while True:
            # 这里要使用异步方法get，阻塞到get数据为止
            local_path, nas_path, action = await self.file_update_queue.get()
            print(local_path, nas_path, action)
            if action == 'u':
                await self.upload(local_path, nas_path, overwrite=1)
            elif action == 'd':
                await self.download()

    async def start_observer(self, nas_path=None, local_path=os.getcwd(), recursive=False, interval=5,
                             exclude: list = None):
        """
        启动文件变化监听， 原理是对比NAS和本地的修改时间谁更新
        :param nas_path: NAS路径 默认我的文件路径
        :param local_path: 本地路径 默认程序工作路径
        :param interval: 每次轮询间隔时间 5
        :param recursive: 是否递归 默认False
        :param exclude: 排除指定后缀
        :return: None
        """
        if exclude is None:
            exclude = []
        while True:
            res = await self.fileList(path=nas_path)
            nas_files = res.get('files', [])
            nas_dict = {file['name']: file['mtim'] for file in nas_files}
            local_files = {}
            local_path_dict = {}
            # 扫描本地文件 TODO: 使用文件变化监听可能是更好的实践，拥有更好的性能，如开源项目Watchdog，但会增加项目复杂度
            for name, file_path, mtime in list_files(local_path, recursive=recursive):
                # TODO 排除指定后缀
                if name in exclude:
                    continue
                local_files[name] = mtime
                local_path_dict[name] = file_path
            # 迭代NAS文件，检查新增、对比那端有更新
            # TODO: 实现文件实际更新 上传已实现
            # 思路： 创建一个异步队列，把需要更新的操作put到队列，写一个异步任务来执行实际的文件更新
            # 分析: 实际上就一个上传和一个下载， 上传已经实现
            #   操作1：下载到本地
            #   操作2：上传到NAS
            # TODO: 上传：递归文件路径不对 下载： NAS不能递归
            # 上传解决思路：替换路径，nas路径最终路径=本地目录去掉根目录部分
            # 问题1， NAS不能显示所有子目录
            # 解决思路1 如果是递归， 给self.fileList加递归参数，一次性返回所有路径, 考虑使用生成器返回
            for name, nas_mtim in nas_dict.items():
                if name in local_files:
                    local_mtim = local_files[name]
                    if nas_mtim > local_mtim:
                        # NAS文件较新，更新本地文件
                        print(f"文件 '{name}' 在NAS上较新，更新到本地。")
                        # 不知道用put还是put_nowait, AI说没区别，强迫症好难选
                        # 看了代码，put最后调用put_nowait，使用put_nowait
                        self.file_update_queue.put_nowait((local_path_dict[name], f'{nas_path}/{name}', 'd'))
                    elif nas_mtim < local_mtim:
                        # 本地文件较新，更新NAS文件
                        print(f"文件 '{name}' 在本地较新，更新到NAS。")
                        print(name, nas_mtim, local_mtim)
                        self.file_update_queue.put_nowait((local_path_dict[name], f'{nas_path}/{name}', 'u'))
                else:
                    # 本地不存在该文件，将其从NAS复制到本地
                    print(f"本地不存在文件 '{name}'，从NAS复制到本地。")
                    self.file_update_queue.put_nowait((f'{local_path}/{name}', f'{nas_path}/{name}', 'd'))

            for name in local_files.keys():
                if name not in nas_dict:
                    # NAS不存在该文件，将其从本地复制到NAS
                    print(f"NAS不存在文件 '{name}'，从本地复制到NAS。")
                    self.file_update_queue.put_nowait((local_path_dict[name], f'{nas_path}/{name}', 'u'))
            await asyncio.sleep(interval)

    async def file_search(self, key: str, path: list):
        data = {
            "key": key,
            "path": path,
        }
        res = await self.request("appcgi.finder.fileSearch", **data)
        return res

class EmptyClient(BaseClient):
    async def _init(self):
        pass


class FnOsClient(FileClient, MainClient, EmptyClient):
    """
    这里有个坑， 以后增加客户端， 请在EmptyClient前面继承
    如果在EmptyClient后面继承，就会调用BaseClient的_init
    导致抛出NotImplementedError异常，这不是我们想要的结果
    所以写了一个EmptyClient, 让它不调用BaseClient的_init
    此时的MRO是FnOsClient=>MainClient=>FileClient=>EmptyClient=>BaseClient ...
    由于EmptyClient没有调用super()._init() 所以不会调用到BaseClient的_init
    """

    async def _init(self):
        await super()._init()
