# 存储空间

## 获取用户存储空间信息

 - req：stor.getUserStorage
 - 需要登录：是
 - 需要签名：是

 **请求示例**

 ```json
 {sign}{"reqid":"reqid","spaceInfo":true,"storInfo":true,"quotaInfo":true,"req":"stor.getUserStorage"}
 ```

 **响应示例**

 ```json
{
    "stor": [
        {
            "id": 1,
            "comment": "",
            "frsize": 31636586496,
            "fssize": 31642714112,
            "level": "basic",
            "fstype": "btrfs",
            "diskType": "HDD",
            "quotaCurr": 16384,
            "quotaMax": -1
        }
    ],
    "uid": 1000,
    "result": "succ",
    "reqid": "reqid"
}
 ```

## 设置用户存储空间

**请求示例**

```json
{"reqid":"reqid","set":[{"uid":1004,"stor":[{"id":1,"quota":-1}]}],"req":"stor.setUserStorage"}
```

 | 字段    | 类型     | 说明       |
| ----- | ------ | ------------- |
| `set` | array | 设置信息        |
| `set[i].uid` | int | 用户id |
| `set.stor[i]` | array | 存储空间信息 |
| `set.stor[i].id` | int | 存储空间id |
| `set.stor[i].quota` | int | 空间大小(字节) -1代表无限制 |

**响应示例**

```json
{"result":"succ","reqid":"reqid"}
```


 ## 获取硬盘信息

 - req：stor.calcSpace
 - 需要登录：是
 - 需要签名：是

 **请求示例**

 ```json
 {sign}{"reqid":"reqid","req":"stor.calcSpace"}
 ```

 **响应示例**

 ```json
{
  "fssizeSys": 19773603840, // 系统预留空间
  "frsizeSys": 9511735296, // 系统实际占用空间
  "sysDiskType": "HDD", // 系统安装的磁盘类型
  "storTotal": 1, // 硬盘数量
  "fssizeStor": 31642714112, // 存储空间总容量
  "frsizeStor": 31636586496, // 存储空间可用容量
  "HDD": 1, // HHD类型硬盘数量
  "SSD": 0, // SSD类型硬盘数量
  "USB": 0, // USB设备数量
  "result": "succ",
  "reqid": "reqid"
}
 ```