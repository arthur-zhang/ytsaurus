# HyperLogLog 基数估计算法库

## 项目概述

HyperLogLog 是一种用于估算集合基数的概率算法，由 Philippe Flajolet、Éric Fusy、Olivier Gandouet 和 Frédéric Meunier 在 2007 年提出。该算法能够在使用极少内存的情况下，对大数据集的基数（唯一元素数量）进行相当准确的估算。此实现严格遵循 Google 的 HyperLogLog 算法论文。

## 算法特点

### 核心优势
- **内存高效**：仅需 1.5KB 内存即可估算十亿级别的基数
- **计算快速**：O(1) 时间复杂度的插入和合并操作
- **精度可控**：通过调整精度参数平衡内存使用和估算精度
- **可合并**：支持多个 HyperLogLog 结构的合并，适合分布式计算

### 精度范围
- **相对误差**：标准差约为 1.04/√m，其中 m 为寄存器数量
- **精度参数**：支持 4-18 位的精度设置
- **内存占用**：2^precision 字节，精度 14 时约 16KB

## 类设计

### 核心类层次结构

#### THyperLogLogBase
- **作用**：基类，提供核心算法实现
- **关键方法**：
  - `Update(ui64 hash)` - 插入元素哈希值
  - `Merge()` - 合并另一个 HyperLogLog
  - `Estimate()` - 估算基数
  - `Save()` - 序列化保存

#### THyperLogLogWithAlloc
- **作用**：模板类，支持自定义分配器
- **特性**：
  - 移动语义支持
  - 工厂模式创建
  - 流式序列化/反序列化

#### THyperLogLog
- **作用**：默认类型定义，使用标准分配器
- **类型别名**：`THyperLogLogWithAlloc<std::allocator<ui8>>`

## 文件说明

### 核心文件
- **`hyperloglog.h`** - 主要接口定义
  - 精度常量定义（PRECISION_MIN/MAX）
  - 类声明和模板特化
  - 类型别名定义

- **`hyperloglog.cpp`** - 算法实现
  - 核心算法逻辑
  - 偏差校正表
  - 经验系数计算
  - 线性计数实现

- **`hyperloglog_corrections.inc`** - 校正数据
  - 预计算的偏差校正表
  - 不同精度下的阈值数据
  - 提升小基数估算精度

### 配置文件
- **`ya.make`** - 构建配置
- **`CMakeLists.txt`** - CMake 构建配置
- **`hyperloglog_ut.cpp`** - 单元测试

## 算法原理

### 基础思想
1. **哈希映射**：将输入元素映射为均匀分布的哈希值
2. **前导零计数**：统计哈希值二进制表示的前导零个数
3. **寄存器更新**：将哈希值分配到不同寄存器，保存最大前导零数
4. **调和平均**：使用调和平均数估算基数

### 算法步骤

#### 插入元素
```cpp
// 伪代码展示核心逻辑
void Update(ui64 hash) {
    // 1. 将哈希值分为两部分
    unsigned subHashBits = 64 - Precision;
    ui64 subHash = hash & ((1ULL << subHashBits) - 1);

    // 2. 计算前导零数量
    ui8 leadingZeros = CountLeadingZeros(subHash) + 1;

    // 3. 确定寄存器位置
    size_t regIndex = hash >> subHashBits;

    // 4. 更新寄存器（取最大值）
    Registers[regIndex] = max(Registers[regIndex], leadingZeros);
}
```

#### 基数估算
```cpp
ui64 Estimate() {
    // 1. 计算原始估计
    double rawEstimate = EmpiricAlpha(m) * m * m / sum(2^(-register[i]));

    // 2. 小范围偏差校正
    if (rawEstimate <= 5 * m) {
        rawEstimate -= EstimateBias(rawEstimate, precision);
    }

    // 3. 稀疏集合线性计数
    size_t zeroCount = countZeroRegisters();
    if (zeroCount > 0) {
        double linearEstimate = m * log(m / zeroCount);
        return (linearEstimate <= threshold) ? linearEstimate : rawEstimate;
    }

    return rawEstimate;
}
```

### 优化技术

#### 偏差校正
- **经验校正**：针对不同精度预计算偏差表
- **阈值切换**：小基数使用线性计数，大基数使用标准估计
- **插值优化**：在校正点间进行线性插值

#### 内存优化
- **寄存器压缩**：每个寄存器仅用 6 位存储
- **对齐优化**：内存布局优化缓存性能
- **分配器支持**：支持自定义内存分配策略

## 使用示例

### 基本使用
```cpp
#include <library/cpp/hyperloglog/hyperloglog.h>

// 创建 HyperLogLog 实例（精度 14）
auto hll = THyperLogLog::Create(14);

// 插入元素（需要先计算哈希值）
for (const auto& item : data) {
    ui64 hash = ComputeHash(item);
    hll.Update(hash);
}

// 估算基数
ui64 estimatedCount = hll.Estimate();
Cout << "Estimated unique items: " << estimatedCount << Endl;
```

### 分布式合并
```cpp
// 多个节点统计
std::vector<THyperLogLog> nodeHLLs;
for (int i = 0; i < nodeCount; ++i) {
    nodeHLLs.push_back(THyperLogLog::Create(14));
}

// 各节点插入数据
// nodeHLLs[i].Update(hash);

// 合并到全局统计
THyperLogLog globalHLL = THyperLogLog::Create(14);
for (auto& nodeHLL : nodeHLLs) {
    globalHLL.Merge(nodeHLL);
}

ui64 totalCount = globalHLL.Estimate();
```

### 序列化
```cpp
// 保存到流
TStringOutput out;
hll.Save(out);

// 从流加载
TStringInput in(out.Str());
auto loadedHLL = THyperLogLog::Load(in);
```

### 自定义分配器
```cpp
// 使用内存池分配器
using MyAllocator = TMemoryPoolAllocator<ui8>;
using MyHLL = THyperLogLogWithAlloc<MyAllocator>;

auto hll = MyHLL::Create(14);
```

## 性能特征

### 时间复杂度
- **插入操作**：O(1) - 常数时间
- **合并操作**：O(m) - m 为寄存器数量
- **估算操作**：O(m) - 需要遍历所有寄存器
- **序列化**：O(m) - 线性时间

### 空间复杂度
- **内存占用**：2^precision 字节
- **典型配置**：
  - Precision 12：4KB，相对误差 ~3%
  - Precision 14：16KB，相对误差 ~2.5%
  - Precision 16：64KB，相对误差 ~2%

### 精度特征
- **标准误差**：1.04/√m
- **实际精度**：在正常情况下优于理论值
- **边界情况**：小基数和极大基数有专门优化

## 应用场景

### 大数据分析
- **用户统计**：估算独立用户数
- **页面浏览**：唯一页面访问量统计
- **搜索分析**：独立搜索词数量
- **日志分析**：唯一日志条目统计

### 实时监控
- **流量分析**：独立 IP 访问统计
- **事件追踪**：独立事件类型统计
- **性能监控**：独立错误类型统计
- **资源使用**：独立资源访问统计

### 数据库系统
- **查询优化**：结果集基数估算
- **索引统计**：索引选择性估计
- **分区规划**：数据分布分析
- **缓存策略**：缓存命中率预测

### 网络系统
- **路由分析**：独立路由路径统计
- **负载均衡**：连接分布分析
- **安全审计**：独立攻击源统计
- **QoS 监控**：服务质量指标统计

## 算法对比

### 与其他基数估计算法比较

| 算法 | 内存使用 | 精度 | 合并支持 | 实现复杂度 |
|------|----------|------|----------|------------|
| HyperLogLog | 极低 | 高 | 支持 | 中等 |
| Linear Counting | 高 | 极高 | 不支持 | 简单 |
| LogLog | 极低 | 中等 | 支持 | 简单 |
| Adaptive Counting | 中等 | 高 | 有限支持 | 复杂 |

### HyperLogLog 优势
1. **内存效率极高**：相比精确计数节省 99%+ 内存
2. **合并友好**：天然支持分布式合并
3. **实现稳定**：算法成熟，实现可靠
4. **参数灵活**：可根据需求调整精度

## 最佳实践

### 精度选择
```cpp
// 根据数据规模选择精度
unsigned SelectPrecision(ui64 expectedCardinality) {
    if (expectedCardinality < 1000) {
        return 10;  // 1KB，误差 ~3.3%
    } else if (expectedCardinality < 1e9) {
        return 14;  // 16KB，误差 ~2.5%
    } else {
        return 16;  // 64KB，误差 ~2%
    }
}
```

### 哈希函数选择
- **要求**：高质量、均匀分布的 64 位哈希
- **推荐**：CityHash、MurmurHash3、xxHash
- **避免**：简单哈希函数、碰撞率高的算法

### 性能优化
- **批量插入**：减少函数调用开销
- **内存对齐**：确保寄存器数组对齐
- **预分配**：避免运行时内存分配
- **SIMD 优化**：利用向量指令加速合并

### 部署建议
- **精度设置**：根据业务需求选择合适精度
- **监控指标**：定期监控估算精度
- **容量规划**：预留内存增长空间
- **备份策略**：重要数据的定期备份

## 限制和注意事项

### 算法限制
1. **概率性质**：结果为估算值，存在误差
2. **最小基数**：对小集合精度较低
3. **哈希依赖**：哈希函数质量影响精度
4. **精度上限**：受精度参数限制

### 使用注意事项
- **哈希碰撞**：确保使用高质量的哈希函数
- **精度权衡**：平衡内存使用和估算精度
- **合并约束**：只能合并相同精度的实例
- **序列化兼容**：注意版本兼容性问题