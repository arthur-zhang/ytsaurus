# Arrow Adapter 模块

## 项目描述

`arrow_adapter` 是 YTsaurus 系统中的一个适配器模块，用于在 YTsaurus 内部集成 Apache Arrow、Parquet 和 ORC 格式支持。该模块提供了高效的列式数据处理能力，实现了 YTsaurus 流式接口与 Arrow 标准库之间的桥接。

## 主要功能

### 1. 格式适配器
- **Parquet 适配器**: 将 YTsaurus 数据流适配为 Apache Parquet 格式的随机访问文件接口
- **ORC 适配器**: 将 YTsaurus 数据流适配为 Apache ORC 格式的随机访问文件接口，支持环形缓冲区优化

### 2. 环形缓冲区 (TRingBuffer)
- 实现高效的环形缓冲区，用于 ORC 数据的流式读取
- 支持数据的顺序写入和随机读取
- 自动管理缓冲区边界，处理环绕写入/读取场景

### 3. Schema 提取
- 从 Parquet 元数据中提取 Arrow Schema
- 从 ORC 元数据中提取 Arrow Schema
- 支持仅从元数据创建 Schema 而不需要完整数据流

### 4. 错误处理
- 统一的 Arrow 状态错误处理机制
- 将 Arrow 库的错误转换为 YTsaurus 错误体系

## 文件说明

| 文件名 | 描述 | 主要功能 |
|--------|------|----------|
| `public.h` | 公共接口头文件 | 定义基本的类型别名和公共接口 |
| `arrow.h` | 主要实现头文件 | 定义 TRingBuffer 类和各种适配器接口 |
| `arrow.cpp` | 核心实现文件 | 包含所有适配器和缓冲区的具体实现 |
| `ya.make` | 构建配置 (YaTool) | 定义构建依赖和源文件 |
| `CMakeLists.txt` | CMake 构建配置 | 跨平台 CMake 构建脚本 |

### 核心类和接口

#### TRingBuffer
```cpp
class TRingBuffer {
    // 构造函数，指定缓冲区大小
    explicit TRingBuffer(i64 bufferSize);

    // 从指定偏移读取数据
    void Read(i64 offset, i64 byteCount, char* output);

    // 写入数据到缓冲区
    arrow20::Status Write(TRef data);

    // 获取缓冲区位置信息
    i64 GetBeginPosition() const;
    i64 GetEndPosition() const;
};
```

#### 适配器创建函数
```cpp
// 创建 Parquet 适配器
TArrowRandomAccessFilePtr CreateParquetAdapter(
    const TString* metadata,
    i64 startMetadataOffset,
    std::shared_ptr<IInputStream> reader = nullptr);

// 创建 ORC 适配器
TArrowRandomAccessFilePtr CreateOrcAdapter(
    const TString* metadata,
    i64 startMetadataOffset,
    i64 maxStripeSize = 1,
    std::shared_ptr<IInputStream> reader = nullptr);

// Schema 提取函数
TArrowSchemaPtr CreateArrowSchemaFromParquetMetadata(const TString* metadata, i64 startIndex);
TArrowSchemaPtr CreateArrowSchemaFromOrcMetadata(const TString* metadata, i64 startIndex);
```

## 使用方法

### 基本用法示例

```cpp
#include <yt/yt/library/arrow_adapter/arrow.h>

// 1. 创建 Parquet 适配器
const TString* parquetMetadata = /* 获取 Parquet 元数据 */;
i64 metadataOffset = /* 元数据偏移量 */;
auto inputStream = /* YTsaurus 输入流 */;

auto parquetAdapter = NYT::NArrow::CreateParquetAdapter(
    parquetMetadata,
    metadataOffset,
    inputStream);

// 2. 创建 Arrow Schema
auto arrowSchema = NYT::NArrow::CreateArrowSchemaFromParquetMetadata(
    parquetMetadata,
    metadataOffset);

// 3. 使用适配器读取数据
// 适配器实现了 arrow::io::RandomAccessFile 接口
// 可以直接用于 Arrow 库的各种读取器
```

### ORC 文件处理

```cpp
// 获取 ORC 文件的最大 stripe 大小
i64 maxStripeSize = NYT::NArrow::GetMaxStripeSize(
    orcMetadata,
    metadataOffset);

// 创建 ORC 适配器（带环形缓冲区优化）
auto orcAdapter = NYT::NArrow::CreateOrcAdapter(
    orcMetadata,
    metadataOffset,
    maxStripeSize,  // 环形缓冲区大小
    inputStream);

// 从 ORC 元数据创建 Schema
auto arrowSchema = NYT::NArrow::CreateArrowSchemaFromOrcMetadata(
    orcMetadata,
    metadataOffset);
```

## 依赖项

### 核心依赖
- **Apache Arrow 2.0+**: 列式数据处理框架
- **Apache Parquet**: 列式存储格式支持
- **Apache ORC**: 优化的列式文件格式
- **YTsaurus Core**: YTsaurus 核心库

### YTsaurus 内部依赖
- `library/cpp/yt/assert`: YTsaurus 断言库
- `yt/yt/core/misc/error`: YTsaurus 错误处理
- `library/cpp/yt/memory/ref`: YTsaurus 内存引用管理

### 构建依赖
- **CMake 3.22+**: 跨平台构建系统
- **Clang-18**: C++ 编译器
- **Conan**: C++ 包管理器

## 实现原理

### 1. 流式适配架构
适配器实现了 Arrow 的 `RandomAccessFile` 接口，将 YTsaurus 的流式数据源包装成支持随机访问的文件接口。这使得 Arrow 库可以直接处理 YTsaurus 的数据流，而无需将完整数据加载到内存中。

### 2. 环形缓冲区优化
对于 ORC 格式，适配器使用环形缓冲区来优化数据访问：

- **写入优化**: 数据按顺序写入环形缓冲区，自动处理环绕写入
- **读取优化**: 支持从任意偏移位置读取，处理环绕读取场景
- **内存效率**: 固定大小的缓冲区，避免无限增长
- **性能优化**: 减少内存拷贝次数，提高数据处理效率

### 3. 元数据分离
适配器支持将元数据与实际数据流分离处理：

- **元数据优先**: 可以仅使用元数据创建 Schema
- **延迟加载**: 实际数据按需从输入流加载
- **内存优化**: 避免将完整文件加载到内存

### 4. 错误处理机制
通过 `ThrowOnError` 函数统一处理 Arrow 库的状态码，将其转换为 YTsaurus 的异常体系，确保错误处理的一致性。

### 5. 跨文件数据组合
适配器能够将分散的元数据流和数据流组合成统一的文件接口：
- 元数据存储在内存中的 `TString` 中
- 实际数据通过 `IInputStream` 按需读取
- 通过偏移量管理协调两种数据源的访问

## 性能特点

- **内存效率**: 使用固定大小缓冲区，避免内存无限增长
- **流式处理**: 支持大文件的处理而无需完全加载到内存
- **随机访问**: 提供真正的随机访问能力，支持 Arrow 库的所有功能
- **零拷贝优化**: 在可能的情况下避免不必要的数据拷贝

## 应用场景

该模块主要用于：
- YTsaurus 与 Arrow 生态系统的集成
- 列式数据格式的高效处理
- 大数据分析工作流中的格式转换
- SPYT (Spark on YTsaurus) 等组件的数据处理支持