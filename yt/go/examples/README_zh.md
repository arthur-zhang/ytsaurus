# YTsaurus Go 示例

## 概述

本目录包含了 YTsaurus Go 客户端库的各种使用示例，展示了如何使用不同的功能模块来完成常见的任务。这些示例涵盖了从基础的表操作到高级的分布式计算等各个方面，是学习和参考 YTsaurus Go API 的绝佳资源。

## 示例列表

### 1. Admin (`admin/`)
展示管理操作示例：
- 集群管理
- 用户和权限管理
- 系统配置修改

### 2. Compute Email Example (`compute-email-example/`)
展示计算任务示例：
- 提交计算任务
- 处理电子邮件数据
- 任务状态监控

### 3. Count Names Example (`count-names-example/`)
MapReduce 计数示例：
- 读取大型数据集
- 统计名称出现频率
- 输出统计结果

### 4. Cypress Example (`cypress-example/`)
Cypress 路径操作示例：
- Cypress 路径解析
- 节点操作
- 属性管理

### 5. Discovery Client (`discovery-client/`)
服务发现客户端示例：
- 连接发现服务
- 查询服务端点
- 负载均衡

### 6. Dynamic Table (`dynamic-table/`)
动态表操作示例：
- 创建动态表
- 插入和更新数据
- 查询和删除操作

### 7. Ordered Dynamic Table (`ordered-dynamic-table/`)
有序动态表示例：
- 创建有序动态表
- 有序数据插入
- 范围查询

### 8. Query Tracker (`query-tracker/`)
查询跟踪示例：
- 提交 SQL 查询
- 监控查询进度
- 获取查询结果

### 9. Schema (`schema/`)
Schema 处理示例：
- 表结构定义
- Schema 推断
- 数据类型转换

### 10. Table Usage (`table-usage/`)
表操作基础示例：
- 表的创建和删除
- 数据读写
- Schema 推断和使用

### 11. Tracing (`tracing/`)
分布式追踪示例：
- 追踪配置
- 操作链路追踪
- 性能分析

### 12. Vanilla Example (`vanilla-example/`)
Vanilla 操作示例：
- 自定义操作执行
- 资源管理
- 任务编排

## 快速开始

### 运行示例

1. **设置环境**
   ```bash
   export YT_PROXY=<cluster-proxy>
   export YT_TOKEN=<auth-token>
   ```

2. **编译示例**
   ```bash
   cd examples/table-usage
   go build -o table-usage main.go
   ```

3. **运行示例**
   ```bash
   ./table-usage
   ```

### 基本示例代码结构

大多数示例遵循相似的结构：

```go
package main

import (
    "context"
    "fmt"

    "go.ytsaurus.tech/yt/go/yt"
    "go.ytsaurus.tech/yt/go/yt/ythttp"
)

func main() {
    // 创建客户端
    yc, err := ythttp.NewClient(&yt.Config{
        Proxy:             "your-cluster",
        ReadTokenFromFile: true,
    })
    if err != nil {
        panic(err)
    }
    defer yc.Close()

    // 执行示例操作
    ctx := context.Background()
    err = runExample(ctx, yc)
    if err != nil {
        panic(err)
    }
}

func runExample(ctx context.Context, yc yt.Client) error {
    // 示例逻辑...
    return nil
}
```

## 详细示例说明

### Table Usage 示例

展示基础的表操作功能：

```go
// 创建表结构
type Contact struct {
    Name  string `yson:"name"`
    Email string `yson:"email"`
    Phone string `yson:"phone"`
    Age   int    `yson:"age"`
}

// 推断 Schema
tableSchema, err := schema.Infer(Contact{})

// 创建表
_, err = yt.CreateTable(ctx, yc, tablePath, yt.WithSchema(tableSchema))

// 写入数据
writer, err := yc.WriteTable(ctx, tablePath, nil)
for _, contact := range contacts {
    err := writer.Write(contact)
    if err != nil {
        return err
    }
}
err = writer.Commit()
```

### Dynamic Table 示例

展示动态表的高级功能：

```go
// 创建动态表
schema := schema.MustInfer(/* ... */)
attributes := map[string]any{
    "dynamic": true,
    "schema":  schema,
}
_, err := yt.CreateTable(ctx, yc, path, yt.WithAttributes(attributes))

// 插入行
row := map[string]any{
    "key":   "my-key",
    "value": "my-value",
}
_, err = yc.InsertRows(ctx, path, []any{row}, nil)

// 查询行
var result []map[string]any
reader, err := yc.LookupRows(ctx, path, []any{map[string]any{"key": "my-key"}}, nil)
err = yt.ReadRowSlice(reader, &result)
```

### MapReduce 示例

展示分布式计算：

```go
// 创建 MapReduce 操作
spec := &yt.MapReduceSpec{
    Mapper: &yt.UserJob{
        JobName: "mapper",
        Command: "cat",
    },
    Reducer: &yt.UserJob{
        JobName: "reducer",
        Command: "sort | uniq -c",
    },
    InputTablePaths:  []ypath.YPath{inputPath},
    OutputTablePaths: []ypath.YPath{outputPath},
}

// 执行操作
operation, err := yt.MapReduce(ctx, yc, spec)
if err != nil {
    return err
}

// 等待完成
err = operation.Wait()
```

## 最佳实践

### 1. 错误处理

```go
// 使用结构化错误处理
err := yc.CreateTable(ctx, path, opts)
if err != nil {
    // 检查是否是表已存在错误
    if yterrors.Contains(err, "already exists") {
        // 处理表已存在的情况
    } else {
        // 处理其他错误
        return fmt.Errorf("创建表失败: %w", err)
    }
}
```

### 2. 资源管理

```go
// 使用 defer 确保资源清理
func runExample() error {
    yc, err := ythttp.NewClient(config)
    if err != nil {
        return err
    }
    defer yc.Close()

    // 其他资源的清理
    tempPath := ypath.Path("//tmp/example-" + guid.New().String())
    defer func() {
        // 清理临时数据
        yc.RemoveNode(context.Background(), tempPath, nil)
    }()

    // 执行操作...
    return nil
}
```

### 3. 批量操作

```go
// 批量写入提高性能
rows := make([]any, 0, 1000)
for i := 0; i < 1000; i++ {
    rows = append(rows, RowData{/* ... */})
}

_, err := yc.InsertRows(ctx, tablePath, rows, nil)
```

### 4. 并发控制

```go
// 使用并发处理大量数据
sem := make(chan struct{}, 10) // 限制并发数
var wg sync.WaitGroup

for _, item := range items {
    wg.Add(1)
    go func(item Item) {
        defer wg.Done()
        sem <- struct{}{} // 获取信号量
        defer func() { <-sem }() // 释放信号量

        processItem(item)
    }(item)
}

wg.Wait()
```

## 测试和调试

### 单元测试

```go
func TestExample(t *testing.T) {
    // 使用 dockertest 进行集成测试
    container, err := dockertest.InitYTsaurusContainer(ctx)
    if err != nil {
        t.Fatal(err)
    }
    defer container.Terminate(ctx)

    // 运行测试...
}
```

### 调试技巧

1. **使用详细日志**
   ```go
   yc, err := ythttp.NewClient(&yt.Config{
       Proxy: "cluster",
       Logger: log.New(),
   })
   ```

2. **打印请求/响应**
   ```go
   // 在开发阶段启用详细输出
   fmt.Printf("请求: %+v\n", request)
   fmt.Printf("响应: %+v\n", response)
   ```

3. **使用网络抓包工具**
   - Wireshark
   - tcpdump
   - MITMproxy

## 性能优化建议

### 1. 连接池配置

```go
config := &yt.Config{
    Proxy: "cluster",
    // 连接池大小
    MaxConnections: 100,
    // 连接超时
    DialTimeout: 30 * time.Second,
    // 读写超时
    ReadTimeout:  60 * time.Second,
    WriteTimeout: 60 * time.Second,
}
```

### 2. 批量处理

```go
// 使用批量操作减少网络往返
batchSize := 1000
for i := 0; i < len(data); i += batchSize {
    end := i + batchSize
    if end > len(data) {
        end = len(data)
    }

    batch := data[i:end]
    err := processBatch(ctx, yc, batch)
    if err != nil {
        return err
    }
}
```

### 3. 并发处理

```go
// 使用 worker pool 模式
workerCount := runtime.NumCPU()
jobs := make(chan Job, 100)
results := make(chan Result, 100)

// 启动 workers
for i := 0; i < workerCount; i++ {
    go worker(jobs, results)
}

// 分发任务
for _, job := range jobsList {
    jobs <- job
}
close(jobs)
```

## 贡献指南

欢迎为示例库做出贡献！

### 添加新示例

1. 在相应目录下创建新的示例文件夹
2. 编写清晰的示例代码
3. 添加详细的注释
4. 提供 README 文件说明示例用途
5. 包含错误处理和最佳实践

### 改进现有示例

1. 修复 bug
2. 更新过时的 API 用法
3. 添加更多错误处理
4. 改进性能
5. 增加更多注释

## 相关资源

- [YTsaurus 文档](https://ytsaurus.tech/docs)
- [Go 客户端 API 参考](https://pkg.go.dev/go.ytsaurus.tech/yt/go)
- [YTsaurus 最佳实践](https://ytsaurus.tech/docs/user-guide/best-practices)
- [问题报告](https://github.com/ytsaurus/ytsaurus/issues)
- [社区讨论](https://github.com/ytsaurus/ytsaurus/discussions)