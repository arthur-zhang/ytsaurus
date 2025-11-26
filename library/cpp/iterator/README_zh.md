# 迭代器工具库

## 项目概述

迭代器工具库提供了类似 Python 的函数式编程工具，包括 `Enumerate`、`Zip`、`Map`、`Filter`、`Concatenate` 和 `CartesianProduct` 等函数。这些工具为 C++ 容器操作提供了强大且直观的接口，让代码更加简洁和富有表现力。

## 核心功能

### 函数式迭代器
- **Enumerate**：为容器元素添加索引
- **Zip**：并行迭代多个容器
- **Map**：对容器元素应用映射函数
- **Filter**：过滤容器元素
- **Concatenate**：连接多个容器
- **CartesianProduct**：计算容器的笛卡尔积

### 设计特点
- **零开销抽象**：编译时优化，运行时开销极小
- **范围兼容**：支持所有支持范围 for 循环的容器
- **引用传递**：支持非 const 引用传递
- **现代 C++**：完美转发和移动语义

## 主要函数

### Enumerate
为容器元素添加索引，类似 Python 的 enumerate()。

```cpp
#include <library/cpp/iterator/enumerate.h>

TVector<int> data = {10, 20, 30, 40};

// 基本用法
for (auto [index, value] : Enumerate(data)) {
    Cout << "Index: " << index << ", Value: " << value << Endl;
}
// 输出：
// Index: 0, Value: 10
// Index: 1, Value: 20
// Index: 2, Value: 30
// Index: 3, Value: 40

// 修改元素（非 const 容器）
for (auto [index, value] : Enumerate(data)) {
    value *= 2;  // 修改原容器中的值
}
```

### Map
对容器元素应用映射函数，类似 Python 的 map()。

```cpp
#include <library/cpp/iterator/mapped.h>

TVector<int> numbers = {1, 2, 3, 4, 5};

// 转换为平方
for (auto square : Map([](int x) { return x * x; }, numbers)) {
    Cout << square << " ";  // 1 4 9 16 25
}

// 转换为字符串
for (auto str : Map([](int x) { return ToString(x); }, numbers)) {
    Cout << str << " ";  // 1 2 3 4 5
}
```

### Filter
过滤容器元素，类似 Python 的 filter()。

```cpp
#include <library/cpp/iterator/filtering.h>

TVector<int> numbers = {1, 2, 3, 4, 5, 6, 7, 8, 9, 10};

// 过滤偶数
for (auto even : Filter([](int x) { return x % 2 == 0; }, numbers)) {
    Cout << even << " ";  // 2 4 6 8 10
}

// 过滤大于 5 的数
for (auto num : Filter([](int x) { return x > 5; }, numbers)) {
    Cout << num << " ";  // 6 7 8 9 10
}
```

### Zip
并行迭代多个容器，类似 Python 的 zip()。

```cpp
#include <library/cpp/iterator/zip.h>

TVector<int> a = {1, 2, 3};
TVector<char> b = {'a', 'b', 'c'};
TVector<double> c = {1.1, 2.2, 3.3};

// 两个容器的 Zip
for (auto [x, y] : Zip(a, b)) {
    Cout << x << y << " ";  // 1a 2b 3c
}

// 三个容器的 Zip
for (auto [x, y, z] : Zip(a, b, c)) {
    Cout << x << ":" << y << ":" << z << " ";
    // 1:a:1.1 2:b:2.2 3:c:3.3
}
```

### Concatenate
连接多个容器，创建一个统一视图。

```cpp
#include <library/cpp/iterator/concatenate.h>

TVector<int> a = {1, 2, 3};
TVector<int> b = {4, 5, 6};
TVector<int> c = {7, 8, 9};

// 连接三个容器
for (auto x : Concatenate(a, b, c)) {
    Cout << x << " ";  // 1 2 3 4 5 6 7 8 9
}

// 也可以连接不同类型的容器
int arr[] = {10, 11, 12};
for (auto x : Concatenate(a, arr)) {
    Cout << x << " ";  // 1 2 3 10 11 12
}
```

### CartesianProduct
计算容器的笛卡尔积。

```cpp
#include <library/cpp/iterator/cartesian_product.h>

TVector<int> a = {1, 2};
TVector<char> b = {'a', 'b', 'c'};

// 计算笛卡尔积
for (auto [x, y] : CartesianProduct(a, b)) {
    Cout << "(" << x << "," << y << ") ";
    // (1,a) (1,b) (1,c) (2,a) (2,b) (2,c)
}

// 三个容器的笛卡尔积
TVector<bool> c = {true, false};
for (auto [x, y, z] : CartesianProduct(a, b, c)) {
    Cout << "(" << x << "," << y << "," << z << ") ";
}
```

## 高级用法

### 链式操作
```cpp
// 组合多个操作
TVector<int> numbers = {1, 2, 3, 4, 5, 6, 7, 8, 9, 10};

// 筛选偶数，计算平方，然后枚举
for (auto [index, square] : Enumerate(Map([](int x) { return x * x; },
                                         Filter([](int x) { return x % 2 == 0; }, numbers)))) {
    Cout << "Even #" << index << ": " << square << Endl;
}
// 输出：
// Even #0: 4
// Even #1: 16
// Even #2: 36
// Even #3: 64
// Even #4: 100
```

### 容器转换
```cpp
// 将结果存储到新容器
TVector<int> original = {1, 2, 3, 4, 5};

// 使用 Map 创建新容器
TVector<int> squares;
for (auto x : Map([](int v) { return v * v; }, original)) {
    squares.push_back(x);
}

// 使用 Filter 创建新容器
TVector<int> evens;
for (auto x : Filter([](int v) { return v % 2 == 0; }, original)) {
    evens.push_back(x);
}
```

### 复杂数据处理
```cpp
struct TPerson {
    TString Name;
    int Age;
    TString City;
};

TVector<TPerson> people = {
    {"Alice", 25, "New York"},
    {"Bob", 30, "San Francisco"},
    {"Charlie", 35, "New York"},
    {"Diana", 28, "Chicago"}
};

// 筛选特定城市的人并枚举
for (auto [index, person] : Enumerate(Filter([](const TPerson& p) {
        return p.City == "New York";
    }, people))) {
    Cout << "Person #" << index << ": " << person.Name
         << " (" << person.Age << " years old)" << Endl;
}

// 提取姓名和年龄
for (auto [name, age] : Map([](const TPerson& p) {
        return std::make_pair(p.Name, p.Age);
    }, people)) {
    Cout << name << " is " << age << " years old" << Endl;
}
```

## 性能特征

### 运行时开销
- **Enumerate, Zip, Map**：零开销，与手动循环相同
- **Filter**：约 1.5 倍开销（函数调用开销）
- **Concatenate, CartesianProduct**：约 3 倍开销（复杂迭代逻辑）

### 编译时开销
- 每个循环增加约 1.5 倍编译时间
- 模板实例化可能增加编译时间
- 优化：适度使用，避免过度嵌套

### 内存效率
- **零拷贝设计**：所有操作都是视图，不复制数据
- **引用传递**：支持对原容器元素的修改
- **移动语义**：完美支持右值引用

## 设计保证

### 容器兼容性
- 支持所有支持范围 for 循环的容器
- 包括原始数组：`int arr[] = {1, 2, 3};`
- 支持右值容器：`Filter([](auto x){...}, TVector{1, 2, 3})`

### 类型安全
- 自动推导正确的引用和 const 修饰符
- 支持模板参数的完美转发
- 保持原容器的 const 正确性

### 迭代器兼容性
- 提供标准迭代器类型 `TView::iterator`
- 支持迭代器特征：`iterator_category`、`value_type` 等
- 兼容标准库算法

## 使用限制

### 不支持的用例
- **初始化列表**：`Enumerate({1, 2, 3})`（类型不明确）
- **容器修改**：改变容器大小或使迭代器失效的操作
- **嵌套修改**：在迭代期间修改底层容器

### 注意事项
- **值传递**：大多数情况下返回 `std::tuple` 按值传递
- **引用处理**：避免使用 `const auto& [i, x]`，应使用 `auto [i, x]`
- **类型推导**：避免直接使用 `value_type` 等嵌套类型

## 最佳实践

### 正确的语法
```cpp
// 推荐：使用 auto，让库处理引用
for (auto [index, value] : Enumerate(container)) {
    value *= 2;  // value 是引用，可以修改原容器
}

// 推荐：const 自动变量
for (const auto [index, value] : Enumerate(container)) {
    Cout << value << " ";  // 只读访问
}

// 避免：不要使用 const auto&（除非确定需要）
// for (const auto& [index, value] : Enumerate(container)) {
//     // 这样写可能不会得到预期的引用语义
// }
```

### 性能优化
```cpp
// 避免过深的嵌套
// 不推荐：
for (auto x : Map(f1, Filter(p1, Map(f2, Filter(p2, container))))) {
    // 处理 x
}

// 推荐：使用临时变量或分离步骤
auto filtered = Filter(p1, container);
auto mapped = Map(f1, filtered);
for (auto x : mapped) {
    // 处理 x
}
```

### 与标准库结合
```cpp
// 与标准算法结合使用
TVector<int> data = {1, 2, 3, 4, 5};

// 使用标准算法处理 Map 结果
TVector<int> squares;
std::copy(Map([](int x){ return x * x; }, data).begin(),
          Map([](int x){ return x * x; }, data).end(),
          std::back_inserter(squares));

// 使用标准算法处理 Filter 结果
auto evenCount = std::count_if(
    Filter([](int x){ return x % 2 == 0; }, data).begin(),
    Filter([](int x){ return x % 2 == 0; }, data).end(),
    [](int) { return true; }
);
```

## 实际应用场景

### 数据处理管道
```cpp
// 处理日志数据
struct TLogEntry {
    TInstant Timestamp;
    TString Level;
    TString Message;
};

TVector<TLogEntry> logs = /* ... */;

// 筛选错误日志并带索引输出
for (auto [index, entry] : Enumerate(Filter([](const TLogEntry& e) {
        return e.Level == "ERROR";
    }, logs))) {
    Cout << "Error #" << index << " at " << entry.Timestamp
         << ": " << entry.Message << Endl;
}
```

### 算法实现
```cpp
// 实现矩阵操作
TVector<TVector<int>> matrix = {
    {1, 2, 3},
    {4, 5, 6},
    {7, 8, 9}
};

// 转置矩阵（简化版）
for (auto [i, j] : CartesianProduct(Enumerate(matrix[0]), Enumerate(matrix))) {
    Cout << "Matrix[" << i << "][" << j << "] = "
         << matrix[j][i] << Endl;
}
```

### 测试和调试
```cpp
// 调试时打印容器内容
TVector<TString> items = {"apple", "banana", "cherry"};

for (auto [index, item] : Enumerate(items)) {
    Cout << "Item #" << index << ": '" << item << "'" << Endl;
}

// 比较两个容器
TVector<int> expected = {1, 2, 3, 4, 5};
TVector<int> actual = {1, 2, 3, 5, 5};

for (auto [i, exp, act] : Zip(Enumerate(expected), actual)) {
    if (exp != act) {
        Cerr << "Mismatch at index " << i << ": expected "
             << exp << ", got " << act << Endl;
    }
}
```