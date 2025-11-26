# Misc - 客户端杂项组件

本模块包含 YTsaurus 客户端的杂项工具和辅助功能，主要提供工作负载管理、方法实现辅助和通用配置等功能。

## 核心组件

### 1. 工作负载管理 (Workload Management)

#### 工作负载分类 (EWorkloadCategory)
定义了不同类型的工作负载，用于管理系统资源分配和优先级：

- **系统工作负载**：
  - `SystemReplication` - 数据复制
  - `SystemMerge` - 数据合并
  - `SystemRepair` - 数据修复
  - `SystemTabletCompaction` - Tablet 压缩
  - `SystemTabletLogging` - Tablet 日志记录
  - `SystemTabletPartitioning` - Tablet 分区
  - `SystemTabletPreload` - Tablet 预加载
  - `SystemTabletRecovery` - Tablet 恢复
  - `SystemTabletReplication` - Tablet 复制
  - `SystemTabletSnapshot` - Tablet 快照
  - `SystemTabletStoreFlush` - Tablet Store 刷新
  - `SystemReincarnation` - 系统重生
  - `SystemArtifactCacheDownload` - 工件缓存下载

- **用户工作负载**：
  - `UserBatch` - 批处理任务
  - `UserInteractive` - 交互式任务
  - `UserRealtime` - 实时任务
  - `UserDynamicStoreRead` - 动态存储读取

#### 工作负载描述符 (TWorkloadDescriptor)
```cpp
struct TWorkloadDescriptor {
    EWorkloadCategory Category;          // 工作负载类别
    int Band;                           // 相对重要性（同类别内）
    TInstant Instant;                   // 初始化时间
    std::vector<TString> Annotations;   // 客户端注解
    std::optional<...> CompressionFairShareTag; // 压缩公平共享标签
};
```

主要功能：
- `GetPriority()` - 计算聚合优先级
- `SetCurrentInstant()` - 更新时间戳
- 序列化/反序列化支持

### 2. 方法实现辅助工具

提供了宏定义来简化未实现或不受支持方法的声明：

```cpp
// 声明未实现的方法
UNIMPLEMENTED_METHOD(ReturnType, MethodName, (int arg1, TString arg2))

// 声明不支持的方法
UNSUPPORTED_METHOD(ReturnType, MethodName, (...))

// 声明未实现的常量方法
UNIMPLEMENTED_CONST_METHOD(ReturnType, MethodName, (...))
```

参数处理宏：
- `Y_METHOD_UNUSED_ARGS_DECLARATION` - 声明未使用的参数
- `Y_METHOD_USED_ARGS_DECLARATION` - 声明使用的参数
- `Y_PASS_METHOD_USED_ARGS` - 传递参数列表

### 3. 配置管理

#### TConfig
提供客户端配置的序列化和反序列化功能，支持从不同格式加载配置。

## 使用示例

### 工作负载管理
```cpp
#include <yt/yt/client/misc/workload.h>

// 创建工作负载描述符
auto descriptor = TWorkloadDescriptor(
    EWorkloadCategory::UserInteractive,
    1,  // band
    TInstant::Now(),  // 当前时间
    {"user_request", "high_priority"}  // 注解
);

// 获取优先级
auto priority = descriptor.GetPriority();

// 获取压缩调用器
auto invoker = GetCompressionInvoker(descriptor);

// 检查是否为系统工作负载
bool isSystem = IsSystemWorkloadCategory(descriptor.Category);
```

### 方法实现辅助
```cpp
class MyInterface {
public:
    // 声明未实现的方法
    UNIMPLEMENTED_METHOD(TString, GetData, ());

    // 声明不支持的方法
    UNSUPPORTED_METHOD(void, SetData, (const TString& data));

    // 声明带参数的未实现方法
    UNIMPLEMENTED_METHOD(int, Calculate, (int x, int y));
};
```

## 设计原理

### 工作负载分类系统
1. **优先级计算**：基于类别和 Band 的组合优先级
2. **公平共享**：不同类别有不同的资源分配权重
3. **注解系统**：支持调试和监控的可选注解
4. **时间追踪**：记录工作负载的创建时间用于排序

### 宏系统设计
- **类型安全**：编译时检查参数类型
- **自动生成**：减少样板代码
- **错误处理**：统一的错误抛出机制
- **一致性**：确保所有未实现方法的错误消息一致

## 依赖项

- `yt/yt/core/actions/public.h` - 动作系统
- `yt/yt/core/rpc/public.h` - RPC 基础设施
- `yt/yt/core/yson/public.h` - YSON 序列化
- `yt/yt/core/ytree/public.h` - 树形结构操作
- `yt/yt/core/concurrency/public.h` - 并发原语
- 标准 C++ 库
- Yandex Util 库

## 注意事项

1. **工作负载优先级**：确保正确的工作负载类别，这将影响资源分配
2. **Band 值**：在同一类别内，较大的 Band 值表示更高的优先级
3. **注解使用**：注解会被记录在服务端，用于调试和监控
4. **宏使用**：宏会自动处理参数传递和错误抛出
5. **序列化**：工作负载描述符支持多种序列化格式

## 相关模块

- `yt/yt/core/concurrency` - 并发控制和线程池
- `yt/yt/core/rpc` - RPC 通信
- `yt/yt/core/yson` - 数据序列化
- `yt/yt/client/table_client` - 表客户端（工作负载的典型使用者）