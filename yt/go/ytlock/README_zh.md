# YTLock - YTsaurus 分布式锁库

## 概述

`ytlock` 包提供了 YTsaurus 分布式锁的高级接口。分布式锁用于协调多个进程或服务对共享资源的访问，防止并发操作导致的数据不一致。

## 核心概念

### 锁类型

YTsaurus 支持多种锁模式：

```go
type LockMode string

const (
    LockModeSnapshot   LockMode = "snapshot"    // 快照锁
    LockModeShared     LockMode = "shared"      // 共享锁
    LockModeExclusive  LockMode = "exclusive"   // 排他锁
    LockModeExclusiveWrite LockMode = "exclusive_write" // 排他写锁
)
```

### 获胜事务信息

当锁竞争发生时，可以获取获胜事务的信息：

```go
type WinnerTx struct {
    ID        yt.TxID       `yson:"id"`                  // 事务ID
    Owner     string        `yson:"owner"`               // 事务所有者
    StartTime yson.Time     `yson:"start_time"`          // 开始时间
    Timeout   yson.Duration `yson:"duration"`            // 超时时间
}
```

## 主要 API

### Lock 结构体

```go
type Lock struct {
    // 内部字段
}
```

### 锁创建

```go
// 创建锁（使用默认选项）
func NewLock(yc yt.Client, path ypath.Path) *Lock

// 创建锁（使用自定义选项）
func NewLockWithOptions(yc yt.Client, path ypath.Path, opts Options) *Lock
```

### 锁操作

```go
// 获取锁
func (l *Lock) Lock(ctx context.Context) (yt.Tx, error)

// 尝试获取锁（非阻塞）
func (l *Lock) TryLock(ctx context.Context) (yt.Tx, bool, error)

// 释放锁
func (l *Lock) Unlock(tx yt.Tx) error

// 检查锁状态
func (l *Lock) IsLocked(ctx context.Context) (bool, error)
```

### 配置选项

```go
type Options struct {
    CreateIfMissing bool             // 如果路径不存在则创建
    LockMode        yt.LockMode     // 锁模式
    LockChild       string           // 锁定子节点
    TxAttributes    map[string]any  // 事务属性
}
```

### 冲突处理

```go
// 查找锁冲突的获胜者
func FindConflictWinner(err error) *WinnerTx
```

## 使用示例

### 基本锁操作

```go
package main

import (
    "context"
    "fmt"
    "time"
    "go.ytsaurus.tech/yt/go/ytlock"
    "go.ytsaurus.tech/yt/go/ypath"
    "go.ytsaurus.tech/yt/go/yt"
    "go.ytsaurus.tech/yt/go/ythttp"
)

func main() {
    // 创建客户端
    client, err := ythttp.NewClient(&yt.Config{
        Proxy: "hahn.yt.yandex.net",
    })
    if err != nil {
        panic(err)
    }
    defer client.Stop()

    ctx := context.Background()
    lockPath := ypath.Path("//tmp/my_lock")

    // 创建锁
    lock := ytlock.NewLock(client, lockPath)

    // 获取锁
    tx, err := lock.Lock(ctx)
    if err != nil {
        panic(err)
    }

    fmt.Printf("成功获取锁，事务ID: %s\n", tx.ID())

    // 执行需要保护的操作
    fmt.Println("执行关键操作...")
    time.Sleep(2 * time.Second)

    // 释放锁
    err = lock.Unlock(tx)
    if err != nil {
        panic(err)
    }

    fmt.Println("锁已释放")
}
```

### 自定义锁选项

```go
package main

import (
    "context"
    "fmt"
    "time"
    "go.ytsaurus.tech/yt/go/ytlock"
    "go.ytsaurus.tech/yt/go/ypath"
    "go.ytsaurus.tech/yt/go/yt"
    "go.ytsaurus.tech/yt/go/ythttp"
)

func main() {
    client, err := ythttp.NewClient(&yt.Config{
        Proxy: "hahn.yt.yandex.net",
    })
    if err != nil {
        panic(err)
    }
    defer client.Stop()

    ctx := context.Background()
    lockPath := ypath.Path("//tmp/resource_lock")

    // 创建带选项的锁
    opts := ytlock.Options{
        CreateIfMissing: true, // 如果锁节点不存在则创建
        LockMode:        yt.LockModeExclusive, // 排他锁
        TxAttributes: map[string]any{
            "owner":    "my-app",
            "purpose":  "resource-protection",
            "duration": "30s",
        },
    }

    lock := ytlock.NewLockWithOptions(client, lockPath, opts)

    // 获取锁
    tx, err := lock.Lock(ctx)
    if err != nil {
        panic(err)
    }

    defer lock.Unlock(tx)

    fmt.Printf("获取到排他锁，事务: %s\n", tx.ID())
    fmt.Println("执行受保护的操作...")
}
```

### 非阻塞锁获取

```go
package main

import (
    "context"
    "fmt"
    "go.ytsaurus.tech/yt/go/ytlock"
    "go.ytsaurus.tech/yt/go/ypath"
    "go.ytsaurus.tech/yt/go/yt"
    "go.ytsaurus.tech/yt/go/ythttp"
)

func main() {
    client, err := ythttp.NewClient(&yt.Config{
        Proxy: "hahn.yt.yandex.net",
    })
    if err != nil {
        panic(err)
    }
    defer client.Stop()

    ctx := context.Background()
    lockPath := ypath.Path("//tmp/nonblocking_lock")

    lock := ytlock.NewLock(client, lockPath)

    // 尝试获取锁（非阻塞）
    tx, acquired, err := lock.TryLock(ctx)
    if err != nil {
        panic(err)
    }

    if acquired {
        fmt.Printf("成功获取锁，事务: %s\n", tx.ID())
        defer lock.Unlock(tx)

        // 执行关键操作
        fmt.Println("执行操作...")
    } else {
        fmt.Println("无法获取锁，资源被占用")
    }
}
```

### 锁冲突处理

```go
package main

import (
    "context"
    "fmt"
    "go.ytsaurus.tech/yt/go/ytlock"
    "go.ytsaurus.tech/yt/go/yterrors"
    "go.ytsaurus.tech/yt/go/ypath"
    "go.ytsaurus.tech/yt/go/yt"
    "go.ytsaurus.tech/yt/go/ythttp"
)

func main() {
    client, err := ythttp.NewClient(&yt.Config{
        Proxy: "hahn.yt.yandex.net",
    })
    if err != nil {
        panic(err)
    }
    defer client.Stop()

    ctx := context.Background()
    lockPath := ypath.Path("//tmp/contended_lock")

    lock := ytlock.NewLock(client, lockPath)

    // 尝试获取锁（可能会冲突）
    tx, err := lock.Lock(ctx)
    if err != nil {
        // 检查是否为锁冲突
        if winner := ytlock.FindConflictWinner(err); winner != nil {
            fmt.Printf("锁冲突！获胜者信息:\n")
            fmt.Printf("  事务ID: %s\n", winner.ID)
            fmt.Printf("  所有者: %s\n", winner.Owner)
            fmt.Printf("  开始时间: %s\n", winner.StartTime)
            fmt.Printf("  超时: %v\n", winner.Timeout)

            // 可以选择等待或放弃
            return
        }

        // 其他类型的错误
        panic(err)
    }

    defer lock.Unlock(tx)
    fmt.Printf("成功获取锁，事务: %s\n", tx.ID())
}
```

### 共享锁示例

```go
package main

import (
    "context"
    "fmt"
    "sync"
    "time"
    "go.ytsaurus.tech/yt/go/ytlock"
    "go.ytsaurus.tech/yt/go/ypath"
    "go.ytsaurus.tech/yt/go/yt"
    "go.ytsaurus.tech/yt/go/ythttp"
)

func main() {
    client, err := ythttp.NewClient(&yt.Config{
        Proxy: "hahn.yt.yandex.net",
    })
    if err != nil {
        panic(err)
    }
    defer client.Stop()

    ctx := context.Background()
    lockPath := ypath.Path("//tmp/shared_lock")

    var wg sync.WaitGroup

    // 启动多个 goroutine，都尝试获取共享锁
    for i := 0; i < 3; i++ {
        wg.Add(1)
        go func(id int) {
            defer wg.Done()

            opts := ytlock.Options{
                LockMode: yt.LockModeShared, // 共享锁
            }

            lock := ytlock.NewLockWithOptions(client, lockPath, opts)

            tx, err := lock.Lock(ctx)
            if err != nil {
                fmt.Printf("Goroutine %d 获取锁失败: %v\n", id, err)
                return
            }

            defer lock.Unlock(tx)

            fmt.Printf("Goroutine %d 获取到共享锁，事务: %s\n", id, tx.ID())
            time.Sleep(time.Second)
            fmt.Printf("Goroutine %d 释放共享锁\n", id)
        }(i)
    }

    wg.Wait()
    fmt.Println("所有 goroutine 完成")
}
```

### 锁状态检查

```go
package main

import (
    "context"
    "fmt"
    "go.ytsaurus.tech/yt/go/ytlock"
    "go.ytsaurus.tech/yt/go/ypath"
    "go.ytsaurus.tech/yt/go/yt"
    "go.ytsaurus.tech/yt/go/ythttp"
)

func main() {
    client, err := ythttp.NewClient(&yt.Config{
        Proxy: "hahn.yt.yandex.net",
    })
    if err != nil {
        panic(err)
    }
    defer client.Stop()

    ctx := context.Background()
    lockPath := ypath.Path("//tmp/status_check_lock")

    lock := ytlock.NewLock(client, lockPath)

    // 检查锁状态
    locked, err := lock.IsLocked(ctx)
    if err != nil {
        panic(err)
    }

    if locked {
        fmt.Println("锁已被占用")
    } else {
        fmt.Println("锁可用")
    }

    // 尝试获取锁
    tx, err := lock.Lock(ctx)
    if err != nil {
        panic(err)
    }

    // 再次检查
    locked, err = lock.IsLocked(ctx)
    if err != nil {
        panic(err)
    }

    fmt.Printf("获取锁后状态: %v\n", locked)

    lock.Unlock(tx)
    fmt.Println("锁已释放")
}
```

## 高级功能

### 锁超时处理

```go
package main

import (
    "context"
    "fmt"
    "time"
    "go.ytsaurus.tech/yt/go/ytlock"
    "go.ytsaurus.tech/yt/go/ypath"
    "go.ytsaurus.tech/yt/go/yt"
    "go.ytsaurus.tech/yt/go/ythttp"
)

func main() {
    client, err := ythttp.NewClient(&yt.Config{
        Proxy: "hahn.yt.yandex.net",
    })
    if err != nil {
        panic(err)
    }
    defer client.Stop()

    ctx := context.Background()
    lockPath := ypath.Path("//tmp/timeout_lock")

    opts := ytlock.Options{
        TxAttributes: map[string]any{
            "timeout": "10s", // 设置锁超时
        },
    }

    lock := ytlock.NewLockWithOptions(client, lockPath, opts)

    // 使用带超时的上下文
    ctx, cancel := context.WithTimeout(ctx, 15*time.Second)
    defer cancel()

    tx, err := lock.Lock(ctx)
    if err != nil {
        panic(err)
    }

    fmt.Printf("获取到锁: %s\n", tx.ID())

    // 模拟长时间操作
    select {
    case <-time.After(5 * time.Second):
        fmt.Println("操作完成")
    case <-ctx.Done():
        fmt.Println("操作超时")
    }

    lock.Unlock(tx)
}
```

### 锁重试机制

```go
package main

import (
    "context"
    "fmt"
    "time"
    "go.ytsaurus.tech/yt/go/ytlock"
    "go.ytsaurus.tech/yt/go/ypath"
    "go.ytsaurus.tech/yt/go/yt"
    "go.ytsaurus.tech/yt/go/ythttp"
    "go.ytsaurus.tech/yt/go/yterrors"
)

func acquireLockWithRetry(lock *ytlock.Lock, ctx context.Context, maxRetries int) (yt.Tx, error) {
    var lastErr error

    for i := 0; i < maxRetries; i++ {
        tx, err := lock.TryLock(ctx)
        if err != nil {
            return nil, err
        }

        if tx != nil {
            return tx, nil
        }

        // 检查是否可以重试
        if lastErr != nil && !yterrors.ContainsLockConflictError(lastErr) {
            return nil, lastErr
        }

        fmt.Printf("锁被占用，等待重试 (%d/%d)...\n", i+1, maxRetries)
        time.Sleep(time.Second)
    }

    return nil, fmt.Errorf("无法获取锁，超过最大重试次数")
}

func main() {
    client, err := ythttp.NewClient(&yt.Config{
        Proxy: "hahn.yt.yandex.net",
    })
    if err != nil {
        panic(err)
    }
    defer client.Stop()

    ctx := context.Background()
    lockPath := ypath.Path("//tmp/retry_lock")

    lock := ytlock.NewLock(client, lockPath)

    // 使用重试机制获取锁
    tx, err := acquireLockWithRetry(lock, ctx, 5)
    if err != nil {
        panic(err)
    }
    defer lock.Unlock(tx)

    fmt.Printf("成功获取锁: %s\n", tx.ID())
}
```

## 最佳实践

### 1. 锁粒度选择

```go
// 推荐：使用具体的锁路径
resourceLock := ytlock.NewLock(client, ypath.Path("//tmp/resources/resource_123"))

// 不推荐：使用过于宽泛的锁路径
globalLock := ytlock.NewLock(client, ypath.Path("//tmp"))
```

### 2. 锁释放保证

```go
// 推荐：使用 defer 确保锁释放
tx, err := lock.Lock(ctx)
if err != nil {
    return err
}
defer lock.Unlock(tx) // 确保锁总是被释放

// 执行关键操作
```

### 3. 上下文管理

```go
// 推荐：使用适当的上下文超时
ctx, cancel := context.WithTimeout(context.Background(), 30*time.Second)
defer cancel()

tx, err := lock.Lock(ctx)
if err != nil {
    return err
}
```

### 4. 错误处理

```go
// 推荐：处理锁冲突
tx, err := lock.Lock(ctx)
if err != nil {
    if winner := ytlock.FindConflictWinner(err); winner != nil {
        // 处理锁冲突
        return fmt.Errorf("锁被 %s 占用", winner.Owner)
    }
    return err
}
```

### 5. 锁模式选择

```go
// 读多写少场景：使用共享锁
readLock := ytlock.NewLockWithOptions(client, path, ytlock.Options{
    LockMode: yt.LockModeShared,
})

// 写操作：使用排他锁
writeLock := ytlock.NewLockWithOptions(client, path, ytlock.Options{
    LockMode: yt.LockModeExclusive,
})
```

## 注意事项

1. **死锁预防**：确保锁总是被释放，使用 defer 语句
2. **锁粒度**：选择合适的锁粒度，避免过度锁定
3. **超时处理**：设置合理的超时时间，避免无限等待
4. **冲突处理**：正确处理锁冲突，实现适当的重试策略
5. **资源清理**：确保在异常情况下也能正确释放锁

## 相关依赖

- `go.ytsaurus.tech/yt/go/yt`: YTsaurus 客户端库
- `go.ytsaurus.tech/yt/go/ypath`: 路径处理库
- `go.ytsaurus.tech/yt/go/yterrors`: 错误处理库

## 更多信息

详细的分布式锁使用指南请参考 [YTsaurus 事务和锁文档](https://ytsaurus.tech/docs/en/user-guide/transactions)。