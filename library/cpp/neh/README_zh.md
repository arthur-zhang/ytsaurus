# Neh 网络传输库

## 项目概述

Neh 是一个高性能的网络传输库，为分布式系统提供了简单而强大的请求/响应接口。该库支持多种传输协议，包括 HTTP/1.1、HTTP/2、TCP、UDP 等，具有卓越的性能和灵活性。

### 核心功能
- **多协议支持**：HTTP/1.1、HTTP/2、TCP、UDP、Unix Socket 等
- **高性能异步I/O**：基于 Boost.Asio 的异步网络处理
- **连接池管理**：智能连接缓存和复用机制
- **SSL/TLS 支持**：安全的 HTTPS 通信
- **负载均衡**：支持多连接和并发请求处理
- **统计监控**：详细的网络性能统计指标

## 文件说明

### 核心头文件
- **neh.h** - 主要接口定义，包含 TMessage、TError 等核心数据结构
- **netliba.h** - NetLiba 协议接口和全局配置选项
- **factory.h** - 协议工厂类，用于创建不同协议实例
- **stat.h** - 统计信息收集和报告接口

### 协议实现
- **http2.h/http2.cpp** - HTTP/1.1 和 HTTP/2 协议实现
- **https.h/https.cpp** - HTTPS 安全传输协议实现
- **tcp.h/tcp.cpp** - TCP 传输协议实现
- **udp.h/udp.cpp** - UDP 数据报传输协议实现
- **rpc.h/rpc.cpp** - RPC 远程过程调用实现

### 辅助组件
- **conn_cache.h/conn_cache.cpp** - 连接缓存管理
- **multiclient.h/multiclient.cpp** - 多客户端并发处理
- **smart_ptr.h/smart_ptr.cpp** - 智能指针管理
- **utils.h/utils.cpp** - 通用工具函数
- **pipequeue.h/pipequeue.h** - 管道队列实现

### 配置选项
- **THttp2Options** - HTTP/2 协议配置参数
- **TNetLibaOptions** - NetLiba 全局配置选项

## 使用示例

### HTTP 客户端示例
```cpp
#include <library/cpp/neh/http2.h>
#include <library/cpp/neh/neh.h>

using namespace NNeh;

// 创建 HTTP 客户端
IProtocol* protocol = Http1Protocol();

// 发送请求
TMessage request("http://example.com/api", "GET /api HTTP/1.1\r\n\r\n");
auto response = protocol->SendRequest(request);

// 处理响应
if (response.IsSuccess()) {
    std::cout << "Response: " << response.Data << std::endl;
} else {
    std::cout << "Error: " << response.Error.GetText() << std::endl;
}
```

### HTTP 服务器示例
```cpp
#include <library/cpp/neh/http2.h>

using namespace NNeh;

// 创建 HTTP 服务器
IProtocol* protocol = Http1Protocol();

// 设置请求处理器
auto handler = [](const TMessage& request) -> TMessage {
    return TMessage("", "HTTP/1.1 200 OK\r\n\r\nHello World!");
};

// 启动服务器
protocol->Listen("http://0.0.0.0:8080", handler);
```

## 实现原理

### 异步 I/O 架构
Neh 采用基于事件驱动的异步 I/O 模型：
- 使用 Boost.Asio 作为底层网络库
- 非阻塞套接字操作
- 事件循环处理所有 I/O 事件
- 回调机制处理请求和响应

### 连接池管理
- **连接复用**：保持活跃连接以减少连接建立开销
- **智能缓存**：LRU 算法管理空闲连接
- **并发控制**：限制每个目标的最大连接数
- **超时管理**：自动清理长时间未使用的连接

### 协议抽象层
- **统一接口**：所有协议实现相同的 IProtocol 接口
- **工厂模式**：通过工厂类创建协议实例
- **插件架构**：支持动态加载新的协议实现

### 性能优化技术
- **零拷贝**：减少内存复制操作
- **缓冲池**：预分配内存缓冲区
- **批处理**：合并小的网络操作
- **压缩**：支持数据压缩传输

## 应用场景

### 分布式系统通信
- 微服务架构中的服务间通信
- 分布式数据库的节点间数据同步
- 分布式计算的任务分发和结果收集

### 高性能 Web 服务
- 高并发 API 网关
- 负载均衡器和反向代理
- CDN 内容分发网络

### 实时数据处理
- 流式数据处理系统
- 实时监控和告警系统
- 在线游戏服务器

### 网络协议开发
- 自定义应用层协议实现
- 网络协议转换和网关
- 协议性能测试和基准评估

## 配置说明

### HTTP/2 协议配置
```cpp
THttp2Options::ConnectTimeout = TDuration::Seconds(30);
THttp2Options::InputDeadline = TDuration::Minutes(5);
THttp2Options::OutputDeadline = TDuration::Minutes(5);
THttp2Options::AsioThreads = std::thread::hardware_concurrency();
THttp2Options::TcpKeepAlive = true;
```

### 连接池配置
```cpp
// 设置输出连接限制
SetHttp2OutputConnectionsLimits(1000, 2000);

// 设置输入连接限制
SetHttp2InputConnectionsLimits(500, 1000);

// 设置连接超时
SetHttp2InputConnectionsTimeouts(60, 300);
```

## 性能特性

- **高吞吐量**：支持每秒数万次请求处理
- **低延迟**：微秒级的请求响应时间
- **高并发**：支持数万并发连接
- **内存效率**：优化的内存使用和垃圾回收
- **CPU 效率**：最少化系统调用和上下文切换

## 依赖项

- **Boost.Asio** - 异步网络编程库
- **OpenSSL** - SSL/TLS 加密支持（可选）
- **Zlib** - 数据压缩支持（可选）