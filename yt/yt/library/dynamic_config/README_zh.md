# Dynamic Config (动态配置)

动态配置是 YTsaurus 中提供的运行时配置管理系统，允许在不重启服务的情况下动态更新配置参数。

## 概述

动态配置系统提供了以下核心功能：
- 从 Cypress 周期性拉取配置
- 支持基于标签的条件配置
- 配置变更实时通知
- 配置验证和错误处理
- 通过 Orchid 提供监控接口

## 核心组件

### 1. TDynamicConfigManagerBase
- **文件**: `dynamic_config_manager.h` 和 `dynamic_config_manager-inl.h`
- **功能**: 模板化的动态配置管理器基类
- **特点**:
  - 线程安全
  - 异步更新
  - 信号机制通知变更
  - 支持多种配置源

### 2. 配置结构
- **TDynamicConfigManagerOptions**: 管理器选项
  - `ConfigPath`: Cypress 中的配置路径
  - `Name`: 管理器名称
  - `ConfigIsTagged`: 是否使用标签化配置
  - `ReadFrom`: 主节点通道类型
  - `SuppressTransactionCoordinatorSync`: 是否抑制事务协调器同步

- **TDynamicConfigManagerConfig**: 管理器配置
  - `UpdatePeriod`: 配置更新周期
  - `EnableUnrecognizedOptionsAlert`: 是否启用未识别选项告警
  - `IgnoreConfigAbsence`: 是否忽略配置缺失

## 主要接口

### 配置管理器接口
```cpp
// 启动动态配置管理器
void Start();

// 获取当前配置
TConfigPtr GetConfig() const;

// 获取初始配置
TConfigPtr GetInitialConfig() const;

// 获取配置节点
NYTree::IMapNodePtr GetConfigNode() const;

// 检查配置是否已加载
bool IsConfigLoaded() const;

// 获取加载完成的Future
TFuture<void> GetConfigLoadedFuture() const;

// 获取错误信息
std::vector<TError> GetErrors() const;

// 获取Orchid监控服务
NYTree::IYPathServicePtr GetOrchidService() const;
```

### 配置变更信号
```cpp
// 配置变更信号
DEFINE_SIGNAL(void(const TConfigPtr& oldConfig, const TConfigPtr& newConfig), ConfigChanged);
```

## 使用方法

### 创建动态配置管理器
```cpp
// 配置选项
TDynamicConfigManagerOptions options{
    .ConfigPath = "//sys/my_service/config",
    .Name = "MyServiceConfigManager",
    .ConfigIsTagged = true
};

// 创建管理器配置
auto managerConfig = New<TDynamicConfigManagerConfig>();
managerConfig->SetUpdatePeriod(TDuration::Seconds(30));

// 创建管理器
auto configManager = New<TDynamicConfigManagerBase<TMyConfig>>(
    options,
    managerConfig,
    client,
    invoker);

// 订阅配置变更
configManager->SubscribeConfigChanged(BIND([&] (const auto& oldConfig, const auto& newConfig) {
    YT_LOG_INFO("Configuration updated");
    // 处理配置变更
}));

// 启动管理器
configManager->Start();
```

### 标签化配置
当启用 `ConfigIsTagged` 时，配置节点包含从布尔公式到动态配置的映射：

```yaml
# Cypress 配置节点内容
{
    "env == \"prod\" and version == \"v2\"": {
        "max_connections": 1000,
        "timeout": 5000
    },
    "env == \"test\"": {
        "max_connections": 100,
        "timeout": 1000
    }
}
```

## 错误处理

### 错误类型
```cpp
enum class EErrorCode {
    FailedToFetchDynamicConfig = 2600,      // 获取动态配置失败
    DuplicateMatchingDynamicConfigs = 2601, // 存在多个匹配的配置
    UnrecognizedDynamicConfigOption = 2602, // 未识别的配置选项
    FailedToApplyDynamicConfig = 2603,      // 应用动态配置失败
    InvalidDynamicConfig = 2604,            // 无效的动态配置
    NoSuitableDynamicConfig = 2605          // 没有合适的配置
};
```

### 错误处理策略
- 自动重试获取配置
- 保持上次成功配置
- 生成告警信息
- 记录详细错误日志

## 监控和调试

### Orchid 接口
动态配置管理器通过 Orchid 提供监控信息：
- `/config`: 当前配置
- `/last_update_time`: 最后更新时间
- `/last_change_time`: 最后变更时间
- `/errors`: 错误列表
- `/unrecognized_options`: 未识别的选项

### 日志记录
- 配置加载成功/失败
- 配置变更通知
- 错误详情
- 性能指标

## 性能考虑

1. **更新频率**: 合理设置更新周期，避免过度频繁
2. **网络开销**: 使用缓存通道减少网络请求
3. **内存使用**: 配置对象轻量化，避免内存泄漏
4. **并发访问**: 使用原子操作和锁保证线程安全

## 最佳实践

1. **配置设计**
   - 配置结构扁平化
   - 使用明确的类型
   - 提供默认值
   - 文档化每个选项

2. **错误处理**
   - 优雅降级
   - 详细日志
   - 及时告警
   - 自动恢复

3. **性能优化**
   - 批量更新
   - 异步处理
   - 缓存机制
   - 避免阻塞

## 依赖项

- YT 核心库 (`yt/yt/core/`)
- 客户端库 (`yt/yt/client/`)
- API 库 (`yt/yt/ytlib/api/`)
- YTree 库 (`yt/yt/core/ytree/`)
- 线程库 (`library/cpp/yt/threading/`)

## 注意事项

1. 配置更新是异步的，可能有短暂延迟
2. 多个匹配的标签化配置会导致冲突
3. 配置验证失败时保持原配置
4. 需要适当的权限访问 Cypress 节点
5. 注意配置版本兼容性