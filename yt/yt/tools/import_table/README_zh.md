# import_table - 数据导入工具

## 项目描述

`import_table` 是 YTsaurus 系统的数据导入工具，用于将外部数据源的数据导入到 YTsaurus 表中。该工具支持多种数据格式，提供了灵活的配置选项，适用于大规模数据迁移和数据集成场景。

## 功能特性

- **多格式支持**：支持 Parquet、JSON、YSON 等多种数据格式
- **集群连接**：支持连接到指定的 YTsaurus 集群
- **灵活配置**：提供丰富的配置选项进行精细化调优
- **网络项目**：支持指定网络项目进行网络隔离
- **批量处理**：适用于大规模数据导入任务

## 文件结构

```
import_table/
├── main.cpp              # 主程序入口
├── lib/                  # 核心库
│   ├── import_table.h    # 导入功能接口
│   └── config.h          # 配置管理
├── unittests/            # 单元测试
├── CMakeLists.txt        # CMake 构建配置
└── ya.make              # YaTool 构建配置
```

## 使用方法

### 编译
```bash
# 使用 CMake 构建
cmake --build . --target import_table

# 或使用 ya 工具构建
ya make import_table
```

### 基本使用
```bash
./import_table \
    --proxy <cluster-proxy> \
    --output <output-table-path> \
    --format <data-format> \
    [options] <input-files...>
```

## 命令行参数说明

| 参数 | 类型 | 必需 | 说明 |
|------|------|------|------|
| `--proxy` | string | 是 | YTsaurus 集群代理地址 |
| `--output` | string | 是 | 输出表路径 |
| `--format` | string | 否 | 输入文件格式（默认：parquet） |
| `--config` | string | 否 | YSON 配置文件路径 |
| `--network-project` | string | 否 | 网络项目名称 |

## 使用示例

### Parquet 文件导入
```bash
./import_table \
    --proxy yt-cluster.mycompany.com \
    --output //sys/tables/imported_data \
    --format parquet \
    data1.parquet data2.parquet
```

### JSON 文件导入
```bash
./import_table \
    --proxy yt-cluster.mycompany.com \
    --output //sys/tables/imported_json \
    --format json \
    --config import_config.yson \
    data.json
```

### 带配置的导入
```bash
./import_table \
    --proxy yt-cluster.mycompany.com \
    --output //sys/tables/special_import \
    --format parquet \
    --config fine_tuned_config.yson \
    --network-project production \
    large_dataset.parquet
```

## 实现原理

1. **参数解析**：解析命令行参数和配置文件
2. **集群连接**：建立与指定 YTsaurus 集群的连接
3. **格式识别**：根据指定格式解析输入数据
4. **数据转换**：将外部格式转换为 YTsaurus 内部格式
5. **批量写入**：将转换后的数据批量写入目标表

## 依赖项

### 核心依赖
- `yt/yt/tools/import_table/lib/` - 导入功能核心库
- `yt/cpp/mapreduce/interface/` - MapReduce 接口
- `yt/yt/library/program/helpers.h` - 程序辅助函数

### 系统依赖
- C++20 编译器
- CMake 3.22+
- YTsaurus 客户端库
- 相关数据格式库（Parquet、JSON 等）

## 最佳实践

### 性能优化
1. **批量大小**：调整批量写入大小以优化性能
2. **并行度**：根据集群资源配置合适的并行度
3. **压缩设置**：选择适当的压缩算法平衡性能和存储
4. **网络优化**：在网络延迟较高时增加重试机制

### 数据质量
1. **格式验证**：导入前验证数据格式的正确性
2. **Schema 匹配**：确保输入数据与目标表 Schema 兼容
3. **错误处理**：配置适当的错误处理策略
4. **数据校验**：导入完成后进行数据一致性检查

### 生产部署
1. **配置管理**：使用版本控制管理配置文件
2. **监控告警**：监控导入任务的进度和性能
3. **日志记录**：详细记录导入过程便于问题排查
4. **备份策略**：在重要数据导入前创建备份

## 故障排除

### 常见问题
1. **连接失败**：检查代理地址和网络连接
2. **格式错误**：验证输入文件格式是否正确
3. **权限问题**：确认对目标路径有写入权限
4. **资源不足**：检查集群资源使用情况

### 调试技巧
```bash
# 使用详细日志
./import_table --verbose ...

# 测试连接
./import_table --proxy <proxy> --test-connection

# 小批量测试
./import_table --batch-size 100 ...
```

## 相关概念

### 数据格式
- **Parquet**：列式存储格式，适合分析型工作负载
- **JSON**：结构化数据格式，易于人类阅读
- **YSON**：YTsaurus 原生序列化格式

### 导入策略
- **全量导入**：完整导入所有数据
- **增量导入**：仅导入新增或变更的数据
- **分区导入**：按分区并行导入

## 注意事项

⚠️ **重要提醒**：
- 大规模导入会影响集群性能，建议在低峰期进行
- 确保有足够的磁盘空间存储临时文件
- 导入过程中避免修改目标表结构
- 生产环境使用前进行充分的测试验证