# BlobTable

## 概述

BlobTable 是 YTsaurus Go 客户端库中用于读取 YTsaurus blob 表的专用模块。Blob 表是 YTsaurus 中存储二进制大型对象（Blob）的特殊表结构，支持高效的大文件存储和读取。

## 功能特性

- **流式读取**：支持以流式方式读取大型二进制对象，避免内存溢出
- **分块处理**：自动处理 blob 数据的分块存储和读取
- **兼容标准接口**：实现标准的 `io.Reader` 接口，便于与其他 Go 库集成
- **错误处理**：完善的错误处理机制，确保数据读取的可靠性

## 核心组件

### BlobTableReader 接口

```go
type BlobTableReader interface {
    Next() bool           // 切换到流中的下一个 blob
    Err() error          // 返回读取器关联的错误
    ScanKey(key any) error // 读取当前行的键
    Read([]byte) (int, error) // 实现 io.Reader，读取 blob 数据
    Close() error        // 释放相关资源
}
```

### 数据结构

- **blobRow**：表示 blob 表中的单行数据
  - `PartIndex`：数据块的索引
  - `Data`：实际的数据内容

## 使用方法

### 基本用法

```go
package main

import (
    "context"
    "fmt"
    "io"

    "go.ytsaurus.tech/yt/go/blobtable"
    "go.ytsaurus.tech/yt/go/ypath"
    "go.ytsaurus.tech/yt/go/yt"
)

func main() {
    var yc yt.TableClient
    ctx := context.Background()

    // 打开 blob 表
    reader, err := blobtable.ReadBlobTable(ctx, yc, ypath.Path("//path/to/blob_table"))
    if err != nil {
        panic(err)
    }
    defer reader.Close()

    // 遍历所有 blob
    for reader.Next() {
        var key string
        if err := reader.ScanKey(&key); err != nil {
            panic(err)
        }

        // 读取 blob 数据
        data, err := io.ReadAll(reader)
        if err != nil {
            panic(err)
        }

        fmt.Printf("Blob %s: %d bytes\n", key, len(data))
    }

    if err := reader.Err(); err != nil {
        panic(err)
    }
}
```

## 实现原理

### 读取机制

1. **初始化**：创建 `blobTableReader`，关联 YTsaurus 表读取器
2. **分块读取**：自动处理 `PartIndex`，确保数据块的顺序正确
3. **流式传输**：通过 `Read` 方法实现流式数据读取
4. **状态管理**：维护读取状态，包括当前块位置和数据偏移

### 错误处理

- 检测并报告不连续的数据块索引
- 提供详细的错误信息，便于调试
- 确保资源正确释放

## 依赖项

- `go.ytsaurus.tech/yt/go/ypath`：YTsaurus 路径处理
- `go.ytsaurus.tech/yt/go/yt`：YTsaurus Go 客户端核心库

## 测试

模块包含完整的测试套件：
- `blob_table_test.go`：核心功能测试
- `example_test.go`：使用示例测试

## 注意事项

1. **资源管理**：使用后必须调用 `Close()` 释放资源
2. **错误检查**：定期检查 `Err()` 方法返回的错误
3. **并发安全**：单个 `BlobTableReader` 实例不是并发安全的
4. **内存使用**：适合处理大型文件，避免一次性加载全部数据到内存