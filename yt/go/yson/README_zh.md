# YSON - YTsaurus 序列化格式库

## 概述

`yson` 包是 YTsaurus 的核心序列化格式库，提供了完整的 YSON (YTsaurus Serialized Object Notation) 编解码功能。YSON 是一种高效的数据序列化格式，支持二进制和文本两种表示形式。

## YSON 格式类型

### 1. 二进制格式 (FormatBinary)

- 高效的二进制编码
- 紧凑的存储空间
- 快速的序列化/反序列化
- 适合网络传输和存储

### 2. 文本格式 (FormatText)

- 人类可读的文本表示
- 便于调试和手动编辑
- 支持注释和格式化
- 适合配置文件和日志

### 3. 美化格式 (FormatPretty)

- 带缩进和格式化的文本
- 更好的可读性
- 适合显示和文档

## 数据类型支持

### 基础类型

```go
// 整数类型
int8, int16, int32, int64
uint8, uint16, uint32, uint64
int, uint

// 浮点类型
float32, float64

// 布尔类型
bool

// 字符串类型
string, []byte

// 空值类型
nil (映射到 YSON entity)
```

### 复合类型

```go
// 列表类型
[]T (任意类型的切片)

// 映射类型
map[string]T
map[K]T (K 实现 TextMarshaler 或 BinaryMarshaler)

// 结构体类型
struct (包含 yson 标签的字段映射)
```

### 特殊类型

```go
// YSON 原始值
type RawValue []byte

// 时间类型
type Duration time.Duration

// YSON 特定值
Entity (对应 YSON 的 #)
```

## 核心 API

### 编码功能

#### Marshal() - 序列化

```go
func Marshal(value any) ([]byte, error)
func MarshalFormat(value any, format Format) ([]byte, error)
func MarshalOptions(value any, opts *EncoderOptions) ([]byte, error)
```

#### Encoder - 流式编码

```go
type Encoder struct {
    // 内部字段
}

func NewEncoder(w io.Writer) *Encoder
func NewEncoderWriter(w *Writer) *Encoder
func (e *Encoder) Encode(value any) error
```

### 解码功能

#### Unmarshal() - 反序列化

```go
func Unmarshal(data []byte, v any) error
func UnmarshalOptions(data []byte, v any, opts *DecoderOptions) error
```

#### Decoder - 流式解码

```go
type Decoder struct {
    // 内部字段
}

func NewDecoder(r io.Reader) *Decoder
func NewDecoderFromBytes(data []byte) *Decoder
func (d *Decoder) Decode(v any) error
func (d *Decoder) CheckFinish() error
```

### 读写器

#### Writer - 写入器

```go
type Writer struct {
    // 内部字段
}

func NewWriter(inner io.Writer) *Writer
func NewWriterFormat(inner io.Writer, format Format) *Writer
func NewWriterConfig(inner io.Writer, c WriterConfig) *Writer

// 写入方法
func (w *Writer) BeginMap()
func (w *Writer) EndMap()
func (w *Writer) BeginList()
func (w *Writer) EndList()
func (w *Writer) BeginAttrs()
func (w *Writer) EndAttrs()
func (w *Writer) MapKeyString(k string)
func (w *Writer) MapKeyBytes(k []byte)
func (w *Writer) String(s string)
func (w *Writer) Bytes(b []byte)
func (w *Writer) Int64(i int64)
func (w *Writer) Uint64(u uint64)
func (w *Writer) Float64(f float64)
func (w *Writer) Bool(b bool)
func (w *Writer) Entity()
func (w *Writer) RawNode(raw []byte)
func (w *Writer) Any(v any)
func (w *Writer) Finish() error
```

#### Reader - 读取器

```go
type Reader struct {
    // 内部字段
}

func NewReader(r io.Reader) *Reader
func NewReaderFromBytes(data []byte) *Reader

// 读取方法
func (r *Reader) Next(allowAttributes bool) (Event, error)
func (r *Reader) NextRawValue() ([]byte, error)
func (r *Reader) Type() Type
func (r *Reader) Bool() bool
func (r *Reader) Int64() int64
func (r *Reader) Uint64() uint64
func (r *Reader) Float64() float64
func (r *Reader) Bytes() []byte
func (r *Reader) String() string
```

## 结构体标签

`yson` 包支持丰富的结构体标签配置：

```go
type User struct {
    ID       int64  `yson:"user_id"`                    // 重命名字段
    Name     string `yson:"name,attr"`                  // 作为属性
    Active   bool   `yson:",omitempty"`                 // 空值时省略
    Data     string `yson:",value"`                     // 替换整个结构体的值
    Internal string `yson:"-"`                          // 忽略字段
    Special  string `yson:"-,"`                         // 字段名为 "-"
}
```

### 标签选项

- `name`: 指定字段名称
- `attr`: 字段作为属性
- `omitempty`: 空值时省略
- `value`: 字段值替换整个结构体
- `-`: 忽略字段
- `-,"`: 字段名为 "-"

## 接口支持

### 编码接口

```go
// Marshaler - 返回 YSON 字节
type Marshaler interface {
    MarshalYSON() ([]byte, error)
}

// StreamMarshaler - 流式编码
type StreamMarshaler interface {
    MarshalYSON(*Writer) error
}
```

### 解码接口

```go
// Unmarshaler - 从 YSON 字节解码
type Unmarshaler interface {
    UnmarshalYSON([]byte) error
}

// StreamUnmarshaler - 流式解码
type StreamUnmarshaler interface {
    UnmarshalYSON(*Reader) error
}
```

## 使用示例

### 基本编解码

```go
package main

import (
    "fmt"
    "go.ytsaurus.tech/yt/go/yson"
)

type User struct {
    ID    int64  `yson:"user_id"`
    Name  string `yson:"name"`
    Email string `yson:"email"`
}

func main() {
    // 编码
    user := User{
        ID:    1,
        Name:  "Alice",
        Email: "alice@example.com",
    }

    data, err := yson.Marshal(user)
    if err != nil {
        panic(err)
    }

    fmt.Printf("YSON: %s\n", string(data))

    // 解码
    var decodedUser User
    err = yson.Unmarshal(data, &decodedUser)
    if err != nil {
        panic(err)
    }

    fmt.Printf("Decoded: %+v\n", decodedUser)
}
```

### 不同格式的序列化

```go
package main

import (
    "fmt"
    "go.ytsaurus.tech/yt/go/yson"
)

func main() {
    data := map[string]interface{}{
        "name": "test",
        "count": 42,
        "active": true,
    }

    // 文本格式
    textData, _ := yson.MarshalFormat(data, yson.FormatText)
    fmt.Printf("Text: %s\n", string(textData))

    // 二进制格式
    binaryData, _ := yson.MarshalFormat(data, yson.FormatBinary)
    fmt.Printf("Binary length: %d\n", len(binaryData))

    // 美化格式
    prettyData, _ := yson.MarshalFormat(data, yson.FormatPretty)
    fmt.Printf("Pretty: %s\n", string(prettyData))
}
```

### 流式处理

```go
package main

import (
    "bytes"
    "fmt"
    "go.ytsaurus.tech/yt/go/yson"
)

func main() {
    // 流式编码
    var buf bytes.Buffer
    writer := yson.NewWriter(&buf)

    writer.BeginMap()
    writer.MapKeyString("users")
    writer.BeginList()

    // 添加用户
    writer.BeginMap()
    writer.MapKeyString("id")
    writer.Int64(1)
    writer.MapKeyString("name")
    writer.String("Alice")
    writer.EndMap()

    writer.EndList()
    writer.EndMap()

    err := writer.Finish()
    if err != nil {
        panic(err)
    }

    fmt.Printf("Streamed YSON: %s\n", buf.String())
}
```

### 自定义编解码

```go
package main

import (
    "fmt"
    "go.ytsaurus.tech/yt/go/yson"
)

type Timestamp struct {
    Seconds int64
    Nanos   int32
}

// 实现 Marshaler 接口
func (t Timestamp) MarshalYSON() ([]byte, error) {
    return yson.Marshal(fmt.Sprintf("%d.%09d", t.Seconds, t.Nanos))
}

// 实现 Unmarshaler 接口
func (t *Timestamp) UnmarshalYSON(data []byte) error {
    var s string
    if err := yson.Unmarshal(data, &s); err != nil {
        return err
    }

    // 解析时间戳字符串
    _, err := fmt.Sscanf(s, "%d.%09d", &t.Seconds, &t.Nanos)
    return err
}

func main() {
    ts := Timestamp{
        Seconds: 1640995200,
        Nanos:   123456789,
    }

    // 编码
    data, err := yson.Marshal(ts)
    if err != nil {
        panic(err)
    }

    fmt.Printf("Custom YSON: %s\n", string(data))

    // 解码
    var decoded Timestamp
    err = yson.Unmarshal(data, &decoded)
    if err != nil {
        panic(err)
    }

    fmt.Printf("Decoded: %+v\n", decoded)
}
```

### 属性处理

```go
package main

import (
    "fmt"
    "go.ytsaurus.tech/yt/go/yson"
)

type File struct {
    Path     string `yson:",value"`
    Size     int64  `yson:"size,attr"`
    Modified string `yson:"modified,attr"`
    Owner    string `yson:"owner,attr"`
}

func main() {
    file := File{
        Path:     "/tmp/data.txt",
        Size:     1024,
        Modified: "2023-01-01T00:00:00Z",
        Owner:    "alice",
    }

    data, err := yson.Marshal(file)
    if err != nil {
        panic(err)
    }

    fmt.Printf("File with attributes: %s\n", string(data))

    // 解码
    var decodedFile File
    err = yson.Unmarshal(data, &decodedFile)
    if err != nil {
        panic(err)
    }

    fmt.Printf("Decoded file: %+v\n", decodedFile)
}
```

## 高级功能

### 事件驱动处理

```go
package main

import (
    "bytes"
    "fmt"
    "go.ytsaurus.tech/yt/go/yson"
)

func processYSON(data []byte) error {
    reader := yson.NewReaderFromBytes(data)

    for {
        event, err := reader.Next(false)
        if err != nil {
            return err
        }

        switch event {
        case yson.EventEOF:
            return nil

        case yson.EventBeginMap:
            fmt.Println("开始映射")

        case yson.EventEndMap:
            fmt.Println("结束映射")

        case yson.EventKey:
            fmt.Printf("键: %s\n", reader.String())

        case yson.EventLiteral:
            switch reader.Type() {
            case yson.TypeString:
                fmt.Printf("字符串值: %s\n", reader.String())
            case yson.TypeInt64:
                fmt.Printf("整数值: %d\n", reader.Int64())
            case yson.TypeBool:
                fmt.Printf("布尔值: %t\n", reader.Bool())
            }
        }
    }
}

func main() {
    data := []byte("{name=test;count=42;active=%true;}")

    err := processYSON(data)
    if err != nil {
        panic(err)
    }
}
```

### 配置选项

```go
package main

import (
    "fmt"
    "go.ytsaurus.tech/yt/go/yson"
)

func main() {
    // 使用编码选项
    opts := &yson.EncoderOptions{
        SupportYPAPIMaps: true, // 支持 YPAPI 映射格式
    }

    data, err := yson.MarshalOptions(map[int]string{1: "one"}, opts)
    if err != nil {
        panic(err)
    }

    fmt.Printf("YSON with options: %s\n", string(data))
}
```

## 性能优化

### 内存优化

```go
package main

import (
    "bytes"
    "go.ytsaurus.tech/yt/go/yson"
)

func optimizedEncoding() {
    // 重用缓冲区
    var buf bytes.Buffer
    writer := yson.NewWriter(&buf)

    // 批量写入
    writer.BeginMap()
    defer writer.EndMap()

    // 流式写入减少内存分配
    for i := 0; i < 1000; i++ {
        writer.MapKeyString(fmt.Sprintf("item_%d", i))
        writer.Int64(int64(i))
    }

    writer.Finish()
}
```

### 类型推断优化

```go
package main

import (
    "go.ytsaurus.tech/yt/go/yson"
    "go.ytsaurus.tech/yt/go/yson/infertype"
)

func optimizedDecoding(data []byte) {
    // 使用类型推断优化
    var value interface{}

    // 快速类型检查
    infertype.Infer(data)

    // 解码
    yson.Unmarshal(data, &value)
}
```

## 错误处理

### 常见错误类型

```go
// 类型错误
type TypeError struct {
    UserType reflect.Type
    YSONType Type
}

// 不支持的类型错误
type UnsupportedTypeError struct {
    Type reflect.Type
}

// 整数溢出错误
var ErrIntegerOverflow = errors.New("yson: integer overflow")
```

### 错误处理最佳实践

```go
package main

import (
    "fmt"
    "go.ytsaurus.tech/yt/go/yson"
    "go.ytsaurus.tech/yt/go/yson/error"
)

func safeUnmarshal(data []byte, v interface{}) error {
    err := yson.Unmarshal(data, v)
    if err != nil {
        // 检查具体错误类型
        if yson.IsTypeError(err) {
            return fmt.Errorf("类型不匹配: %w", err)
        }
        if yson.IsOverflowError(err) {
            return fmt.Errorf("数值溢出: %w", err)
        }
        return fmt.Errorf("YSON 解码失败: %w", err)
    }
    return nil
}
```

## 最佳实践

### 1. 选择合适的格式

```go
// 存储和网络传输 - 使用二进制格式
binaryData, _ := yson.MarshalFormat(data, yson.FormatBinary)

// 调试和日志 - 使用文本格式
textData, _ := yson.MarshalFormat(data, yson.FormatText)

// 配置文件 - 使用美化格式
prettyData, _ := yson.MarshalFormat(data, yson.FormatPretty)
```

### 2. 使用流式处理处理大数据

```go
// 大数据处理使用流式 API
func processLargeData(writer io.Writer, items []interface{}) error {
    w := yson.NewWriter(writer)

    w.BeginList()
    for _, item := range items {
        w.Any(item)
    }
    w.EndList()

    return w.Finish()
}
```

### 3. 实现自定义编解码

```go
// 为复杂类型实现自定义编解码接口
type ComplexType struct {
    // 字段定义
}

func (c *ComplexType) MarshalYSON() ([]byte, error) {
    // 自定义编码逻辑
}

func (c *ComplexType) UnmarshalYSON(data []byte) error {
    // 自定义解码逻辑
}
```

## 注意事项

1. **类型安全**：确保类型匹配以避免运行时错误
2. **性能考虑**：大数据集使用流式处理
3. **内存管理**：注意内存分配和释放
4. **并发安全**：读写器不是并发安全的
5. **版本兼容**：注意 YSON 格式的版本兼容性

## 相关依赖

- `go.ytsaurus.tech/yt/go/yson/infertype`: 类型推断支持
- `go.ytsaurus.tech/yt/go/yson/error`: 错误处理工具

## 更多信息

详细的 YSON 格式规范和 API 文档请参考 [YTsaurus 文档](https://ytsaurus.tech/docs/en/user-guide/storage/yson)。