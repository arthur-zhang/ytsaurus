# Numeric (数值算法库)

## 项目概述

Numeric 模块提供了一套高性能的数值计算算法和数据结构，专门为 YTsaurus 的大数据处理场景优化。该模块包含了二分搜索、分段线性函数、定点数运算等核心数值计算功能。

## 核心功能

### 算法工具集
- **二分搜索**: 高效的二分搜索算法实现
- **中点计算**: 避免溢出的中点计算算法
- **类型转换**: 安全的数值类型转换
- **饱和算术**: 防止溢出的饱和算术运算

### 特殊数据结构
- **分段线性函数**: 高效的分段线性函数表示和计算
- **定点数**: 高精度定点数运算支持
- **双精度数组格式**: 优化的双精度数组存储格式

### 数值工具
- **位转换**: 安全的类型位转换
- **数值范围检查**: 边界检查和范围验证
- **精度控制**: 数值精度和舍入控制

## 主要接口

### 基础算法函数

```cpp
// 位转换（C++20 std::bit_cast 的替代实现）
template <class TTo, class TFrom>
TTo BitCast(const TFrom &src) noexcept;

// 中点计算（C++20 std::midpoint 的替代实现）
template <class TInt>
TInt Midpoint(TInt a, TInt b) noexcept;

// 饱和算术乘法
i64 SignedSaturationArithmeticMultiply(i64 lhs, i64 rhs) noexcept;
i64 UnsignedSaturationArithmeticMultiply(i64 lhs, i64 rhs, i64 max) noexcept;

// 饱和算术加法
i64 SignedSaturationArithmeticAdd(i64 lhs, i64 rhs) noexcept;
i64 UnsignedSaturationArithmeticAdd(i64 lhs, i64 rhs, i64 max) noexcept;

// 有符号饱和转换
i64 SignedSaturationConversion(double value) noexcept;
```

### 二分搜索

```cpp
// 高效二分搜索算法
template <typename T, typename TComparer>
size_t BinarySearch(const std::vector<T>& data, const T& target, TComparer comparer);

// 自定义二分搜索
template <typename T>
size_t LowerBound(const std::vector<T>& data, const T& value);

template <typename T>
size_t UpperBound(const std::vector<T>& data, const T& value);
```

### 分段线性函数

```cpp
class TPiecewiseLinearFunction
{
public:
    // 构造函数
    TPiecewiseLinearFunction() = default;

    // 添加点
    void AddPoint(double x, double y);

    // 计算函数值
    double Evaluate(double x) const;

    // 获取函数定义域
    std::pair<double, double> GetDomain() const;

    // 获取函数值域
    std::pair<double, double> GetRange() const;

    // 合并两个函数
    static TPiecewiseLinearFunction Merge(
        const TPiecewiseLinearFunction& f1,
        const TPiecewiseLinearFunction& f2);
};
```

### 定点数运算

```cpp
template <int IntegerBits, int FractionalBits>
class TFixedPointNumber
{
public:
    // 构造函数
    TFixedPointNumber() = default;
    explicit TFixedPointNumber(double value);
    explicit TFixedPointNumber(i64 rawValue);

    // 基本运算
    TFixedPointNumber operator+(const TFixedPointNumber& other) const;
    TFixedPointNumber operator-(const TFixedPointNumber& other) const;
    TFixedPointNumber operator*(const TFixedPointNumber& other) const;
    TFixedPointNumber operator/(const TFixedPointNumber& other) const;

    // 转换为浮点数
    double ToDouble() const;

    // 获取原始值
    i64 GetRawValue() const;
};
```

## 使用方法

### 饱和算术运算示例

```cpp
#include <yt/yt/library/numeric/util.h>

using namespace NYT;

void SafeArithmeticExample() {
    // 饱和乘法 - 防止溢出
    i64 a = 1000000;
    i64 b = 1000000;

    // 普通乘法会溢出
    i64 normalResult = a * b;  // 溢出！

    // 饱和乘法不会溢出
    i64 saturatedResult = SignedSaturationArithmeticMultiply(a, b);
    Cout << "Saturated result: " << saturatedResult << Endl;

    // 饱和加法
    i64 maxResult = SignedSaturationArithmeticAdd(
        std::numeric_limits<i64>::max() - 100,
        200);  // 结果将是 max_i64

    // 安全的中点计算
    i64 midpoint = Midpoint(std::numeric_limits<i64>::max(), 0);
    Cout << "Safe midpoint: " << midpoint << Endl;

    // 安全的类型转换
    double largeValue = 1e20;
    i64 converted = SignedSaturationConversion(largeValue);
    Cout << "Converted value: " << converted << Endl;
}
```

### 二分搜索应用示例

```cpp
#include <yt/yt/library/numeric/binary_search.h>

class DataSearcher {
public:
    // 查找第一个大于等于目标值的索引
    size_t FindFirstGreaterOrEqual(const std::vector<int>& data, int target) {
        return LowerBound(data, target);
    }

    // 查找第一个大于目标值的索引
    size_t FindFirstGreater(const std::vector<int>& data, int target) {
        return UpperBound(data, target);
    }

    // 自定义条件搜索
    size_t FindFirstSatisfying(
        const std::vector<double>& data,
        std::function<bool(double)> condition) {

        size_t left = 0;
        size_t right = data.size();

        while (left < right) {
            size_t mid = Midpoint(left, right);
            if (condition(data[mid])) {
                right = mid;
            } else {
                left = mid + 1;
            }
        }

        return left;
    }
};
```

### 分段线性函数示例

```cpp
#include <yt/yt/library/numeric/piecewise_linear_function.h>

class ApproximationCalculator {
public:
    // 创建近似函数
    static TPiecewiseLinearFunction CreateSineApproximation() {
        TPiecewiseLinearFunction func;

        // 添加关键点来近似 sin(x) 在 [0, 2π] 区间
        for (double x = 0; x <= 2 * M_PI; x += M_PI / 4) {
            func.AddPoint(x, sin(x));
        }

        return func;
    }

    // 创建自定义分段函数
    static TPiecewiseLinearFunction CreateCustomFunction() {
        TPiecewiseLinearFunction func;

        // 定义一个分段函数：在不同区间有不同的线性关系
        func.AddPoint(0.0, 0.0);    // 起点
        func.AddPoint(1.0, 2.0);    // 第一个线性段
        func.AddPoint(3.0, 1.0);    // 第二个线性段
        func.AddPoint(5.0, 4.0);    // 第三个线性段

        return func;
    }

    // 函数合并示例
    static TPiecewiseLinearFunction CombineFunctions() {
        auto f1 = CreateCustomFunction();
        auto f2 = CreateSineApproximation();

        // 合并两个函数
        return TPiecewiseLinearFunction::Merge(f1, f2);
    }
};

// 使用分段线性函数
void UsePiecewiseFunction() {
    auto func = ApproximationCalculator::CreateCustomFunction();

    // 计算函数值
    std::vector<double> testPoints = {0.5, 1.5, 2.5, 3.5, 4.5};
    for (double x : testPoints) {
        double y = func.Evaluate(x);
        Cout << "f(" << x << ") = " << y << Endl;
    }

    // 获取函数定义域和值域
    auto domain = func.GetDomain();
    auto range = func.GetRange();

    Cout << "Domain: [" << domain.first << ", " << domain.second << "]" << Endl;
    Cout << "Range: [" << range.first << ", " << range.second << "]" << Endl;
}
```

### 定点数运算示例

```cpp
#include <yt/yt/library/numeric/fixed_point_number.h>

// 定义 16.16 格式的定点数（16位整数，16位小数）
using Fixed1616 = TFixedPointNumber<16, 16>;

// 定义 8.8 格式的定点数
using Fixed88 = TFixedPointNumber<8, 8>;

class FinancialCalculator {
public:
    // 使用定点数进行精确的财务计算
    static Fixed1616 CalculateInterest(
        Fixed1616 principal,
        Fixed1616 rate,
        int periods) {

        Fixed1616 amount = principal;
        Fixed1616 onePlusRate = Fixed1616(1.0) + rate;

        for (int i = 0; i < periods; ++i) {
            amount = amount * onePlusRate;
        }

        return amount;
    }

    // 货币计算
    static double CalculateTotal(
        double price,
        double taxRate,
        int quantity) {

        Fixed1616 fixedPrice(price);
        Fixed1616 fixedTaxRate(taxRate);
        Fixed1616 fixedQuantity(quantity);

        Fixed1616 subtotal = fixedPrice * fixedQuantity;
        Fixed1616 tax = subtotal * fixedTaxRate;
        Fixed1616 total = subtotal + tax;

        return total.ToDouble();
    }
};
```

### 双精度数组处理示例

```cpp
#include <yt/yt/library/numeric/double_array.h>

class DataProcessor {
public:
    // 高效的双精度数组处理
    static void ProcessLargeDataset(const std::vector<double>& data) {
        // 使用优化的数组格式
        TDoubleArray array(data.begin(), data.end());

        // 统计计算
        double sum = 0.0;
        double minVal = std::numeric_limits<double>::max();
        double maxVal = std::numeric_limits<double>::min();

        for (size_t i = 0; i < array.Size(); ++i) {
            double value = array[i];
            sum += value;
            minVal = std::min(minVal, value);
            maxVal = std::max(maxVal, value);
        }

        double mean = sum / array.Size();

        Cout << "Statistics:" << Endl;
        Cout << "  Count: " << array.Size() << Endl;
        Cout << "  Sum: " << sum << Endl;
        Cout << "  Mean: " << mean << Endl;
        Cout << "  Min: " << minVal << Endl;
        Cout << "  Max: " << maxVal << Endl;
    }
};
```

## 配置说明

### 定点数配置

```cpp
// 常用的定点数格式
using Fixed3232 = TFixedPointNumber<32, 32>;  // 32位整数，32位小数
using Fixed248 = TFixedPointNumber<24, 8>;    // 24位整数，8位小数
using Fixed1616 = TFixedPointNumber<16, 16>;  // 16位整数，16位小数
using Fixed88 = TFixedPointNumber<8, 8>;      // 8位整数，8位小数
```

### 数值精度控制

```cpp
// 默认数值精度设置
constexpr double DEFAULT_EPSILON = 1e-12;
constexpr int DEFAULT_PRECISION = 15;

// 数值比较容差
bool AreAlmostEqual(double a, double b, double epsilon = DEFAULT_EPSILON);
```

## 性能考虑

### 算法复杂度
- **二分搜索**: O(log n) 时间复杂度
- **分段线性函数**: O(log m) 查找复杂度，其中 m 为段数
- **定点数运算**: O(1) 基本运算复杂度

### 内存使用
- **分段线性函数**: O(m) 内存使用，其中 m 为控制点数量
- **双精度数组**: 紧凑的内存布局，减少缓存未命中
- **定点数**: 固定大小内存使用

### 编译优化
- **模板特化**: 针对常用数值类型的模板特化
- **内联优化**: 关键路径函数内联
- **向量化**: 支持 SIMD 指令优化

## 最佳实践

### 1. 数值安全性

```cpp
class SafeNumericOperations {
public:
    // 安全的数组访问
    static double SafeArrayAccess(
        const std::vector<double>& array,
        size_t index) {
        if (index >= array.size()) {
            return std::numeric_limits<double>::quiet_NaN();
        }
        return array[index];
    }

    // 安全的除法运算
    static std::optional<double> SafeDivision(double numerator, double denominator) {
        constexpr double EPSILON = 1e-12;
        if (std::abs(denominator) < EPSILON) {
            return std::nullopt;
        }
        return numerator / denominator;
    }

    // 边界检查
    static bool IsInValidRange(double value, double min, double max) {
        return value >= min && value <= max;
    }
};
```

### 2. 性能优化技巧

```cpp
class OptimizedCalculations {
public:
    // 批量操作优化
    static void BatchProcess(
        const std::vector<double>& input,
        std::vector<double>& output,
        std::function<double(double)> processor) {

        output.resize(input.size());

        // 使用并行处理（如果支持）
        #pragma omp parallel for
        for (size_t i = 0; i < input.size(); ++i) {
            output[i] = processor(input[i]);
        }
    }

    // 内存预分配
    static std::vector<double> PreallocatedCalculation(size_t size) {
        std::vector<double> result;
        result.reserve(size);  // 预分配内存

        for (size_t i = 0; i < size; ++i) {
            result.push_back(CalculateValue(i));
        }

        return result;
    }

private:
    static double CalculateValue(size_t index) {
        // 示例计算函数
        return std::sin(index * 0.01) * std::cos(index * 0.02);
    }
};
```

## 依赖项

- **Standard Library**: STL 容器和算法
- **System Headers**: 编译器和系统相关头文件

## 注意事项

### 1. 数值精度
- 浮点数运算可能存在精度误差
- 定点数可以提供更精确的计算结果
- 选择合适的数据类型平衡精度和性能

### 2. 溢出处理
- 使用饱和算术避免溢出
- 检查数值边界条件
- 合理使用数值范围检查

### 3. 性能考虑
- 不同的数值类型有不同的性能特征
- 批量操作通常比单个操作更高效
- 考虑缓存友好的数据访问模式

### 4. 兼容性
- 某些函数是 C++20 标准的替代实现
- 在编译器支持时可以迁移到标准实现
- 注意不同平台的数值行为差异