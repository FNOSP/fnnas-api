# 系统信息

## 获取设备基础信息

 - req: appcgi.sysinfo.getHostName
 - 是否需要登录：否
 - 是否需要签名：否

**请求示例**

```json
{"reqid":"reqid","req":"appcgi.sysinfo.getHostName"}
```

**响应示例**

```json
{
    "data": {
        "hostName": "dev-test",
        "hasUsers": true,
        "trimVersion": "0.9.35"
    },
    "reqid": "reqid",
    "result": "succ",
    "rev": "0.1",
    "req": "appcgi.sysinfo.getHostName"
}
```

## 获取设备版本

 - req: appcgi.sysinfo.getTrimVersion
 - 是否需要登录：是
 - 是否需要签名：是

**请求示例**

```json
{sign}{"reqid":"reqid","req":"appcgi.sysinfo.getTrimVersion"}
```

**响应示例**

```json
{
  "data": {
    "trimVersion": "0.9.35"
  },
  "reqid": "reqid",
  "result": "succ",
  "rev": "0.1",
  "req": "appcgi.sysinfo.getTrimVersion"
}
```

## 获取设备ID

 - req: appcgi.sysinfo.getMachineId
 - 是否需要登录：是
 - 是否需要签名：是

**请求示例**

```json
{sign}{"reqid":"reqid","req":"appcgi.sysinfo.getMachineId"}
```

**响应示例**

```json
{
  "data": {
    "machineId": "machineId"
  },
  "reqid": "reqid",
  "result": "succ",
  "rev": "0.1",
  "req": "appcgi.sysinfo.getMachineId"
}
```

## 获取硬件信息

 - req: appcgi.sysinfo.getHardwareInfo
 - 是否需要登录：否
 - 是否需要签名：否

**请求示例**

```json
{"reqid":"reqid","req":"appcgi.sysinfo.getHardwareInfo"}
```

**响应示例**

```json
{
  "data": {
    "cpu": {
      "name": "Intel(R) Core(TM) i7-10750H CPU @ 2.60GHz",
      "num": 4,
      "core": 4,
      "thread": 4
    },
    "mem": {
      "num": 1,
      "total": 4294967296,
      "frequency": 0,
      "type": "RAM",
      "vendor": "QEMU"
    },
    "vm": {
      "available": 0,
      "iommu": 0,
      "sriov": 1
    },
    "bios": {
      "vendor": "SeaBIOS",
      "version": "1.16.3-debian-1.16.3-2",
      "baseboard": {},
      "system": {
        "vendor": "QEMU",
        "productName": "Standard PC (Q35 + ICH9, 2009)",
        "version": "pc-q35-10.0",
        "serialNumber": "",
        "sku": "",
        "uuid": "1f6396b0-cb27-4e33-8088-948940cea6fb",
        "family": ""
      }
    },
    "sysdisk": {
      "size": 0,
      "model": "Unknown",
      "protocol": "Unknown",
      "serialNumber": "Unknown"
    }
  },
  "reqid": "reqid",
  "result": "succ",
  "rev": "0.1",
  "req": "appcgi.sysinfo.getHardwareInfo"
}
```


## 获取硬件信息

 - req: appcgi.network.net.list
 - 是否需要登录：是
 - 是否需要签名：是

**请求示例**

```json
{sign}{"reqid":"reqid","req":"appcgi.network.net.list"}
```

**响应示例**

```json
{
  "data": {
    "net": {
      "ifs": [
        {
          "name": "enp1s0",
          "index": 1,
          "ifType": 0,
          "enable": true,
          "running": true,
          "onlink": true,
          "state": 100,
          "duplex": false,
          "speed": 65535,
          "mtu": 1500,
          "hwAddr": "Mac Addr",
          "isOvsPort": false,
          "wireless": false,
          "ipv4Dhcp": true,
          "ipv4Mode": "auto",
          "ipv4Broad": "192.168.100.255",
          "ipv4Mask": "255.255.255.0",
          "ipv4Gateway": "192.168.100.1",
          "ipv4Dns": "192.168.100.1",
          "ipv4": [
            "192.168.100.162"
          ],
          "ipv4Addr": "192.168.100.162",
          "ipv6Mode": "auto",
          "ipv6Gateway": "",
          "ipv6Dns": "",
          "ipv6": [
            {
              "addr": "addr",
              "prefixLen": 64,
              "scope": "link"
            }
          ]
        }
      ]
    }
  },
  "reqid": "reqid",
  "result": "succ",
  "rev": "0.1",
  "req": "appcgi.network.net.list"
}
```
