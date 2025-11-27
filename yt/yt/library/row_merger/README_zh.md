# Row Merger 行合并库

## 项目概述

`NRowMerger` 是 YTsaurus 中负责行数据合并的核心库，提供了多种行合并策略来处理表数据的版本控制、聚合和时间戳管理。该库支持模式化行合并、非版本化行合并、嵌套表合并和版本化行合并，是 YTsaurus 存储引擎的关键组件。

## 核心功能

- **多种合并策略**：支持 Schemaful、Unversioned、Sampling 和 Versioned 行合并
- **时间戳管理**：处理写时间戳和删除时间戳
- **列过滤**：支持列过滤器进行选择性合并
- **聚合计算**：内置聚合函数支持
- **嵌套表支持**：处理复杂的嵌套数据结构
- **内存优化**：高效的行缓冲区管理

## 主要接口

### TSchemafulRowMerger - 模式化行合并器

```cpp
#include <yt/yt/library/row_merger/row_merger.h>

using namespace NYT::NRowMerger;

// 创建模式化行合并器
auto merger = TSchemafulRowMerger(
    rowBuffer,                    // 行缓冲区
    columnCount,                  // 列数量
    keyColumnCount,              // 键列数量
    columnFilter,                // 列过滤器
    columnEvaluator,             // 列求值器
    retentionTimestamp,          // 保留时间戳
    timestampColumnMapping,      // 时间戳列映射
    nestedColumnsSchema          // 嵌套列模式
);

// 添加部分行
merger.AddPartialRow(versionedRow);
merger.AddPartialRow(versionedRow, upperTimestampLimit);

// 构建合并后的行
auto mergedRow = merger.BuildMergedRow();

// 重置合并器状态
merger.Reset();
```

### TUnversionedRowMerger - 非版本化行合并器

```cpp
// 创建非版本化行合并器
auto unversionedMerger = TUnversionedRowMerger(
    rowBuffer,
    columnCount,
    keyColumnCount,
    columnEvaluator,
    nestedColumnsSchema
);

// 添加、删除或初始化部分行
unversionedMerger.AddPartialRow(unversionedRow);
unversionedMerger.DeletePartialRow(unversionedRow);
unversionedMerger.InitPartialRow(unversionedRow);

// 构建删除行或合并行
auto deleteRow = unversionedMerger.BuildDeleteRow();
auto mergedRow = unversionedMerger.BuildMergedRow();
```

### TSamplingRowMerger - 采样行合并器

```cpp
// 创建采样行合并器
auto samplingMerger = TSamplingRowMerger(
    rowBuffer,
    tableSchema
);

// 合并行数据
auto mergedRow = samplingMerger.MergeRow(versionedRow);

// 重置状态
samplingMerger.Reset();
```

### IVersionedRowMerger - 版本化行合并接口

```cpp
// 创建版本化行合并器
auto versionedMerger = CreateVersionedRowMerger(
    rowMergerType,               // 行合并器类型
    rowBuffer,
    tableSchema,
    columnFilter,
    retentionConfig,
    currentTimestamp,
    majorTimestamp,
    columnEvaluator,
    customRuntimeData,
    mergeRowsOnFlush,
    useTtlColumn,
    mergeDeletionsOnFlush,
    memoryTracker
);

// 添加部分行
versionedMerger->AddPartialRow(versionedRow, upperTimestampLimit);

// 构建合并后的行
auto mergedRow = versionedMerger->BuildMergedRow(produceEmptyRow);

// 重置合并器
versionedMerger->Reset();
```

## 使用方法

### 基本行合并

```cpp
#include <yt/yt/library/row_merger/row_merger.h>

using namespace NYT;
using namespace NYT::NRowMerger;
using namespace NYT::NTableClient;

void mergeRows() {
    auto rowBuffer = New<TRowBuffer>(TRowBufferTag());

    // 列过滤器 - 只合并特定列
    TColumnFilter columnFilter({0, 1, 2});  // 只合并前3列

    // 创建模式化行合并器
    auto merger = TSchemafulRowMerger(
        rowBuffer,
        10,                          // 总列数
        3,                           // 键列数
        columnFilter,
        nullptr,                     // 列求值器
        NullTimestamp,               // 保留时间戳
        {},                          // 时间戳列映射
        {}                           // 嵌套列模式
    );

    // 添加多个版本的行
    for (const auto& row : versionedRows) {
        merger.AddPartialRow(row);
    }

    // 获取合并结果
    auto mergedRow = merger.BuildMergedRow();

    // 使用合并后的行
    processRow(mergedRow);
}
```

### 嵌套表合并

```cpp
#include <yt/yt/library/row_merger/nested_row_merger.h>

void processNestedColumns() {
    // 获取嵌套列模式
    auto nestedSchema = GetNestedColumnsSchema(tableSchema);

    // 过滤嵌套列模式
    auto filteredSchema = FilterNestedColumnsSchema(
        nestedSchema,
        {1, 2, 3}  // 要包含的列ID
    );

    // 创建嵌套表合并器
    TNestedTableMerger nestedMerger;

    // 解包键列
    std::vector<TMutableRange<TVersionedValue>> keyColumns;
    nestedMerger.UnpackKeyColumns(keyColumns, filteredSchema.KeyColumns);

    // 构建合并后的键列
    auto mergedKeyColumn = nestedMerger.BuildMergedKeyColumns(0, rowBuffer.Get());

    // 构建合并后的值列（带聚合）
    auto mergedValueColumn = nestedMerger.BuildMergedValueColumn(
        values,                      // 值列表
        EValueType::Int64,           // 元素类型
        &AggregateSum,               // 聚合函数
        rowBuffer.Get()
    );
}
```

### 版本化行合并

```cpp
#include <yt/yt/library/row_merger/versioned_row_merger.h>

void createVersionedMerger() {
    // 保留配置
    auto retentionConfig = New<TRetentionConfig>();
    retentionConfig->MinDataVersions = 2;
    retentionConfig->MaxDataVersions = 10;

    // 创建版本化行合并器
    auto merger = CreateVersionedRowMerger(
        NTabletClient::ERowMergerType::Sorted,
        rowBuffer,
        tableSchema,
        columnFilter,
        retentionConfig,
        GetCurrentTimestamp(),
        GetMajorTimestamp(),
        columnEvaluator,
        NYson::TYsonString("{}"),    // 自定义运行时数据
        true,                        // flush时合并行
        false,                       // 使用TTL列
        false,                       // flush时合并删除
        memoryTracker
    );

    // 按时间戳顺序添加行
    for (const auto& row : rows) {
        merger->AddPartialRow(row);
    }

    // 生成最终合并结果
    auto finalRow = merger->BuildMergedRow();
}
```

## 性能考虑

- **内存管理**：使用行缓冲区池减少内存分配开销
- **批量处理**：尽量批量添加行以提高效率
- **列过滤**：使用列过滤器减少不必要的数据处理
- **嵌套优化**：针对嵌套列的特殊优化算法

```cpp
// 性能优化示例
class OptimizedRowMerger {
public:
    OptimizedRowMerger(size_t batchSize)
        : batchSize_(batchSize)
    {
        rowBuffer_ = New<TRowBuffer>(TRowBufferTag());
        setupMerger();
    }

    void processBatch(TRange<TVersionedRow> rows) {
        merger_.Reset();

        for (const auto& row : rows) {
            merger_.AddPartialRow(row);
        }

        auto mergedRow = merger_.BuildMergedRow();
        processMergedRow(mergedRow);
    }

private:
    void setupMerger() {
        merger_ = TSchemafulRowMerger(
            rowBuffer_,
            columnCount_,
            keyColumnCount_,
            columnFilter_,
            columnEvaluator_,
            retentionTimestamp_
        );
    }

    TRowBufferPtr rowBuffer_;
    TSchemafulRowMerger merger_;
    size_t batchSize_;
};
```

## 最佳实践

1. **缓冲区管理**：合理设置行缓冲区大小，避免频繁内存分配
2. **列过滤**：只合并需要的列，提高处理效率
3. **批量操作**：批量处理行数据，减少函数调用开销
4. **错误处理**：妥善处理合并过程中的异常情况
5. **资源清理**：及时重置合并器状态，释放内存资源

```cpp
// 最佳实践示例
class RowProcessingService {
public:
    RowProcessingService() {
        initialize();
    }

    ~RowProcessingService() {
        cleanup();
    }

    void processChunk(TRange<TVersionedRow> chunk) {
        // 重置合并器状态
        merger_->Reset();

        // 批量处理行
        for (const auto& row : chunk) {
            try {
                merger_->AddPartialRow(row);
            } catch (const std::exception& ex) {
                YT_LOG_ERROR(ex, "Failed to add partial row");
                // 继续处理其他行
            }
        }

        // 生成合并结果
        auto result = merger_->BuildMergedRow();
        handleResult(result);
    }

private:
    void initialize() {
        rowBuffer_ = CreateOptimizedRowBuffer();
        merger_ = createOptimizedMerger();
    }

    void cleanup() {
        merger_.reset();
        rowBuffer_.reset();
    }

    TRowBufferPtr rowBuffer_;
    std::unique_ptr<IVersionedRowMerger> merger_;
};
```

## 依赖项

- **yt/yt/client/table_client**：表客户端接口和行类型定义
- **yt/yt/client/tablet_client**：表t客户端特定功能
- **yt/yt/library/query/base**：查询基础库
- **library/cpp/yt/compact_containers**：紧凑容器实现
- **yt/yt/core/concurrency**：并发控制支持

## 注意事项

- **线程安全**：合并器对象不是线程安全的，每个线程使用独立实例
- **内存限制**：监控内存使用情况，避免内存溢出
- **时间戳顺序**：确保按时间戳顺序添加行以保证正确的合并结果
- **列模式**：注意处理列模式变化和数据类型转换
- **嵌套限制**：嵌套表有深度和大小限制，需注意数据复杂度

该库是 YTsaurus 存储系统的核心组件，提供了高效、灵活的行数据合并能力，支持复杂的数据版本控制和聚合操作。