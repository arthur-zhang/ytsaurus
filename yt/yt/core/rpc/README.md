# RPC 模块

## 模块概述

`yt/yt/core/rpc` 模块是 YTsaurus 分布式系统的远程过程调用（RPC）框架，提供了完整的高性能 RPC 服务实现。该模块基于 Bus 通信层构建，支持服务注册、方法调用、流式传输、负载均衡、重试机制等功能，为 YTsaurus 系统中各组件间的通信提供统一、可靠、高效的 RPC 基础设施。

## 主要功能

### 1. RPC 服务框架
- **服务注册**: RPC 服务的注册和发现
- **方法调用**: 远程方法的调用和响应
- **服务代理**: 客户端代理的自动生成
- **接口定义**: 基于 Protocol Buffers 的接口定义

### 2. 通信协议
- **二进制协议**: 高效的二进制 RPC 协议
- **消息序列化**: 基于 protobuf 的消息序列化
- **压缩传输**: 可选的消息压缩传输
- **流式传输**: 支持流式的数据传输

### 3. 可靠性保证
- **重试机制**: 自动重试失败的调用
- **超时控制**: 调用超时的控制和处理
- **错误传播**: RPC 错误的统一传播机制
- **熔断器**: 防止级联故障的熔断机制

### 4. 性能优化
- **连接复用**: RPC 连接的复用和管理
- **批量调用**: 批量 RPC 调用优化
- **并发控制**: 并发调用的控制和管理
- **负载均衡**: 多服务实例的负载均衡

## 核心组件

### IChannel
RPC 通道抽象，表示与 RPC 服务的连接通道。

### IServiceContext
服务上下文，包含单个 RPC 调用的所有信息。

### TDispatcher
RPC 调度器，负责 RPC 调用的调度和执行。

## 使用示例

### RPC 服务定义
```cpp
// 定义 RPC 服务接口
interface IMyService
    : public virtual TRefCounted
{
    virtual TFuture<TString> GetData(const TString& key) = 0;
    virtual TFuture<void> SetData(const TString& key, const TString& value) = 0;
};

DEFINE_REFCOUNTED_TYPE(IMyService)

// 实现服务
class TMyService
    : public IMyService
{
public:
    TFuture<TString> GetData(const TString& key) override {
        return MakeFuture("Value for " + key);
    }

    TFuture<void> SetData(const TString& key, const TString& value) override {
        // 存储数据的逻辑
        return VoidFuture;
    }
};
```

### RPC 服务注册
```cpp
#include <yt/yt/core/rpc/server.h>

// 创建 RPC 服务器
auto server = CreateRpcServer();

// 注册服务
auto service = New<TMyService>();
server->RegisterService(service);

// 启动服务器
server->Start();
```

### RPC 客户端调用
```cpp
#include <yt/yt/core/rpc/channel.h>

// 创建 RPC 通道
auto channel = CreateTcpChannel("localhost:9000");

// 创建服务代理
auto proxy = CreateProxy<IMyService>(channel);

// 调用 RPC 方法
auto future = proxy->GetData("test_key");
auto result = WaitFor(future).ValueOrThrow();

std::cout << "Got result: " << result << std::endl;
```

## 配置选项

### 连接配置
- **超时设置**: 连接和调用超时
- **重试策略**: 重试次数和间隔
- **负载均衡**: 负载均衡策略
- **压缩选项**: 消息压缩配置

### 服务配置
- **最大并发**: 最大并发调用数
- **队列大小**: 请求队列大小
- **线程池**: 服务执行线程池
- **内存限制**: 内存使用限制

## 性能特性

- **低延迟**: 微秒级的 RPC 调用延迟
- **高吞吐**: 支持每秒数十万次 RPC 调用
- **内存高效**: 优化的内存使用和分配
- **CPU 高效**: 最小化 CPU 开销

## 依赖关系

- **yt/yt/core/bus**: 底层通信框架
- **yt/yt/core/actions**: 异步编程支持
- **yt/yt/core/misc**: 基础工具和错误处理
- **protobuf**: Protocol Buffers 序列化