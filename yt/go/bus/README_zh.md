# Bus

## 概述

Bus 模块是 YTsaurus Go 客户端的核心通信组件，实现了高性能的二进制协议传输层。该模块负责处理客户端与 YTsaurus 集群之间的底层网络通信，包括消息传输、连接管理、加密支持和错误处理等功能。

## 功能特性

- **高性能通信**：基于二进制协议的高效数据传输
- **连接管理**：自动管理连接池和连接复用
- **加密支持**：支持 TLS 加密传输，确保数据安全
- **流式传输**：支持大数据的流式传输
- **可靠性保证**：实现消息确认机制和重试策略
- **压缩支持**：集成数据压缩功能，减少网络传输开销

## 核心组件

### 1. Bus 连接

```go
type Options struct {
    Address string        // 服务器地址
    Logger  log.Logger    // 日志记录器
    EncryptionMode EncryptionMode  // 加密模式
    TLSConfig      *tls.Config    // TLS 配置
}
```

### 2. 客户端连接 (ClientConn)

客户端连接是 Bus 模块的核心，提供了完整的 RPC 通信功能：

- 请求/响应处理
- 流式消息传输
- 自动重连机制
- 超时控制
- 错误处理

### 3. 消息类型

支持多种消息类型：
- `msgRequest`：请求消息
- `msgCancel`：取消请求
- `msgResponse`：响应消息
- `msgStreamPayload`：流式数据负载
- `msgStreamFeedback`：流式反馈

### 4. 数据包格式

Bus 使用定制的二进制协议格式：

```
固定头部 (36字节):
- 签名 (4字节)
- 包类型 (2字节)
- 标志位 (2字节)
- 包ID (16字节)
- 分片数量 (4字节)
- 校验和 (8字节)
```

## 使用方法

### 基本连接

```go
package main

import (
    "context"
    "log"

    "go.ytsaurus.tech/yt/go/bus"
)

func main() {
    // 创建连接选项
    opts := &bus.Options{
        Address: "localhost:9013",
    }

    // 建立连接
    conn, err := bus.NewConn(context.Background(), opts)
    if err != nil {
        log.Fatal(err)
    }
    defer conn.Close()

    // 使用连接进行通信...
}
```

### 发送请求

```go
// 发送 RPC 请求
req := &MyRequest{
    // 填充请求字段
}

rsp := &MyResponse{}

err := conn.Call(context.Background(), req, rsp)
if err != nil {
    log.Fatal(err)
}
```

### 流式传输

```go
// 创建流
stream, err := conn.NewStream(context.Background(), &MyStreamRequest{})
if err != nil {
    log.Fatal(err)
}

// 发送数据
err = stream.Send(&MyStreamPayload{
    Data: []byte("large data chunk"),
})

// 接收数据
payload := &MyStreamPayload{}
err = stream.Recv(payload)
```

## 配置选项

### 加密模式

```go
const (
    EncryptionModeDisabled EncryptionMode = 0  // 禁用加密
    EncryptionModeOptional EncryptionMode = 1  // 可选加密
    EncryptionModeRequired EncryptionMode = 2  // 必须加密
)
```

### 客户端选项

- `WithLogger`：设置自定义日志记录器
- `WithDialer`：自定义连接拨号器
- `WithHandshakeTimeout`：设置握手超时
- `WithReadTimeout`：设置读取超时
- `WithWriteTimeout`：设置写入超时

## 性能优化

### 1. 连接池

Bus 自动管理连接池，支持连接复用：
```go
// 设置最大连接数
conn := bus.NewConn(opts, bus.WithMaxConnections(100))
```

### 2. 压缩

启用数据压缩以减少网络传输：
```go
conn := bus.NewConn(opts, bus.WithCompression(true))
```

### 3. 批量发送

支持批量发送多个请求：
```go
requests := []proto.Message{req1, req2, req3}
responses, err := conn.CallBatch(context.Background(), requests)
```

## 错误处理

Bus 提供了完善的错误处理机制：

### 错误类型

- 连接错误：网络连接失败
- 超时错误：请求或响应超时
- 协议错误：协议格式或版本不匹配
- 认证错误：身份验证失败

### 错误恢复

- 自动重连：网络断开时自动重新连接
- 请求重试：临时性错误自动重试
- 熔断机制：连续失败时暂停请求

## 监控和调试

### 日志记录

Bus 支持结构化日志记录：
```go
logger := log.New()
conn := bus.NewConn(opts, bus.WithLogger(logger))
```

### 指标收集

内置性能指标：
- 连接数量
- 请求数量
- 响应时间
- 错误率

## 依赖项

- `go.ytsaurus.tech/yt/go/crc64`：CRC64 校验和计算
- `go.ytsaurus.tech/yt/go/guid`：GUID 生成和处理
- `go.ytsaurus.tech/yt/go/compression`：数据压缩
- `go.ytsaurus.tech/yt/go/proto/core/bus`：Bus 协议定义
- `go.ytsaurus.tech/library/go/core/log`：日志库

## 测试

模块包含完整的测试套件：
- 单元测试：`bus_test.go`, `client_test.go`
- 集成测试：`test_service_test.go`
- 示例代码：`example/main.go`

## 注意事项

1. **并发安全**：单个连接实例是并发安全的
2. **资源管理**：必须调用 `Close()` 释放连接资源
3. **超时设置**：合理设置请求超时，避免长时间阻塞
4. **错误处理**：始终检查返回的错误
5. **内存使用**：大文件传输时注意内存使用情况