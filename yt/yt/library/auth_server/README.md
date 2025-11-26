# Auth Server 认证服务器

## 概述

`auth_server` 是 YTsaurus 分布式存储系统的核心认证模块，提供统一的身份验证和授权服务。该模块支持多种认证方式，包括 Token 认证、Cookie 认证、Ticket 认证等，并与外部认证服务（如 Blackbox、OAuth、Yandex Cloud IAM）集成。

## 核心功能

### 多种认证方式支持

1. **Token 认证** (`token_authenticator.h/cpp`)
   - Blackbox Token 认证
   - Cypress Token 认证
   - OAuth Token 认证
   - Yandex Cloud IAM Token 认证
   - 支持缓存和组合认证器

2. **Cookie 认证** (`cookie_authenticator.h/cpp`)
   - Blackbox Cookie 认证
   - Cypress Cookie 认证
   - OAuth Cookie 认证
   - 支持 CSRF 保护

3. **Ticket 认证** (`ticket_authenticator.h/cpp`)
   - 服务票据认证
   - 用户票据认证

### 外部服务集成

1. **Blackbox 服务** (`blackbox_service.h/cpp`)
   - Yandex 内部认证服务集成
   - 支持用户登录验证和会话管理

2. **OAuth 服务** (`oauth_service.h/cpp`)
   - 第三方 OAuth 提供商集成
   - 支持用户信息获取和转换

3. **Secret Vault 服务** (`secret_vault_service.h/cpp`)
   - 密钥存储和管理
   - 委托令牌管理
   - 支持批处理和缓存优化

4. **Yandex Cloud IAM** (`yc_iam_token_authenticator.h/cpp`)
   - YC IAM 令牌验证
   - 用户自动创建和管理

### Cypress 集成

1. **Cookie 管理** (`cypress_cookie_manager.h/cpp`)
   - Cypress Cookie 生成和验证
   - Cookie 存储和管理

2. **用户管理** (`cypress_user_manager.h/cpp`)
   - 用户存在性检查
   - 用户自动创建

## 架构设计

### 核心组件

```
IAuthenticationManager
├── ITokenAuthenticator (Token 认证)
├── ICookieAuthenticator (Cookie 认证)
├── ITicketAuthenticator (Ticket 认证)
├── ITvmService (TVM 服务)
├── ICypressCookieManager (Cypress Cookie 管理)
└── ICypressUserManager (Cypress 用户管理)
```

### 认证流程

1. **凭证接收**: 接收 Token、Cookie 或 Ticket 凭证
2. **认证器选择**: 根据凭证类型选择相应的认证器
3. **外部验证**: 调用外部认证服务进行验证
4. **缓存处理**: 使用缓存机制提高性能
5. **结果返回**: 返回认证结果和用户信息

### 缓存机制

- **认证结果缓存**: 减少外部服务调用
- **用户存在性缓存**: 优化用户检查性能
- **密钥缓存**: 提升 Secret Vault 访问效率

## 配置管理

### 主要配置类

- `TAuthenticationManagerConfig`: 认证管理器主配置
- `TBlackboxServiceConfig`: Blackbox 服务配置
- `TOAuthServiceConfig`: OAuth 服务配置
- `TDefaultSecretVaultServiceConfig`: Secret Vault 配置
- `TYCIamTokenAuthenticatorConfig`: YC IAM 配置

### 缓存配置

- `TAuthCacheConfig`: 认证缓存通用配置
- `TCachingTokenAuthenticatorConfig`: Token 认证缓存配置
- `TCachingCookieAuthenticatorConfig`: Cookie 认证缓存配置

## 安全特性

### CSRF 保护
- CSRF 令牌生成和验证
- 可配置的令牌过期时间

### 安全传输
- HTTPS 支持
- 安全 Cookie 配置
- 委托令牌管理

### 访问控制
- 多种认证方式支持
- 用户角色和权限管理
- 会话管理

## 性能优化

### 批处理机制
- Secret Vault 批处理请求
- 减少网络调用次数

### 并发控制
- 请求限流
- 连接池管理
- 异步处理

### 缓存策略
- 多级缓存架构
- 可配置的缓存过期策略
- 错误缓存机制

## 错误处理

### 错误类型定义
```cpp
enum class EBlackboxStatus;
enum class EBlackboxException;
enum class ESecretVaultErrorCode;
```

### 重试机制
- 可配置的重试策略
- 指数退避算法
- 错误分类处理

## 使用示例

### 创建认证管理器
```cpp
auto config = New<TAuthenticationManagerConfig>();
// 配置各种认证器...
auto authManager = CreateAuthenticationManager(
    config,
    poller,
    client,
    tvmService);
authManager->Start();
```

### Token 认证
```cpp
auto tokenAuthenticator = authManager->GetTokenAuthenticator();
TTokenCredentials credentials{token, userIP};
auto result = WaitFor(tokenAuthenticator->Authenticate(credentials))
    .ValueOrThrow();
```

### Cookie 认证
```cpp
auto cookieAuthenticator = authManager->GetCookieAuthenticator();
TCookieCredentials credentials{cookies, userIP};
auto result = WaitFor(cookieAuthenticator->Authenticate(credentials))
    .ValueOrThrow();
```

## 构建和测试

### 构建依赖
- `yt/yt/client`: Cypress 客户端
- `yt/yt/core/https`: HTTPS 支持
- `yt/yt/library/auth`: 认证基础库
- `yt/yt/library/tvm/service`: TVM 服务
- `library/cpp/string_utils`: 字符串处理工具

### 测试
单元测试位于 `unittests/` 目录：
- `blackbox_ut.cpp`: Blackbox 服务测试
- `secret_vault_ut.cpp`: Secret Vault 测试
- `yc_iam_token_ut.cpp`: YC IAM Token 测试

## 兼容性

### 平台支持
- Linux (x86_64, aarch64)
- macOS (x86_64, arm64)

### 编译器要求
- C++20 标准
- Clang-18+ 推荐

## 许可证

本模块遵循 YTsaurus 项目的开源许可证。

## 贡献指南

请参考项目根目录的 `CONTRIBUTING.md` 文件了解贡献指南。在提交代码时，请确保：

1. 遵循项目的代码风格规范
2. 添加适当的单元测试
3. 更新相关文档
4. 通过所有现有测试

## 相关文档

- [YTsaurus 官方文档](https://ytsaurus.tech/)
- [Blackbox 认证服务文档](https://doc.yandex-team.ru/blackbox/)
- [OAuth 2.0 规范](https://tools.ietf.org/html/rfc6749)
- [Yandex Cloud IAM 文档](https://cloud.yandex.ru/docs/iam/)