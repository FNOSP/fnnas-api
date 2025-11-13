# 用户模块

## 用户信息

 - req： user.info
 - 需要登录：是
 - 需要签名：是

 **请求示例**

 ```json
{sign}{"reqid":"reqid","user":"test1","req":"user.info"}
 ```
 | 字段    | 类型     | 说明       |
| ----- | ------ | ------------- |
| `user` | string | 可选，默认查自己        |

 **响应示例**

 ```json
 {
    "userInfo": {
        "user": "dev",
        "uid": 1000,
        "comment": "",
        "email": "",
        "mobile": "",
        "disableChangePassword": false,
        "lastChange": 20405,
        "disableUser": 0,
        "admin": true,
        "allowSSH": true,
        "groups": [
            "Administrators",
            "Users"
        ]
    },
    "result": "succ",
    "reqid": "reqid"
}
```

## 用户是否为管理员

 - req：user.isAdmin
 - 需要登录：是
 - 需要签名：是

 **请求示例**
 
```json
{sign}{"reqid":"reqid","req":"user.isAdmin"}
```

**响应示例**

```json
{
    "admin": true,
    "result": "succ",
    "reqid": "reqid"
}
```

## 检查用户是否存在

**请求示例**

```json
{sign}{"reqid":"reqid","user":"test","req":"user.checkNewUser"}
```

**响应示例**

 - 用户不存在响应

```json
{
  "result": "succ",
  "reqid": "reqid"
}
```

 - 用户存在响应
```json
{
    "errno": 131074,
    "result": "fail",
    "reqid": "reqid"
}
```

## 创建新用户

**请求data**

```json
{
    "reqid": "reqid",
    "user": "username", // 用户名
    "password": "password", // 用户密码
    "comment": "这是描述", // 用户描述
    "setAdmin": false, // 设置为管理员
    "req": "user.add",
    "si": "si"
}
```

**请求示例**
> 该接口需要加密

```json
{"req":"encrypted","iv":"Base64(aes_iv)","rsa":"Base64(RSA_Encrypt(aes_key))","aes":"Base64(AES_Encrypt(data))"}
```

**响应示例**

> 成功响应示例
```json
{"uid":1001,"result":"succ","reqid":"reqid"}
```

> 失败响应示例
```json
{"errno":131074,"result":"fail","reqid":"reqid"}
```

## 删除用户

**请求示例**

```json
{sign}{"reqid":"reqid","user":"username","req":"user.del"}
```

**响应示例**

```json
{
  "result": "succ",
  "reqid": "reqid"
}
```

## 修改用户信息

**请求示例**

```json
{sign}{"reqid":"reqid","user":"test","comment":"修改描述","newName":"test1","req":"user.mod"}
```

| 字段    | 类型     | 说明       |
| ----- | ------ | ------------- |
| `user` | string | 被修改的用户名        |
| `comment` | string | 描述[可选] |
| `newName` | string | 新用户名[可选] |
| `disableUser` | int | 禁用[可选[1\|0]] |
| `allowSSH` | bool | 启用SSH登录[可选[true\|false]] 需要为管理员才生效|

**响应示例**

```json
{"result":"succ","reqid":"reqid"}
```

## 设置管理员

**请求示例**

```json
{sign}{"reqid":"reqid","user":"test1","setAdmin":false,"req":"user.setAdmin"}
```

| 字段    | 类型     | 说明       |
| ----- | ------ | ------------- |
| `user` | string | 被修改的用户名        |
| `setAdmin` | bool | 设置管理员[可选[true\|false]] |

**响应示例**

```json
{"result":"succ","reqid":"reqid"}
```

## 修改用户组

**请求示例**

```json
{sign}{"req":"req","reqid":"reqid","group":"Administrators","users":["test1"]}
```

| 字段    | 类型     | 说明       |
| ----- | ------ | ------------- |
| `req` | string | [user.groupAddUsers\|user.groupDelUsers]      |
| `group` | string | 组名称        |
| `users` | array | 操作的用户列表 |

**响应示例**

```json
{"result":"succ","reqid":"reqid"}
```

##  修改密码


```json
// 管理员
{
    "reqid": "6916174369160768000000200a8f",
    "user": "test2",
    "newPassword": "%b9#}6CmJfVs9",
    "removeToken": true,
    "req": "user.changePassword",
    "si": "72057654167470148"
}
```

```json
// 自己修改
{
    "reqid": "691617cd691617b800000042001b",
    "user": "test2",
    "password": "%b9#}6CmJfVs9",
    "newPassword": "Rr64RNi5|Vd(#o",
    "req": "user.changePassword",
    "si": "60129542249"
}
```

