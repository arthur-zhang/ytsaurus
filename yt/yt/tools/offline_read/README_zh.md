# offline_read - 离线数据读取工具

## 项目描述

`offline_read` 是 YTsaurus 系统的离线数据读取工具，用于在不连接到集群的情况下读取和分析 YTsaurus 数据块和表数据。该工具支持多种数据格式和读取模式，是数据分析和调试的重要工具。

## 功能特性

- **离线读取**：无需连接集群即可读取数据
- **多格式支持**：支持版本化和非版本化数据
- **Chunk 读取**：直接读取数据块文件
- **数据过滤**：支持基于键范围和数据过滤
- **压缩支持**：自动处理各种压缩格式
- **错误修复**：支持数据块的自动修复

## 文件说明

- `main.cpp` - 主程序实现，包含数据读取和处理逻辑
- `CMakeLists.txt` - CMake 构建配置文件（支持多平台）
- `ya.make` - YaTool 构建系统配置文件

## 使用方法

### 编译
```bash
# 使用 CMake 构建
cmake --build . --target offline_read

# 或使用 ya 工具构建
ya make offline_read
```

### 运行
```bash
./offline_read [options] <chunk-files...>
```

## 实现原理

该工具基于 YTsaurus 的数据读取架构：

1. **Chunk 读取**：使用 Chunk 文件读取器读取数据块
2. **格式解析**：解析数据的内部格式和结构
3. **版本处理**：处理版本化数据的时间线
4. **数据过滤**：根据条件过滤需要的行和列
5. **格式输出**：将数据转换为可读格式输出

## 核心组件

- **TChunkFileReader**：数据块文件读取器
- **TVersionedReader**：版本化数据读取器
- **TSchemalessReader**：无模式数据读取器
- **TRowMerger**：数据合并器

## 使用示例

```bash
# 读取单个数据块
./offline_read chunk_1_0_0.chunks

# 读取多个数据块
./offline_read chunk_*.chunks

# 指定读取范围
./offline_read --lower-key "key1" --upper-key "key2" data.chunks

# 读取特定列
./offline_read --columns "col1,col2,col3" data.chunks
```

## 命令行参数说明

| 参数 | 说明 |
|------|------|
| `--columns` | 指定要读取的列（逗号分隔） |
| `--lower-key` | 指定读取的起始键 |
| `--upper-key` | 指定读取的结束键 |
| `--max-rows` | 限制最大读取行数 |
| `--output-format` | 输出格式（yson/json/text） |
| `--verbose` | 详细输出模式 |

## 依赖项

### 核心依赖
- `yt/yt/server/lib/io/` - IO 库
- `yt/yt/ytlib/chunk_client/` - 数据块客户端库
- `yt/yt/ytlib/table_client/` - 表客户端库
- `yt/yt/library/row_merger/` - 行合并库

### 系统依赖
- C++20 编译器
- CMake 3.22+
- YTsaurus 核心库
- Zlib/LZ4 压缩库

## 相关概念

### Chunk
YTsaurus 的基本数据存储单元，包含实际数据和元数据。

### Versioned Data
支持时间旅行功能的数据，可以查询历史版本。

### Row Merger
合并来自多个 Chunk 的行数据，处理版本冲突。

## 使用场景

1. **数据分析**：离线分析表数据和统计信息
2. **故障排查**：分析损坏或异常的数据块
3. **数据迁移**：辅助数据迁移和格式转换
4. **性能测试**：测试数据读取和解析性能

## 最佳实践

1. **内存管理**：处理大型数据时注意内存使用
2. **批量处理**：对多个 Chunk 进行批量处理
3. **输出控制**：使用行数限制避免输出过多
4. **格式选择**：根据需要选择合适的输出格式

## 注意事项

- 确保数据块文件的完整性
- 处理大型数据时注意系统资源
- 某些操作可能需要较长时间完成
- 生产数据使用前进行充分测试