# 约束容器库

## 概述

这个库提供了带有编译时和运行时约束的容器包装器。当前实现了 `TNonEmpty` 包装器，确保容器不为空，提供更强的类型安全和编程保证。

## 功能特性

### TNonEmpty 约束

- **编译时保证**：容器必须至少包含一个元素
- **运行时检查**：构造时验证非空约束
- **类型安全**：保持原始容器的所有操作
- **零开销**：编译器优化后无额外性能开销

## 文件说明

### 核心文件

- `nonempty.h` - TNonEmpty 包装器定义
- `nonempty-inl.h` - 内联实现

### 构建文件

- `CMakeLists.txt` - CMake 构建配置
- `CMakeLists.*.txt` - 针对不同平台的特定构建配置
- `ya.make` - YaMake 构建系统配置

## 核心接口

### TNonEmpty 类模板

```cpp
template <class TContainer>
class TNonEmpty {
public:
    using TUnderlying = TContainer;

    // 构造函数
    explicit TNonEmpty(TContainer underlying);

    // 迭代器构造
    template <class TIterator>
    TNonEmpty(TIterator first, TIterator last);

    // 初始化列表构造
    TNonEmpty(std::initializer_list<typename TContainer::value_type> values);

    // 容器操作
    typename TContainer::size_type size() const;
    typename TContainer::const_iterator begin() const;
    typename TContainer::const_iterator end() const;

    // 访问底层容器
    const TContainer& Get() const;
    operator const TContainer&() const;

private:
    TContainer Underlying_;
};
```

## 使用示例

### 基本使用

```cpp
#include <yt/yt/library/constrained/nonempty.h>

using namespace NYT;

// 从容器创建
std::vector<int> vec = {1, 2, 3};
TNonEmpty<std::vector<int>> nonEmptyVec(std::move(vec));

// 从迭代器创建
std::list<int> list = {1, 2, 3};
TNonEmpty<std::list<int>> nonEmptyList(list.begin(), list.end());

// 从初始化列表创建
TNonEmpty<std::vector<int>> nonEmptyVec2 = {1, 2, 3};

// 访问元素
for (const auto& item : nonEmptyVec) {
    std::cout << item << std::endl;
}

// 获取底层容器
const auto& underlying = nonEmptyVec.Get();
```

### 函数参数使用

```cpp
// 接受非空容器的函数
void ProcessItems(const TNonEmpty<std::vector<int>>& items) {
    // 不需要检查容器是否为空
    auto first = *items.begin();  // 安全访问第一个元素

    // 处理所有元素
    for (const auto& item : items) {
        // 处理逻辑
    }
}

// 调用函数
ProcessItems(TNonEmpty<std::vector<int>>{1, 2, 3, 4, 5});
```

### 类型推导

```cpp
// 自动类型推导
TNonEmpty vec = std::vector<int>{1, 2, 3};  // C++17

// 使用 make 辅助函数（如果提供）
auto nonEmpty = MakeNonEmpty({1, 2, 3});
```

## 实现原理

### 约束检查

构造时的验证机制：

```cpp
TNonEmpty(TContainer underlying)
    : Underlying_(std::move(underlying)) {
    YT_VERIFY(!Underlying_.empty());  // 运行时检查
}
```

### 操作转发

所有容器操作通过转发到底层容器实现：

```cpp
auto begin() const {
    return Underlying_.begin();
}

auto size() const {
    return Underlying_.size();
}
```

### 隐式转换

支持到底层容器的隐式转换：

```cpp
operator const TContainer&() const {
    return Underlying_;
}
```

## 支持的容器类型

### 标准容器

- `std::vector<T>`
- `std::list<T>`
- `std::deque<T>`
- `std::set<T>`
- `std::unordered_set<T>`
- `std::array<T, N>`（编译时检查）

### 自定义容器

任何满足以下条件的容器：
- 提供 `empty()` 方法
- 提供 `begin()` 和 `end()` 迭代器
- 支持 `size_type` 类型定义

## 性能特性

### 编译时优化

- **零开销抽象**：编译后与原始容器性能相同
- **内联优化**：所有操作内联展开
- **编译时检查**：部分约束可在编译时验证

### 运行时开销

- **构造时检查**：仅一次 `empty()` 调用
- **访问开销**：无额外开销
- **内存占用**：与原始容器相同

## 错误处理

### 运行时验证

当违反约束时的处理：

```cpp
YT_VERIFY(!Underlying_.empty());
```

- **Debug 模式**：详细错误信息
- **Release 模式**：最小检查开销
- **断言失败**：程序终止并显示错误

### 编译时检查

对于已知大小的容器：

```cpp
std::array<int, 0> emptyArray;  // 编译时检测
TNonEmpty<std::array<int, 0>> nonEmpty;  // 编译错误
```

## 使用场景

### API 设计

```cpp
// 函数参数：确保参数非空
void ProcessData(const TNonEmpty<std::vector<DataPoint>>& data);

// 返回值：确保返回非空
TNonEmpty<std::vector<Result>> ComputeResults();

// 类成员：确保状态有效
class Processor {
    TNonEmpty<std::vector<Rule>> rules_;
public:
    Processor(TNonEmpty<std::vector<Rule>> rules) : rules_(std::move(rules)) {}
};
```

### 数据验证

```cpp
// 验证输入数据
auto ValidateInput(const std::vector<int>& input) {
    if (input.empty()) {
        throw std::invalid_argument("Input cannot be empty");
    }
    return TNonEmpty<std::vector<int>>{input};
}

// 使用验证后的数据
auto validInput = ValidateInput(userInput);
// 后续代码无需再检查空值
```

## 最佳实践

1. **使用场景**
   - API 边界确保非空约束
   - 关键数据结构保证
   - 避免重复的空值检查

2. **性能考虑**
   - 在热路径中谨慎使用
   - 利用编译器优化
   - 避免不必要的包装

3. **错误处理**
   - 提供清晰的错误信息
   - 在适当时层使用异常
   - 考虑防御性编程

## 扩展可能性

### 其他约束类型

```cpp
// 可能的扩展
template <class TContainer>
class TSorted {
    // 确保容器已排序
};

template <class TContainer>
class TUnique {
    // 确保元素唯一
};

template <class TContainer, size_t N>
class TFixedSize {
    // 固定大小容器
};
```

### 组合约束

```cpp
// 组合多个约束
template <class TContainer>
using TNonEmptySorted = TSorted<TNonEmpty<TContainer>>;
```

## 依赖项

- YTsaurus 核心库
- 标准库组件
- 编译器支持（C++17 或更高）

## 平台支持

- Linux x86_64
- Linux aarch64
- macOS x86_64
- macOS arm64

## 测试

```bash
# 运行测试
ninja test_constrained
```

测试覆盖：
- 各种容器类型
- 边界条件
- 错误情况
- 性能基准

## 未来发展

1. **更多约束类型**
   - 大小范围约束
   - 值范围约束
   - 排序约束

2. **编译时优化**
   - 更多的编译时检查
   - 静态断言支持

3. **工具支持**
   - IDE 集成
   - 调试器支持