# 用户模块

## 用户信息

 - req： user.info
 - 需要登录：是
 - 需要签名：是

 **请求示例**

 ```json
{sign}{"reqid":"reqid","req":"user.info"}
 ```

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


