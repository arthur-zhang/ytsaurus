# YTsaurus Signature Client 模块

## 概述

Signature Client 模块是 YTsaurus 数字签名系统的客户端接口，提供数据完整性验证、身份认证和防篡改保护功能。

## 核心功能

### 1. 数字签名
- **数据签名**: 对数据进行数字签名
- **签名验证**: 验证数字签名的有效性
- **密钥管理**: 公私钥管理

### 2. 完整性保护
- **数据校验**: 数据完整性校验
- **防篡改**: 防止数据篡改
- **哈希计算**: 数据哈希值计算

## 使用方法

```cpp
#include <yt/yt/client/signature/public.h>

// 创建签名客户端
auto client = CreateSignatureClient(config);

// 签名数据
auto signature = client->SignData(data, privateKey);

// 验证签名
bool isValid = client->VerifySignature(data, signature, publicKey);
```

## 依赖项

### 内部依赖
- `yt/yt/core/misc/public.h` - 核心公共定义

## 相关模块

- **File Client**: 文件签名
- **Security Client**: 安全验证

## 贡献指南

确保加密算法的安全性和签名的可靠性。