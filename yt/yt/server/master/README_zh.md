# YTsaurus Master 服务

## 概述

YTsaurus Master 是集群的中央元数据管理服务，作为整个系统的核心控制平面。它负责管理所有元数据操作、事务处理、访问控制以及集群的统一协调。Master 是 YTsaurus 架构中的关键组件，确保分布式环境下数据的一致性和可靠性。

Master 服务采用主从复制架构，通过 Raft 协议实现高可用性和故障恢复，支持水平扩展以处理大规模集群的元数据请求。

## 核心功能

### 1. 元数据管理
- **Cypress 管理**：负责 Cypress（YTsaurus 的层次化文件系统）的节点创建、更新、删除操作
- **对象生命周期管理**：处理所有系统对象的创建、修改和销毁
- **Schema 管理**：维护表结构和数据类型定义
- **引用计数和垃圾回收**：自动清理不再使用的对象

### 2. 事务处理
- **分布式事务**：提供 ACID 事务支持，跨多个节点和表
- **事务协调**：协调分布式事务的两阶段提交
- **锁管理**：支持乐观锁和悲观锁机制
- **冲突检测和解决**：自动处理并发访问冲突

### 3. Chunk 管理
- **Chunk 元数据**：维护所有数据块的位置信息和元数据
- **副本管理**：管理数据副本的分布和冗余度
- **数据平衡**：自动平衡数据在集群中的分布
- **Chunk 生命周期**：处理 Chunk 的创建、合并、分裂和清理

### 4. 节点跟踪
- **节点注册**：管理集群中所有节点的注册和心跳
- **健康监控**：监控节点状态和可用性
- **资源统计**：收集和维护集群资源使用情况
- **故障检测**：快速检测和响应节点故障

### 5. 安全管理
- **访问控制**：基于角色的访问控制 (RBAC)
- **用户认证**：支持多种认证机制
- **权限管理**：细粒度的权限控制系统
- **审计日志**：记录所有重要操作用于审计

### 6. Tablet 管理
- **Tablet Cell 管理**：管理 Tablet Cell 的创建和配置
- **负载均衡**：自动平衡 Tablet 在节点间的分布
- **Leader 选举**：处理 Tablet Leader 的选举和故障转移
- **数据迁移**：协调 Tablet 在节点间的迁移

## 架构设计

### 核心组件

#### 1. Cypress Server
```
cypress_server/
├── cypress_manager.cpp      # Cypress 管理器核心实现
├── expiration_tracker.cpp   # 过期节点跟踪器
├── grafting_manager.cpp     # 节点移植管理器
└── portal_manager.cpp       # 门户管理器
```

#### 2. Transaction Server
```
transaction_server/
├── transaction_manager.cpp   # 事务管理器
├── transaction_finisher.cpp  # 事务完成处理器
└── transaction_service.cpp   # 事务服务接口
```

#### 3. Chunk Server
```
chunk_server/
├── chunk_manager.cpp          # Chunk 管理器
├── data_node_tracker.cpp      # 数据节点跟踪器
├── chunk_autotomizer.cpp      # Chunk 自动分割器
└── chunk_merger.cpp           # Chunk 合并器
```

#### 4. Object Server
```
object_server/
├── object_manager.cpp         # 对象管理器
├── master_proxy.cpp           # Master 代理
└── object_service.cpp         # 对象服务
```

#### 5. Tablet Server
```
tablet_server/
├── tablet_manager.cpp         # Tablet 管理器
├── tablet_node_tracker.cpp    # Tablet 节点跟踪器
└── backup_manager.cpp         # 备份管理器
```

### 数据流程

1. **客户端请求处理**
   - RPC Proxy 接收客户端请求
   - 路由到对应的 Master 服务
   - 执行相应的操作和验证

2. **元数据修改流程**
   - 事务开始时分配事务 ID
   - 执行操作并记录到 WAL
   - 通过 Raft 协议复制到跟随者
   - 提交事务并更新状态机

3. **分布式协调**
   - 通过 Hydra 框架实现分布式一致性
   - 使用 Snapshots 进行状态同步
   - 支持动态配置更新

## 配置说明

### 关键配置参数

#### 基础配置
```yaml
master:
  # Master 服务监听地址
  rpc_port: 9013
  # HTTP 监控端口
  monitoring_port: 9014

  # 集群标识
  cell_id: "master-cell-1"

  # 最大并发请求数
  max_concurrent_requests: 10000
```

#### Cypress 配置
```yaml
cypress_manager:
  # 最大节点数量
  max_node_count: 10000000
  # 事务超时时间
  transaction_timeout: 60000
  # 批处理大小
  batch_size: 1000
```

#### 事务配置
```yaml
transaction_manager:
  # 最大事务持续时间
  max_transaction_duration: 3600000
  # 清理间隔
  cleanup_period: 5000
  # 最大并发事务数
  max_concurrent_transactions: 100000
```

#### Chunk 配置
```yaml
chunk_manager:
  # 默认副本数
  default_replication_factor: 3
  # 最大副本数
  max_replication_factor: 10
  # 重新平衡间隔
  rebalance_period: 30000
```

### 动态配置

Master 支持运行时动态配置更新，无需重启服务：

```yaml
dynamic_config:
  # 更新间隔
  update_period: 5000
  # 配置路径
  config_path: "//sys/master/config"
```

## 使用方法

### 启动 Master 服务

1. **编译 Master 二进制**
```bash
# 构建所有组件
ninja ytserver-all

# 或仅构建 Master
ninja ytserver-master
```

2. **准备配置文件**
```bash
# 创建配置目录
mkdir -p /etc/ytsaurus

# 复制示例配置
cp config/ytserver-master.yaml /etc/ytsaurus/
```

3. **启动服务**
```bash
# 前台启动（用于调试）
./yt/yt/server/all/ytserver-all --config /etc/ytsaurus/ytserver-master.yaml

# 后台启动
nohup ./yt/yt/server/all/ytserver-all --config /etc/ytsaurus/ytserver-master.yaml > /var/log/ytsaurus/master.log 2>&1 &
```

### 集群部署

#### 单节点部署
```yaml
# 适用于测试环境
master:
  primary_address: "localhost:9013"
  secondary_addresses: []
```

#### 多节点部署
```yaml
# 生产环境推荐配置
masters:
  - address: "master1.ytsaurus.local:9013"
    cell_id: "master-cell-1"
  - address: "master2.ytsaurus.local:9013"
    cell_id: "master-cell-1"
  - address: "master3.ytsaurus.local:9013"
    cell_id: "master-cell-1"
```

### 基本操作

#### 检查 Master 状态
```bash
# 通过 CLI 检查
yt get //sys/primary_master

# 通过 HTTP API
curl http://localhost:9014/orchid/sys/master
```

#### 查看集群信息
```bash
# 查看节点状态
yt get //sys/cluster_nodes

# 查看表信息
yt list //sys/tables

# 查看事务状态
yt get //sys/transactions
```

## 实现原理

### 分布式一致性

Master 使用基于 Raft 的分布式一致性算法：

1. **Leader 选举**
   - 所有 Master 节点参与选举
   - 获得多数票的节点成为 Leader
   - Leader 处理所有写请求

2. **日志复制**
   - 所有修改操作记录到 WAL
   - 日志条目复制到多数跟随者
   - 确认后应用到状态机

3. **快照机制**
   - 定期生成系统状态快照
   - 新节点通过快照快速同步
   - 压缩日志减少存储开销

### 事务处理机制

1. **两阶段提交**
   - 阶段一：准备阶段，锁定资源
   - 阶段二：提交阶段，确认提交或回滚

2. **MVCC 支持**
   - 多版本并发控制
   - 支持读快照和写隔离
   - 优化读性能

3. **锁机制**
   - 支持多种锁类型（共享锁、排他锁）
   - 死锁检测和自动解除
   - 锁升级和降级

### 元数据存储

1. **内存结构**
   - 热数据存储在内存中
   - 使用高效的数据结构（红黑树、哈希表）
   - 支持范围查询和点查询

2. **持久化**
   - WAL 记录所有操作
   - 定期快照保存完整状态
   - 支持增量快照

3. **索引机制**
   - 多种索引类型（B树、哈希索引）
   - 索引自动维护和优化
   - 支持复合索引

## 性能优化

### 内存优化

1. **对象池**
   - 重用对象减少内存分配
   - 预分配常用数据结构
   - 内存池管理

2. **压缩算法**
   - 使用 LZ4 压缩减少内存占用
   - 智能缓存热点数据
   - 内存使用监控和自动清理

3. **NUMA 优化**
   - 绑定内存到特定 NUMA 节点
   - 优化内存访问模式
   - 减少跨节点内存访问

### I/O 优化

1. **批量操作**
   - 批量提交操作提高吞吐量
   - 合并小操作减少 I/O
   - 异步写入提高性能

2. **缓存策略**
   - 多级缓存系统
   - LRU 替换算法
   - 预读取热点数据

3. **磁盘优化**
   - 使用 SSD 提高读写性能
   - 文件系统优化
   - I/O 调度优化

### 网络优化

1. **连接池**
   - 复用 TCP 连接
   - 连接池管理和监控
   - 自动重连机制

2. **压缩传输**
   - 网络数据压缩
   - 批量传输减少延迟
   - 协议优化

## 监控调试

### 关键监控指标

#### 性能指标
```bash
# 请求处理延迟
yt get //sys/primary_master/@request_latency

# 吞吐量
yt get //sys/primary_master/@request_rate

# 内存使用
yt get //sys/primary_master/@memory_usage

# CPU 使用率
yt get //sys/primary_master/@cpu_usage
```

#### 业务指标
```bash
# 事务数量
yt get //sys/primary_master/@transaction_count

# Cypress 节点数
yt get //sys/primary_master/@node_count

# Chunk 数量
yt get //sys/primary_master/@chunk_count

# 在线节点数
yt get //sys/primary_master/@online_node_count
```

### 调试工具

#### 1. Orchid 监控
```bash
# 访问 Master Orchid
curl http://localhost:9014/orchid

# 查看服务状态
curl http://localhost:9014/orchid/service

# 查看配置信息
curl http://localhost:9014/orchid/config
```

#### 2. 日志分析
```bash
# 查看 Master 日志
tail -f /var/log/ytsaurus/master.log

# 搜索错误日志
grep "ERROR" /var/log/ytsaurus/master.log

# 分析性能日志
grep "PERFORMANCE" /var/log/ytsaurus/master.log
```

#### 3. 状态检查
```bash
# 检查集群健康状态
yt get //sys/cluster_nodes/@health

# 检查事务状态
yt list //sys/transactions

# 检查锁状态
yt list //sys/locks
```

### 故障诊断

#### 常见问题及解决方案

1. **Master 无法启动**
   ```bash
   # 检查端口占用
   netstat -tlnp | grep 9013

   # 检查配置文件
   ytserver-all --config config.yaml --dry-run

   # 检查磁盘空间
   df -h /var/lib/ytsaurus
   ```

2. **性能下降**
   ```bash
   # 检查内存使用
   free -h

   # 检查 CPU 负载
   top -p $(pgrep ytserver)

   # 检查网络连接
   netstat -an | grep ESTABLISHED | wc -l
   ```

3. **集群分裂**
   ```bash
   # 检查网络连通性
   ping master2.ytsaurus.local

   # 检查时钟同步
   ntpq -p

   # 检查 Raft 状态
   yt get //sys/primary_master/@raft_state
   ```

## 故障处理

### 故障类型及处理

#### 1. Master 节点故障

**故障现象**：
- Master 节点无响应
- 客户端请求超时
- 集群状态异常

**处理步骤**：
```bash
# 1. 检查节点状态
systemctl status ytserver-master

# 2. 查看日志
journalctl -u ytserver-master -f

# 3. 重启服务
systemctl restart ytserver-master

# 4. 检查集群状态
yt get //sys/primary_master/@health
```

#### 2. 网络分区

**故障现象**：
- 节点间通信中断
- 集群分裂为多个分区
- 数据不一致

**处理步骤**：
```bash
# 1. 检查网络连通性
ping master2.ytsaurus.local

# 2. 检查防火墙规则
iptables -L -n

# 3. 恢复网络连接
# 根据具体网络问题进行修复

# 4. 等待集群自动恢复
watch yt get //sys/primary_master/@health
```

#### 3. 内存溢出

**故障现象**：
- Master 进程被杀死
- OOM 错误日志
- 服务不可用

**处理步骤**：
```bash
# 1. 增加内存限制
echo "vm.overcommit_memory = 1" >> /etc/sysctl.conf

# 2. 优化配置
# 调整缓存大小
# 减少批处理大小

# 3. 监控内存使用
watch -n 1 'ps aux | grep ytserver'
```

### 数据恢复

#### 1. 从快照恢复
```bash
# 1. 停止 Master 服务
systemctl stop ytserver-master

# 2. 备份当前数据
cp -r /var/lib/ytsaurus/master /var/lib/ytsaurus/master.backup

# 3. 恢复快照
cp snapshot_file /var/lib/ytsaurus/master/

# 4. 重启服务
systemctl start ytserver-master
```

#### 2. 集群重建
```bash
# 在极端情况下，需要重建集群
# 1. 停止所有节点
# 2. 清理数据目录
# 3. 从备份恢复
# 4. 重新启动集群
```

## 最佳实践

### 部署建议

#### 1. 硬件配置
- **CPU**：至少 16 核，推荐 32 核以上
- **内存**：至少 64GB，推荐 128GB 以上
- **存储**：使用 SSD，至少 1TB
- **网络**：万兆网卡，低延迟连接

#### 2. 网络配置
- 专用网络用于 Master 间通信
- 配置网络 QoS 保证带宽
- 使用多路径冗余连接
- 配置防火墙只允许必要端口

#### 3. 存储配置
- 使用 RAID 10 提高可靠性
- 配置日志和数据分离存储
- 定期备份重要数据
- 监控磁盘使用情况

### 运维建议

#### 1. 监控告警
```yaml
alerts:
  - name: "master_down"
    condition: "up == 0"
    severity: "critical"

  - name: "high_memory_usage"
    condition: "memory_usage > 0.9"
    severity: "warning"

  - name: "high_request_latency"
    condition: "request_latency > 1000ms"
    severity: "warning"
```

#### 2. 定期维护
- 定期更新系统补丁
- 监控磁盘空间并及时清理
- 定期备份配置和数据
- 测试故障恢复流程

#### 3. 性能调优
- 根据负载调整缓存大小
- 优化批处理参数
- 监控和调整线程池大小
- 定期分析性能瓶颈

### 安全建议

#### 1. 访问控制
- 配置防火墙规则
- 使用 TLS 加密通信
- 实施最小权限原则
- 定期轮换证书和密钥

#### 2. 审计日志
- 启用详细审计日志
- 定期分析异常操作
- 长期保存重要日志
- 配置日志告警

#### 3. 数据保护
- 定期备份重要数据
- 实施异地备份策略
- 测试数据恢复流程
- 加密敏感数据

## 相关文档

- [YTsaurus 架构概述](../../README.md)
- [Node 服务文档](../node/README_zh.md)
- [Scheduler 服务文档](../scheduler/README_zh.md)
- [Client 库文档](../../client/README_zh.md)
- [部署指南](../../../docs/deployment.md)
- [运维手册](../../../docs/operations.md)
- [故障排除指南](../../../docs/troubleshooting.md)