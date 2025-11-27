# Dump Changelog

## 项目描述

Dump Changelog 是一个专业的 YTsaurus 变更日志分析工具。该工具能够解析以 YSON 格式存储的变更日志文件，并以人类可读的方式展示每个变更记录的详细信息。它主要用于调试、审计和分析分布式系统中的变更历史。

## 功能特性

- **详细解析**：解析变更日志中的每条记录
- **多格式支持**：自动识别并解析多种 protobuf 消息类型
- **层次化显示**：以清晰的层次结构展示变更内容
- **Hive 特殊处理**：对 Hive 相关消息进行特殊解析和格式化
- **完整元数据**：显示所有变更相关的元数据信息

## 文件说明

- `main.cpp` - 主程序源代码，实现 YSON 解析和格式化输出
- `ya.make` - 构建配置文件
- `CMakeLists.*.txt` - CMake 构建配置文件

## 使用方法

### 编译

```bash
# 使用 ya 工具构建
ya make -t dump_changelog

# 或使用 CMake 构建
cmake --build . --target dump_changelog
```

### 命令行参数

- `--input` - 输入文件路径（YSON 格式的变更日志文件，必需参数）

### 使用示例

```bash
# 解析变更日志文件
./dump_changelog --input /path/to/changelog.yson

# 输出到文件
./dump_changelog --input changelog.yson > changelog_dump.txt

# 分页查看长日志
./dump_changelog --input changelog.yson | less
```

## 输出格式

### 基本信息

对于每条变更记录，工具会显示：

```
Record <索引>
  MutationType:   <变更类型>
  Timestamp:      <时间戳>
  RandomSeed:     <随机种子>
  PrevRandomSeed: <前一个随机种子>
  SegmentId:      <段ID>
  RecordId:       <记录ID>
  MutationId:     <变更ID>
  Reign:          <统治期>
  SequenceNumber: <序列号>
  Term:           <任期>
```

### 变更内容

根据变更类型的不同，会显示具体的变更内容：

- **Hive 消息**：详细列出所有消息类型和数据
- **Protobuf 消息**：格式化显示 protobuf 消息内容
- **未知类型**：标记为 `<Unknown protobuf type>`

### Hive 消息特殊处理

对于 Hive 相关的变更（如 `TReqPostMessages`、`TReqSendMessages`），会额外显示：

```
  Messages:
    Type: <消息类型>
    <消息内容>
    --------------------
```

## 输入文件格式

工具期望输入文件为 YSON ListFragment 格式，其中每个元素是一个包含 `payload` 键的映射：

```yson
{
  payload="<序列化的变更数据>"
}
{
  payload="<序列化的变更数据>"
}
...
```

## 实现原理

### 核心处理流程

1. **YSON 解析**：使用 `TYsonPullParser` 解析输入文件
2. **数据提取**：从每个记录中提取 `payload` 字段
3. **反序列化**：将 payload 反序列化为 `TMutationHeader` 和 `TMutationData`
4. **格式化输出**：以人类可读的格式显示所有信息

### 关键技术

- **Protobuf 反射**：动态查找和解析 protobuf 消息类型
- **类型识别**：自动识别不同类型的消息
- **递归解析**：递归解析嵌套的消息结构

### 特殊处理

- **Hive 消息**：识别并特殊格式化 Hive 集群消息
- **消息列表**：批量处理消息列表中的每个消息
- **错误处理**：优雅处理未知类型的消息

## 使用场景

### 1. 调试分布式事务

```bash
# 查看特定时间段的变更
./dump_changelog --input changelog.yson | grep -A 20 "Timestamp: 1640995200"
```

### 2. 审计变更历史

```bash
# 查找特定类型的变更
./dump_changelog --input changelog.yson | grep -B 5 -A 15 "MutationType: UpdateTable"
```

### 3. 性能分析

```bash
# 统计变更数量
./dump_changelog --input changelog.yson | grep -c "^Record"
```

### 4. 数据恢复

```bash
# 查找特定序列号的变更
./dump_changelog --input changelog.yson | grep -A 50 "SequenceNumber: 12345"
```

## 高级用法

### 过滤和搜索

```bash
# 只查看 Hive 消息
./dump_changelog --input changelog.yson | grep -A 100 "Type: TReqPostMessages"

# 查找特定 MutationId
./dump_changelog --input changelog.yson | grep -B 5 "MutationId: 67890-12345"
```

### 与其他工具组合使用

```bash
# 统计变更类型分布
./dump_changelog --input changelog.yson | grep "MutationType:" | sort | uniq -c

# 提取所有时间戳
./dump_changelog --input changelog.yson | grep "Timestamp:" | awk '{print $2}'
```

## 故障排除

### 常见问题

1. **输入文件格式错误**
   ```
   Unexpected value type: ...
   ```
   确保输入文件是有效的 YSON ListFragment 格式

2. **无法解析 protobuf 类型**
   ```
   <Unknown protobuf type>
   ```
   这通常表示消息类型不在当前编译的 protobuf 描述池中

3. **内存不足**
   对于大型日志文件，考虑分段处理

### 调试技巧

```bash
# 检查 YSON 格式
cat changelog.yson | yson-cat | head -20

# 查看文件大小
ls -lh changelog.yson

# 分段处理大文件
split -l 1000 changelog.yson part_
for part in part_*; do ./dump_changelog --input $part > ${part}_dump.txt; done
```

## 性能考虑

- **内存使用**：工具会一次性加载整个文件到内存
- **处理速度**：主要瓶颈在于 protobuf 反序列化
- **输出大小**：输出通常比输入大很多

## 依赖项

- **yt/yt/server/lib/hydra** - Hydra 序列化库
- **yt/yt/ytlib/hive** - Hive protobuf 定义
- **yt/yt/ytlib/hydra** - Hydra protobuf 定义
- **yt/yt/library/program** - 程序框架库
- **yt/yt/core/yson** - YSON 解析库
- **google/protobuf** - Protobuf 库

## 相关概念

- **Changelog** - 记录所有变更的日志
- **Mutation** - 对系统状态的变更操作
- **YSON** - YTsaurus 的数据序列化格式
- **Protobuf** - Protocol Buffers 数据格式
- **Hive** - YTsaurus 的元数据管理组件

## 最佳实践

1. **定期备份**：在分析前备份原始日志文件
2. **分段处理**：对于大文件使用分割工具
3. **输出管理**：将输出重定向到文件以便后续分析
4. **版本兼容**：确保使用与日志生成时兼容的工具版本

## 扩展功能

可以通过修改源代码来添加新功能：

- 添加新的消息类型解析器
- 实现 JSON 或 XML 输出格式
- 添加过滤和搜索功能
- 实现统计分析功能

## 示例输出

```
Record 0
  MutationType:   NYT.NHiveClient.NProto.TReqPostMessages
  Timestamp:      1640995200000000
  RandomSeed:     1234567890abcdef
  PrevRandomSeed: 0
  SegmentId:      1
  RecordId:       0
  MutationId:     00000000-0000-0000-0000-000000000000
  Reign:          1
  SequenceNumber: 1
  Term:           1
  Messages:
    Type: NYT.NHiveClient.NProto.TReqCreateTable
    table_path: "//tmp/my_table"
    schema: [{name=id;type=int64}]
    --------------------
  Messages:
    Type: NYT.NHiveClient.NProto.TReqWriteTable
    table_path: "//tmp/my_table"
    data: "sample data"
    --------------------

Record 1
  MutationType:   NYT.NTabletServer.NProto.TReqWriteRow
  Timestamp:      1640995201000000
  ...
```