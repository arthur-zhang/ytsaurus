# Migrate

## 概述

Migrate 模块是 YTsaurus Go 客户端的数据库迁移工具，支持在 YTsaurus 系统中创建和管理数据迁移。该模块提供了动态表的创建、TTL（生存时间）设置等功能，帮助开发者管理数据生命周期和表结构演进。

## 功能特性

- **动态表创建**：支持创建各种类型的动态表
- **TTL 管理**：设置和管理数据的自动过期策略
- **灵活配置**：支持多种表配置选项
- **事务支持**：确保迁移操作的原子性
- **错误处理**：完善的错误处理和回滚机制

## 核心组件

### 1. CreateTable

创建各种类型的表：

```go
func CreateTable(
    ctx context.Context,
    yc yt.Client,
    path ypath.YPath,
    schema schema.Schema,
    options ...Option,
) error
```

### 2. TTL 配置

设置表的 TTL 策略：

```go
func EnableTTL(
    ctx context.Context,
    yc yt.Client,
    path ypath.YPath,
    ttlConfig *TTLConfig,
) error
```

### 3. 配置选项

```go
type Options struct {
    Attributes map[string]any
    Dynamic    bool
}
```

## 使用方法

### 创建静态表

```go
package main

import (
    "context"
    "fmt"

    "go.ytsaurus.tech/yt/go/migrate"
    "go.ytsaurus.tech/yt/go/schema"
    "go.ytsaurus.tech/yt/go/ypath"
    "go.ytsaurus.tech/yt/go/yt"
    "go.ytsaurus.tech/yt/go/yt/ythttp"
)

func createStaticTable() error {
    // 创建客户端
    yc, err := ythttp.NewClient(&yt.Config{
        Proxy:             "cluster",
        ReadTokenFromFile: true,
    })
    if err != nil {
        return err
    }
    defer yc.Close()

    ctx := context.Background()

    // 定义表结构
    tableSchema, err := schema.Infer(struct {
        ID    string `yson:"id"`
        Name  string `yson:"name"`
        Value int    `yson:"value"`
    }{})
    if err != nil {
        return err
    }

    // 创建静态表
    path := ypath.Path("//tmp/static_table")
    err = migrate.CreateTable(ctx, yc, path, tableSchema)
    if err != nil {
        return err
    }

    fmt.Printf("静态表创建成功: %s\n", path)
    return nil
}
```

### 创建动态表

```go
func createDynamicTable() error {
    yc, err := ythttp.NewClient(&yt.Config{
        Proxy:             "cluster",
        ReadTokenFromFile: true,
    })
    if err != nil {
        return err
    }
    defer yc.Close()

    ctx := context.Background()

    // 定义动态表结构
    tableSchema := schema.Schema{
        Columns: []schema.Column{
            {Name: "key", Type: schema.TypeString, SortOrder: yt.SortAscending},
            {Name: "value", Type: schema.TypeInt64},
            {Name: "timestamp", Type: schema.TypeUint64},
        },
    }

    // 创建有序动态表
    path := ypath.Path("//tmp/dynamic_table")
    err = migrate.CreateTable(ctx, yc, path, tableSchema,
        migrate.WithDynamic(true),
        migrate.WithSorted(true),
        migrate.WithUniqueKeys(true),
    )
    if err != nil {
        return err
    }

    fmt.Printf("动态表创建成功: %s\n", path)
    return nil
}
```

### 创建时序表

```go
func createTimeSeriesTable() error {
    yc, err := ythttp.NewClient(&yt.Config{
        Proxy:             "cluster",
        ReadTokenFromFile: true,
    })
    if err != nil {
        return err
    }
    defer yc.Close()

    ctx := context.Background()

    // 定义时序表结构
    tableSchema := schema.Schema{
        Columns: []schema.Column{
            {Name: "metric", Type: schema.TypeString, SortOrder: yt.SortAscending},
            {Name: "timestamp", Type: schema.TypeUint64, SortOrder: yt.SortAscending},
            {Name: "value", Type: schema.TypeDouble},
            {Name: "labels", Type: schema.TypeAny},
        },
    }

    // 创建时序表
    path := ypath.Path("//tmp/timeseries")
    err = migrate.CreateTable(ctx, yc, path, tableSchema,
        migrate.WithDynamic(true),
        migrate.WithSorted(true),
        migrate.WithBuiltinAttribute(
            "optimize_for",
            "lookup_and_scan",
        ),
        migrate.WithBuiltinAttribute(
            "in_memory_mode",
            "compressed",
        ),
    )
    if err != nil {
        return err
    }

    fmt.Printf("时序表创建成功: %s\n", path)
    return nil
}
```

### TTL 配置

```go
func configureTTL() error {
    yc, err := ythttp.NewClient(&yt.Config{
        Proxy:             "cluster",
        ReadTokenFromFile: true,
    })
    if err != nil {
        return err
    }
    defer yc.Close()

    ctx := context.Background()
    path := ypath.Path("//tmp/dynamic_table")

    // 配置 TTL - 删除 7 天前的数据
    ttlConfig := &migrate.TTLConfig{
        ColumnName: "timestamp",
        RetentionPeriod: 7 * 24 * time.Hour,
    }

    err = migrate.EnableTTL(ctx, yc, path, ttlConfig)
    if err != nil {
        return err
    }

    fmt.Printf("TTL 配置成功: %s\n", path)
    return nil
}
```

### 复杂表配置

```go
func createComplexTable() error {
    yc, err := ythttp.NewClient(&yt.Config{
        Proxy:             "cluster",
        ReadTokenFromFile: true,
    })
    if err != nil {
        return err
    }
    defer yc.Close()

    ctx := context.Background()

    // 定义复杂表结构
    tableSchema := schema.Schema{
        Columns: []schema.Column{
            // 主键
            {Name: "user_id", Type: schema.TypeString, SortOrder: yt.SortAscending},
            {Name: "session_id", Type: schema.TypeString, SortOrder: yt.SortAscending},
            {Name: "event_time", Type: schema.TypeUint64, SortOrder: yt.SortAscending},

            // 数据列
            {Name: "event_type", Type: schema.TypeString},
            {Name: "properties", Type: schema.TypeAny},
            {Name: "timestamp", Type: schema.TypeUint64},
        },
    }

    // 创建具有多种优化的表
    path := ypath.Path("//tmp/events_table")
    err = migrate.CreateTable(ctx, yc, path, tableSchema,
        migrate.WithDynamic(true),
        migrate.WithSorted(true),

        // 性能优化
        migrate.WithBuiltinAttribute("optimize_for", "lookup_and_scan"),
        migrate.WithBuiltinAttribute("in_memory_mode", "compressed"),

        // 压缩设置
        migrate.WithBuiltinAttribute("compression_codec", "lz4"),

        // 表属性
        migrate.WithAttribute("description", "User events table"),
        migrate.WithAttribute("owner", "data-team"),
        migrate.WithAttribute("retention_policy", "30d"),
    )
    if err != nil {
        return err
    }

    // 启用 TTL
    ttlConfig := &migrate.TTLConfig{
        ColumnName: "event_time",
        RetentionPeriod: 30 * 24 * time.Hour,
        ExpireColumn: "expired",
    }

    err = migrate.EnableTTL(ctx, yc, path, ttlConfig)
    if err != nil {
        return err
    }

    fmt.Printf("复杂表创建成功: %s\n", path)
    return nil
}
```

## 迁移脚本示例

### 版本化迁移

```go
type Migration struct {
    Version int
    Name    string
    Up      func(ctx context.Context, yc yt.Client) error
    Down    func(ctx context.Context, yc yt.Client) error
}

var migrations = []Migration{
    {
        Version: 1,
        Name:    "create_users_table",
        Up: func(ctx context.Context, yc yt.Client) error {
            schema := schema.Schema{
                Columns: []schema.Column{
                    {Name: "id", Type: schema.TypeString, SortOrder: yt.SortAscending},
                    {Name: "email", Type: schema.TypeString},
                    {Name: "created_at", Type: schema.TypeUint64},
                },
            }

            return migrate.CreateTable(ctx, yc,
                ypath.Path("//tmp/users"),
                schema,
                migrate.WithDynamic(true),
                migrate.WithSorted(true),
            )
        },
        Down: func(ctx context.Context, yc yt.Client) error {
            return yt.RemoveNode(ctx, yc, ypath.Path("//tmp/users"), nil)
        },
    },
    {
        Version: 2,
        Name:    "add_ttl_to_users",
        Up: func(ctx context.Context, yc yt.Client) error {
            ttlConfig := &migrate.TTLConfig{
                ColumnName: "created_at",
                RetentionPeriod: 365 * 24 * time.Hour, // 1 year
            }

            return migrate.EnableTTL(ctx, yc,
                ypath.Path("//tmp/users"),
                ttlConfig,
            )
        },
        Down: func(ctx context.Context, yc yt.Client) error {
            return migrate.DisableTTL(ctx, yc, ypath.Path("//tmp/users"))
        },
    },
}

func RunMigrations() error {
    yc, err := ythttp.NewClient(&yt.Config{
        Proxy:             "cluster",
        ReadTokenFromFile: true,
    })
    if err != nil {
        return err
    }
    defer yc.Close()

    ctx := context.Background()

    // 获取当前版本
    currentVersion, err := getCurrentVersion(ctx, yc)
    if err != nil {
        return err
    }

    // 运行待执行的迁移
    for _, migration := range migrations {
        if migration.Version > currentVersion {
            fmt.Printf("运行迁移 %d: %s\n", migration.Version, migration.Name)

            if err := migration.Up(ctx, yc); err != nil {
                return fmt.Errorf("迁移 %d 失败: %w", migration.Version, err)
            }

            // 更新版本
            if err := updateVersion(ctx, yc, migration.Version); err != nil {
                return err
            }
        }
    }

    return nil
}
```

## 最佳实践

### 1. 表设计

```go
// 主键设计
goodSchema := schema.Schema{
    Columns: []schema.Column{
        // 使用复合主键
        {Name: "partition_key", Type: schema.TypeString, SortOrder: yt.SortAscending},
        {Name: "clustering_key", Type: schema.TypeString, SortOrder: yt.SortAscending},
        {Name: "timestamp", Type: schema.TypeUint64, SortOrder: yt.SortAscending},
        // 数据列
        {Name: "data", Type: schema.TypeAny},
    },
}

// 避免过宽的行
narrowSchema := schema.Schema{
    Columns: []schema.Column{
        {Name: "id", Type: schema.TypeString, SortOrder: yt.SortAscending},
        // 使用 JSON 字段存储灵活数据
        {Name: "attributes", Type: schema.TypeAny},
    },
}
```

### 2. TTL 策略

```go
// 分层 TTL
dataLakeSchema := schema.Schema{
    Columns: []schema.Column{
        {Name: "id", Type: schema.TypeString, SortOrder: yt.SortAscending},
        {Name: "event_time", Type: schema.TypeUint64, SortOrder: yt.SortAscending},
        {Name: "tier", Type: schema.TypeString}, // hot, warm, cold
        {Name: "data", Type: schema.TypeAny},
    },
}

// 创建分区表
createPartitionedTable := func() {
    for _, tier := range []string{"hot", "warm", "cold"} {
        path := ypath.Path(fmt.Sprintf("//tmp/events_%s", tier))
        err := migrate.CreateTable(ctx, yc, path, dataLakeSchema,
            migrate.WithDynamic(true),
            migrate.WithSorted(true),
        )

        // 不同的 TTL 策略
        ttlDuration := map[string]time.Duration{
            "hot":  7 * 24 * time.Hour,
            "warm": 30 * 24 * time.Hour,
            "cold": 365 * 24 * time.Hour,
        }[tier]

        migrate.EnableTTL(ctx, yc, path, &migrate.TTLConfig{
            ColumnName: "event_time",
            RetentionPeriod: ttlDuration,
        })
    }
}
```

### 3. 性能优化

```go
// 表优化选项
optimizedTable := func() {
    options := []migrate.Option{
        migrate.WithDynamic(true),
        migrate.WithSorted(true),

        // 查询优化
        migrate.WithBuiltinAttribute("optimize_for", "lookup"),

        // 内存模式
        migrate.WithBuiltinAttribute("in_memory_mode", "compressed"),

        // 压缩
        migrate.WithBuiltinAttribute("compression_codec", "zstd"),

        // 读取性能
        migrate.WithBuiltinAttribute("max_row_weight", 16*1024*1024),

        // 写入性能
        migrate.WithBuiltinAttribute("desired_chunk_size", 1024*1024),
    }

    migrate.CreateTable(ctx, yc, path, schema, options...)
}
```

### 4. 错误处理

```go
func safeMigration() error {
    yc, err := ythttp.NewClient(&yt.Config{
        Proxy:             "cluster",
        ReadTokenFromFile: true,
    })
    if err != nil {
        return err
    }
    defer yc.Close()

    ctx, cancel := context.WithTimeout(context.Background(), 30*time.Minute)
    defer cancel()

    // 使用事务
    tx, err := yt.BeginTransaction(ctx, yc, nil)
    if err != nil {
        return err
    }

    // 在事务中执行迁移
    txClient := yt.WithTransactionID(yc, tx.ID())

    path := ypath.Path("//tmp/migration_test")
    err = migrate.CreateTable(ctx, txClient, path, schema)
    if err != nil {
        // 自动回滚
        _ = yt.AbortTransaction(ctx, yc, tx.ID(), nil)
        return fmt.Errorf("创建表失败: %w", err)
    }

    // 验证表
    attributes, err := yt.GetNode(ctx, txClient, path, nil)
    if err != nil {
        _ = yt.AbortTransaction(ctx, yc, tx.ID(), nil)
        return fmt.Errorf("验证表失败: %w", err)
    }

    // 提交事务
    if err := yt.CommitTransaction(ctx, yc, tx.ID(), nil); err != nil {
        return fmt.Errorf("提交事务失败: %w", err)
    }

    fmt.Printf("迁移成功完成: %v\n", attributes)
    return nil
}
```

## 注意事项

1. **事务支持**：大型迁移使用事务确保一致性
2. **回滚计划**：始终准备回滚方案
3. **性能影响**：迁移操作可能影响集群性能
4. **备份策略**：重要数据迁移前进行备份
5. **版本控制**：维护迁移版本历史