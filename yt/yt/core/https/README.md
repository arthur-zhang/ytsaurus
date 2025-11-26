# HTTPS 模块

## 模块概述

`yt/yt/core/https` 模块是 YTsaurus 分布式系统的 HTTPS 协议实现库，在 HTTP 模块的基础上提供了基于 SSL/TLS 的安全 HTTP 通信功能。该模块集成了证书管理、加密传输、安全验证等功能，为 YTsaurus 系统提供安全的 Web 服务和 API 通信支持。

## 主要功能

### 1. SSL/TLS 支持
- **HTTPS 客户端**: 支持安全 HTTPS 请求
- **HTTPS 服务端**: 支持安全 HTTPS 服务器
- **证书验证**: 客户端和服务端证书验证
- **加密套件**: 现代安全的加密套件支持

### 2. 安全配置
- **证书管理**: SSL/TLS 证书加载和管理
- **私钥管理**: 私钥的安全加载和使用
- **CA 验证**: 证书颁发机构验证
- **主机名验证**: 防止中间人攻击

### 3. 连接安全
- **安全连接**: 建立加密的 HTTPS 连接
- **会话复用**: SSL 会话复用提高性能
- **前向安全**: 支持前向安全的密钥交换
- **协议版本**: 支持 TLS 1.2 和 TLS 1.3

## 文件说明

### 核心文件
- **https_client.h/c**: HTTPS 客户端实现
- **https_server.h/c**: HTTPS 服务端实现
- **ssl_config.h**: SSL/TLS 配置管理

## 使用示例

### HTTPS 客户端使用
```cpp
#include <yt/yt/core/https/https_client.h>

using namespace NYT::NHttps;

// 创建 HTTPS 客户端
auto config = New<THttpsClientConfig>();
config->SslVerifyPeer = true;
config->SslVerifyHost = true;

auto client = CreateHttpsClient(config);

// 发送 HTTPS 请求
auto response = WaitFor(client->Get("https://api.example.com/data"))
    .ValueOrThrow();
```

### HTTPS 服务端使用
```cpp
#include <yt/yt/core/https/https_server.h>

// 创建 HTTPS 服务器配置
auto config = New<THttpsServerConfig>();
config->Port = 443;
config->CertFile = "/path/to/server.crt";
config->KeyFile = "/path/to/server.key";

// 创建并启动 HTTPS 服务器
auto server = CreateHttpsServer(config);
server->AddHandler("/api", [](const TRequest& request) {
    return TResponse::Ok("{\"secure\": true}");
});

server->Start();
```

## 配置选项

### SSL 配置
- **证书文件**: SSL/TLS 证书文件路径
- **私钥文件**: 私钥文件路径
- **CA 证书**: 受信任的 CA 证书
- **验证模式**: 证书验证模式

### 安全选项
- **协议版本**: 支持的 TLS 协议版本
- **加密套件**: 支持的加密套件列表
- **会话超时**: SSL 会话超时时间
- **证书链**: 证书链验证配置

## 依赖关系

- **yt/yt/core/http**: HTTP 协议基础实现
- **yt/yt/core/crypto**: 加密算法和 SSL/TLS 支持
- **OpenSSL**: 底层 SSL/TLS 实现
- **yt/yt/core/net**: 网络连接抽象

## 安全特性

- **现代协议**: 支持 TLS 1.2 和 TLS 1.3
- **强加密**: 使用强加密算法和密钥长度
- **证书验证**: 完整的证书链验证
- **前向安全**: 支持前向安全的密钥交换

## 性能优化

- **会话复用**: SSL 会话缓存和复用
- **连接池**: HTTPS 连接池管理
- **硬件加速**: 利用硬件 SSL 加速
- **内存优化**: 优化 SSL 内存使用

## 最佳实践

1. **证书管理**: 定期更新证书和私钥
2. **协议配置**: 禁用过时的 SSL/TLS 版本
3. **加密套件**: 选择安全的加密套件
4. **验证策略**: 启用完整的证书验证
5. **监控告警**: 监控 SSL 错误和性能指标