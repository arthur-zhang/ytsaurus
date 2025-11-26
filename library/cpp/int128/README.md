# 128位整数（Int128）库

高性能的128位整数实现，支持有符号和无符号运算。

## 概述

该库提供了完整的128位整数实现，包括有符号（i128）和无符号（ui128）版本。在原生不支持128位整数的平台上通过软件实现，在有硬件支持的平台上利用编译器扩展进行优化。

## 核心特性

### 完整的整数类型
- **i128**: 128位有符号整数
- **ui128**: 128位无符号整数
- **自动类型转换**: 与标准整数类型的无缝转换
- **编译器优化**: 利用平台的128位支持（如GCC的`__int128`）

### 丰富的运算支持
- **算术运算**: 加、减、乘、除、取模
- **位运算**: 与、或、异或、取反、位移
- **比较运算**: 所有的比较操作符
- **数学函数**: 绝对值、幂运算等

### 平台兼容性
- **跨平台**: 支持多种CPU架构和操作系统
- **字节序**: 自动处理大小端序
- **编译器支持**: 兼容GCC、Clang、MSVC等主流编译器

## 设计原则

该库的设计目标是让 ui128/i128 类型的使用体验尽可能接近原生整数类型。因此：
- **不提供** GetHigh()、GetLow() 等底层访问函数
- **不支持** 多参数构造函数
- **强调** 运算符重载和隐式类型转换
- **保持** 与标准整数类型一致的接口

## 基本使用

### 类型定义
```cpp
#include <int128.h>

// 类型别名
using i128 = TInteger128<true>;   // 128位有符号整数
using ui128 = TInteger128<false>; // 128位无符号整数
```

### 构造和赋值
```cpp
// 从基本类型构造
i128 a = 123;                    // 从int构造
i128 b = 1234567890LL;           // 从long long构造
ui128 c = 9876543210ULL;         // 从unsigned long long构造

// 隐式类型转换
i128 d = c;                      // 从ui128转换到i128
ui128 e = -123;                  // 从负数转换到ui128（注意符号扩展）

// 从字符串构造
i128 f = i128::FromString("123456789012345678901234567890");
ui128 g = ui128::FromString("0x123456789abcdef0123456789abcdef0", 16);
```

### 基本运算
```cpp
i128 a = 10000000000000000000LL;
i128 b = 20000000000000000000LL;

// 算术运算
i128 sum = a + b;                 // 加法
i128 diff = b - a;               // 减法
i128 product = a * b;            // 乘法
i128 quotient = b / a;           // 除法
i128 remainder = b % a;          // 取模

// 位运算
i128 bitwise_and = a & b;        // 按位与
i128 bitwise_or = a | b;         // 按位或
i128 bitwise_xor = a ^ b;        // 按位异或
i128 bitwise_not = ~a;           // 按位取反

// 位移运算
i128 shifted_left = a << 10;     // 左移
i128 shifted_right = a >> 10;    // 右移

// 比较运算
bool greater = a > b;            // 大于
bool equal = a == b;             // 等于
bool less_or_equal = a <= b;     // 小于等于
```

## 实际应用

### 大数计算
```cpp
// 计算大数的阶乘
ui128 Factorial(int n) {
    ui128 result = 1;
    for (int i = 2; i <= n; ++i) {
        result *= i;
    }
    return result;
}

// 计算组合数
ui128 BinomialCoefficient(int n, int k) {
    if (k > n || k < 0) return 0;
    if (k > n - k) k = n - k;

    ui128 result = 1;
    for (int i = 1; i <= k; ++i) {
        result = result * (n - k + i) / i;
    }
    return result;
}
```

### 金融计算
```cpp
// 高精度货币计算（以分为单位）
class TMoney {
private:
    i128 cents_;  // 金额（分）

public:
    TMoney(i64 dollars, i64 cents)
        : cents_(dollars * 100 + cents)
    {}

    TMoney operator+(const TMoney& other) const {
        return TMoney(cents_ + other.cents_);
    }

    TMoney operator*(const i128& multiplier) const {
        return TMoney(cents_ * multiplier);
    }

    TString ToString() const {
        i64 dollars = static_cast<i64>(cents_ / 100);
        i64 cents = static_cast<i64>(cents_ % 100);
        return Sprintf("%lld.%02lld", dollars, std::abs(cents));
    }

private:
    TMoney(i128 cents) : cents_(cents) {}
};
```

### 密码学基础
```cpp
// 大素数测试（简化版）
bool IsProbablyPrime(ui128 n) {
    if (n < 2) return false;
    if (n == 2 || n == 3) return true;
    if (n % 2 == 0) return false;

    // Miller-Rabin 测试的简化版本
    for (ui128 a = 2; a < 10 && a < n - 2; ++a) {
        ui128 result = Power(a, n - 1, n);
        if (result != 1) return false;
    }
    return true;
}

// 模幂运算
ui128 Power(ui128 base, ui128 exponent, ui128 modulus) {
    ui128 result = 1;
    base = base % modulus;

    while (exponent > 0) {
        if (exponent % 2 == 1) {
            result = (result * base) % modulus;
        }
        exponent >>= 1;
        base = (base * base) % modulus;
    }

    return result;
}
```

## 字符串转换

### 转换为字符串
```cpp
i128 value = 123456789012345678901234567890LL;

// 转换为不同进制的字符串
TString decimal = value.ToString();        // 十进制
TString hex = value.ToString(16);          // 十六进制
TString binary = value.ToString(2);        // 二进制
TString octal = value.ToString(8);         // 八进制
```

### 从字符串解析
```cpp
// 解析不同进制的数字
TString input = "123456789012345678901234567890";
i128 parsed = i128::FromString(input);

TString hexInput = "0x123456789abcdef0123456789abcdef0";
ui128 hexParsed = ui128::FromString(hexInput, 16);

// 带错误检查的严格解析
try {
    i128 safeParsed = i128::ParseStrict(input);
} catch (const TParseException& e) {
    std::cerr << "Parse error: " << e.what() << std::endl;
}
```

## 位操作

### 位操作函数
```cpp
ui128 value = ui128::FromString("0x123456789abcdef0123456789abcdef0");

// 位计数
int bit_count = CountBits(value);                    // 设置位的数量
int leading_zeros = CountLeadingZeros(value);        // 前导零的数量
int trailing_zeros = CountTrailingZeros(value);      // 尾随零的数量

// 位测试和操作（如果提供）
bool test_bit = value.TestBit(10);        // 测试第10位
value.SetBit(10);                         // 设置第10位
value.ClearBit(10);                       // 清除第10位
```

### 位掩码操作
```cpp
// 创建和使用位掩码
ui128 mask = ui128(0) - 1;               // 全1掩码
ui128 lowByteMask = 0xff;                 // 低字节掩码
ui128 highByteMask = lowByteMask << 56;  // 高字节掩码

ui128 value = /* 某个值 */;
ui128 lowByte = value & lowByteMask;      // 提取低字节
ui128 highByte = (value & highByteMask) >> 56; // 提取高字节
```

## 性能优化

### 编译器优化
```cpp
// 编译时会自动选择最优实现
void OptimizedCalculation() {
    // 在支持 __int128 的平台上，会使用硬件指令
    ui128 a = 12345678901234567890ULL;
    ui128 b = 98765432109876543210ULL;

    ui128 result = a * b;  // 可能会使用硬件128位乘法
}
```

### 内存优化
```cpp
// 使用引用避免拷贝
void ProcessLargeInt128(const ui128& value) {
    // 处理大整数
}

// 返回值优化
ui128 ExpensiveCalculation() {
    ui128 result = /* 复杂计算 */;
    return result;  // RVO 会避免不必要的拷贝
}
```

### 常量定义
```cpp
// 预定义的常量
constexpr ui128 KILOBYTE = 1024;
constexpr ui128 MEGABYTE = KILOBYTE * KILOBYTE;
constexpr ui128 GIGABYTE = MEGABYTE * KILOBYTE;
constexpr ui128 TERABYTE = GIGABYTE * KILOBYTE;
constexpr ui128 PETABYTE = TERABYTE * KILOBYTE;
```

## 平台特性

### 字节序处理
```cpp
// 库会自动处理大小端序问题
ui128 value = ui128(0x12345678, 0x9abcdef0);
// 在不同平台上，内存布局会自动调整
```

### 编译器支持检测
```cpp
#if defined(Y_HAVE_INT128)
    // 使用编译器原生 __int128 支持
    using NativeInt128 = unsigned __int128;
#else
    // 使用软件实现的128位整数
    using NativeInt128 = ui128;
#endif
```

## 最佳实践

### 类型安全
```cpp
// 安全的类型转换
void SafeConversion(i128 largeValue) {
    if (largeValue >= std::numeric_limits<i64>::min() &&
        largeValue <= std::numeric_limits<i64>::max()) {
        i64 safeValue = static_cast<i64>(largeValue);
        // 安全地使用 safeValue
    }
}

// 除零检查
i128 SafeDivision(i128 dividend, i128 divisor) {
    if (divisor == 0) {
        throw std::invalid_argument("Division by zero");
    }
    return dividend / divisor;
}
```

### 性能考虑
```cpp
// 避免频繁的临时对象创建
void EfficientProcessing(const TVector<ui128>& values) {
    ui128 sum = 0;
    for (const ui128& value : values) {
        sum += value;  // 使用引用避免拷贝
    }
}

// 使用合适的数据类型
void ChooseRightType() {
    // 如果64位足够，不要使用128位
    i64 normalCalculation = 1234567890LL * 987654321LL;  // 可能溢出

    // 使用128位避免溢出
    ui128 safeCalculation = ui128(1234567890ULL) * ui128(987654321ULL);
}
```

## 注意事项

### 设计限制
- **不暴露内部实现**: 没有 GetHigh()/GetLow() 等函数
- **单一构造**: 不支持多参数构造函数
- **类型一致性**: 保持与原生整数类型相同的使用方式

### 使用注意
- **溢出处理**: 128位整数的运算也可能溢出
- **除法安全**: 除法运算时需要检查除零
- **类型转换**: 注意有符号和无符号之间的转换

### 性能考虑
- **运算开销**: 128位运算比64位运算慢
- **内存使用**: 128位整数占用16字节内存
- **平台差异**: 不同平台的性能可能不同

## 相关项目

该库统一了 Arcadia 中分散的128位整数实现，提供了：
- 统一的接口设计
- 跨平台兼容性
- 性能优化
- 类型安全保证

项目追踪: https://st.yandex-team.ru/IGNIETFERRO-697

这个128位整数库为 YTsaurus 项目提供了处理大数的能力，适用于需要超出标准整数范围的计算场景，同时保持了与原生整数类型一致的使用体验。