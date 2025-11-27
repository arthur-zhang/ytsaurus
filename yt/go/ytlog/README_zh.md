# YTLog - YTsaurus 日志库

## 概述

`ytlog` 包提供了 YTsaurus 专用的日志记录工具。该库基于 Uber 的 Zap 日志库构建，提供了符合 YTsaurus 项目标准的日志配置和功能。

## 核心功能

### 日志级别支持

支持标准的日志级别：

- **Debug**: 调试信息，默认开启
- **Info**: 一般信息
- **Warn**: 警告信息
- **Error**: 错误信息
- **Fatal**: 致命错误，会终止程序

### 日志格式

使用结构化的 JSON 格式日志，包含以下字段：
- 时间戳（ISO8601 格式）
- 日志级别
- 消息内容
- 结构化字段

## 主要 API

### 基本日志创建

```go
// 创建默认日志器
func New() (*logzap.Logger, error)

// 创建默认日志器（panic on error）
func Must() *logzap.Logger

// 创建日志器配置
func NewConfig() zap.Config
```

### 自滚动日志

```go
// 创建自滚动日志器
func NewSelfrotate(logPath string, options ...Option) (*logzap.Logger, func(), error)

// 创建自滚动日志核心
func NewSelfrotateCore(logPath string, options ...Option) (*asynczap.Core, func(), error)
```

### 配置选项

```go
// 设置日志级别
func WithLogLevel(level zapcore.Level) Option

// 设置最小剩余空间
func WithMinFreeSpace(space float64) Option
```

## 使用示例

### 基本日志记录

```go
package main

import (
    "go.uber.org/zap"
    "go.ytsaurus.tech/library/go/core/log/zap"
    "go.ytsaurus.tech/yt/go/ytlog"
)

func main() {
    // 创建默认日志器
    logger, err := ytlog.New()
    if err != nil {
        panic(err)
    }

    // 基本日志记录
    logger.Info("应用程序启动")
    logger.Debug("调试信息")
    logger.Warn("警告信息")

    // 带字段的日志
    logger.Info("用户操作",
        zap.String("user_id", "12345"),
        zap.String("action", "login"),
        zap.Duration("duration", time.Millisecond*150),
    )

    // 错误日志
    err := someOperation()
    if err != nil {
        logger.Error("操作失败",
            zap.Error(err),
            zap.String("operation", "some_operation"),
        )
    }
}

func someOperation() error {
    return fmt.Errorf("模拟错误")
}
```

### 使用 Must 创建日志器

```go
package main

import (
    "go.uber.org/zap"
    "go.ytsaurus.tech/yt/go/ytlog"
)

func main() {
    // 使用 Must 创建日志器（panic on error）
    logger := ytlog.Must()

    logger.Info("日志器创建成功")

    // 结构化日志
    logger.Info("处理请求",
        zap.String("method", "GET"),
        zap.String("path", "/api/users"),
        zap.Int("status_code", 200),
        zap.Duration("latency", time.Millisecond*50),
    )
}
```

### 自定义配置

```go
package main

import (
    "go.uber.org/zap/zapcore"
    "go.ytsaurus.tech/yt/go/ytlog"
)

func main() {
    // 获取默认配置
    config := ytlog.NewConfig()

    // 修改配置
    config.Level = zap.NewAtomicLevelAt(zapcore.InfoLevel) // 只记录 Info 及以上级别
    config.OutputPaths = []string{"stdout", "/var/log/app.log"}

    // 创建日志器
    logger, err := config.Build()
    if err != nil {
        panic(err)
    }

    logger.Info("使用自定义配置的日志器")
}
```

### 自滚动日志

```go
package main

import (
    "go.uber.org/zap/zapcore"
    "go.ytsaurus.tech/yt/go/ytlog"
    "go.ytsaurus.tech/library/go/core/log/zap"
)

func main() {
    logPath := "/var/log/ytsaurus/app.log"

    // 创建自滚动日志器
    logger, stop, err := ytlog.NewSelfrotate(logPath,
        ytlog.WithLogLevel(zapcore.InfoLevel),
        ytlog.WithMinFreeSpace(0.1), // 最少保留 10% 空间
    )
    if err != nil {
        panic(err)
    }
    defer stop() // 确保停止日志器

    logger.Info("自滚动日志器创建成功")

    // 模拟大量日志
    for i := 0; i < 1000; i++ {
        logger.Info("日志消息",
            zap.Int("index", i),
            zap.String("data", fmt.Sprintf("log-entry-%d", i)),
        )
    }
}
```

### 不同日志级别的使用

```go
package main

import (
    "go.uber.org/zap"
    "go.ytsaurus.tech/yt/go/ytlog"
)

func main() {
    logger := ytlog.Must()

    // Debug 级别 - 详细的调试信息
    logger.Debug("进入函数",
        zap.String("function", "processData"),
        zap.Any("input", map[string]interface{}{"count": 100}),
    )

    // Info 级别 - 一般信息
    logger.Info("处理数据完成",
        zap.Int("processed_count", 100),
        zap.Duration("duration", time.Second*5),
    )

    // Warn 级别 - 警告信息
    logger.Warn("处理时间较长",
        zap.Duration("duration", time.Second*30),
        zap.Int("threshold", 10),
    )

    // Error 级别 - 错误信息（程序可继续）
    err := processData()
    if err != nil {
        logger.Error("数据处理失败",
            zap.Error(err),
            zap.String("component", "data_processor"),
        )
    }

    // Fatal 级别 - 致命错误（程序终止）
    if criticalError() {
        logger.Fatal("系统配置错误",
            zap.String("config_file", "/etc/app/config.yaml"),
            zap.Error(err),
        )
    }
}
```

### 在 YTsaurus 客户端中使用

```go
package main

import (
    "go.uber.org/zap"
    "go.ytsaurus.tech/library/go/core/log"
    "go.ytsaurus.tech/yt/go/ytlog"
    "go.ytsaurus.tech/yt/go/yt"
    "go.ytsaurus.tech/yt/go/ythttp"
)

func main() {
    // 创建日志器
    logger, err := ytlog.New()
    if err != nil {
        panic(err)
    }

    // 创建带日志的 YTsaurus 客户端
    client, err := ythttp.NewClient(&yt.Config{
        Proxy: "hahn.yt.yandex.net",
        Logger: logger,
    })
    if err != nil {
        logger.Fatal("创建客户端失败", zap.Error(err))
    }
    defer client.Stop()

    // 记录操作
    logger.Info("开始执行操作",
        zap.String("operation", "list_nodes"),
        zap.String("path", "//tmp"),
    )

    // 执行 YTsaurus 操作
    nodes, err := client.ListNode(context.Background(), ypath.Path("//tmp"), nil)
    if err != nil {
        logger.Error("列出节点失败",
            zap.Error(err),
            zap.String("path", "//tmp"),
        )
        return
    }

    logger.Info("操作成功",
        zap.Strings("nodes", nodes),
        zap.Int("count", len(nodes)),
    )
}
```

### 带上下文的日志

```go
package main

import (
    "context"
    "go.uber.org/zap"
    "go.ytsaurus.tech/library/go/core/log"
    "go.ytsaurus.tech/yt/go/ytlog"
)

func processRequest(ctx context.Context, requestID string) {
    logger := ytlog.Must()

    // 从上下文获取日志器（如果有的话）
    if l := log.Ctx(ctx); l != nil {
        logger = l.(*logzap.Logger)
    }

    logger.Info("处理请求",
        zap.String("request_id", requestID),
        zap.String("trace_id", getTraceID(ctx)),
    )

    // 模拟处理
    err := doWork(ctx)
    if err != nil {
        logger.Error("处理失败",
            zap.Error(err),
            zap.String("request_id", requestID),
        )
        return
    }

    logger.Info("处理成功",
        zap.String("request_id", requestID),
    )
}

func getTraceID(ctx context.Context) string {
    // 从上下文获取 trace ID
    return "trace-12345"
}

func doWork(ctx context.Context) error {
    // 模拟工作
    return nil
}
```

## 高级功能

### 日志采样配置

```go
package main

import (
    "go.uber.org/zap/zapcore"
    "go.ytsaurus.tech/yt/go/ytlog"
)

func main() {
    // 获取默认配置
    config := ytlog.NewConfig()

    // 启用日志采样（减少高频日志的输出）
    config.Sampling = &zap.SamplingConfig{
        Initial:    100, // 最初每秒记录 100 条
        Thereafter: 10,  // 之后每秒记录 10 条
        Tick:       time.Second,
    }

    // 设置输出路径
    config.OutputPaths = []string{"stdout", "/var/log/app.log"}
    config.ErrorOutputPaths = []string{"stderr", "/var/log/app-error.log"}

    logger, err := config.Build()
    if err != nil {
        panic(err)
    }

    // 高频日志会被采样
    for i := 0; i < 1000; i++ {
        logger.Info("高频日志消息", zap.Int("index", i))
    }
}
```

### 自定义编码器配置

```go
package main

import (
    "go.uber.org/zap/zapcore"
    "go.ytsaurus.tech/yt/go/ytlog"
)

func main() {
    config := ytlog.NewConfig()

    // 自定义编码器
    config.EncoderConfig = zapcore.EncoderConfig{
        TimeKey:        "timestamp",
        LevelKey:       "level",
        NameKey:        "logger",
        CallerKey:      "caller",
        MessageKey:     "message",
        StacktraceKey:  "stacktrace",
        LineEnding:     zapcore.DefaultLineEnding,
        EncodeLevel:    zapcore.LowercaseLevelEncoder,
        EncodeTime:     zapcore.ISO8601TimeEncoder,
        EncodeDuration: zapcore.SecondsDurationEncoder,
        EncodeCaller:   zapcore.ShortCallerEncoder,
    }

    // 添加自定义字段
    config.InitialFields = map[string]interface{}{
        "service": "my-app",
        "version": "1.0.0",
        "env":     "production",
    }

    logger, err := config.Build()
    if err != nil {
        panic(err)
    }

    logger.Info("带自定义字段的日志")
}
```

### 性能监控日志

```go
package main

import (
    "time"
    "go.uber.org/zap"
    "go.ytsaurus.tech/yt/go/ytlog"
)

func main() {
    logger := ytlog.Must()

    // 性能监控模式
    start := time.Now()

    // 记录操作开始
    logger.Info("开始处理批量数据",
        zap.Int("batch_size", 10000),
        zap.String("operation", "process_batch"),
    )

    // 模拟处理
    processed, err := processBatch(10000)
    if err != nil {
        logger.Error("批量处理失败",
            zap.Error(err),
            zap.Duration("elapsed", time.Since(start)),
        )
        return
    }

    // 记录操作完成
    logger.Info("批量处理完成",
        zap.Int("processed", processed),
        zap.Duration("elapsed", time.Since(start)),
        zap.Float64("throughput", float64(processed)/time.Since(start).Seconds()),
    )
}

func processBatch(size int) (int, error) {
    // 模拟处理时间
    time.Sleep(time.Millisecond * 100)
    return size, nil
}
```

## 配置选项详解

### 日志级别选项

```go
// 支持的日志级别
const (
    DebugLevel = zapcore.DebugLevel
    InfoLevel  = zapcore.InfoLevel
    WarnLevel  = zapcore.WarnLevel
    ErrorLevel = zapcore.ErrorLevel
    FatalLevel = zapcore.FatalLevel
)
```

### 自滚动选项

```go
// 默认自滚动选项
var defaultRotationOptions = selfrotate.Options{
    MaxKeep:        0,                    // 保留所有日志文件
    MaxSize:        0,                    // 无大小限制
    MinFreeSpace:   0.05,                 // 最少保留 5% 空间
    Compress:       selfrotate.CompressDelayed, // 延迟压缩
    RotateInterval: selfrotate.RotateHourly,    // 每小时轮转
}
```

## 最佳实践

### 1. 日志级别使用

```go
// 推荐：合理使用日志级别
logger.Debug("详细调试信息")     // 开发环境
logger.Info("重要业务信息")      // 生产环境
logger.Warn("潜在问题")         // 需要关注
logger.Error("错误信息")        // 需要处理
logger.Fatal("致命错误")        // 程序终止
```

### 2. 结构化字段

```go
// 推荐：使用结构化字段
logger.Info("用户登录",
    zap.String("user_id", "12345"),
    zap.String("ip", "192.168.1.1"),
    zap.Time("login_time", time.Now()),
)

// 不推荐：字符串拼接
logger.Info(fmt.Sprintf("用户 %s 从 %s 登录", userID, ip))
```

### 3. 错误日志

```go
// 推荐：包含错误的完整上下文
logger.Error("操作失败",
    zap.Error(err),
    zap.String("operation", "create_user"),
    zap.Any("request", request),
    zap.Duration("retry_delay", time.Second*5),
)
```

### 4. 性能考虑

```go
// 推荐：避免在热路径中进行昂贵的日志格式化
if logger.Core().Enabled(zapcore.DebugLevel) {
    logger.Debug("详细调试信息", zap.Any("large_object", expensiveOperation()))
}

// 或者使用 defer 计算性能更好的格式
logger.Debug("处理请求", zap.String("data", func() string {
    return expensiveToString()
}()))
```

### 5. 上下文传递

```go
// 推荐：通过上下文传递日志器
func handleRequest(ctx context.Context) {
    logger := log.Ctx(ctx).(*logzap.Logger)
    logger.Info("处理请求")
}

// 创建带上下文的子日志器
ctx := log.WithContext(context.Background(), logger)
```

## 注意事项

1. **性能影响**：日志记录会影响性能，合理使用日志级别
2. **存储管理**：配置适当的日志轮转和清理策略
3. **敏感信息**：避免记录密码、密钥等敏感信息
4. **线程安全**：Zap 日志器是并发安全的
5. **资源清理**：使用 NewSelfrotate 时记得调用 stop 函数

## 相关依赖

- `go.uber.org/zap`: 高性能日志库
- `go.ytsaurus.tech/library/go/core/log/zap`: YTsaurus 日志接口
- `go.ytsaurus.tech/library/go/core/log/zap/asynczap`: 异步日志核心

## 更多信息

详细的日志配置和使用指南请参考 [Zap 官方文档](https://github.com/uber-go/zap) 和 [YTsaurus 日志规范](https://ytsaurus.tech/docs/)。