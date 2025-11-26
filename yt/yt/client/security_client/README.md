# YTsaurus Security Client 模块

## 概述

Security Client 模块是 YTsaurus 安全系统的客户端接口，提供身份认证、授权管理和安全策略控制功能。

## 核心功能

### 1. 身份认证
- **用户认证**: 用户身份验证
- **令牌管理**: 访问令牌管理
- **权限验证**: 权限检查和验证

### 2. 授权管理
- **ACL 管理**: 访问控制列表管理
- **角色管理**: 用户角色管理
- **权限继承**: 权限继承关系

## 使用方法

```cpp
#include <yt/yt/client/security_client/public.h>

// 创建安全客户端
auto client = CreateSecurityClient(config);

// 用户认证
bool isAuthenticated = client->AuthenticateUser(username, password);

// 检查权限
bool hasPermission = client->CheckPermission(user, path, EPermission::Read);
```

## 依赖项

### 内部依赖
- `yt/yt/core/misc/public.h` - 核心公共定义

## 相关模块

- **API Client**: 安全 API 调用
- **Cypress Client**: 安全元数据

## 贡献指南

确保安全策略的正确实施和权限控制。