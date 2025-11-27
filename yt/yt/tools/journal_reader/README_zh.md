# journal_reader - Journal 读取和调试工具

## 项目描述

`journal_reader` 是 YTsaurus 系统的 Journal 数据读取和调试工具，专门用于读取和分析 YTsaurus Journal 的日志数据和变更记录。该工具支持将 Journal 数据转换为可读格式，便于开发者进行故障排查和数据恢复。

## 功能特性

- **Journal 读取**：读取 YTsaurus Journal 的原始数据
- **格式转换**：将内部数据格式转换为人类可读的格式
- **Schema 支持**：支持自定义表结构定义
- **多种输出**：支持多种输出格式和分析模式
- **调试功能**：提供丰富的调试和分析功能

## 文件结构

```
journal_reader/
├── main.cpp                  # 主程序入口
├── journal_dumper.cpp        # Journal 数据转储器
├── journal_dumper.h          # Journal 转储器头文件
├── mutation_dumper.cpp       # Mutation 数据转储器
├── mutation_dumper.h         # Mutation 转储器头文件
├── private.h                 # 私有定义和常量
├── README.md                 # 英文文档
├── CMakeLists.txt           # CMake 构建配置
└── ya.make                  # YaTool 构建配置
```

## 使用方法

### 编译
```bash
# 使用 CMake 构建
cmake --build . --target journal_reader

# 或使用 ya 工具构建
ya make journal_reader
```

### 基本使用
```bash
./journal_reader \
    --schema <schema-file> \
    --tablet-id <tablet-id> \
    <journal-dump-file>
```

## 命令行参数说明

| 参数 | 类型 | 必需 | 说明 |
|------|------|------|------|
| `schema` | string | 是 | 表结构文件路径（YSON 格式） |
| `tablet-id` | string | 可选 | Tablet ID（用于过滤特定 Tablet 的数据） |
| `journal-dump-file` | string | 是 | Journal 转储文件路径 |

## 实现原理

### 核心组件

1. **Journal Dumper**：负责读取和解析 Journal 数据
2. **Mutation Dumper**：处理变更记录的数据转储
3. **Schema Loader**：加载和应用表结构定义
4. **Record Parser**：解析记录结构和内容

### 数据处理流程

1. **Schema 加载**：从 YSON 文件加载表结构定义
2. **Journal 读取**：读取指定的 Journal 转储文件
3. **Record 解析**：根据 Schema 解析每条记录
4. **格式转换**：将内部格式转换为可读格式
5. **过滤输出**：根据条件过滤和输出数据

### 数据结构
```cpp
// 读取记录示例
auto ReadRecords(const TString& filename) {
    auto str = TIFStream(filename).ReadAll();
    return ConvertTo<std::vector<IMapNodePtr>>(
        TYsonString(str, EYsonType::ListFragment));
}

// Schema 加载
TTableSchemaPtr LoadSchema(const TString& filename) {
    TIFStream stream(filename);
    return ConvertTo<TTableSchemaPtr>(TYsonString(stream.ReadAll()));
}
```

## 使用示例

### 基础 Journal 读取
```bash
# 读取完整的 Journal 数据
./journal_reader \
    --schema table_schema.yson \
    journal_dump.yson

# 读取特定 Tablet 的数据
./journal_reader \
    --schema table_schema.yson \
    --tablet-id "1-2-3-4" \
    journal_dump.yson
```

### Schema 文件示例
```yson
# table_schema.yson
[
    {name = "timestamp", type = "int64", sort_order = "ascending"},
    {name = "key", type = "string", sort_order = "ascending"},
    {name = "value", type = "string"},
    {name = "metadata", type = "any"}
]
```

### 调试和故障排查
```bash
# 分析特定时间段的 Journal 数据
./journal_reader \
    --schema debug_schema.yson \
    --tablet-id "7-8-9-10" \
    corrupted_journal.yson > journal_analysis.txt
```

## 依赖项

### 核心依赖
- `yt/yt/client/table_client/schema.h` - 表结构定义
- `yt/yt/core/misc/protobuf_helpers.h` - Protobuf 辅助工具
- `yt/yt/core/ytree/node.h` - YTree 节点操作
- `yt/yt/core/ytree/convert.h` - YSON 转换工具

### 系统依赖
- C++20 编译器
- CMake 3.22+
- YTsaurus 核心库
- Protobuf 库

## 相关概念

### Journal
YTsaurus 中的日志存储结构，用于存储 Tablet 的操作日志和变更记录。Journal 提供了数据的变更历史和恢复能力。

### Mutation
对 Tablet 数据的变更操作，包括插入、更新、删除等操作。Mutation 记录了数据变更的完整信息。

### Tablet
YTsaurus 动态表的水平分片单元，每个 Tablet 负责处理特定键范围的数据。

### Schema
表的结构定义，包括列名、数据类型、排序键等信息。

## 使用场景

### 故障排查
1. **数据损坏分析**：分析 Journal 数据定位数据损坏原因
2. **恢复验证**：验证数据恢复操作的准确性
3. **性能分析**：分析 Journal 读取和写入性能
4. **一致性检查**：检查数据的一致性状态

### 开发调试
1. **功能测试**：测试新功能的 Journal 处理逻辑
2. **数据迁移**：辅助数据迁移和升级操作
3. **格式研究**：研究 YTsaurus 内部数据格式
4. **基准测试**：进行性能基准测试

## 最佳实践

### 使用建议
1. **Schema 匹配**：确保 Schema 文件与 Journal 数据匹配
2. **资源控制**：处理大型 Journal 时注意内存使用
3. **输出重定向**：将结果重定向到文件便于分析
4. **增量处理**：对大型 Journal 进行分批处理

### 调试技巧
```bash
# 生成详细日志
./journal_reader --verbose --schema schema.yson journal.yson

# 过滤特定时间段的数据
./journal_reader --schema schema.yson journal.yson | grep "timestamp: 1[6-7]"

# 统计记录数量
./journal_reader --schema schema.yson journal.yson | wc -l
```

### 性能优化
1. **批量处理**：批量读取和处理记录以提高效率
2. **内存管理**：及时释放不需要的数据结构
3. **并行处理**：对多个 Journal 文件进行并行处理
4. **缓存利用**：充分利用系统缓存提高读取速度

## 故障排除

### 常见问题
1. **Schema 错误**：Schema 文件与 Journal 数据不匹配
2. **文件格式**：输入文件不是有效的 YSON 格式
3. **内存不足**：处理大型 Journal 时内存不足
4. **权限问题**：无法读取指定的 Journal 文件

### 错误处理
- 检查 Schema 文件的格式和内容
- 验证 Journal 文件的完整性
- 增加系统内存或使用流式处理
- 确认文件权限和访问路径

### 调试命令
```bash
# 验证 Schema 文件
yt get <schema-path> > schema.yson

# 检查 Journal 文件大小
ls -lh journal_dump.yson

# 查看部分内容
head -n 10 journal_dump.yson
```

## 注意事项

⚠️ **重要提醒**：
- Journal 文件可能包含敏感数据，注意数据安全
- 大型 Journal 文件处理可能需要大量内存
- 确保有足够的磁盘空间存储输出结果
- 生产环境使用时避免影响正常业务运行
- 建议在测试环境充分验证后再用于生产数据

## 扩展功能

### 自定义解析器
可以根据需要扩展解析器以支持特殊的数据格式或分析需求：

```cpp
// 示例：自定义记录处理器
void ProcessRecord(IMapNodePtr record, const TTableSchemaPtr& schema) {
    // 自定义处理逻辑
    // 可以添加特定的数据验证、转换或统计
}
```

### 输出格式
除了默认的文本输出外，还可以支持：
- JSON 格式输出
- CSV 格式输出
- HTML 报告生成
- 统计图表生成