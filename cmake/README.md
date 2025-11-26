# CMake 构建模块目录 (CMake Build Modules)

## 概述

此目录包含 YTsaurus 项目使用的 CMake 构建系统模块和配置文件。这些模块提供了统一的构建配置，支持跨平台编译和依赖管理。

## 核心模块说明

### 构建基础设施
- **common.cmake** - 通用CMake函数和宏定义，包含项目中广泛使用的工具函数
- **conan_provider.cmake** - Conan包管理器集成模块，负责第三方依赖的获取和管理
- **conan-profiles/** - Conan配置文件目录，包含不同平台的编译配置

### 编译器配置
- **global_flags.cmake** - 全局编译标志配置，定义通用的编译选项
- **global_flags.compiler.gnu.cmake** - GCC编译器特定配置
- **global_flags.compiler.gnu.march.cmake** - GCC架构优化配置
- **global_flags.compiler.msvc.cmake** - MSVC编译器特定配置
- **global_flags.linker.gnu.cmake** - GNU链接器配置
- **global_flags.linker.msvc.cmake** - MSVC链接器配置
- **global_vars.cmake** - 全局变量定义和项目范围配置

### 工具链配置
- **llvm-tools.cmake** - LLVM工具链配置，支持Clang编译器和相关工具
- **shared_libs.cmake** - 共享库构建规则配置

### 依赖管理模块
- **antlr.cmake** - ANTLR解析器生成器集成
- **archive.cmake** - 归档库（libarchive）配置
- **bison.cmake** - Bison解析器生成器配置
- **protobuf.cmake** - Protocol Buffers编译和集成
- **fbs.cmake** - FlatBuffers编译支持

### 查找模块
- **FindIDN.cmake** - GNU libidn库查找模块

## 使用方法

### 构建项目
使用这些模块构建YTsaurus：
```bash
cmake -G Ninja -DCMAKE_BUILD_TYPE=Release \
      -DCMAKE_TOOLCHAIN_FILE=../ytsaurus/clang.toolchain \
      -DCMAKE_PROJECT_TOP_LEVEL_INCLUDES=../ytsaurus/cmake/conan_provider.cmake \
      ../ytsaurus
```

### 添加新依赖
1. 在conanfile.txt中添加新的依赖
2. 创建相应的CMake模块（如需要）
3. 在common.cmake中添加处理逻辑

## 架构特点

### 模块化设计
- 每个工具和依赖都有独立的配置模块
- 清晰的职责分离，便于维护

### 跨平台支持
- 支持Linux（x86_64、aarch64）
- 支持macOS（x86_64、arm64）
- 支持Windows（通过MSVC）

### 依赖管理
- 使用Conan进行第三方依赖管理
- 自动下载和配置依赖库
- 支持版本锁定和自定义配置

## 维护指南

### 添加新工具
1. 创建新的.cmake文件
2. 在common.cmake中添加引用
3. 更新相关文档

### 修改编译选项
- 在global_flags.*文件中修改
- 确保所有平台的兼容性
- 运行完整测试验证

### Conan集成
- 更新conanfile.txt添加新依赖
- 在conan-profiles中配置平台特定选项
- 使用conan_provider.cmake自动处理