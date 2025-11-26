# GUID

## 概述

GUID 模块实现了 YTsaurus 特有的 GUID（全局唯一标识符）格式。由于 YTsaurus 使用非标准的文本表示格式，该模块基于标准的 UUID 实现提供了兼容 YTsaurus 系统的 GUID 处理功能。

## 功能特性

- **YTsaurus 兼容**：实现 YTsaurus 特有的 GUID 文本格式
- **高效处理**：基于 `gofrs/uuid` 库的高效实现
- **YSON 支持**：完整的 YSON 序列化/反序列化支持
- **类型安全**：强类型的 GUID 操作
- **多种格式**：支持多种表示和解析格式

## YTsaurus GUID 格式

YTsaurus 使用特殊的 GUID 文本格式：`%x-%x-%x-%x`，其中四个部分分别对应 GUID 的不同字节段，顺序与标准 UUID 不同。

### 格式说明

- **标准 UUID 格式**：`8-4-4-4-12`（如 `550e8400-e29b-41d4-a716-446655440000`）
- **YTsaurus GUID 格式**：`8-8-8-8`（四个32位整数的十六进制表示）

## 核心类型

### GUID 类型

```go
type GUID uuid.UUID  // 基于 UUID 的 16 字节值
```

## 主要方法

### 1. 创建和解析

```go
// 创建新的 GUID
g := guid.New()

// 从字符串解析
g, err := guid.ParseString("a1b2c3d4-e5f6-a7b8-c9d0-e1f2a3b4c5d6")
```

### 2. 转换方法

```go
// 获取 32 位整数部分
a, b, c, d := g.Parts()

// 获取 64 位整数部分
a, b := g.Halves()

// 从 32 位整数创建
g := guid.FromParts(0xa1b2c3d4, 0xe5f6a7b8, 0xc9d0e1f2, 0xa3b4c5d6)

// 从 64 位整数创建
g := guid.FromHalves(0xe5f6a7b8a1b2c3d4, 0xa3b4c5d6c9d0e1f2)
```

### 3. 字符串表示

```go
// YTsaurus 格式字符串
s := g.String()  // 输出: "a3b4c5d6-c9d0-e1f2-a5f6-a7b8a1b2c3d4"

// 十六进制字符串
hex := g.HexString()  // 输出: "d6c5b4a3f2e1d0c9b8a7f6e5d4c3b2a1"
```

## 使用方法

### 基本用法

```go
package main

import (
    "fmt"

    "go.ytsaurus.tech/yt/go/guid"
)

func main() {
    // 创建新的 GUID
    g := guid.New()
    fmt.Printf("新 GUID: %s\n", g)

    // 解析 GUID 字符串
    parsed, err := guid.ParseString("a3b4c5d6-c9d0-e1f2-a5f6-a7b8a1b2c3d4")
    if err != nil {
        panic(err)
    }
    fmt.Printf("解析的 GUID: %s\n", parsed)

    // 获取各部分
    a, b, c, d := parsed.Parts()
    fmt.Printf("32位部分: %08x-%08x-%08x-%08x\n", a, b, c, d)

    // 从部分重建
    rebuilt := guid.FromParts(a, b, c, d)
    fmt.Printf("重建的 GUID: %s\n", rebuilt)
}
```

### YSON 序列化

```go
import "go.ytsaurus.tech/yt/go/yson"

func ysonExample() {
    g := guid.New()

    // 序列化为 YSON
    data, err := yson.Marshal(g)
    if err != nil {
        panic(err)
    }
    fmt.Printf("YSON: %s\n", string(data))

    // 从 YSON 反序列化
    var g2 guid.GUID
    err = yson.Unmarshal(data, &g2)
    if err != nil {
        panic(err)
    }
    fmt.Printf("反序列化: %s\n", g2)
}
```

### 结构体中使用

```go
type Record struct {
    ID    guid.GUID `yson:"id"`
    Name  string    `yson:"name"`
    Value int       `yson:"value"`
}

func recordExample() {
    r := Record{
        ID:    guid.New(),
        Name:  "test-record",
        Value: 42,
    }

    // 序列化记录
    data, err := yson.Marshal(&r)
    if err != nil {
        panic(err)
    }

    // 反序列化记录
    var r2 Record
    err = yson.Unmarshal(data, &r2)
    if err != nil {
        panic(err)
    }

    fmt.Printf("记录 ID: %s\n", r2.ID)
}
```

### 批量处理

```go
func batchProcessing() {
    // 生成多个 GUID
    guids := make([]guid.GUID, 1000)
    for i := range guids {
        guids[i] = guid.New()
    }

    // 检查唯一性
    unique := make(map[guid.GUID]struct{})
    for _, g := range guids {
        if _, exists := unique[g]; exists {
            panic("发现重复的 GUID")
        }
        unique[g] = struct{}{}
    }
    fmt.Printf("生成了 %d 个唯一 GUID\n", len(unique))
}
```

## 性能优化

### 1. 缓存和重用

```go
// 对于需要大量 GUID 的场景，考虑预生成
var guidPool chan guid.GUID

func initGUIDPool(size int) {
    guidPool = make(chan guid.GUID, size)
    for i := 0; i < size; i++ {
        guidPool <- guid.New()
    }
}

func getGUID() guid.GUID {
    select {
    case g := <-guidPool:
        return g
    default:
        return guid.New()
    }
}
```

### 2. 批量操作

```go
// 批量生成 GUID
func generateBatch(count int) []guid.GUID {
    guids := make([]guid.GUID, count)
    for i := 0; i < count; i++ {
        guids[i] = guid.New()
    }
    return guids
}

// 批量序列化
func serializeBatch(guids []guid.GUID) [][]byte {
    results := make([][]byte, len(guids))
    for i, g := range guids {
        results[i], _ = g.MarshalText()
    }
    return results
}
```

### 3. 比较和排序

```go
// GUID 支持直接比较
func sortGUIDs(guids []guid.GUID) {
    // 使用标准排序
    sort.Slice(guids, func(i, j int) bool {
        // 按字节序比较
        return string(guids[i][:]) < string(guids[j][:])
    })
}

// 检查相等
func compareGUIDs(g1, g2 guid.GUID) bool {
    return g1 == g2
}
```

## 最佳实践

### 1. 错误处理

```go
func safeParse(s string) (guid.GUID, bool) {
    g, err := guid.ParseString(s)
    if err != nil {
        // 记录错误日志
        log.Printf("解析 GUID 失败 %q: %v", s, err)
        return guid.GUID{}, false
    }
    return g, true
}
```

### 2. 验证

```go
func isValidGUID(s string) bool {
    _, err := guid.ParseString(s)
    return err == nil
}

// 检查是否为零值
func isZero(g guid.GUID) bool {
    var zero guid.GUID
    return g == zero
}
```

### 3. 转换

```go
// 转换为标准 UUID（如果需要与其他系统交互）
func toUUID(g guid.GUID) uuid.UUID {
    return uuid.UUID(g)
}

// 从标准 UUID 转换
func fromUUID(u uuid.UUID) guid.GUID {
    return guid.GUID(u)
}
```

## 应用场景

### 1. 唯一标识符

```go
type Task struct {
    ID     guid.GUID `yson:"task_id"`
    Status string    `yson:"status"`
}

func createTask() *Task {
    return &Task{
        ID:     guid.New(),
        Status: "created",
    }
}
```

### 2. 分布式系统

```go
// 分布式锁使用 GUID 作为标识
type DistributedLock struct {
    LockID guid.GUID
    Owner  string
}

func acquireLock(resource string) *DistributedLock {
    return &DistributedLock{
        LockID: guid.New(),
        Owner:  getHostID(),
    }
}
```

### 3. 事务标识

```go
type Transaction struct {
    TxID    guid.GUID `yson:"tx_id"`
    Actions []Action  `yson:"actions"`
}

func beginTransaction() *Transaction {
    return &Transaction{
        TxID: guid.New(),
    }
}
```

## 注意事项

1. **格式兼容性**：YTsaurus GUID 格式与标准 UUID 不同
2. **字节序**：使用小端字节序存储整数部分
3. **唯一性保证**：基于 UUID v4 算法，具有很高的唯一性
4. **零值**：零值 GUID 不是有效的标识符
5. **并发安全**：GUID 值是不可变的，可以安全地在并发环境中使用

## 技术细节

### 字节布局

```
字节位置:  0-3      4-7      8-11     12-15
内容:     Part1    Part2    Part3    Part4
字节序:    Little Endian (所有部分)
```

### 字符串格式

```go
// YTsaurus 格式：从后向前读取各部分
format := "%x-%x-%x-%x"  // d, c, b, a 顺序

// 示例
// Parts: a=0x12345678, b=0x9abcdef0, c=0x12345678, d=0x9abcdef0
// String: "9abcdef0-12345678-9abcdef0-12345678"
```

## 依赖项

- `github.com/gofrs/uuid`：UUID 实现
- `golang.org/x/xerrors`：增强的错误处理
- `go.ytsaurus.tech/yt/go/yson`：YSON 序列化支持

## 测试

模块包含完整的单元测试：

```go
func TestGUID(t *testing.T) {
    // 测试 GUID 创建
    g := guid.New()
    assert.NotEqual(t, guid.GUID{}, g)

    // 测试字符串解析
    parsed, err := guid.ParseString(g.String())
    assert.NoError(t, err)
    assert.Equal(t, g, parsed)

    // 测试 YSON 序列化
    data, err := yson.Marshal(g)
    assert.NoError(t, err)

    var g2 guid.GUID
    err = yson.Unmarshal(data, &g2)
    assert.NoError(t, err)
    assert.Equal(t, g, g2)
}
```