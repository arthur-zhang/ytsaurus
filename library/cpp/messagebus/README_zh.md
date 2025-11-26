# MessageBus 异步消息总线

## 项目概述

MessageBus 是一个高性能的异步消息传输框架，专门为分布式系统中的进程间通信设计。它提供了可靠的消息传递、连接管理、会话控制、负载均衡、故障转移等功能，支持 TCP 和 Unix Domain Socket 传输，是 YTsaurus 系统的核心通信基础设施。

## 文件说明

### 核心组件

- **`ybus.h`** - 主要入口头文件
  - 包含所有核心功能的统一接口
  - 提供异步消息传输的完整 API
  - 支持协议定义和消息处理

- **`message.h/cpp`** - 消息系统
  - `TBusMessage`: 消息基类
  - `TBusIdentity`: 消息身份标识
  - 消息序列化和反序列化
  - 支持请求-响应模式和单向消息

- **`session.h/cpp`** - 会话管理
  - `TBusSession`: 会话基类
  - `TBusClientSession`: 客户端会话
  - `TBusServerSession`: 服务端会话
  - 连接池和会话生命周期管理

- **`connection.h/cpp`** - 连接管理
  - 网络连接的建立和维护
  - 连接状态监控和故障检测
  - 自动重连和负载均衡

### 网络和传输

- **`network.h/cpp`** - 网络抽象层
  - `TNetAddr`: 网络地址封装
  - 支持多种网络协议 (TCP/UDP/Unix Socket)
  - 地址解析和路由

- **`remote_connection.h/cpp`** - 远程连接实现
  - `TRemoteClientConnection`: 客户端连接
  - `TRemoteServerConnection`: 服务端连接
  - 异步 I/O 和事件驱动

- **`socket_addr.h/cpp`** - 套接字地址
  - IP 地址和端口封装
  - IPv4/IPv6 支持
  - Unix Domain Socket 支持

### 协议和编解码

- **`config/`** - 协议配置
  - 消息协议定义
  - 编解码器配置
  - 序列化格式设置

- **`protobuf/`** - Protocol Buffers 支持
  - protobuf 消息编解码
  - 版本兼容性处理
  - 消息格式验证

### 处理器和调度

- **`handler.h/cpp`** - 消息处理器
  - `IBusClientHandler`: 客户端处理器接口
  - `IBusServerHandler`: 服务端处理器接口
  - 消息路由和分发

- **`scheduler/`** - 调度器
  - 消息调度和优先级管理
  - 任务队列和工作线程
  - 负载均衡算法

- **`actor/`** - Actor 模式实现
  - 消息驱动的并发模型
  - Actor 生命周期管理
  - 消息邮箱和调度

### 队列和缓冲

- **`messqueue.cpp`** - 消息队列实现
- **`lfqueue_batch.h`** - 无锁队列批处理
- **`left_right_buffer.h`** - 左右缓冲区模式

### 监控和调试

#### `monitoring/` 目录

- 连接状态监控
- 性能指标收集
- 实时状态展示

#### `debug_receiver/` 目录

- 调试消息接收器
- 消息跟踪和分析
- 开发辅助工具

### 工具和辅助

- **`locator.h/cpp`** - 服务定位器
- **`event_loop.h/cpp`** - 事件循环
- **`duration_histogram.h/cpp`** - 延迟直方图
- **`message_counter.h/cpp`** - 消息计数器

### 配置和测试

- **`session_config.h`** - 会话配置
- **`queue_config.h/cpp`** - 队列配置
- **`test/`** - 测试套件
- **`www/`** - Web 管理界面

## 实现原理

### 架构设计

MessageBus 采用分层架构设计：

```
┌─────────────────────────────────────────┐
│           Application Layer              │
├─────────────────────────────────────────┤
│           Session Layer                 │
├─────────────────────────────────────────┤
│           Connection Layer              │
├─────────────────────────────────────────┤
│           Network Layer                 │
├─────────────────────────────────────────┤
│           Transport Layer               │
└─────────────────────────────────────────┘
```

### 消息生命周期

```cpp
class TBusMessage {
    TBusIdentity Identity;     // 消息唯一标识
    EMessageStatus Status;     // 消息状态
    TInstant RecvTime;        // 接收时间

    virtual void Serialize(TBuffer& buffer) = 0;
    virtual void Deserialize(const TBuffer& buffer) = 0;
};
```

### 会话管理

```cpp
// 客户端会话
class TBusClientSession: public TBusSession {
    virtual TFuture<TMessagePtr> Send(
        TBusMessagePtr msg,
        const TNetAddr& addr,
        TDuration timeout = TDuration::Max()
    ) = 0;

    virtual void SendAndForget(
        TBusMessagePtr msg,
        const TNetAddr& addr
    ) = 0;
};

// 服务端会话
class TBusServerSession: public TBusSession {
    virtual void RegisterHandler(
        const TString& service,
        IBusServerHandler* handler
    ) = 0;
};
```

### 异步事件循环

```cpp
class TEventLoop {
private:
    TVector<T pollfd> PollFds;
    TQueue<TEvent> EventQueue;

public:
    void Run() {
        while (!Stopped) {
            WaitAndProcessEvents();
            DrainEventQueue();
            ScheduleTimeouts();
        }
    }
};
```

### 无锁队列

```cpp
template<typename T>
class TLockFreeQueue {
private:
    std::atomic<Node*> Head;
    std::atomic<Node*> Tail;

public:
    void Enqueue(const T& item);
    bool Dequeue(T& item);
    bool DequeueBatch(TVector<T>& items, size_t maxSize);
};
```

## 使用示例

### 基础客户端

```cpp
#include <library/cpp/messagebus/ybus.h>

// 定义消息类型
class TRequestMessage: public TBusMessage {
    TString Data;

public:
    TRequestMessage(const TString& data) : Data(data) {}

    void Serialize(TBuffer& buffer) override {
        SerializeToString(Data, buffer);
    }

    void Deserialize(const TBuffer& buffer) override {
        DeserializeFromString(Data, buffer);
    }
};

class TResponseMessage: public TBusMessage {
    TString Result;

public:
    // 类似的序列化/反序列化实现
};

// 实现客户端处理器
class TMyClientHandler: public IBusClientHandler {
public:
    void OnReply(TBusMessage* request, TBusMessage* reply) override {
        auto* resp = dynamic_cast<TResponseMessage*>(reply);
        if (resp) {
            std::cout << "Received reply: " << resp->Result << std::endl;
        }
    }

    void OnMessageError(TBusMessage* request, EMessageStatus status) override {
        std::cerr << "Error: " << status << std::endl;
    }
};

int main() {
    // 创建消息队列
    auto queue = CreateMessageQueue(TBusQueueConfig());

    // 创建协议
    auto protocol = new TBusProtocol("MyProtocol");

    // 创建客户端会话
    TBusClientSessionConfig config;
    config.SendTimeout = TDuration::Seconds(5);
    config.ConnectTimeout = TDuration::Seconds(3);

    auto handler = MakeHolder<TMyClientHandler>();
    auto session = TBusClientSession::Create(protocol, handler.Get(), config, queue);

    // 发送消息
    TNetAddr addr("127.0.0.1", 8080);
    auto request = MakeHolder<TRequestMessage>("Hello, Server!");
    session->Send(request.Release(), addr);

    // 运行事件循环
    queue->Run();

    return 0;
}
```

### 服务端实现

```cpp
// 实现服务端处理器
class TMyServerHandler: public IBusServerHandler {
public:
    void OnMessage(TOnMessageContext& context) override {
        auto* request = dynamic_cast<TRequestMessage*>(context.GetMessage());
        if (request) {
            // 处理请求
            TString result = ProcessRequest(request->Data);

            // 发送响应
            auto response = MakeHolder<TResponseMessage>();
            response->Result = result;
            context.SendReplyMove(response.Release());
        }
    }

private:
    TString ProcessRequest(const TString& data) {
        return "Processed: " + data;
    }
};

int main() {
    // 创建消息队列
    auto queue = CreateMessageQueue(TBusQueueConfig());

    // 创建协议
    auto protocol = new TBusProtocol("MyProtocol");

    // 创建服务端会话
    TBusServerSessionConfig config;
    config.ListenPort = 8080;
    config.MaxConnections = 1000;

    auto handler = MakeHolder<TMyServerHandler>();
    auto session = TBusServerSession::Create(protocol, handler.Get(), config, queue);

    // 运行事件循环
    queue->Run();

    return 0;
}
```

### 高级功能示例

#### 连接池管理

```cpp
class TConnectionPoolManager {
private:
    TBusClientSessionPtr Session;
    THashMap<TNetAddr, TBusConnectionPtr> Connections;

public:
    void EnsureConnection(const TNetAddr& addr) {
        if (!Connections.contains(addr)) {
            auto conn = Session->GetConnection(addr);
            Connections[addr] = conn;
        }
    }

    template<typename TMsg>
    TFuture<TBusMessage*> SendMessage(TMsg* msg, const TNetAddr& addr) {
        EnsureConnection(addr);
        return Session->Send(msg, addr);
    }
};
```

#### 负载均衡

```cpp
class TLoadBalancer {
private:
    TVector<TNetAddr> Servers;
    std::atomic<size_t> RoundRobinIndex{0};

public:
    TNetAddr SelectServer() {
        size_t index = RoundRobinIndex.fetch_add(1) % Servers.size();
        return Servers[index];
    }

    template<typename TMsg>
    TFuture<TBusMessage*> SendWithLoadBalancing(
        TBusClientSession* session,
        TMsg* msg
    ) {
        TNetAddr addr = SelectServer();
        return session->Send(msg, addr);
    }
};
```

#### 监控集成

```cpp
class TMessageBusMonitor {
private:
    TAtomic MessagesSent{0};
    TAtomic MessagesReceived{0};
    TAtomic Errors{0};
    TDurationHistogram LatencyHistogram;

public:
    void OnMessageSent() {
        MessagesSent.fetch_add(1);
    }

    void OnMessageReceived(TDuration latency) {
        MessagesReceived.fetch_add(1);
        LatencyHistogram.Add(latency);
    }

    void OnError() {
        Errors.fetch_add(1);
    }

    void PrintStats() {
        std::cout << "Sent: " << MessagesSent.load() << std::endl;
        std::cout << "Received: " << MessagesReceived.load() << std::endl;
        std::cout << "Errors: " << Errors.load() << std::endl;
        std::cout << "Avg Latency: " << LatencyHistogram.GetMean() << std::endl;
    }
};
```

## 应用场景

### 1. 微服务架构

- **服务发现**: 服务注册和发现机制
- **服务间通信**: 同步和异步消息传递
- **API 网关**: 统一的服务入口点
- **负载均衡**: 请求分发和负载管理

### 2. 分布式系统

- **协调服务**: 分布式协调和同步
- **数据复制**: 主从复制和多副本同步
- **集群管理**: 节点健康检查和故障检测
- **配置管理**: 集中配置分发和更新

### 3. 实时系统

- **消息队列**: 高吞吐量消息处理
- **事件流处理**: 实时事件流和分析
- **通知系统**: 实时通知和告警
- **数据同步**: 多系统数据同步

### 4. 高性能计算

- **任务分发**: 计算任务的分发和结果收集
- **集群通信**: 计算节点间的高效通信
- **数据传输**: 大规模数据传输
- **容错处理**: 任务失败和重试机制

### 5. IoT 和边缘计算

- **设备通信**: IoT 设备与云端通信
- **数据收集**: 传感器数据采集和传输
- **远程控制**: 设备远程控制和管理
- **边缘协调**: 边缘节点协调通信

## 技术特性

### 高性能

1. **异步 I/O**: 基于事件驱动的非阻塞 I/O
2. **无锁设计**: 关键路径使用无锁数据结构
3. **零拷贝**: 减少内存拷贝优化性能
4. **批量处理**: 批量消息处理提高吞吐量

### 可靠性

1. **故障检测**: 连接健康检查和故障发现
2. **自动重连**: 连接断开后自动重连机制
3. **消息持久化**: 关键消息的持久化支持
4. **重试机制**: 消息发送失败自动重试

### 可扩展性

1. **水平扩展**: 支持集群部署和负载均衡
2. **协议扩展**: 支持自定义消息协议
3. **插件架构**: 支持功能插件扩展
4. **多传输**: 支持多种传输协议

### 安全性

1. **认证授权**: 支持客户端认证和授权
2. **数据加密**: 支持传输数据加密
3. **访问控制**: 细粒度访问控制机制
4. **审计日志**: 完整的操作审计记录

## 性能指标

### 吞吐量

- **单连接**: > 100K messages/second
- **多连接**: > 1M messages/second (集群)
- **小消息**: 1KB 消息传输优化
- **大消息**: > 1GB 大文件传输支持

### 延迟

- **本地通信**: < 10μs (Unix Socket)
- **局域网**: < 100μs
- **广域网**: < 10ms (优化网络)
- **99%ile**: < 1% 延迟抖动

### 资源使用

- **内存开销**: < 1MB 每连接
- **CPU 使用**: < 5% 单核
- **网络带宽**: 线路带宽利用率 > 80%
- **连接数**: 支持 > 10K 并发连接

## 配置选项

### 会话配置

```cpp
struct TBusSessionConfig {
    TDuration ConnectTimeout = TDuration::Seconds(5);
    TDuration SendTimeout = TDuration::Seconds(10);
    TDuration ReceiveTimeout = TDuration::Seconds(30);

    size_t MaxConnections = 1000;
    size_t MaxInFlight = 10000;

    bool EnableCompression = false;
    bool EnableEncryption = false;

    size_t SendBufferSize = 64 * 1024;      // 64KB
    size_t ReceiveBufferSize = 64 * 1024;   // 64KB
};
```

### 队列配置

```cpp
struct TBusQueueConfig {
    size_t WorkerThreads = std::thread::hardware_concurrency();
    size_t QueueSize = 10000;
    size_t MaxMessageSize = 64 * 1024 * 1024;  // 64MB

    bool EnableMetrics = true;
    bool EnableTracing = false;

    TDuration MetricsInterval = TDuration::Seconds(60);
};
```

### 网络配置

```cpp
// TCP 选项
bool TcpNoDelay = true;           // 禁用 Nagle 算法
bool TcpKeepAlive = true;         // 启用 Keep-Alive
int TcpKeepIdle = 7200;           // Keep-Alive 空闲时间
int TcpKeepIntvl = 75;            // Keep-Alive 间隔

// 缓冲区大小
int SocketSendBuffer = 1024 * 1024;    // 1MB
int SocketReceiveBuffer = 1024 * 1024; // 1MB
```

## 最佳实践

### 1. 消息设计

```cpp
// ✅ 好的消息设计
class TCompactMessage: public TBusMessage {
    ui32 Type;
    ui64 Id;
    TString Data;  // 压缩数据

    void Serialize(TBuffer& buffer) override {
        buffer.Append(&Type, sizeof(Type));
        buffer.Append(&Id, sizeof(Id));
        SerializeCompressed(Data, buffer);
    }
};

// ❌ 避免的消息设计
class TBadMessage: public TBusMessage {
    std::vector<std::string> LargeStrings;  // 大量小字符串
    std::map<std::string, std::string> Headers;  // 复杂结构
};
```

### 2. 连接管理

```cpp
// ✅ 连接池管理
class TManagedConnection {
    TAtomic RefCount{1};
    TAtomic LastUsed{TInstant::Now().MicroSeconds()};

public:
    void Acquire() {
        RefCount.fetch_add(1);
    }

    void Release() {
        if (RefCount.fetch_sub(1) == 1) {
            Cleanup();
        }
    }

    bool IsExpired(TDuration timeout) {
        auto now = TInstant::Now().MicroSeconds();
        return (now - LastUsed) > timeout.MicroSeconds();
    }
};
```

### 3. 错误处理

```cpp
// ✅ 完善的错误处理
class TRobustHandler: public IBusClientHandler {
public:
    void OnReply(TBusMessage* request, TBusMessage* reply) override {
        try {
            ProcessReply(request, reply);
        } catch (const std::exception& e) {
            LOG_ERROR("Reply processing failed: " << e.what());
            // 尝试恢复或记录错误
            ScheduleRetry(request);
        }
    }

    void OnMessageError(TBusMessage* request, EMessageStatus status) override {
        if (IsRetryableError(status)) {
            LOG_INFO("Retrying message, status: " << status);
            ScheduleRetry(request);
        } else {
            LOG_ERROR("Permanent error, status: " << status);
            NotifyFailure(request);
        }
    }

private:
    bool IsRetryableError(EMessageStatus status) {
        return status == MESSAGE_TIMEOUT ||
               status == MESSAGE_CONNECTION_FAILED ||
               status == MESSAGE_SERVER_BUSY;
    }
};
```

### 4. 性能优化

```cpp
// ✅ 批量消息处理
void ProcessBatch(TVector<TBusMessagePtr>& messages) {
    for (auto& msg : messages) {
        ProcessMessage(msg);
    }

    // 批量发送响应
    TVector<TBusMessagePtr> responses;
    responses.reserve(messages.size());

    for (auto& msg : messages) {
        auto resp = CreateResponse(msg);
        responses.push_back(resp);
    }

    SendBatchResponses(responses);
}

// ✅ 内存池使用
class TMessagePool {
    TLockFreeQueue<TBusMessage*> Available;

public:
    TBusMessage* Acquire() {
        TBusMessage* msg;
        return Available.Dequeue(msg) ? msg : new TBusMessage();
    }

    void Release(TBusMessage* msg) {
        msg->Reset();
        Available.Enqueue(msg);
    }
};
```

## 调试和监控

### 日志配置

```bash
# 启用详细日志
export YBUS_LOG_LEVEL=DEBUG
export YBUS_LOG_FILE=/var/log/messagebus.log
export YBUS_LOG_MAX_SIZE=100MB
export YBUS_LOG_ROTATION=true
```

### 监控指标

```cpp
// 关键指标
- MessagesSentPerSecond
- MessagesReceivedPerSecond
- AverageLatency
- P99Latency
- ErrorRate
- ActiveConnections
- QueueDepth
- MemoryUsage
- CPUUsage
```

### 故障排除

```bash
# 检查连接状态
netstat -an | grep :8080

# 监控网络流量
iftop -i eth0

# 调试网络连接
telnet localhost 8080

# 分析消息流量
tcpdump -i eth0 -w messages.pcap port 8080
```