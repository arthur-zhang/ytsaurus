# Crypto 模块

## 模块概述

`yt/yt/core/crypto` 模块是 YTsaurus 分布式系统的加密和安全通信核心库，提供了完整的加密算法、SSL/TLS 支持、数字签名和安全配置管理功能。该模块集成了多种加密算法和安全协议，为 YTsaurus 系统中的数据加密传输、身份验证和安全通信提供统一的安全基础设施。

## 主要功能

### 1. 加密算法支持
- **对称加密**: AES、ChaCha20 等对称加密算法
- **非对称加密**: RSA、ECDSA 等非对称加密算法
- **哈希算法**: SHA-256、SHA-512、Blake2 等哈希算法
- **消息认证码**: HMAC、CMAC 等消息认证码

### 2. SSL/TLS 实现
- **SSL 上下文管理**: SSL/TLS 连接的上下文配置和管理
- **证书验证**: 客户端和服务端证书验证
- **握手协议**: SSL/TLS 握手过程的实现
- **加密套件**: 支持现代安全的加密套件

### 3. 配置管理
- **安全配置**: 加密算法和安全参数的配置
- **证书管理**: 证书加载、验证和管理
- **动态配置**: 支持运行时配置更新
- **安全策略**: 安全策略的定义和执行

## 文件说明

### 核心文件
- **public.h**: 模块的公共接口声明
- **crypto.h/c**: 核心加密算法接口和实现
- **config.h/c**: 加密配置管理
- **tls.cpp**: TLS/SSL 实现细节

## 使用示例

### 基本加密操作
```cpp
#include <yt/yt/core/crypto/crypto.h>

using namespace NYT::NCrypto;

// 数据加密
auto encrypted = Encrypt(data, key);
// 数据解密
auto decrypted = Decrypt(encrypted, key);
```

### TLS 配置
```cpp
#include <yt/yt/core/crypto/config.h>

// 创建 SSL 配置
auto config = New<TSSLConfig>();
config->CertFile = "/path/to/cert.pem";
config->KeyFile = "/path/to/key.pem";

// 应用配置
ApplySSLConfig(config);
```

## 依赖关系

- **OpenSSL**: 底层加密算法和 SSL/TLS 实现
- **yt/yt/core/misc**: 基础工具和配置系统
- **yt/yt/core/ytree**: YTree 配置系统

## 安全特性

- **现代加密**: 使用现代安全的加密算法和协议
- **证书验证**: 完整的证书链验证
- **前向安全**: 支持前向安全的密钥交换
- **合规性**: 符合安全行业标准和最佳实践

## 性能优化

- **硬件加速**: 利用 CPU 的加密指令集
- **内存安全**: 防止时序攻击和侧信道攻击
- **缓存友好**: 优化内存访问模式