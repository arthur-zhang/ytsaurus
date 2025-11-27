# YTWalk - YTsaurus 目录遍历库

## 概述

`ytwalk` 包提供了 YTsaurus Cypress 文件系统的高效遍历功能。该库支持递归遍历目录结构、节点属性获取、自定义过滤和回调处理等功能，适用于大规模文件系统的探索和处理。

## 核心概念

### Walk 配置

```go
type Walk struct {
    // 根目录 - 遍历的起始路径
    Root ypath.Path

    // 要请求的节点属性列表
    Attributes []string

    // 可选指针，用于存储反序列化的 Cypress 节点
    Node any

    // 为每个遍历到的节点调用的回调函数
    OnNode func(path ypath.Path, node any) error

    // 是否在不透明节点处停止遍历
    RespectOpaque bool
}
```

### 特殊错误

```go
// ErrSkipSubtree 是从 OnNode 返回的哨兵值，用于跳过子树的遍历
var ErrSkipSubtree = errors.New("skip subtree")
```

## 主要 API

### 遍历函数

```go
// 执行目录遍历
func Do(ctx context.Context, yc yt.Client, w *Walk) error
```

## 使用示例

### 基本目录遍历

```go
package main

import (
    "context"
    "fmt"
    "go.ytsaurus.tech/yt/go/ytwalk"
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

    // 配置遍历
    walk := &ytwalk.Walk{
        Root: ypath.Path("//tmp"), // 从 //tmp 开始遍历
        OnNode: func(path ypath.Path, node any) error {
            fmt.Printf("访问节点: %s\n", path)
            return nil
        },
    }

    // 执行遍历
    err = ytwalk.Do(ctx, client, walk)
    if err != nil {
        panic(err)
    }
}
```

### 带属性的遍历

```go
package main

import (
    "context"
    "fmt"
    "time"
    "go.ytsaurus.tech/yt/go/ytwalk"
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

    // 定义节点结构
    type NodeInfo struct {
        Type         string    `yson:"type"`
        CreationTime time.Time `yson:"creation_time"`
        ModificationTime time.Time `yson:"modification_time"`
        Size         int64     `yson:"size,omitempty"`
    }

    // 配置带属性的遍历
    walk := &ytwalk.Walk{
        Root: ypath.Path("//home"),
        Attributes: []string{
            "type",
            "creation_time",
            "modification_time",
            "size",
        },
        Node: &NodeInfo{}, // 用于存储反序列化的节点信息
        OnNode: func(path ypath.Path, node any) error {
            if info, ok := node.(*NodeInfo); ok {
                fmt.Printf("路径: %s\n", path)
                fmt.Printf("  类型: %s\n", info.Type)
                fmt.Printf("  创建时间: %s\n", info.CreationTime)
                fmt.Printf("  修改时间: %s\n", info.ModificationTime)
                if info.Size > 0 {
                    fmt.Printf("  大小: %d bytes\n", info.Size)
                }
                fmt.Println()
            }
            return nil
        },
    }

    err = ytwalk.Do(ctx, client, walk)
    if err != nil {
        panic(err)
    }
}
```

### 过滤特定类型的节点

```go
package main

import (
    "context"
    "fmt"
    "strings"
    "go.ytsaurus.tech/yt/go/ytwalk"
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

    // 只查找表格节点
    walk := &ytwalk.Walk{
        Root: ypath.Path("//tmp"),
        Attributes: []string{"type"},
        OnNode: func(path ypath.Path, node any) error {
            // 假设我们有一个简单的结构来存储类型信息
            var nodeInfo struct {
                Type string `yson:"type"`
            }

            // 重新获取节点信息（简化示例）
            err := client.GetNode(ctx, path, &nodeInfo, &yt.GetNodeOptions{
                Attributes: []string{"type"},
            })
            if err != nil {
                return err
            }

            if nodeInfo.Type == "table" {
                fmt.Printf("找到表格: %s\n", path)
            }
            return nil
        },
    }

    err = ytwalk.Do(ctx, client, walk)
    if err != nil {
        panic(err)
    }
}
```

### 跳过子树遍历

```go
package main

import (
    "context"
    "fmt"
    "strings"
    "go.ytsaurus.tech/yt/go/ytwalk"
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

    walk := &ytwalk.Walk{
        Root: ypath.Path("//tmp"),
        OnNode: func(path ypath.Path, node any) error {
            fmt.Printf("访问: %s\n", path)

            // 如果路径包含 "skip"，跳过该子树
            if strings.Contains(path.String(), "skip") {
                fmt.Printf("  -> 跳过子树: %s\n", path)
                return ytwalk.ErrSkipSubtree
            }

            return nil
        },
    }

    err = ytwalk.Do(ctx, client, walk)
    if err != nil {
        panic(err)
    }
}
```

### 统计文件系统信息

```go
package main

import (
    "context"
    "fmt"
    "sync/atomic"
    "go.ytsaurus.tech/yt/go/ytwalk"
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

    var (
        totalNodes   int64
        fileCount    int64
        directoryCount int64
        tableCount   int64
    )

    walk := &ytwalk.Walk{
        Root: ypath.Path("//tmp"),
        Attributes: []string{"type"},
        OnNode: func(path ypath.Path, node any) error {
            atomic.AddInt64(&totalNodes, 1)

            // 简化的类型检查（实际应用中可能需要更复杂的逻辑）
            pathStr := path.String()
            switch {
            case strings.HasSuffix(pathStr, "/"):
                atomic.AddInt64(&directoryCount, 1)
            default:
                // 这里应该实际获取节点类型
                atomic.AddInt64(&fileCount, 1)
            }

            return nil
        },
    }

    err = ytwalk.Do(ctx, client, walk)
    if err != nil {
        panic(err)
    }

    fmt.Printf("文件系统统计:\n")
    fmt.Printf("  总节点数: %d\n", totalNodes)
    fmt.Printf("  文件数: %d\n", fileCount)
    fmt.Printf("  目录数: %d\n", directoryCount)
    fmt.Printf("  表格数: %d\n", tableCount)
}
```

### 查找特定模式的文件

```go
package main

import (
    "context"
    "fmt"
    "regexp"
    "strings"
    "go.ytsaurus.tech/yt/go/ytwalk"
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

    // 查找日志文件
    logPattern := regexp.MustCompile(`.*\.log$`)
    var logFiles []string

    walk := &ytwalk.Walk{
        Root: ypath.Path("//tmp/logs"),
        OnNode: func(path ypath.Path, node any) error {
            pathStr := path.String()

            if logPattern.MatchString(pathStr) {
                fmt.Printf("找到日志文件: %s\n", path)
                logFiles = append(logFiles, pathStr)
            }
            return nil
        },
    }

    err = ytwalk.Do(ctx, client, walk)
    if err != nil {
        panic(err)
    }

    fmt.Printf("\n找到 %d 个日志文件:\n", len(logFiles))
    for _, file := range logFiles {
        fmt.Printf("  %s\n", file)
    }
}
```

### 尊重不透明节点

```go
package main

import (
    "context"
    "fmt"
    "go.ytsaurus.tech/yt/go/ytwalk"
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

    walk := &ytwalk.Walk{
        Root: ypath.Path("//tmp"),
        Attributes: []string{"opaque"},
        RespectOpaque: true, // 尊重不透明节点
        OnNode: func(path ypath.Path, node any) error {
            fmt.Printf("访问节点: %s\n", path)

            // 这里可以检查节点是否不透明
            // 并采取相应的处理策略
            return nil
        },
    }

    err = ytwalk.Do(ctx, client, walk)
    if err != nil {
        panic(err)
    }
}
```

## 高级功能

### 自定义节点类型处理

```go
package main

import (
    "context"
    "fmt"
    "time"
    "go.ytsaurus.tech/yt/go/ytwalk"
    "go.ytsaurus.tech/yt/go/ypath"
    "go.ytsaurus.tech/yt/go/yt"
)

type FileSystemNode struct {
    Type         string            `yson:"type"`
    CreationTime time.Time         `yson:"creation_time"`
    ModificationTime time.Time     `yson:"modification_time"`
    Size         int64             `yson:"size,omitempty"`
    Attributes   map[string]interface{} `yson:",attrs"`
}

func walkWithCustomTypes(ctx context.Context, client yt.Client, root ypath.Path) error {
    walk := &ytwalk.Walk{
        Root: root,
        Attributes: []string{
            "type", "creation_time", "modification_time",
            "size", "account", "owner",
        },
        Node: &FileSystemNode{},
        OnNode: func(path ypath.Path, node any) error {
            if fsNode, ok := node.(*FileSystemNode); ok {
                switch fsNode.Type {
                case "table":
                    fmt.Printf("表格: %s (所有者: %s)\n", path, fsNode.Attributes["owner"])
                case "file":
                    fmt.Printf("文件: %s (大小: %d bytes)\n", path, fsNode.Size)
                case "map":
                    fmt.Printf("目录: %s\n", path)
                default:
                    fmt.Printf("未知类型: %s (%s)\n", path, fsNode.Type)
                }
            }
            return nil
        },
    }

    return ytwalk.Do(ctx, client, walk)
}
```

### 并行处理

```go
package main

import (
    "context"
    "fmt"
    "sync"
    "go.ytsaurus.tech/yt/go/ytwalk"
    "go.ytsaurus.tech/yt/go/ypath"
    "go.ytsaurus.tech/yt/go/yt"
)

func parallelProcess(ctx context.Context, client yt.Client, root ypath.Path, workers int) error {
    var (
        nodeChan = make(chan ypath.Path, 100)
        wg       sync.WaitGroup
        errChan  = make(chan error, 1)
    )

    // 启动 worker
    for i := 0; i < workers; i++ {
        wg.Add(1)
        go func(workerID int) {
            defer wg.Done()

            for path := range nodeChan {
                // 处理节点
                fmt.Printf("Worker %d 处理: %s\n", workerID, path)

                // 这里可以添加具体的处理逻辑
                // 比如获取节点属性、处理文件内容等
            }
        }(i)
    }

    // 遍历并分发节点
    walk := &ytwalk.Walk{
        Root: root,
        OnNode: func(path ypath.Path, node any) error {
            select {
            case nodeChan <- path:
                return nil
            case <-ctx.Done():
                return ctx.Err()
            }
        },
    }

    // 在单独的 goroutine 中运行遍历
    go func() {
        defer close(nodeChan)
        if err := ytwalk.Do(ctx, client, walk); err != nil {
            select {
            case errChan <- err:
            default:
            }
        }
    }()

    // 等待完成
    go func() {
        wg.Wait()
        close(errChan)
    }()

    return <-errChan
}
```

### 条件遍历

```go
package main

import (
    "context"
    "fmt"
    "strings"
    "time"
    "go.ytsaurus.tech/yt/go/ytwalk"
    "go.ytsaurus.tech/yt/go/ypath"
    "go.ytsaurus.tech/yt/go/yt"
)

func conditionalWalk(ctx context.Context, client yt.Client) error {
    var oldFiles []string
    cutoffTime := time.Now().AddDate(0, -1, 0) // 一个月前

    walk := &ytwalk.Walk{
        Root: ypath.Path("//tmp/old_data"),
        Attributes: []string{"type", "modification_time"},
        OnNode: func(path ypath.Path, node any) error {
            // 简化示例：检查路径中是否包含时间信息
            pathStr := path.String()

            // 如果路径包含 "temp"，跳过
            if strings.Contains(pathStr, "temp") {
                return ytwalk.ErrSkipSubtree
            }

            // 如果是旧文件，记录到列表中
            if strings.Contains(pathStr, "old") ||
               strings.Contains(pathStr, "backup") {
                fmt.Printf("找到可能的旧文件: %s\n", path)
                oldFiles = append(oldFiles, pathStr)
            }

            return nil
        },
    }

    err := ytwalk.Do(ctx, client, walk)
    if err != nil {
        return err
    }

    fmt.Printf("\n找到 %d 个可能的旧文件:\n", len(oldFiles))
    for _, file := range oldFiles {
        fmt.Printf("  %s\n", file)
    }

    return nil
}
```

## 性能优化

### 批量属性获取

```go
package main

import (
    "context"
    "fmt"
    "go.ytsaurus.tech/yt/go/ytwalk"
    "go.ytsaurus.tech/yt/go/ypath"
    "go.ytsaurus.tech/yt/go/yt"
)

func optimizedWalk(ctx context.Context, client yt.Client, root ypath.Path) error {
    // 请求所有需要的属性，避免多次请求
    walk := &ytwalk.Walk{
        Root: root,
        Attributes: []string{
            "type", "size", "creation_time", "modification_time",
            "account", "owner", "compression_codec", "erasure_codec",
        },
        OnNode: func(path ypath.Path, node any) error {
            // 一次性获取所有属性信息
            // 避免额外的网络请求
            fmt.Printf("处理节点: %s\n", path)
            return nil
        },
    }

    return ytwalk.Do(ctx, client, walk)
}
```

### 分层遍历

```go
package main

import (
    "context"
    "fmt"
    "go.ytsaurus.tech/yt/go/ytwalk"
    "go.ytsaurus.tech/yt/go/ypath"
    "go.ytsaurus.tech/yt/go/yt"
)

func layeredWalk(ctx context.Context, client yt.Client) error {
    layers := []ypath.Path{
        ypath.Path("//tmp/layer1"),
        ypath.Path("//tmp/layer2"),
        ypath.Path("//tmp/layer3"),
    }

    for _, layer := range layers {
        fmt.Printf("遍历层: %s\n", layer)

        walk := &ytwalk.Walk{
            Root: layer,
            OnNode: func(path ypath.Path, node any) error {
                fmt.Printf("  节点: %s\n", path)
                return nil
            },
        }

        if err := ytwalk.Do(ctx, client, walk); err != nil {
            return fmt.Errorf("遍历层 %s 失败: %w", layer, err)
        }
    }

    return nil
}
```

## 最佳实践

### 1. 错误处理

```go
// 推荐：处理遍历错误
err := ytwalk.Do(ctx, client, walk)
if err != nil {
    return fmt.Errorf("目录遍历失败: %w", err)
}

// 推荐：在回调中处理错误
walk.OnNode = func(path ypath.Path, node any) error {
    if shouldSkip(path) {
        return ytwalk.ErrSkipSubtree
    }

    if err := processNode(path, node); err != nil {
        // 记录错误但继续处理其他节点
        fmt.Printf("处理节点 %s 失败: %v\n", path, err)
        return nil // 继续遍历
    }

    return nil
}
```

### 2. 资源管理

```go
// 推荐：使用带超时的上下文
ctx, cancel := context.WithTimeout(context.Background(), 30*time.Minute)
defer cancel()

err := ytwalk.Do(ctx, client, walk)
```

### 3. 性能考虑

```go
// 推荐：批量请求属性
walk.Attributes = []string{
    "type", "size", "creation_time", "modification_time",
}

// 推荐：避免在回调中进行重量操作
walk.OnNode = func(path ypath.Path, node any) error {
    // 轻量处理
    results <- path
    return nil
}

// 在其他 goroutine 中处理结果
go processResults(results)
```

## 注意事项

1. **网络请求**：遍历会产生大量网络请求，注意性能影响
2. **内存使用**：大规模遍历可能消耗大量内存
3. **权限检查**：确保有足够的权限访问目标路径
4. **并发控制**：避免同时运行多个大型遍历操作
5. **错误恢复**：实现适当的错误处理和恢复机制

## 相关依赖

- `go.ytsaurus.tech/yt/go/yt`: YTsaurus 客户端
- `go.ytsaurus.tech/yt/go/ypath`: 路径处理
- `go.ytsaurus.tech/yt/go/yson`: YSON 序列化

## 更多信息

详细的 Cypress 文件系统说明请参考 [YTsaurus 文档](https://ytsaurus.tech/docs/en/user-guide/storage/cypress)。