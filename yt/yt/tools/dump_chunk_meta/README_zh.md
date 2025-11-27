# dump_chunk_meta

## 项目描述

`dump_chunk_meta` 是 YTsaurus 系统中的一个调试工具，用于分析和显示数据块（chunk）的元数据信息。该工具可以读取并解析 YTsaurus 存储系统的 chunk meta 文件，以可读格式输出其中的详细信息。

## 功能特性

- 读取 YTsaurus chunk meta 文件
- 显示 chunk 的基本信息（ID、类型、格式）
- 解析并输出所有 protobuf 扩展信息
- 支持未知扩展类型的识别和警告
- 提供详细的调试信息输出

## 文件说明

- `main.cpp` - 主程序实现文件，包含参数解析和 chunk meta 读取逻辑
- `CMakeLists.txt` - CMake 构建配置文件
- `ya.make` - YaTool 构建系统配置文件

## 使用方法

### 编译
```bash
# 使用 CMake 构建
cmake --build . --target dump_chunk_meta

# 或使用 ya 工具构建
ya make dump_chunk_meta
```

### 运行
```bash
./dump_chunk_meta <chunk-meta-file-path>
```

## 实现原理

该工具基于 YTsaurus 的 IO 引擎和 chunk 客户端库实现：

1. **初始化读取器**：创建 `TChunkFileReader` 实例，使用线程池 IO 引擎
2. **获取基本信息**：读取 chunk ID 和元数据
3. **解析扩展**：遍历所有 protobuf 扩展，根据注册表识别扩展类型
4. **格式化输出**：将二进制元数据转换为人类可读的格式

## 命令行参数说明

- `chunk-meta-file` - （必需）chunk meta 文件的路径

### 示例
```bash
# 分析指定的 chunk meta 文件
./dump_chunk_meta /var/lib/yt/data/chunks/0/0/1.meta

# 输出示例
# ID: 1-0-0-00000000000000000001
# Type: Table
# Format: SchemalessHorizontal
#
# Extension NYT.NChunkClient.NProto.TChunkMetaExt
# data_size: 1048576
# chunk_row_count: 1000
# ...
```

## 依赖项

- `yt/yt/server/lib/io/chunk_file_reader.h` - Chunk 文件读取器
- `yt/yt/server/lib/io/io_engine.h` - IO 引擎接口
- `yt/yt/ytlib/chunk_client/` - Chunk 客户端库
- `yt/yt/library/program/program.h` - 程序框架
- Protocol Buffers - 序列化支持

## 相关概念

### Chunk（数据块）
YTsaurus 中的基本存储单元，包含实际的数据和元数据信息。

### Chunk Meta（数据块元数据）
存储 chunk 的描述信息，包括：
- Chunk 类型和格式
- 数据大小和行数统计
- 压缩和编码信息
- 分区信息
- 扩展属性

### Protobuf Extensions
YTsaurus 使用 protobuf 扩展机制来存储各种类型的元数据，支持灵活的扩展。

## 最佳实践

1. **调试用途**：主要用于问题诊断和开发调试，不建议在生产环境中频繁使用
2. **文件路径**：确保提供的 chunk meta 文件路径正确且可访问
3. **权限检查**：运行时需要对 chunk meta 文件的读取权限
4. **输出处理**：输出可能较长，建议重定向到文件进行进一步分析
5. **版本兼容性**：确保工具版本与 YTsaurus 集群版本兼容

## 常见问题

**Q: 工具显示 "Unknown protobuf extension" 警告**
A: 这表示遇到了未知类型的扩展，通常是由于版本不匹配导致的，可以忽略该警告。

**Q: 无法读取 chunk meta 文件**
A: 检查文件路径、文件存在性以及读取权限。

**Q: 输出信息不完整**
A: 确保使用与集群相同版本的工具，以支持所有扩展类型的解析。