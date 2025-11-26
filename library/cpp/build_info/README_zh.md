# Build Info - 构建信息库

## 项目概述

Build Info 是一个轻量级的构建信息库，用于在编译时注入构建相关信息并在运行时提供访问接口。该库主要用于版本管理、调试、问题诊断和系统监控等场景，为 YTsaurus 分布式系统提供详细的构建环境上下文。

## 功能特性

### 核心功能
- **编译器信息获取**: 获取编译器版本和编译标志
- **构建类型识别**: 识别构建类型（Release、Debug 等）
- **沙箱环境信息**: 获取沙箱任务 ID 和版本信息
- **版本控制集成**: 支持 SVN 版本信息管理
- **运行时查询**: 在运行时动态获取构建信息

### 技术特性
- **零运行时开销**: 编译时注入，运行时只需简单字符串返回
- **跨平台兼容**: 支持多种操作系统和编译器
- **C/C++ 双接口**: 同时支持 C 和 C++ 调用方式
- **安全版本管理**: 使用 Base64 编码保护敏感版本信息

## 文件说明

### 核心头文件
- **`build_info.h`**: 主要接口头文件，提供构建类型获取功能
- **`build_info_static.h`**: 静态构建信息接口，提供编译器相关信息
- **`sandbox.h`**: 沙箱环境信息接口，提供任务 ID 和版本信息

### 实现模板
- **`build_info.cpp.in`**: 构建信息实现的 CMake 模板文件
- **`sandbox.cpp.in`**: 沙箱信息实现的 CMake 模板文件

### 实现文件
- **`build_info_static.cpp`**: 静态构建信息的具体实现
- **`buildinfo_data.h`**: 编译时生成的构建数据头文件（通常由构建系统生成）

### 构建配置
- **`CMakeLists.txt`**: CMake 构建配置，处理模板文件替换
- **`ya.make`**: YaTool 构建系统配置

## 核心接口

### 构建信息接口
```cpp
// 获取构建类型 (Release, Debug, RelWithDebInfo 等)
const char* GetBuildType();

// 获取编译器版本
const char* GetCompilerVersion();

// 获取编译标志
const char* GetCompilerFlags();

// 获取完整构建信息
const char* GetBuildInfo();
```

### 沙箱环境接口
```cpp
// 获取沙箱任务 ID
const char* GetSandboxTaskId();

// 获取 Kosher SVN 版本（Base64 解码）
const char* GetKosherSvnVersion();
```

## 使用示例

### 基本构建信息查询
```cpp
#include <library/cpp/build_info/build_info.h>

void PrintBuildInfo() {
    // 输出构建类型
    std::cout << "构建类型: " << GetBuildType() << std::endl;

    // 输出编译器信息
    std::cout << "编译器版本: " << GetCompilerVersion() << std::endl;
    std::cout << "编译标志: " << GetCompilerFlags() << std::endl;

    // 输出完整构建信息
    std::cout << "构建信息: " << GetBuildInfo() << std::endl;
}
```

### 应用程序版本信息
```cpp
#include <library/cpp/build_info/build_info.h>
#include <library/cpp/build_info/sandbox.h>

class ApplicationInfo {
public:
    void PrintVersion() const {
        std::cout << "=== 应用程序版本信息 ===" << std::endl;
        std::cout << "构建类型: " << GetBuildType() << std::endl;
        std::cout << "编译器: " << GetCompilerVersion() << std::endl;

        if (strlen(GetSandboxTaskId()) > 0) {
            std::cout << "沙箱任务 ID: " << GetSandboxTaskId() << std::endl;
        }

        if (strlen(GetKosherSvnVersion()) > 0) {
            std::cout << "SVN 版本: " << GetKosherSvnVersion() << std::endl;
        }

        std::cout << "编译时间: " << __DATE__ << " " << __TIME__ << std::endl;
    }

    bool IsDebugBuild() const {
        return strcmp(GetBuildType(), "Debug") == 0;
    }

    bool IsProductionBuild() const {
        return strcmp(GetBuildType(), "Release") == 0;
    }
};
```

### 错误诊断和调试
```cpp
#include <library/cpp/build_info/build_info.h>

void DiagnoseEnvironment() {
    std::cout << "=== 环境诊断信息 ===" << std::endl;

    // 检查构建类型
    const char* buildType = GetBuildType();
    if (strcmp(buildType, "Debug") == 0) {
        std::cout << "警告: 运行在 Debug 模式，性能可能受影响" << std::endl;
    }

    // 输出编译器信息用于问题报告
    std::cout << "编译器信息: " << GetCompilerVersion() << std::endl;
    std::cout << "编译标志: " << GetCompilerFlags() << std::endl;

    // 输出完整构建上下文
    std::cout << "完整构建信息: " << GetBuildInfo() << std::endl;
}
```

### 日志系统集成
```cpp
#include <library/cpp/build_info/build_info.h>

class EnhancedLogger {
public:
    void LogWithContext(const std::string& message, const std::string& level = "INFO") {
        auto now = std::chrono::system_clock::now();
        auto time_t = std::chrono::system_clock::to_time_t(now);

        std::cout << "[" << std::put_time(std::localtime(&time_t), "%Y-%m-%d %H:%M:%S") << "]"
                  << "[" << level << "]"
                  << "[Build:" << GetBuildType() << "]"
                  << " " << message << std::endl;
    }

    void LogErrorWithContext(const std::string& error) {
        LogWithContext("错误: " + error, "ERROR");
        LogWithContext("构建信息: " + std::string(GetBuildInfo()), "DEBUG");
    }
};
```

## 实现原理

### 1. 编译时注入机制
```cmake
# CMake 构建时处理模板
configure_file(
    ${CMAKE_CURRENT_SOURCE_DIR}/build_info.cpp.in
    ${CMAKE_CURRENT_BINARY_DIR}/build_info.cpp
    @ONLY
)

# 替换占位符
# @BUILD_TYPE@ -> 构建类型 (Release/Debug)
# @SANDBOX_TASK_ID@ -> 沙箱任务 ID
# @KOSHER_SVN_VERSION@ -> SVN 版本（Base64 编码）
```

### 2. 模板变量替换
- **@BUILD_TYPE@**: CMAKE_BUILD_TYPE 变量值
- **@SANDBOX_TASK_ID@**: 沙箱环境任务标识
- **@KOSHER_SVN_VERSION@**: SVN 版本信息（Base64 编码）

### 3. 版本信息安全处理
```cpp
// 安全的版本信息解码
class TKosherVersionHolder {
    const char* Version() const {
        TString version = "@KOSHER_SVN_VERSION@";  // Base64 编码
        SubstGlobal(version, ".", "=");  // 简单混淆
        Version_ = Base64Decode(version);  // 解码
        return Version_.c_str();
    }
};
```

### 4. 条件编译支持
```cpp
#if defined(BUILD_COMPILER_VERSION)
    return BUILD_COMPILER_VERSION;
#else
    return "";
#endif
```

## 构建系统配置

### CMake 集成
```cmake
# 设置构建信息变量
set(BUILD_COMPILER_VERSION "${CMAKE_CXX_COMPILER_ID} ${CMAKE_CXX_COMPILER_VERSION}")
set(BUILD_COMPILER_FLAGS "${CMAKE_CXX_FLAGS}")

# 配置模板文件
configure_file(
    "${CMAKE_CURRENT_SOURCE_DIR}/build_info.cpp.in"
    "${CMAKE_CURRENT_BINARY_DIR}/build_info.cpp"
    @ONLY
)

# 添加到构建目标
target_sources(your_target PRIVATE
    "${CMAKE_CURRENT_BINARY_DIR}/build_info.cpp"
)
```

### YaTool 集成
```make
PEERDIR(
    library/cpp/build_info
)

CPPFLAGS += -DBUILD_COMPILER_VERSION="\"$(CXX_VERSION)\""
CPPFLAGS += -DBUILD_COMPILER_FLAGS="\"$(CXX_FLAGS)\""
```

## 应用场景

### 1. 版本管理
```cpp
// 软件版本报告
void GenerateVersionReport() {
    std::cout << "软件版本信息:" << std::endl;
    std::cout << "- 构建类型: " << GetBuildType() << std::endl;
    std::cout << "- 编译器: " << GetCompilerVersion() << std::endl;
    std::cout << "- SVN 版本: " << GetKosherSvnVersion() << std::endl;
}
```

### 2. 问题诊断
```cpp
// 生产环境问题诊断
void DiagnoseProductionIssue() {
    if (strcmp(GetBuildType(), "Debug") == 0) {
        LogWarning("生产环境运行了 Debug 构建");
    }

    // 记录完整的构建上下文
    LogInfo("问题发生时的构建环境: " + std::string(GetBuildInfo()));
}
```

### 3. 性能分析
```cpp
// 性能测试上下文记录
class PerformanceTester {
public:
    void RunBenchmark() {
        std::cout << "=== 性能测试环境 ===" << std::endl;
        std::cout << "构建类型: " << GetBuildType() << std::endl;
        std::cout << "编译优化: " << GetCompilerFlags() << std::endl;

        // 运行基准测试...
    }
};
```

### 4. 兼容性检查
```cpp
// 运行时兼容性验证
bool CheckBuildCompatibility() {
    const char* compiler = GetCompilerVersion();

    // 检查编译器版本兼容性
    if (strstr(compiler, "clang") && !strstr(compiler, "18.")) {
        std::cerr << "警告: 推荐使用 Clang 18+" << std::endl;
        return false;
    }

    return true;
}
```

### 5. 自动化测试
```cpp
// 测试环境验证
class TestEnvironmentValidator {
public:
    bool ValidateEnvironment() {
        // 验证构建类型
        const char* buildType = GetBuildType();
        if (strcmp(buildType, "Debug") != 0) {
            std::cerr << "错误: 测试需要 Debug 构建" << std::endl;
            return false;
        }

        // 验证编译器标志包含调试信息
        const char* flags = GetCompilerFlags();
        if (!strstr(flags, "-g") && !strstr(flags, "-O0")) {
            std::cerr << "警告: 编译标志可能不适合调试" << std::endl;
        }

        return true;
    }
};
```

## 注意事项

### 1. 信息安全
- SVN 版本使用 Base64 编码和简单混淆
- 避免在构建信息中包含敏感数据
- 生产环境注意信息泄露风险

### 2. 性能考虑
- 字符串在首次访问时计算，后续直接返回
- 避免在热路径中频繁调用这些函数
- 考虑缓存构建信息字符串

### 3. 跨平台兼容
- 不同平台编译器信息格式可能不同
- 注意字符串编码和字符集问题
- 测试各平台的构建信息正确性

### 4. 维护建议
- 保持构建信息的一致性和完整性
- 定期更新编译器版本信息
- 建立构建信息的版本控制流程

这个库为 YTsaurus 系统提供了重要的构建上下文信息，对于系统维护、问题诊断和版本管理具有关键作用。通过在编译时注入相关信息，可以在运行时提供丰富的环境上下文，帮助开发者更好地理解和维护分布式系统。