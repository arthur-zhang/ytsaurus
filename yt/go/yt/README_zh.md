# YT - YTsaurus Go 客户端库

## 概述

`yt` 包是 YTsaurus 的官方 Go 客户端库，提供了与 YTsaurus 集群交互的完整功能。该库支持各种 YTsaurus 操作，包括文件操作、表格处理、事务管理、作业调度等。

## 核心架构

### 客户端接口

```go
// Client 是主要的客户端接口
type Client interface {
    // 嵌入各种子客户端接口
    CypressClient      // Cypress 节点操作
    LowLevelTxClient   // 事务操作
    LockClient         // 锁操作
    LowLevelSchedulerClient // 调度器操作
    FileClient         // 文件操作
    TableClient        // 表格操作
    AdminClient        // 管理操作
    TabletClient       // 动态表操作

    // 事务管理
    Transaction() (Tx, error)
}
```

### 事务接口

```go
// Tx 事务接口
type Tx interface {
    Client
    ID() TxID
    Commit() error
    Abort() error
    Ping() error
}
```

## 主要功能模块

### 1. Cypress 客户端

Cypress 客户端提供 YTsaurus 文件系统的基本操作：

```go
type CypressClient interface {
    // 节点操作
    CreateNode(ctx context.Context, path ypath.YPath, type NodeType, opts *CreateNodeOptions) (NodeID, error)
    CopyNode(ctx context.Context, sourcePath, destinationPath ypath.YPath, opts *CopyNodeOptions) error
    MoveNode(ctx context.Context, sourcePath, destinationPath ypath.YPath, opts *MoveNodeOptions) error
    RemoveNode(ctx context.Context, path ypath.YPath, opts *RemoveNodeOptions) error

    // 节点属性
    GetNode(ctx context.Context, path ypath.YPath, value any, opts *GetNodeOptions) error
    SetNode(ctx context.Context, path ypath.YPath, value any, opts *SetNodeOptions) error

    // 节点存在性检查
    NodeExists(ctx context.Context, path ypath.YPath, opts *NodeExistsOptions) (bool, error)

    // 目录列表
    ListNode(ctx context.Context, path ypath.YPath, opts *ListNodeOptions) ([]string, error)
}
```

#### 基本操作示例

```go
package main

import (
    "context"
    "fmt"
    "go.ytsaurus.tech/yt/go/yt"
    "go.ytsaurus.tech/yt/go/ypath"
)

func main() {
    // 创建客户端
    client, err := yt.NewClient(&yt.Config{
        Proxy: "hahn.yt.yandex.net",
    })
    if err != nil {
        panic(err)
    }
    defer client.Stop()

    ctx := context.Background()

    // 创建目录
    _, err = client.CreateNode(ctx, ypath.Path("//tmp/example"), yt.NodeMap, nil)
    if err != nil {
        panic(err)
    }

    // 设置属性
    err = client.SetNode(ctx, ypath.Path("//tmp/example/@description"), "示例目录", nil)
    if err != nil {
        panic(err)
    }

    // 获取属性
    var description string
    err = client.GetNode(ctx, ypath.Path("//tmp/example/@description"), &description, nil)
    if err != nil {
        panic(err)
    }

    fmt.Printf("目录描述: %s\n", description)
}
```

### 2. 表格客户端

表格客户端提供表格数据的读写操作：

```go
type TableClient interface {
    // 读取表格
    ReadTable(ctx context.Context, path ypath.YPath, opts *ReadTableOptions) (RowReader, error)
    ReadRow(ctx context.Context, path ypath.YPath, row any, opts *ReadRowOptions) error

    // 写入表格
    WriteTable(ctx context.Context, path ypath.YPath, opts *WriteTableOptions) (RowWriter, error)
    WriteRow(ctx context.Context, path ypath.YPath, row any, opts *WriteRowOptions) error

    // 表格操作
    MountTable(ctx context.Context, path ypath.YPath, opts *MountTableOptions) error
    UnmountTable(ctx context.Context, path ypath.YPath, opts *UnmountTableOptions) error
    RemountTable(ctx context.Context, path ypath.YPath, opts *RemountTableOptions) error

    // 表格统计
    GetTableInfo(ctx context.Context, path ypath.YPath, opts *GetTableInfoOptions) (*TableInfo, error)
}
```

#### 表格操作示例

```go
package main

import (
    "context"
    "fmt"
    "go.ytsaurus.tech/yt/go/yt"
    "go.ytsaurus.tech/yt/go/ypath"
    "go.ytsaurus.tech/yt/go/schema"
)

type User struct {
    ID    int64  `yson:"user_id"`
    Name  string `yson:"name"`
    Email string `yson:"email"`
}

func main() {
    client, err := yt.NewClient(&yt.Config{
        Proxy: "hahn.yt.yandex.net",
    })
    if err != nil {
        panic(err)
    }
    defer client.Stop()

    ctx := context.Background()
    tablePath := ypath.Path("//tmp/users")

    // 创建表格
    tableSchema := schema.Schema{
        Columns: []schema.Column{
            {Name: "user_id", Type: schema.TypeInt64},
            {Name: "name", Type: schema.TypeString},
            {Name: "email", Type: schema.TypeString},
        },
    }

    _, err = client.CreateNode(ctx, tablePath, yt.NodeTable, &yt.CreateNodeOptions{
        Attributes: map[string]any{"schema": tableSchema},
    })
    if err != nil {
        panic(err)
    }

    // 写入数据
    writer, err := client.WriteTable(ctx, tablePath, nil)
    if err != nil {
        panic(err)
    }

    users := []User{
        {ID: 1, Name: "Alice", Email: "alice@example.com"},
        {ID: 2, Name: "Bob", Email: "bob@example.com"},
    }

    for _, user := range users {
        if err := writer.Write(user); err != nil {
            panic(err)
        }
    }

    if err := writer.Commit(); err != nil {
        panic(err)
    }

    // 读取数据
    reader, err := client.ReadTable(ctx, tablePath, nil)
    if err != nil {
        panic(err)
    }
    defer reader.Close()

    for reader.Next() {
        var user User
        if err := reader.Scan(&user); err != nil {
            panic(err)
        }
        fmt.Printf("用户: %+v\n", user)
    }

    if err := reader.Err(); err != nil {
        panic(err)
    }
}
```

### 3. 文件客户端

文件客户端提供文件的上传下载操作：

```go
type FileClient interface {
    // 文件下载
    DownloadFile(ctx context.Context, path ypath.YPath, opts *DownloadFileOptions) (io.ReadCloser, error)
    GetFileFromCache(ctx context.Context, path ypath.YPath, opts *GetFileFromCacheOptions) (io.ReadCloser, error)

    // 文件上传
    UploadFile(ctx context.Context, path ypath.YPath, reader io.Reader, opts *UploadFileOptions) error

    // 文件信息
    GetFileFromCache(ctx context.Context, path ypath.YPath, opts *GetFileFromCacheOptions) (io.ReadCloser, error)
}
```

### 4. 事务管理

事务客户端提供分布式事务支持：

```go
type LowLevelTxClient interface {
    BeginTransaction(ctx context.Context, options *BeginTransactionOptions) (Tx, error)
    PingTransaction(ctx context.Context, txID TxID, options *PingTransactionOptions) error
    CommitTransaction(ctx context.Context, txID TxID, options *CommitTransactionOptions) error
    AbortTransaction(ctx context.Context, txID TxID, options *AbortTransactionOptions) error
    GetTransaction(ctx context.Context, txID TxID, value any, options *GetTransactionOptions) error
}
```

#### 事务操作示例

```go
package main

import (
    "context"
    "fmt"
    "go.ytsaurus.tech/yt/go/yt"
    "go.ytsaurus.tech/yt/go/ypath"
)

func main() {
    client, err := yt.NewClient(&yt.Config{
        Proxy: "hahn.yt.yandex.net",
    })
    if err != nil {
        panic(err)
    }
    defer client.Stop()

    ctx := context.Background()

    // 开始事务
    tx, err := client.BeginTransaction(ctx, &yt.BeginTransactionOptions{
        Timeout: yt.Duration(30 * time.Second),
    })
    if err != nil {
        panic(err)
    }

    // 在事务中执行操作
    err = tx.CreateNode(ctx, ypath.Path("//tmp/tx_example"), yt.NodeMap, &yt.CreateNodeOptions{
        TransactionOptions: yt.TransactionOptions{
            TransactionID: tx.ID(),
        },
    })
    if err != nil {
        tx.Abort() // 出错时中止事务
        panic(err)
    }

    // 提交事务
    if err := tx.Commit(); err != nil {
        panic(err)
    }

    fmt.Printf("事务 %s 提交成功\n", tx.ID())
}
```

### 5. 作业调度

调度器客户端提供 MapReduce 作业操作：

```go
type LowLevelSchedulerClient interface {
    // 作业操作
    StartOperation(ctx context.Context, spec any, options *StartOperationOptions) (OperationID, error)
    AbortOperation(ctx context.Context, operationID OperationID, options *AbortOperationOptions) error
    CompleteOperation(ctx context.Context, operationID OperationID, options *CompleteOperationOptions) error
    SuspendOperation(ctx context.Context, operationID OperationID, options *SuspendOperationOptions) error

    // 作业信息
    GetOperation(ctx context.Context, operationID OperationID, value any, options *GetOperationOptions) error
    ListOperations(ctx context.Context, options *ListOperationsOptions) ([]*Operation, error)

    // 作业监控
    FollowOperation(ctx context.Context, operationID OperationID, options *FollowOperationOptions) (OperationID, error)
    PollOperation(ctx context.Context, operationID OperationID, options *PollOperationOptions) (OperationID, error)
}
```

## 配置选项

### 基本配置

```go
type Config struct {
    // 代理配置
    Proxy     string // 代理地址
    RPCProxy  string // RPC 代理地址
    ProxyRole string // 代理角色

    // 认证配置
    Token     string // 认证令牌
    User      string // 用户名
    Password  string // 密码

    // 网络配置
    NetworkName string // 网络名称

    // 超时配置
    ReadTimeout  time.Duration
    WriteTimeout time.Duration

    // 重试配置
    RetryCount    int
    RetryBackoff  time.Duration

    // 日志配置
    Logger log.Structured
}
```

### 高级配置

```go
// 创建客户端
client, err := yt.NewClient(&yt.Config{
    Proxy:     "hahn.yt.yandex.net",
    Token:     "your-token",
    RPCProxy:  "rpc-proxy.yt.yandex.net",
    ProxyRole: "admin",

    ReadTimeout:  30 * time.Second,
    WriteTimeout: 60 * time.Second,
    RetryCount:   5,
    RetryBackoff: time.Second,

    Logger: logger,
})
```

## 批量操作

客户端支持批量操作以提高性能：

```go
package main

import (
    "context"
    "go.ytsaurus.tech/yt/go/yt"
    "go.ytsaurus.tech/yt/go/ypath"
)

func main() {
    client, err := yt.NewClient(&yt.Config{
        Proxy: "hahn.yt.yandex.net",
    })
    if err != nil {
        panic(err)
    }
    defer client.Stop()

    ctx := context.Background()

    // 创建批量请求
    batch := client.CreateBatch()

    // 添加多个操作到批量请求
    var result1, result2, result3 any

    batch.AddGetNode(ctx, ypath.Path("//tmp/node1/@value"), &result1, nil)
    batch.AddGetNode(ctx, ypath.Path("//tmp/node2/@value"), &result2, nil)
    batch.AddGetNode(ctx, ypath.Path("//tmp/node3/@value"), &result3, nil)

    // 执行批量请求
    if err := batch.Execute(); err != nil {
        panic(err)
    }

    // 使用结果
    fmt.Printf("结果1: %v\n", result1)
    fmt.Printf("结果2: %v\n", result2)
    fmt.Printf("结果3: %v\n", result3)
}
```

## 错误处理

### 错误类型

YTsaurus 客户端提供了详细的错误处理：

```go
// 检查特定错误代码
if yterrors.ContainsErrorCode(err, yterrors.CodeResolveError) {
    // 处理路径解析错误
}

// 检查节点是否已存在
if yterrors.ContainsAlreadyExistsError(err) {
    // 处理节点已存在错误
}

// 检查节点是否不存在
if yterrors.ContainsNotFoundError(err) {
    // 处理节点不存在错误
}
```

### 错误处理示例

```go
package main

import (
    "context"
    "fmt"
    "go.ytsaurus.tech/yt/go/yt"
    "go.ytsaurus.tech/yt/go/yterrors"
    "go.ytsaurus.tech/yt/go/ypath"
)

func safeCreateNode(client yt.Client, ctx context.Context, path ypath.YPath) error {
    err := client.CreateNode(ctx, path, yt.NodeMap, nil)
    if err != nil {
        if yterrors.ContainsAlreadyExistsError(err) {
            fmt.Printf("节点 %s 已存在\n", path)
            return nil
        }
        return fmt.Errorf("创建节点失败: %w", err)
    }
    fmt.Printf("节点 %s 创建成功\n", path)
    return nil
}
```

## 性能优化

### 连接池配置

```go
config := &yt.Config{
    Proxy: "hahn.yt.yandex.net",

    // 连接池配置
    MaxConnectionsPerHost: 100,
    MaxIdleConnections:    10,

    // 缓存配置
    EnableNodeCache: true,
    NodeCacheTTL:    5 * time.Minute,
}
```

### 并发操作

```go
// 使用 goroutine 并发执行操作
func concurrentOperations(client yt.Client, paths []ypath.YPath) {
    var wg sync.WaitGroup
    sem := make(chan struct{}, 10) // 限制并发数

    for _, path := range paths {
        wg.Add(1)
        go func(p ypath.YPath) {
            defer wg.Done()
            sem <- struct{}{}
            defer func() { <-sem }()

            err := client.GetNode(context.Background(), p, nil, nil)
            if err != nil {
                log.Printf("获取 %s 失败: %v", p, err)
            }
        }(path)
    }

    wg.Wait()
}
```

## 监控和追踪

### OpenTracing 支持

```go
import (
    "github.com/opentracing/opentracing-go"
)

// 设置 tracer
tracer := opentracing.GlobalTracer()

// 创建带追踪的客户端
client, err := yt.NewClient(&yt.Config{
    Proxy:  "hahn.yt.yandex.net",
    Tracer: tracer,
})
```

### 指标收集

```go
// 客户端会自动收集以下指标：
// - 请求计数
// - 响应时间
// - 错误率
// - 重试次数
```

## 安全认证

### 令牌认证

```go
client, err := yt.NewClient(&yt.Config{
    Proxy: "hahn.yt.yandex.net",
    Token: "your-auth-token",
})
```

### 用户名密码认证

```go
client, err := yt.NewClient(&yt.Config{
    Proxy:    "hahn.yt.yandex.net",
    User:     "username",
    Password: "password",
})
```

## 最佳实践

### 1. 客户端生命周期

```go
// 推荐：复用客户端实例
client, err := yt.NewClient(config)
if err != nil {
    panic(err)
}
defer client.Stop() // 确保资源清理

// 在应用生命周期中复用 client
```

### 2. 错误处理

```go
// 始终检查和处理错误
err := client.CreateNode(ctx, path, yt.NodeMap, nil)
if err != nil {
    // 处理特定错误类型
    if yterrors.ContainsErrorCode(err, yterrors.CodeResolveError) {
        return fmt.Errorf("路径解析错误: %w", err)
    }
    return err
}
```

### 3. 上下文管理

```go
// 使用适当的上下文
ctx, cancel := context.WithTimeout(context.Background(), 30*time.Second)
defer cancel()

err := client.GetNode(ctx, path, value, nil)
```

### 4. 批量操作

```go
// 对多个操作使用批量请求
batch := client.CreateBatch()
batch.AddGetNode(ctx, path1, &value1, nil)
batch.AddGetNode(ctx, path2, &value2, nil)
err := batch.Execute()
```

## 注意事项

1. **资源管理**：确保调用 `client.Stop()` 清理资源
2. **并发安全**：客户端是并发安全的，可以安全地在 goroutine 中使用
3. **错误重试**：客户端会自动重试瞬时错误，但要注意事务的特殊性
4. **上下文取消**：使用 context.Context 来控制操作的生命周期
5. **性能监控**：监控客户端的性能指标和错误率

## 相关包

- `go.ytsaurus.tech/yt/go/yt/ythttp`: HTTP 客户端实现
- `go.ytsaurus.tech/yt/go/yt/ytrpc`: RPC 客户端实现
- `go.ytsaurus.tech/yt/go/mapreduce`: MapReduce 客户端
- `go.ytsaurus.tech/yt/go/yt/internal`: 内部实现

## 更多信息

详细的 API 文档和使用示例请参考 [YTsaurus 官方文档](https://ytsaurus.tech/docs/)。