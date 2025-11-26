# Dependencies

## 概述

Deps 模块是 YTsaurus Go 客户端的依赖管理模块，负责导入和初始化必要的第三方依赖库。该模块确保所有必需的依赖项被正确加载，以支持 YTsaurus Go 客户端的完整功能。

## 功能特性

- **依赖管理**：统一管理第三方依赖项的导入
- **初始化**：确保依赖项在使用前被正确初始化
- **空白导入**：使用空白导入触发依赖项的初始化函数
- **简化导入**：减少其他模块对第三方依赖的直接引用

## 当前依赖项

### 1. HTTP 客户端库

```go
import _ "github.com/go-resty/resty/v2"
```

**Resty (v2)** - 简洁强大的 HTTP 和 REST 客户端库
- **功能**：提供简单易用的 HTTP 客户端接口
- **特性**：
  - 自动请求/响应处理
  - 支持中间件
  - 重试机制
  - JSON/XML 自动编解码
  - 文件上传下载

### 2. HTTP 指标中间件

```go
import _ "go.ytsaurus.tech/library/go/httputil/middleware/httpmetrics"
```

**HTTP Metrics** - HTTP 请求指标收集中间件
- **功能**：收集 HTTP 请求的性能指标
- **指标类型**：
  - 请求数量
  - 请求延迟
  - 响应状态码分布
  - 错误率统计

## 使用方式

### 间接依赖

该模块的主要作用是通过空白导入触发依赖项的初始化。其他模块不需要直接引用这些库：

```go
package main

import (
    // 通过导入 deps 模块，所有依赖项会被自动初始化
    _ "go.ytsaurus.tech/yt/go/deps"

    "go.ytsaurus.tech/yt/go/yt"
)

func main() {
    // 现在可以使用依赖项提供的功能
    // 例如，HTTP 客户端会自动配置好指标收集
}
```

## 依赖项作用

### 1. 自动配置

导入 deps 模块会：
- 注册 HTTP 客户端配置
- 初始化指标收集器
- 设置默认中间件
- 配置日志记录

### 2. 性能监控

HTTP 指标中间件提供：
- 请求级别的性能数据
- 内置的 Prometheus 指标导出
- 自动的错误统计
- 延迟分布直方图

### 3. 增强功能

Resty 库提供：
- 更简洁的 API 设计
- 自动重试和超时处理
- 请求/响应拦截器
- 并发安全的会话管理

## 配置选项

### Resty 客户端配置

虽然 deps 模块提供默认配置，但可以通过其他模块自定义：

```go
// 在其他模块中自定义 Resty 客户端
client := resty.New().
    SetTimeout(30 * time.Second).
    SetRetryCount(3).
    AddRetryHook(func(r *resty.Response, err error) {
        // 自定义重试逻辑
    })
```

### 指标配置

HTTP 指标可以通过环境变量或配置文件调整：

```go
// 默认指标路径
metricsPath := "/metrics"

// 指标命名空间
metricsNamespace := "yt_go_client"
```

## 最佳实践

### 1. 依赖版本管理

确保在 `go.mod` 中固定依赖版本：

```go
require (
    github.com/go-resty/resty/v2 v2.10.0
    go.ytsaurus.tech/library/go/httputil v0.0.0
)
```

### 2. 优雅关闭

在使用 HTTP 客户端的应用中，确保优雅关闭：

```go
func main() {
    // 导入依赖
    _ "go.ytsaurus.tech/yt/go/deps"

    // 应用逻辑...

    // 优雅关闭
    ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
    defer cancel()

    // 关闭 HTTP 连接
    if err := shutdownHTTPClients(ctx); err != nil {
        log.Printf("关闭 HTTP 客户端失败: %v", err)
    }
}
```

### 3. 指标监控

利用自动收集的指标进行监控：

```go
// 设置 Prometheus 指标端点
http.Handle("/metrics", promhttp.Handler())
go func() {
    log.Fatal(http.ListenAndServe(":8080", nil))
}()
```

## 注意事项

1. **导入顺序**：确保在主程序入口导入 deps 模块
2. **版本兼容**：注意依赖项版本之间的兼容性
3. **资源使用**：监控指标收集可能增加内存使用
4. **网络配置**：合理配置 HTTP 客户端的超时和重试参数

## 未来扩展

deps 模块设计为可扩展的，未来可能添加：

- 更多 HTTP 客户端增强功能
- 数据库驱动初始化
- 缓存库配置
- 认证和授权模块
- 监控和追踪集成

## 相关文档

- [Resty 官方文档](https://github.com/go-resty/resty)
- [YTsaurus Go 库文档](https://github.com/ytsaurus/ytsaurus/tree/main/yt/go)
- [Prometheus 指标最佳实践](https://prometheus.io/docs/practices/instrumentation/)