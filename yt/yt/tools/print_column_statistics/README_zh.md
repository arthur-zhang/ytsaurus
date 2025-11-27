# print_column_statistics - 列统计信息打印工具

## 项目描述

`print_column_statistics` 是 YTsaurus 系统的数据分析工具，用于读取和显示数据块的列统计信息。该工具能够解析数据块的元数据，提取各列的统计信息，帮助分析数据的分布特征和存储特性。

## 功能特性

- **统计信息提取**：从数据块元数据中提取列统计信息
- **多格式支持**：支持多种数据块格式
- **详细信息显示**：显示列的类型、压缩比、数据分布等
- **元数据分析**：分析数据块的元数据结构
- **错误处理**：提供完善的错误处理和异常恢复

## 文件说明

- `main.cpp` - 主程序实现，包含统计信息读取和显示逻辑
- `CMakeLists.txt` - CMake 构建配置文件（支持多平台）
- `ya.make` - YaTool 构建系统配置文件

## 使用方法

### 编译
```bash
# 使用 CMake 构建
cmake --build . --target print_column_statistics

# 或使用 ya 工具构建
ya make print_column_statistics
```

### 运行
```bash
./print_column_statistics <chunk_meta_file>
```

**参数说明：**
- `chunk_meta_file` - 数据块元数据文件路径

## 实现原理

该工具基于 YTsaurus 的数据块读取架构：

1. **文件读取**：使用数据块文件读取器读取元数据文件
2. **元数据解析**：解析数据块的元数据结构
3. **统计提取**：提取各列的统计信息
4. **格式化输出**：将统计信息以可读格式输出

### 核心组件
```cpp
// 创建读取器
auto reader = New<TChunkFileReader>(
    CreateIOEngine(EIOEngineType::ThreadPool, NYTree::INodePtr()),
    NullChunkId,
    fileName);

// 获取元数据
auto meta = reader->GetMeta({}).Get().ValueOrThrow();

// 解析扩展信息
auto miscExt = GetProtoExtension<NTableClient::NProto::TMiscExt>(meta->extensions());
```

## 使用示例

### 基本使用
```bash
# 分析数据块统计信息
./print_column_statistics /var/lib/yt/chunks/1-0-0.meta

# 输出示例：
# Column: user_id
#   Type: string
#   Max Value: user_1000000
#   Min Value: user_1
#   Data Weight: 125829120
#   Chunk Count: 1024
#
# Column: timestamp
#   Type: int64
#   Max Value: 1640995200000000
#   Min Value: 1609459200000000
#   Data Weight: 52428800
#   Chunk Count: 512
```

### 批量分析
```bash
# 分析目录下所有数据块
for meta_file in /var/lib/yt/chunks/*.meta; do
    echo "=== $meta_file ==="
    ./print_column_statistics "$meta_file"
    echo
done
```

### 输出重定向
```bash
# 保存分析结果
./print_column_statistics chunk.meta > column_stats.txt

# 生成 CSV 报告
./print_column_statistics chunk.meta | grep -E "Column:|Data Weight:" > stats.csv
```

## 依赖项

### 核心依赖
- `yt/yt/server/lib/io/chunk_file_reader.h` - 数据块文件读取器
- `yt/yt/server/lib/io/io_engine.h` - IO 引擎
- `yt/yt/ytlib/chunk_client/` - 数据块客户端库
- `yt/yt/ytlib/table_client/` - 表客户端库
- `yt/yt_proto/yt/client/chunk_client/proto/chunk_meta.pb.h` - 元数据协议定义

### 系统依赖
- C++20 编译器
- CMake 3.22+
- YTsaurus 核心库
- Protobuf 库

## 相关概念

### Chunk Meta
数据块的元数据，包含数据的结构信息、统计信息、压缩信息等。

### Column Statistics
列的统计信息，包括：
- **数据类型**：列的数据类型
- **值范围**：最大值和最小值
- **数据权重**：列的数据大小
- **块数量**：列包含的数据块数量
- **压缩信息**：压缩比和压缩算法

### Data Weight
数据在内存中的估算大小，用于计算资源消耗和查询成本。

### Chunk
YTsaurus 的基本数据存储单元，包含实际数据和元数据。

## 使用场景

### 数据分析
1. **存储优化**：分析数据分布以优化存储策略
2. **查询规划**：根据统计信息优化查询计划
3. **压缩评估**：评估压缩效果和选择压缩算法
4. **分区设计**：设计合适的数据分区策略

### 性能调优
1. **热点分析**：识别数据热点和访问模式
2. **容量规划**：规划存储容量和资源需求
3. **索引设计**：设计有效的索引策略
4. **缓存优化**：优化缓存策略和预取机制

### 数据质量
1. **数据验证**：验证数据的完整性和一致性
2. **异常检测**：检测异常数据和分布变化
3. **数据治理**：支持数据治理和质量监控
4. **合规检查**：检查数据合规性要求

## 最佳实践

### 分析策略
1. **定期分析**：定期分析数据统计信息
2. **增量更新**：关注统计信息的增量变化
3. **对比分析**：对比不同时间段的数据分布
4. **趋势分析**：分析数据分布的变化趋势

### 输出处理
```bash
# 提取特定列信息
./print_column_statistics chunk.meta | grep -A 10 "Column: user_id"

# 生成统计摘要
./print_column_statistics chunk.meta | grep "Data Weight:" | awk '{sum+=$3} END {print "Total:", sum}'

# 格式化输出
./print_column_statistics chunk.meta | column -t
```

### 性能优化
1. **批量处理**：批量分析多个数据块
2. **并行处理**：并行处理不同的分析任务
3. **内存管理**：处理大型数据块时注意内存使用
4. **缓存利用**：利用系统缓存提高读取性能

## 扩展功能

### 自定义分析
可以根据需要扩展分析功能：

```cpp
// 自定义统计信息
void AnalyzeColumnCustom(const NTableClient::NProto::TColumnMeta& column) {
    // 自定义分析逻辑
    // 可以添加特定的统计指标
}
```

### 报告生成
支持生成多种格式的分析报告：
- HTML 报告
- PDF 报告
- Excel 报告
- JSON 数据导出

## 故障排除

### 常见问题
1. **文件不存在**：指定的元数据文件不存在
2. **格式错误**：元数据文件格式不正确或损坏
3. **权限不足**：没有读取文件的权限
4. **内存不足**：处理大型文件时内存不足

### 调试技巧
```bash
# 检查文件存在性
ls -l chunk.meta

# 验证文件格式
file chunk.meta

# 检查权限
stat chunk.meta

# 监控内存使用
./print_column_statistics large_chunk.meta &
ps aux | grep print_column
```

### 错误恢复
1. **文件修复**：尝试修复损坏的元数据文件
2. **部分读取**：从部分完好的数据中提取信息
3. **备份恢复**：从备份中恢复元数据
4. **重新生成**：重新生成统计信息

## 注意事项

⚠️ **重要提醒**：
- 确保元数据文件的完整性
- 处理大型文件时注意系统资源使用
- 保护敏感数据，避免统计信息泄露
- 定期备份重要的分析结果
- 在生产环境使用时避免影响正常业务

## 输出格式说明

### 标准输出格式
```
Column: <column_name>
  Type: <data_type>
  Max Value: <max_value>
  Min Value: <min_value>
  Data Weight: <data_weight>
  Chunk Count: <chunk_count>
  Compression Ratio: <compression_ratio>
  Null Count: <null_count>
  Unique Count: <unique_count>
```

### 统计指标说明
- **Type**：列的数据类型（string、int64、double 等）
- **Max/Min Value**：列的最大值和最小值
- **Data Weight**：列的数据大小（字节）
- **Chunk Count**：列包含的数据块数量
- **Compression Ratio**：压缩比（原始大小/压缩后大小）
- **Null Count**：空值数量
- **Unique Count**：唯一值数量（如果可用）