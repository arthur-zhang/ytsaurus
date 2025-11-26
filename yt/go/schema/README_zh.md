# Schema 表结构定义模块

Schema 模块定义了 YTsaurus 表的结构模式，提供了表结构定义、类型推断、模式转换和验证等功能。

## 概述

该模块是 YTsaurus Go 客户端的核心组件之一，负责：

- 定义 YTsaurus 表的结构模式
- 提供 Go 类型到 YTsaurus 类型的自动推断
- 支持传统模式和新版本复杂类型系统的转换
- 处理 Protobuf 模式的相互转换
- 提供模式合并、比较等实用功能

## 核心组件

### 基础类型系统

#### 基本数据类型

```go
type Type string

const (
    // 整数类型
    TypeInt8   Type = "int8"
    TypeInt16  Type = "int16"
    TypeInt32  Type = "int32"
    TypeInt64  Type = "int64"
    TypeUint8  Type = "uint8"
    TypeUint16 Type = "uint16"
    TypeUint32 Type = "uint32"
    TypeUint64 Type = "uint64"

    // 浮点类型
    TypeFloat32 Type = "float"
    TypeFloat64 Type = "double"

    // 字符串和字节类型
    TypeBytes  Type = "string"   // 字节数组
    TypeString Type = "utf8"     // UTF-8 字符串

    // 布尔和特殊类型
    TypeBoolean Type = "boolean"
    TypeAny     Type = "any"
    TypeNull    Type = "null"

    // 时间类型
    TypeDate      Type = "date"
    TypeDatetime  Type = "datetime"
    TypeTimestamp Type = "timestamp"
    TypeInterval  Type = "interval"
)
```

#### 复杂类型系统

```go
type ComplexType interface {
    isType()
}

// 可选类型
type Optional struct {
    Item ComplexType `yson:"item"`
}

// 列表类型
type List struct {
    Item ComplexType `yson:"item"`
}

// 结构体类型
type Struct struct {
    Members []StructMember `yson:"members"`
}

type StructMember struct {
    Name string      `yson:"name"`
    Type ComplexType `yson:"type"`
}

// 元组类型
type Tuple struct {
    Elements []TupleElement `yson:"elements"`
}

// 字典类型
type Dict struct {
    Key   ComplexType `yson:"key"`
    Value ComplexType `yson:"value"`
}

// 变体类型
type Variant struct {
    Members  []StructMember `yson:"members"`
    Elements []TupleElement `yson:"elements"`
}

// 标签类型
type Tagged struct {
    Tag  string      `yson:"tag"`
    Item ComplexType `yson:"item"`
}

// 十进制类型
type Decimal struct {
    Precision int `yson:"precision"`
    Scale     int `yson:"scale"`
}
```

### Column 结构体

```go
type Column struct {
    Name string `yson:"name"`

    // 传统模式字段
    Type     Type `yson:"type,omitempty"`
    Required bool `yson:"required,omitempty"`

    // 新版复杂类型
    ComplexType ComplexType `yson:"type_v3,omitempty"`

    // 排序和索引
    SortOrder SortOrder `yson:"sort_order,omitempty"`

    // 高级属性
    Lock       string            `yson:"lock,omitempty"`
    Expression string            `yson:"expression,omitempty"`
    Aggregate  AggregateFunction `yson:"aggregate,omitempty"`
    Group      string            `yson:"group,omitempty"`
}
```

#### SortOrder 排序顺序

```go
type SortOrder string

const (
    SortNone       SortOrder = ""           // 不排序
    SortAscending  SortOrder = "ascending"  // 升序
    SortDescending SortOrder = "descending" // 降序
)
```

#### AggregateFunction 聚合函数

```go
type AggregateFunction string

const (
    AggregateSum   AggregateFunction = "sum"
    AggregateMin   AggregateFunction = "min"
    AggregateMax   AggregateFunction = "max"
    AggregateFirst AggregateFunction = "first"
)
```

### Schema 结构体

```go
type Schema struct {
    Strict     *bool   `yson:"strict,attr,omitempty"` // 是否严格模式
    UniqueKeys bool    `yson:"unique_keys,attr"`      // 键值是否唯一
    Columns    []Column `yson:",value"`               // 列定义
}
```

## 核心功能

### 1. 模式推断（Inference）

从 Go 结构体自动推断 YTsaurus 表结构：

```go
// 从结构体推断模式
func Infer(value any) (Schema, error)
func MustInfer(value any) Schema // panic on error

// 从 Map 推断模式
func InferMap(value any) (Schema, error)
func MustInferMap(value any) Schema // panic on error
```

### 2. 模式操作

```go
// 添加列
func (s Schema) Append(column ...Column) Schema
func (s Schema) Prepend(column ...Column) Schema

// 复制模式
func (s Schema) Copy() Schema

// 获取键列
func (s Schema) KeyColumns() []string

// 设置排序列
func (s Schema) SortedBy(keyColumns ...string) Schema

// 模式标准化
func (s Schema) Normalize() Schema

// 模式比较
func (s Schema) Equal(other Schema) bool

// 设置唯一键
func (s Schema) WithUniqueKeys() Schema

// 检查是否为严格模式
func (s *Schema) IsStrict() bool
```

### 3. 模式合并

```go
func MergeSchemas(lhs, rhs Schema) Schema
```

### 4. Protobuf 转换

```go
func ConvertFromProto(rpcSchema *rpc_proxy.TTableSchema) (Schema, error)
```

### 5. 列类型标准化

```go
func (c Column) NormalizeType() Column
```

## 使用示例

### 基本模式定义

```go
package main

import (
    "fmt"
    "log"

    "go.ytsaurus.com/yt/go/schema"
)

func main() {
    // 创建表结构
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
            {
                Name:     "created_at",
                Type:     schema.TypeTimestamp,
                Required: true,
            },
        },
    }

    fmt.Printf("表结构: %+v\n", tableSchema)

    // 获取键列
    keys := tableSchema.KeyColumns()
    fmt.Printf("键列: %v\n", keys)
}
```

### 从结构体推断模式

```go
package main

import (
    "fmt"
    "log"

    "go.ytsaurus.com/yt/go/schema"
    "go.ytsaurus.com/yt/go/yson"
)

// 用户结构体
type User struct {
    ID       int64  `yson:"id,key"`
    Name     string `yson:"name"`
    Email    string `yson:"email,omitempty"`
    Age      int    `yson:"age,omitempty"`
    IsActive bool   `yson:"is_active"`
    Created  string `yson:"created_at"`
}

func main() {
    user := User{}

    // 从结构体推断模式
    schema, err := schema.Infer(user)
    if err != nil {
        log.Fatalf("推断模式失败: %v", err)
    }

    fmt.Printf("推断的模式:\n")
    for i, col := range schema.Columns {
        fmt.Printf("  %d. %s: %s (必需: %t, 排序: %s)\n",
            i+1, col.Name, col.Type, col.Required, col.SortOrder)
    }
}
```

### 复杂类型使用

```go
package main

import (
    "fmt"
    "go.ytsaurus.com/yt/go/schema"
)

func main() {
    // 创建包含复杂类型的列
    complexColumns := []schema.Column{
        {
            Name: "id",
            ComplexType: schema.TypeInt64,
        },
        {
            Name: "optional_field",
            ComplexType: schema.Optional{
                Item: schema.TypeString,
            },
        },
        {
            Name: "string_list",
            ComplexType: schema.List{
                Item: schema.TypeString,
            },
        },
        {
            Name: "user_data",
            ComplexType: schema.Struct{
                Members: []schema.StructMember{
                    {
                        Name: "name",
                        Type: schema.TypeString,
                    },
                    {
                        Name: "age",
                        Type: schema.TypeInt32,
                    },
                },
            },
        },
        {
            Name: "tags",
            ComplexType: schema.Dict{
                Key:   schema.TypeString,
                Value: schema.TypeString,
            },
        },
    }

    tableSchema := schema.Schema{
        Strict:  ptr.Bool(true),
        Columns: complexColumns,
    }

    fmt.Printf("复杂类型模式:\n")
    for _, col := range tableSchema.Columns {
        fmt.Printf("- %s: %T\n", col.Name, col.ComplexType)
    }
}
```

### 模式操作和转换

```go
package main

import (
    "fmt"
    "go.ytsaurus.com/yt/go/schema"
)

func main() {
    // 基础模式
    baseSchema := schema.Schema{
        Columns: []schema.Column{
            {Name: "id", Type: schema.TypeInt64, Required: true},
            {Name: "name", Type: schema.TypeString, Required: true},
        },
    }

    // 添加列
    extendedSchema := baseSchema.Append(
        schema.Column{Name: "email", Type: schema.TypeString},
        schema.Column{Name: "age", Type: schema.TypeInt32},
    )

    // 设置排序列
    sortedSchema := extendedSchema.SortedBy("id", "name")

    // 标准化模式
    normalizedSchema := sortedSchema.Normalize()

    fmt.Printf("原始模式列数: %d\n", len(baseSchema.Columns))
    fmt.Printf("扩展模式列数: %d\n", len(extendedSchema.Columns))
    fmt.Printf("键列: %v\n", normalizedSchema.KeyColumns())
}
```

### 模式合并

```go
package main

import (
    "fmt"
    "go.ytsaurus.com/yt/go/schema"
)

func main() {
    // 第一个模式
    schema1 := schema.Schema{
        Columns: []schema.Column{
            {Name: "id", Type: schema.TypeInt64, Required: true},
            {Name: "name", Type: schema.TypeString, Required: true},
            {Name: "age", Type: schema.TypeInt32},
        },
    }

    // 第二个模式
    schema2 := schema.Schema{
        Columns: []schema.Column{
            {Name: "id", Type: schema.TypeInt64, Required: true},
            {Name: "name", Type: schema.TypeString, Required: false}, // 类型冲突
            {Name: "email", Type: schema.TypeString},
        },
    }

    // 合并模式
    mergedSchema := schema.MergeSchemas(schema1, schema2)

    fmt.Printf("合并后的模式:\n")
    for _, col := range mergedSchema.Columns {
        fmt.Printf("- %s: %s (必需: %t)\n",
            col.Name, col.Type, col.Required)
    }
}
```

## Go 类型到 YTsaurus 类型映射

### 基本类型映射

| Go 类型 | YTsaurus 类型 | 说明 |
|---------|---------------|------|
| int, int16, int32, int64 | int64 | 整数（int8/uint8 不支持） |
| uint, uint16, uint32, uint64 | uint64 | 无符号整数 |
| float32 | float | 单精度浮点 |
| float64 | double | 双精度浮点 |
| bool | boolean | 布尔值 |
| string | utf8 | UTF-8 字符串 |
| []byte | string | 字节数组 |
| time.Time | timestamp | 时间戳 |

### 接口实现映射

| 接口 | YTsaurus 类型 | 说明 |
|------|---------------|------|
| encoding.TextMarshaler | utf8 | 文本序列化 |
| encoding.BinaryMarshaler | string | 二进制序列化 |

### 特殊类型

```go
// YTsaurus 特殊时间类型
type Date int32       // 日期
type Datetime int64   // 日期时间
type Timestamp int64  // 时间戳
type Interval int64   // 时间间隔
```

### 结构体推断规则

1. **字段可见性**: 只处理导出字段（首字母大写）
2. **标签支持**: 使用 `yson` 标签控制映射
3. **指针处理**: 指针类型自动转为 Optional 类型
4. **嵌套结构**: 嵌套字段会被展开
5. **循环引用**: 自动检测并转为 Any 类型

## 标签说明

### yson 标签

```go
type User struct {
    ID    int64  `yson:"id,key"`       // 列名，同时标记为键列
    Name  string `yson:"name"`         // 指定列名
    Email string `yson:"email,omitempty"` // 可选字段
    Age   int    `yson:"age"`          // 普通字段
}
```

标签选项：
- `"column_name"` - 指定列名
- `"column_name,key"` - 标记为键列
- `"column_name,omitempty"` - 可选字段

### ytgroup 标签

```go
type Row struct {
    ID   int64   `yson:"id" ytgroup:"primary"`
    Data []byte  `yson:"data" ytgroup:"blob"`
    Meta string  `yson:"meta" ytgroup:"metadata"`
}
```

用于指定列组，在优化存储时同组列会被存储在一起。

## 最佳实践

### 1. 类型选择

```go
// ✅ 推荐：使用明确的类型
type User struct {
    ID        int64  `yson:"id,key"`
    Name      string `yson:"name"`
    CreatedAt int64  `yson:"created_at"` // 使用时间戳
}

// ❌ 避免：类型不明确
type User struct {
    ID    interface{} `yson:"id"`
    Name  interface{} `yson:"name"`
    Date  interface{} `yson:"date"`
}
```

### 2. 可选字段处理

```go
// ✅ 推荐：明确区分必需和可选字段
type Record struct {
    ID    int64   `yson:"id,key"`
    Title string  `yson:"title"`
    Desc  *string `yson:"description,omitempty"` // 指针表示可选
}

// ❌ 避免：所有字段都是可选的
type Record struct {
    ID    int64  `yson:"id"`
    Title string `yson:"title"`
    Desc  string `yson:"description"`
}
```

### 3. 复杂类型使用

```go
// ✅ 推荐：合理使用复杂类型
type ComplexRow struct {
    ID      int64                    `yson:"id"`
    Tags    []string                 `yson:"tags"`         // List
    Meta    map[string]interface{}   `yson:"metadata"`     // Dict
    Profile UserProfile              `yson:"profile"`      // Struct
}

// ❌ 避免：过度复杂的嵌套
type TooComplex struct {
    Data map[string]map[string][]struct {
        Field1 interface{}
        Field2 interface{}
    }
}
```

### 4. 模式标准化

```go
// 总是在使用前标准化模式
schema := schema.Infer(data).Normalize()

// 检查严格模式
if !schema.IsStrict() {
    log.Printf("警告：模式不是严格模式")
}
```

## 性能考虑

1. **反射开销**: 模式推断使用反射，性能敏感场景建议缓存结果
2. **内存分配**: 复杂类型的推断会产生临时对象
3. **深度嵌套**: 过深的结构体嵌套可能影响性能

## 错误处理

常见错误及处理：

```go
schema, err := schema.Infer(data)
if err != nil {
    switch {
    case xerrors.Is(err, schema.ErrUnsupportedType):
        log.Printf("不支持的类型: %v", err)
    case xerrors.Is(err, schema.ErrCircularReference):
        log.Printf("循环引用: %v", err)
    default:
        log.Printf("模式推断失败: %v", err)
    }
}
```

## 调试和验证

### 模式验证

```go
func validateSchema(s schema.Schema) error {
    // 检查键列
    if len(s.KeyColumns()) == 0 {
        return fmt.Errorf("缺少键列")
    }

    // 检查列名重复
    names := make(map[string]bool)
    for _, col := range s.Columns {
        if names[col.Name] {
            return fmt.Errorf("重复列名: %s", col.Name)
        }
        names[col.Name] = true
    }

    return nil
}
```

### 模式打印

```go
func printSchema(s schema.Schema) {
    fmt.Printf("Schema (strict=%v, unique_keys=%v):\n",
        s.IsStrict(), s.UniqueKeys)

    for _, col := range s.Columns {
        fmt.Printf("  %-20s %-15s required=%v sort=%s\n",
            col.Name, col.Type, col.Required, col.SortOrder)
    }
}
```

## 注意事项

1. **类型兼容性**: 确保类型推断结果与预期一致
2. **版本兼容性**: 注意新旧版本类型系统的差异
3. **标签使用**: 正确使用结构体标签控制映射行为
4. **性能优化**: 合理使用缓存避免重复推断
5. **错误处理**: 妥善处理推断过程中的各种错误情况

## 扩展功能

该模块还支持以下高级功能：

- **时间类型转换**: 提供专门的 YTsaurus 时间类型
- **Decimal 类型**: 支持高精度数值计算
- **Variant 类型**: 支持变体类型和联合类型
- **Tagged 类型**: 支持带标签的类型系统

详细的高级功能使用请参考相关测试文件和示例代码。