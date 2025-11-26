# 枚举位集合（Enum BitSet）库

为枚举值范围提供高性能位操作的模板类库。

## 概述

`TEnumBitSet` 是一个模板类，为枚举类型的连续值范围提供栈内存位掩码操作。它继承自 `TBitMap`，专门针对枚举值进行了优化，提供了类型安全的位操作功能。

## 核心特性

### 类型安全
- **强类型**: 基于 C++ 枚举类型的位操作
- **范围检查**: 自动验证枚举值的有效性
- **编译时优化**: 编译时确定大小，运行时零开销

### 高效存储
- **栈内存**: 使用栈内存，避免堆分配
- **紧凑存储**: 每个枚举值仅占用一位
- **快速访问**: O(1) 时间复杂度的位操作

### 丰富接口
- **位操作**: 完整的位操作集合（设置、清除、翻转、测试）
- **安全操作**: 提供边界检查的安全版本
- **流式接口**: 支持链式调用
- **初始化**: 多种构造和初始化方式

## 模板参数

```cpp
template <typename TEnum, int mbegin, int mend>
class TEnumBitSet
```

- **TEnum**: 枚举类型
- **mbegin**: 枚举范围的起始值（包含）
- **mend**: 枚举范围的结束值（不包含）

## 使用示例

### 定义枚举和位集合
```cpp
enum class EStatus {
    Active = 0,
    Inactive,
    Pending,
    Suspended,
    Deleted
};

using TStatusMask = TEnumBitSet<EStatus, 0, 5>;
```

### 基本操作
```cpp
// 构造
TStatusMask mask;                                    // 空集合
TStatusMask mask2(EStatus::Active);                 // 单个值
TStatusMask mask3(EStatus::Active, EStatus::Pending); // 多个值

// 设置和测试
mask.Set(EStatus::Active);
mask.Set(EStatus::Pending);
bool hasActive = mask.Test(EStatus::Active);        // true

// 清除和翻转
mask.Reset(EStatus::Active);
mask.Flip(EStatus::Inactive);
mask.Flip();                                        // 翻转所有位
```

### 安全操作
```cpp
TStatusMask mask;

// 安全操作会检查枚举值的有效范围
mask.SafeSet(EStatus::Active);                      // 正常设置
mask.SafeSet(static_cast<EStatus>(100));            // 无效值，忽略

bool isValid = mask.SafeTest(EStatus::Active);      // true
bool isInvalid = mask.SafeTest(static_cast<EStatus>(100)); // false
```

### 迭代器构造
```cpp
std::vector<EStatus> statuses = {EStatus::Active, EStatus::Pending};
TStatusMask mask(statuses.begin(), statuses.end());
```

### 集合操作
```cpp
TStatusMask mask1(EStatus::Active, EStatus::Pending);
TStatusMask mask2(EStatus::Active, EStatus::Inactive);

// 比较操作
bool equal = (mask1 == mask2);
bool notEqual = (mask1 != mask2);
bool lessThan = (mask1 < mask2);                    // 字典序比较
```

## 接口详解

### 构造函数
```cpp
TEnumBitSet();                                      // 默认构造
explicit TEnumBitSet(TEnum c);                     // 单值构造
TEnumBitSet(TEnum c1, TEnum c2, ...R... r);       // 多值构造
template<class TIt>
TEnumBitSet(const TIt& begin_, const TIt& end_);   // 迭代器构造
```

### 位操作
```cpp
TThis& Set(TEnum c);                               // 设置位
TThis& Set(TEnum c, bool val);                     // 条件设置
TThis& Reset(TEnum c);                             // 清除位
TThis& Flip(TEnum c);                              // 翻转位
bool Test(TEnum c) const;                          // 测试位
TThis& Flip();                                     // 翻转所有位
TThis& Reset();                                    // 清除所有位
```

### 安全操作
```cpp
TThis& SafeSet(TEnum c);                           // 安全设置
TThis& SafeSet(TEnum c, bool val);                 // 安全条件设置
TThis& SafeReset(TEnum c);                         // 安全清除
TThis& SafeFlip(TEnum c);                          // 安全翻转
bool SafeTest(TEnum c) const;                      // 安全测试
static TThis SafeConstruct(TEnum c);               // 安全构造
```

### 工具方法
```cpp
static bool IsValid(TEnum c);                      // 验证枚举值
static const int BeginIndex;                       // 起始索引
static const int EndIndex;                         // 结束索引
static const size_t BitsetSize;                    // 位集合大小
```

## 实现细节

### 内存布局
- 继承自 `TBitMap<mend - mbegin>`
- 使用连续的位存储枚举值
- 每个枚举值映射到一个唯一的位位置

### 位置计算
```cpp
static int Pos(TEnum c) {
    return int(c) - BeginIndex;
}
```

### 边界检查
```cpp
static bool IsValid(TEnum c) {
    return int(c) >= BeginIndex && int(c) < EndIndex;
}
```

## 性能特性

### 时间复杂度
- **设置/清除/翻转**: O(1)
- **测试**: O(1)
- **比较**: O(n) 其中 n 是位块数量

### 空间复杂度
- **存储**: O(1) - 编译时确定大小
- **内存**: 栈分配，无堆内存使用

### 编译器优化
- **内联**: 所有小函数都会被内联
- **常量传播**: 编译时确定的操作会优化掉
- **位操作**: 编译器生成高效的位操作指令

## 应用场景

### 状态管理
```cpp
enum class EFeature {
    Compression = 0,
    Encryption,
    Caching,
    Logging,
    Monitoring
};

using TFeatureSet = TEnumBitSet<EFeature, 0, 5>;

TFeatureSet features;
features.Set(EFeature::Compression);
features.Set(EFeature::Encryption);

if (features.Test(EFeature::Compression)) {
    // 启用压缩功能
}
```

### 权限控制
```cpp
enum class EPermission {
    Read = 0,
    Write,
    Execute,
    Admin
};

using TPermissionMask = TEnumBitSet<EPermission, 0, 4>;

TPermissionMask userPermissions;
userPermissions.Set(EPermission::Read);
userPermissions.Set(EPermission::Write);
```

### 配置管理
```cpp
enum class EConfigOption {
    Debug = 0,
    Verbose,
    Profiling,
    Logging
};

using TConfigMask = TEnumBitSet<EConfigOption, 0, 4>;

TConfigMask config;
if (debugMode) {
    config.Set(EConfigOption::Debug);
    config.Set(EConfigOption::Verbose);
}
```

## 最佳实践

### 命名约定
```cpp
// 推荐的命名方式
using TStatusMask = TEnumBitSet<EStatus, 0, 5>;
using TPermissionSet = TEnumBitSet<EPermission, 0, 4>;
using TFeatureFlags = TEnumBitSet<EFeature, 0, 8>;
```

### 错误处理
```cpp
// 使用安全操作避免越界
if (TStatusMask::IsValid(status)) {
    mask.Set(status);
} else {
    mask.SafeSet(status);  // 自动忽略无效值
}
```

### 性能优化
```cpp
// 批量操作时使用迭代器构造
std::vector<EStatus> statuses = /* ... */;
TStatusMask mask(statuses.begin(), statuses.end());

// 避免重复的边界检查
if (TStatusMask::IsValid(status)) {
    mask.Set(status);
    // 更多操作，无需再次检查
}
```

## 注意事项

1. **枚举范围**: 确保指定的范围包含所有需要的枚举值
2. **连续性**: 枚举值应该是连续的，中间没有间隙
3. **边界值**: `mend` 参数是不包含的，需要加1
4. **类型安全**: 使用 `enum class` 而不是传统枚举以获得更好的类型安全

## 兼容性

- **C++11**: 支持可变参数模板
- **C++14**: 更好的模板推导
- **C++17**: `if constexpr` 支持（如果使用）
- **编译器**: GCC 4.8+, Clang 3.4+, MSVC 2015+

## 相关库

- **langmask**: 使用此库实现的语言掩码
- **bitmap**: 基础位图实现
- **serialized_enum**: 枚举序列化支持

## 测试

包含完整的单元测试，覆盖：
- 基本功能测试
- 边界条件测试
- 安全操作测试
- 性能测试
- 异常情况处理