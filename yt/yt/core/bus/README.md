# Bus 模块

## 模块概述

`yt/yt/core/bus` 模块是 YTsaurus 分布式系统的核心通信层，提供了高性能、可扩展的消息传输基础设施。该模块实现了基于 TCP 的异步通信协议，支持多路复用、SSL/TLS 加密、本地绕过优化等高级特性，为 YTsaurus 系统中各个组件间的通信提供统一的传输层抽象。

Bus 模块采用生产者-消费者模式设计，通过 `IBus` 接口抽象消息传输，支持客户端-服务器架构和点对点通信模式。模块内部实现了高效的数据包编码解码、连接池管理、流量控制等机制，确保在大规模分布式环境下的稳定性和性能。

## 主要功能

### 1. 消息传输抽象 (IBus)
- **异步发送**: 支持异步消息发送，提供交付确认和错误处理
- **多路复用**: 支持在单个连接上并行传输多个消息流
- **优先级支持**: 支持不同优先级的消息传输（Default、Control、Heavy、Interactive、RealTime）
- **统计监控**: 提供详细的网络统计信息和性能指标

### 2. 客户端通信 (IBusClient)
- **连接管理**: 自动建立和管理到服务器的连接
- **负载均衡**: 支持多路复用连接池以提高吞吐量
- **故障恢复**: 自动重连和故障转移机制
- **动态配置**: 支持运行时配置更新

### 3. 服务器通信 (IBusServer)
- **监听服务**: 监听指定端口接受客户端连接
- **消息路由**: 将接收到的消息路由到相应的处理器
- **连接池管理**: 高效管理大量并发连接
- **优雅关闭**: 支持优雅的服务关闭流程

### 4. TCP 协议实现
- **高效协议**: 自定义的二进制协议，支持消息分片和重组
- **数据包编码**: 基于流式编码器的高效数据包编码/解码
- **校验和验证**: 支持可选的数据完整性校验
- **确认机制**: 可靠的消息传输确认机制

### 5. 安全传输
- **SSL/TLS 支持**: 完整的 SSL/TLS 加密传输
- **证书管理**: 灵活的证书配置和验证机制
- **加密模式**: 支持禁用、可选、必需等多种加密模式
- **主机名验证**: 防止中间人攻击的主机名验证

### 6. 性能优化
- **本地绕过**: 同进程内的通信优化，避免网络栈开销
- **零拷贝传输**: 最小化数据拷贝以提高传输效率
- **内存池**: 预分配内存池减少动态内存分配
- **事件驱动**: 基于事件驱动的高效 I/O 处理

### 7. 配置系统
- **分层配置**: 静态配置和动态配置分离
- **多路复用段**: 不同优先级段的独立配置
- **网络适配**: 支持不同网络的特定配置
- **运行时调整**: 支持运行时配置热更新

## 文件说明

### 核心接口文件
- **public.h**: 模块的公共接口声明，定义枚举类型和常量
- **bus.h**: 核心的 `IBus` 接口定义，包含消息传输的主要抽象
- **client.h**: `IBusClient` 接口，用于创建客户端总线连接
- **server.h**: `IBusServer` 接口，用于创建服务器监听服务
- **private.h**: 私有接口和内部数据结构定义

### TCP 实现文件
- **tcp/public.h**: TCP 实现的公共接口和配置类型声明
- **tcp/config.h/c**: 配置系统实现，支持静态和动态配置
- **tcp/dispatcher.h/c**: TCP 调度器，管理网络事件和线程池
- **tcp/dispatcher_impl.h/c**: 调度器的具体实现细节
- **tcp/client.h/c**: TCP 客户端实现
- **tcp/server.h/c**: TCP 服务器实现
- **tcp/connection.h/c**: 连接管理和状态机实现
- **tcp/packet.h/c**: 数据包编码解码实现
- **tcp/local_bypass.h/c**: 本地绕过优化实现
- **tcp/private.h**: TCP 实现的私有接口
- **tcp/configure_dispatcher.cpp**: 调度器配置初始化

### 公共实现文件
- **public.cpp**: 模块初始化和全局状态管理

### 测试文件
- **unittests/bus_ut.cpp**: 基础功能测试
- **unittests/ssl_ut.cpp**: SSL 功能测试

## 使用方法

### 基本客户端使用
```cpp
#include <yt/yt/core/bus/tcp/client.h>
#include <yt/yt/core/bus/bus.h>

// 创建客户端配置
auto clientConfig = New<NBus::TBusClientConfig>();
clientConfig->Address = "localhost:9000";

// 创建客户端
auto client = NBus::CreateTcpBusClient(clientConfig);

// 创建消息处理器
class MyHandler : public NBus::IMessageHandler {
public:
    void HandleMessage(NBus::TSharedRefArray message, NBus::IBusPtr replyBus) noexcept override {
        // 处理接收到的消息
        std::cout << "Received message" << std::endl;
    }
};

// 创建总线连接
auto bus = client->CreateBus(New<MyHandler>());

// 发送消息
auto message = NBus::TSharedRefArray(NBus::TSharedRef::FromString("Hello, Server!"));
auto sendFuture = bus->Send(message);
```

### 基本服务器使用
```cpp
#include <yt/yt/core/bus/tcp/server.h>

// 创建服务器配置
auto serverConfig = New<NBus::TBusServerConfig>();
serverConfig->Port = 9000;

// 创建消息处理器
class EchoHandler : public NBus::IMessageHandler {
public:
    void HandleMessage(NBus::TSharedRefArray message, NBus::IBusPtr replyBus) noexcept override {
        // 回显消息
        if (replyBus) {
            replyBus->Send(message);
        }
    }
};

// 创建服务器
auto server = NBus::CreateTcpBusServer(serverConfig);

// 启动服务器
server->Start(New<EchoHandler>());

// 服务器运行...
```

### 使用 SSL 加密传输
```cpp
#include <yt/yt/core/bus/tcp/config.h>

// 创建启用 SSL 的客户端配置
auto clientConfig = New<NBus::TBusClientConfig>();
clientConfig->Address = "secure.example.com:9443";
clientConfig->EncryptionMode = NBus::EEncryptionMode::Required;
clientConfig->VerificationMode = NBus::EVerificationMode::Full;

auto client = NBus::CreateTcpBusClient(clientConfig);
```

### 使用多路复用和优先级
```cpp
// 为不同优先级创建不同的客户端连接
auto normalClient = NBus::CreateTcpBusClient(clientConfig);
auto highPriorityClient = NBus::CreateTcpBusClient(clientConfig);

auto normalBus = normalClient->CreateBus(handler, NBus::TCreateBusOptions{
    .MultiplexingBand = NBus::EMultiplexingBand::Default
});

auto realtimeBus = highPriorityClient->CreateBus(handler, NBus::TCreateBusOptions{
    .MultiplexingBand = NBus::EMultiplexingBand::RealTime
});
```

### 使用交付确认
```cpp
// 发送带交付确认的消息
NBus::TSendOptions options;
options.TrackingLevel = NBus::EDeliveryTrackingLevel::Full;

auto message = NBus::TSharedRefArray(NBus::TSharedRef::FromString("Important message"));
auto deliveryFuture = bus->Send(message, options);

// 等待交付确认
deliveryFuture.Subscribe([](const NYT::TError& error) {
    if (error.IsOK()) {
        std::cout << "Message delivered successfully" << std::endl;
    } else {
        std::cout << "Delivery failed: " << error.GetMessage() << std::endl;
    }
});
```

### 动态配置更新
```cpp
// 创建动态配置
auto dynamicConfig = New<NBus::TBusClientDynamicConfig>();
dynamicConfig->ReadTimeout = TDuration::Seconds(30);

// 更新客户端配置
client->Reconfigure(dynamicConfig);
```

## 依赖关系

### 内部依赖
- **yt/yt/core/actions**: 异步编程基础设施，Future/Promise 机制
- **yt/yt/core/net**: 网络地址和套接字抽象
- **yt/yt/core/crypto**: SSL/TLS 加密支持
- **yt/yt/core/misc**: 基础工具和错误处理
- **yt/yt/core/ytree**: 配置系统和属性字典

### 外部依赖
- **OpenSSL**: SSL/TLS 加密实现
- **系统网络栈**: TCP/IP 协议栈和套接字 API
- **C++20**: 现代 C++ 特性支持

## 实现原理

### 协议设计
Bus 模块使用自定义的二进制协议，协议头部包含：
- 包类型（Message、Ack、SslAck）
- 包标志位
- 包 ID（用于确认和重传）
- 包大小
- 可选的校验和

### 多路复用机制
通过 EMultiplexingBand 枚举实现不同优先级的消息流：
- **Default**: 普通消息，默认优先级
- **Control**: 控制消息，较高优先级
- **Heavy**: 大数据传输，低优先级
- **Interactive**: 交互式消息，高优先级
- **RealTime**: 实时消息，最高优先级

### 连接管理
- **连接池**: 客户端维护连接池以复用 TCP 连接
- **心跳检测**: 定期发送心跳包维持连接活跃
- **自动重连**: 连接断开时自动尝试重新建立
- **优雅关闭**: 确保所有正在传输的消息完成后再关闭连接

### 数据包处理
使用流式编码器/解码器处理数据包：
- **零拷贝编码**: 直接从用户内存构建网络数据包
- **增量解码**: 逐步解码接收到的数据流
- **内存复用**: 重用编码器/解码器实例减少分配

### 错误处理
- **分类错误**: TransportError、SslError 等不同类型的错误
- **错误传播**: 将网络错误转换为 TError 对象
- **重试机制**: 对可恢复错误实施自动重试

### 性能优化
- **本地绕过**: 同进程通信通过内存拷贝而非网络栈
- **批量处理**: 批量发送和接收消息提高吞吐量
- **内存预分配**: 预分配缓冲区减少运行时分配
- **事件驱动**: 使用 epoll/kqueue 实现高效 I/O 多路复用

## 配置系统

### 静态配置
- **TTcpDispatcherConfig**: 调度器全局配置
- **TBusClientConfig**: 客户端配置
- **TBusServerConfig**: 服务器配置
- **TMultiplexingBandConfig**: 多路复用段配置

### 动态配置
- **TTcpDispatcherDynamicConfig**: 调度器动态配置
- **TBusClientDynamicConfig**: 客户端动态配置
- **TBusServerDynamicConfig**: 服务器动态配置

### 配置热更新
所有配置都支持运行时热更新，无需重启服务即可应用新配置。

## 安全特性

### SSL/TLS 支持
- **证书验证**: 支持 CA 签名证书验证
- **主机名验证**: 防止证书替换攻击
- **密码套件**: 支持现代安全的密码套件
- **协议版本**: 支持 TLS 1.2 和 TLS 1.3

### 访问控制
- **IP 白名单**: 限制允许连接的客户端 IP
- **网络隔离**: 支持多网络环境的访问控制
- **端口绑定**: 精确控制监听端口和接口

## 监控和诊断

### 网络统计
- **吞吐量统计**: 发送/接收的字节数和包数
- **错误统计**: 读写错误、重传次数等
- **连接统计**: 活跃连接数、等待队列等
- **延迟统计**: 消息传输延迟指标

### 调试支持
- **端点描述**: 详细的连接端点信息
- **Orchid 集成**: 通过 Orchid 暴露监控指标
- **日志记录**: 详细的连接和传输日志
- **调试模式**: 开发环境下的调试选项

## 最佳实践

1. **连接复用**: 优先使用连接池而非频繁创建新连接
2. **优先级管理**: 合理使用多路复用段提高关键消息的优先级
3. **错误处理**: 总是检查发送操作的返回状态
4. **资源清理**: 在应用退出时正确关闭总线连接
5. **配置调优**: 根据网络环境调整超时和缓冲区大小

## 性能调优

### 网络优化
- 调整 TCP 缓冲区大小以匹配网络带宽延迟积
- 启用 TCP_NODELAY 减少小包延迟
- 使用合适的 TOS 优化网络路径选择

### 内存优化
- 预分配消息缓冲区减少动态分配
- 调整连接池大小平衡内存使用和性能
- 使用内存复用减少 GC 压力

### 并发优化
- 根据硬件配置调整线程池大小
- 合理设置最大并发连接数
- 使用多路复用减少连接开销

## 故障排查

### 常见问题
1. **连接超时**: 检查网络连通性和防火墙设置
2. **SSL 错误**: 验证证书配置和加密模式
3. **内存泄漏**: 确保正确释放总线资源
4. **性能问题**: 检查网络统计和配置参数

### 调试工具
- 使用网络统计信息分析性能瓶颈
- 通过日志追踪连接建立和消息传输
- 使用网络抓包工具分析协议交互
- 监控系统资源使用情况

## 扩展点

- **自定义协议**: 实现自己的 IPacketTranscoderFactory
- **传输层**: 实现非 TCP 的传输层（如 Unix Domain Socket）
- **消息路由**: 实现自定义的消息路由策略
- **负载均衡**: 实现特殊的连接负载均衡算法
- **监控集成**: 集成外部监控系统和告警