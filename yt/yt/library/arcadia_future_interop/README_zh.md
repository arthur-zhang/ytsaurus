# Arcadia Future 互操作库

## 概述

这个库提供了 YTsaurus Future 实现与 Arcadia (library/cpp/threading/future) Future 实现之间的互操作功能。它允许在两个不同的 Future 系统之间进行转换，确保代码的兼容性和集成性。

## 功能特性

- **双向转换**：支持 YTsaurus Future 和 Arcadia Future 之间的相互转换
- **类型安全**：模板化设计，支持任意类型的 Future
- **异常处理**：正确处理和传递异常情况
- **异步支持**：保持异步操作的完整语义

## 文件说明

### 核心文件

- `interop.h` - 头文件，定义转换函数的接口
- `interop-inl.h` - 内联实现文件，包含具体的转换逻辑

### 构建文件

- `CMakeLists.txt` - CMake 构建配置
- `CMakeLists.*.txt` - 针对不同平台的特定构建配置
- `ya.make` - YaMake 构建系统配置

### 测试文件

- `unittests/interop_ut.cpp` - 单元测试，验证转换功能的正确性

## 核心接口

### ToArcadiaFuture

将 YTsaurus TFuture 转换为 Arcadia TFuture：

```cpp
template <class T>
::NThreading::TFuture<T> ToArcadiaFuture(const TFuture<T>& future);
```

### FromArcadiaFuture

将 Arcadia TFuture 转换为 YTsaurus TFuture：

```cpp
template <class T>
TFuture<T> FromArcadiaFuture(const ::NThreading::TFuture<T>& future);
```

## 实现原理

### 转换机制

转换过程通过创建新的 Promise 和对应的 Future 来实现：

1. **源 Future 订阅**：在源 Future 上设置回调
2. **目标 Promise 创建**：创建目标系统的 Promise
3. **结果传递**：当源 Future 完成时，将结果或异常传递给目标 Promise
4. **类型适配**：处理不同系统的 void 类型差异

### 异常处理

- YTsaurus 使用 `TErrorOr<T>` 包装结果
- Arcadia 使用异常机制
- 转换时正确处理两种异常模型

### 特殊情况处理

- **void 类型**：针对 void 类型提供特化处理
- **异常捕获**：确保异常不会在转换过程中丢失
- **线程安全**：保证多线程环境下的正确性

## 使用示例

```cpp
#include <yt/yt/library/arcadia_future_interop/interop.h>

using namespace NYT;

// YTsaurus Future 到 Arcadia Future
auto ytFuture = AsyncYtOperation();
auto arcadiaFuture = ToArcadiaFuture(ytFuture);

// Arcadia Future 到 YTsaurus Future
auto arcadiaFuture2 = AsyncArcadiaOperation();
auto ytFuture2 = FromArcadiaFuture(arcadiaFuture2);
```

## 依赖项

- YTsaurus 核心库 (`yt/yt/core/actions/future.h`)
- Arcadia threading 库 (`library/cpp/threading/future/core/future.h`)

## 测试

运行单元测试以验证功能：

```bash
# 在构建目录中
ninja test_arcadia_future_interop
```

测试覆盖了以下场景：
- 基本类型转换
- void 类型转换
- 异常传递
- 复合类型转换

## 注意事项

1. **性能考虑**：转换涉及创建新的 Promise/Future 对象
2. **生命周期管理**：确保源 Future 在转换完成前保持有效
3. **异常安全**：转换过程中的异常会被正确传播
4. **线程模型**：遵循两个系统的线程模型约束

## 平台支持

支持以下平台：
- Linux x86_64
- Linux aarch64
- macOS x86_64
- macOS arm64

## 维护说明

- 保持与两个 Future 系统的同步更新
- 确保异常处理的一致性
- 定期更新测试用例覆盖新场景