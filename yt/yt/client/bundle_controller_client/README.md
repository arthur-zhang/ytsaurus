# YTsaurus Bundle Controller 客户端

## 概述

`bundle_controller_client` 目录提供了 YTsaurus Bundle Controller 的客户端接口。Bundle Controller 是 YTsaurus 中负责管理和配置服务器 Bundle（服务器集合）的组件，用于控制集群中 Tablet Server 和其他服务的资源配置和部署策略。

## 核心功能

### Bundle 配置管理
- **配置获取**: 获取指定 Bundle 的当前配置信息
- **配置设置**: 更新 Bundle 的配置参数
- **配置约束**: 管理 Bundle 配置的约束和限制
- **资源配额**: 控制 Bundle 的资源使用配额

### 资源管理
- **CPU 资源**: 管理 Bundle 的 CPU 资源限制和线程池配置
- **内存资源**: 控制各种类型内存的使用限制
- **实例资源**: 管理 Bundle 中实例的资源分配

### 实例管理
- **实例大小**: 定义不同大小的实例规格
- **默认配置**: 提供实例的默认配置模板
- **实例资源**: 计算和管理实例的资源需求

## 主要文件说明

### 核心客户端接口
- `bundle_controller_client.h/.cpp`: Bundle Controller 客户端接口实现
  - `IBundleControllerClient`: 主要客户端接口
  - `TBundleConfigDescriptor`: Bundle 配置描述符
  - `TGetBundleConfigOptions`: 获取配置选项
  - `TSetBundleConfigOptions`: 设置配置选项

### 配置和设置
- `bundle_controller_settings.h/.cpp`: Bundle 配置设置定义
  - `TCpuLimits`: CPU 资源限制配置
  - `TMemoryLimits`: 内存资源限制配置
  - `TInstanceResources`: 实例资源需求定义
  - `TDefaultInstanceConfig`: 默认实例配置
  - `TInstanceSize`: 实例大小规格
  - `TBundleTargetConfig`: Bundle 目标配置
  - `TBundleConfigConstraints`: Bundle 配置约束
  - `TBundleResourceQuota`: Bundle 资源配额

### 公共接口
- `public.h`: 公共类型声明和前向定义

## 配置详细说明

### CPU 资源配置
```cpp
struct TCpuLimits {
    std::optional<int> LookupThreadPoolSize;    // 查询线程池大小
    std::optional<int> QueryThreadPoolSize;      // 查询处理线程池大小
    std::optional<int> WriteThreadPoolSize;      // 写入操作线程池大小
};
```

### 内存资源配置
```cpp
struct TMemoryLimits {
    std::optional<i64> CompressedBlockCache;     // 压缩块缓存
    std::optional<i64> KeyFilterBlockCache;      // 键过滤块缓存
    std::optional<i64> LookupRowCache;           // 查找行缓存
    std::optional<i64> TabletDynamic;            // Tablet 动态内存
    std::optional<i64> TabletStatic;             // Tablet 静态内存
    std::optional<i64> UncompressedBlockCache;   // 未压缩块缓存
    std::optional<i64> VersionedChunkMeta;       // 版本化 Chunk 元数据
    std::optional<i64> Reserved;                 // 预留内存
    std::optional<i64> Query;                    // 查询内存
};
```

## 使用示例

### 创建客户端
```cpp
#include <yt/yt/client/bundle_controller_client/bundle_controller_client.h>

// 创建 Bundle Controller 客户端
auto client = CreateBundleControllerClient(connection);
```

### 获取 Bundle 配置
```cpp
// 获取 Bundle 配置
auto future = client->GetBundleConfig("my_bundle");
auto configDescriptor = future.Get();

// 访问配置信息
auto bundleName = configDescriptor->BundleName;
auto config = configDescriptor->Config;
auto constraints = configDescriptor->ConfigConstraints;
auto quota = configDescriptor->ResourceQuota;
```

### 设置 Bundle 配置
```cpp
// 创建新的 Bundle 配置
auto newConfig = New<TBundleTargetConfig>();
// 设置配置参数...

// 更新 Bundle 配置
auto future = client->SetBundleConfig(
    "my_bundle",
    newConfig,
    TSetBundleConfigOptions()
);
future.Get(); // 等待操作完成
```

## Bundle 配置管理

### 配置约束
Bundle 配置支持多种约束机制：
- **资源约束**: 限制 Bundle 可使用的最大资源
- **实例约束**: 限制 Bundle 中实例的数量和大小
- **性能约束**: 限制 Bundle 的性能参数

### 资源配额
支持细粒度的资源配额管理：
- **CPU 配额**: 限制 CPU 使用率
- **内存配额**: 限制内存使用量
- **存储配额**: 限制存储空间使用
- **网络配额**: 限制网络带宽使用

### 配置验证
所有配置变更都会进行严格验证：
- **格式验证**: 检查配置格式是否正确
- **约束验证**: 检查是否满足预定义约束
- **资源验证**: 检查资源分配是否合理
- **依赖验证**: 检查配置间的依赖关系

## 实例规格管理

### 预定义实例规格
支持多种预定义的实例规格：
- **小规格**: 适用于低负载场景
- **中规格**: 适用于中等负载场景
- **大规格**: 适用于高负载场景
- **自定义规格**: 支持用户自定义配置

### 实例配置模板
提供丰富的实例配置模板：
- **默认配置**: 通用默认配置
- **优读配置**: 优化读性能的配置
- **优写配置**: 优化写性能的配置
- **平衡配置**: 读写平衡的配置

## 监控和诊断

### 配置状态监控
- **配置版本**: 跟踪配置变更历史
- **应用状态**: 监控配置应用进度
- **错误报告**: 记录配置变更错误

### 性能指标
- **资源使用率**: 监控各种资源的使用情况
- **性能指标**: 跟踪 Bundle 的性能表现
- **容量指标**: 监控容量使用情况

## 错误处理

### 常见错误类型
- **配置格式错误**: 配置参数格式不正确
- **约束违反错误**: 配置违反预定义约束
- **资源不足错误**: 分配的资源不足
- **权限错误**: 没有配置修改权限

### 错误恢复机制
- **自动回滚**: 配置失败时自动回滚
- **重试机制**: 临时性错误自动重试
- **降级处理**: 部分失败时优雅降级

## 最佳实践

### 配置管理
1. **渐进式变更**: 避免大规模一次性配置变更
2. **充分测试**: 在测试环境充分验证配置
3. **监控影响**: 密切监控配置变更的影响
4. **备份配置**: 保留配置备份以备恢复

### 资源规划
1. **容量规划**: 根据业务增长预测资源需求
2. **性能调优**: 根据性能指标调整资源配置
3. **成本控制**: 在性能和成本间找到平衡
4. **冗余配置**: 预留适当的资源冗余

## 注意事项

1. **权限管理**: 确保用户具有必要的配置修改权限
2. **一致性**: 保持 Bundle 配置与集群状态的一致性
3. **监控告警**: 设置适当的配置变更监控和告警
4. **文档记录**: 详细记录配置变更的原因和影响
5. **测试验证**: 生产环境变更前必须充分测试

## 扩展性

该模块设计支持：
- **自定义约束**: 添加新的配置约束类型
- **插件化配置**: 支持第三方配置插件
- **监控集成**: 与外部监控系统集成
- **自动化工具**: 支持配置管理和自动化工具