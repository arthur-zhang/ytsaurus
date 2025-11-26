# Skiff 高效序列化格式模块

Skiff 是一个为 YTsaurus 优化的二进制序列化格式，提供了高性能的数据编码和解码功能。它通过预定义的模式协商实现极高效的数据传输。

## 概述

Skiff 格式专为 YTsaurus 大数据场景设计，具有以下特点：

- **高效性**: 二进制格式，无模式开销，压缩性好
- **高性能**: 预编译编解码器，最小化运行时开销
- **强类型**: 严格模式检查，确保数据一致性
- **零拷贝**: 内部优化减少内存分配和拷贝

**注意**: Skiff 需要模式协商且不支持模式演进，适用于数据结构稳定的场景。

## 核心组件

### WireType 线路类型系统

```go
type WireType int

const (
    TypeNothing           WireType = iota  // 空值
    TypeBoolean                           // 布尔值
    TypeInt8                              // 8位整数
    TypeInt16                             // 16位整数
    TypeInt32                             // 32位整数
    TypeInt64                             // 64位整数
    TypeInt128                            // 128位整数
    TypeInt256                            // 256位整数
    TypeUint8                             // 8位无符号整数
    TypeUint16                            // 16位无符号整数
    TypeUint32                            // 32位无符号整数
    TypeUint64                            // 64位无符号整数
    TypeDouble                            // 双精度浮点数
    TypeString32                          // 字符串（32位长度）
    TypeYSON32                            // YSON数据（32位长度）

    // 复杂类型
    TypeVariant8                          // 变体类型（8位索引）
    TypeVariant16                         // 变体类型（16位索引）
    TypeRepeatedVariant8                  // 重复变体（8位索引）
    TypeRepeatedVariant16                 // 重复变体（16位索引）
    TypeTuple                             // 元组类型
)
```

### Schema 结构体

```go
// Schema 描述单个值的线路格式
type Schema struct {
    Type     WireType `yson:"wire_type"`    // 线路类型
    Name     string   `yson:"name,omitempty"` // 列名
    Children []Schema `yson:"children,omitempty"` // 子类型（复杂类型）
}

// Format 描述流的 Skiff 格式
type Format struct {
    Name         string            `yson:",value"`                    // 固定为 "skiff"
    TableSchemas []any             `yson:"table_skiff_schemas,attr"`  // 表模式或引用
    SchemaRegistry map[string]*Schema `yson:"skiff_schema_registry,attr"` // 共享模式注册表
}
```

### 核心接口

#### 编码器
```go
type Encoder struct {
    w      *writer
    cache  opCache
    schema *Schema
}

func NewEncoder(w io.Writer, schema Schema) (*Encoder, error)
func (e *Encoder) Encode(row any) error
```

#### 解码器
```go
type Decoder struct {
    tables []tableInfo
    r      *reader
    // ... 内部状态
}

func NewDecoder(r io.Reader, format Format, opts ...decoderOption) (*Decoder, error)
func (d *Decoder) Scan(row any) (bool, error)
func (d *Decoder) TableIndex() int
func (d *Decoder) RowIndex() int64
```

## 类型映射关系

### YTsaurus 类型到 Skiff 线路类型

| YTsaurus 类型 | Skiff WireType | 说明 |
|---------------|----------------|------|
| boolean | TypeBoolean | 布尔值 |
| int8 | TypeInt8 | 8位整数 |
| int16 | TypeInt16 | 16位整数 |
| int32 | TypeInt32 | 32位整数 |
| int64 | TypeInt64 | 64位整数 |
| uint8 | TypeUint8 | 8位无符号整数 |
| uint16 | TypeUint16 | 16位无符号整数 |
| uint32 | TypeUint32 | 32位无符号整数 |
| uint64 | TypeUint64 | 64位无符号整数 |
| float32/float64 | TypeDouble | 双精度浮点数 |
| string/bytes | TypeString32 | 字符串 |
| any | TypeYSON32 | YSON 数据 |
| null | TypeNothing | 空值 |
| date/datetime/timestamp | TypeUint64 | 时间类型 |
| interval | TypeInt64 | 时间间隔 |

### 复杂类型映射

| YTsaurus 复杂类型 | Skiff 表示 |
|-------------------|------------|
| Optional\<T> | Variant8<nothing, T> |
| List\<T> | RepeatedVariant8\<T> |
| Struct | Tuple |
| Tuple | Tuple |
| Dict\<K,V> | RepeatedVariant8\<Tuple<K, V>> |
| Variant | Variant8 或 Variant16 |
| Tagged | 内部类型 |

## 使用示例

### 基本编码示例

```go
package main

import (
    "bytes"
    "fmt"
    "log"

    "go.ytsaurus.com/yt/go/skiff"
    "go.ytsaurus.com/yt/go/schema"
)

type User struct {
    ID       int64  `yson:"id,key"`
    Name     string `yson:"name"`
    Email    string `yson:"email,omitempty"`
    Age      int32  `yson:"age,omitempty"`
    IsActive bool   `yson:"is_active"`
}

func main() {
    // 从结构体推断 Skiff 模式
    skiffFormat := skiff.MustInferFormat(User{})

    // 获取单表模式
    skiffSchema, err := skiff.SingleSchema(&skiffFormat)
    if err != nil {
        log.Fatal(err)
    }

    // 创建编码器
    var buf bytes.Buffer
    encoder, err := skiff.NewEncoder(&buf, *skiffSchema)
    if err != nil {
        log.Fatal(err)
    }

    // 编码多行数据
    users := []User{
        {ID: 1, Name: "张三", Email: "zhangsan@example.com", Age: 25, IsActive: true},
        {ID: 2, Name: "李四", Age: 30, IsActive: false}, // Email 为空
        {ID: 3, Name: "王五", Email: "wangwu@example.com", Age: 28, IsActive: true},
    }

    for _, user := range users {
        if err := encoder.Encode(user); err != nil {
            log.Fatal(err)
        }
    }

    fmt.Printf("编码数据大小: %d 字节\n", buf.Len())
}
```

### 基本解码示例

```go
package main

import (
    "bytes"
    "fmt"
    "log"

    "go.ytsaurus.com/yt/go/skiff"
)

func decodeData(data []byte) {
    // 创建解码器
    skiffFormat := skiff.MustInferFormat(User{})
    decoder, err := skiff.NewDecoder(bytes.NewReader(data), skiffFormat)
    if err != nil {
        log.Fatal(err)
    }

    var user User
    count := 0

    for decoder.Scan(&user) {
        count++
        fmt.Printf("行 %d: ID=%d, Name=%s, Email=%s, Age=%d, Active=%t\n",
            count, user.ID, user.Name, user.Email, user.Age, user.IsActive)
    }

    if err := decoder.Err(); err != nil {
        log.Fatal(err)
    }

    fmt.Printf("共解码 %d 行数据\n", count)
}
```

### 从表模式创建 Skiff 模式

```go
package main

import (
    "fmt"

    "go.ytsaurus.com/yt/go/schema"
    "go.ytsaurus.com/yt/go/skiff"
    "go.ytsaurus.tech/library/go/ptr"
)

func createSkiffFromTableSchema() {
    // 定义表模式
    tableSchema := schema.Schema{
        Strict:     ptr.Bool(true),
        UniqueKeys: false,
        Columns: []schema.Column{
            {
                Name:     "id",
                Type:     schema.TypeInt64,
                Required: true,
                SortOrder: schema.SortAscending,
            },
            {
                Name:     "name",
                Type:     schema.TypeString,
                Required: true,
            },
            {
                Name:     "email",
                Type:     schema.TypeString,
                Required: false,
            },
            {
                Name:     "age",
                Type:     schema.TypeInt32,
                Required: false,
            },
        },
    }

    // 转换为 Skiff 模式
    skiffSchema := skiff.FromTableSchema(tableSchema)

    fmt.Printf("Skiff 模式:\n")
    printSkiffSchema(skiffSchema, 0)
}

func printSkiffSchema(s skiff.Schema, indent int) {
    prefix := ""
    for i := 0; i < indent; i++ {
        prefix += "  "
    }

    fmt.Printf("%s%s: %s", prefix, s.Name, s.Type)
    if len(s.Children) > 0 {
        fmt.Printf(" [\n")
        for _, child := range s.Children {
            printSkiffSchema(child, indent+1)
        }
        fmt.Printf("%s]", prefix)
    }
    fmt.Printf("\n")
}
```

### 复杂类型示例

```go
package main

import (
    "fmt"

    "go.ytsaurus.com/yt/go/skiff"
    "go.ytsaurus.com/yt/go/schema"
)

func complexTypesExample() {
    // 创建包含复杂类型的表模式
    tableSchema := schema.Schema{
        Strict: ptr.Bool(true),
        Columns: []schema.Column{
            {
                Name: "id",
                ComplexType: schema.TypeInt64,
            },
            {
                Name: "tags",
                ComplexType: schema.List{
                    Item: schema.TypeString,
                },
            },
            {
                Name: "metadata",
                ComplexType: schema.Optional{
                    Item: schema.Struct{
                        Members: []schema.StructMember{
                            {Name: "author", Type: schema.TypeString},
                            {Name: "version", Type: schema.TypeInt32},
                            {Name: "created", Type: schema.TypeTimestamp},
                        },
                    },
                },
            },
            {
                Name: "properties",
                ComplexType: schema.Dict{
                    Key:   schema.TypeString,
                    Value: schema.TypeString,
                },
            },
        },
    }

    // 转换为 Skiff 模式
    skiffSchema := skiff.FromTableSchema(tableSchema)

    fmt.Println("复杂类型 Skiff 模式:")
    printSkiffSchema(skiffSchema, 0)
}
```

### 系统列支持

```go
package main

import (
    "fmt"

    "go.ytsaurus.com/yt/go/skiff"
    "go.ytsaurus.com/yt/go/schema"
)

func systemColumnsExample() {
    tableSchema := schema.Schema{
        Columns: []schema.Column{
            {Name: "key", Type: schema.TypeInt64},
            {Name: "value", Type: schema.TypeString},
        },
    }

    // 添加系统列
    skiffSchema := skiff.FromTableSchema(
        tableSchema,
        skiff.withKeySwitch(),  // 添加 $key_switch
        skiff.withRowIndex(),   // 添加 $row_index
        skiff.withRangeIndex(), // 添加 $range_index
    )

    fmt.Println("包含系统列的 Skiff 模式:")
    printSkiffSchema(skiffSchema, 0)
}
```

### 多表格式

```go
package main

import (
    "fmt"

    "go.ytsaurus.com/yt/go/skiff"
)

func multiTableFormat() {
    // 创建共享模式注册表
    registry := make(map[string]*skiff.Schema)

    // 定义基础模式
    baseSchema := skiff.Schema{
        Type: skiff.TypeTuple,
        Children: []skiff.Schema{
            {Type: skiff.TypeInt64, Name: "id"},
            {Type: skiff.TypeString, Name: "name"},
        },
    }
    registry["base"] = &baseSchema

    // 创建多表格式
    multiTableFormat := skiff.Format{
        Name: "skiff",
        TableSchemas: []any{
            "$base",        // 引用注册表中的模式
            &skiff.Schema{  // 内联模式
                Type: skiff.TypeTuple,
                Children: []skiff.Schema{
                    {Type: skiff.TypeString32, Name: "data"},
                },
            },
        },
        SchemaRegistry: registry,
    }

    fmt.Printf("多表格式: %+v\n", multiTableFormat)
}
```

## 高级功能

### 1. 模式验证

```go
func validateSchema(skiffSchema *skiff.Schema, tableSchema *schema.Schema) error {
    // 检查类型兼容性
    if skiffSchema.Type != skiff.TypeTuple {
        return fmt.Errorf("根类型必须是 Tuple")
    }

    if tableSchema != nil {
        if len(skiffSchema.Children) != len(tableSchema.Columns) {
            return fmt.Errorf("列数不匹配")
        }

        for i, col := range skiffSchema.Children {
            tableCol := tableSchema.Columns[i]
            if col.Name != tableCol.Name {
                return fmt.Errorf("列名不匹配: %s vs %s", col.Name, tableCol.Name)
            }

            // 验证类型兼容性
            if err := validateColumnType(col, tableCol); err != nil {
                return fmt.Errorf("列 %s 类型验证失败: %w", col.Name, err)
            }
        }
    }

    return nil
}
```

### 2. 性能基准测试

```go
func benchmarkSkiff() {
    // 创建测试数据
    users := make([]User, 10000)
    for i := range users {
        users[i] = User{
            ID:       int64(i),
            Name:     fmt.Sprintf("用户_%d", i),
            Email:    fmt.Sprintf("user_%d@example.com", i),
            Age:      int32(20 + i%50),
            IsActive: i%2 == 0,
        }
    }

    // 基准测试编码
    skiffFormat := skiff.MustInferFormat(User{})
    skiffSchema, _ := skiff.SingleSchema(&skiffFormat)

    start := time.Now()
    var buf bytes.Buffer
    encoder, _ := skiff.NewEncoder(&buf, *skiffSchema)

    for _, user := range users {
        _ = encoder.Encode(user)
    }

    encodeTime := time.Since(start)
    fmt.Printf("编码 %d 行耗时: %v, 大小: %d 字节\n",
        len(users), encodeTime, buf.Len())

    // 基准测试解码
    start = time.Now()
    decoder, _ := skiff.NewDecoder(bytes.NewReader(buf.Bytes()), skiffFormat)
    count := 0
    var user User

    for decoder.Scan(&user) {
        count++
    }

    decodeTime := time.Since(start)
    fmt.Printf("解码 %d 行耗时: %v\n", count, decodeTime)
}
```

### 3. 流式处理

```go
func streamProcessing() {
    // 模拟大数据流处理
    skiffFormat := skiff.MustInferFormat(User{})
    skiffSchema, _ := skiff.SingleSchema(&skiffFormat)

    var buf bytes.Buffer
    encoder, _ := skiff.NewEncoder(&buf, *skiffSchema)

    // 流式生成和编码数据
    go func() {
        for i := 0; i < 1000000; i++ {
            user := User{
                ID:       int64(i),
                Name:     fmt.Sprintf("用户_%d", i),
                Email:    fmt.Sprintf("user_%d@example.com", i),
                Age:      int32(20 + i%50),
                IsActive: i%3 != 0,
            }

            if err := encoder.Encode(user); err != nil {
                log.Printf("编码失败: %v", err)
                return
            }
        }
    }()

    // 流式解码和处理
    decoder, _ := skiff.NewDecoder(&buf, skiffFormat)
    var user User

    for decoder.Scan(&user) {
        // 处理每一行数据
        if user.ID%10000 == 0 {
            fmt.Printf("处理到 ID: %d, 表索引: %d, 行索引: %d\n",
                user.ID, decoder.TableIndex(), decoder.RowIndex())
        }
    }
}
```

## 最佳实践

### 1. 模式设计

```go
// ✅ 推荐：使用固定大小的类型
type OptimizedUser struct {
    ID    int64  `yson:"id,key"`
    Name  string `yson:"name"`
    Age   int32  `yson:"age"`      // 使用 int32 而不是 int
    Flags uint8  `yson:"flags"`    // 使用 uint8 存储标志位
}

// ❌ 避免：使用动态类型
type BadUser struct {
    ID    interface{} `yson:"id"`
    Name  interface{} `yson:"name"`
    Data  interface{} `yson:"data"`
}
```

### 2. 内存管理

```go
func efficientProcessing() {
    // 重用解码对象减少内存分配
    var user User

    decoder, _ := skiff.NewDecoder(reader, format)

    for decoder.Scan(&user) {
        // 处理数据，但不保留 user 对象引用
        processData(user)

        // 重置对象（可选，下一轮 Scan 会覆盖）
        user = User{}
    }
}
```

### 3. 错误处理

```go
func robustDecoding(decoder *skiff.Decoder) error {
    var data User

    for {
        hasData, err := decoder.Scan(&data)
        if err != nil {
            return fmt.Errorf("扫描失败: %w", err)
        }

        if !hasData {
            break // 数据流结束
        }

        // 处理数据
        if err := processData(data); err != nil {
            return fmt.Errorf("处理数据 %d 失败: %w", data.ID, err)
        }
    }

    return nil
}
```

### 4. 性能优化

```go
func optimizeEncoding() {
    // 使用缓冲 Writer
    bufferedWriter := bufio.NewWriter(os.Stdout)
    encoder, _ := skiff.NewEncoder(bufferedWriter, schema)

    // 批量编码后刷新
    for i := 0; i < batchSize; i++ {
        _ = encoder.Encode(generateData())
    }

    _ = bufferedWriter.Flush() // 一次性刷新
}
```

## 性能特点

### 优势

1. **高效率**: 二进制格式，无序列化开销
2. **低延迟**: 预编译编解码器，运行时开销小
3. **紧凑性**: 压缩比高，网络传输效率好
4. **类型安全**: 强类型检查，减少运行时错误

### 限制

1. **模式协商**: 需要预先定义模式
2. **不支持模式演进**: 结构变更需要重新协商
3. **向后兼容性**: 有限的兼容性支持

## 错误处理

常见错误类型：

```go
// 模式错误
var (
    ErrInvalidSchema     = xerrors.New("无效的 Skiff 模式")
    ErrTypeMismatch      = xerrors.New("类型不匹配")
    ErrColumnNotFound    = xerrors.New("列不存在")
    ErrInvalidFormat     = xerrors.New("无效的格式")
)

// 数据错误
var (
    ErrDataCorrupted     = xerrors.New("数据损坏")
    ErrSizeExceeded      = xerrors.New("数据大小超限")
    ErrUnexpectedEOF     = xerrors.New("意外的文件结束")
)
```

## 调试工具

### 模式打印

```go
func debugSkiffSchema(schema skiff.Schema) {
    fmt.Printf("=== Skiff 模式调试 ===\n")
    fmt.Printf("根类型: %s\n", schema.Type)
    fmt.Printf("子类型数: %d\n", len(schema.Children))

    for i, child := range schema.Children {
        fmt.Printf("  [%d] %s: %s", i, child.Name, child.Type)
        if child.Type.IsSimple() {
            fmt.Printf(" (简单类型)")
        } else {
            fmt.Printf(" (复杂类型)")
        }
        fmt.Printf("\n")
    }
    fmt.Printf("====================\n")
}
```

### 数据验证

```go
func validateSkiffData(data []byte, format skiff.Format) error {
    // 创建解码器验证数据完整性
    decoder, err := skiff.NewDecoder(bytes.NewReader(data), format)
    if err != nil {
        return fmt.Errorf("创建解码器失败: %w", err)
    }

    // 扫描所有数据验证完整性
    var dummy interface{}
    count := 0
    for decoder.Scan(&dummy) {
        count++
    }

    if err := decoder.Err(); err != nil {
        return fmt.Errorf("数据验证失败: %w", err)
    }

    fmt.Printf("数据验证通过，共 %d 行\n", count)
    return nil
}
```

## 注意事项

1. **模式兼容性**: 确保编码和解码使用相同的模式
2. **内存限制**: 注意大数据量的内存使用
3. **错误检查**: 总是检查编解码操作的错误
4. **性能测试**: 在生产环境前进行充分的性能测试
5. **数据完整性**: 验证序列化和反序列化的一致性

## 扩展和定制

### 自定义类型处理

```go
// 实现自定义类型的编解码逻辑
func customTypeHandler(value CustomType) error {
    // 转换为 Skiff 支持的基础类型
    return nil
}
```

### 缓存优化

```go
// 使用编解码缓存提升性能
type CachedTranscoder struct {
    cache map[reflect.Type]Transcoder
    mu    sync.RWMutex
}

func (c *CachedTranscoder) GetTranscoder(typ reflect.Type) (Transcoder, error) {
    c.mu.RLock()
    if transcoder, exists := c.cache[typ]; exists {
        c.mu.RUnlock()
        return transcoder, nil
    }
    c.mu.RUnlock()

    // 创建新的转换器
    c.mu.Lock()
    defer c.mu.Unlock()

    // 双重检查
    if transcoder, exists := c.cache[typ]; exists {
        return transcoder, nil
    }

    transcoder, err := createTranscoder(typ)
    if err != nil {
        return nil, err
    }

    c.cache[typ] = transcoder
    return transcoder, nil
}
```

Skiff 模块为 YTsaurus 提供了高性能的数据序列化解决方案，特别适用于大数据场景下对性能有严格要求的应用。