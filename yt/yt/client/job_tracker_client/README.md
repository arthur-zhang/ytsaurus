# YTsaurus Job Tracker Client 模块

## 概述

Job Tracker Client 模块是 YTsaurus 作业跟踪系统的客户端接口，提供了作业和操作的核心数据类型定义。该模块定义了作业ID、操作ID、作业类型等基本概念，是整个作业管理系统的基础组件。

## 核心功能

### 1. 标识符定义
- **作业ID (TJobId)**: 全局唯一的作业标识符
- **操作ID (TOperationId)**: 全局唯一的操作标识符
- **作业跟踪ID (TJobTraceId)**: 作业追踪和调试标识符

### 2. 作业类型系统
- **调度器作业**: Map、Sort、Merge、Join 等计算作业
- **主节点作业**: 复制、删除等维护作业
- **扩展作业类型**: 支持自定义作业类型

### 3. 辅助功能
- **作业状态查询**: 作业状态信息获取
- **操作管理**: 操作生命周期管理
- **作业统计**: 作业执行统计和监控

## 主要类型定义

### 1. 标识符类型

```cpp
// 作业ID - 全局唯一标识符
YT_DEFINE_STRONG_TYPEDEF(TJobId, TGuid);
extern const TJobId NullJobId;

// 操作ID - 操作的全局唯一标识符
YT_DEFINE_STRONG_TYPEDEF(TOperationId, TGuid);
extern const TOperationId NullOperationId;

// 作业跟踪ID - 用于作业追踪和调试
YT_DEFINE_STRONG_TYPEDEF(TJobTraceId, TGuid);
extern const TJobTraceId NullJobTraceId;
```

### 2. 作业类型枚举 (EJobType)

```cpp
DEFINE_ENUM(EJobType,
    // 调度器作业 (1-98)
    ((Map)               (  1))     // Map 作业
    ((PartitionMap)      (  2))     // 分区 Map 作业
    ((SortedMerge)       (  3))     // 有序合并作业
    ((OrderedMerge)      (  4))     // 顺序合并作业
    ((UnorderedMerge)    (  5))     // 无序合并作业
    ((Partition)         (  6))     // 分区作业
    ((SimpleSort)        (  7))     // 简单排序作业
    ((FinalSort)         (  8))     // 最终排序作业
    ((SortedReduce)      (  9))     // 有序 Reduce 作业
    ((PartitionReduce)   ( 10))     // 分区 Reduce 作业
    ((ReduceCombiner)    ( 11))     // Reduce 组合器作业
    ((RemoteCopy)        ( 12))     // 远程复制作业
    ((IntermediateSort)  ( 13))     // 中间排序作业
    ((OrderedMap)        ( 14))     // 顺序 Map 作业
    ((JoinReduce)        ( 15))     // 连接 Reduce 作业
    ((Vanilla)           ( 16))     // 原生作业
    ((ShallowMerge)      ( 17))     // 浅合并作业
    ((SchedulerUnknown)  ( 98))     // 调度器未知作业

    // 主节点作业 (100-199)
    ((ReplicateChunk)    (100))     // 复制分片作业
    ((RemoveChunk)       (101))     // 删除分片作业
);
```

## 作业类型详解

### 1. 基础计算作业

#### Map (1) - Map 作业
- **用途**: 对数据进行一对一的映射转换
- **特点**: 简单、高效、易于并行化
- **应用场景**: 数据清洗、格式转换、特征提取

#### PartitionMap (2) - 分区 Map 作业
- **用途**: 在 Map 操作的同时进行数据分区
- **特点**: 减少数据 shuffle，提高整体效率
- **应用场景**: 预分区处理、局部聚合

#### SimpleSort (7) - 简单排序作业
- **用途**: 对数据进行基础排序
- **特点**: 适合小数据集排序
- **应用场景**: 数据排序、预处理

#### FinalSort (8) - 最终排序作业
- **用途**: 完成多阶段排序的最终阶段
- **特点**: 处理已预排序的数据
- **应用场景**: 大规模数据排序的收尾阶段

### 2. 高级计算作业

#### SortedMerge (3) - 有序合并作业
- **用途**: 合并多个已排序的数据流
- **特点**: 保持数据有序性，高效合并
- **应用场景**: 多路归并、结果汇总

#### JoinReduce (15) - 连接 Reduce 作业
- **用途**: 执行数据连接操作
- **特点**: 支持多种连接算法
- **应用场景**: 表连接、数据关联

#### PartitionReduce (10) - 分区 Reduce 作业
- **用途**: 在特定分区上执行 Reduce 操作
- **特点**: 支持局部性优化
- **应用场景**: 分区聚合、统计计算

### 3. 数据处理作业

#### RemoteCopy (12) - 远程复制作业
- **用途**: 在集群间复制数据
- **特点**: 跨节点、跨集群数据传输
- **应用场景**: 数据迁移、备份、分发

#### ShallowMerge (17) - 浅合并作业
- **用途**: 轻量级数据合并操作
- **特点**: 资源消耗少，速度快
- **应用场景**: 快速汇总、元数据合并

### 4. 维护作业

#### ReplicateChunk (100) - 复制分片作业
- **用途**: 复制数据分片到多个节点
- **特点**: 保证数据可靠性和可用性
- **应用场景**: 数据冗余、负载均衡

#### RemoveChunk (101) - 删除分片作业
- **用途**: 删除过时或无用的数据分片
- **特点**: 安全删除、垃圾回收
- **应用场景**: 存储清理、数据生命周期管理

### 5. 通用作业

#### Vanilla (16) - 原生作业
- **用途**: 执行自定义的用户代码
- **特点**: 最大灵活性，完全用户控制
- **应用场景**: 自定义算法、复杂业务逻辑

## 使用方法

### 1. 作业标识符使用

```cpp
#include <yt/yt/client/job_tracker_client/public.h>

using namespace NYT::NJobTrackerClient;

// 创建作业ID
TJobId jobId = TJobId::Create();

// 检查空ID
if (jobId != NullJobId) {
    // 处理有效作业ID
    ProcessValidJob(jobId);
}

// 操作ID使用
TOperationId operationId = TOperationId::Create();
AssociateJobWithOperation(jobId, operationId);

// 作业跟踪ID
TJobTraceId traceId = TJobTraceId::Create();
SetupJobTracing(jobId, traceId);
```

### 2. 作业类型判断

```cpp
// 作业类型工具函数
class JobTypeUtils {
public:
    static bool IsSchedulerJob(EJobType jobType) {
        return static_cast<int>(jobType) >= 1 && static_cast<int>(jobType) <= 98;
    }

    static bool IsMasterJob(EJobType jobType) {
        return static_cast<int>(jobType) >= 100 && static_cast<int>(jobType) <= 199;
    }

    static bool IsMapReduceJob(EJobType jobType) {
        return jobType == EJobType::Map ||
               jobType == EJobType::PartitionMap ||
               jobType == EJobType::SortedReduce ||
               jobType == EJobType::PartitionReduce;
    }

    static bool IsSortJob(EJobType jobType) {
        return jobType == EJobType::SimpleSort ||
               jobType == EJobType::FinalSort ||
               jobType == EJobType::IntermediateSort;
    }

    static TString GetJobTypeDescription(EJobType jobType) {
        switch (jobType) {
            case EJobType::Map:
                return "Map job - transforms input data records";
            case EJobType::SortedMerge:
                return "Sorted merge job - merges sorted data streams";
            case EJobType::Vanilla:
                return "Vanilla job - custom user code execution";
            default:
                return "Unknown job type";
        }
    }
};
```

### 3. 作业状态查询

```cpp
// 作业状态查询示例
class JobStatusQuery {
public:
    TFuture<TJobInfo> GetJobInfo(const TJobId& jobId) {
        return jobTrackerClient_->GetJob(jobId)
            .Apply(BIND([this] (const TJobPtr& job) {
                return ExtractJobInfo(job);
            }));
    }

    TFuture<std::vector<TJobInfo>> GetOperationJobs(const TOperationId& operationId) {
        return jobTrackerClient_->ListJobs(operationId)
            .Apply(BIND([this] (const std::vector<TJobPtr>& jobs) {
                return ExtractJobInfos(jobs);
            }));
    }

private:
    TJobInfo ExtractJobInfo(const TJobPtr& job) {
        TJobInfo info;
        info.JobId = job->GetId();
        info.JobType = job->GetType();
        info.State = job->GetState();
        info.StartTime = job->GetStartTime();
        info.FinishTime = job->GetFinishTime();
        info.Progress = job->GetProgress();
        return info;
    }
};
```

### 4. 作业类型转换

```cpp
// 作业类型序列化和转换
class JobTypeSerializer {
public:
    static TString SerializeJobType(EJobType jobType) {
        return ToString(static_cast<int>(jobType));
    }

    static EJobType DeserializeJobType(const TString& str) {
        int value = FromString<int>(str);
        return static_cast<EJobType>(value);
    }

    static NYson::TYsonString ConvertToYson(EJobType jobType) {
        return NYson::ConvertToYsonString(static_cast<int>(jobType));
    }

    static EJobType ConvertFromYson(const NYson::TYsonString& yson) {
        int value = NYson::ConvertTo<int>(yson);
        return static_cast<EJobType>(value);
    }
};
```

## 扩展性

### 1. 自定义作业类型

```cpp
// 扩展作业类型 (预留空间)
enum class EExtendedJobType {
    // 现有类型保持不变
    SchedulerUnknown = 98,

    // 新增自定义类型 (200+)
    CustomMLTraining = 200,
    CustomDataProcessing = 201,
    CustomAnalytics = 202,
};
```

### 2. 作业元数据扩展

```cpp
// 作业扩展元数据
struct ExtendedJobMetadata {
    TJobId JobId;
    EJobType JobType;
    TOperationId OperationId;

    // 扩展字段
    std::optional<TString> CustomName;
    std::optional<THashMap<TString, TString>> Tags;
    std::optional<THashMap<TString, NYson::TYsonString>> Attributes;
    std::optional<TInstant> Deadline;
    std::optional<int> Priority;
};
```

## 性能考虑

### 1. 标识符生成优化

```cpp
// 高性能ID生成器
class JobIdGenerator {
private:
    std::atomic<ui64> counter_{0};
    TGuid nodeId_;

public:
    TJobId GenerateJobId() {
        // 使用本地计数器减少全局同步开销
        auto localCounter = counter_.fetch_add(1);
        return TJobId::CreateWithCounter(nodeId_, localCounter);
    }
};
```

### 2. 作业类型缓存

```cpp
// 作业类型信息缓存
class JobTypeCache {
private:
    std::unordered_map<EJobType, JobTypeInfo> cache_;
    TSpinLock spinLock_;

public:
    const JobTypeInfo& GetJobTypeInfo(EJobType jobType) {
        TGuard<TSpinLock> guard(spinLock_);
        auto it = cache_.find(jobType);
        if (it != cache_.end()) {
            return it->second;
        }

        // 缓存未命中，创建并缓存
        auto& info = cache_[jobType];
        info.Type = jobType;
        info.Description = GetJobTypeDescription(jobType);
        info.ResourceRequirements = EstimateResourceRequirements(jobType);
        return info;
    }
};
```

## 最佳实践

### 1. 作业类型选择

```cpp
// 作业类型选择指南
class JobTypeSelector {
public:
    EJobType SelectOptimalJobType(const TProcessingRequest& request) {
        if (request.RequiresSorting) {
            if (request.DataSize < SmallDataThreshold) {
                return EJobType::SimpleSort;
            } else {
                return EJobType::FinalSort;
            }
        } else if (request.RequiresPartitioning) {
            return EJobType::PartitionMap;
        } else if (request.IsCustomLogic) {
            return EJobType::Vanilla;
        } else {
            return EJobType::Map;
        }
    }
};
```

### 2. 作业ID管理

```cpp
// 作业ID生命周期管理
class JobIdManager {
private:
    std::unordered_set<TJobId> activeJobs_;
    std::mutex mutex_;

public:
    TJobId AllocateJobId() {
        auto jobId = GenerateUniqueJobId();

        std::lock_guard<std::mutex> lock(mutex_);
        activeJobs_.insert(jobId);
        return jobId;
    }

    void ReleaseJobId(const TJobId& jobId) {
        std::lock_guard<std::mutex> lock(mutex_);
        activeJobs_.erase(jobId);
    }

    bool IsJobIdActive(const TJobId& jobId) const {
        std::lock_guard<std::mutex> lock(mutex_);
        return activeJobs_.find(jobId) != activeJobs_.end();
    }
};
```

## 依赖项

### 内部依赖
- `library/cpp/yt/misc/enum.h` - 枚举支持
- `library/cpp/yt/misc/guid.h` - GUID 支持
- `library/cpp/yt/misc/strong_typedef.h` - 强类型定义

### 外部依赖
- 标准库 C++ 运行时
- 原子操作支持

## 版本兼容性

- **标识符兼容性**: ID 格式保持向后兼容
- **枚举兼容性**: 新增作业类型不影响现有代码
- **序列化兼容性**: 支持多版本序列化格式

## 相关模块

- **Job Proxy Client**: 作业执行代理
- **Scheduler Client**: 作业调度系统
- **Operation Client**: 操作管理

## 参考文档

- [YTsaurus 作业系统架构](../../../docs/job-system.md)
- [作业类型参考](../../../docs/job-types.md)
- [作业调度算法](../../../docs/job-scheduling.md)
- [作业监控指南](../../../docs/job-monitoring.md)

## 贡献指南

在修改此模块时：
1. 保持作业类型编号的稳定性
2. 新增作业类型应遵循现有模式
3. 确保标识符的唯一性
4. 更新相关文档和示例
5. 保持向后兼容性