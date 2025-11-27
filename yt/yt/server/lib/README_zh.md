# YTsaurus Server 公共库

## 概述

YTsaurus Server 公共库是服务器端组件的核心共享代码库，提供各个服务组件（Master、Node、Scheduler、Query Tracker 等）共用的基础功能和抽象层。该库通过统一的接口和实现，确保了代码复用性、一致性和可维护性，是整个 YTsaurus 服务器架构的重要基础。

公共库采用了模块化设计，包含分布式系统基础设施、RPC 框架、存储引擎、安全机制、监控工具等多个关键模块，为上层服务提供了稳定可靠的底层支持。

## 核心功能

### 1. 分布式系统基础

#### Hydra 一致性框架
- **Raft 实现**：基于 Raft 算法的分布式一致性实现
- **状态机复制**：支持用户自定义状态机的复制
- **快照机制**：高效的快照生成和恢复
- **成员管理**：动态成员变更和领导者选举
- **日志压缩**：智能日志压缩和垃圾回收

#### Cellar 存储
- **多副本存储**：自动的多副本数据存储
- **一致性保证**：强一致性和最终一致性支持
- **分区容错**：网络分区时的容错处理
- **负载均衡**：智能的读写负载均衡
- **故障恢复**：自动的故障检测和恢复

#### 选举服务
- **领导者选举**：分布式环境下的领导者选举
- **租约管理**：租约续租和失效处理
- **主从切换**：平滑的主从切换机制
- **故障检测**：快速的节点故障检测

### 2. RPC 框架

#### 通信基础
- **协议支持**：HTTP/HTTPS、TCP、Unix Socket
- **序列化**：高效的二进制序列化协议
- **压缩传输**：支持多种压缩算法
- **连接池**：高效的连接池管理
- **负载均衡**：多种负载均衡策略

#### 服务发现
- **动态注册**：服务的自动注册和发现
- **健康检查**：实时的服务健康检查
- **路由策略**：智能的服务路由
- **容错机制**：服务调用失败时的容错处理

#### 安全通信
- **TLS 支持**：TLS 1.2/1.3 加密通信
- **认证机制**：多种认证方式支持
- **授权控制**：细粒度的访问控制
- **审计日志**：完整的安全审计日志

### 3. 存储引擎

#### Chunk 服务器
- **数据存储**：高效的数据块存储服务
- **元数据管理**：完整的元数据管理
- **数据压缩**：多种压缩算法支持
- **数据校验**：完整的数据校验机制
- **垃圾回收**：自动的数据垃圾回收

#### Tablet 服务器
- **表服务**：分布式表的存储服务
- **事务支持**：ACID 事务支持
- **索引管理**：多维度索引支持
- **数据分片**：智能的数据分片
- **负载均衡**：自动的负载均衡

#### 文件系统
- **层次化存储**：树形结构的文件系统
- **版本控制**：文件版本管理
- **访问控制**：基于权限的访问控制
- **快照支持**：文件系统快照
- **配额管理**：存储配额管理

### 4. 作业执行

#### 作业代理
- **作业生命周期**：完整的作业生命周期管理
- **资源隔离**：CPU、内存、磁盘资源隔离
- **环境管理**：作业执行环境的管理
- **监控报告**：实时的作业监控和报告

#### 用户作业
- **作业框架**：用户作业的基础框架
- **环境管理**：沙箱环境管理
- **资源管理**：作业资源的分配和管理
- **输出管理**：作业输出的管理和收集

#### 执行节点
- **槽位管理**：作业槽位的分配和管理
- **资源调度**：CPU、内存资源的调度
- **环境准备**：作业环境的准备和清理
- **状态监控**：作业执行状态的监控

### 5. 查询处理

#### 查询引擎
- **SQL 解析**：完整的 SQL 语法解析
- **查询优化**：基于代价的查询优化
- **执行计划**：高效的执行计划生成
- **结果处理**：查询结果的处理和返回

#### 查询跟踪
- **查询监控**：实时的查询监控
- **性能分析**：查询性能分析
- **资源跟踪**：查询资源使用跟踪
- **历史记录**：查询历史记录管理

#### 多引擎支持
- **YQL 引擎**：YQL 查询引擎支持
- **ClickHouse**：CHYT 集成
- **Spark**：SPYT 集成
- **外部引擎**：可扩展的外部引擎接口

### 6. 安全机制

#### 认证授权
- **用户认证**：多种用户认证方式
- **角色管理**：基于角色的访问控制
- **权限管理**：细粒度的权限控制
- **会话管理**：安全的会话管理

#### 加密服务
- **数据加密**：数据的透明加密
- **传输加密**：网络传输加密
- **密钥管理**：安全的密钥管理
- **签名验证**：数字签名和验证

#### 审计日志
- **操作审计**：完整的操作审计日志
- **访问日志**：详细的访问日志
- **安全事件**：安全事件记录和告警
- **合规支持**：符合安全合规要求

### 7. 监控和诊断

#### 指标收集
- **性能指标**：详细的性能指标收集
- **业务指标**：关键业务指标监控
- **资源指标**：资源使用情况监控
- **错误指标**：错误率和异常统计

#### 链路追踪
- **分布式追踪**：分布式系统调用链追踪
- **性能分析**：调用链性能分析
- **故障定位**：快速定位系统故障
- **优化分析**：系统优化分析支持

#### 日志管理
- **结构化日志**：结构化的日志格式
- **日志聚合**：分布式日志聚合
- **日志查询**：高效的日志查询
- **日志分析**：智能的日志分析

## 架构设计

### 模块组织结构

```
lib/
├── hydra/                    # 分布式一致性框架
│   ├── mutation_context.cpp
│   ├── automaton.cpp
│   ├── snapshot_builder.cpp
│   └── changelog.cpp
├── cellar/                   # 多副本存储
│   ├── cellar_manager.cpp
│   ├── cellar_node.cpp
│   └── cellar_service.cpp
├── chunk_server/            # Chunk 服务器
│   ├── chunk_manager.cpp
│   ├── chunk_store.cpp
│   └── chunk_registry.cpp
├── tablet_server/           # Tablet 服务器
│   ├── tablet_manager.cpp
│   ├── tablet_cell.cpp
│   └── tablet_service.cpp
├── rpc/                     # RPC 框架
│   ├── server.cpp
│   ├── client.cpp
│   └── channel.cpp
├── security/                # 安全服务
│   ├── security_manager.cpp
│   ├── authentication.cpp
│   └── authorization.cpp
├── scheduler/               # 调度器库
│   ├── scheduler_strategy.cpp
│   ├── resource_manager.cpp
│   └── operation_controller.cpp
├── job_agent/               # 作业代理
│   ├── job_controller.cpp
│   ├── job_proxy.cpp
│   └── job_environment.cpp
├── io/                      # I/O 库
│   ├── async_reader.cpp
│   ├── async_writer.cpp
│   └── buffer_pool.cpp
└── misc/                    # 其他组件
    ├── alert_manager.cpp
    ├── component_state_checker.cpp
    └── config.cpp
```

### 核心抽象接口

#### 1. 可观察对象接口
```cpp
template <class T>
class TRefCounted {
public:
    void Ref();
    void Unref();
    int GetRefCount() const;
protected:
    virtual ~TRefCounted();
};
```

#### 2. 异步操作接口
```cpp
class TFuture {
public:
    template <class T>
    TFuture<T> Then(TCallback callback);

    bool IsReady() const;
    void Wait();
    T Get();
};
```

#### 3. 配置管理接口
```cpp
template <class TConfig>
class TConfigurable {
public:
    void SetConfig(TConfigPtr config);
    TConfigPtr GetConfig() const;

    virtual void ApplyConfig() = 0;
};
```

### 设计原则

#### 1. 模块化设计
- **松耦合**：模块间尽量松耦合
- **高内聚**：模块内部高度内聚
- **接口抽象**：通过接口进行抽象
- **依赖注入**：支持依赖注入

#### 2. 可扩展性
- **插件架构**：支持插件式扩展
- **策略模式**：可插拔的策略实现
- **事件驱动**：基于事件的架构
- **异步处理**：异步非阻塞处理

#### 3. 可靠性
- **错误处理**：完善的错误处理机制
- **重试机制**：智能的重试策略
- **熔断保护**：熔断和降级机制
- **资源管理**：自动的资源管理

## 核心组件详解

### 1. Hydra 分布式一致性框架

#### 状态机接口
```cpp
class IHydraManager {
public:
    virtual TFuture<void> ApplyMutation(
        TMutationRequest request) = 0;

    virtual TFuture<TSnapshotInfo> BuildSnapshot() = 0;

    virtual void ValidateSnapshot(TSnapshotInfo snapshot) = 0;

    virtual void Start() = 0;
    virtual void Stop() = 0;
};
```

#### 变更上下文
```cpp
class TMutationContext {
public:
    TMutationId GetMutationId() const;
    TInstant GetTimestamp() const;
    const TString& GetData() const;
    TResponseHandler GetResponseHandler() const;
};
```

#### 自动机实现
```cpp
template <class TDerived>
class TAutomaton {
public:
    void ApplyMutation(const TMutationContext& context);
    void SaveSnapshot(TSnapshotBuilder* builder);
    void LoadSnapshot(TSnapshotReader* reader);

protected:
    virtual void OnBeforeMutationApplied(const TMutationContext& context);
    virtual void OnAfterMutationApplied(const TMutationContext& context);
};
```

### 2. RPC 框架

#### 服务接口
```cpp
class IService {
public:
    virtual TServiceDescriptor GetDescriptor() const = 0;
    virtual void Invoke(IServiceContext* context) = 0;
};
```

#### 服务上下文
```cpp
class IServiceContext {
public:
    const TRequestId& GetRequestId() const;
    const TString& GetMethod() const;
    TSharedRefArray GetRequestMessage() const;

    void Reply(TSharedRefArray response);
    void Reply(const TError& error);
};
```

#### 通道抽象
```cpp
class IChannel {
public:
    TFuture<TSharedRefArray> Send(TSharedRefArray request);
    TString GetEndpointDescription() const;

    virtual TFuture<void> Terminate(const TError& error) = 0;
};
```

### 3. 存储引擎

#### Chunk 管理器
```cpp
class IChunkManager {
public:
    virtual TFuture<IChunkPtr> CreateChunk(
        const TChunkCreateOptions& options) = 0;

    virtual TFuture<void> ConfirmChunk(
        const TChunkId& chunkId,
        const TChunkInfo& info) = 0;

    virtual IChunkPtr FindChunk(const TChunkId& chunkId) = 0;
};
```

#### Tablet 管理器
```cpp
class ITabletManager {
public:
    virtual TFuture<ITabletCellPtr> CreateCell(
        const TTabletCellOptions& options) = 0;

    virtual ITabletCellPtr FindCell(const TTabletCellId& cellId) = 0;

    virtual void ReconfigureCell(
        const TTabletCellId& cellId,
        const TTabletCellOptions& options) = 0;
};
```

### 4. 作业执行框架

#### 作业控制器
```cpp
class IJobController {
public:
    virtual TFuture<IJobPtr> StartJob(
        const TJobStartOptions& options) = 0;

    virtual void AbortJob(const TJobId& jobId) = 0;

    virtual IJobPtr FindJob(const TJobId& jobId) = 0;

    virtual std::vector<IJobPtr> GetJobs() = 0;
};
```

#### 作业接口
```cpp
class IJob {
public:
    const TJobId& GetId() const;
    const TJobResources& GetResourceUsage() const;
    EJobState GetState() const;

    TFuture<TJobResult> GetResult();
    void Abort(const TError& error);
};
```

### 5. 安全框架

#### 安全管理器
```cpp
class ISecurityManager {
public:
    virtual TFuture<TAuthenticationResult> Authenticate(
        const TAuthenticationRequest& request) = 0;

    virtual TFuture<TAuthorizationResult> Authorize(
        const TAuthorizationRequest& request) = 0;

    virtual IIdentityPtr GetAuthenticatedIdentity() const = 0;
};
```

#### 权限检查
```cpp
class IAuthorizationManager {
public:
    virtual TFuture<void> CheckPermission(
        const TUser& user,
        const TString& object,
        EPermission permission) = 0;

    virtual void AddPermission(
        const TUser& user,
        const TString& object,
        EPermission permission) = 0;

    virtual void RemovePermission(
        const TUser& user,
        const TString& object,
        EPermission permission) = 0;
};
```

## 使用指南

### 编译和构建

1. **编译公共库**
```bash
# 构建整个项目（包含公共库）
ninja

# 仅构建公共库
ninja yt_server_lib

# 构建特定模块
ninja hydra_lib
ninja rpc_lib
```

2. **依赖配置**
```bash
# 安装编译依赖
sudo apt-get install -y libprotobuf-dev libgrpc++-dev

# 配置 CMake
cmake -G Ninja \
  -DCMAKE_BUILD_TYPE=Release \
  -DYT_BUILD_SERVER_LIBS=ON \
  ../ytsaurus
```

### 集成使用

#### 1. 包含头文件
```cpp
#include <yt/yt/server/lib/hydra/public.h>
#include <yt/yt/server/lib/rpc/public.h>
#include <yt/yt/server/lib/security/public.h>
#include <yt/yt/server/lib/scheduler/public.h>
```

#### 2. 使用 Hydra 框架
```cpp
class TMyAutomaton : public TAutomaton<TMyAutomaton> {
public:
    void ApplyMutation(const TMutationContext& context) {
        // 处理状态变更
    }

    void SaveSnapshot(TSnapshotBuilder* builder) {
        // 保存快照
    }

    void LoadSnapshot(TSnapshotReader* reader) {
        // 加载快照
    }
};
```

#### 3. 使用 RPC 服务
```cpp
class TMyService : public IService {
public:
    void Invoke(IServiceContext* context) override {
        if (context->GetMethod() == "MyMethod") {
            HandleMyMethod(context);
        }
    }

private:
    void HandleMyMethod(IServiceContext* context);
};
```

#### 4. 使用安全管理
```cpp
class TMyServer {
public:
    void Start() {
        // 初始化安全管理器
        securityManager_ = CreateSecurityManager(config_);

        // 启动服务
        StartService();
    }

private:
    ISecurityManagerPtr securityManager_;
};
```

### 配置管理

#### 1. 配置文件结构
```yaml
server_lib:
  # Hydra 配置
  hydra:
    enable_wal: true
    wal_path: "/var/lib/ytsaurus/wal"
    snapshot_path: "/var/lib/ytsaurus/snapshots"

  # RPC 配置
  rpc:
    max_concurrent_requests: 10000
    request_timeout: 30000
    enable_compression: true

  # 安全配置
  security:
    enable_authentication: true
    enable_authorization: true
    token_path: "/etc/ytsaurus/tokens"

  # 监控配置
  monitoring:
    enable_metrics: true
    metrics_port: 9090
    enable_tracing: true
```

#### 2. 动态配置
```cpp
class TDynamicConfigManager {
public:
    void LoadConfig(const TString& configPath);
    void UpdateConfig(const TDynamicConfig& config);
    TDynamicConfigPtr GetConfig() const;

private:
    TDynamicConfigPtr config_;
    TInstant lastUpdateTime_;
};
```

## 性能优化

### 内存管理

#### 1. 对象池
```cpp
template <class T>
class TObjectPool {
public:
    std::unique_ptr<T> Acquire() {
        if (pool_.empty()) {
            return std::make_unique<T>();
        }
        auto obj = std::move(pool_.back());
        pool_.pop_back();
        return obj;
    }

    void Release(std::unique_ptr<T> obj) {
        if (pool_.size() < maxSize_) {
            pool_.push_back(std::move(obj));
        }
    }

private:
    std::vector<std::unique_ptr<T>> pool_;
    size_t maxSize_;
};
```

#### 2. 内存分配器
```cpp
class TChunkedMemoryPool {
public:
    void* Allocate(size_t size) {
        if (currentChunk_ == nullptr ||
            currentOffset_ + size > ChunkSize) {
            AllocateNewChunk();
        }

        void* ptr = currentChunk_ + currentOffset_;
        currentOffset_ += size;
        return ptr;
    }

    void Clear() {
        currentOffset_ = 0;
        chunks_.clear();
    }

private:
    static constexpr size_t ChunkSize = 1_MB;

    std::vector<std::unique_ptr<char[]>> chunks_;
    char* currentChunk_ = nullptr;
    size_t currentOffset_ = 0;
};
```

### 网络优化

#### 1. 连接池
```cpp
class TConnectionPool {
public:
    TFuture<IChannelPtr> GetChannel(const TString& address) {
        auto it = channels_.find(address);
        if (it != channels_.end()) {
            return MakeFuture(it->second);
        }

        return CreateChannel(address).Apply(BIND([=, this] (IChannelPtr channel) {
            channels_[address] = channel;
            return channel;
        }));
    }

private:
    THashMap<TString, IChannelPtr> channels_;
};
```

#### 2. 批量处理
```cpp
class TBatchProcessor {
public:
    void AddRequest(TRequest request) {
        batch_.push_back(request);

        if (batch_.size() >= maxBatchSize_) {
            ProcessBatch();
        }
    }

    void Flush() {
        if (!batch_.empty()) {
            ProcessBatch();
        }
    }

private:
    void ProcessBatch();

    std::vector<TRequest> batch_;
    size_t maxBatchSize_;
};
```

### 并发优化

#### 1. 线程池
```cpp
class TThreadPool {
public:
    TThreadPool(size_t threadCount) {
        for (size_t i = 0; i < threadCount; ++i) {
            threads_.emplace_back([this] { WorkerLoop(); });
        }
    }

    TFuture<void> Invoke(TCallback callback) {
        auto promise = NewPromise<void>();

        {
            TGuard guard(mutex_);
            queue_.push({callback, promise});
        }

        conditionVariable_.notify_one();
        return promise;
    }

private:
    void WorkerLoop();

    std::vector<std::thread> threads_;
    std::queue<std::pair<TCallback, TPromise<void>>> queue_;
    std::mutex mutex_;
    std::condition_variable conditionVariable_;
};
```

#### 2. 异步处理
```cpp
class TAsyncProcessor {
public:
    TFuture<TResult> ProcessAsync(TInput input) {
        return Async(input, [this] (TInput input) {
            return Process(input);
        });
    }

private:
    TResult Process(const TInput& input);
};
```

## 监控和调试

### 指标收集

#### 1. 性能指标
```cpp
class TPerformanceCounters {
public:
    void Increment(const TString& name, double delta = 1.0) {
        counters_[name] += delta;
    }

    void Set(const TString& name, double value) {
        counters_[name] = value;
    }

    double Get(const TString& name) const {
        auto it = counters_.find(name);
        return it != counters_.end() ? it->second : 0.0;
    }

    THashMap<TString, double> GetAll() const {
        return counters_;
    }

private:
    THashMap<TString, double> counters_;
};
```

#### 2. 健康检查
```cpp
class THealthChecker {
public:
    void RegisterCheck(TString name, THealthCheckFunc func) {
        checks_[name] = func;
    }

    TFuture<THealthCheckResult> CheckAll() {
        std::vector<TFuture<THealthCheckResult>> futures;

        for (const auto& [name, func] : checks_) {
            futures.push_back(func());
        }

        return All(futures).Apply([](const std::vector<THealthCheckResult>& results) {
            THealthCheckResult combined;
            combined.Healthy = std::all_of(results.begin(), results.end(),
                [](const auto& result) { return result.Healthy; });
            return combined;
        });
    }

private:
    THashMap<TString, THealthCheckFunc> checks_;
};
```

### 日志管理

#### 1. 结构化日志
```cpp
class TStructuredLogger {
public:
    template <class... Args>
    void LogInfo(const TString& message, Args&&... args) {
        Log(ELogLevel::Info, message, std::forward<Args>(args)...);
    }

    template <class... Args>
    void LogError(const TString& message, Args&&... args) {
        Log(ELogLevel::Error, message, std::forward<Args>(args)...);
    }

private:
    template <class... Args>
    void Log(ELogLevel level, const TString& message, Args&&... args);
};
```

#### 2. 审计日志
```cpp
class TAuditLogger {
public:
    void LogEvent(const TAuditEvent& event) {
        auto record = BuildAuditRecord(event);
        WriteAuditRecord(record);
    }

    void LogAccess(const TUser& user, const TString& resource, EAction action) {
        TAuditEvent event;
        event.Timestamp = TInstant::Now();
        event.User = user;
        event.Resource = resource;
        event.Action = action;

        LogEvent(event);
    }

private:
    TAuditRecord BuildAuditRecord(const TAuditEvent& event);
    void WriteAuditRecord(const TAuditRecord& record);
};
```

### 调试工具

#### 1. 内存分析
```cpp
class TMemoryAnalyzer {
public:
    struct TMemoryUsage {
        size_t TotalAllocated;
        size_t CurrentlyUsed;
        size_t PeakUsage;
        THashMap<TString, size_t> UsageByType;
    };

    TMemoryUsage AnalyzeMemoryUsage() {
        TMemoryUsage usage;

        // 分析内存使用情况
        usage.TotalAllocated = GetTotalAllocated();
        usage.CurrentlyUsed = GetCurrentlyUsed();
        usage.PeakUsage = GetPeakUsage();
        usage.UsageByType = GetUsageByType();

        return usage;
    }

private:
    size_t GetTotalAllocated();
    size_t GetCurrentlyUsed();
    size_t GetPeakUsage();
    THashMap<TString, size_t> GetUsageByType();
};
```

#### 2. 性能分析
```cpp
class TProfiler {
public:
    class TScopeTimer {
    public:
        TScopeTimer(TProfiler* profiler, const TString& name)
            : Profiler_(profiler)
            , Name_(name)
            , StartTime_(TInstant::Now())
        {}

        ~TScopeTimer() {
            auto duration = TInstant::Now() - StartTime_;
            Profiler_->RecordTiming(Name_, duration);
        }

    private:
        TProfiler* Profiler_;
        TString Name_;
        TInstant StartTime_;
    };

    void RecordTiming(const TString& name, TDuration duration) {
        timings_[name].push_back(duration);
    }

    TDuration GetAverageTiming(const TString& name) const {
        auto it = timings_.find(name);
        if (it == timings_.end() || it->second.empty()) {
            return TDuration::Zero();
        }

        auto total = std::accumulate(it->second.begin(), it->second.end(), TDuration::Zero());
        return total / it->second.size();
    }

private:
    THashMap<TString, std::vector<TDuration>> timings_;
};
```

## 最佳实践

### 代码组织

#### 1. 模块化设计
- 每个模块都有清晰的职责边界
- 通过接口进行模块间交互
- 避免循环依赖
- 使用依赖注入减少耦合

#### 2. 错误处理
```cpp
// 推荐的错误处理方式
TResult<TValue> SafeOperation() {
    try {
        auto value = DoOperation();
        return TResult<TValue>(value);
    } catch (const std::exception& e) {
        return TResult<TValue>(TError(e.what()));
    }
}
```

#### 3. 资源管理
```cpp
// 使用 RAII 管理资源
class TResourceGuard {
public:
    TResourceGuard(IResource* resource) : resource_(resource) {}
    ~TResourceGuard() {
        if (resource_) {
            resource_->Release();
        }
    }

    TResourceGuard(TResourceGuard&& other) noexcept
        : resource_(other.resource_) {
        other.resource_ = nullptr;
    }

private:
    IResource* resource_;
};
```

### 性能优化建议

#### 1. 内存使用
- 使用对象池减少内存分配
- 合理设置缓存大小
- 避免内存泄漏
- 使用内存映射文件处理大文件

#### 2. 并发处理
- 使用异步 I/O 减少阻塞
- 合理设置线程池大小
- 避免锁竞争
- 使用无锁数据结构

#### 3. 网络通信
- 使用连接池复用连接
- 启用数据压缩
- 批量处理减少网络开销
- 选择合适的序列化协议

### 测试策略

#### 1. 单元测试
```cpp
TEST(THydraManager, BasicTest) {
    auto manager = CreateHydraManager(config);

    auto mutation = CreateMutation("test_data");
    auto future = manager->ApplyMutation(mutation);

    EXPECT_TRUE(future.Wait(TDuration::Seconds(5)));
    EXPECT_TRUE(future.IsOK());
}
```

#### 2. 集成测试
```cpp
TEST(TClusterIntegration, NodeFailure) {
    // 设置集群环境
    auto cluster = CreateTestCluster(3);

    // 启动服务
    cluster->Start();

    // 模拟节点故障
    cluster->FailNode(1);

    // 验证系统仍然可用
    EXPECT_TRUE(cluster->IsHealthy());

    // 清理
    cluster->Shutdown();
}
```

#### 3. 性能测试
```cpp
TEST(Performance, ThroughputTest) {
    auto service = CreateTestService();

    auto startTime = TInstant::Now();
    const int operationCount = 10000;

    for (int i = 0; i < operationCount; ++i) {
        service->ProcessRequest(CreateTestRequest());
    }

    auto duration = TInstant::Now() - startTime;
    double throughput = operationCount / duration.Seconds();

    EXPECT_GT(throughput, 1000.0); // 至少 1000 ops/sec
}
```

## 相关文档

- [YTsaurus 架构概述](../../README.md)
- [Master 服务文档](../master/README_zh.md)
- [Node 服务文档](../node/README_zh.md)
- [Scheduler 服务文档](../scheduler/README_zh.md)
- [RPC 框架设计](../../../docs/rpc.md)
- [分布式一致性](../../../docs/consistency.md)
- [存储引擎设计](../../../docs/storage.md)
- [安全机制文档](../../../docs/security.md)
- [性能调优指南](../../../docs/performance.md)