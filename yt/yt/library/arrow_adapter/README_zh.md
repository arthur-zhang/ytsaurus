# Apache Arrow 适配器库

## 概述

这个库提供了 YTsaurus 与 Apache Arrow 之间的适配功能，使 YTsaurus 能够与 Arrow 生态系统进行集成。Apache Arrow 是一个跨平台的内存列式数据格式，专为高效的内存数据分析而设计。

## 功能特性

- **Ring Buffer 实现**：高效的环形缓冲区，用于数据流处理
- **Arrow 集成**：与 Apache Arrow 库的深度集成
- **多格式支持**：支持 Parquet、ORC 等多种列式存储格式
- **错误处理**：统一的错误处理机制
- **内存管理**：与 YTsaurus 内存管理系统集成

## 文件说明

### 核心文件

- `arrow.h` - 主要头文件，定义核心接口和数据结构
- `arrow.cpp` - 实现文件，包含具体的功能实现
- `public.h` - 公共接口头文件，定义对外暴露的类型

### 构建文件

- `CMakeLists.txt` - CMake 构建配置
- `CMakeLists.*.txt` - 针对不同平台的特定构建配置
- `ya.make` - YaMake 构建系统配置

## 核心组件

### TRingBuffer

高效的环形缓冲区实现，用于处理连续的数据流：

```cpp
class TRingBuffer {
public:
    explicit TRingBuffer(i64 bufferSize);

    void Read(i64 offset, i64 byteCount, char* output);
    arrow20::Status Write(TRef data);

    i64 GetBeginPosition() const;
    i64 GetEndPosition() const;
};
```

### 类型定义

```cpp
using TArrowSchemaPtr = std::shared_ptr<arrow20::Schema>;
using TArrowRandomAccessFilePtr = std::shared_ptr<arrow20::io::RandomAccessFile>;
```

### 错误处理

```cpp
void ThrowOnError(const arrow20::Status& status);
```

## 实现原理

### Ring Buffer 设计

环形缓冲区使用固定大小的连续内存区域：

1. **循环写入**：当到达缓冲区末尾时，从开头继续写入
2. **位置追踪**：维护起始和结束位置信息
3. **高效读写**：支持一次或两次内存拷贝完成操作
4. **覆盖策略**：当数据超过缓冲区大小时，覆盖最旧的数据

### 内存管理

- 使用 YTsaurus 的 `TSharedMutableRef` 进行内存管理
- 支持 `InitializeStorage` 选项控制内存初始化
- 标签化的内存分配（`TRingBufferAdapterTag`）

### Arrow 集成

- **Schema 支持**：处理 Arrow Schema 对象
- **IO 适配**：实现 Arrow IO 接口
- **格式转换**：支持 Parquet 和 ORC 格式读写

## 使用示例

### 基本使用

```cpp
#include <yt/yt/library/arrow_adapter/arrow.h>

using namespace NYT::NArrow;

// 创建环形缓冲区
auto buffer = std::make_unique<TRingBuffer>(1024 * 1024); // 1MB

// 写入数据
TRef data = /* 获取数据 */;
buffer->Write(data);

// 读取数据
char output[1024];
buffer->Read(offset, sizeof(output), output);
```

### Arrow 集成

```cpp
// 处理 Arrow 错误
arrow20::Status status = /* Arrow 操作 */;
ThrowOnError(status);

// 使用 Arrow Schema
auto schema = /* 创建或获取 schema */;
```

## 依赖项

- Apache Arrow 库 (contrib/libs/apache/arrow_next)
- Apache ORC 库 (contrib/libs/apache/orc)
- YTsaurus 核心库
- YTsaurus 内存管理库

## 支持的格式

- **Apache Arrow** - 内存列式格式
- **Parquet** - 列式存储格式
- **ORC** - 优化的行列式文件格式

## 性能特性

- **零拷贝**：尽可能减少数据拷贝操作
- **缓存友好**：优化的内存访问模式
- **并发安全**：支持多线程环境下的使用
- **内存效率**：固定大小缓冲区，避免动态分配

## 平台支持

支持以下平台：
- Linux x86_64
- Linux aarch64
- macOS x86_64
- macOS arm64

## 注意事项

1. **缓冲区大小**：根据实际需求选择合适的缓冲区大小
2. **线程安全**：当前实现不是线程安全的，需要外部同步
3. **内存管理**：确保缓冲区生命周期正确管理
4. **错误处理**：所有 Arrow 操作都应检查状态

## 调试和测试

- 使用 YT_VERIFY 进行断言检查
- 详细的错误信息和堆栈跟踪
- 与 Arrow 单元测试集成

## 未来扩展

可能的功能扩展：
- 支持更多 Arrow 数据类型
- 异步 IO 操作
- 批量读写优化
- 压缩支持