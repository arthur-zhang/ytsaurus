# YTsaurus Node 服务

## 概述

YTsaurus Node 是集群的数据存储和计算执行节点，负责处理实际的数据读写操作和作业执行任务。Node 服务作为 YTsaurus 集群的工作节点，承担着数据存储、计算执行、资源管理等多重职责，是集群中最重要的执行单元。

Node 服务采用模块化设计，包含数据节点（Data Node）、执行节点（Exec Node）、Tablet 节点（Tablet Node）等多个功能模块，可以根据需要灵活部署不同的服务组合。

## 核心功能

### 1. 数据存储 (Data Node)

#### Chunk 管理
- **Chunk 存储**：负责数据块的存储和管理，支持多种存储介质
- **数据读写**：高效的数据读写服务，支持并发访问
- **副本管理**：维护数据副本的一致性和可用性
- **存储优化**：自动的数据压缩和存储空间优化

#### 存储介质支持
- **SSD 存储**：高速 SSD 用于热数据存储
- **HDD 存储**：大容量 HDD 用于冷数据存储
- **内存缓存**：内存中缓存热点数据
- **分层存储**：自动数据分层和迁移

#### 数据完整性
- **校验机制**：数据完整性校验和自动修复
- **数据压缩**：支持多种压缩算法
- **垃圾回收**：自动清理过期和无效数据
- **存储平衡**：智能的数据分布和负载均衡

### 2. 作业执行 (Exec Node)

#### 作业环境管理
- **沙箱环境**：隔离的作业执行环境
- **资源限制**：CPU、内存、磁盘等资源限制
- **作业调度**：与 Scheduler 协调的作业调度
- **生命周期管理**：作业的创建、监控和清理

#### 资源管理
- **CPU 管理**：CPU 核心分配和调度
- **内存管理**：内存分配和回收
- **磁盘管理**：临时磁盘空间管理
- **网络管理**：网络带宽控制和优化

#### 作业支持
- **MapReduce**：MapReduce 作业执行
- **用户作业**：自定义用户程序执行
- **容器化作业**：Docker 容器支持
- **GPU 作业**：GPU 资源管理和调度

### 3. Tablet 服务 (Tablet Node)

#### Tablet 管理
- **Tablet 存储服务**：作为 Tablet 的存储节点
- **Leader 选举**：参与 Tablet Leader 选举
- **数据同步**：与其他 Tablet 节点同步数据
- **负载均衡**：支持 Tablet 的动态迁移

#### 数据一致性
- **WAL 管理**：预写日志管理确保持久性
- **快照机制**：定期生成数据快照
- **副本同步**：多副本数据同步
- **一致性协议**：基于 Raft 的一致性保证

#### 性能优化
- **内存管理**：高效的内存使用和管理
- **缓存机制**：多级缓存系统
- **压缩存储**：数据压缩减少存储开销
- **批处理优化**：批量操作提高性能

### 4. 代理服务 (Job Proxy)

#### 作业代理
- **作业通信**：作为作业与集群间的通信代理
- **状态报告**：实时报告作业执行状态
- **资源监控**：监控作业资源使用情况
- **异常处理**：处理作业执行异常

## 架构设计

### 核心组件

#### 1. Data Node 模块
```
data_node/
├── chunk_store.cpp           # Chunk 存储管理
├── session_manager.cpp       # 会话管理
├── location_manager.cpp      # 存储位置管理
├── chunk_location.cpp        # Chunk 位置管理
└── master_connector.cpp      # Master 连接器
```

#### 2. Exec Node 模块
```
exec_node/
├── slot_manager.cpp          # 槽位管理
├── job_controller.cpp        # 作业控制器
├── volume_manager.cpp        # 卷管理器
├── gpu_manager.cpp           # GPU 管理器
└── scheduler_connector.cpp   # Scheduler 连接器
```

#### 3. Tablet Node 模块
```
tablet_node/
├── tablet_manager.cpp        # Tablet 管理器
├── tablet_cell.cpp           # Tablet Cell
├── tablet_service.cpp        # Tablet 服务
└── hybrid_manager.cpp        # 混合管理器
```

#### 4. 公共组件
```
cellar_node/
├── cellar_manager.cpp        # Cellar 管理器
├── hydra_facade.cpp          # Hydra 门面
└── automaton.cpp             # 自动机实现
```

### 数据流架构

#### 1. 数据写入流程
```
Client → RPC Proxy → Master → Node
        ↓
    1. 请求写入权限
        ↓
    2. 分配 Session
        ↓
    3. 写入数据到 Chunk
        ↓
    4. 确认写入完成
        ↓
    5. 更新元数据
```

#### 2. 数据读取流程
```
Client → RPC Proxy → Master → Node
        ↓
    1. 查询数据位置
        ↓
    2. 定位存储节点
        ↓
    3. 读取数据块
        ↓
    4. 返回数据给客户端
```

#### 3. 作业执行流程
```
Scheduler → Node → Job Environment
     ↓          ↓         ↓
  1. 分配作业  2. 创建环境 3. 执行作业
     ↓          ↓         ↓
  4. 监控状态  5. 资源管理 6. 结果收集
     ↓          ↓         ↓
  8. 作业完成  7. 清理资源
```

## 配置说明

### 主配置文件结构

#### 基础配置
```yaml
node:
  # 节点标识
  node_id: "node-001"

  # 监听地址
  rpc_port: 9012
  monitoring_port: 9013
  http_port: 9014

  # 数据存储路径
  data_path: "/var/lib/ytsaurus/node"

  # 日志配置
  log_level: "info"
  log_path: "/var/log/ytsaurus/node.log"
```

#### Data Node 配置
```yaml
data_node:
  # 存储位置配置
  storage_locations:
    - path: "/mnt/disk1/chunk_data"
      medium_type: "ssd"
      max_available_space: "100GB"
    - path: "/mnt/disk2/chunk_data"
      medium_type: "hdd"
      max_available_space: "1TB"

  # 会话管理
  session_manager:
    max_concurrent_sessions: 10000
    session_timeout: 300000
    chunk_upload_timeout: 60000

  # 块存储配置
  block_cache:
    max_size: "8GB"
    max_part_size: "64MB"
    compressed_block_cache_size: "2GB"

  # P2P 配置
  p2p:
    enabled: true
    max_incoming_connections: 100
    block_cache_size: "4GB"
```

#### Exec Node 配置
```yaml
exec_node:
  # 槽位管理
  slot_manager:
    slot_count: 32
    job_environment_type: "simple"
    enable_tmpfs: true
    tmpfs_size: "2GB"

  # GPU 配置
  gpu_manager:
    enabled: true
    gpu_count: 4
    gpu_memory_factor: 1.0

  # 卷管理
  volume_manager:
    enable_squashfs: true
    enable_nbd: true
    cache_location_path: "/tmp/volume_cache"

  # 作业控制器
  job_controller:
    max_concurrent_jobs: 100
    job_proxy_timeout: 300000
    enable_job_interception: false
```

#### Tablet Node 配置
```yaml
tablet_node:
  # Tablet 管理
  tablet_manager:
    max_tablet_count: 1000
    tablet_cell_count: 10

  # 混合管理器
  hybrid_manager:
    enable_leader_reassignment: true
    leader_reassignment_timeout: 60000

  # 压缩配置
  compression_codec:
    default_codec: "lz4"
    heavy_codec: "zstd_5"

  # 存储配置
  store_manager:
    max_dynamic_store_count: 100
    store_rotation_threshold: 1000
```

### 动态配置

Node 支持运行时配置更新：

```yaml
dynamic_config:
  # 配置更新间隔
  update_period: 5000

  # 动态配置路径
  config_path: "//sys/cluster_nodes/{node_id}/config"
```

## 使用方法

### 编译和安装

1. **编译 Node 服务**
```bash
# 构建完整服务
ninja ytserver-all

# 或单独构建
ninja ytserver-node
```

2. **安装依赖**
```bash
# Ubuntu/Debian
sudo apt-get install -y libsnappy-dev liblz4-dev libzstd-dev

# CentOS/RHEL
sudo yum install -y snappy-devel lz4-devel zstd-devel
```

3. **配置环境**
```bash
# 创建数据目录
sudo mkdir -p /var/lib/ytsaurus/node
sudo chown ytsaurus:ytsaurus /var/lib/ytsaurus/node

# 创建日志目录
sudo mkdir -p /var/log/ytsaurus
sudo chown ytsaurus:ytsaurus /var/log/ytsaurus
```

### 服务启动

#### 单服务启动
```bash
# 启动完整 Node 服务
./yt/yt/server/all/ytserver-all \
  --config /etc/ytsaurus/ytserver-node.yaml \
  --node-id node-001

# 指定角色启动
./yt/yt/server/all/ytserver-all \
  --config /etc/ytsaurus/ytserver-node.yaml \
  --node-id node-001 \
  --roles data_node,exec_node
```

#### 系统服务配置
```ini
# /etc/systemd/system/ytserver-node.service
[Unit]
Description=YTsaurus Node Service
After=network.target

[Service]
Type=simple
User=ytsaurus
Group=ytsaurus
ExecStart=/usr/local/bin/ytserver-all \
  --config /etc/ytsaurus/ytserver-node.yaml \
  --node-id node-001
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

```bash
# 启用并启动服务
sudo systemctl enable ytserver-node
sudo systemctl start ytserver-node
```

### 集群注册

1. **注册节点到集群**
```bash
# 通过 CLI 注册
yt create map_node //sys/cluster_nodes/node-001
yt set //sys/cluster_nodes/node-001/@host "node-001.ytsaurus.local"
yt set //sys/cluster_nodes/node-001/@rpc_port 9012
yt set //sys/cluster_nodes/node-001/@data_node/http_port 9013
yt set //sys/cluster_nodes/node-001/@exec_node/http_port 9014
```

2. **配置存储介质**
```bash
# 添加存储位置
yt set //sys/cluster_nodes/node-001/@locations \
  '[{"path": "/mnt/disk1", "medium_type": "ssd"}, \
    {"path": "/mnt/disk2", "medium_type": "hdd"}]'
```

3. **验证节点状态**
```bash
# 检查节点状态
yt get //sys/cluster_nodes/node-001/@state

# 查看节点指标
yt get //sys/cluster_nodes/node-001/@statistics
```

## 实现原理

### 数据存储机制

#### 1. Chunk 存储架构
- **Chunk 分割**：数据被分割为固定大小的 Chunk（通常 64MB-256MB）
- **多副本存储**：每个 Chunk 有多个副本存储在不同节点
- **位置信息**：Master 维护 Chunk 到节点的映射关系
- **动态迁移**：支持 Chunk 在节点间的动态迁移

#### 2. 数据完整性保证
- **校验和**：每个数据块都有校验和保证完整性
- **版本控制**：支持数据的版本管理和回滚
- **事务写入**：支持事务性的数据写入
- **自动修复**：检测到数据损坏时自动从副本修复

#### 3. 缓存机制
- **多级缓存**：内存缓存 + 磁盘缓存的多级架构
- **LRU 策略**：使用 LRU 算法管理缓存
- **预读取**：智能预读取热点数据
- **压缩缓存**：缓存压缩数据提高效率

### 作业执行机制

#### 1. 沙箱环境
```cpp
class TUserSandboxOptions {
    std::vector<TTmpfsVolumeParams> TmpfsVolumes;  // 临时文件系统
    std::optional<i64> InodeLimit;                 // inode 限制
    std::optional<i64> DiskSpaceLimit;             // 磁盘空间限制
    int UserId;                                    // 用户 ID
    // ...
};
```

#### 2. 资源隔离
- **CPU 隔离**：使用 cgroups 限制 CPU 使用
- **内存隔离**：限制内存使用和交换空间
- **I/O 隔离**：限制磁盘 I/O 带宽
- **网络隔离**：控制网络访问和带宽

#### 3. 生命周期管理
```cpp
enum class EAllocationState {
    Waiting,     // 等待资源
    Running,     // 正在运行
    Finished,    // 已完成
    Failed,      // 执行失败
    Aborted,     // 被中止
};
```

### Tablet 服务机制

#### 1. 数据模型
- **Tablet Cell**：一组 Tablet 的逻辑集合
- **Leader-Follower**：每个 Tablet 有一个 Leader 和多个 Follower
- **Raft 协议**：基于 Raft 算法保证一致性
- **分片机制**：大数据表自动分片为多个 Tablet

#### 2. 写入流程
```
Client → Tablet Leader → Followers → Ack
   ↓         ↓              ↓
 1.写请求  2.复制日志     3.确认提交
   ↓         ↓              ↓
 8.响应   4.提交日志     5.应用状态机
           ↓              ↓
         7.释放锁       6.持久化
```

#### 3. 读取优化
- **本地读取**：优先从本地读取数据
- **缓存加速**：使用内存缓存提高读取速度
- **并行读取**：支持多线程并行读取
- **智能预取**：预测性数据预取

## 性能优化

### 存储优化

#### 1. 磁盘优化
```yaml
storage_optimization:
  # 使用多个磁盘并行 I/O
  enable_multiple_disks: true

  # SSD 优化
  ssd_optimization:
    enable_trim: true
    alignment: 4K

  # HDD 优化
  hdd_optimization:
    enable_read_ahead: true
    read_ahead_size: "1MB"
```

#### 2. 内存优化
```yaml
memory_optimization:
  # 块缓存配置
  block_cache:
    max_size: "8GB"
    max_part_size: "64MB"

  # 压缩缓存
  compressed_cache:
    max_size: "2GB"

  # 元数据缓存
  metadata_cache:
    max_size: "1GB"
```

#### 3. 网络优化
```yaml
network_optimization:
  # TCP 优化
  tcp_optimization:
    enable_tcp_nodelay: true
    socket_buffer_size: "1MB"

  # 批量传输
  batch_transfer:
    max_batch_size: 100
    batch_timeout: "10ms"
```

### 计算优化

#### 1. CPU 优化
```yaml
cpu_optimization:
  # CPU 绑定
  enable_cpu_affinity: true

  # 线程池配置
  thread_pool_size: 16

  # NUMA 优化
  enable_numa_optimization: true
```

#### 2. 作业调度优化
```yaml
job_optimization:
  # 槽位配置
  slot_count: 32

  # 预分配槽位
  enable_slot_preallocation: true

  # 作业抢占
  enable_job_preemption: true
```

## 监控调试

### 关键监控指标

#### Node 状态指标
```bash
# 节点状态
yt get //sys/cluster_nodes/node-001/@state

# 在线状态
yt get //sys/cluster_nodes/node-001/@online

# 最后心跳时间
yt get //sys/cluster_nodes/node-001/@last_seen_time
```

#### Data Node 指标
```bash
# 存储使用情况
yt get //sys/cluster_nodes/node-001/@statistics/disk_space

# Chunk 数量
yt get //sys/cluster_nodes/node-001/@statistics/chunk_count

# 读取性能
yt get //sys/cluster_nodes/node-001/@statistics/read_rate

# 写入性能
yt get //sys/cluster_nodes/node-001/@statistics/write_rate
```

#### Exec Node 指标
```bash
# 运行作业数
yt get //sys/cluster_nodes/node-001/@statistics/running_job_count

# 资源使用
yt get //sys/cluster_nodes/node-001/@statistics/resource_usage

# 槽位利用率
yt get //sys/cluster_nodes/node-001/@statistics/slot_utilization
```

#### Tablet Node 指标
```bash
# Tablet 数量
yt get //sys/cluster_nodes/node-001/@statistics/tablet_count

# Leader 数量
yt get //sys/cluster_nodes/node-001/@statistics/leader_tablet_count

# 写入延迟
yt get //sys/cluster_nodes/node-001/@statistics/write_latency
```

### 调试工具

#### 1. Orchid 监控
```bash
# 访问 Node Orchid
curl http://localhost:9013/orchid

# 查看数据节点状态
curl http://localhost:9013/orchid/data_node

# 查看执行节点状态
curl http://localhost:9013/orchid/exec_node

# 查看 tablet 节点状态
curl http://localhost:9013/orchid/tablet_node
```

#### 2. 性能分析
```bash
# CPU 使用情况
top -p $(pgrep ytserver)

# 内存使用情况
cat /proc/$(pgrep ytserver)/status

# 网络连接
netstat -an | grep $(pgrep ytserver)

# 磁盘 I/O
iostat -x 1
```

#### 3. 日志分析
```bash
# 查看实时日志
tail -f /var/log/ytsaurus/node.log

# 搜索错误
grep "ERROR" /var/log/ytsaurus/node.log

# 性能日志
grep "PERFORMANCE" /var/log/ytsaurus/node.log

# 作业日志
grep "JOB" /var/log/ytsaurus/node.log
```

## 故障处理

### 常见故障及解决方案

#### 1. 磁盘空间不足
```bash
# 现象：写入失败，磁盘空间告警
# 解决方案：

# 1. 清理临时文件
find /tmp -type f -mtime +7 -delete

# 2. 清理日志文件
logrotate -f /etc/logrotate.d/ytsaurus

# 3. 移动数据到其他磁盘
# yt move-chunk <chunk_id> <target_node>

# 4. 扩展存储空间
# 添加新的存储位置到配置文件
```

#### 2. 内存不足
```bash
# 现象：进程被杀死，OOM 错误
# 解决方案：

# 1. 调整缓存大小
# 修改配置文件中的 cache_size 参数

# 2. 增加交换空间
fallocate -l 8G /swapfile
chmod 600 /swapfile
mkswap /swapfile
swapon /swapfile

# 3. 优化内存使用
# 调整批处理大小和并发数
```

#### 3. 网络连接问题
```bash
# 现象：无法连接到 Master 或其他节点
# 解决方案：

# 1. 检查网络连通性
ping master.ytsaurus.local

# 2. 检查防火墙
iptables -L -n

# 3. 检查端口监听
netstat -tlnp | grep 9012

# 4. 重启网络服务
systemctl restart network
```

#### 4. 作业执行失败
```bash
# 现象：作业频繁失败或超时
# 解决方案：

# 1. 检查资源限制
df -h
free -h

# 2. 检查作业日志
find /var/lib/ytsaurus/jobs -name "*.log" -exec tail {} \;

# 3. 调整槽位配置
# 增加 slot_count 或调整 slot_size

# 4. 重启作业控制器
# 通过 Orchid 重启相关组件
```

### 数据恢复

#### 1. Chunk 数据恢复
```bash
# 如果检测到 Chunk 损坏，系统会自动从副本恢复
# 也可以手动触发恢复：

yt repair-chunk <chunk_id> --replica-count 3
```

#### 2. Tablet 数据恢复
```bash
# Tablet 数据损坏时的恢复流程：

# 1. 停止 Tablet 服务
yt set //sys/tablet_cells/<cell_id>/@health "banned"

# 2. 从快照恢复
yt restore-tablet --cell-id <cell_id> --snapshot-id <snapshot_id>

# 3. 重新启动服务
yt set //sys/tablet_cells/<cell_id>/@health "good"
```

## 最佳实践

### 部署建议

#### 1. 硬件配置
- **CPU**：至少 8 核，推荐 16 核以上
- **内存**：至少 32GB，推荐 64GB 以上
- **存储**：SSD + HDD 混合存储
- **网络**：千兆网卡，推荐万兆

#### 2. 存储配置
```yaml
# 推荐存储配置
storage_locations:
  # 热数据使用 SSD
  - path: "/fast/ssd1"
    medium_type: "ssd"
    max_available_space: "200GB"

  # 温数据使用高速 HDD
  - path: "/medium/hdd1"
    medium_type: "hdd"
    max_available_space: "2TB"

  # 冷数据使用大容量 HDD
  - path: "/slow/hdd2"
    medium_type: "hdd"
    max_available_space: "4TB"
```

#### 3. 网络配置
```yaml
# 网络优化配置
network:
  # 绑定到特定网络接口
  bind_address: "10.0.1.100"

  # 启用 TCP_NODELAY
  enable_tcp_nodelay: true

  # 设置发送缓冲区
  send_buffer_size: "16MB"

  # 设置接收缓冲区
  receive_buffer_size: "16MB"
```

### 运维建议

#### 1. 监控配置
```yaml
monitoring:
  # 启用性能监控
  enable_profiling: true

  # 监控指标收集间隔
  metrics_collection_interval: 1000

  # 健康检查间隔
  health_check_interval: 5000
```

#### 2. 日志配置
```yaml
logging:
  # 日志级别
  level: "info"

  # 日志轮转
  rotation_policy:
    max_size: "100MB"
    max_files: 10

  # 结构化日志
  enable_structured_logging: true
```

#### 3. 安全配置
```yaml
security:
  # 启用 TLS
  enable_tls: true

  # 证书配置
  certificate_path: "/etc/ytsaurus/certs/node.crt"
  private_key_path: "/etc/ytsaurus/certs/node.key"

  # 访问控制
  enable_authentication: true
```

### 性能调优

#### 1. 批处理优化
```yaml
batch_optimization:
  # 读取批处理
  read_batch_size: 1000
  read_batch_timeout: "10ms"

  # 写入批处理
  write_batch_size: 100
  write_batch_timeout: "5ms"
```

#### 2. 并发控制
```yaml
concurrency:
  # 最大并发连接数
  max_concurrent_connections: 10000

  # 最大并发会话数
  max_concurrent_sessions: 5000

  # 最大并发作业数
  max_concurrent_jobs: 100
```

#### 3. 缓存优化
```yaml
cache:
  # 块缓存
  block_cache:
    max_size: "8GB"
    max_part_size: "64MB"

  # 元数据缓存
  metadata_cache:
    max_size: "2GB"

  # 压缩缓存
  compressed_cache:
    max_size: "4GB"
```

## 相关文档

- [YTsaurus 架构概述](../../README.md)
- [Master 服务文档](../master/README_zh.md)
- [Scheduler 服务文档](../scheduler/README_zh.md)
- [存储引擎设计](../../../docs/storage.md)
- [作业调度系统](../../../docs/scheduler.md)
- [集群部署指南](../../../docs/deployment.md)
- [性能调优手册](../../../docs/performance.md)