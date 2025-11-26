# HTTP 模块

## 模块概述

`yt/yt/core/http` 模块是 YTsaurus 分布式系统的 HTTP 协议实现库，提供了完整的 HTTP/1.1 客户端和服务端功能。该模块实现了 HTTP 请求和响应处理、连接管理、流式传输和错误处理等功能，为 YTsaurus 系统中的 HTTP 通信和 REST API 提供基础设施支持。

## 主要功能

### 1. HTTP 客户端
- **请求发送**: 支持 GET、POST、PUT、DELETE 等 HTTP 方法
- **连接管理**: HTTP 连接池和 Keep-Alive 支持
- **异步操作**: 基于 Future 的异步 HTTP 请求
- **错误处理**: 完整的 HTTP 错误码和异常处理

### 2. HTTP 服务端
- **请求处理**: HTTP 请求路由和处理
- **响应生成**: HTTP 响应构建和发送
- **流式传输**: 支持流式 HTTP 响应
- **中间件**: 请求处理中间件支持

### 3. 协议支持
- **HTTP/1.1**: 完整的 HTTP/1.1 协议实现
- **Chunked 编码**: 支持 Transfer-Encoding: chunked
- **压缩传输**: 支持 gzip、deflate 压缩传输
- **连接复用**: HTTP 连接复用和管道化

## 文件说明

### 核心文件
- **client.h/c**: HTTP 客户端实现
- **server.h**: HTTP 服务端接口定义
- **config.h**: HTTP 配置管理

### 实现文件
- **http.cpp**: HTTP 协议核心实现
- **headers.cpp**: HTTP 头部处理
- **parser.cpp**: HTTP 协议解析器

## 使用示例

### HTTP 客户端使用
```cpp
#include <yt/yt/core/http/client.h>

using namespace NYT::NHttp;

// 创建 HTTP 客户端
auto client = CreateHttpClient();

// 发送 GET 请求
auto response = WaitFor(client->Get("http://example.com/api"))
    .ValueOrThrow();

// 发送 POST 请求
auto postResponse = WaitFor(client->Post(
    "http://example.com/api",
    TSharedRef::FromString("{\"key\":\"value\"}")
)).ValueOrThrow();
```

### HTTP 服务端使用
```cpp
#include <yt/yt/core/http/server.h>

// 创建 HTTP 服务器
auto server = CreateHttpServer();

// 注册处理器
server->AddHandler("/api", [](const TRequest& request) {
    return TResponse::Ok("{\"status\":\"success\"}");
});

// 启动服务器
server->Start(8080);
```

## 配置选项

### 客户端配置
- **连接超时**: HTTP 连接建立超时时间
- **读取超时**: HTTP 响应读取超时时间
- **最大重试**: 失败请求的最大重试次数
- **连接池大小**: HTTP 连接池的大小

### 服务端配置
- **监听端口**: HTTP 服务监听端口
- **最大连接数**: 最大并发连接数
- **请求超时**: HTTP 请求处理超时时间
- **缓冲区大小**: 请求和响应缓冲区大小

## 依赖关系

- **yt/yt/core/net**: 网络连接和套接字抽象
- **yt/yt/core/bus**: 底层通信框架
- **yt/yt/core/actions**: 异步编程基础设施
- **yt/yt/core/json**: JSON 数据处理

## 性能特性

- **异步处理**: 基于 Future 的异步 HTTP 操作
- **连接复用**: HTTP Keep-Alive 和连接池
- **流式传输**: 支持大文件的流式传输
- **内存效率**: 零拷贝的 HTTP 数据处理

## 安全特性

- **HTTPS 支持**: 基于 SSL/TLS 的安全传输
- **请求验证**: HTTP 请求验证和过滤
- **访问控制**: 基于头部的访问控制
- **速率限制**: 请求速率限制和防护