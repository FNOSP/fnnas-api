# 鉴权

## 用户登录

### 获取 RSA 公钥

 - 命令：util.crypto.getRSAPub
 - 说明：获取服务器当前 RSA 公钥，用于加密登录凭据。
 - 是否需要登录：否
 - 是否需要签名：否

 **请求示例**
 ```json
{"req":"util.crypto.getRSAPub","reqid":"6915893900000000000000000001"}
 ```

 **响应示例**
 ```json
{"pub":"-----BEGIN PUBLIC KEY-----\nMIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAkfXZ6ywukYoVmxnGej0c\nuWWeMWUN3JBuubUX1cAsGBoVzMw2SpbQcdUVsnQ58W//0WxZoYWYS3hndtYMAKhE\neZJcuzZc2dahcRLi0H3xUdZo6R00HUTgK3JHWkBjEtyxjGnL9VvFTjgl3ivRmgxR\nV1AqvnvVyAdeXAYjtGOxxUhKmz5O5ayCnjGJlmt4TcGQpk8e+GidBNiJeL5fz/0r\nVvOFJTk/UPANf1ygaJSEYR+Eo/0ZgVm2SZ4ZU310pZNQo2S4pr+VpZc3y9lJrOAf\nGDzUoxbAzyZKIS65Am3ufBFcBi39Chtfa8Hzm7FW7p3LTMqBWY9ZfrHwiWkms06I\nQwIDAQAB\n-----END PUBLIC KEY-----\n","si":"72057757246685317","result":"succ","reqid":"6915893900000000000000000001"}
 ```

 **字段说明**

 | 字段    | 类型     | 说明            |
| ----- | ------ | ------------- |
| `si` | string | 待定        |
| `pub` | string | RSA 公钥 PEM 格式 |

### 登录请求

- 命令：encrypted
- 说明：使用加密后的账号信息登录系统，返回用户信息。
- 依赖接口：util.crypto.getRSAPub
- 是否需要登录：否
- 是否需要签名：否
- 是否需要加密：是

**请求data**
> 加密前的数据

```json
{
    "user": "username", // 用户名
    "password": "password", // 密码
    "deviceType": "Browser", // 设备类型
    "deviceName": "Windows-Google Chrome", // 设备名称
    "stay": false,
    "si": "si"
}
```

 **字段说明**

 | 字段    | 类型     | 说明            |
| ----- | ------ | ------------- |
| `user` | string | 用户名        |
| `password` | string | 用户密码 |
| `deviceType` | string | 设备类型[Browser] |
| `deviceName` | string | 设备名称[Windows-Google Chrome] |
| `stay` | bool | 保持登录 |
| `si` | string | 待定 |


**请求示例**
> 请求要把请求数据进行加密，并传递客户端生成的AES key和iv。

```json
{"req":"encrypted","iv":"Base64(aes_iv)","rsa":"Base64(RSA_Encrypt(aes_key))","aes":"Base64(AES_Encrypt(data))"}
```

**字段说明**

 | 字段    | 类型     | 说明            |
| ----- | ------ | ------------- |
| `iv` | string | Baes64编码的AES iv        |
| `rsa` | string | 使用RSA公钥加密后再Base64编码的AES key        |
| `aes` | string | 使用AES加密后在用Base64编码的请求体 |

**成功响应示例**

```json
{"uid":1000,"admin":true,"secret":"secret","token":"token","backId":"6915b82200000001","machineId":"machineId","result":"succ","reqid":"reqid"}
```

**失败响应示例**
```json
{"errno":8192,"result":"fail","reqid":"reqid"}
```

**字段说明**

 | 字段    | 类型     | 说明            |
| ----- | ------ | ------------- |
| `uid` | int | 用户id        |
| `admin` | bool | 是否管理员 |
| `secret` | string | 签名密钥（使用AES解密后使用） |
| `token` | string | 特殊接口鉴权 |
| `backId` | string | reqid中的一部分 |
| `machineId` | string | 设备id |


## 用户登出

- 命令：user.logout
- 说明：用户登出、注销登录状态
- 是否需要登录：是
- 是否需要签名：是

```json
{sign}{"reqid":"6915bcaf6915bca4000000030021","req":"user.logout"}
```

## 刷新Token