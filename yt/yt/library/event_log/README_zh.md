# Event Log (事件日志)

事件日志是 YTsaurus 中用于记录和管理系统事件的框架，提供高效的事件收集、序列化和持久化功能。

## 概述

事件日志系统提供以下核心功能：
- 结构化事件记录
- 异步批量写入
- YSON格式序列化
- 可配置的刷新策略
- 灵活的事件格式定义

## 核心组件

### 1. IEventLogWriter (事件写入器)
- **功能**: 事件日志的写入接口
- **特点**:
  - 异步写入支持
  - 批量处理优化
  - 配置动态更新
  - 优雅关闭机制

#### 主要接口
```cpp
struct IEventLogWriter : public TRefCounted {
    // 创建YSON消费者
    virtual std::unique_ptr<NYson::IYsonConsumer> CreateConsumer() = 0;

    // 获取当前配置
    virtual TEventLogManagerConfigPtr GetConfig() const = 0;

    // 更新配置
    virtual void UpdateConfig(const TEventLogManagerConfigPtr& config) = 0;

    // 关闭写入器
    virtual TFuture<void> Close() = 0;
};
```

### 2. TFluentLogEvent (流畅事件构建器)
- **功能**: 提供流畅的API构建事件
- **特点**:
  - 链式调用语法
  - 类型安全的字段设置
  - 自动资源管理
  - YSON格式输出

#### 使用示例
```cpp
auto event = CreateEventLogWriter(config, invoker, writer, logger);
auto consumer = event->CreateConsumer();
TFluentLogEvent fluent(std::move(consumer))
    .Item("event_type").Value("user_login")
    .Item("user_id").Value("john_doe")
    .Item("timestamp").Value(TInstant::Now())
    .Item("ip_address").Value("192.168.1.100");
```

### 3. TFluentLogEventConsumer (事件消费者)
- **功能**: YSON事件消费实现
- **特点**:
  - 与日志系统集成
  - 自动格式化输出
  - 错误处理机制

### 4. TEventLogManagerConfig (配置管理)
- **功能**: 事件日志管理器配置
- **配置项**:
  - `Enable`: 是否启用事件日志
  - `PendingRowsFlushPeriod`: 待刷新行的刷新周期

## 配置说明

```yaml
event_log_manager:
  enable: true                          # 启用事件日志
  pending_rows_flush_period: 5000ms     # 刷新周期5秒
```

## 使用方法

### 创建事件写入器
```cpp
// 准备配置
auto config = New<TEventLogManagerConfig>();
config->SetEnable(true);
config->SetPendingRowsFlushPeriod(TDuration::Seconds(5));

// 创建写入器
auto writer = CreateEventLogWriter(
    config,
    GetSyncInvoker(),
    tableWriter,
    Logger);
```

### 记录事件
```cpp
// 方法1: 使用流畅API
void LogUserAction(const std::string& action, const std::string& user) {
    auto consumer = EventWriter->CreateConsumer();
    TFluentLogEvent event(std::move(consumer));
    event
        .Item("timestamp").Value(TInstant::Now())
        .Item("action").Value(action)
        .Item("user").Value(user)
        .Item("service").Value("auth_service");
}

// 方法2: 手动构建YSON
void LogSystemEvent(const TError& error) {
    auto consumer = EventWriter->CreateConsumer();
    consumer->OnBeginMap();
    consumer->OnKeyedItem("event_type");
    consumer->OnStringScalar("system_error");
    consumer->OnKeyedItem("error");
    NYson::Serialize(error, consumer.get());
    consumer->OnKeyedItem("severity");
    consumer->OnStringScalar("critical");
    consumer->OnEndMap();
}
```

### 更新配置
```cpp
// 动态更新配置
auto newConfig = New<TEventLogManagerConfig>();
newConfig->SetEnable(false);  // 临时禁用
EventWriter->UpdateConfig(newConfig);
```

### 优雅关闭
```cpp
// 关闭事件写入器，确保所有事件都被写入
auto closeFuture = EventWriter->Close();
WaitFor(closeFuture).ThrowOnError();
```

## 事件格式

事件以YSON格式存储，建议包含以下字段：
- **timestamp**: 事件时间戳
- **event_type**: 事件类型标识
- **service**: 服务名称
- **host**: 主机名
- **severity**: 严重级别 (info/warning/error/critical)
- **user**: 相关用户（如果适用）
- **request_id**: 请求ID（用于追踪）
- **data**: 事件特定数据

### 示例事件
```yaml
{
  "timestamp" = "2024-01-20T10:30:45.123456Z";
  "event_type" = "job_started";
  "service" = "scheduler";
  "host" = "node-1.cluster.local";
  "severity" = "info";
  "operation_id" = "5f2a8b1c-3d4e-5f6a-7b8c-9d0e1f2a3b4c";
  "job_id" = "job-12345";
  "data" = {
    "job_type" = "map";
    "input_size" = 1073741824;
    "output_paths" = ["/tmp/output1", "/tmp/output2"];
  };
}
```

## 性能优化

### 1. 批量写入
- 自动批量收集事件
- 定期刷新到存储
- 减少I/O开销

### 2. 异步处理
- 非阻塞事件记录
- 后台线程处理写入
- 缓冲区管理

### 3. 内存优化
- 使用对象池
- 智能指针管理
- 及时释放资源

## 最佳实践

### 1. 事件设计
- 保持事件结构一致
- 使用有意义的事件类型
- 包含足够的上下文信息

### 2. 性能考虑
```cpp
// 避免在热路径记录过多事件
if (LogLevel >= NLogging::ELogLevel::Info) {
    LogDetailedEvent();
}

// 批量记录相关事件
{
    auto consumer = EventWriter->CreateConsumer();
    TFluentLogEvent fluent(std::move(consumer));
    fluent
        .Item("batch_id").Value(batchId)
        .Item("events").BeginList();
    for (const auto& event : events) {
        fluent.Item().BeginMap()
            .Item("type").Value(event.type)
            .Item("data").Value(event.data)
            .EndMap();
    }
    fluent.EndList();
}
```

### 3. 错误处理
- 检查写入器状态
- 处理写入失败
- 实现降级策略

## 监控指标

建议监控以下指标：
- 事件写入速率
- 缓冲区使用率
- 写入延迟
- 失败事件数量

## 依赖项

- YTsaurus 核心库 (`yt/yt/core/`)
- 表客户端库 (`yt/yt/client/table_client/`)
- YSON 库 (`yt/yt/core/yson/`)
- YTree 库 (`yt/yt/core/ytree/`)

## 注意事项

1. **性能影响**: 事件记录有一定开销，合理控制记录频率
2. **存储空间**: 事件日志会占用存储空间，定期清理旧数据
3. **一致性**: 确保事件格式的一致性以便于分析
4. **错误恢复**: 实现适当的错误恢复机制
5. **配置管理**: 合理设置刷新周期平衡性能和实时性