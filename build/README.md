# 构建系统目录 (Build System)

## 概述

此目录包含 YTsaurus 项目的构建系统配置和支持文件。构建系统负责管理项目的编译、链接、打包和部署流程，确保在各个平台上的一致性和可靠性。

## 目录结构

### 核心配置
- **CMakeLists.txt** - 主 CMake 配置文件，定义构建目标和规则
- **ya.conf.json** - Yandex 构建系统配置，包含构建参数和依赖
- **mapping.conf.json** - 构建映射配置，定义源码到目标的映射关系
- **sanitize-blacklist.txt** - 清理器黑名单，排除不需要检查的文件

### 平台支持 (platform/)
多平台构建支持：
- **配置文件** - 各平台特定的构建配置
- **工具链** - 不同平台的编译器和工具链配置
- **架构支持** - x86_64、aarch64、arm64 等架构支持

#### 支持的平台
- Linux (x86_64, aarch64)
- macOS (Intel, Apple Silicon)
- Windows (部分支持)

### 插件系统 (plugins/)
构建插件和扩展：
- **编译器插件** - 编译器特定配置
- **工具插件** - 构建工具集成
- **检查插件** - 代码质量检查

### 外部资源 (external_resources/)
外部依赖和资源：
- **第三方库** - 外部库的构建配置
- **资源文件** - 构建时需要的资源
- **下载脚本** - 依赖下载脚本

### 预构建组件 (prebuilt/)
预编译的组件：
- **二进制文件** - 预编译的可执行文件
- **库文件** - 预编译的库
- **工具链** - 预构建的工具链

### 构建脚本 (scripts/)
辅助构建脚本：
- **编译脚本** - 自动化编译流程
- **测试脚本** - 构建后测试
- **打包脚本** - 创建发布包

## 构建流程

### 配置阶段
```bash
# 基本配置
cmake -G Ninja -DCMAKE_BUILD_TYPE=Release \
      -DCMAKE_TOOLCHAIN_FILE=../ytsaurus/clang.toolchain \
      -DCMAKE_PROJECT_TOP_LEVEL_INCLUDES=../ytsaurus/cmake/conan_provider.cmake \
      ../ytsaurus
```

### 编译阶段
```bash
# 编译所有目标
ninja

# 编译特定目标
ninja ytserver-all
ninja ytsaurus-client

# 并行编译
ninja -j$(nproc)
```

### 安装阶段
```bash
# 安装到指定目录
ninja install
DESTDIR=/path/to/install ninja install
```

## 构建选项

### 主要选项
- **CMAKE_BUILD_TYPE** - 构建类型 (Release/Debug/RelWithDebInfo)
- **CMAKE_INSTALL_PREFIX** - 安装前缀
- **BUILD_TESTS** - 是否构建测试
- **ENABLE_BENCHMARKS** - 是否启用基准测试

### 高级选项
- **USE_SYSTEM_LIBS** - 使用系统库
- **ENABLE_PYTHON** - 启用 Python 绑定
- **ENABLE_JAVA** - 启用 Java 组件
- **ENABLE_GO** - 启用 Go 组件

## 依赖管理

### Conan 集成
使用 Conan 进行 C++ 依赖管理：
- 自动下载依赖
- 版本锁定
- 跨平台支持

### 配置文件依赖
- **clang.toolchain** - Clang 工具链配置
- **conan_provider.cmake** - Conan 集成配置

## 平台特定配置

### Linux
- 使用 GCC 或 Clang
- 支持 glibc 和 musl
- 支持多种 Linux 发行版

### macOS
- 使用 Clang
- 支持 Xcode 工具链
- 通用二进制支持

### Windows
- 实验性支持
- 使用 MSVC 或 Clang
- MinGW 支持

## 构建优化

### 性能优化
- **链接时优化 (LTO)** - 全程序优化
- **并行编译** - 多核并行构建
- **预编译头** - 减少编译时间
- **增量构建** - 只编译变更部分

### 内存优化
- **ccache** - 编译缓存
- **并行链接** - 并行链接支持
- **内存限制** - 编译器内存限制

## 调试支持

### Debug 构建
```bash
cmake -DCMAKE_BUILD_TYPE=Debug \
      -DENABLE_SANITIZERS=ON \
      -DDEBUG_SYMBOLS=ON \
      ../ytsaurus
```

### 清理器支持
- **AddressSanitizer** - 内存错误检测
- **ThreadSanitizer** - 并发错误检测
- **MemorySanitizer** - 未初始化内存检测
- **UndefinedBehaviorSanitizer** - 未定义行为检测

## 测试集成

### 单元测试
```bash
# 运行 C++ 测试
./yt/yt/scripts/run_unittests.sh

# 运行集成测试
./yt/yt/tests/integration/run_tests.sh -m opensource
```

### Python 测试
```bash
./yt/yt/scripts/run_python_tests.sh
```

## 持续集成

### CI 配置
- **GitHub Actions** - 主要 CI 平台
- **TeamCity** - 内部 CI 系统
- **Jenkins** - 部分 CI 任务

### 构建矩阵
- 多平台并行构建
- 多编译器测试
- 不同配置组合

## 发布流程

### 版本构建
```bash
# 创建发布构建
cmake -DCMAKE_BUILD_TYPE=Release \
      -DVERSION_STRING=v1.0.0 \
      ../ytsaurus
ninja package
```

### 打包
- **源码包** - Source Distribution
- **二进制包** - Binary Distribution
- **Docker 镜像** - Container Images

## 故障排除

### 常见问题
1. **依赖缺失** - 检查 Conan 配置
2. **编译错误** - 查看详细日志
3. **链接失败** - 检查库路径
4. **测试失败** - 检查环境配置

### 调试技巧
- 使用详细输出 `ninja -v`
- 检查 CMake 缓存
- 查看构建日志
- 使用构建分析工具

## 维护指南

### 添加新目标
1. 在相应目录添加 CMakeLists.txt
2. 定义目标和依赖
3. 更新顶级配置
4. 测试构建

### 更新依赖
1. 修改 conanfile.txt
2. 更新版本约束
3. 测试新版本
4. 更新文档

### 性能调优
1. 分析构建时间
2. 优化并行度
3. 使用缓存
4. 减少依赖