# Arcadia Future 互操作库

## 项目/模块描述

`arcadia_future_interop` 是 YTsaurus 项目中的一个核心互操作库，专门用于在 YTsaurus 内部的 `TFuture` 实现和 Arcadia (Yandex 内部构建系统) 的 `::NThreading::TFuture` 实现之间进行转换和桥接。

该模块解决了在混合使用两套 Future 实现时的兼容性问题，确保异步操作能够在不同框架之间无缝传递和执行。

## 主要功能

### 1. 双向 Future 转换
- **`ToArcadiaFuture`**: 将 YTsaurus 的 `TFuture<T>` 转换为 Arcadia 的 `::NThreading::TFuture<T>`
- **`FromArcadiaFuture`**: 将 Arcadia 的 `::NThreading::TFuture<T>` 转换为 YTsaurus 的 `TFuture<T>`

### 2. 类型安全
- 支持泛型类型 `T`，包括 `void` 类型
- 保持类型信息的完整传递
- 编译时类型检查

### 3. 异常和错误处理
- 正确传播异常和错误状态
- 支持 YTsaurus 的 `TError` 错误机制
- 异常安全的内存管理

### 4. 异步操作保持
- 转换过程保持异步特性
- 不阻塞原始 Future 的执行
- 支持回调机制的正确传递

## 文件说明

### 核心文件

| 文件名 | 类型 | 描述 |
|--------|------|------|
| `interop.h` | 头文件 | 主要的 API 接口声明，包含两个转换函数的声明 |
| `interop-inl.h` | 内联实现文件 | 模板函数的具体实现，通过 include 机制包含 |

### 测试文件

| 文件名 | 类型 | 描述 |
|--------|------|------|
| `unittests/interop_ut.cpp` | 单元测试 | 完整的测试套件，覆盖各种转换场景 |

### 构建配置文件

| 文件名 | 类型 | 描述 |
|--------|------|------|
| `CMakeLists.txt` | CMake 主配置 | 平台检测和子 CMake 文件包含 |
| `CMakeLists.*.txt` | 平台特定配置 | 针对不同平台的构建配置 |
| `ya.make` | YaTool 构建配置 | Arcadia 构建系统的配置文件 |

## 使用方法

### 基本用法

```cpp
#include <yt/yt/library/arcadia_future_interop/interop.h>

using namespace NYT;

// 从 YTsaurus Future 转换到 Arcadia Future
auto ytPromise = NewPromise<int>();
ytPromise.Set(42);
auto ytFuture = ytPromise.ToFuture();

// 转换为 Arcadia Future
auto arcadiaFuture = ToArcadiaFuture(ytFuture);
int value = arcadiaFuture.GetValueSync(); // value = 42

// 从 Arcadia Future 转换到 YTsaurus Future
auto arcadiaPromise = ::NThreading::NewPromise<std::string>();
arcadiaPromise.SetValue("Hello");
auto arcadiaFuture = arcadiaPromise.GetFuture();

// 转换为 YTsaurus Future
auto ytFuture = FromArcadiaFuture(arcadiaFuture);
std::string result = ytFuture.Get().ValueOrThrow(); // result = "Hello"
```

### void 类型支持

```cpp
// void 类型的 Future 转换
auto ytVoidPromise = NewPromise<void>();
auto ytVoidFuture = ytVoidPromise.ToFuture();
auto arcadiaVoidFuture = ToArcadiaFuture(ytVoidFuture);

ytVoidPromise.Set();
arcadiaVoidFuture.GetValueSync(); // 成功完成
```

### 错误处理

```cpp
// 错误状态的正确传递
auto ytPromise = NewPromise<int>();
ytPromise.Set(TError("Something went wrong"));
auto ytFuture = ytPromise.ToFuture();

auto arcadiaFuture = ToArcadiaFuture(ytFuture);
// arcadiaFuture.HasException() 将为 true
```

## 依赖项

### 核心依赖
- **yt/yt/core/actions/future.h** - YTsaurus Future 实现
- **library/cpp/threading/future/core/future.h** - Arcadia Future 实现

### 构建时依赖
- **yt-yt-core** - YTsaurus 核心库
- **cpp-threading-future** - Arcadia 线程和 Future 库
- **contrib-libs-cxxsupp** - C++ 标准库支持
- **yutil** - Yandex 基础工具库

### 平台依赖
- **linux-headers-generic** - Linux 系统头文件（Linux 平台）

## 实现原理

### 1. Promise-Future 模式
转换过程使用经典的 Promise-Future 模式：

- 创建目标框架的 Promise 对象
- 订阅源 Future 的完成事件
- 在回调中将结果或异常传播到目标 Promise

### 2. 异步桥接机制
```cpp
template <class T>
::NThreading::TFuture<T> ToArcadiaFuture(const TFuture<T>& future)
{
    // 1. 创建 Arcadia Promise
    auto promise = ::NThreading::NewPromise<T>();
    auto wrappedFuture = promise.GetFuture();

    // 2. 订阅 YTsaurus Future 的完成事件
    future.Subscribe(BIND([promise = std::move(promise)] (const TErrorOr<T>& valueOrError) mutable {
        // 3. 处理结果或异常
        try {
            if constexpr (std::is_same_v<T, void>) {
                valueOrError.ThrowOnError();
                promise.TrySetValue();
            } else {
                auto value = valueOrError.ValueOrThrow();
                promise.TrySetValue(std::move(value));
            }
        } catch (...) {
            promise.TrySetException(std::current_exception());
        }
    }));

    return wrappedFuture;
}
```

### 3. 类型特化处理
- 对 `void` 类型进行特殊处理，避免值传递
- 使用 `if constexpr` 实现编译时分支
- 保持异常安全性和内存效率

### 4. 内存管理
- 使用移动语义优化性能
- 正确处理 Promise 的生命周期
- 避免内存泄漏和悬挂引用

### 5. 线程安全
- 转换操作本身是线程安全的
- 正确处理跨线程的异步操作
- 保持原始 Future 的线程安全特性

## 测试覆盖

该模块包含全面的单元测试，覆盖以下场景：

1. **正常值传递** - 各种数据类型的成功转换
2. **异常传播** - 错误状态在不同框架间的正确传递
3. **void 类型** - 空返回值类型的特殊处理
4. **取消操作** - Future 取消状态的处理
5. **异步行为** - 转换过程的异步特性验证
6. **内存效率** - 移动语义和拷贝次数的优化验证

## 注意事项

1. **性能考虑** - 转换操作会创建新的 Promise/Future 对象，有一定的性能开销
2. **异常安全** - 转换过程中异常会被正确捕获和传播
3. **取消传播** - 一端的取消操作会影响另一端的状态
4. **类型匹配** - 模板参数类型必须在两端完全匹配
5. **线程模型** - 遵循各框架的线程模型和调度规则