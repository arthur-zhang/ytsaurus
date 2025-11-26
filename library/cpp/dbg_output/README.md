# dbg_output 调试输出模块

[dbg_output](.) 是 YTsaurus 中专门用于调试和开发阶段结构化数据输出的 C++ 库。它提供了强大且灵活的数据转储功能，支持复杂的嵌套数据结构、智能指针、容器类型的高效展示，以及可定制的颜色方案。

## 📋 项目描述

`dbg_output` 模块为 C++ 开发者提供了一个优雅的调试输出解决方案，能够以结构化、可读性强的格式展示复杂的数据结构。该模块特别适合在开发和调试过程中快速了解程序状态，包括容器内容、指针关系、对象层次结构等。

### 核心价值

- **智能数据识别**：自动识别并格式化各种标准容器和智能指针
- **深度递归支持**：安全处理复杂的指针引用和循环引用
- **可定制输出**：支持自定义颜色方案和输出格式
- **类型安全**：基于模板的类型安全实现
- **高性能**：编译时优化，运行时开销最小

## 🚀 核心特性

### 1. 多层次输出支持

模块提供两种主要的输出模式：

- **DbgDump**：浅层转储，显示指针地址和基本信息
- **DbgDumpDeep**：深度转储，递归展开指针指向的内容

### 2. 全面的类型支持

#### 标准容器类型
- **序列容器**：`TVector`, `std::vector`, `TArrayRef`, `std::array`, `TDeque`, `TList`
- **关联容器**：`TMap`, `TMultiMap`, `TSet`, `TMultiSet`
- **哈希容器**：`THashMap`, `THashMultiMap`, `THashSet`, `THashMultiSet`

#### 智能指针
- `TAutoPtr`：自动指针
- `THolder`：持有者指针
- `TIntrusivePtr`：侵入式指针
- `TSharedPtr`：共享指针
- `TCopyPtr`：复制指针

#### 基础类型
- **字符串**：`TString`, `TUtf16String`, `const char*`, `const wchar16*`
- **字符**：`char`, `wchar16`，特殊处理避免显示为原始字符
- **数值类型**：包括 `ui8`, `i8` 等小整数类型
- **键值对**：`std::pair` 的优雅展示

### 3. 可定制颜色方案

#### 内置颜色方案
- **TPlain**：无颜色方案，适合日志文件和管道输出
- **TEyebleed**：彩色方案，为终端输出提供丰富的视觉区分

#### 颜色元素
- **Markup**：标记颜色（如括号、分隔符）
- **String**：字符串内容颜色
- **Literal**：字面量值颜色
- **Key/Value**：键值对的不同背景色
- **Reset**：颜色重置

## 🏗️ 主要组件

### 核心头文件

1. **dump.h**：主要接口定义，提供 `DbgDump` 和 `DbgDumpDeep` 函数
2. **engine.h**：底层转储引擎，定义 `TDumpBase` 和相关基础设施
3. **dumpers.h**：标准类型的转储器实现
4. **auto.h**：智能指针类型的转储器
5. **colorscheme.h**：颜色方案系统

### 关键类和函数

#### TDumpBase
所有转储器的基础类，提供：
- 输出流管理
- 缩进级别控制
- 字符串、字符、原始文本输出
- 指针显示支持

#### TDumper 特化模板
为不同类型提供专门的输出格式化：
```cpp
template <class T>
struct TDumper {
    template <class S>
    static inline void Dump(S& s, const T& t);
};
```

#### 辅助工具
- **TIndentScope**：自动管理缩进级别的RAII类
- **TRawLiteral**：原始文本输出包装器
- **TIndentNewLine**：格式化换行和缩进

## 💡 使用示例

### 基础用法

```cpp
#include <library/cpp/dbg_output/dump.h>
#include <util/stream/str.h>

// 基本数据结构输出
TVector<int> numbers = {1, 2, 3, 4, 5};
Cout << DbgDump(numbers) << Endl;
// 输出: [1, 2, 3, 4, 5]

// 带缩进的格式化输出
TMap<TString, int> config = {
    {"port", 8080},
    {"timeout", 30}
};
Cout << DbgDump(config).SetIndent(true) << Endl;
```

### 深度转储示例

```cpp
struct Node {
    int value;
    Node* next;
};

Node node1{1, nullptr};
Node node2{2, &node1};
Node node3{3, &node2};

// 浅层转储：只显示指针地址
Cout << DbgDump(node3) << Endl;

// 深度转储：递归展开指针内容
Cout << DbgDumpDeep(node3) << Endl;
```

### 自定义类型支持

```cpp
// 方法1：特化 TDumper 模板
template <>
struct TDumper<MyStruct> {
    template <class S>
    static inline void Dump(S& s, const MyStruct& obj) {
        s << DumpRaw("MyStruct{")
          << obj.field1
          << DumpRaw(", ")
          << obj.field2
          << DumpRaw("}");
    }
};

// 方法2：使用 DEFINE_DUMPER 宏
DEFINE_DUMPER(MyNamespace::MyStruct, field1, field2, field3);
```

### 自定义颜色方案

```cpp
// 定义自定义颜色方案
struct MyColorScheme {
    DBG_OUTPUT_COLOR_HANDLER(Markup) {
        stream << DumpRaw("\033[36m"); // 青色
    }
    DBG_OUTPUT_COLOR_HANDLER(String) {
        stream << DumpRaw("\033[33m"); // 黄色
    }
    DBG_OUTPUT_COLOR_HANDLER(Literal) {
        stream << DumpRaw("\033[32m"); // 绿色
    }
    DBG_OUTPUT_COLOR_HANDLER(ResetType) {
        stream << DumpRaw("\033[0m");
    }
    // ... 其他颜色处理函数
};

// 使用自定义颜色方案
Cout << DbgDump<MyColorScheme>(myData) << Endl;
```

### 高级用法示例

```cpp
// 使用彩色输出
#include <library/cpp/dbg_output/colorscheme.h>

Cout << DbgDump<NDbgDump::NColorScheme::TEyebleed<>>(complexData) << Endl;

// 强制启用彩色（非TTY输出也显示颜色）
Cout << DbgDump<NDbgDump::NColorScheme::TEyebleed<true>>(complexData) << Endl;
```

## 🎯 应用场景

### 1. 开发阶段调试
- 快速查看复杂数据结构的内容
- 验证算法中间结果
- 调试容器操作和数据流

### 2. 错误诊断
- 输出异常发生时的程序状态
- 分析内存泄漏和指针错误
- 记录详细的错误上下文

### 3. 性能分析
- 监控数据结构和算法的行为
- 分析内存使用模式
- 验证优化效果

### 4. 测试辅助
- 单元测试中的数据验证
- 集成测试的状态检查
- 基准测试的结果展示

### 5. 日志记录
- 结构化日志输出
- 调试信息的格式化记录
- 运行时状态监控

## ⚡ 最佳实践

### 1. 性能优化
- **避免过度使用**：`dbg_output` 主要用于开发调试，生产环境应谨慎使用
- **选择合适模式**：对于大型数据结构，优先使用 `DbgDump` 而非 `DbgDumpDeep`
- **编译时优化**：在 Release 构建中考虑禁用或最小化调试输出

### 2. 可读性增强
- **使用缩进**：`.SetIndent(true)` 显著提高复杂数据结构的可读性
- **自定义类型**：为业务数据类型实现专门的转储器
- **合理使用颜色**：在终端环境中使用彩色输出提高区分度

### 3. 集成建议
```cpp
// 调试宏定义
#ifdef DEBUG
    #define DEBUG_PRINT(data) \
        Cout << "[DEBUG] " << __FILE__ << ":" << __LINE__ << " " << #data \
             << " = " << DbgDump(data).SetIndent(true) << Endl
#else
    #define DEBUG_PRINT(data) do {} while(0)
#endif
```

### 4. 类型安全
- **优先使用模板特化**：相比宏定义，模板特化提供更好的类型安全
- **避免递归循环**：`DbgDumpDeep` 会检测循环引用，但复杂结构仍需注意
- **字符串处理**：注意字符串和字符的区别，避免意外显示

### 5. 错误处理
```cpp
// 安全的调试输出
template <typename T>
void SafeDebugPrint(const T& data) {
    try {
        Cout << DbgDump(data) << Endl;
    } catch (const std::exception& e) {
        Cout << "Debug print failed: " << e.what() << Endl;
    }
}
```

## 🔗 相关模块

- **util/stream**：基础流操作和格式化
- **util/generic**：通用容器和数据结构
- **library/cpp/colorizer**：终端颜色输出支持
- **library/cpp/testing**：测试框架集成

## 📝 注意事项

1. **编译时依赖**：确保模板实例化所需的头文件都已包含
2. **运行时开销**：深度转储可能涉及大量内存分配和字符串操作
3. **线程安全**：输出操作本身不是线程安全的，多线程环境需要额外同步
4. **内存限制**：极大型数据结构的深度转储可能导致内存不足

`dbg_output` 模块为 YTsaurus 项目中的调试和开发工作提供了强大的工具支持，其灵活性和可扩展性使其能够适应各种复杂的数据展示需求。