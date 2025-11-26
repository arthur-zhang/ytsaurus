# YTsaurus Apache Arrow 集成

## 概述

`arrow` 目录提供了 YTsaurus 与 Apache Arrow 列式存储格式的集成支持。Apache Arrow 是一个高性能的内存列式数据处理框架，该模块实现了 YTsaurus 数据格式与 Arrow 格式之间的相互转换。

## 核心功能

### 格式转换
- **YTsaurus to Arrow**: 将 YTsaurus 表数据转换为 Arrow 格式
- **Arrow to YTsaurus**: 将 Arrow 数据转换为 YTsaurus 表格式
- **Schema 映射**: 两种格式之间的类型映射和模式转换

### 数据流处理
- **行流编码器**: 将 YTsaurus 行流编码为 Arrow 格式
- **行流解码器**: 将 Arrow 数据解码为 YTsaurus 行流
- **高效序列化**: 针对大数据量的优化序列化

### 类型系统支持
支持 Arrow 和 YTsaurus 之间的完整类型映射：
- **基础数据类型**: 整数、浮点数、布尔值、字符串
- **复合类型**: 结构体、列表、映射
- **特殊类型**: 时间戳、二进制数据、UUID
- **NULL 值处理**: 完整的空值语义支持

## 主要文件说明

### 核心文件
- `public.h/.cpp`: 公共接口和日志配置
- `schema.h/.cpp`: Schema 转换实现，处理类型映射
- `arrow_row_stream_encoder.h/.cpp`: Arrow 行流编码器实现
- `arrow_row_stream_decoder.h/.cpp`: Arrow 行流解码器实现

### 构建配置
- `CMakeLists.txt`: 跨平台构建配置
- 平台特定的 CMakeLists 文件：Linux 和 macOS 的不同架构支持
- `ya.make`: YaTool 构建系统配置

### 测试
- `unittests/`: 单元测试目录

## 使用示例

### Schema 转换
```cpp
#include <yt/yt/client/arrow/schema.h>

// 从 Arrow Schema 创建 YTsaurus TableSchema
auto arrowSchema = ...;  // Arrow schema 对象
auto ytSchema = NYT::NArrow::CreateYTTableSchemaFromArrowSchema(arrowSchema);
```

### 行流编码
```cpp
#include <yt/yt/client/arrow/arrow_row_stream_encoder.h>

// 创建 Arrow 行流编码器
auto encoder = NYT::NArrow::CreateArrowRowStreamEncoder(
    schema,           // YTsaurus 表 Schema
    columns,          // 要编码的列
    nameTable,        // 名称表
    fallbackEncoder,  // 备用编码器
    controlAttributesConfig // 控制属性配置
);
```

## 类型映射规则

### 数值类型
- Arrow `int8` → YTsaurus `Int8`
- Arrow `int16` → YTsaurus `Int16`
- Arrow `int32` → YTsaurus `Int32`
- Arrow `int64` → YTsaurus `Int64`
- Arrow `uint8` → YTsaurus `Uint8`
- Arrow `uint16` → YTsaurus `Uint16`
- Arrow `uint32` → YTsaurus `Uint32`
- Arrow `uint64` → YTsaurus `Uint64`
- Arrow `float` → YTsaurus `Float`
- Arrow `double` → YTsaurus `Double`

### 字符串和二进制类型
- Arrow `string` → YTsaurus `String`
- Arrow `binary` → YTsaurus `String`
- Arrow `large_string` → YTsaurus `String`

### 时间类型
- Arrow `timestamp` → YTsaurus `Timestamp`
- Arrow `date32` → YTsaurus `Date`
- Arrow `time32` → YTsaurus `Time`

### 复合类型
- Arrow `struct` → YTsaurus 结构体类型
- Arrow `list` → YTsaurus 数组类型
- Arrow `map` → YTsaurus 映射类型

## 性能优化

### 内存管理
- **零拷贝优化**: 尽可能避免数据复制
- **内存池**: 重用内存分配
- **批量处理**: 批量处理行数据以减少开销

### 序列化优化
- **列式存储**: 利用 Arrow 的列式存储优势
- **压缩支持**: 支持各种压缩算法
- **向量化处理**: 使用 SIMD 指令优化

### 并行处理
- **多线程支持**: 支持并行编码/解码
- **流水线处理**: 数据流水线处理优化
- **异步 I/O**: 支持异步数据传输

## 构建和部署

### 依赖项
- **Apache Arrow**: 核心依赖，需要特定版本兼容
- **YTsaurus 核心库**: 表客户端、格式支持等
- **Protocol Buffers**: 序列化支持

### 平台支持
支持多平台编译：
- Linux x86_64
- Linux aarch64
- macOS x86_64
- macOS arm64

### 构建选项
```bash
# 标准构建
cmake -DCMAKE_BUILD_TYPE=Release ...

# 开发构建
cmake -DCMAKE_BUILD_TYPE=Debug ...
```

## 错误处理

### 类型不匹配
- 自动类型转换尝试
- 详细的错误信息
- 优雅降级机制

### 内存不足
- 内存使用监控
- 流式处理支持
- 错误恢复机制

### 数据损坏
- 完整性检查
- 错误检测和报告
- 数据恢复选项

## 应用场景

### 数据分析
- **大数据分析**: 与现代分析工具集成
- **实时数据处理**: 流式数据处理
- **机器学习**: 与 ML 框架集成

### 数据交换
- **ETL 流程**: 数据提取、转换、加载
- **数据迁移**: 不同系统间的数据迁移
- **格式转换**: 各种数据格式间的转换

### 性能优化
- **查询加速**: 利用 Arrow 的列式存储优势
- **内存效率**: 减少内存使用和提高缓存命中率
- **并行计算**: 支持现代多核处理器

## 最佳实践

### 性能调优
1. **批量操作**: 尽可能使用批量处理
2. **内存预热**: 预分配内存以减少运行时开销
3. **类型选择**: 选择最适合的数据类型
4. **压缩设置**: 根据数据特点选择压缩算法

### 开发建议
1. **错误处理**: 始终检查返回值和异常
2. **资源管理**: 正确管理内存和资源生命周期
3. **版本兼容性**: 注意 Arrow 版本兼容性
4. **测试覆盖**: 确保充分测试各种边界情况

## 扩展性

该模块设计支持：
- **自定义类型**: 添加新的类型映射
- **性能插件**: 自定义性能优化
- **格式扩展**: 支持新的 Arrow 功能
- **监控集成**: 添加性能监控和指标

## 注意事项

1. **版本兼容性**: 确保 Arrow 版本与 YTsaurus 兼容
2. **内存使用**: 大数据集可能消耗大量内存
3. **线程安全**: 注意多线程环境下的使用
4. **性能监控**: 定期监控性能指标
5. **错误恢复**: 实现适当的错误恢复机制