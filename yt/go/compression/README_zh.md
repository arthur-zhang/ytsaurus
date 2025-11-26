# Compression

## 概述

Compression 模块是 YTsaurus Go 客户端的统一压缩库，提供了多种压缩算法的统一接口。该模块支持多种主流压缩算法，包括 Snappy、LZ4、Brotli、Zlib 和 Zstd，并允许通过配置不同的压缩级别来平衡压缩比和性能。

## 功能特性

- **统一接口**：所有压缩算法都实现相同的 `Codec` 接口
- **多算法支持**：支持 5 种主流压缩算法
- **可配置级别**：多数算法支持多个压缩级别
- **高性能**：针对不同场景优化的压缩算法选择
- **零开销**：支持无压缩模式，避免不必要的数据处理

## 支持的压缩算法

### 1. Snappy (CodecID = 1)
- **特点**：高速压缩，适合实时应用
- **压缩比**：中等
- **压缩速度**：极快
- **解压速度**：极快
- **适用场景**：需要高性能的场景

### 2. LZ4 (CodecID = 4, 5)
- **CodecIDLz4**：标准 LZ4 压缩
- **CodecIDLz4HighCompression**：高压缩比 LZ4
- **特点**：极快的压缩和解压速度
- **压缩比**：中低
- **适用场景**：对速度要求极高的场景

### 3. Brotli (CodecID = 8-18, 11)
- **压缩级别**：1-11 级
- **特点**：优秀的压缩比，适合网络传输
- **压缩比**：高
- **压缩速度**：中等
- **解压速度**：快
- **适用场景**：Web 内容压缩

### 4. Zlib (CodecID = 2-3, 6, 19-25)
- **压缩级别**：1-9 级
- **特点**：成熟稳定的压缩算法
- **压缩比**：中高
- **压缩速度**：中等
- **解压速度**：快
- **适用场景**：通用压缩需求

### 5. Zstd (CodecID = 26-32)
- **压缩级别**：1-7 级
- **特点**：现代压缩算法，性能和压缩比平衡
- **压缩比**：高
- **压缩速度**：快
- **解压速度**：极快
- **适用场景**：大数据处理和存储

## 核心接口

### Codec 接口

```go
type Codec interface {
    // Compress 压缩给定的数据块
    Compress(block []byte) ([]byte, error)

    // Decompress 解压缩给定的数据块
    Decompress(block []byte) ([]byte, error)

    // GetID 返回压缩算法标识符
    GetID() CodecID
}
```

## 使用方法

### 创建压缩器

```go
package main

import (
    "fmt"
    "log"

    "go.ytsaurus.tech/yt/go/compression"
)

func main() {
    // 创建 Snappy 压缩器
    codec := compression.NewCodec(compression.CodecIDSnappy)

    // 创建 LZ4 高压缩比压缩器
    codecHC := compression.NewCodec(compression.CodecIDLz4HighCompression)

    // 创建 Brotli 9 级压缩器
    codecBrotli := compression.NewCodec(compression.CodecIDBrotli9)

    // 创建 Zstd 5 级压缩器
    codecZstd := compression.NewCodec(compression.CodecIDZstd5)

    fmt.Printf("Codec: %s\n", codec.GetID())
}
```

### 压缩和解压

```go
func compressExample() {
    // 创建压缩器
    codec := compression.NewCodec(compression.CodecIDZstd5)

    // 原始数据
    data := []byte("这是一段需要压缩的重复数据。" +
        "这是一段需要压缩的重复数据。" +
        "这是一段需要压缩的重复数据。")

    // 压缩
    compressed, err := codec.Compress(data)
    if err != nil {
        log.Fatal(err)
    }

    fmt.Printf("原始大小: %d, 压缩后大小: %d\n",
        len(data), len(compressed))

    // 解压
    decompressed, err := codec.Decompress(compressed)
    if err != nil {
        log.Fatal(err)
    }

    fmt.Printf("解压后: %s\n", string(decompressed))
}
```

### 性能测试

```go
func benchmarkCodecs() {
    codecs := []compression.CodecID{
        compression.CodecIDSnappy,
        compression.CodecIDLz4,
        compression.CodecIDLz4HighCompression,
        compression.CodecIDBrotli9,
        compression.CodecIDZlib6,
        compression.CodecIDZstd5,
    }

    data := generateTestData(1024 * 1024) // 1MB 测试数据

    for _, id := range codecs {
        codec := compression.NewCodec(id)

        start := time.Now()
        compressed, _ := codec.Compress(data)
        compressTime := time.Since(start)

        start = time.Now()
        _, _ := codec.Decompress(compressed)
        decompressTime := time.Since(start)

        fmt.Printf("%s: 压缩比=%.2f, 压耗时=%v, 解压耗时=%v\n",
            id,
            float64(len(compressed))/float64(len(data)),
            compressTime,
            decompressTime)
    }
}
```

## 压缩算法选择指南

### 根据使用场景选择

1. **实时数据处理**
   - 推荐：Snappy、LZ4
   - 原因：极快的压缩/解压速度
   - 权衡：较低的压缩比

2. **网络传输**
   - 推荐：Brotli、Zstd
   - 原因：高压缩比，减少带宽使用
   - 权衡：稍慢的压缩速度

3. **长期存储**
   - 推荐：Zstd、Brotli 高级别
   - 原因：最大化压缩比，节省存储空间
   - 权衡：压缩时间较长

4. **CPU 受限环境**
   - 推荐：Snappy、LZ4
   - 原因：低 CPU 使用率
   - 权衡：较低的压缩比

### 性能对比

| 算法 | 压缩速度 | 解压速度 | 压缩比 | 适用场景 |
|------|----------|----------|--------|----------|
| Snappy | 极快 | 极快 | 低 | 实时处理 |
| LZ4 | 极快 | 极快 | 中低 | 高速缓存 |
| LZ4 HC | 慢 | 极快 | 中高 | 一次写入，多次读取 |
| Brotli | 中等 | 快 | 高 | Web 传输 |
| Zlib | 中等 | 快 | 中高 | 通用场景 |
| Zstd | 快 | 极快 | 高 | 大数据处理 |

## 最佳实践

### 1. 选择合适的压缩级别

```go
// 对于实时数据，使用低压缩级别
codec := compression.NewCodec(compression.CodecIDZstd1)

// 对于存储数据，使用高压缩级别
codec := compression.NewCodec(compression.CodecIDZstd7)

// 对于网络传输，使用中等压缩级别
codec := compression.NewCodec(compression.CodecIDBrotli5)
```

### 2. 错误处理

```go
compressed, err := codec.Compress(data)
if err != nil {
    // 处理压缩错误
    log.Printf("压缩失败: %v", err)
    return
}

decompressed, err := codec.Decompress(compressed)
if err != nil {
    // 处理解压错误
    log.Printf("解压失败: %v", err)
    return
}
```

### 3. 内存管理

```go
// 对于大数据，分块压缩
const chunkSize = 64 * 1024 // 64KB

var compressedChunks [][]byte
for i := 0; i < len(data); i += chunkSize {
    chunk := data[i:min(i+chunkSize, len(data))]
    compressed, err := codec.Compress(chunk)
    if err != nil {
        return err
    }
    compressedChunks = append(compressedChunks, compressed)
}
```

## 注意事项

1. **线程安全**：Codec 实例不是线程安全的，每个 goroutine 应使用独立实例
2. **内存使用**：压缩和解压都需要额外的内存缓冲区
3. **错误处理**：必须检查压缩和解压操作的返回错误
4. **兼容性**：确保压缩和解压使用相同的算法
5. **性能测试**：在实际数据上测试压缩算法的性能

## 依赖项

- Snappy：github.com/golang/snappy
- LZ4：github.com/pierrec/lz4/v4
- Brotli：github.com/andybalholm/brotli
- Zlib：标准库 compress/zlib
- Zstd：github.com/klauspost/compress/zstd