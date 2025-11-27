# YTTest - YTsaurus 测试工具库

## 概述

`yttest` 包提供了 YTsaurus Go 客户端的测试辅助工具。该包简化了测试环境的创建、YTsaurus 客户端的初始化、测试数据的准备和清理等常见的测试操作。

## 核心组件

### Env 测试环境

```go
type Env struct {
    Ctx context.Context // 测试上下文
    YT  yt.Client       // YTsaurus 客户端
    MR  mapreduce.Client // MapReduce 客户端
    L   log.Structured  // 结构化日志器
}
```

### 配置选项

```go
type Option interface {
    isOption()
}

type configOption struct {
    c yt.Config
}

type loggerOption struct {
    l log.Structured
}
```

## 主要 API

### 环境创建

```go
// 创建测试环境（自动清理）
func New(t testing.TB, opts ...Option) *Env

// 创建测试环境（手动管理生命周期）
func NewEnv(t testing.TB, opts ...Option) (env *Env, cancel func())
```

### 数据操作辅助

```go
// 上传数据切片到表格
func UploadSlice(ctx context.Context, c yt.Client, path ypath.YPath, slice any) error

// 从表格下载数据切片
func DownloadSlice(ctx context.Context, c yt.TableClient, path ypath.YPath, value any) error

// 环境方法版本
func (e *Env) UploadSlice(path ypath.YPath, slice any) error
func (e *Env) DownloadSlice(path ypath.YPath, value any) error
```

### 路径生成

```go
// 生成临时路径
func (e *Env) TmpPath() ypath.Path
```

## 使用示例

### 基本测试环境

```go
package mytest

import (
    "context"
    "testing"
    "go.ytsaurus.tech/yt/go/yttest"
)

func TestBasicOperation(t *testing.T) {
    // 创建测试环境（自动清理）
    env := yttest.New(t)

    // 使用临时路径
    tmpPath := env.TmpPath()
    t.Logf("临时路径: %s", tmpPath)

    // 执行测试操作
    err := env.YT.CreateNode(env.Ctx, tmpPath, yt.NodeMap, nil)
    if err != nil {
        t.Fatalf("创建节点失败: %v", err)
    }

    // 验证节点存在
    exists, err := env.YT.NodeExists(env.Ctx, tmpPath, nil)
    if err != nil {
        t.Fatalf("检查节点存在性失败: %v", err)
    }

    if !exists {
        t.Error("节点应该存在")
    }
}
```

### 自定义配置测试

```go
package mytest

import (
    "testing"
    "time"
    "go.uber.org/zap/zapcore"
    "go.ytsaurus.tech/library/go/core/log/zap"
    "go.ytsaurus.tech/yt/go/yt"
    "go.ytsaurus.tech/yt/go/yttest"
)

func TestWithCustomConfig(t *testing.T) {
    // 创建自定义配置
    config := yt.Config{
        Proxy:     "test-proxy.yt.local",
        ReadTimeout:  30 * time.Second,
        WriteTimeout: 60 * time.Second,
    }

    // 创建自定义日志器
    logger, _ := zap.New(zap.NewProductionConfig())
    logger.SetLevel(zapcore.DebugLevel)

    // 创建带自定义配置的测试环境
    env := yttest.New(t,
        yttest.WithConfig(config),
        yttest.WithLogger(logger),
    )

    t.Logf("使用自定义代理: %s", "test-proxy.yt.local")

    // 执行测试操作
    tmpPath := env.TmpPath()
    err := env.YT.CreateNode(env.Ctx, tmpPath, yt.NodeMap, nil)
    if err != nil {
        t.Fatalf("创建节点失败: %v", err)
    }

    t.Logf("成功创建节点: %s", tmpPath)
}
```

### 数据上传下载测试

```go
package mytest

import (
    "testing"
    "go.ytsaurus.tech/yt/go/yttest"
)

type User struct {
    ID    int64  `yson:"user_id"`
    Name  string `yson:"name"`
    Email string `yson:"email"`
}

func TestDataUploadDownload(t *testing.T) {
    env := yttest.New(t)

    // 准备测试数据
    users := []User{
        {ID: 1, Name: "Alice", Email: "alice@example.com"},
        {ID: 2, Name: "Bob", Email: "bob@example.com"},
        {ID: 3, Name: "Charlie", Email: "charlie@example.com"},
    }

    // 创建表格路径
    tablePath := env.TmpPath().Child("users")

    // 上传数据
    err := env.UploadSlice(tablePath, users)
    if err != nil {
        t.Fatalf("上传数据失败: %v", err)
    }

    t.Logf("成功上传 %d 个用户记录", len(users))

    // 下载数据
    var downloadedUsers []User
    err = env.DownloadSlice(tablePath, &downloadedUsers)
    if err != nil {
        t.Fatalf("下载数据失败: %v", err)
    }

    // 验证数据
    if len(downloadedUsers) != len(users) {
        t.Errorf("数据数量不匹配: 期望 %d, 实际 %d", len(users), len(downloadedUsers))
    }

    for i, user := range downloadedUsers {
        if user.ID != users[i].ID || user.Name != users[i].Name {
            t.Errorf("用户数据不匹配: 期望 %+v, 实际 %+v", users[i], user)
        }
    }

    t.Logf("成功验证 %d 个用户记录", len(downloadedUsers))
}
```

### MapReduce 测试

```go
package mytest

import (
    "context"
    "testing"
    "go.ytsaurus.tech/yt/go/mapreduce"
    "go.ytsaurus.tech/yt/go/yttest"
)

func TestMapReduceOperation(t *testing.T) {
    env := yttest.New(t)

    // 准备输入数据
    input := []map[string]interface{}{
        {"key": "a", "value": 1},
        {"key": "b", "value": 2},
        {"key": "a", "value": 3},
        {"key": "b", "value": 4},
    }

    inputPath := env.TmpPath().Child("input")
    err := env.UploadSlice(inputPath, input)
    if err != nil {
        t.Fatalf("上传输入数据失败: %v", err)
    }

    outputPath := env.TmpPath().Child("output")

    // 创建 MapReduce 操作
    mapper := &mapreduce.Mapper{
        InputPaths:  []ypath.YPath{inputPath},
        OutputPath:  outputPath,
        MapperSpec: map[string]interface{}{
            "class_name": "WordCountMapper",
            "code":       "def mapper(key, value): yield key, int(value)",
        },
    }

    // 执行操作
    _, err = env.MR.Run(env.Ctx, mapper)
    if err != nil {
        t.Fatalf("MapReduce 操作失败: %v", err)
    }

    t.Logf("MapReduce 操作完成")

    // 读取结果
    var results []map[string]interface{}
    err = env.DownloadSlice(outputPath, &results)
    if err != nil {
        t.Fatalf("下载结果失败: %v", err)
    }

    t.Logf("结果: %+v", results)
}
```

### 复杂测试场景

```go
package mytest

import (
    "context"
    "testing"
    "time"
    "go.ytsaurus.tech/yt/go/yttest"
    "go.ytsaurus.tech/yt/go/schema"
)

func TestComplexScenario(t *testing.T) {
    // 创建手动管理的测试环境
    env, cancel := yttest.NewEnv(t)
    defer cancel() // 手动清理

    // 创建带超时的上下文
    ctx, timeoutCancel := context.WithTimeout(env.Ctx, 30*time.Second)
    defer timeoutCancel()

    t.Logf("开始复杂测试场景")

    // 创建目录结构
    basePath := env.TmpPath()
    for _, dir := range []string{"data", "logs", "temp"} {
        dirPath := basePath.Child(dir)
        err := env.YT.CreateNode(ctx, dirPath, yt.NodeMap, nil)
        if err != nil {
            t.Fatalf("创建目录 %s 失败: %v", dirPath, err)
        }
        t.Logf("创建目录: %s", dirPath)
    }

    // 创建表格
    tableSchema := schema.Schema{
        Columns: []schema.Column{
            {Name: "timestamp", Type: schema.TypeString},
            {Name: "level", Type: schema.TypeString},
            {Name: "message", Type: schema.TypeString},
        },
    }

    logTable := basePath.Child("logs").Child("app_logs")
    _, err := env.YT.CreateNode(ctx, logTable, yt.NodeTable, &yt.CreateNodeOptions{
        Attributes: map[string]any{"schema": tableSchema},
    })
    if err != nil {
        t.Fatalf("创建日志表格失败: %v", err)
    }

    // 写入日志数据
    logs := []map[string]interface{}{
        {"timestamp": "2023-01-01T00:00:00Z", "level": "INFO", "message": "应用启动"},
        {"timestamp": "2023-01-01T00:01:00Z", "level": "WARN", "message": "内存使用率高"},
        {"timestamp": "2023-01-01T00:02:00Z", "level": "INFO", "message": "处理请求"},
    }

    err = env.UploadSlice(logTable, logs)
    if err != nil {
        t.Fatalf("上传日志数据失败: %v", err)
    }

    t.Logf("成功写入 %d 条日志记录", len(logs))

    // 创建事务执行操作
    tx, err := env.YT.BeginTransaction(ctx, nil)
    if err != nil {
        t.Fatalf("开始事务失败: %v", err)
    }

    // 在事务中创建新文件
    configFile := basePath.Child("config").Child("app.yaml")
    err = env.YT.CreateNode(ctx, configFile, yt.NodeFile, &yt.CreateNodeOptions{
        TransactionOptions: yt.TransactionOptions{
            TransactionID: tx.ID(),
        },
    })
    if err != nil {
        tx.Abort()
        t.Fatalf("在事务中创建文件失败: %v", err)
    }

    // 提交事务
    if err := tx.Commit(); err != nil {
        t.Fatalf("提交事务失败: %v", err)
    }

    t.Logf("事务 %s 提交成功", tx.ID())

    // 验证文件存在
    exists, err := env.YT.NodeExists(ctx, configFile, nil)
    if err != nil {
        t.Fatalf("检查文件存在性失败: %v", err)
    }

    if !exists {
        t.Error("配置文件应该存在")
    } else {
        t.Logf("配置文件创建成功: %s", configFile)
    }
}
```

### 并发测试

```go
package mytest

import (
    "sync"
    "testing"
    "go.ytsaurus.tech/yt/go/yttest"
)

func TestConcurrentOperations(t *testing.T) {
    env := yttest.New(t)

    var wg sync.WaitGroup
    numWorkers := 10

    // 并发创建多个文件
    for i := 0; i < numWorkers; i++ {
        wg.Add(1)
        go func(id int) {
            defer wg.Done()

            filePath := env.TmpPath().Child("worker").Child(fmt.Sprintf("file_%d", id))
            err := env.YT.CreateNode(env.Ctx, filePath, yt.NodeFile, nil)
            if err != nil {
                t.Errorf("Worker %d 创建文件失败: %v", id, err)
                return
            }

            t.Logf("Worker %d 创建文件: %s", id, filePath)
        }(i)
    }

    wg.Wait()
    t.Logf("所有 %d 个 worker 完成", numWorkers)

    // 验证所有文件都被创建
    filesPath := env.TmpPath().Child("worker")
    files, err := env.YT.ListNode(env.Ctx, filesPath, nil)
    if err != nil {
        t.Fatalf("列出文件失败: %v", err)
    }

    if len(files) != numWorkers {
        t.Errorf("文件数量不匹配: 期望 %d, 实际 %d", numWorkers, len(files))
    }

    t.Logf("成功创建 %d 个文件", len(files))
}
```

## 测试辅助函数

### 创建测试数据的辅助函数

```go
package mytest

import (
    "context"
    "go.ytsaurus.tech/yt/go/yttest"
    "go.ytsaurus.tech/yt/go/schema"
)

func createTableWithData(t testing.TB, env *yttest.Env, tableName string, data interface{}) ypath.YPath {
    // 推断表格模式
    tableSchema, err := schema.Infer(data)
    if err != nil {
        t.Fatalf("推断表格模式失败: %v", err)
    }

    // 创建表格路径
    tablePath := env.TmpPath().Child(tableName)

    // 创建表格
    _, err = env.YT.CreateNode(env.Ctx, tablePath, yt.NodeTable, &yt.CreateNodeOptions{
        Attributes: map[string]any{"schema": tableSchema},
    })
    if err != nil {
        t.Fatalf("创建表格失败: %v", err)
    }

    // 上传数据
    err = env.UploadSlice(tablePath, data)
    if err != nil {
        t.Fatalf("上传数据失败: %v", err)
    }

    return tablePath
}

func TestWithHelper(t *testing.T) {
    env := yttest.New(t)

    // 使用辅助函数创建表格
    users := []struct {
        ID    int64  `yson:"user_id"`
        Name  string `yson:"name"`
        Email string `yson:"email"`
    }{
        {ID: 1, Name: "Alice", Email: "alice@example.com"},
        {ID: 2, Name: "Bob", Email: "bob@example.com"},
    }

    userTable := createTableWithData(t, env, "users", users)
    t.Logf("创建用户表格: %s", userTable)
}
```

### 清理资源的辅助函数

```go
package mytest

import (
    "context"
    "go.ytsaurus.tech/yt/go/ypath"
    "go.ytsaurus.tech/yt/go/yttest"
)

func cleanupPath(t testing.TB, env *yttest.Env, path ypath.Path) {
    err := env.YT.RemoveNode(env.Ctx, path, nil)
    if err != nil {
        // 不要因为清理失败导致测试失败
        t.Logf("清理路径 %s 失败: %v", path, err)
    }
}

func TestWithCleanup(t *testing.T) {
    env, cancel := yttest.NewEnv(t)
    defer cancel()

    testPath := env.TmpPath().Child("test_data")

    // 创建测试数据
    err := env.YT.CreateNode(env.Ctx, testPath, yt.NodeMap, nil)
    if err != nil {
        t.Fatalf("创建测试数据失败: %v", err)
    }

    // 执行测试
    t.Logf("测试路径: %s", testPath)

    // 手动清理
    cleanupPath(t, env, testPath)
}
```

## 配置选项详解

### WithConfig

```go
// 使用自定义配置
config := yt.Config{
    Proxy:      "custom-proxy",
    Token:      "test-token",
    RetryCount: 3,
}

env := yttest.New(t, yttest.WithConfig(config))
```

### WithLogger

```go
// 使用自定义日志器
logger, _ := zap.New(zap.NewDevelopmentConfig())
env := yttest.New(t, yttest.WithLogger(logger))
```

### 组合使用

```go
// 组合多个选项
env := yttest.New(t,
    yttest.WithConfig(customConfig),
    yttest.WithLogger(logger),
)
```

## 最佳实践

### 1. 资源管理

```go
// 推荐：使用自动清理的环境
func TestAutoCleanup(t *testing.T) {
    env := yttest.New(t) // 自动清理
    // 测试代码...
}

// 推荐：需要精细控制时手动管理
func TestManualControl(t *testing.T) {
    env, cancel := yttest.NewEnv(t)
    defer cancel() // 确保清理
    // 测试代码...
}
```

### 2. 错误处理

```go
// 推荐：详细的错误信息
err := env.YT.CreateNode(env.Ctx, path, yt.NodeMap, nil)
if err != nil {
    t.Fatalf("创建节点 %s 失败: %v", path, err)
}

// 推荐：使用 t.Helper() 标记辅助函数
func createTestDir(t *testing.T, env *yttest.Env, name string) ypath.Path {
    t.Helper()
    // 实现逻辑...
}
```

### 3. 测试数据准备

```go
// 推荐：使用辅助函数减少重复代码
func setupTestData(t *testing.T, env *yttest.Env) (ypath.Path, ypath.Path) {
    t.Helper()

    inputPath := env.TmpPath().Child("input")
    outputPath := env.TmpPath().Child("output")

    // 准备输入数据...

    return inputPath, outputPath
}
```

### 4. 并发测试

```go
// 推荐：使用 sync.WaitGroup 等待并发操作
func TestConcurrent(t *testing.T) {
    env := yttest.New(t)

    var wg sync.WaitGroup
    for i := 0; i < 10; i++ {
        wg.Add(1)
        go func(id int) {
            defer wg.Done()
            // 并发操作...
        }(i)
    }
    wg.Wait()
}
```

## 注意事项

1. **资源清理**：确保测试资源被正确清理
2. **临时路径**：使用 `TmpPath()` 生成唯一的测试路径
3. **错误处理**：提供详细的错误信息以便调试
4. **并发安全**：注意并发测试的线程安全
5. **性能考虑**：避免在测试中创建过大的数据集

## 相关依赖

- `go.ytsaurus.tech/yt/go/yt`: YTsaurus 客户端
- `go.ytsaurus.tech/yt/go/mapreduce`: MapReduce 客户端
- `go.ytsaurus.tech/yt/go/ypath`: 路径处理
- `go.ytsaurus.tech/yt/go/schema`: 模式定义

## 更多信息

详细的测试指南和示例请参考 [YTsaurus Go 客户端文档](https://ytsaurus.tech/docs/en/api/go)。