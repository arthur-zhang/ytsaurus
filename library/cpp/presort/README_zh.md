# Presort 预排序算法库

## 项目概述

Presort 是一个专门用于预排序操作的算法库，提供了高效的数据预处理和排序功能。该库主要用于大数据处理场景，通过预排序优化后续的数据操作性能。

### 核心功能
- **预排序算法**：高效的预排序处理
- **外部排序**：大文件的外部排序支持
- **内存优化**：内存使用优化的排序策略
- **并行排序**：多线程并行排序支持
- **增量排序**：增量数据的排序更新

## 文件说明

### 核心文件
- **presort.h/presort.cpp** - 预排序算法主要实现

## 使用示例

### 基础预排序
```cpp
#include <library/cpp/presort/presort.h>

void BasicPresortExample() {
    TVector<int> data = {5, 2, 8, 1, 9, 3, 7, 4, 6};

    // 执行预排序
    TPresorter<int> presorter;
    presorter.Presort(data);

    // 预排序后的数据
    for (int value : data) {
        printf("%d ", value);
    }
    printf("\n");
}
```

### 外部排序
```cpp
void ExternalSortExample() {
    TString inputFile = "large_data.txt";
    TString outputFile = "sorted_data.txt";

    // 创建外部排序器
    TExternalPresorter sorter;

    // 设置排序参数
    sorter.SetMemoryLimit(1024 * 1024 * 1024);  // 1GB 内存限制
    sorter.SetTempDirectory("/tmp");             // 临时目录

    // 执行外部排序
    TError error = sorter.Sort(inputFile, outputFile);
    if (error) {
        printf("External sort failed: %s\n", error.GetMessage().c_str());
        return;
    }

    printf("External sort completed successfully\n");
}
```

### 并行预排序
```cpp
void ParallelPresortExample() {
    TVector<TVector<int>> batches = {
        {5, 2, 8},
        {1, 9, 3},
        {7, 4, 6}
    };

    // 创建并行预排序器
    TParallelPresorter<int> presorter;
    presorter.SetThreadCount(4);  // 使用 4 个线程

    // 并行预排序
    TVector<TVector<int>> sortedBatches;
    presorter.PresortParallel(batches, &sortedBatches);

    // 合并排序结果
    TVector<int> finalResult;
    MergeSortedBatches(sortedBatches, &finalResult);

    for (int value : finalResult) {
        printf("%d ", value);
    }
    printf("\n");
}
```

## 实现原理

### 预排序策略
- **局部排序**：对数据块进行局部排序
- **元数据生成**：生成排序元数据信息
- **边界优化**：优化数据块的边界处理
- **合并策略**：高效的排序结果合并

### 内存管理
- **分块处理**：将大数据分割为可管理的块
- **内存池**：使用内存池减少分配开销
- **LRU 缓存**：使用 LRU 缓存策略
- **垃圾回收**：自动的内存垃圾回收

### 并行化
- **任务分解**：将排序任务分解为子任务
- **工作窃取**：使用工作窃取算法平衡负载
- **锁优化**：减少锁竞争提高并行效率
- **NUMA 优化**：针对 NUMA 架构的优化

## 应用场景

### 大数据处理
- **ETL 流程**：数据提取、转换、加载的预处理
- **数据仓库**：数据仓库的加载前排序
- **日志分析**：日志数据的预排序分析
- **数据挖掘**：数据挖掘前的数据预处理

### 数据库系统
- **索引构建**：数据库索引的构建过程
- **查询优化**：查询结果的预排序优化
- **数据导入**：大批量数据的导入排序
- **表连接**：多表连接前的排序优化

### 搜索引擎
- **倒排索引**：搜索引擎倒排索引的构建
- **文档排序**：搜索结果的预排序
- **缓存优化**：搜索缓存的预排序组织
- **索引合并**：多个索引的合并排序

### 科学计算
- **数值模拟**：模拟数据的预排序处理
- **统计分析**：统计数据的预处理排序
- **图像处理**：图像像素的排序操作
- **信号处理**：信号数据的预排序

## 性能特性

### 时间复杂度
- **预排序**：O(n log k) - n 为数据量，k 为块数
- **合并排序**：O(n log k) - k 个有序块的合并
- **外部排序**：O(n log n) - 外部排序总复杂度
- **并行排序**：O((n log n)/p) - p 为并行度

### 空间复杂度
- **内存使用**：O(k) - k 个块的内存开销
- **临时空间**：O(n) - 外部排序的临时空间
- **缓存空间**：O(√n) - 优化的缓存空间使用
- **并行开销**：O(p) - 并行处理的开销

### 并行性能
- **线性扩展**：接近线性的并行扩展性
- **负载均衡**：良好的负载均衡特性
- **缓存友好**：缓存友好的访问模式
- **NUMA 感知**：针对 NUMA 架构的优化

## 配置选项

### 基础配置
```cpp
// 预排序器配置
TPresorter<int> presorter;
presorter.SetBlockSize(1024 * 1024);     // 块大小
presorter.SetMemoryLimit(512 * 1024 * 1024); // 内存限制
presorter.SetTempDirectory("/tmp");       // 临时目录
presorter.SetThreadCount(4);              // 线程数
```

### 外部排序配置
```cpp
// 外部排序器配置
TExternalPresorter sorter;
sorter.SetMergeFactor(4);                 // 合并因子
sorter.SetCompressionEnabled(true);       // 启用压缩
sorter.SetCompressionLevel(6);            // 压缩级别
sorter.SetBufferSize(64 * 1024);          // 缓冲区大小
```

### 并行配置
```cpp
// 并行预排序器配置
TParallelPresorter<int> parallelSorter;
parallelSorter.SetThreadCount(std::thread::hardware_concurrency());
parallelSorter.SetLoadBalanceStrategy(LoadBalance::WorkStealing);
parallelSorter.SetChunkSize(1024);        // 任务块大小
parallelSorter.SetPriority(SchedulingPriority::Normal);
```

## 最佳实践

### 性能优化
- **合理的块大小**：根据内存限制设置合适的块大小
- **并行度调整**：根据系统调整并行度参数
- **内存管理**：有效管理内存使用避免溢出
- **I/O 优化**：优化磁盘 I/O 操作

### 错误处理
- **异常安全**：保证异常情况下的数据一致性
- **恢复机制**：提供错误恢复和重试机制
- **资源清理**：正确清理临时文件和资源
- **日志记录**：记录关键操作和错误信息

### 调试支持
- **进度监控**：监控排序进度和性能指标
- **中间结果**：保留中间结果用于调试
- **数据验证**：验证排序结果的正确性
- **性能分析**：分析性能瓶颈和优化点