# Netliba 网络库

## 项目概述

Netliba 是一个高性能的网络通信库，专门为分布式系统设计。该库提供了基于 UDP 的可靠传输协议和 InfiniBand RDMA 支持，具有极低的延迟和极高的吞吐量。

### 核心功能
- **UDP 可靠传输**：提供类似 TCP 的可靠性保证，但保持 UDP 的低延迟特性
- **InfiniBand 支持**：利用 RDMA 技术实现零拷贝数据传输
- **HTTP over UDP**：在 UDP 协议之上实现 HTTP 语义
- **多平台兼容**：支持 Linux、Windows 等多个平台
- **高性能网络 I/O**：优化的套接字操作和缓冲区管理

## 目录结构

### socket/ 目录
基础的套接字抽象层，提供跨平台的网络接口。

#### 主要文件
- **socket.h/socket.cpp** - 套接字抽象和跨平台兼容性
- **allocator.h** - 内存分配器接口
- **protocols.h** - 协议定义和常量
- **creators.cpp** - 套接字创建工具
- **udp_recv_packet.h** - UDP 数据包接收接口
- **packet_queue.h** - 数据包队列管理

### v6/ 目录
Netliba 的核心实现，包含主要的网络协议和功能。

#### 主要文件
- **udp_client_server.h/udp_client_server.cpp** - UDP 客户端/服务器实现
- **udp_socket.h/udp_socket.cpp** - UDP 套接字封装
- **udp_address.h/udp_address.cpp** - 网络地址抽象
- **udp_http.h/udp_http.cpp** - HTTP over UDP 协议实现
- **net_request.h/net_request.cpp** - 网络请求处理
- **net_acks.h/net_acks.cpp** - 确认应答机制
- **net_queue_stat.h** - 网络队列统计

#### InfiniBand 支持
- **ib_low.h/ib_low.cpp** - InfiniBand 底层接口
- **ib_buffers.h/ib_buffers.cpp** - InfiniBand 缓冲区管理
- **ib_mem.h/ib_mem.cpp** - InfiniBand 内存管理
- **ib_memstream.h/ib_memstream.cpp** - InfiniBand 内存流
- **ib_collective.h/ib_collective.cpp** - InfiniBand 集体操作
- **ib_cs.h/ib_cs.cpp** - InfiniBand 客户端/服务器

#### 测试和调试
- **udp_test.h/udp_test.cpp** - UDP 协议测试
- **net_test.h/net_test.cpp** - 网络功能测试
- **ib_test.h/ib_test.cpp** - InfiniBand 功能测试
- **udp_debug.h/udp_debug.cpp** - UDP 调试工具

#### 系统集成
- **cpu_affinity.h/cpu_affinity.cpp** - CPU 亲和性管理
- **block_chain.h/block_chain.cpp** - 数据块链管理

## 使用示例

### UDP 客户端示例
```cpp
#include <library/cpp/netliba/v6/udp_client_server.h>
#include <library/cpp/netliba/v6/udp_address.h>

using namespace NNetliba;

// 创建 UDP 主机
TAutoPtr<IUdpHost> host = CreateUdpHost();

// 解析目标地址
TUdpAddress targetAddr;
ResolveUdpAddress("example.com", 8080, &targetAddr);

// 创建数据包
TAutoPtr<TRopeDataPacket> packet = new TRopeDataPacket();
packet->Append("Hello World");

// 发送数据
int transferId = host->Send(targetAddr, packet, ComputeCrc32(packet), nullptr, PP_NORMAL);

// 处理响应
TSendResult result;
if (host->GetSendResult(&result) && result.Success) {
    printf("Data sent successfully, transfer id: %d\n", result.TransferId);
}
```

### HTTP over UDP 服务器示例
```cpp
#include <library/cpp/netliba/v6/udp_http.h>

using namespace NNetliba;

// 创建 HTTP 服务器
TAutoPtr<TUdpHttpServer> server = CreateUdpHttpServer(8080);

// 设置请求处理器
auto handler = [](const TUdpHttpRequest& req) -> TUdpHttpResponse {
    TUdpHttpResponse response;
    response.Result = TUdpHttpResponse::OK;
    response.Data = "HTTP/1.1 200 OK\r\n\r\nHello UDP Client!";
    return response;
};

// 启动服务器
server->SetRequestHandler(handler);
server->Start();

// 事件循环
while (true) {
    server->Step();
    usleep(1000); // 1ms
}
```

### InfiniBand 客户端示例
```cpp
#include <library/cpp/netliba/v6/ib_low.h>
#include <library/cpp/netliba/v6/udp_address.h>

using namespace NNetliba;

// 检查 InfiniBand 支持
if (IsInfiniBandAvailable()) {
    // 创建 InfiniBand 上下文
    TAutoPtr<TIBContext> ibContext = CreateIBContext();

    // 注册内存区域
    TIBMemoryRegion* memRegion = ibContext->RegisterMemoryRegion(
        dataBuffer, bufferSize,
        IBV_ACCESS_LOCAL_WRITE | IBV_ACCESS_REMOTE_WRITE
    );

    // 执行 RDMA 写操作
    PerformRDMAWrite(remoteAddr, memRegion, offset, size);
}
```

## 实现原理

### UDP 可靠传输协议
Netliba 在 UDP 基础上实现了类似 TCP 的可靠性机制：

#### 可靠性保证
- **序列号**：每个数据包分配唯一的序列号
- **确认应答**：接收方确认成功接收的数据包
- **重传机制**：未确认的数据包会被重传
- **流量控制**：基于窗口的流量控制算法
- **拥塞控制**：自适应拥塞窗口调整

#### 性能优化
- **批量确认**：合并多个 ACK 包减少网络开销
- **快速重传**：快速检测和恢复丢包
- **选择性重传**：只重传丢失的数据包

### InfiniBand RDMA 集成
#### 零拷贝传输
- **内存注册**：将应用内存注册为 RDMA 可访问
- **直接内存访问**：绕过操作系统内核直接访问远程内存
- **异步操作**：非阻塞的 RDMA 读写操作

####  verbs 接口
- **Queue Pairs (QP)**：建立通信端点对
- **Completion Queues (CQ)**：异步操作完成通知
- **Work Requests (WR)**：描述要执行的操作

### HTTP over UDP
#### 协议设计
- **请求映射**：将 HTTP 请求映射到 UDP 数据包
- **响应处理**：处理 HTTP 响应并映射回 UDP 包
- **错误处理**：处理网络错误和协议错误

#### 性能优化
- **连接复用**：避免 TCP 连接建立开销
- **流水线处理**：并行处理多个请求
- **压缩传输**：支持数据压缩减少传输量

### 多线程架构
#### 线程模型
- **I/O 线程**：专门处理网络 I/O 操作
- **工作线程**：处理业务逻辑和协议解析
- **统计线程**：收集和报告性能统计

#### 线程安全
- **无锁队列**：使用原子操作的线程安全队列
- **内存屏障**：确保内存访问顺序
- **CPU 亲和性**：绑定线程到特定 CPU 核心

## 应用场景

### 高性能分布式计算
- **MapReduce 框架**：节点间数据传输和任务调度
- **分布式数据库**：数据分片和复制
- **流式处理**：实时数据流处理系统

### 高频交易系统
- **低延迟通信**：微秒级延迟要求
- **高频数据交换**：市场数据和交易指令
- **实时风控**：实时风险评估和控制

### 大数据传输
- **海量数据同步**：数据中心间数据同步
- **备份和恢复**：高速数据备份
- **内容分发**：CDN 内容分发网络

### 科学计算
- **集群计算**：MPI 替代方案
- **数值模拟**：大规模数值计算
- **数据采集**：高速数据采集系统

## 性能特性

### 延迟性能
- **微秒级延迟**：单程延迟 < 100μs
- **Jitter 控制**：延迟抖动 < 10μs
- **实时响应**：确定性延迟保证

### 吞吐量性能
- **线速传输**：可达网络带宽上限
- **多核扩展**：线性扩展到多个 CPU 核心
- **RDMA 加速**：InfiniBand 下可达 100Gbps+

### 资源效率
- **CPU 利用率低**：优化的系统调用和内存访问
- **内存效率高**：零拷贝和内存池技术
- **网络效率高**：智能的数据包合并和批处理

## 配置参数

### UDP 协议配置
```cpp
// 最大包大小
const ui64 MAX_PACKET_SIZE = 0x70000000;

// 包优先级
enum EPacketPriority {
    PP_LOW,      // 低优先级
    PP_NORMAL,   // 普通优先级
    PP_HIGH      // 高优先级
};

// 发送结果
struct TSendResult {
    int TransferId;  // 传输 ID
    bool Success;    // 是否成功
};
```

### InfiniBand 配置
```cpp
// 最大 Scatter-Gather 元素数量
const int MAX_SGE = 1;

// 最大内联数据大小
const size_t MAX_INLINE_DATA_SIZE = 16;

// 最大未完成 RDMA 操作数
const int MAX_OUTSTANDING_RDMA = 10;
```

## 系统要求

### 硬件要求
- **网络接口**：支持高速网络（10Gbps+）
- **CPU**：多核处理器（4核+推荐）
- **内存**：充足内存用于缓冲区管理
- **InfiniBand**：RDMA 网卡（可选）

### 软件要求
- **操作系统**：Linux（推荐）/ Windows
- **内核版本**：Linux 3.0+（支持 sendmmsg）
- **库依赖**：libibverbs、librdmacm（InfiniBand 支持）
- **编译器**：支持 C++11 的编译器

## 调试和监控

### 统计信息
- **网络统计**：发送/接收包数量、字节统计
- **延迟统计**：最小、最大、平均延迟
- **错误统计**：丢包率、重传次数
- **资源统计**：内存使用、连接数统计

### 调试工具
- **UDP 调试器**：详细的 UDP 包分析
- **网络测试**：连通性和性能测试
- **内存分析**：内存使用和泄漏检测
- **性能分析**：CPU 和网络性能分析