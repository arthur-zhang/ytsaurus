# 作业代理服务 (Job Proxy)

## 概述

Job Proxy 是 YTsaurus 分布式存储系统中的作业执行代理，负责在计算节点上管理和执行各种类型的用户作业。它作为 Scheduler 和 Executor 之间的桥梁，提供作业环境准备、资源管理、进度监控、结果收集等功能，确保作业在受控环境中安全高效地执行。

## 功能特性

### 核心功能
- **作业管理**: 启动、监控和控制作业生命周期
- **资源隔离**: 使用容器技术实现作业间的资源隔离
- **环境准备**: 设置作业执行环境和依赖项
- **进度监控**: 实时监控作业执行状态和资源使用
- **结果收集**: 收集作业输出和执行结果

### 高级特性
- **多类型作业**: 支持 Map、Reduce、Sort、Merge 等多种作业类型
- **容器化支持**: 集成 Porto 和 Docker 容器技术
- **性能监控**: 详细的资源使用统计和性能分析
- **故障处理**: 自动故障检测和恢复机制
- **分布式追踪**: 集成链路追踪系统

## 架构设计

### 组件架构
```
Job Proxy
├── Job Proxy Core (核心代理)
│   ├── Job Controller (作业控制器)
│   ├── Resource Manager (资源管理器)
│   └── State Manager (状态管理器)
├── Job Environment (作业环境)
│   ├── Container Manager (容器管理器)
│   ├── File System Manager (文件系统管理器)
│   └── Network Manager (网络管理器)
├── Job Types (作业类型)
│   ├── Map Job (映射作业)
│   ├── Reduce Job (规约作业)
│   ├── Sort Job (排序作业)
│   ├── Merge Job (合并作业)
│   └── User Job (用户作业)
├── Monitoring System (监控系统)
│   ├── Resource Monitor (资源监控器)
│   ├── Progress Tracker (进度跟踪器)
│   └── Performance Profiler (性能分析器)
└── Communication Layer (通信层)
    ├── Scheduler Client (调度器客户端)
    ├── Node Client (节点客户端)
    └── Exec Node Client (执行节点客户端)
```

### 关键组件说明

#### 1. Job Controller (作业控制器)
- 管理作业的启动、执行和终止
- 处理作业状态转换和事件
- 协调各个组件的协同工作

#### 2. Resource Manager (资源管理器)
- 管理 CPU、内存、磁盘等资源分配
- 实施资源限制和配额控制
- 监控资源使用情况

#### 3. Container Manager (容器管理器)
- 创建和管理作业容器环境
- 实现 namespace 隔离和资源限制
- 处理容器生命周期

#### 4. Job Types (作业类型)
- 实现不同类型作业的执行逻辑
- 提供统一的作业接口
- 支持自定义作业类型

## 支持的作业类型

### 1. Map Job (映射作业)
```cpp
// 映射作业处理单个数据块
class TMapJob : public IJob {
    void Run(const TJobRunContext& context) override {
        // 读取输入数据
        auto input = context.GetInputReader();
        // 处理数据
        auto output = context.GetOutputWriter();
        // 写入结果
    }
};
```

### 2. Reduce Job (规约作业)
```cpp
// 规约作业处理分组数据
class TReduceJob : public IJob {
    void Run(const TJobRunContext& context) override {
        // 按键分组处理
        for (const auto& group : context.GetInputGroups()) {
            ProcessGroup(group, context.GetOutputWriter());
        }
    }
};
```

### 3. Sort Job (排序作业)
- Simple Sort: 单阶段排序
- Partition Sort: 分区排序
- Sorted Merge: 有序合并

### 4. Merge Job (合并作业)
- Shallow Merge: 浅层合并
- Remote Copy: 远程复制合并

### 5. User Job (用户作业)
- 支持自定义作业逻辑
- 灵活的环境配置
- 完整的资源管理

## 配置说明

### 基本配置结构
```yaml
job_proxy:
  # 作业配置
  job:
    resource_limits:
      cpu_limit: 4                  # CPU 核心数
      memory_limit: 8GB             # 内存限制
      disk_limit: 100GB             # 磁盘空间限制
      network_limit: 1GB/s          # 网络带宽限制

    time_limits:
      prepare_time_limit: 300s      # 准备时间限制
    execute_time_limit: 3600s       # 执行时间限制
    cleanup_time_limit: 60s         # 清理时间限制

  # 容器配置
  container:
    runtime: "porto"                # 容器运行时 (porto/docker)
    enable_root_fs: false           # 是否启用根文件系统隔离
    extra_layers: []                # 额外的文件系统层

    environment:
      PATH: "/usr/bin:/bin"
      LD_LIBRARY_PATH: "/usr/lib"

    mounts:
      - type: bind
        source: "/tmp"
        destination: "/tmp"
        read_only: false

  # 网络配置
  network:
    enable_network: true
    network_namespace: "job_network"
    dns_servers: ["8.8.8.8", "8.8.4.4"]
```

### 监控配置
```yaml
job_proxy:
  monitoring:
    enable_resource_monitoring: true
    monitoring_interval: 1s
    enable_profiling: true
    profiling_output_path: "/tmp/job_profile"

    resource_limits_check_interval: 5s
    memory_watchdog_threshold: 0.9
    cpu_watchdog_threshold: 0.95
```

### 性能优化配置
```yaml
job_proxy:
  performance:
    io_buffer_size: 1MB
    network_io_thread_count: 2
    disk_io_thread_count: 4

    cache:
      enable_read_cache: true
      read_cache_size: 64MB
      enable_write_cache: true
      write_cache_size: 32MB
```

## 使用方法

### 作业执行流程
1. **作业分配**: Scheduler 分配作业到执行节点
2. **环境准备**: Job Proxy 准备作业执行环境
3. **资源分配**: 分配 CPU、内存等资源
4. **容器创建**: 创建隔离的执行容器
5. **作业执行**: 在容器中执行用户作业
6. **进度监控**: 监控作业执行状态和进度
7. **结果收集**: 收集作业输出和结果
8. **环境清理**: 清理临时文件和资源

### 资源监控
```bash
# 查看作业资源使用情况
curl http://job-proxy:8080/job/<job-id>/resources

# 查看作业统计信息
curl http://job-proxy:8080/job/<job-id>/statistics

# 实时监控作业进度
curl http://job-proxy:8080/job/<job-id>/progress
```

### 调试和诊断
```bash
# 查看作业日志
cat /var/log/ytsaurus/job_proxy_<job-id>.log

# 查看容器状态
portoctl list | grep <job-id>

# 进入作业容器调试
portoctl enter <container-id>
```

## 实现原理

### 作业生命周期
1. **初始化阶段**: 分配资源和创建环境
2. **准备阶段**: 下载输入数据和依赖
3. **执行阶段**: 运行用户作业代码
4. **清理阶段**: 清理临时数据和资源
5. **完成阶段**: 收集结果和更新状态

### 资源隔离机制
1. **CPU 隔离**: 使用 CFS 调度器和 CPU 配额
2. **内存隔离**: 使用内存限制和 OOM 保护
3. **IO 隔离**: 使用 blkio 限制磁盘 IO
4. **网络隔离**: 使用网络命名空间和流量控制

### 容器技术集成
1. **Porto 集成**: 原生容器管理支持
2. **Docker 支持**: 兼容 Docker 镜像格式
3. **文件系统**: 支持层叠文件系统
4. **网络管理**: 支持 overlay 网络模式

### 监控和追踪
1. **资源监控**: 实时监控 CPU、内存、IO 使用
2. **性能分析**: 提供详细的性能分析数据
3. **链路追踪**: 集成分布式追踪系统
4. **日志收集**: 统一的日志收集和分析

## 性能优化

### 资源利用优化
- 动态资源调整
- 资源超售控制
- 亲和性调度优化

### IO 性能优化
- 异步 IO 模式
- 缓存策略优化
- 并行 IO 处理

### 网络性能优化
- 连接复用
- 批量数据传输
- 压缩和流控制

## 监控和调试

### 关键指标
- 作业执行时间和成功率
- 资源利用率统计
- 错误类型和频率
- 容器启动时间
- 数据传输速度

### 监控端点
```bash
# 作业状态
GET /job/{job_id}/status

# 资源使用
GET /job/{job_id}/resources

# 进度信息
GET /job/{job_id}/progress

# 性能指标
GET /job/{job_id}/metrics
```

### 日志分析
```bash
# 启用详细日志
export YT_LOG_LEVEL=debug

# 查看作业代理日志
tail -f /var/log/ytsaurus/job_proxy.log

# 分析错误日志
grep "ERROR" /var/log/ytsaurus/job_proxy.log
```

## 故障排除

### 常见问题
1. **资源不足**: 检查资源限制和分配
2. **容器启动失败**: 检查容器配置和依赖
3. **网络连接问题**: 检查网络配置和防火墙
4. **权限错误**: 检查文件权限和用户权限

### 调试步骤
1. 检查作业配置和环境
2. 查看详细错误日志
3. 验证资源可用性
4. 测试容器运行环境
5. 检查网络连接

### 恢复策略
- 自动重试机制
- 故障转移处理
- 状态恢复和重建

## 安全考虑

### 容器安全
- 最小权限原则
- 安全镜像扫描
- 运行时安全监控

### 网络安全
- 网络隔离和访问控制
- 流量加密和认证
- DDoS 防护

### 数据安全
- 敏感数据加密
- 访问审计日志
- 数据生命周期管理

## 相关组件

- **Scheduler**: 作业调度器
- **Exec Node**: 执行节点服务
- **Node Service**: 节点管理服务
- **Master**: 集群主节点
- **Container Runtime**: 容器运行时

## 最佳实践

### 作业设计
- 合理设置资源限制
- 优化数据访问模式
- 实现容错和重试机制

### 性能调优
- 根据负载调整配置
- 监控性能瓶颈
- 持续优化改进

### 运维管理
- 建立监控告警机制
- 实施自动化运维
- 定期备份和测试

## 版本历史

- 初始版本支持基本作业执行
- 增加容器化支持和资源隔离
- 增强监控和调试功能
- 性能优化和稳定性改进
- 增加安全特性和故障恢复机制