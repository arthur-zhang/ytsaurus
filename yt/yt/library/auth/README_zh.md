# YTsaurus 认证库 (NAuth)

## 项目描述

`yt/library/auth` 是 YTsaurus 分布式存储和计算平台的核心认证库，提供统一的身份验证和凭证管理功能。该库支持多种认证机制，包括令牌认证、会话认证、TVM票据认证等，为YTsaurus客户端和服务端提供安全可靠的身份验证解决方案。

## 主要功能

### 1. 令牌管理
- **令牌验证**：严格的格式验证，确保令牌只包含安全的可打印ASCII字符
- **自动令牌发现**：按优先级从多个来源自动加载令牌
- **文件令牌加载**：支持从指定文件路径读取令牌

### 2. 认证选项配置
- 灵活的认证参数配置
- 用户名和用户标签管理
- 多种认证凭据支持（令牌、会话ID、票据等）

### 3. 凭证注入通道
- **装饰器模式**：为RPC通道透明地添加认证信息
- **多种认证方式**：
  - 用户名注入
  - 令牌注入
  - 会话Cookie注入
  - TVM服务票据注入
  - 用户票据注入

## 文件说明

### 核心文件

| 文件 | 描述 |
|------|------|
| `auth.h/auth.cpp` | 认证核心功能，包括令牌验证和加载 |
| `authentication_options.h/authentication_options.cpp` | 认证选项结构体和管理功能 |
| `credentials_injecting_channel.h/credentials_injecting_channel.cpp` | 凭证注入通道实现 |
| `public.h` | 公共接口声明 |

### 构建文件

| 文件 | 描述 |
|------|------|
| `CMakeLists.txt` | CMake构建配置 |
| `CMakeLists.*.txt` | 平台特定构建配置 |
| `ya.make` | YaTool构建系统配置 |

### 测试文件

| 文件 | 描述 |
|------|------|
| `unittests/auth_ut.cpp` | 单元测试，覆盖主要功能 |
| `unittests/CMakeLists.*.txt` | 测试构建配置 |

## 使用方法

### 基本令牌认证

```cpp
#include <yt/yt/library/auth/auth.h>
#include <yt/yt/library/auth/authentication_options.h>
#include <yt/yt/library/auth/credentials_injecting_channel.h>

// 1. 自动加载令牌
auto token = NYT::NAuth::LoadToken();
if (token) {
    std::cout << "Loaded token: " << *token << std::endl;
}

// 2. 手动验证令牌
try {
    NYT::NAuth::ValidateToken("your-token-here");
    std::cout << "Token is valid" << std::endl;
} catch (const std::exception& ex) {
    std::cerr << "Invalid token: " << ex.what() << std::endl;
}
```

### 创建认证通道

```cpp
// 3. 使用令牌创建认证通道
NYT::NAuth::TAuthenticationOptions options;
options.Token = "your-auth-token";
options.User = "username";
options.UserTag = "client-tag";

auto underlyingChannel = CreateRpcChannel("cluster.example.com");
auto authChannel = NYT::NAuth::CreateCredentialsInjectingChannel(
    underlyingChannel,
    options);
```

### TVM服务票据认证

```cpp
// 4. 使用TVM服务票据认证
NYT::NAuth::TAuthenticationOptions options;
options.ServiceTicketAuth = serviceTicketAuth; // TVM服务票据对象
options.User = "service-name";

auto channel = NYT::NAuth::CreateServiceTicketInjectingChannel(
    underlyingChannel,
    options);
```

## 令牌来源

`LoadToken()` 函数按以下优先级顺序查找令牌：

1. **`YT_TOKEN`** 环境变量
2. **`YT_SECURE_VAULT_YT_TOKEN`** 环境变量（YT操作内部使用）
3. **`YT_TOKEN_PATH`** 环境变量指向的文件路径
4. **`$HOME/.yt/token`** 默认令牌文件

### 安全建议

- 对于YT操作内部，优先使用 `YT_SECURE_VAULT_YT_TOKEN` 避免令牌在UI中暴露
- 令牌文件权限应设置为仅当前用户可读（`chmod 600`）
- 避免在命令行历史或日志中暴露令牌

## 依赖项

### 内部依赖
- `yt/yt/core/rpc` - RPC通信框架
- `yt/yt/library/tvm` - TVM认证库
- `yt/yt/core/misc` - 核心工具和错误处理
- `yt_proto/yt/core/rpc/proto` - RPC协议定义

### 外部依赖
- C++17 标准库（`std::optional`, `std::string`）
- 系统库：环境变量处理、文件系统操作
- 构建工具：CMake 3.22+, Ninja, 或 YaTool

### 平台支持
- Linux (x86_64, aarch64)
- macOS (x86_64, arm64)

## 实现原理

### 1. 令牌验证机制
- 只接受ASCII字符范围 0x21-0x7e（可打印字符，排除空格）
- 逐字符验证，提供详细的错误信息（字符位置和值）

### 2. 装饰器模式
- 凭证注入通道作为底层RPC通道的装饰器
- 在发送请求前自动注入认证信息
- 支持多种认证方式的透明切换

### 3. 工厂模式
- `CreateCredentialsInjectingChannel()` 根据配置自动选择合适的注入通道
- `CreateServiceTicketInjectingChannelFactory()` 批量创建相同认证配置的通道

### 4. 安全设计
- 多层认证机制支持
- 敏感信息的安全处理
- YT操作环境下的特殊安全考虑

## 测试

运行单元测试：

```bash
# 使用 CMake
cd build
ninja yt-library-auth-tests

# 使用 YaTool
ya make yt/yt/library/auth -t tests

# 运行测试
./yt/yt/library/auth/unittests/auth_ut
```

测试覆盖：
- 令牌验证的边界情况
- 文件令牌加载功能
- 多种令牌来源的优先级处理
- 错误处理机制

## 注意事项

1. **安全性**：令牌包含敏感信息，请妥善保管
2. **性能**：令牌验证在每次调用时进行，避免在热路径中频繁调用
3. **兼容性**：不同认证方式可能需要服务端相应支持
4. **错误处理**：所有认证相关错误都通过异常机制报告

## 相关模块

- `yt/yt/core/rpc` - RPC通信框架
- `yt/yt/library/tvm` - TVM认证集成
- `yt/yt/server/*` - 服务端认证处理
- `yt/yt/client/*` - 客户端认证实现