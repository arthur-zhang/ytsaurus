# RPC - 远程过程调用客户端

本模块提供 YTsaurus 客户端 RPC（远程过程调用）的辅助功能，主要用于处理请求的工作负载描述符。

## 核心功能

### 1. 工作负载描述符处理

提供了在 RPC 请求中处理工作负载描述符的模板函数：

```cpp
// 从 RPC 上下文获取工作负载描述符
template <class TContextPtr>
TWorkloadDescriptor GetRequestWorkloadDescriptor(const TContextPtr& context);

// 设置 RPC 请求的工作负载描述符
template <class TRequestPtr>
void SetRequestWorkloadDescriptor(
    const TRequestPtr& request,
    const TWorkloadDescriptor& workloadDescriptor);
```

## 使用示例

```cpp
#include <yt/yt/client/rpc/helpers.h>
#include <yt/yt/client/misc/workload.h>

// 在 RPC 处理中获取工作负载描述符
void HandleRequest(const TRequestContextPtr& context) {
    auto workloadDescriptor = GetRequestWorkloadDescriptor(context);

    // 根据工作负载类别调整处理策略
    switch (workloadDescriptor.Category) {
        case NObjectClient::EWorkloadCategory::UserInteractive:
            // 优先处理交互式请求
            ProcessWithHighPriority();
            break;
        case NObjectClient::EWorkloadCategory::UserBatch:
            // 批处理请求使用普通优先级
            ProcessWithNormalPriority();
            break;
        default:
            ProcessWithDefaultPriority();
    }
}

// 在发送 RPC 请求前设置工作负载描述符
void SendRequest(const TRequestPtr& request) {
    auto workloadDescriptor = NObjectClient::TWorkloadDescriptor(
        NObjectClient::EWorkloadCategory::UserRealtime,
        1,  // band
        TInstant::Now(),
        {"client_request"}  // annotations
    );

    SetRequestWorkloadDescriptor(request, workloadDescriptor);

    // 发送请求
    SendRpcRequest(request);
}
```

## 设计原理

### 工作负载分类
- 通过工作负载描述符，系统可以根据请求的性质进行资源分配和优先级调度
- 支持用户工作负载（交互式、批处理、实时）和系统工作负载

### 模板设计
- 使用模板函数支持不同类型的 RPC 上下文和请求对象
- 提供类型安全的工作负载描述符操作

## 依赖项

- `yt/yt/client/chunk_client/public.h` - Chunk 客户端公共接口
- `yt/yt/client/misc/workload.h` - 工作负载定义

## 注意事项

1. 确保正确设置工作负载类别，这会影响请求的处理优先级
2. Band 值用于同一类别内的优先级排序
3. 注解信息会被记录到服务端，用于调试和监控