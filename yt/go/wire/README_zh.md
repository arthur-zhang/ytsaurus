# Wire - 线协议编码/解码库

## 概述

`wire` 包是 YTsaurus Go 客户端的核心组件，负责处理 YTsaurus 线协议的编码和解码操作。该库主要用于高性能的数据序列化和反序列化，特别是在表格数据处理和网络传输场景中。

## 主要功能

### 数据类型支持

`wire` 包支持以下 YTsaurus 数据类型：

- **基础类型**：
  - `TypeNull`: 空值类型
  - `TypeInt64`: 64位有符号整数
  - `TypeUint64`: 64位无符号整数
  - `TypeFloat64`: 64位浮点数
  - `TypeBool`: 布尔值
  - `TypeBytes`: 字节数组

- **复合类型**：
  - `TypeAny`: 任意类型（使用 YSON 编码）
  - `TypeComposite`: 复合类型

### 核心组件

#### 1. Value 结构体

```go
type Value struct {
    ID        uint16      // 字段ID
    Type      ValueType   // 值类型
    Aggregate bool        // 是否聚合
    scalar    uint64      // 标量值
    blob      []byte      // 二进制数据
}
```

#### 2. Row 类型

```go
type Row []Value
```

一行数据由多个 `Value` 组成，每个 `Value` 对应一个字段。

#### 3. NameTable

```go
type NameTable []NameTableEntry

type NameTableEntry struct {
    Name string
}
```

名称表用于映射字段ID到字段名称，实现高效的字段名称管理。

## 主要 API

### 编码功能

#### Encode() - 编码数据

```go
func Encode(items []any) (NameTable, []Row, error)
```

将 Go 数据结构编码为 wire 格式：
- `items`: 要编码的数据项
- 返回：名称表、行数据、错误

#### EncodePivotKeys() - 编码主键

```go
func EncodePivotKeys(keys []any) ([]Row, error)
```

专门用于编码表格主键。

### 解码功能

#### WireDecoder - 解码器

```go
type WireDecoder struct {
    NameTable NameTable
    Schema    *schema.Schema
}

func NewDecoder(table NameTable, schema *schema.Schema) *WireDecoder
func (d *WireDecoder) UnmarshalRow(row Row, v any) error
```

### 类型转换函数

```go
func NewNull(id uint16) Value
func NewInt64(id uint16, i int64) Value
func NewUint64(id uint16, i uint64) Value
func NewFloat64(id uint16, f float64) Value
func NewBool(id uint16, b bool) Value
func NewBytes(id uint16, b []byte) Value
func NewAny(id uint16, b []byte) Value
func NewComposite(id uint16, b []byte) Value
```

## 使用示例

### 基本编码示例

```go
package main

import (
    "fmt"
    "go.ytsaurus.tech/yt/go/wire"
)

type User struct {
    ID    int64  `yson:"user_id"`
    Name  string `yson:"name"`
    Email string `yson:"email"`
}

func main() {
    users := []User{
        {ID: 1, Name: "Alice", Email: "alice@example.com"},
        {ID: 2, Name: "Bob", Email: "bob@example.com"},
    }

    // 转换为 any 类型进行编码
    items := make([]any, len(users))
    for i := range users {
        items[i] = users[i]
    }

    nameTable, rows, err := wire.Encode(items)
    if err != nil {
        panic(err)
    }

    fmt.Printf("NameTable: %+v\n", nameTable)
    fmt.Printf("Rows: %+v\n", rows)
}
```

### 解码示例

```go
package main

import (
    "fmt"
    "go.ytsaurus.tech/yt/go/wire"
    "go.ytsaurus.tech/yt/go/schema"
)

func main() {
    // 假设有已编码的数据
    nameTable := wire.NameTable{
        {Name: "user_id"},
        {Name: "name"},
        {Name: "email"},
    }

    rows := []wire.Row{
        {
            wire.NewInt64(0, 1),
            wire.NewBytes(1, []byte("Alice")),
            wire.NewBytes(2, []byte("alice@example.com")),
        },
    }

    // 创建解码器
    decoder := wire.NewDecoder(nameTable, nil)

    var user User
    err := decoder.UnmarshalRow(rows[0], &user)
    if err != nil {
        panic(err)
    }

    fmt.Printf("Decoded user: %+v\n", user)
}
```

### 处理复杂类型

```go
package main

import (
    "fmt"
    "go.ytsaurus.tech/yt/go/wire"
    "go.ytsaurus.tech/yt/go/yson"
)

type ComplexData struct {
    Metadata map[string]interface{} `yson:"metadata"`
    Tags     []string              `yson:"tags"`
}

func main() {
    data := ComplexData{
        Metadata: map[string]interface{}{
            "version": 1,
            "active":  true,
        },
        Tags: []string{"important", "processed"},
    }

    nameTable, rows, err := wire.Encode([]any{data})
    if err != nil {
        panic(err)
    }

    fmt.Printf("Encoded complex data with %d rows\n", len(rows))
}
```

## 高级特性

### 并发编码

`wire` 包的编码器支持并发处理，在编码大量数据时会自动启用 goroutine 池来提高性能。

### 模式支持

解码器可以接受 YTsaurus schema，用于类型检查和数据验证：

```go
schema := &schema.Schema{
    Columns: []schema.Column{
        {Name: "user_id", Type: schema.TypeInt64},
        {Name: "name", Type: schema.TypeString},
        {Name: "email", Type: schema.TypeString},
    },
}

decoder := wire.NewDecoder(nameTable, schema)
```

### Decimal 类型支持

支持 YTsaurus 的 Decimal 类型，包括高精度数值的处理和转换。

## 性能优化

### 内存管理

- 使用对象池减少内存分配
- 预分配切片容量避免频繁扩容
- 零拷贝操作减少内存复制

### 并发处理

- 编码过程支持并行处理
- 使用读写锁保护共享状态
- 异步错误处理机制

## 最佳实践

1. **复用对象**：对于高频操作，考虑复用 NameTable 和 Decoder
2. **批量处理**：尽可能批量处理数据，减少函数调用开销
3. **错误处理**：始终检查编码/解码过程中的错误
4. **类型安全**：使用适当的 Go 类型匹配 YTsaurus 数据类型
5. **性能监控**：监控编码/解码性能，必要时进行优化

## 错误处理

`wire` 包定义了多种错误类型：

- `UnsupportedTypeError`: 不支持的类型错误
- `ReflectTypeError`: 反射类型错误
- `ErrIntegerOverflow`: 整数溢出错误
- `ErrFloat32Overflow`: 32位浮点数溢出错误

## 注意事项

1. 字段 ID 必须在 65535 以内（uint16 限制）
2. 名称表条目必须是唯一的
3. 并发编码时注意数据竞争问题
4. 复杂类型的序列化使用 YSON 格式
5. Decimal 类型需要正确的精度和刻度配置

## 相关依赖

- `go.ytsaurus.tech/yt/go/schema`: YTsaurus 模式定义
- `go.ytsaurus.tech/yt/go/yson`: YSON 序列化支持
- `golang.org/x/xerrors`: 增强错误处理

## 更多信息

详细的 API 文档和使用示例请参考 [YTsaurus 文档](https://ytsaurus.tech/docs/)。