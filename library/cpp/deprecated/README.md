# deprecated 废弃功能模块

[deprecated](.) 目录包含 YTsaurus 项目中已被废弃但为向后兼容而保留的 C++ 库组件。这些模块已经被更现代、更高效的实现所替代，但仍然保留以确保现有代码的正常运行。

## ⚠️ 重要声明

**此目录中的所有组件都已被标记为废弃（deprecated）**，建议在新的开发项目中使用相应的现代替代方案。这些模块仅用于：

- 维护现有代码的向后兼容性
- 为从旧版本迁移提供过渡期
- 在特殊场景下的临时解决方案

## 📋 模块概览

### 1. atomic - 原子操作模块

**状态**：已废弃
**替代方案**：`util/system/atomic.h` 或 C++11 `std::atomic`

#### 功能描述
提供了跨平台的原子操作接口，支持 GCC 和 MSVC 编译器。

#### 核心组件
- **atomic.h**：主要接口定义
- **atomic_gcc.h**：GCC 平台特定实现
- **atomic_win.h**：Windows 平台特定实现
- **atomic_ops.h**：基本原子操作定义

#### 主要功能
```cpp
// 原子加法操作
TAtomicBase AtomicAdd(TAtomic& a, TAtomicBase v);

// 原子减法操作
TAtomicBase AtomicSub(TAtomic& a, TAtomicBase v);

// 原子比较交换
bool AtomicCas(TAtomic* a, TAtomicBase exchange, TAtomicBase compare);

// 原子获取和设置
TAtomicBase AtomicGet(const TAtomic& a);
void AtomicSet(TAtomic& a, TAtomicBase v);

// 简单自旋锁
bool AtomicTryLock(TAtomic* a);
void AtomicUnlock(TAtomic* a);
```

### 2. accessors - 内存访问统一接口

**状态**：已废弃
**替代方案**：标准容器接口 + 自定义类型特征

#### 功能描述
为不同类型的内存区域提供统一的访问接口，使不同数据类型可以使用相同的 API 进行操作。

#### 核心接口
```cpp
namespace NAccessors {
    // 获取内存区域的起始和结束指针
    template <typename T>
    const typename TMemoryTraits<T>::TElementType* Begin(const T& t);

    template <typename T>
    const typename TMemoryTraits<T>::TElementType* End(const T& t);

    // 获取内存区域大小
    template <typename T>
    size_t Size(const T& t);

    // 容器操作
    template <typename T>
    void Reserve(T& t, size_t sz);

    template <typename T>
    void Resize(T& t, size_t sz);

    template <typename T>
    void Clear(T& t);

    template <typename T>
    void Append(T& t, const typename TMemoryTraits<T>::TElementType& v);
}
```

#### 支持类型
- 标准容器（string, vector 等）
- 原始数据类型
- 自定义内存区域类型

### 3. enum_codegen - 枚举代码生成工具

**状态**：已废弃
**替代方案**：C++ 强类型枚举 + 现代反射机制

#### 功能描述
提供宏定义用于自动生成枚举类型的字符串转换和流输出功能。

#### 核心宏定义
```cpp
// 枚举值定义宏
#define ENUM_VALUE_GEN(name, value, ...) name = value,
#define ENUM_VALUE_GEN_NO_VALUE(name, ...) name,

// 枚举到字符串转换
#define ENUM_TO_STRING(type, MAP) \
    static inline const char* ToCString(type value); \
    static inline IOutputStream& operator<<(IOutputStream& os, type value);

// 辅助宏
#define ENUM_TO_STRING_IMPL_ITEM(name, ...) \
    case name: return #name;

#define ENUM_LTLT_IMPL_ITEM(name, ...) \
    case name: os << #name; break;
```

#### 使用示例
```cpp
// 定义枚举
#define MY_ENUM_MAP(XX) \
    XX(VALUE_A, 1) \
    XX(VALUE_B, 2) \
    XX(VALUE_C, 3)

enum MyEnum {
    MY_ENUM_MAP(ENUM_VALUE_GEN)
};

// 生成字符串转换函数
ENUM_TO_STRING(MyEnum, MY_ENUM_MAP)

// 使用
MyEnum value = VALUE_A;
std::cout << ToCString(value) << std::endl; // "VALUE_A"
std::cout << value << std::endl; // "VALUE_A"
```

### 4. kmp - Knuth-Morris-Pratt 字符串搜索

**状态**：已废弃
**替代方案**：标准库字符串搜索算法或优化的第三方实现

#### 功能描述
实现了 KMP 算法进行高效的字符串模式匹配搜索。

### 5. split - 字符串分割工具

**状态**：已废弃
**替代方案**：`util/string/split.h` 或 C++17 `std::string_view`

#### 功能描述
提供了多种字符串分割迭代器和工具函数。

#### 核心组件
- **split_iterator.h/cpp**：主要分割迭代器实现
- **delim_string_iter.h/cpp**：分隔符字符串迭代器

#### 主要功能
```cpp
// 数字区间表示
template <typename T>
struct TNumPair {
    T Begin;
    T End;

    T Length() const;
    bool operator==(const TNumPair& r) const;
    bool operator!=(const TNumPair& r) const;
};

using TSizeTRegion = TNumPair<size_t>;
using TUi32Region = TNumPair<ui32>;

// 字符串分割迭代器
template <typename DelimType>
class TSplitIterator {
    // 提供高效的字符串分割功能
};
```

### 6. mapped_file - 内存映射文件

**状态**：已废弃
**替代方案**：`util/system/filemap.h` 或平台特定的 mmap API

#### 功能描述
提供跨平台的内存映射文件操作接口。

### 7. threadable - 可线程化工具

**状态**：已废弃
**替代方案**：现代 C++ 线程库和并发工具

#### 功能描述
提供多线程编程中的基础工具和抽象。

## 🔄 迁移指南

### 1. atomic 模块迁移

**从废弃版本**：
```cpp
#include <library/cpp/deprecated/atomic/atomic.h>

TAtomic counter;
AtomicAdd(counter, 1);
bool locked = AtomicTryLock(&counter);
```

**迁移到现代版本**：
```cpp
#include <util/system/atomic.h>
// 或者使用 C++11
#include <atomic>

TAtomic counter;
AtomicAdd(counter, 1);
// 或者
std::atomic<int> counter;
counter.fetch_add(1);

bool locked = AtomicTryLock(&counter);
// 或者使用 std::atomic_flag
std::atomic_flag lockFlag = ATOMIC_FLAG_INIT;
bool locked = !lockFlag.test_and_set(std::memory_order_acquire);
```

### 2. accessors 模块迁移

**从废弃版本**：
```cpp
#include <library/cpp/deprecated/accessors/accessors.h>

TString data;
auto begin = NAccessors::Begin(data);
auto end = NAccessors::End(data);
size_t size = NAccessors::Size(data);
```

**迁移到现代版本**：
```cpp
// 对于标准容器，直接使用容器接口
TString data;
auto begin = data.begin();
auto end = data.end();
size_t size = data.size();

// 或者使用 std::span (C++20)
std::span<const char> span(data);
```

### 3. enum_codegen 模块迁移

**从废弃版本**：
```cpp
#define MY_ENUM_MAP(XX) \
    XX(VALUE_A, 1) \
    XX(VALUE_B, 2)

enum MyEnum {
    MY_ENUM_MAP(ENUM_VALUE_GEN)
};

ENUM_TO_STRING(MyEnum, MY_ENUM_MAP)
```

**迁移到现代版本**：
```cpp
// 使用 C++11 强类型枚举
enum class MyEnum {
    VALUE_A = 1,
    VALUE_B = 2
};

// 使用 switch 语句或映射表
std::string ToString(MyEnum value) {
    switch (value) {
        case MyEnum::VALUE_A: return "VALUE_A";
        case MyEnum::VALUE_B: return "VALUE_B";
        default: return "UNKNOWN";
    }
}

// 或者使用 magic_enum 库（如果可用）
#include <magic_enum.hpp>
auto enumName = magic_enum::enum_name(value);
```

### 4. split 模块迁移

**从废弃版本**：
```cpp
#include <library/cpp/deprecated/split/split_iterator.h>

TSplitIterator<' '> splitter(text);
for (auto it = splitter.begin(); it != splitter.end(); ++it) {
    // 处理分割结果
}
```

**迁移到现代版本**：
```cpp
#include <util/string/split.h>

// 使用 YTsaurus 的现代分割工具
for (const auto& part : StringSplitter(text).Split(' ')) {
    // 处理分割结果
}

// 或者使用 C++17 std::string_view
std::vector<std::string_view> parts;
size_t start = 0, end = 0;
while ((end = text.find(' ', start)) != std::string::npos) {
    parts.emplace_back(text.data() + start, end - start);
    start = end + 1}
```

## ⚠️ 使用注意事项

### 1. 性能考虑
- 废弃模块可能没有使用最新的优化技术
- 某些实现可能存在已知的性能问题
- 在新项目中优先考虑现代替代方案

### 2. 维护状态
- 废弃模块不再积极维护
- 可能包含已知但未修复的 bug
- 不保证与最新编译器版本的兼容性

### 3. 安全性
- 某些实现可能存在安全隐患
- 没有经过最新的安全审计
- 在安全敏感的应用中应避免使用

### 4. 兼容性
- 主要为向后兼容而保留
- 可能在未来的版本中被完全移除
- 不建议在新的开发中使用

## 🎯 迁移策略

### 阶段 1：识别和评估
1. 使用代码搜索工具识别使用废弃模块的代码
2. 评估每个使用场景的复杂性和风险
3. 制定迁移优先级和时间表

### 阶段 2：渐进式替换
1. 从最简单的替换开始
2. 确保替换后的功能测试通过
3. 逐步处理更复杂的场景

### 阶段 3：清理和验证
1. 移除废弃模块的依赖
2. 运行完整的测试套件
3. 进行性能回归测试

### 阶段 4：文档更新
1. 更新相关文档和注释
2. 通知团队成员关于 API 变更
3. 更新构建脚本和配置

## 🔗 相关资源

- **现代替代模块**：查看 YTsaurus 核心库中的相应现代实现
- **迁移指南**：参考项目中的代码示例和最佳实践
- **测试工具**：使用现有的单元测试验证迁移的正确性
- **性能基准**：比较新旧实现的性能差异

## 📝 总结

`deprecated` 目录中的模块代表了 YTsaurus 项目演进过程中的历史实现。虽然这些模块在过去的开发中发挥了重要作用，但现代的替代方案提供了更好的性能、安全性和可维护性。

建议开发团队：
- **避免在新项目中使用这些废弃模块**
- **制定系统性的迁移计划**
- **利用这个机会进行代码现代化和技术债务清理**
- **在迁移过程中保持充分的测试覆盖**

通过系统性地迁移到现代实现，可以显著提升代码质量、性能和可维护性。