# Scheduler - 调度器客户端

本模块提供 YTsaurus 调度器的客户端接口，用于管理操作（Operation）和分配（Allocation）的提交和控制。

## 核心概念

### 1. 操作类型
- **Map** - 映射操作
- **Merge** - 合并操作
- **Erase** - 擦除操作
- **Sort** - 排序操作
- **Reduce** - 归约操作
- **MapReduce** - 映射归约操作
- **RemoteCopy** - 远程复制操作
- **JoinReduce** - 连接归约操作
- **Vanilla** - 原始操作

### 2. 核心类型
```cpp
using TAllocationId = TGuid;  // 分配ID
using TOperationId = TGuid;   // 操作ID
using TJobId = TGuid;         // 作业ID
```

### 3. 主要功能
- 操作缓存管理
- 操作ID和别名处理
- 规格补丁（Spec Patch）支持
- 操作状态跟踪