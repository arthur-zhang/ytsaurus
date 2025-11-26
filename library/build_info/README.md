# build_info

构建信息管理系统，用于在编译时嵌入版本、构建时间、编译器信息等元数据到二进制文件中。

## 功能描述

build_info 提供了一套机制，可以在程序编译时自动收集和嵌入构建相关的信息，包括版本号、构建时间、Git 提交哈希、编译器版本、编译选项等。这些信息在运行时可以通过 API 访问，用于调试、版本管理和问题排查。

## 核心特性

- **自动收集**：编译时自动收集构建信息
- **多格式支持**：支持 CMake 和 YaMake 构建系统
- **模板生成**：使用模板生成源文件
- **运行时访问**：提供 C++ API 访问构建信息
- **跨平台**：支持 Linux、macOS、Windows 等平台
- **版本控制**：集成 Git 信息收集

## 主要组件

### build_info.h
定义构建信息的数据结构和访问接口：

```cpp
struct TBuildInfo {
    TString Version;           // 版本号
    TString BuildTime;        // 构建时间
    TString BuildDate;        // 构建日期
    TString Compiler;         // 编译器信息
    TString CompileFlags;     // 编译标志
    TString Target;           // 目标平台
    TString GitCommit;        // Git 提交哈希
    TString GitBranch;        // Git 分支
    TString BuildUser;        // 构建用户
};

// 全局访问函数
const TBuildInfo& GetBuildInfo();
```

### 模板文件
使用 CMake 配置文件模板生成源代码：
- `build_info.cpp.in`：动态构建信息模板
- `sandbox.cpp.in`：沙箱环境信息模板

## 使用示例

### 基本使用
```cpp
#include <library/cpp/build_info/build_info.h>

void PrintBuildInfo() {
    const auto& info = GetBuildInfo();

    Cout << "Version: " << info.Version << Endl;
    Cout << "Build Time: " << info.BuildTime << Endl;
    Cout << "Git Commit: " << info.GitCommit << Endl;
    Cout << "Compiler: " << info.Compiler << Endl;
}
```

### 版本检查
```cpp
bool CheckVersionCompatibility(const TString& minVersion) {
    const auto& info = GetBuildInfo();
    return CompareVersions(info.Version, minVersion) >= 0;
}
```

### 调试信息
```cpp
void PrintDebugInfo() {
    const auto& info = GetBuildInfo();

    Cerr << "=== Build Debug Info ===" << Endl;
    Cerr << "Version: " << info.Version << Endl;
    Cerr << "Build Date: " << info.BuildDate << Endl;
    Cerr << "Compiler: " << info.Compiler << Endl;
    Cerr << "Compile Flags: " << info.CompileFlags << Endl;
    Cerr << "Git Branch: " << info.GitBranch << Endl;
    Cerr << "Git Commit: " << info.GitCommit << Endl;
    Cerr << "Target Platform: " << info.Target << Endl;
}
```

## 构建系统集成

### CMake 集成
```cmake
# 在 CMakeLists.txt 中添加
include(build_info)

# 生成构建信息
configure_file(
    ${CMAKE_CURRENT_SOURCE_DIR}/build_info.cpp.in
    ${CMAKE_CURRENT_BINARY_DIR}/build_info.cpp
    @ONLY
)

# 添加到构建目标
target_sources(my_target PRIVATE
    ${CMAKE_CURRENT_BINARY_DIR}/build_info.cpp
)
```

### YaMake 集成
```make
# ya.make 文件
PEERDIR(
    library/cpp/build_info
)

# 构建信息会自动生成和链接
```

## 配置选项

### 编译时定义
在编译时可以定义以下宏：
- `BUILD_INFO_VERSION`：版本号
- `BUILD_INFO_GIT_COMMIT`：Git 提交哈希
- `BUILD_INFO_GIT_BRANCH`：Git 分支名
- `BUILD_INFO_COMPILER`：编译器信息
- `BUILD_INFO_BUILD_TIME`：构建时间戳

### 模板变量
模板文件支持以下变量：
- `@VERSION@`：版本号
- `@GIT_COMMIT@`：Git 提交哈希
- `@GIT_BRANCH@`：Git 分支
- `@BUILD_TIME@`：构建时间
- `@COMPILER@`：编译器版本
- `@CMAKE_BUILD_TYPE@`：构建类型

## 实现细节

### Git 信息收集
```bash
# 获取 Git 提交哈希
git rev-parse HEAD

# 获取 Git 分支
git rev-parse --abbrev-ref HEAD

# 检查工作目录是否干净
git status --porcelain
```

### 编译器检测
```cpp
#if defined(__clang__)
#define COMPILER_VERSION "Clang " __clang_version__
#elif defined(__GNUC__)
#define COMPILER_VERSION "GCC " __VERSION__
#elif defined(_MSC_VER)
#define COMPILER_VERSION "MSVC " _MSC_VER
#else
#define COMPILER_VERSION "Unknown"
#endif
```

### 平台检测
```cpp
#if defined(__linux__)
#define PLATFORM "Linux"
#elif defined(__APPLE__)
#define PLATFORM "macOS"
#elif defined(_WIN32)
#define PLATFORM "Windows"
#else
#define PLATFORM "Unknown"
#endif
```

## 静态构建信息

build_info_static 提供了静态构建信息版本，适用于不需要动态生成信息的场景：

```cpp
#include <library/cpp/build_info/build_info_static.h>

// 静态版本信息，不依赖生成的文件
extern const char* GetStaticVersion();
extern const char* GetStaticBuildTime();
```

## 应用场景

### 版本管理
- **软件发布**：自动嵌入版本信息
- **兼容性检查**：运行时验证版本兼容
- **发布追踪**：追踪特定构建的功能

### 调试和故障排查
- **问题定位**：通过提交哈希定位问题代码
- **环境信息**：收集构建环境的详细信息
- **重现问题**：确保在相同环境下重现问题

### 监控和日志
- **服务监控**：显示服务版本信息
- **日志记录**：在日志中包含构建信息
- **审计追踪**：记录软件使用情况

### 自动化部署
- **CI/CD 流程**：自动注入构建信息
- **回滚机制**：通过版本信息进行回滚
- **A/B 测试**：区分不同版本的功能

## 最佳实践

### 版本号规范
建议使用语义化版本号：
- 格式：MAJOR.MINOR.PATCH
- 示例：1.2.3、2.0.0-beta.1

### Git 工作流
- **主分支**：使用稳定的版本号
- **开发分支**：包含开发版本标识
- **发布标签**：精确匹配版本号

### 信息安全
- **敏感信息**：避免在构建信息中包含敏感数据
- **生产环境**：考虑限制构建信息的详细程度
- **审计日志**：记录构建信息的访问

## 故障排除

### 常见问题

1. **Git 信息缺失**
   ```bash
   # 确保在 Git 仓库中构建
   git init
   git add .
   git commit -m "Initial commit"
   ```

2. **时间戳不正确**
   ```bash
   # 检查系统时区
   date
   timedatectl status
   ```

3. **编译器信息不准确**
   ```bash
   # 检查编译器版本
   clang --version
   gcc --version
   ```

### 调试技巧

1. **验证生成的信息**
   ```bash
   strings binary_file | grep "Build Info"
   ```

2. **检查模板生成**
   ```bash
   # 查看生成的源文件
   cat build_dir/build_info.cpp
   ```

3. **运行时验证**
   ```cpp
   // 添加断点检查构建信息
   const auto& info = GetBuildInfo();
   assert(!info.Version.empty());
   ```

## 扩展功能

### 自定义构建信息
```cpp
struct TExtendedBuildInfo : public TBuildInfo {
    TString BuildHost;       // 构建主机
    TString BuildUser;       // 构建用户
    TString BuildConfig;     // 构建配置
    TString Dependencies;    // 依赖版本信息
};
```

### 运行时更新
```cpp
class DynamicBuildInfo {
private:
    TBuildInfo info_;
    std::mutex mutex_;

public:
    void Update(const TBuildInfo& newInfo) {
        std::lock_guard<std::mutex> lock(mutex_);
        info_ = newInfo;
    }

    TBuildInfo Get() const {
        std::lock_guard<std::mutex> lock(mutex_);
        return info_;
    }
};
```

### 远程配置
```cpp
// 从远程服务加载版本信息
class RemoteBuildInfo {
public:
    static TBuildInfo LoadFromServer(const TString& serverUrl) {
        // 实现从服务器加载构建信息
    }
};
```