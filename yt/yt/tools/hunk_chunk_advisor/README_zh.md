# hunk_chunk_advisor - Hunk Chunk 优化顾问工具

## 项目描述

`hunk_chunk_advisor` 是 YTsaurus 系统的数据存储优化分析工具，专门用于分析和优化 Hunk Chunk 的使用效率。该工具通过分析表的列数据分布和 Hunk Chunk 的饱和度，为数据压缩和存储优化提供决策支持。

## 功能特性

### 主要功能
- **列数据重量分析**：计算各列的数据权重分布和内联存储比例
- **饱和度分析**：评估 Hunk Chunk 的使用效率和饱和度
- **可视化报告**：生成详细的分析图表和统计报告
- **批量处理**：支持大规模数据表的高效分析
- **采样分析**：支持采样模式以控制分析成本

### 分析模式
1. **compute_weight** - 计算列数据重量分布和内联比例
2. **compute_saturation** - 分析 Hunk Chunk 的饱和度和使用效率

## 文件结构

```
hunk_chunk_advisor/
├── __main__.py              # 主程序入口
├── __init__.py             # 模块初始化
├── ya.make                 # 构建配置
└── templates/              # 模板文件目录
    └── ...                 # 相关模板文件
```

## 使用方法

### 环境要求
```bash
# 安装依赖
pip install matplotlib yt.wrapper
```

### 基本使用

#### 1. 计算列数据重量分布
```bash
python -m yt.yt.tools.hunk_chunk_advisor \
    --proxy <yt-proxy> \
    --table-path <table-path> \
    --computation-path <temp-path> \
    --result-file <output-file> \
    --sampling-rate 0.1 \
    compute_weight
```

#### 2. 计算 Hunk Chunk 饱和度
```bash
python -m yt.yt.tools.hunk_chunk_advisor \
    --proxy <yt-proxy> \
    --table-path <table-path> \
    --result-file <output-file> \
    --sampling-rate 1.0 \
    compute_saturation
```

### 命令行参数说明

#### 通用参数
- `--proxy` - YT 代理地址（必需）
- `--table-path` - 要分析的表路径（必需）
- `--sampling-rate` - 采样率（默认：1.0）
- `--result-file` - 结果输出文件路径（必需）

#### compute_weight 模式参数
- `--computation-path` - 中间计算结果存储路径（必需）

#### compute_saturation 模式参数
- 无额外参数

## 实现原理

### 数据重量分析（compute_weight）

1. **表采样**：使用指定的采样率创建表的采样副本
2. **MapReduce 分析**：
   - **Mapper 阶段**：分析每行数据的列值长度分布
   - **Reducer 阶段**：聚合各列的统计信息
3. **桶统计**：将数据按长度分为 24 个桶（2^0 到 2^23）
4. **可视化**：生成列重量分布和内联比例图表

### 饱和度分析（compute_saturation）

1. **Chunk 信息收集**：批量读取表的 Chunk 元数据
2. **分类统计**：区分 Table Chunk 和 Hunk Chunk
3. **引用分析**：计算 Hunk Chunk 的引用次数和引用长度
4. **饱和度计算**：评估每个 Hunk Chunk 的使用效率
5. **分布分析**：生成六个维度的统计图表

## 分析结果

### compute_weight 输出

#### 控制台输出
```
column_a:    15.23G (45.67%)
column_b:    8.91G (26.71%)
column_c:    4.56G (13.68%)
...
Total static:    33.45G (100.00%)
Total dynamic:    45.67G (136.52%)
```

#### 图表说明
- **列数据重量分布图**：显示各列的数据权重
- **内联重量比例图**：显示不同内联阈值下的存储效率

### compute_saturation 输出

#### 控制台输出
```
Table chunk count: 1250,    data weight: 850.23G (85.67%)
Hunk chunk count: 320,     data weight: 143.15G (14.33%), total ref length: 280.45G (28.24%)
```

#### 图表说明
1. **Chunk 按引用 Hunk 数量分布**
2. **Chunk 按引用 Hunk 总数分布**
3. **Chunk 按总引用长度分布**
4. **Hunk Chunk 按引用 Chunk 数量分布**
5. **Hunk Chunk 按总引用长度分布**
6. **Hunk Chunk 按饱和度分布**

## 核心算法

### 数据分桶算法
```python
BUCKETS = [2 ** i for i in range(24)]  # 2^0 到 2^23
BUCKET_DESCRIPTORS = ["<{}".format(bucket) for bucket in BUCKETS + ["inf"]]

def compute_bucket_index(self, length):
    index = 0
    while index < len(BUCKETS):
        if BUCKETS[index] > length:
            break
        index += 1
    return index
```

### 饱和度计算
```python
def compute_saturation(weight, ref_length):
    return 100 * float(ref_length) / weight
```

## 性能优化

### 批量处理
- 使用批量客户端减少 RPC 调用次数
- 最大批量大小：100 个 Chunk
- 分批处理大规模数据

### 采样策略
- 支持 0.0 到 1.0 的采样率
- 采样数据可用于估计全表特征
- 减少分析时间和资源消耗

## 使用示例

### 完整分析流程
```bash
# 1. 分析大型日志表
python -m yt.yt.tools.hunk_chunk_advisor \
    --proxy yt-cluster.mycompany.com \
    --table-path //sys/tables/user_logs \
    --computation-path //tmp/hunk_analysis \
    --result-file /tmp/logs_weight_analysis.png \
    --sampling-rate 0.01 \
    compute_weight

# 2. 分析 Hunk Chunk 饱和度
python -m yt.yt.tools.hunk_chunk_advisor \
    --proxy yt-cluster.mycompany.com \
    --table-path //sys/tables/user_logs \
    --result-file /tmp/logs_saturation_analysis.png \
    --sampling-rate 1.0 \
    compute_saturation
```

### 生产环境分析
```bash
# 分析关键业务表
python -m yt.yt.tools.hunk_chunk_advisor \
    --proxy yt-production.mycompany.com \
    --table-path //sys/tables/orders \
    --computation-path //tmp/analysis/$(date +%Y%m%d) \
    --result-file /tmp/analysis/orders_$(date +%Y%m%d).png \
    --sampling-rate 0.1 \
    compute_weight
```

## 依赖项

### Python 库
- `yt.wrapper` - YTsaurus Python 客户端
- `yt.yson` - YSON 序列化支持
- `matplotlib` - 数据可视化
- `argparse` - 命令行参数解析
- `collections` - 数据结构支持

### 系统要求
- Python 3.6+
- 足够的存储空间用于中间结果
- 网络连接到 YT 代理

## 最佳实践

### 分析策略
1. **采样率选择**：
   - 探索性分析：0.01-0.1
   - 精确分析：0.5-1.0
   - 超大规模表：0.001-0.01

2. **计算路径规划**：
   - 使用专用的临时目录
   - 考虑磁盘空间需求
   - 及时清理中间结果

3. **结果解读**：
   - 关注饱和度 > 50% 的 Hunk Chunk
   - 识别内联比例过低的列
   - 分析数据分布特征

### 优化建议
1. **内联阈值优化**：根据分析结果调整列的内联阈值
2. **数据重组**：对低饱和度的 Hunk Chunk 进行重组
3. **压缩策略**：基于数据特征选择合适的压缩算法
4. **分区策略**：优化表的分区以改善数据局部性

## 故障排除

### 常见问题
1. **内存不足**：降低采样率或增加内存配额
2. **网络超时**：增加重试次数或使用更稳定的网络
3. **权限问题**：确认对表和目标路径有读写权限
4. **磁盘空间**：确保有足够空间存储中间结果

### 调试技巧
```bash
# 使用小采样率测试
--sampling-rate 0.001

# 检查权限
yt ls //tmp/hunk_analysis

# 监控进度
yt list //tmp/hunk_analysis
```

## 相关概念

### Hunk Chunk
YTsaurus 中用于存储大值（如 BLOB、长字符串）的特殊存储格式，支持去重和压缩。

### 内联存储（Inline Storage）
将小值直接存储在主 Chunk 中，避免额外的存储开销。

### 饱和度（Saturation）
Hunk Chunk 的使用效率，计算公式为：`引用长度 / 存储空间 * 100%`

### 数据重量（Data Weight）
数据在内存中的估算大小，用于计算资源消耗和查询成本。

## 注意事项

⚠️ **重要提醒**：
- 大规模分析会消耗大量计算资源
- 确保有足够的临时存储空间
- 生产环境分析建议在低峰期进行
- 分析结果仅供参考，实际优化需结合业务需求