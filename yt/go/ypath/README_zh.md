# YPath - YTsaurus 路径处理库

## 概述

`ypath` 包提供了处理 YTsaurus 路径的完整功能。YPath 是 YTsaurus 中用于定位和引用 Cypress 节点的路径系统，支持简单路径和丰富路径两种形式。

## 路径类型

### 1. 简单路径 (Path)

简单路径是基于字符串的路径表示，适用于基本的路径操作：

```go
type Path string
```

#### 特点
- 轻量级，基于字符串实现
- 支持链式操作构建复杂路径
- 提供丰富的路径操作方法
- 适合简单的路径构建和操作

### 2. 丰富路径 (Rich)

丰富路径提供了更复杂的路径表示，支持属性、范围选择等高级功能：

```go
type Rich struct {
    Path Path `yson:",value"`

    // 基本属性
    Append   *bool          `yson:"append,attr,omitempty"`
    Columns  []string       `yson:"columns,attr,omitempty"`
    Ranges   []Range        `yson:"ranges,attr,omitempty"`
    Schema   *schema.Schema `yson:"schema,attr,omitempty"`

    // 表格特定属性
    SortedBy []string `yson:"sorted_by,attr,omitempty"`
    FileName string   `yson:"file_name,attr,omitempty"`

    // 编解码属性
    Compression CompressionCodec `yson:"compression_codec,attr,omitempty"`
    Erasure     ErasureCodec     `yson:"erasure_codec,attr,omitempty"`

    // 其他属性
    Teleport      bool                   `yson:"teleport,attr,omitempty"`
    Foreign       bool                   `yson:"foreign,attr,omitempty"`
    Create        bool                   `yson:"create,attr,omitempty"`
    TransactionID any                    `yson:"transaction_id,attr,omitempty"`
    RenameColumns map[string]string      `yson:"rename_columns,attr,omitempty"`
}
```

## 核心功能

### 路径构建

#### 简单路径操作

```go
// 创建根路径
root := ypath.Root  // "/"

// 构建嵌套路径
userHome := ypath.Root.Child("home").Child("user")  // "/home/user"
userHome = ypath.Root.JoinChild("home", "user")     // "/home/user"

// 列表操作
listPath := ypath.Path("//tmp/mylist")
firstItem := listPath.ListIndex(0)      // "/tmp/mylist/0"
lastItem := listPath.ListLast()         // "/tmp/mylist/-1"
allItems := listPath.Children()         // "/tmp/mylist/*"

// 列表插入操作
beginPos := listPath.ListBegin()        // "/tmp/mylist/begin"
endPos := listPath.ListEnd()            // "/tmp/mylist/end"
beforePos := listPath.ListBefore(5)     // "/tmp/mylist/before:5"
afterPos := listPath.ListAfter(5)       // "/tmp/mylist/after:5"

// 属性操作
attrPath := ypath.Path("//tmp/node").Attr("type")     // "/tmp/node/@type"
allAttrs := ypath.Path("//tmp/node").Attrs()          // "/tmp/node/@"

// 符号链接处理
linkPath := ypath.Path("//tmp/link").SuppressSymlink() // "/tmp/link&"
```

#### 丰富路径操作

```go
// 创建丰富路径
richPath := ypath.NewRich("//home/user/data")

// 添加列选择
richPath.SetColumns([]string{"user_id", "name", "email"})

// 添加范围选择
richPath.AddRange(ypath.Interval(
    ypath.RowIndex(0),
    ypath.RowIndex(1000),
))

// 设置模式
richPath.SetSchema(schema.Schema{
    Columns: []schema.Column{
        {Name: "user_id", Type: schema.TypeInt64},
        {Name: "name", Type: schema.TypeString},
    },
})

// 设置追加模式
richPath.SetAppend()

// 设置压缩
richPath.SetCompression(ypath.CompressionCodecLz4)
```

### 范围选择

YPath 支持灵活的表格数据范围选择：

#### 读取限制类型

```go
// 基于行索引的限制
rowLimit := ypath.RowIndex(100)

// 基于键的限制
keyLimit := ypath.Key("user_123", "active")
compositeKey := ypath.Key(100, "data")
```

#### 范围类型

```go
// 完整表格
fullRange := ypath.Full()

// 从某个限制开始到结束
startFrom := ypath.StartingFrom(ypath.RowIndex(100))

// 从开始到某个限制
upTo := ypath.UpTo(ypath.RowIndex(1000))

// 区间范围
interval := ypath.Interval(
    ypath.RowIndex(100),
    ypath.RowIndex(1000),
)

// 精确匹配
exact := ypath.Exact(ypath.Key("user_123"))
```

### 路径解析

`ypath` 包提供强大的路径解析功能：

```go
// 解析复杂路径
rich, err := ypath.Parse("//tmp/table[#100:#200]{user_id,name}")
if err != nil {
    panic(err)
}

fmt.Printf("Path: %s\n", rich.Path)
fmt.Printf("Ranges: %+v\n", rich.Ranges)
fmt.Printf("Columns: %+v\n", rich.Columns)
```

### 路径操作工具

#### 路径分割

```go
// 分割路径为父路径和子路径
parent, child, err := ypath.Split("//home/user/data")
// parent = "//home/user", child = "data"
```

#### 路径到根路径列表

```go
// 获取到根路径的所有路径
paths, err := ypath.PathsUpToRoot("//home/user/data")
// 返回: ["//home/user/data", "//home/user", "//home", "/"]
```

#### 令牌分割

```go
// 将路径分割为令牌
tokens, err := ypath.SplitTokens("//home/user/data")
// 返回: ["", "home", "user", "data"]
```

## 编解码支持

### YSON 序列化

`Path` 和 `Rich` 都实现了 YSON 编解码接口：

```go
// 编码为 YSON
path := ypath.Path("//home/user")
data, err := yson.Marshal(path)

// 解码 YSON
var decodedPath ypath.Path
err = yson.Unmarshal(data, &decodedPath)
```

### 文本编解码

支持标准的文本编解码：

```go
// 文本编码
path := ypath.Path("//home/user")
text, _ := path.MarshalText()

// 文本解码
var decodedPath ypath.Path
decodedPath.UnmarshalText(text)
```

## 编解码器支持

`ypath` 包定义了多种编解码器：

### 压缩编解码器

```go
const (
    CompressionCodecNone CompressionCodec = "none"
    CompressionCodecLz4  CompressionCodec = "lz4"
    CompressionCodecZstd CompressionCodec = "zstd"
)
```

### 纠删编解码器

```go
const (
    ErasureCodecNone            ErasureCodec = "none"
    ErasureCodecReedSolomon_6_3 ErasureCodec = "reed_solomon_6_3"
    ErasureCodecLrc_12_2_2      ErasureCodec = "lrc_12_2_2"
)
```

## 使用示例

### 基本路径操作

```go
package main

import (
    "fmt"
    "go.ytsaurus.tech/yt/go/ypath"
)

func main() {
    // 构建用户主目录路径
    userHome := ypath.Root.Child("home").Child("alice")
    fmt.Printf("用户主目录: %s\n", userHome)

    // 访问用户表的属性
    tableAttr := userHome.Child("table").Attr("row_count")
    fmt.Printf("表行数属性: %s\n", tableAttr)

    // 创建列表操作路径
    tasks := ypath.Path("//tmp/tasks")
    firstTask := tasks.ListIndex(0)
    fmt.Printf("第一个任务: %s\n", firstTask)
}
```

### 复杂表格查询

```go
package main

import (
    "fmt"
    "go.ytsaurus.tech/yt/go/ypath"
    "go.ytsaurus.tech/yt/go/schema"
)

func main() {
    // 创建复杂的表格查询路径
    tablePath := ypath.NewRich("//home/user/logs")

    // 设置列选择
    tablePath.SetColumns([]string{"timestamp", "level", "message"})

    // 添加时间范围
    tablePath.AddRange(ypath.Interval(
        ypath.Key("2023-01-01T00:00:00Z"),
        ypath.Key("2023-01-02T00:00:00Z"),
    ))

    // 设置排序
    tablePath.SetSortedBy([]string{"timestamp"})

    // 设置模式
    tablePath.SetSchema(schema.Schema{
        Columns: []schema.Column{
            {Name: "timestamp", Type: schema.TypeString},
            {Name: "level", Type: schema.TypeString},
            {Name: "message", Type: schema.TypeString},
        },
    })

    fmt.Printf("复杂查询路径已创建\n")
}
```

### 路径解析和处理

```go
package main

import (
    "fmt"
    "go.ytsaurus.tech/yt/go/ypath"
)

func main() {
    // 解析复杂路径
    complexPath := "//logs/app[100:200]{timestamp,level}"
    parsed, err := ypath.Parse(complexPath)
    if err != nil {
        panic(err)
    }

    fmt.Printf("解析结果:\n")
    fmt.Printf("路径: %s\n", parsed.Path)
    fmt.Printf("列: %v\n", parsed.Columns)
    fmt.Printf("范围: %v\n", parsed.Ranges)

    // 路径分割
    parent, child, err := ypath.Split(parsed.Path)
    if err != nil {
        panic(err)
    }

    fmt.Printf("父路径: %s\n", parent)
    fmt.Printf("子路径: %s\n", child)
}
```

## 最佳实践

### 1. 路径构建

```go
// 推荐：使用链式调用
path := ypath.Root.Child("home").Child("user").Child("data")

// 不推荐：字符串拼接
path := ypath.Path("/home/user/data")
```

### 2. 复杂查询

```go
// 推荐：使用 Rich 进行复杂查询
rich := ypath.NewRich("//tmp/table").
    SetColumns([]string{"id", "name"}).
    AddRange(ypath.Interval(...))

// 不推荐：手动构建复杂字符串
path := ypath.Path("//tmp/table[#100:#200]{id,name}")
```

### 3. 错误处理

```go
// 始终检查解析错误
rich, err := ypath.Parse(complexPath)
if err != nil {
    // 处理错误
    return fmt.Errorf("路径解析失败: %w", err)
}
```

### 4. 路径验证

```go
// 使用 Parse 验证路径格式
_, err := ypath.Path("//invalid@path").YPath()
if err != nil {
    // 路径格式错误
}
```

## 注意事项

1. **路径格式**：确保路径符合 YTsaurus 路径规范
2. **大小写敏感**：YPath 对大小写敏感
3. **特殊字符**：特殊字符需要正确转义
4. **性能考虑**：频繁的路径操作可能影响性能
5. **并发安全**：Path 类型是并发安全的，Rich 不是

## 相关依赖

- `go.ytsaurus.tech/yt/go/yson`: YSON 序列化支持
- `go.ytsaurus.tech/yt/go/schema`: YTsaurus 模式定义

## 更多信息

详细的 YPath 语法和用法请参考 [YTsaurus 文档](https://ytsaurus.tech/docs/en/user-guide/storage/ypath)。