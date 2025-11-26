# 代码生成 API 库

## 概述

这是一个轻量级的 API 库，定义了代码生成系统使用的公共枚举和常量。它为 YTsaurus 的代码生成功能提供了统一的接口定义。

## 功能特性

### 执行后端定义

- **Native 后端**：本地机器码执行
- **WebAssembly 后端**：WASM 虚拟机执行

### 优化级别定义

- **None**：无优化，用于调试
- **Default**：默认优化级别，平衡性能和编译时间

## 文件说明

### 核心文件

- `execution_backend.h` - 定义执行后端和优化级别枚举

### 构建文件

- `CMakeLists.txt` - CMake 构建配置
- `CMakeLists.*.txt` - 针对不同平台的特定构建配置
- `ya.make` - YaMake 构建系统配置

## 枚举定义

### EExecutionBackend

执行后端枚举：

```cpp
DEFINE_ENUM(EExecutionBackend,
    (Native)      // 本地执行，生成原生机器码
    (WebAssembly) // WebAssembly 执行，在 WASM 虚拟机中运行
);
```

### EOptimizationLevel

优化级别枚举：

```cpp
DEFINE_ENUM(EOptimizationLevel,
    (None)     // 无优化，保持原始 IR 结构
    (Default)  // 默认优化，应用标准优化通道
);
```

## 使用示例

### 选择执行后端

```cpp
#include <yt/yt/library/codegen_api/execution_backend.h>

using namespace NYT::NCodegen;

// 创建本地代码生成模块
auto nativeModule = CreateCodeModule(
    EExecutionBackend::Native,
    EOptimizationLevel::Default);

// 创建 WebAssembly 代码生成模块
auto wasmModule = CreateCodeModule(
    EExecutionBackend::WebAssembly,
    EOptimizationLevel::None);  // 调试模式，无优化
```

### 优化级别选择

```cpp
// 调试构建
auto debugModule = CreateCodeModule(
    EExecutionBackend::Native,
    EOptimizationLevel::None);

// 发布构建
auto releaseModule = CreateCodeModule(
    EExecutionBackend::Native,
    EOptimizationLevel::Default);

// 性能关键路径
auto perfModule = CreateCodeModule(
    EExecutionBackend::Native,
    EOptimizationLevel::Default);
```

## 后端特性

### Native 后端

**优点**：
- 最高执行性能
- 直接访问系统资源
- 完整的 C++ 特性支持
- 与现有代码无缝集成

**缺点**：
- 编译时间较长
- 平台相关
- 安全性较低（直接执行机器码）

**适用场景**：
- 性能关键的计算密集型任务
- 需要与 C++ 代码紧密集成的场景
- 批量数据处理

### WebAssembly 后端

**优点**：
- 跨平台兼容性
- 沙箱安全执行
- 较快的编译速度
- 可移植性

**缺点**：
- 执行性能较低
- 系统访问受限
- 与原生代码交互开销

**适用场景**：
- 用户自定义代码执行
- 插件系统
- 安全要求高的环境
- 快速原型开发

## 优化级别详细说明

### None (无优化)

- 保持原始 LLVM IR 结构
- 最快的编译速度
- 便于调试和问题定位
- 生成的代码较大且较慢

**使用时机**：
- 开发和调试阶段
- 需要查看 IR 结构
- 快速迭代验证

### Default (默认优化)

- 应用 LLVM 标准优化通道
- 平衡编译时间和执行性能
- 移除冗余代码
- 内联小函数
- 常量传播
- 死代码消除

**使用时机**：
- 生产环境部署
- 性能敏感的应用
- 发布版本

## 平台支持

### Native 后端支持

- Linux x86_64
- Linux aarch64
- macOS x86_64
- macOS arm64

### WebAssembly 后端支持

- 所有支持 WASM 的平台
- 通过 WASM 运行时执行

## 性能对比

### 执行性能

Native >> WebAssembly

Native 后端通常比 WebAssembly 快 5-20 倍，具体取决于：

- 代码特性
- 优化级别
- 系统架构
- 缓存命中率

### 编译速度

WebAssembly > Native

WebAssembly 通常编译更快，因为：

- 更简单的目标架构
- 较少的优化通道
- 较小的代码生成开销

## 安全考虑

### Native 后端安全风险

- 代码注入攻击
- 内存安全漏洞
- 特权提升
- 侧信道攻击

### 防护措施

- 代码验证
- 沙箱执行
- 权限控制
- 审计日志

## 最佳实践

1. **后端选择**
   - 性能关键使用 Native
   - 安全要求高使用 WebAssembly
   - 开发阶段灵活切换

2. **优化策略**
   - 开发时使用 None
   - 测试时使用 Default
   - 根据性能需求调整

3. **错误处理**
   - 验证后端支持
   - 处理编译失败
   - 提供回退机制

## 依赖项

- LLVM 核心库
- YTsaurus 枚举库
- WebAssembly 运行时（使用 WASM 后端时）

## 未来扩展

可能添加的功能：

- 更多优化级别（Aggressive、Os、Oz）
- GPU 后端支持（CUDA、OpenCL）
- 解释器后端
- AOT（Ahead-Of-Time）编译支持

## 故障排除

### 常见问题

1. **后端不支持**
   ```
   错误：Execution backend not supported
   解决：检查平台支持，安装相应运行时
   ```

2. **优化级别无效**
   ```
   错误：Invalid optimization level
   解决：使用 EOptimizationLevel 枚举值
   ```

3. **编译失败**
   ```
   错误：Code generation failed
   解决：检查 IR 有效性，查看详细错误信息
   ```

## 调试技巧

1. **使用 None 优化级别**便于调试
2. **启用详细日志**查看编译过程
3. **使用 IR 转储**分析生成代码
4. **性能分析**对比不同配置效果