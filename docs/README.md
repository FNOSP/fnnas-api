# fnOS Web API 文档

> 本文档用于记录 fnOS Web 的 WebSocket 和 HTTP通信协议与各功能模块接口。

## 概述

- 通信方式：WebSocket HTTP
- 地址示例：`ws://{你的飞牛地址}/websocket?type=main`
- 鉴权方式：Token + 签名
- 响应匹配：通过 `reqid` 对应请求与响应

## 模块一览
- [通信协议说明](protocol.md)
- [鉴权模块](modules/auth.md)
- [系统信息](modules/sysinfo.md)
- [用户管理](modules/user.md)
- [存储空间](modules/stor.md)
- [文件管理](modules/file.md)
