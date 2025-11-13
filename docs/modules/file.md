# 文件管理
- 需要登录：是
- 需要签名：是


## 文件列表

**请求示例**
```json
{sign}{"reqid":"reqid","path":"vol1/1000/测试文件夹","req":"file.ls"}
```

**参数说明**

> path字段是由 vol{stor_id}/{user_id}/{path} 组成的

| 字段      | 类型     | 说明                                   |
| ------- | ------ | ------------------------------------ |
| `path`  | string \| null | 查询目录路径(为null默认为用户目录)  |

**响应示例**

```json
{
  "files": [
    {
      "name": "微软.jpg", // 文件名称
      "uid": 1000, // 所属用户id
      "size": 814378, // 文件大小
      "mtim": 1762805820, // 创建时间
      "btim": 1763036958 // 修改时间
    },
    {
      "name": "12131", // 文件夹名称
      "uid": 1000, // 所属用户id
      "mtim": 1763038335, // 创建时间
      "btim": 1763038335, // 修改时间
      "dir": 1, // 1为文件夹 文件不返回该字段
      "v": 1 // 存储空间id 只有用户根目录才返回
    }
  ],
  "uver": 115541950529538,
  "reqid": "reqid"
}
```
## 创建文件夹

**请求示例**

> 在`vol1/1000/测试文件夹`路径下创建`创建文件夹测试`文件夹

```json
{sign}{"reqid":"reqid","path":"vol1/1000/测试文件夹/创建文件夹测试","req":"file.mkdir"}
```

| 字段    | 类型   | 说明       |
| ------- | ------ | -------    |
| `path`  | string | 文件夹路径 |


**响应示例**

```json
{"result":"succ","reqid":"reqid"}
```



## 文件(夹)删除

**请求示例**

```json
{sign}{"reqid":"reqid","files":["vol1/1000/测试文件夹/12131"],"moveToTrashbin":true,"details":{"name":"12131","count":1,"dir":1},"req":"file.rm"}
```

| 字段      | 类型     | 说明                                   |
| ------- | ------ | ------------------------------------ |
| `files`  | array | 需要删除的文件绝对路径数组  |
| `moveToTrashbin`  | bool | 移至回收站 [true\|false] |
| `details`  | object | 用于显示文件任务描述[可选] |
| `details.name`  | string | 任务名称 |
| `details.count`  | int | 删除数量 |
| `details.dir`  | int | 是否目录[可选:1] |


**响应示例**

```json
{"result":"succ","reqid":"reqid"}
```

