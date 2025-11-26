# YTsaurus RPC Client 模块

## 概述

RPC Client 模块是 YTsaurus 远程过程调用系统的客户端实现，提供高性能、可靠的分布式通信能力。该模块基于 TCP/IP 协议实现，支持请求/响应模式、流式传输、负载均衡和故障转移等高级功能。

## 核心功能

### 1. 远程调用
- **同步调用**: 阻塞式的远程过程调用
- **异步调用**: 非阻塞的异步调用
- **流式调用**: 支持双向数据流
- **批量调用**: 批量请求处理

### 2. 连接管理
- **连接池**: 高效的连接池管理
- **连接复用**: TCP 连接复用
- **自动重连**: 连接断开自动重连
- **负载均衡**: 智能的负载均衡

### 3. 协议支持
- **二进制协议**: 高效的二进制通信协议
- **压缩传输**: 数据压缩传输
- **加密传输**: TLS 加密通信
- **协议版本**: 多版本协议兼容

### 4. 错误处理
- **超时处理**: 请求超时处理
- **重试机制**: 智能重试策略
- **错误传播**: 结构化错误传播
- **故障转移**: 自动故障转移

## 使用方法

```cpp
#include <yt/yt/client/rpc/public.h>

using namespace NYT::NRpc;

// 创建 RPC 客户端
auto clientConfig = New<TClientConfig>();
clientConfig->Addresses = {"server1:9013", "server2:9013"};
clientConfig->Timeout = TDuration::Seconds(30);

auto client = CreateClient(clientConfig);

// 发起 RPC 调用
auto request = TMyService::TMyMethodRequest();
request.SetParameter("value", 42);

auto future = client->Invoke<TMyService::TMyMethodResponse>(request);

auto response = WaitFor(future)
    .ValueOrThrow();

std::cout << "Result: " << response.GetResult() << std::endl;
```

## 配置参数

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| Timeout | TDuration | 30s | 请求超时时间 |
| RetryCount | int | 3 | 重试次数 |
| EnableCompression | bool | true | 启用压缩 |
| EnableEncryption | bool | false | 启用加密 |
| ConnectionPoolSize | int | 10 | 连接池大小 |

## 依赖项

### 内部依赖
- `yt/yt/core/rpc/public.h` - RPC 核心接口

### 外部依赖
- 网络通信库
- 压缩库
- 加密库

## 相关模块

- **API Client**: 高级 API 接口
- **Driver**: 命令行驱动

## 贡献指南

在修改此模块时：
1. 确保协议实现的正确性
2. 优化网络性能
3. 添加充分的错误处理
4. 保持协议向后兼容