# RateLimit 限流模块

RateLimit 是一个精确的限流器，支持上下文（Context）感知，用于控制 API 调用或其他操作的执行频率。

## 概述

该限流器实现了令牌桶算法，能够精确控制在指定时间窗口内允许的最大操作数量。它支持并发安全的操作，并提供了优雅的上下文取消机制。

## 核心特性

- **精确限流**: 在指定时间窗口内精确控制操作数量
- **上下文支持**: 支持 Go 的 `context.Context`，可以优雅地处理超时和取消
- **并发安全**: 内部使用互斥锁保证线程安全
- **高性能**: 优化的实现，支持高并发场景
- **灵活配置**: 支持配置最大操作数和时间间隔

## 核心组件

### Limiter 结构体

```go
type Limiter struct {
    maxSize  int                    // 时间窗口内允许的最大操作数
    interval time.Duration         // 时间窗口长度
    mu       sync.Mutex           // 互斥锁
    size     int                  // 当前活跃的操作数
    active, waiting waiter        // 活跃和等待的操作队列
    blocked  bool                 // 是否有唤醒调度器在运行
}
```

### 主要方法

#### NewLimiter(maxCount int, interval time.Duration) *Limiter
创建一个新的限流器实例。

**参数:**
- `maxCount`: 在时间窗口内允许的最大操作数
- `interval`: 时间窗口长度

#### Acquire(ctx context.Context) error
获取一个操作许可。如果当前已经达到限制，则会等待直到有时间窗过期或上下文被取消。

**参数:**
- `ctx`: 上下文，支持超时和取消

**返回:**
- 成功时返回 `nil`
- 上下文取消时返回 `ctx.Err()`

### ParseRate 函数

```go
func ParseRate(rate string) (count int, interval time.Duration, err error)
```

解析字符串格式的速率配置，格式为 "N/D"，如 "10/1s" 表示每秒最多 10 个操作。

**示例:**
- "100/1s" - 每秒 100 个操作
- "1000/1m" - 每分钟 1000 个操作
- "10/1ms" - 每毫秒 10 个操作

## 使用示例

### 基本用法

```go
package main

import (
    "context"
    "fmt"
    "time"

    "go.ytsaurus.com/yt/go/ratelimit"
)

func main() {
    // 创建限流器：每秒最多 10 个操作
    limiter := ratelimit.NewLimiter(10, time.Second)

    ctx := context.Background()

    for i := 0; i < 20; i++ {
        err := limiter.Acquire(ctx)
        if err != nil {
            fmt.Printf("操作 %d 失败: %v\n", i+1, err)
            break
        }
        fmt.Printf("执行操作 %d\n", i+1)
    }
}
```

### 使用 ParseRate

```go
package main

import (
    "context"
    "fmt"

    "go.ytsaurus.com/yt/go/ratelimit"
)

func main() {
    // 从字符串解析速率配置
    count, interval, err := ratelimit.ParseRate("50/1s")
    if err != nil {
        panic(err)
    }

    limiter := ratelimit.NewLimiter(count, interval)

    ctx := context.Background()
    err = limiter.Acquire(ctx)
    if err != nil {
        fmt.Printf("获取许可失败: %v\n", err)
    } else {
        fmt.Println("成功获取许可，执行操作")
    }
}
```

### 带超时的上下文

```go
package main

import (
    "context"
    "fmt"
    "time"

    "go.ytsaurus.com/yt/go/ratelimit"
)

func main() {
    limiter := ratelimit.NewLimiter(1, time.Second)

    // 使用带超时的上下文
    ctx, cancel := context.WithTimeout(context.Background(), 500*time.Millisecond)
    defer cancel()

    // 第一个操作应该成功
    err := limiter.Acquire(ctx)
    if err != nil {
        fmt.Printf("第一个操作失败: %v\n", err)
    } else {
        fmt.Println("第一个操作成功")
    }

    // 第二个操作应该因为超时而失败
    err = limiter.Acquire(ctx)
    if err != nil {
        fmt.Printf("第二个操作失败（预期）: %v\n", err)
    } else {
        fmt.Println("第二个操作成功")
    }
}
```

### 并发使用

```go
package main

import (
    "context"
    "fmt"
    "sync"
    "time"

    "go.ytsaurus.com/yt/go/ratelimit"
)

func main() {
    limiter := ratelimit.NewLimiter(10, time.Second)
    var wg sync.WaitGroup

    // 启动 100 个协程并发获取许可
    for i := 0; i < 100; i++ {
        wg.Add(1)
        go func(id int) {
            defer wg.Done()

            ctx := context.Background()
            err := limiter.Acquire(ctx)
            if err != nil {
                fmt.Printf("协程 %d 失败: %v\n", id, err)
                return
            }

            fmt.Printf("协程 %d 执行操作: %s\n", id, time.Now().Format("15:04:05"))
        }(i)
    }

    wg.Wait()
}
```

## 最佳实践

### 1. 合理配置参数
- 根据系统容量和目标性能设置合适的 `maxCount` 和 `interval`
- 避免设置过于严格的限制，以免影响系统响应性

### 2. 上下文管理
- 总是使用合适的上下文，设置合理的超时时间
- 确保在不再需要时取消上下文，避免资源泄漏

### 3. 错误处理
- 正确处理 `Acquire()` 返回的错误，特别是上下文取消错误
- 根据业务需求决定是否重试失败的操作

### 4. 性能考虑
- 限流器设计为高性能，适用于高并发场景
- 在极高频率调用时，建议进行性能测试

## 常见模式

### API 调用限流
```go
func callAPIWithRateLimit(ctx context.Context, apiFunc func() error) error {
    limiter := ratelimit.NewLimiter(100, time.Second) // 每秒最多 100 次 API 调用

    err := limiter.Acquire(ctx)
    if err != nil {
        return err
    }

    return apiFunc()
}
```

### 数据库操作限流
```go
func batchInsertWithRateLimit(ctx context.Context, records []Record) error {
    limiter := ratelimit.NewLimiter(1000, time.Minute) // 每分钟最多 1000 次插入

    for _, record := range records {
        err := limiter.Acquire(ctx)
        if err != nil {
            return err
        }

        if err := insertRecord(record); err != nil {
            return err
        }
    }

    return nil
}
```

## 注意事项

1. **零时间间隔**: 如果设置 `interval` 为 0，则限流器不进行限制
2. **零最大计数**: 如果设置 `maxCount` 为 0，则所有操作都会被阻塞
3. **内存使用**: 每个等待的操作都会分配相应的内存结构
4. **时间精度**: 限流的精度取决于系统的时间精度和调度延迟

## 性能基准

根据测试结果：
- 非阻塞场景下性能接近原生互斥锁
- 支持高并发场景，适合生产环境使用
- 内存占用合理，每个等待操作约占用几十字节

详细基准测试请参考 `ratelimit_test.go` 中的基准测试函数。