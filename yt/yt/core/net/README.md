# Net 模块

## 模块概述

`yt/yt/core/net` 模块是 YTsaurus 分布式系统的网络通信基础库，提供了完整的网络地址管理、套接字抽象、DNS 解析和网络配置功能。该模块封装了底层的网络操作，为上层通信模块（如 Bus、HTTP）提供统一的网络接口，支持 IPv4/IPv6、Unix Domain Socket 等多种网络协议。

## 主要功能

### 1. 网络地址抽象
- **IP 地址**: 支持 IPv4 和 IPv6 地址
- **网络套接字地址**: 完整的网络地址封装
- **Unix 套接字**: Unix Domain Socket 支持
- **地址解析**: DNS 和主机名解析

### 2. 套接字管理
- **套接字创建**: TCP、UDP 套接字的创建和配置
- **连接管理**: 套接字连接的建立和管理
- **选项配置**: 套接字选项的设置和获取
- **错误处理**: 网络错误的统一处理

### 3. 网络配置
- **接口枚举**: 网络接口的枚举和查询
- **路由信息**: 网络路由信息的获取
- **网络配置**: 网络参数的配置和管理
- **本地地址**: 本地网络地址的检测

### 4. DNS 解析
- **主机名解析**: 主机名到 IP 地址的解析
- **反向解析**: IP 地址到主机名的反向解析
- **缓存机制**: DNS 查询结果的缓存
- **超时处理**: DNS 查询超时处理

## 核心类型

### TNetworkAddress
网络地址的统一表示，支持：
- IPv4 地址和端口
- IPv6 地址和端口
- Unix Domain Socket 路径

### TIP6Network
IPv6 网络地址段，用于网络匹配和路由。

### TSocket
套接字的封装，提供跨平台的套接字操作。

## 使用示例

### 网络地址操作
```cpp
#include <yt/yt/core/net/address.h>

using namespace NYT::NNet;

// 创建网络地址
TNetworkAddress address;
address.Parse("localhost:8080");

// IPv6 地址
TNetworkAddress ipv6Addr;
ipv6Addr.Parse("[2001:db8::1]:80");

// Unix Socket
TNetworkAddress unixAddr;
unixAddr.Parse("/tmp/socket.sock");

// 地址比较
if (address.GetPort() == 8080) {
    std::cout << "Port 8080" << std::endl;
}
```

### 套接字操作
```cpp
#include <yt/yt/core/net/socket.h>

// 创建 TCP 套接字
auto socket = CreateTcpSocket();

// 连接到远程地址
socket->Connect(address);

// 设置套接字选项
socket->SetReuseAddr(true);
socket->SetNoDelay(true);

// 读取数据
char buffer[1024];
size_t bytesRead = socket->Read(buffer, sizeof(buffer));

// 写入数据
const char* data = "Hello, Network!";
size_t bytesWritten = socket->Write(data, strlen(data));
```

### DNS 解析
```cpp
#include <yt/yt/core/net/dns_resolver.h>

// 解析主机名
auto resolver = CreateDnsResolver();
auto addresses = resolver->Resolve("example.com");

for (const auto& addr : addresses) {
    std::cout << "Resolved: " << addr.ToString() << std::endl;
}
```

### 网络接口信息
```cpp
#include <yt/yt/core/net/interface.h>

// 获取网络接口列表
auto interfaces = GetNetworkInterfaces();

for (const auto& iface : interfaces) {
    std::cout << "Interface: " << iface.Name << std::endl;
    std::cout << "  Address: " << iface.Address.ToString() << std::endl;
    std::cout << "  Netmask: " << iface.Netmask.ToString() << std::endl;
}
```

## 配置选项

### 套接字选项
- **SO_REUSEADDR**: 地址重用
- **SO_REUSEPORT**: 端口重用
- **TCP_NODELAY**: 禁用 Nagle 算法
- **SO_KEEPALIVE**: 启用 TCP Keep-Alive

### 网络配置
- **DNS 超时**: DNS 查询超时时间
- **连接超时**: 连接建立超时时间
- **缓冲区大小**: 套接字缓冲区大小
- **重试次数**: 连接失败重试次数

## 性能优化

- **地址缓存**: DNS 解析结果缓存
- **连接复用**: 套接字连接复用
- **批量操作**: 批量网络操作
- **异步 I/O**: 非阻塞 I/O 操作

## 依赖关系

- **系统网络库**: 各平台的网络 API
- **yt/yt/core/misc**: 基础工具和错误处理
- **yt/yt/core/logging**: 网络操作日志记录

## 跨平台支持

### 支持平台
- **Linux**: epoll 和其他 Linux 特有特性
- **macOS**: kqueue 和 macOS 网络特性
- **Windows**: WinSock 和 Windows 网络特性

### 统一接口
提供跨平台的统一网络接口，隐藏平台差异。

## 错误处理

- **网络异常**: 网络相关的异常类型
- **错误码**: 网络错误码的统一处理
- **重试机制**: 网络失败的重试策略
- **超时处理**: 网络操作超时处理