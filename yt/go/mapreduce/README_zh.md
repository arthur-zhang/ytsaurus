# MapReduce

## 概述

MapReduce 模块是 YTsaurus Go 客户端的核心组件，用于在大规模数据集上执行分布式计算任务。该模块实现了 MapReduce 编程模型，支持 Mapper、Reducer 和 Combiner 等操作，能够高效地处理 TB 级别的数据。

## 功能特性

- **分布式计算**：自动分布式执行 MapReduce 作业
- **多种操作类型**：支持 Map、Reduce、MapReduce、JoinReduce 等
- **灵活的 Job 接口**：支持自定义 Go 函数作为作业逻辑
- **操作管理**：完整的作业生命周期管理
- **错误处理**：健壮的错误处理和恢复机制
- **性能优化**：支持本地组合和多种优化策略

## 核心组件

### 1. Client

MapReduce 客户端，负责提交和管理操作：

```go
type client struct {
    yc        yt.Client
    ctx       context.Context
    tmr       *timer
    debug     bool
    registry  *registry
}
```

### 2. Operation

操作接口，提供对运行中操作的控制：

```go
type Operation interface {
    ID() string
    Wait() error
    Track() (yt.OperationID, error)
    Progress() (float64, error)
    Stderr() (io.ReadCloser, error)
}
```

### 3. Job

作业接口，定义 MapReduce 逻辑：

```go
type Job interface {
    Do(ctx context.Context, in Reader, out Writer) error
}
```

## 使用方法

### 基本用法

```go
package main

import (
    "context"
    "fmt"

    "go.ytsaurus.tech/yt/go/mapreduce"
    "go.ytsaurus.tech/yt/go/mapreduce/spec"
    "go.ytsaurus.tech/yt/go/ypath"
    "go.ytsaurus.tech/yt/go/yt"
    "go.ytsaurus.tech/yt/go/yt/ythttp"
)

func main() {
    // 创建 YTsaurus 客户端
    yc, err := ythttp.NewClient(&yt.Config{
        Proxy:             "cluster",
        ReadTokenFromFile: true,
    })
    if err != nil {
        panic(err)
    }
    defer yc.Close()

    // 创建 MapReduce 客户端
    mr := mapreduce.New(yc)

    // 定义作业规范
    s := &spec.Spec{
        InputTablePaths:  []ypath.YPath{ypath.Path("//input/data")},
        OutputTablePaths: []ypath.YPath{ypath.Path("//output/result")},
    }

    // 创建 Mapper
    mapper := &mapreduce.GoJob{
        Do: func(ctx context.Context, in mapreduce.Reader, out mapreduce.Writer) error {
            for {
                row, err := in.Read()
                if err == io.EOF {
                    break
                }
                if err != nil {
                    return err
                }

                // 处理数据
                processed := processRow(row)
                if err := out.Write(processed); err != nil {
                    return err
                }
            }
            return nil
        },
    }

    // 执行 Map 操作
    operation, err := mr.Map(mapper, s)
    if err != nil {
        panic(err)
    }

    // 等待操作完成
    if err := operation.Wait(); err != nil {
        panic(err)
    }

    fmt.Println("Map 操作完成")
}
```

### MapReduce 操作

```go
func mapReduceExample() {
    // Mapper：提取并转换数据
    mapper := &mapreduce.GoJob{
        Do: func(ctx context.Context, in mapreduce.Reader, out mapreduce.Writer) error {
            for {
                var record map[string]any
                if err := in.Read(&record); err == io.EOF {
                    break
                } else if err != nil {
                    return err
                }

                // 提取键值对
                key := record["key"].(string)
                value := record["value"].(int)

                // 输出中间结果
                if err := out.Write(map[string]any{
                    "key":   key,
                    "value": value,
                }); err != nil {
                    return err
                }
            }
            return nil
        },
    }

    // Reducer：聚合数据
    reducer := &mapreduce.GoJob{
        Do: func(ctx context.Context, in mapreduce.Reader, out mapreduce.Writer) error {
            var currentKey string
            var sum int

            for {
                var record map[string]any
                if err := in.Read(&record); err == io.EOF {
                    break
                } else if err != nil {
                    return err
                }

                key := record["key"].(string)
                value := record["value"].(int)

                // 检查是否新键
                if currentKey != "" && key != currentKey {
                    // 输出前一个键的结果
                    if err := out.Write(map[string]any{
                        "key":   currentKey,
                        "total": sum,
                    }); err != nil {
                        return err
                    }
                    sum = 0
                }

                currentKey = key
                sum += value
            }

            // 输出最后一个键的结果
            if currentKey != "" {
                return out.Write(map[string]any{
                    "key":   currentKey,
                    "total": sum,
                })
            }

            return nil
        },
    }

    // 创建规范
    s := &spec.Spec{
        InputTablePaths:      []ypath.YPath{ypath.Path("//input/data")},
        OutputTablePaths:     []ypath.YPath{ypath.Path("//output/result")},
        MapOutputTableCount:  1,
        SortBy:              []yt.SortColumn{{Name: "key", SortOrder: yt.SortAscending}},
    }

    // 执行 MapReduce
    operation, err := mr.MapReduce(mapper, reducer, s)
    if err != nil {
        return err
    }

    return operation.Wait()
}
```

### Join 操作

```go
func joinExample() {
    reducer := &mapreduce.GoJob{
        Do: func(ctx context.Context, in mapreduce.Reader, out mapreduce.Writer) error {
            // 处理来自多个输入表的连接数据
            var records []map[string]any

            for {
                var record map[string]any
                if err := in.Read(&record); err == io.EOF {
                    break
                } else if err != nil {
                    return err
                }

                records = append(records, record)

                // 如果有来自所有表的数据
                if len(records) == 2 { // 假设连接两个表
                    joined := joinRecords(records[0], records[1])
                    if err := out.Write(joined); err != nil {
                        return err
                    }
                    records = nil
                }
            }
            return nil
        },
    }

    s := &spec.Spec{
        InputTablePaths: []ypath.YPath{
            ypath.Path("//input/table1"),
            ypath.Path("//input/table2"),
        },
        OutputTablePaths: []ypath.YPath{ypath.Path("//output/joined")},
    }

    operation, err := mr.JoinReduce(reducer, s)
    if err != nil {
        return err
    }

    return operation.Wait()
}
```

### 高级配置

```go
func advancedExample() {
    s := &spec.Spec{
        InputTablePaths:  []ypath.YPath{ypath.Path("//input/data")},
        OutputTablePaths: []ypath.YPath{ypath.Path("//output/result")},

        // Map 配置
        Mapper: &spec.Mapper{
            JobType: "user_job",
            MemoryLimit: 1024 * 1024 * 1024, // 1GB
            JobCount:    10,
        },

        // Reduce 配置
        Reducer: &spec.Reducer{
            JobType:     "user_job",
            MemoryLimit: 2 * 1024 * 1024 * 1024, // 2GB
            JobCount:    5,
        },

        // 排序配置
        SortBy: []yt.SortColumn{
            {Name: "key", SortOrder: yt.SortAscending},
            {Name: "timestamp", SortOrder: yt.SortDescending},
        },

        // 输入格式
        InputFormat: &yt.Format{
            Name: "yson",
        },

        // 输出格式
        OutputFormat: &yt.Format{
            Name: "yson",
        },
    }

    // 使用操作选项
    opts := []mapreduce.OperationOption{
        mapreduce.WithPool("my-pool"),
        mapreduce.WithTitle("My MapReduce Operation"),
        mapreduce.WithResourceLimits(mapreduce.ResourceLimits{
            Memory: 4 * 1024 * 1024 * 1024, // 4GB
            CPU:    4,
        }),
    }

    operation, err := mr.MapReduce(mapper, reducer, s, opts...)
    if err != nil {
        return err
    }

    // 监控进度
    ticker := time.NewTicker(5 * time.Second)
    defer ticker.Stop()

    for {
        select {
        case <-ticker.C:
            progress, err := operation.Progress()
            if err != nil {
                return err
            }
            fmt.Printf("进度: %.2f%%\n", progress*100)

            // 获取日志
            stderr, err := operation.Stderr()
            if err == nil {
                // 读取日志...
            }

        case <-ctx.Done():
            return ctx.Err()
        }
    }
}
```

## Job 类型

### 1. GoJob

使用 Go 函数实现的作业：

```go
goJob := &mapreduce.GoJob{
    Do: func(ctx context.Context, in mapreduce.Reader, out mapreduce.Writer) error {
        // 自定义逻辑
        return nil
    },
}
```

### 2. RawJob

使用原始命令的作业：

```go
rawJob := &mapreduce.RawJob{
    Command: "cat",
}
```

### 3. VanilaJob

Vanilla 操作作业：

```go
vanillaJob := &mapreduce.VanillaJob{
    Task: map[string]interface{}{
        "prepare": map[string]interface{}{
            "command": "prepare.sh",
        },
        "run": map[string]interface{}{
            "command": "run.sh",
            "file_paths": []string{"./run.sh"},
        },
    },
}
```

## 操作选项

### 常用选项

```go
opts := []mapreduce.OperationOption{
    // 设置作业池
    mapreduce.WithPool("production"),

    // 设置标题
    mapreduce.WithTitle("Data Processing"),

    // 设置资源限制
    mapreduce.WithResourceLimits(mapreduce.ResourceLimits{
        Memory: 8 * 1024 * 1024 * 1024,
        CPU:    8,
    }),

    // 设置超时
    mapreduce.WithTimeout(2 * time.Hour),

    // 设置重试策略
    mapreduce.WithMaxFailedJobCount(10),

    // 设置数据大小限制
    mapreduce.WithMaxDataSizePerJob(1024 * 1024 * 1024),
}
```

## 错误处理

### 1. 操作级错误

```go
operation, err := mr.Map(mapper, spec)
if err != nil {
    // 处理提交错误
    return fmt.Errorf("提交操作失败: %w", err)
}

// 等待完成
if err := operation.Wait(); err != nil {
    // 处理执行错误
    var ytErr *yterrors.Error
    if yterrors.As(err, &ytErr) {
        fmt.Printf("YT 错误: %s\n", ytErr.Message)
    }
    return err
}
```

### 2. Job 级错误

```go
goJob := &mapreduce.GoJob{
    Do: func(ctx context.Context, in mapreduce.Reader, out mapreduce.Writer) error {
        for {
            var row map[string]any
            if err := in.Read(&row); err != nil {
                if err == io.EOF {
                    break
                }
                // 记录错误但继续处理
                log.Printf("读取行失败: %v", err)
                continue
            }

            // 处理数据
            if err := processRow(row); err != nil {
                log.Printf("处理行失败: %v", err)
                continue
            }
        }
        return nil
    },
}
```

## 性能优化

### 1. 数据本地性

```go
// 启用数据本地性优化
s := &spec.Spec{
    InputTablePaths: []ypath.YPath{ypath.Path("//input/data")},

    // 本地性优化选项
    JobIO: &spec.JobIO{
        TableReader: &spec.TableReader{
            // 启用有序读取
            OptimizedForSequential: true,
        },
        TableWriter: &spec.TableWriter{
            // 启用批量写入
            MaxBufferSize: 1024 * 1024,
        },
    },
}
```

### 2. 内存管理

```go
// 控制内存使用
goJob := &mapreduce.GoJob{
    Do: func(ctx context.Context, in mapreduce.Reader, out mapreduce.Writer) error {
        // 使用固定大小的缓冲区
        buffer := make([]Record, 0, 1000)

        for {
            var record Record
            if err := in.Read(&record); err == io.EOF {
                // 刷新缓冲区
                if err := flushBuffer(buffer, out); err != nil {
                    return err
                }
                break
            }

            buffer = append(buffer, record)

            // 定期刷新
            if len(buffer) == cap(buffer) {
                if err := flushBuffer(buffer, out); err != nil {
                    return err
                }
                buffer = buffer[:0]
            }
        }
        return nil
    },
}
```

### 3. 并发处理

```go
goJob := &mapreduce.GoJob{
    Do: func(ctx context.Context, in mapreduce.Reader, out mapreduce.Writer) error {
        // 使用 worker pool
        numWorkers := 4
        jobs := make(chan Record, 100)
        results := make(chan ProcessedRecord, 100)

        // 启动 workers
        for i := 0; i < numWorkers; i++ {
            go worker(ctx, jobs, results)
        }

        // 读取和分发
        go func() {
            defer close(jobs)
            for {
                var record Record
                if err := in.Read(&record); err == io.EOF {
                    break
                } else if err != nil {
                    return
                }
                jobs <- record
            }
        }()

        // 写入结果
        for i := 0; i < numWorkers; i++ {
            result := <-results
            if err := out.Write(result); err != nil {
                return err
            }
        }

        return nil
    },
}
```

## 监控和调试

### 1. 进度跟踪

```go
func monitorOperation(operation mapreduce.Operation) {
    ticker := time.NewTicker(10 * time.Second)
    defer ticker.Stop()

    for {
        select {
        case <-ticker.C:
            progress, err := operation.Progress()
            if err != nil {
                log.Printf("获取进度失败: %v", err)
                continue
            }

            id, err := operation.Track()
            if err != nil {
                log.Printf("获取操作ID失败: %v", err)
                continue
            }

            log.Printf("操作 %s: %.2f%% 完成", id, progress*100)

        case <-ctx.Done():
            return
        }
    }
}
```

### 2. 日志查看

```go
func viewLogs(operation mapreduce.Operation) {
    stderr, err := operation.Stderr()
    if err != nil {
        log.Printf("获取日志失败: %v", err)
        return
    }
    defer stderr.Close()

    scanner := bufio.NewScanner(stderr)
    for scanner.Scan() {
        fmt.Printf("日志: %s\n", scanner.Text())
    }
}
```

### 3. 性能分析

```go
// 启用调试模式
mr := mapreduce.New(yc, mapreduce.WithDebug(true))

// 或在操作中启用
opts := []mapreduce.OperationOption{
    mapreduce.WithDebug(true),
}

operation, err := mr.Map(mapper, spec, opts...)
```

## 注意事项

1. **资源管理**：合理设置内存和 CPU 限制
2. **错误处理**：实现健壮的错误处理逻辑
3. **数据倾斜**：注意 key 分布，避免数据倾斜
4. **网络传输**：最小化数据在网络中的传输
5. **作业数量**：根据集群大小调整并发作业数