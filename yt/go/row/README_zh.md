# Row 行数据处理模块

Row 模块定义了 YTsaurus 和 Go 数据类型之间的转换机制，用于处理表数据的序列化和反序列化操作。

## 概述

该模块提供了 YTsaurus 行数据与 Go 结构体之间的映射和转换功能，支持字段级别的配置和自定义处理规则。通过结构体标签可以控制字段的映射行为。

## 核心组件

### FieldTag 结构体

```go
type FieldTag struct {
    Name      string    // 字段名称，对应 YTsaurus 表中的列名
    OmitEmpty bool      // 是否在字段为空值时忽略
}
```

### ParseTag 函数

```go
func ParseTag(fieldName, tag string) (*FieldTag, error)
```

解析结构体标签字符串，返回字段标签配置。

**参数:**
- `fieldName`: 字段名称
- `tag`: 标签字符串

**返回:**
- `*FieldTag`: 解析后的字段标签配置
- `error`: 解析错误

## 使用示例

### 基本结构体映射

```go
package main

import (
    "encoding/json"
    "fmt"
    "log"

    "go.ytsaurus.com/yt/go/row"
)

// 定义用户数据结构
type User struct {
    ID       int64  `yt:"id"`
    Name     string `yt:"name"`
    Email    string `yt:"email,omitempty"`
    Age      int    `yt:"age,omitempty"`
    IsActive bool   `yt:"is_active"`
}

func main() {
    user := User{
        ID:       12345,
        Name:     "张三",
        Email:    "",  // 空值将被忽略
        Age:      25,
        IsActive: true,
    }

    // 处理结构体字段
    fmt.Printf("用户数据: %+v\n", user)

    // 可以配合 JSON 进行序列化
    jsonData, err := json.MarshalIndent(user, "", "  ")
    if err != nil {
        log.Fatal(err)
    }

    fmt.Println("JSON 输出:")
    fmt.Println(string(jsonData))
}
```

### 标签解析示例

```go
package main

import (
    "fmt"
    "reflect"
    "strings"

    "go.ytsaurus.com/yt/go/row"
)

type ExampleStruct struct {
    Field1 string `yt:"field_name"`
    Field2 int    `yt:"field_number,omitempty"`
    Field3 bool   `yt:"is_active"`
}

func processStructTags() {
    t := reflect.TypeOf(ExampleStruct{})

    for i := 0; i < t.NumField(); i++ {
        field := t.Field(i)
        tag := field.Tag.Get("yt")

        if tag != "" {
            fmt.Printf("字段: %s, 标签: %s\n", field.Name, tag)

            // 解析标签
            fieldTag, err := row.ParseTag(field.Name, tag)
            if err != nil {
                fmt.Printf("解析标签失败: %v\n", err)
                continue
            }

            if fieldTag != nil {
                fmt.Printf("  - 映射名: %s\n", fieldTag.Name)
                fmt.Printf("  - 忽略空值: %t\n", fieldTag.OmitEmpty)
            }
        }
    }
}

func main() {
    processStructTags()
}
```

### 数据转换示例

```go
package main

import (
    "fmt"
    "reflect"
    "time"

    "go.ytsaurus.com/yt/go/row"
)

// 定义复杂的行数据结构
type TableRow struct {
    Key         string    `yt:"key"`
    Value       float64   `yt:"value"`
    Timestamp   time.Time `yt:"timestamp"`
    Description string    `yt:"description,omitempty"`
    Tags        []string  `yt:"tags,omitempty"`
}

// 模拟行数据转换为 YTsaurus 格式
func convertToYTRow(data interface{}) map[string]interface{} {
    v := reflect.ValueOf(data)
    t := reflect.TypeOf(data)

    if t.Kind() == reflect.Ptr {
        v = v.Elem()
        t = t.Elem()
    }

    result := make(map[string]interface{})

    for i := 0; i < t.NumField(); i++ {
        field := t.Field(i)
        fieldValue := v.Field(i)

        tag := field.Tag.Get("yt")
        if tag == "" {
            continue
        }

        // 解析标签
        fieldTag, err := row.ParseTag(field.Name, tag)
        if err != nil {
            fmt.Printf("解析字段 %s 标签失败: %v\n", field.Name, err)
            continue
        }

        if fieldTag == nil {
            continue
        }

        // 检查是否应该忽略空值
        if fieldTag.OmitEmpty && isZeroValue(fieldValue) {
            continue
        }

        // 添加到结果中
        result[fieldTag.Name] = fieldValue.Interface()
    }

    return result
}

// 检查是否为零值
func isZeroValue(v reflect.Value) bool {
    switch v.Kind() {
    case reflect.String:
        return v.String() == ""
    case reflect.Int, reflect.Int8, reflect.Int16, reflect.Int32, reflect.Int64:
        return v.Int() == 0
    case reflect.Uint, reflect.Uint8, reflect.Uint16, reflect.Uint32, reflect.Uint64:
        return v.Uint() == 0
    case reflect.Float32, reflect.Float64:
        return v.Float() == 0
    case reflect.Bool:
        return !v.Bool()
    case reflect.Slice, reflect.Array, reflect.Map:
        return v.Len() == 0
    case reflect.Ptr, reflect.Interface:
        return v.IsNil()
    default:
        return false
    }
}

func main() {
    row := TableRow{
        Key:         "row_123",
        Value:       42.5,
        Timestamp:   time.Now(),
        Description: "示例行数据",
        Tags:        []string{"tag1", "tag2"},
    }

    ytRow := convertToYTRow(row)
    fmt.Printf("YTsaurus 行数据: %+v\n", ytRow)

    // 测试空值忽略
    emptyRow := TableRow{
        Key:       "empty_row",
        Value:     0,
        Timestamp: time.Time{},
    }

    emptyYTRow := convertToYTRow(emptyRow)
    fmt.Printf("空值行数据: %+v\n", emptyYTRow)
}
```

## 标签语法

### 基本语法

```
`yt:"column_name"`
```

### 选项语法

```
`yt:"column_name,option1,option2"`
```

### 支持的选项

- `omitempty` 或 `omitempty`: 当字段值为空时，忽略该字段

### 标签示例

```go
type ExampleStruct struct {
    // 基本映射
    ID       int64  `yt:"id"`

    // 空值忽略
    Email    string `yt:"email,omitempty"`

    // 多个选项
    Status   string `yt:"status,omitempty"`

    // 下划线命名映射
    IsActive bool   `yt:"is_active"`

    // 无标签（忽略）
    InternalData string
}
```

## 数据类型映射

| Go 类型          | YTsaurus 类型   | 说明 |
|-----------------|----------------|------|
| int, int32      | int64          | 整数类型 |
| int64           | int64          | 64位整数 |
| uint, uint32    | uint64         | 无符号整数 |
| uint64          | uint64         | 64位无符号整数 |
| float32         | double         | 单精度浮点数 |
| float64         | double         | 双精度浮点数 |
| bool            | boolean        | 布尔值 |
| string          | string         | 字符串 |
| []byte          | string         | 字节数组转字符串 |
| time.Time       | timestamp      | 时间戳 |
| []T             | list<T>        | 数组类型 |
| map[K]V         | dict<K,V>      | 字典类型 |

## 最佳实践

### 1. 字段命名

```go
// 推荐：使用下划线命名
type User struct {
    UserID    int64  `yt:"user_id"`     // ✅ 清晰的映射
    CreatedAt int64  `yt:"created_at"`  // ✅ 标准命名
}

// 避免：与 Go 命名不一致
type User struct {
    UserID int64 `yt:"UserID"`  // ❌ 与 YTsaurus 命名规范不符
}
```

### 2. 空值处理

```go
type Product struct {
    ID          int64   `yt:"id"`
    Name        string  `yt:"name"`
    Description string  `yt:"description,omitempty"`  // 可选字段
    Price       float64 `yt:"price"`
    Discount    float64 `yt:"discount,omitempty"`     // 可选字段
}
```

### 3. 时间处理

```go
type Event struct {
    ID        int64     `yt:"id"`
    Name      string    `yt:"name"`
    CreatedAt time.Time `yt:"created_at"`  // 自动转换为时间戳
    UpdatedAt *time.Time `yt:"updated_at,omitempty"`  // 可选时间
}
```

### 4. 复合类型

```go
type ComplexRow struct {
    ID       int64            `yt:"id"`
    Tags     []string         `yt:"tags,omitempty"`
    Metadata map[string]interface{} `yt:"metadata,omitempty"`
    Config   []ConfigItem     `yt:"config,omitempty"`
}

type ConfigItem struct {
    Key   string `yt:"key"`
    Value string `yt:"value"`
}
```

## 性能考虑

1. **反射开销**: 模块使用反射机制，在性能敏感场景中需要注意
2. **内存分配**: 频繁的映射操作会产生额外的内存分配
3. **缓存优化**: 对于重复使用的类型，可以考虑缓存反射信息

## 错误处理

常见错误及处理方式：

```go
// 标签解析错误
fieldTag, err := row.ParseTag(fieldName, tag)
if err != nil {
    return fmt.Errorf("解析字段标签失败: %w", err)
}

// 类型不匹配错误
if !fieldValue.Type().AssignableTo(targetType) {
    return fmt.Errorf("类型不匹配: %v -> %v",
        fieldValue.Type(), targetType)
}
```

## 扩展和自定义

### 自定义标签解析

```go
// 可以扩展 ParseTag 函数以支持更多选项
func ParseCustomTag(fieldName, tag string) (*row.FieldTag, error) {
    // 解析自定义标签格式
    // 例如: yt:"name,required,format=email"

    baseTag, err := row.ParseTag(fieldName, tag)
    if err != nil {
        return nil, err
    }

    // 添加自定义逻辑

    return baseTag, nil
}
```

## 注意事项

1. **标签格式**: 确保标签格式正确，使用逗号分隔选项
2. **字段可见性**: 只有导出的字段（首字母大写）才会被处理
3. **空值判断**: 不同类型的空值判断逻辑可能有所不同
4. **并发安全**: 当前实现不是并发安全的，需要在应用层处理并发问题

## 发展计划

该模块目前处于早期阶段，计划在未来版本中添加以下功能：

- 更丰富的标签选项支持
- 自动类型推断和转换
- 性能优化和缓存机制
- 更完善的错误处理
- 批量操作支持