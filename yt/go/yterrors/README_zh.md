# YTErrors - YTsaurus 错误处理库

## 概述

`yterrors` 包提供了 YTsaurus 错误处理的标准实现。YTsaurus 错误被设计为可以在网络和不同语言之间轻松传输的格式，具有层次化结构和丰富的属性信息。

## 错误结构

### Error 类型

```go
type Error struct {
    Code       ErrorCode      `yson:"code" json:"code"`                        // 错误代码
    Message    string         `yson:"message" json:"message"`                  // 错误消息
    Attributes map[string]any `yson:"attributes,omitempty" json:"attributes,omitempty"` // 错误属性

    InnerErrors []*Error `yson:"inner_errors,omitempty" json:"inner_errors,omitempty"` // 内部错误列表
    origError   error    // 原始 Go 错误，保存转换时的错误
}
```

### ErrorCode 类型

错误代码是整数类型，用于标识特定的错误类型：

```go
type ErrorCode int
```

常见的错误代码包括：

- `CodeTimeout`: 超时错误
- `CodeResolveError`: 路径解析错误
- `CodeAuthenticationError`: 认证错误
- `CodeAuthorizationError`: 授权错误
- `CodeConcurrentTransactionLockConflict`: 并发事务锁冲突
- `CodeRequestQueueSizeLimitExceeded`: 请求队列大小限制超出
- `CodeNoSuchTransaction`: 事务不存在

## 核心功能

### 错误检查函数

#### 按代码检查

```go
// 检查错误是否包含特定错误代码
func ContainsErrorCode(err error, code ErrorCode) bool

// 查找包含特定错误代码的错误
func FindErrorCode(err error, code ErrorCode) *Error

// 检查错误是否为特定代码
func IsErrorCode(err error, code ErrorCode) bool
```

#### 常见错误类型检查

```go
// 检查是否为解析错误
func ContainsResolveError(err error) bool

// 检查是否为节点已存在错误
func ContainsAlreadyExistsError(err error) bool

// 检查是否为节点不存在错误
func ContainsNotFoundError(err error) bool

// 检查是否为认证错误
func ContainsAuthenticationError(err error) bool

// 检查是否为授权错误
func ContainsAuthorizationError(err error) bool

// 检查是否为超时错误
func ContainsTimeoutError(err error) bool

// 检查是否为锁冲突错误
func ContainsLockConflictError(err error) bool
```

### 错误创建和转换

#### 从 Go 错误创建

```go
// 从字符串创建 YTsaurus 错误
func New(code ErrorCode, message string, args ...any) *Error

// 从 Go 错误创建 YTsaurus 错误
func FromGo(err error) *Error

// 带属性的创建
func NewWithAttrs(code ErrorCode, message string, attributes map[string]any) *Error
```

#### 错误包装

```go
// 包装 Go 错误为 YTsaurus 错误
func Wrap(err error, code ErrorCode, message string, args ...any) *Error

// 包装现有 YTsaurus 错误
func WrapError(err *Error, code ErrorCode, message string, args ...any) *Error

// 添加内部错误
func WrapInner(err error, inner *Error) *Error
```

### 错误解析和序列化

#### YSON 支持

```go
// 从 YSON 字节解析错误
func UnmarshalYSON(data []byte) (*Error, error)

// 将错误序列化为 YSON
func (e *Error) MarshalYSON() ([]byte, error)
```

#### JSON 支持

```go
// 从 JSON 解析错误
func UnmarshalJSON(data []byte) (*Error, error)

// 将错误序列化为 JSON
func (e *Error) MarshalJSON() ([]byte, error)
```

## 使用示例

### 基本错误处理

```go
package main

import (
    "fmt"
    "go.ytsaurus.tech/yt/go/yterrors"
)

func main() {
    // 创建错误
    err := yterrors.New(yterrors.CodeResolveError, "路径解析失败: %s", "//invalid/path")

    fmt.Printf("错误代码: %d\n", err.Code)
    fmt.Printf("错误消息: %s\n", err.Message)
    fmt.Printf("错误详情: %v\n", err)

    // 检查特定错误类型
    if yterrors.ContainsResolveError(err) {
        fmt.Println("这是一个解析错误")
    }

    if yterrors.ContainsErrorCode(err, yterrors.CodeResolveError) {
        fmt.Println("包含解析错误代码")
    }
}
```

### 错误包装和嵌套

```go
package main

import (
    "fmt"
    "errors"
    "go.ytsaurus.tech/yt/go/yterrors"
)

func main() {
    // 原始错误
    originalErr := errors.New("网络连接失败")

    // 包装为 YTsaurus 错误
    ytErr := yterrors.Wrap(originalErr, yterrors.CodeTimeout, "请求超时")

    fmt.Printf("包装后的错误: %v\n", ytErr)
    fmt.Printf("原始错误: %v\n", ytErr.origError)

    // 添加内部错误
    innerErr := yterrors.New(yterrors.CodeResolveError, "无法解析主机名")
    wrappedErr := yterrors.WrapInner(ytErr, innerErr)

    fmt.Printf("嵌套错误: %+v\n", wrappedErr)

    // 检查内部错误
    if yterrors.ContainsErrorCode(wrappedErr, yterrors.CodeResolveError) {
        fmt.Println("包含解析错误")
    }
}
```

### 错误属性处理

```go
package main

import (
    "fmt"
    "go.ytsaurus.tech/yt/go/yterrors"
)

func main() {
    // 创建带属性的错误
    attrs := map[string]any{
        "path":      "//tmp/data",
        "timestamp": 1640995200,
        "retry":     3,
    }

    err := yterrors.NewWithAttrs(
        yterrors.CodeTimeout,
        "操作超时",
        attrs,
    )

    fmt.Printf("错误代码: %d\n", err.Code)
    fmt.Printf("错误消息: %s\n", err.Message)

    // 访问属性
    if path, ok := err.Attributes["path"]; ok {
        fmt.Printf("错误路径: %v\n", path)
    }

    if timestamp, ok := err.Attributes["timestamp"]; ok {
        fmt.Printf("错误时间戳: %v\n", timestamp)
    }
}
```

### 错误序列化和反序列化

```go
package main

import (
    "fmt"
    "go.ytsaurus.tech/yt/go/yterrors"
    "go.ytsaurus.tech/yt/go/yson"
)

func main() {
    // 创建复杂错误
    err := yterrors.New(yterrors.CodeTimeout, "请求超时")

    innerErr := yterrors.NewWithAttrs(
        yterrors.CodeResolveError,
        "路径解析失败",
        map[string]any{"path": "//invalid/path"},
    )

    err.InnerErrors = append(err.InnerErrors, innerErr)

    // 序列化为 YSON
    data, err := err.MarshalYSON()
    if err != nil {
        panic(err)
    }

    fmt.Printf("YSON 序列化结果: %s\n", string(data))

    // 反序列化
    parsedErr, err := yterrors.UnmarshalYSON(data)
    if err != nil {
        panic(err)
    }

    fmt.Printf("反序列化的错误: %+v\n", parsedErr)
    fmt.Printf("内部错误数量: %d\n", len(parsedErr.InnerErrors))
}
```

### HTTP 错误处理

```go
package main

import (
    "fmt"
    "net/http"
    "go.ytsaurus.tech/yt/go/yterrors"
)

func handleHTTPError(resp *http.Response) error {
    if resp.StatusCode == http.StatusOK {
        return nil
    }

    // 从 HTTP 响应创建错误
    err := yterrors.New(
        yterrors.CodeAuthorizationError,
        "HTTP 请求失败: %d %s",
        resp.StatusCode,
        resp.Status,
    )

    // 添加 HTTP 相关属性
    if err.Attributes == nil {
        err.Attributes = make(map[string]any)
    }
    err.Attributes["http_status_code"] = resp.StatusCode
    err.Attributes["http_status"] = resp.Status

    return err
}

func main() {
    // 模拟 HTTP 错误响应
    resp := &http.Response{
        StatusCode: http.StatusForbidden,
        Status:     "403 Forbidden",
    }

    err := handleHTTPError(resp)
    if err != nil {
        if yterrors.ContainsAuthorizationError(err) {
            fmt.Println("认证失败，请检查权限")
        }
        fmt.Printf("错误详情: %v\n", err)
    }
}
```

## 高级功能

### 错误遍历和搜索

```go
package main

import (
    "fmt"
    "go.ytsaurus.tech/yt/go/yterrors"
)

func findErrorByCode(err error, code yterrors.ErrorCode) *yterrors.Error {
    var ytErr *yterrors.Error
    if yterrors.As(err, &ytErr) {
        return findInErrorTree(ytErr, code)
    }
    return nil
}

func findInErrorTree(err *yterrors.Error, code yterrors.ErrorCode) *yterrors.Error {
    if err.Code == code {
        return err
    }

    for _, inner := range err.InnerErrors {
        if found := findInErrorTree(inner, code); found != nil {
            return found
        }
    }

    return nil
}

func main() {
    // 创建嵌套错误
    rootErr := yterrors.New(yterrors.CodeTimeout, "根错误")
    childErr := yterrors.New(yterrors.CodeResolveError, "子错误")
    grandChildErr := yterrors.New(yterrors.CodeAuthenticationError, "孙错误")

    childErr.InnerErrors = append(childErr.InnerErrors, grandChildErr)
    rootErr.InnerErrors = append(rootErr.InnerErrors, childErr)

    // 搜索特定错误
    if found := findErrorByCode(rootErr, yterrors.CodeAuthenticationError); found != nil {
        fmt.Printf("找到认证错误: %s\n", found.Message)
    }
}
```

### 错误格式化

```go
package main

import (
    "fmt"
    "go.ytsaurus.tech/yt/go/yterrors"
)

func main() {
    err := yterrors.New(
        yterrors.CodeTimeout,
        "操作超时",
    )

    // 简单格式化
    fmt.Printf("简单格式: %v\n", err)

    // 详细格式化
    fmt.Printf("详细格式: %+v\n", err)

    // JSON 格式化
    if jsonBytes, err := err.MarshalJSON(); err == nil {
        fmt.Printf("JSON 格式: %s\n", string(jsonBytes))
    }
}
```

### 错误恢复策略

```go
package main

import (
    "fmt"
    "time"
    "go.ytsaurus.tech/yt/go/yterrors"
)

type RetryStrategy struct {
    MaxRetries int
    BaseDelay  time.Duration
}

func (rs *RetryStrategy) ShouldRetry(err error, attempt int) bool {
    if attempt >= rs.MaxRetries {
        return false
    }

    // 可重试的错误类型
    return yterrors.ContainsTimeoutError(err) ||
           yterrors.ContainsErrorCode(err, yterrors.CodeRequestQueueSizeLimitExceeded) ||
           yterrors.ContainsErrorCode(err, yterrors.CodeConcurrentTransactionLockConflict)
}

func (rs *RetryStrategy) GetDelay(attempt int) time.Duration {
    return rs.BaseDelay * time.Duration(attempt+1)
}

func executeWithRetry(fn func() error) error {
    strategy := &RetryStrategy{
        MaxRetries: 3,
        BaseDelay:  time.Second,
    }

    var err error
    for attempt := 0; attempt <= strategy.MaxRetries; attempt++ {
        err = fn()
        if err == nil {
            return nil
        }

        if !strategy.ShouldRetry(err, attempt) {
            return err
        }

        delay := strategy.GetDelay(attempt)
        fmt.Printf("重试 %d/%d，等待 %v\n", attempt+1, strategy.MaxRetries, delay)
        time.Sleep(delay)
    }

    return err
}

func main() {
    attempt := 0
    err := executeWithRetry(func() error {
        attempt++
        if attempt < 3 {
            return yterrors.New(yterrors.CodeTimeout, "模拟超时")
        }
        return nil
    })

    if err != nil {
        fmt.Printf("操作失败: %v\n", err)
    } else {
        fmt.Println("操作成功")
    }
}
```

## 常见错误代码参考

### 系统错误

- `CodeOK`: 成功
- `CodeGenericError`: 通用错误
- `CodeTimeout`: 超时
- `CodeUnavailable`: 服务不可用

### 认证和授权

- `CodeAuthenticationError`: 认证错误
- `CodeAuthorizationError`: 授权错误

### 路径和节点

- `CodeResolveError`: 路径解析错误
- `CodeAlreadyExists`: 节点已存在
- `CodeNoSuchNode`: 节点不存在

### 事务和锁

- `CodeNoSuchTransaction`: 事务不存在
- `CodeConcurrentTransactionLockConflict`: 并发事务锁冲突

### 请求和队列

- `CodeRequestQueueSizeLimitExceeded`: 请求队列大小限制超出
- `CodeRequestRateLimitExceeded`: 请求频率限制超出

## 最佳实践

### 1. 错误检查

```go
// 推荐：使用具体的错误检查函数
if yterrors.ContainsResolveError(err) {
    // 处理解析错误
}

// 不推荐：字符串匹配
if strings.Contains(err.Error(), "resolve") {
    // 可能不可靠
}
```

### 2. 错误创建

```go
// 推荐：使用标准错误代码
err := yterrors.New(yterrors.CodeTimeout, "操作超时")

// 推荐：添加有用的属性
err := yterrors.NewWithAttrs(
    yterrors.CodeTimeout,
    "操作超时",
    map[string]any{
        "operation": "read_table",
        "path":      "//tmp/data",
        "timeout":   30000,
    },
)
```

### 3. 错误包装

```go
// 推荐：保留原始错误信息
return yterrors.Wrap(originalErr, yterrors.CodeTimeout, "请求超时")

// 不推荐：丢失原始错误信息
return yterrors.New(yterrors.CodeTimeout, "请求超时")
```

### 4. 错误恢复

```go
// 推荐：根据错误类型采取不同的恢复策略
switch {
case yterrors.ContainsTimeoutError(err):
    // 重试
case yterrors.ContainsAuthorizationError(err):
    // 重新认证
case yterrors.ContainsResolveError(err):
    // 检查路径格式
default:
    // 通用错误处理
}
```

## 注意事项

1. **错误代码唯一性**：确保使用正确的错误代码
2. **错误信息清晰**：提供清晰、有用的错误消息
3. **属性完整性**：添加相关的错误属性以便调试
4. **错误链保持**：包装错误时保持原始错误信息
5. **序列化兼容性**：注意错误序列化的版本兼容性

## 相关依赖

- `go.ytsaurus.tech/yt/go/yson`: YSON 序列化支持
- `golang.org/x/xerrors`: 增强错误处理

## 更多信息

详细的错误代码列表和处理指南请参考 [YTsaurus 错误处理文档](https://ytsaurus.tech/docs/en/user-guide/errors)。