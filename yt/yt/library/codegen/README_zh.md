# 代码生成库

## 概述

这个库提供了基于 LLVM 的动态代码生成功能，用于在运行时生成和编译 C++ 代码。它主要用于 YTsaurus 中的性能关键路径，通过 JIT（Just-In-Time）编译生成优化的机器码。

## 功能特性

### LLVM 集成

- **动态编译**：运行时编译 LLVM IR 到机器码
- **优化支持**：支持多种 LLVM 优化级别
- **多后端支持**：支持不同的执行后端
- **符号管理**：完整的符号注册和查找机制

### 类型系统

- **类型构建器**：C++ 类型到 LLVM 类型的映射
- **函数类型**：自动生成函数类型签名
- **符号修饰**：支持 C++ 名称修饰和去修饰

### 内存安全

- **MSAN 支持**：MemorySanitizer 集成
- **安全执行**：隔离的执行环境
- **错误处理**：完善的错误检测和报告

## 文件说明

### 核心模块

- `module.h/cpp` - LLVM 模块封装，主要的代码生成接口
- `module-inl.h` - 内联实现
- `routine_registry.h/cpp` - 例程注册表，管理可调用的函数

### 构建器

- `builder_base.h/cpp` - 基础构建器
- `builder_base-inl.h` - 内联实现
- `type_builder.h` - 类型构建器，定义类型映射

### 辅助文件

- `caller.h` - 调用器接口
- `init.h/cpp` - 初始化代码
- `private.h` - 私有定义
- `public.h` - 公共接口

### 工具类

- `llvm_migrate_helpers.h` - LLVM 迁移辅助工具
- `msan.h/cpp` - MemorySanitizer 支持

## 核心接口

### TCGModule

代码生成模块：

```cpp
class TCGModule : public TRefCounted {
public:
    static TCGModulePtr Create(
        TRoutineRegistry* routineRegistry,
        EExecutionBackend backend = EExecutionBackend::Native,
        EOptimizationLevel optimizationLevel = EOptimizationLevel::Default,
        const std::string& moduleName = "module");

    llvm::LLVMContext& GetContext();
    llvm::Module* GetModule();

    // 编译模块
    void Compile();

    // 获取编译后的函数指针
    template <typename T>
    T GetCompiledFunction(const std::string& name);
};
```

### TRoutineRegistry

例程注册表：

```cpp
class TRoutineRegistry {
public:
    // 注册 C++ 函数
    template <class TResult, class... TArgs>
    void RegisterRoutine(const char* symbol, TResult(*fp)(TArgs...));

    // 获取函数地址
    uint64_t GetAddress(const std::string& symbol) const;

    // 获取类型构建器
    TValueTypeBuilder GetTypeBuilder(const std::string& symbol) const;
};
```

### TTypeBuilder

类型构建器模板：

```cpp
// 基础类型特化
template <>
class TTypeBuilder<int> {
public:
    static llvm::Type* Get(llvm::LLVMContext& context);
};

// 复合类型
template <>
class TTypeBuilder<std::vector<int>> {
public:
    static llvm::Type* Get(llvm::LLVMContext& context);
};
```

## 使用示例

### 基本代码生成

```cpp
#include <yt/yt/library/codegen/public.h>

using namespace NYT::NCodegen;

// 1. 创建例程注册表
TRoutineRegistry registry;

// 2. 注册可调用函数
registry.RegisterRoutine("my_function", &MyFunction);

// 3. 创建代码生成模块
auto module = TCGModule::Create(
    &registry,
    EExecutionBackend::Native,
    EOptimizationLevel::O2);

// 4. 生成 LLVM IR
auto* function = llvm::Function::Create(
    /* function type */,
    llvm::Function::ExternalLinkage,
    "generated_function",
    module->GetModule());

// 5. 编译模块
module->Compile();

// 6. 获取编译后的函数
auto compiledFn = module->GetCompiledFunction<int(int)>("generated_function");
int result = compiledFn(42);
```

### 类型构建示例

```cpp
// 构建函数类型
using FunctionType = int(double, const char*);
auto* llvmType = TFunctionTypeBuilder<FunctionType>::Get(context);

// 构建复杂类型
auto* vectorType = TTypeBuilder<std::vector<int>>::Get(context);
auto* mapType = TTypeBuilder<THashMap<TString, int>>::Get(context);
```

### 符号管理

```cpp
// 符号修饰
std::string mangled = MangleSymbol("MyFunction");
std::string demangled = DemangleSymbol(mangled);

// 注册和查找符号
uint64_t address = registry.GetAddress("my_function");
auto typeBuilder = registry.GetTypeBuilder("my_function");
```

## 执行后端

### Native 后端

- 使用 LLVM JIT 编译器
- 直接生成机器码
- 最高性能

### Interpretive 后端

- LLVM 解释器执行
- 更好的调试支持
- 较低性能但更安全

## 优化级别

- `None` - 无优化
- `Less` - 基础优化
- `Default` - 默认优化（推荐）
- `Aggressive` - 激进优化

## 内存安全

### MSAN 集成

```cpp
// 启用 MSAN 支持
EnableMSAN();

// 标记内存已初始化
MarkMemoryInitialized(ptr, size);

// 检查内存是否已初始化
bool isInitialized = IsMemoryInitialized(ptr, size);
```

## 实现原理

### 编译流程

1. **IR 生成**：生成 LLVM 中间表示
2. **优化**：应用 LLVM 优化通道
3. **代码生成**：编译到目标机器码
4. **链接**：解决符号引用
5. **加载**：加载到可执行内存

### 类型映射

- C++ 基础类型 → LLVM 类型
- STL 容器 → 自定义结构
- 指针和引用 → LLVM 指针类型
- 函数签名 → LLVM 函数类型

### 符号解析

- C++ 名称修饰
- 动态符号查找
- 延迟解析机制

## 性能考虑

### 热路径优化

- 预编译常用函数
- 缓存编译结果
- 批量编译优化

### 内存管理

- LLVM 对象池
- 自动垃圾回收
- 内存泄漏检测

## 调试支持

### IR 转储

```cpp
// 打印 LLVM IR
module->GetModule()->print(llvm::errs(), nullptr);

// 验证 IR
bool isValid = llvm::verifyModule(*module->GetModule());
```

### 调试信息

- 源码级调试
- 符号信息生成
- 堆栈跟踪支持

## 依赖项

- LLVM 库（>= 15.0）
- YTsaurus 核心库
- C++20 编译器
- 系统链接器

## 平台支持

- Linux x86_64
- Linux aarch64
- macOS x86_64
- macOS arm64

## 最佳实践

1. **模块设计**
   - 保持模块小型化
   - 明确的接口边界
   - 版本化管理

2. **性能优化**
   - 选择合适的优化级别
   - 避免过度编译
   - 使用内联优化

3. **错误处理**
   - 验证 IR 正确性
   - 处理编译错误
   - 提供回退机制

4. **资源管理**
   - 及时释放资源
   - 避免内存泄漏
   - 监控内存使用

## 安全注意事项

1. **代码注入防护**
   - 验证生成的代码
   - 限制访问权限
   - 使用沙箱执行

2. **内存安全**
   - 启用 ASAN/MSAN
   - 检查边界访问
   - 避免悬垂指针

## 故障排除

### 常见问题

1. **编译失败**
   - 检查 IR 有效性
   - 验证类型匹配
   - 查看编译日志

2. **链接错误**
   - 确认符号存在
   - 检查名称修饰
   - 验证签名匹配

3. **运行时错误**
   - 启用调试模式
   - 检查内存访问
   - 查看调用栈

### 调试工具

- `llvm-as`/`llvm-dis` - IR 汇编/反汇编
- `opt` - LLVM 优化器
- `llc` - LLVM 静态编译器
- `lli` - LLVM 解释器