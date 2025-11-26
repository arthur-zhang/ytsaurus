# DNS over RPC (基于RPC的DNS解析)

DNS over RPC 是 YTsaurus 中提供的分布式DNS解析服务，允许通过RPC协议远程执行DNS查询操作。

## 概述

该组件实现了基于YTsaurus RPC框架的DNS解析服务，主要特点：
- 支持远程DNS查询
- 批量DNS解析请求
- IPv4/IPv6双栈支持
- 异步查询处理
- 错误处理和重试机制

## 组件架构

### 1. 客户端 (client/)
- **DNS解析器**: `dns_over_rpc_resolver.h/cpp`
  - 实现 `IDnsResolver` 接口
  - 通过RPC通道调用远程DNS服务
- **配置**: `config.h/cpp`
  - `TDnsOverRpcResolverConfig`: 客户端配置
- **服务代理**: `dns_over_rpc_service_proxy.h`
  - RPC服务的客户端代理类
- **辅助函数**: `helpers.h/cpp`
  - 通用辅助函数

### 2. 服务端 (server/)
- **DNS服务**: `dns_over_rpc_service.h/cpp`
  - 实现RPC服务接口
  - 接收并处理DNS查询请求
- **服务创建**: `CreateDnsOverRpcService()`
  - 创建DNS服务实例

### 3. 协议定义 (client/proto/)
- **协议文件**: `dns_over_rpc_service.proto`
  - 定义请求/响应消息格式
  - 支持批量查询

## 核心接口

### 客户端接口
```cpp
// 创建DNS over RPC解析器
IDnsResolverPtr CreateDnsOverRpcResolver(
    TDnsOverRpcResolverConfigPtr config,
    NRpc::IChannelPtr channel);
```

### 服务端接口
```cpp
// 创建DNS服务
NRpc::IServicePtr CreateDnsOverRpcService(
    IDnsResolverPtr resolver,
    IInvokerPtr invoker);
```

## 协议消息

### 请求消息 (TReqResolve)
```protobuf
message TReqResolve {
    message TSubrequest {
        required string host_name = 1;           // 主机名
        optional TDnsResolveOptions options = 2; // 解析选项
    }
    repeated TSubrequest subrequests = 1;       // 批量子请求
}
```

### 响应消息 (TRspResolve)
```protobuf
message TRspResolve {
    message TSubresponse {
        optional NYT.NProto.TError error = 1;   // 错误信息
        required bytes address = 2;             // 解析结果地址
    }
    repeated TSubresponse subresponses = 2;     // 批量响应
}
```

### 解析选项 (TDnsResolveOptions)
```protobuf
message TDnsResolveOptions {
    optional bool enable_ipv4 = 1 [default = true];  // 启用IPv4
    optional bool enable_ipv6 = 2 [default = true];  // 启用IPv6
}
```

## 使用方法

### 客户端使用
```cpp
// 创建RPC通道
auto channel = NRpc::CreateChannel(address);

// 创建配置
auto config = New<TDnsOverRpcResolverConfig>();

// 创建DNS解析器
auto resolver = CreateDnsOverRpcResolver(config, channel);

// 解析域名
auto future = resolver->Resolve("example.com");
auto addresses = WaitFor(future).ValueOrThrow();
```

### 服务端部署
```cpp
// 创建本地DNS解析器
auto localResolver = CreateLocalDnsResolver();

// 创建调用器
auto invoker = GetSyncInvoker();

// 创建DNS服务
auto service = CreateDnsOverRpcService(localResolver, invoker);

// 注册到RPC服务器
rpcServer->RegisterService(service);
```

## 特性

### 1. 批量查询
- 支持一次请求解析多个域名
- 减少网络开销
- 提高查询效率

### 2. 异步处理
- 所有操作都是异步的
- 返回 `TFuture` 对象
- 支持并发查询

### 3. 错误处理
- 完整的错误传播机制
- 支持部分成功/失败
- 详细的错误信息

### 4. 配置选项
- 可配置超时时间
- 可配置重试策略
- 可选择IPv4/IPv6支持

## 性能优化

1. **连接池**: 复用RPC连接减少开销
2. **批量处理**: 减少网络往返次数
3. **缓存机制**: 可配置本地缓存
4. **并发控制**: 限制并发查询数量

## 依赖项

- YT 核心库 (`yt/yt/core/`)
- RPC 框架 (`yt/yt/core/rpc/`)
- DNS 解析器 (`yt/yt/core/dns/`)
- Protocol Buffers

## 应用场景

1. **集群内部DNS**: 为YTsaurus集群提供统一的DNS服务
2. **网络隔离环境**: 通过RPC代理访问外部DNS
3. **负载均衡**: 将DNS查询分散到多个服务节点
4. **监控和审计**: 集中管理DNS查询日志

## 注意事项

1. RPC服务需要正确配置网络访问
2. 注意DNS查询的延迟对性能的影响
3. 合理配置超时和重试参数
4. 监控服务的健康状态和性能指标