# 认证服务器库

## 概述

这个库提供了 YTsaurus 的完整认证和授权服务实现。它支持多种认证方式，包括令牌认证、Cookie 认证、OAuth 认证等，并与 Yandex Blackbox、Yandex Cloud IAM 等外部认证服务集成。

## 功能特性

### 认证方式支持

- **令牌认证**：支持各种令牌类型的验证
- **Ticket 认证**：基于票据的认证机制
- **Cookie 认证**：基于 Cookie 的 Web 认证
- **OAuth 认证**：OAuth 2.0 协议支持
- **Blackbox 认证**：与 Yandex Blackbox 服务集成
- **YC IAM 认证**：Yandex Cloud IAM 令牌验证
- **Cypress 认证**：基于 Cypress 的用户管理

### 安全特性

- **Secret Vault 集成**：安全的密钥管理
- **认证缓存**：提高认证性能
- **批处理支持**：批量处理认证请求
- **用户管理**：完整的用户生命周期管理

## 文件结构

### 核心认证组件

- `authentication_manager.h/cpp` - 认证管理器，统一管理所有认证器
- `ticket_authenticator.h/cpp` - Ticket 认证器实现
- `token_authenticator.h/cpp` - 令牌认证器实现
- `cookie_authenticator.h/cpp` - Cookie 认证器基础实现

### 认证方式实现

- `blackbox_service.h/cpp` - Blackbox 服务客户端
- `blackbox_cookie_authenticator.h/cpp` - Blackbox Cookie 认证
- `cypress_token_authenticator.h/cpp` - Cypress 令牌认证
- `oauth_service.h/cpp` - OAuth 服务实现
- `oauth_cookie_authenticator.h/cpp` - OAuth Cookie 认证
- `oauth_token_authenticator.h/cpp` - OAuth 令牌认证
- `yc_iam_token_authenticator.h/cpp` - YC IAM 令牌认证

### Cookie 管理

- `cypress_cookie.h/cpp` - Cypress Cookie 数据结构
- `cypress_cookie_manager.h/cpp` - Cookie 管理器
- `cypress_cookie_store.h/cpp` - Cookie 存储实现
- `cypress_cookie_login.h/cpp` - Cookie 登录处理

### 用户管理

- `cypress_user_manager.h/cpp` - Cypress 用户管理器
- `credentials.h/cpp` - 认证凭据定义

### Secret Vault 服务

- `secret_vault_service.h/cpp` - Secret Vault 接口定义
- `default_secret_vault_service.h/cpp` - 默认实现
- `batching_secret_vault_service.h/cpp` - 批处理实现
- `caching_secret_vault_service.h/cpp` - 缓存实现

### 缓存组件

- `auth_cache.h/cpp` - 认证缓存实现
- `auth_cache-inl.h` - 内联实现

### 配置文件

- `config.h/cpp` - 认证配置定义
- `private.h` - 私有接口
- `public.h` - 公共接口

### 工具类

- `helpers.h/cpp` - 辅助函数
- `helpers-inl.h` - 内联辅助函数

## 核心接口

### IAuthenticator 认证器接口

```cpp
// 所有认证器的基础接口
class IAuthenticator {
    virtual TFuture<TAuthenticationResult> Authenticate(
        const TAuthenticationRequest& request) = 0;
};
```

### ISecretVaultService 密钥库接口

```cpp
// 密钥库服务接口
class ISecretVaultService {
    virtual TFuture<TSecret> GetSecret(const TString& secretId) = 0;
    virtual TFuture<std::vector<TSecret>> GetSecrets(
        const std::vector<TString>& secretIds) = 0;
};
```

### ICypressCookieManager Cookie 管理接口

```cpp
// Cookie 管理器接口
class ICypressCookieManager {
    virtual TFuture<TCypressCookie> CreateCookie(
        const TCypressCookieGeneratorConfig& config) = 0;
    virtual TFuture<void> RevokeCookie(const TString& cookieId) = 0;
};
```

## 使用示例

### 基本认证配置

```cpp
#include <yt/yt/library/auth_server/public.h>

using namespace NYT::NAuth;

// 创建认证配置
auto config = New<TAuthenticationManagerConfig>();
config->TokenAuthenticator = New<TTokenAuthenticatorConfig>();
config->CookieAuthenticator = New<TCookieAuthenticatorConfig>();

// 创建认证管理器
auto authManager = CreateAuthenticationManager(config);

// 执行认证
auto request = TAuthenticationRequest{
    .Token = "user_token",
    .UserIP = TNetAddress::FromString("127.0.0.1")
};
auto result = WaitFor(authManager->Authenticate(request))
    .ValueOrThrow();
```

### Secret Vault 使用

```cpp
// 创建 Secret Vault 服务
auto vaultConfig = New<TDefaultSecretVaultServiceConfig>();
vaultConfig->Address = "vault.example.com";
vaultConfig->Token = "vault_token";

auto vaultService = CreateDefaultSecretVaultService(vaultConfig);

// 获取密钥
auto secret = WaitFor(vaultService->GetSecret("secret_id"))
    .ValueOrThrow();
```

### Cookie 管理

```cpp
// 创建 Cookie 管理器
auto cookieConfig = New<TCypressCookieManagerConfig>();
auto cookieManager = CreateCypressCookieManager(cookieConfig);

// 创建新 Cookie
auto cookie = WaitFor(cookieManager->CreateCookie(generatorConfig))
    .ValueOrThrow();
```

## 配置选项

### 认证缓存配置

- `EnableAuthCache` - 是否启用认证缓存
- `AuthCacheExpireTime` - 缓存过期时间
- `MaxAuthCacheSize` - 最大缓存大小

### Blackbox 配置

- `BlackboxHost` - Blackbox 服务地址
- `EnableBlackboxUserExistenceCheck` - 启用用户存在性检查
- `RequestTimeout` - 请求超时时间

### Secret Vault 配置

- `VaultAddress` - Vault 服务地址
- `VaultToken` - 认证令牌
- `BatchSize` - 批处理大小
- `EnableCaching` - 是否启用缓存

## 安全考虑

1. **令牌安全**：所有令牌在传输和存储时都应加密
2. **缓存安全**：敏感信息不应长期缓存
3. **网络安全**：使用 HTTPS 进行外部服务通信
4. **访问控制**：实施严格的访问控制策略

## 性能优化

- **认证缓存**：减少重复认证请求
- **批处理**：合并多个请求提高效率
- **异步处理**：所有操作都是异步的
- **连接池**：复用外部服务连接

## 依赖项

- YTsaurus 核心库
- YTsaurus TVM 库
- OpenSSL（加密支持）
- cURL（HTTP 客户端）
- 外部认证服务（Blackbox、Yandex Cloud IAM）

## 测试

单元测试位于 `unittests/` 目录：

```bash
# 运行认证服务器测试
ninja test_auth_server
```

## 错误处理

所有认证操作都返回 `TFuture<TErrorOr<T>>`，支持：
- 网络错误处理
- 认证失败处理
- 超时处理
- 重试机制

## 扩展性

系统设计支持：
- 添加新的认证方式
- 自定义认证器实现
- 插件式架构
- 配置驱动的功能开关