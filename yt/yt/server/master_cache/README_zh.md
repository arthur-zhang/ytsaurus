# 主节点缓存服务 (Master Cache)

## 概述

Master Cache 是 YTsaurus 分布式存储系统中的主节点缓存服务，为 Master 节点的元数据操作提供高性能缓存层。它通过缓存频繁访问的元数据信息，显著减少对底层存储系统的访问次数，提高集群的响应速度和吞吐量，同时降低主节点的负载压力。

## 功能特性

### 核心功能
- **元数据缓存**: 缓存节点、表、用户等核心元数据
- **多级缓存**: 支持内存和磁盘的多级缓存架构
- **缓存一致性**: 保证缓存数据与主节点数据的一致性
- **自动失效**: 自动检测和处理缓存失效事件
- **预取机制**: 智能预取热点数据提高命中率

### 高级特性
- **分布式缓存**: 支持多实例的分布式缓存架构
- **Chaos 缓存**: 支持 Chaos 实验环境的特殊缓存需求
- **动态配置**: 支持运行时配置调整和策略优化
- **性能监控**: 提供详细的缓存性能统计和监控
- **故障恢复**: 具备自动故障检测和恢复能力

## 架构设计

### 组件架构
```
Master Cache
├── Cache Core (缓存核心)
│   ├── Cache Storage (缓存存储)
│   ├── Cache Manager (缓存管理器)
│   └── Eviction Policy (淘汰策略)
├── Master Cache Part (主缓存部分)
│   ├── Bootstrap (启动引导)
│   ├── Synchronizer (同步器)
│   └── Consistency Manager (一致性管理器)
├── Chaos Cache Part (混沌缓存部分)
│   ├── Chaos Bootstrap (混沌启动)
│   ├── Experiment Manager (实验管理器)
│   └── Failure Simulator (故障模拟器)
├── Dynamic Config Manager (动态配置管理器)
│   ├── Config Loader (配置加载器)
│   ├── Policy Manager (策略管理器)
│   └── Hot Reload (热重载)
└── Monitoring System (监控系统)
    ├── Performance Metrics (性能指标)
    ├── Cache Statistics (缓存统计)
    └── Health Monitoring (健康监控)
```

### 关键组件说明

#### 1. Cache Storage (缓存存储)
- 高性能的键值存储实现
- 支持多种数据结构的缓存
- 内存和磁盘的分层存储
- 自动压缩和序列化

#### 2. Cache Manager (缓存管理器)
- 缓存项的生命周期管理
- 读写操作的并发控制
- 缓存预热和刷新策略
- 内存使用和垃圾回收

#### 3. Consistency Manager (一致性管理器)
- 与主节点的数据同步
- 版本控制和冲突解决
- 缓存失效和更新机制
- 分布式一致性保证

#### 4. Dynamic Config Manager (动态配置管理器)
- 运行时配置更新
- 缓存策略动态调整
- 性能参数实时优化
- 配置变更通知机制

## 支持的缓存类型

### 1. Node Cache (节点缓存)
```cpp
// 节点元数据缓存
struct TNodeInfo {
    TString NodeId;
    TString Address;
    TInstant LastSeen;
    TNodeState State;
    // 其他节点属性...
};
```

### 2. Table Cache (表缓存)
```cpp
// 表元数据缓存
struct TTableInfo {
    TString TableId;
    TString TablePath;
    TSchemaPtr Schema;
    TTableConfigPtr Config;
    TInstant LastModified;
};
```

### 3. User Cache (用户缓存)
```cpp
// 用户信息缓存
struct TUserInfo {
    TString UserName;
    TUserGroups Groups;
    TPermissions Permissions;
    TInstant LastLogin;
};
```

### 4. Chaos Cache (混沌缓存)
- 支持混沌工程实验
- 模拟各种故障场景
- 验证系统容错能力
- 收集实验数据

## 配置说明

### 基本配置结构
```yaml
master_cache:
  # 缓存基本配置
  cache:
    max_memory_usage: 8GB           # 最大内存使用量
    max_disk_usage: 100GB           # 最大磁盘使用量
    max_items: 1000000              # 最大缓存项数
    item_ttl: 3600s                 # 缓存项生存时间
    cleanup_interval: 300s          # 清理间隔时间

  # 分片配置
  sharding:
    enabled: true                   # 启用分片
    shard_count: 16                 # 分片数量
    hash_function: "murmur3"        # 哈希函数

  # 淘汰策略
  eviction_policy:
    type: "lru"                     # 淘汰策略: lru/lfu/fifo/random
    eviction_watermark: 0.8         # 开始淘汰的水位
    eviction_aggressiveness: 0.2    # 淘汰激进程度
```

### 主缓存部分配置
```yaml
master_cache:
  master_cache_part:
    enabled: true
    bootstrap_timeout: 60000ms      # 启动超时时间
    sync_interval: 5000ms           # 同步间隔
    connection_pool_size: 10        # 连接池大小

    # 一致性配置
    consistency:
      check_interval: 1000ms        # 一致性检查间隔
      max_staleness: 5000ms         # 最大陈旧时间
      auto_refresh: true            # 自动刷新
```

### Chaos 缓存配置
```yaml
master_cache:
  chaos_cache_part:
    enabled: false                  # 默认禁用
    experiments:
      - name: "cache_failure"
        type: "random_invalidation"
        probability: 0.01
        duration: 60s

      - name: "network_partition"
        type: "network_failure"
        target_shards: [0, 1, 2]
        duration: 30s
```

### 动态配置管理
```yaml
master_cache:
  dynamic_config:
    enabled: true
    update_interval: 10000ms        # 配置更新间隔
    retry_count: 3                  # 重试次数
    timeout: 5000ms                 # 请求超时

    # 配置源
    config_sources:
      - type: "file"
        path: "/etc/master_cache.d/conf.yson"
      - type: "http"
        url: "http://config-server:8080/cache_config"
```

## 使用方法

### 启动服务
```bash
# 从构建目录启动
./yt/yt/server/all/ytserver-all --config master_cache.config.yson

# 启用主缓存部分
./ytserver-master-cache --config master_config.yson

# 启用混沌缓存部分
./ytserver-chaos-cache --config chaos_config.yson
```

### 缓存操作
```cpp
// C++ 客户端操作示例
#include <yt/yt/server/master_cache/client.h>

// 创建缓存客户端
auto cacheClient = CreateMasterCacheClient(config);

// 缓存读取
auto nodeInfo = cacheClient->GetNodeInfo("node-001");
if (nodeInfo) {
    std::cout << "Node address: " << nodeInfo->Address << std::endl;
}

// 缓存写入
cacheClient->PutNodeInfo("node-002", nodeInfo);

// 缓存失效
cacheClient->InvalidateNodeInfo("node-001");

// 批量操作
std::vector<TString> nodeIds = {"node-001", "node-002", "node-003"};
auto nodeInfos = cacheClient->GetNodeInfos(nodeIds);
```

### 监控和统计
```bash
# 获取缓存统计信息
curl http://master-cache:8080/statistics

# 查看缓存命中率
curl http://master-cache:8080/metrics | grep cache_hit_rate

# 获取内存使用情况
curl http://master-cache:8080/memory_usage

# 查看分片状态
curl http://master-cache:8080/shards
```

### 配置管理
```bash
# 重新加载配置
curl -X POST http://master-cache:8080/reload_config

# 更新缓存策略
curl -X PUT http://master-cache:8080/cache_policy \
  -H "Content-Type: application/json" \
  -d '{"eviction_policy": "lfu", "max_memory_usage": "16GB"}'

# 清空缓存
curl -X POST http://master-cache:8080/clear_cache
```

## 实现原理

### 缓存存储机制
1. **内存存储**: 使用高效的数据结构存储热点数据
2. **磁盘存储**: 使用 SSD 或高性能磁盘存储冷数据
3. **压缩存储**: 自动压缩减少内存和磁盘占用
4. **序列化**: 高效的序列化和反序列化机制

### 一致性保证机制
1. **版本控制**: 使用版本号跟踪数据变化
2. **订阅通知**: 订阅主节点的变更事件
3. **定期同步**: 定期检查和同步数据
4. **冲突解决**: 智能的冲突检测和解决

### 分片策略
1. **一致性哈希**: 使用一致性哈希分配数据
2. **动态调整**: 支持动态增加或减少分片
3. **负载均衡**: 在分片间平衡负载
4. **故障转移**: 分片故障时的自动转移

### 淘汰策略
1. **LRU**: 最近最少使用算法
2. **LFU**: 最少使用频率算法
3. **TTL**: 基于时间的淘汰
4. **混合策略**: 结合多种因素的智能淘汰

## 性能优化

### 内存优化
- 对象池减少内存分配
- 内存映射文件提高访问速度
- 压缩算法减少内存占用
- 智能预取提高命中率

### 磁盘优化
- SSD 缓存提高IO性能
- 异步IO减少延迟
- 批量操作提高吞吐量
- 数据局部性优化

### 网络优化
- 连接复用减少开销
- 数据压缩减少传输量
- 批量请求提高效率
- 缓存预热减少冷启动

## 监控和调试

### 关键指标
- 缓存命中率和响应时间
- 内存和磁盘使用情况
- 数据一致性和延迟
- 错误率和重试次数
- 分片负载分布

### 监控端点
```bash
# 服务健康状态
curl http://master-cache:8080/health

# 详细的性能指标
curl http://master-cache:8080/metrics

# 缓存统计信息
curl http://master-cache:8080/cache_stats

# 分片详细信息
curl http://master-cache:8080/shard_details
```

### 调试工具
```bash
# 启用详细日志
export MASTER_CACHE_LOG_LEVEL=debug

# 查看缓存内容
curl http://master-cache:8080/cache_dump?pattern=*

# 分析内存使用
curl http://master-cache:8080/memory_dump

# 性能分析
perf record -p <pid> -g
```

## 故障排除

### 常见问题
1. **缓存命中率低**: 检查缓存策略和预取配置
2. **内存不足**: 调整内存限制和淘汰策略
3. **一致性问题**: 检查同步机制和网络连接
4. **性能下降**: 分析瓶颈和优化配置

### 调试步骤
1. 检查服务状态和日志
2. 分析性能指标和统计
3. 验证配置参数设置
4. 测试缓存操作
5. 检查网络和存储状况

## 安全考虑

### 访问控制
- 基于角色的访问控制
- API 认证和授权
- 网络安全隔离
- 操作审计日志

### 数据安全
- 敏感数据加密存储
- 传输过程加密保护
- 数据备份和恢复
- 访问权限管理

## 相关组件

- **Master**: 主节点服务，提供元数据
- **Node**: 节点服务，存储实际数据
- **Scheduler**: 调度器，负责任务分配
- **Discovery Server**: 服务发现和注册

## 最佳实践

### 部署建议
- 根据集群规模配置实例数量
- 使用高性能存储介质
- 合理设置内存和磁盘限制
- 启用监控和告警

### 性能调优
- 根据访问模式调整缓存策略
- 优化分片数量和分布
- 定期监控和调整参数
- 实施容量规划

### 运维管理
- 建立完善的监控体系
- 制定故障恢复流程
- 定期进行性能测试
- 保持配置文档更新

## 版本历史

- 初始版本支持基本缓存功能
- 增加分布式缓存架构
- 增强一致性和可靠性
- 增加混沌缓存支持
- 性能优化和稳定性改进