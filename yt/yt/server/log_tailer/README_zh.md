# 日志跟踪服务 (Log Tailer)

## 概述

Log Tailer 是 YTsaurus 分布式存储系统中的日志收集和处理服务，负责实时监控、收集和转发各个组件产生的日志数据。它提供统一的日志聚合接口，支持日志轮转、过滤、压缩和转发等功能，是系统监控、调试和审计的核心组件。

## 功能特性

### 核心功能
- **实时日志收集**: 实时监控和读取日志文件变化
- **日志轮转管理**: 自动处理日志文件的轮转和归档
- **日志过滤和解析**: 支持基于模式的日志过滤和结构化解析
- **数据转发**: 将收集的日志数据转发到集中式存储或分析系统
- **健康检查**: 监控日志写入进程的活跃状态

### 高级特性
- **多源日志聚合**: 同时处理来自多个组件的日志流
- **缓冲和批处理**: 智能缓冲和批处理提高传输效率
- **压缩存储**: 支持日志数据的压缩存储和传输
- **错误处理**: 完善的错误检测和恢复机制
- **性能监控**: 提供详细的性能统计和监控指标

## 架构设计

### 组件架构
```
Log Tailer
├── Log Tailer Core (核心跟踪器)
│   ├── Periodic Executor (周期执行器)
│   ├── Log Readers (日志读取器)
│   └── Event Dispatcher (事件分发器)
├── Log Management (日志管理)
│   ├── Log Rotator (日志轮转器)
│   ├── File Monitor (文件监控器)
│   └── Path Manager (路径管理器)
├── Processing Pipeline (处理流水线)
│   ├── Log Parser (日志解析器)
│   ├── Filter Engine (过滤引擎)
│   ├── Format Converter (格式转换器)
│   └── Data Enricher (数据增强器)
├── Output Layer (输出层)
│   ├── Buffer Manager (缓冲管理器)
│   ├── Batching Engine (批处理引擎)
│   ├── Compression Handler (压缩处理器)
│   └── Forwarding Service (转发服务)
└── Monitoring System (监控系统)
    ├── Performance Monitor (性能监控器)
    ├── Health Checker (健康检查器)
    └── Statistics Collector (统计收集器)
```

### 关键组件说明

#### 1. Log Readers (日志读取器)
- 监控多个日志文件的变化
- 支持不同格式的日志文件读取
- 处理文件轮转和重命名事件
- 维护读取位置和偏移量

#### 2. Log Rotator (日志轮转器)
- 监控日志文件大小和创建时间
- 执行日志文件轮转操作
- 管理归档日志的生命周期
- 清理过期的日志文件

#### 3. Log Writer Liveness Checker (日志写入器活性检查器)
- 监控日志写入进程的状态
- 检测日志写入中断或异常
- 触发告警和故障恢复
- 维护写入进程的健康状态

#### 4. Processing Pipeline (处理流水线)
- 解析和结构化日志数据
- 应用过滤规则和转换逻辑
- 增强日志数据（添加元数据）
- 格式标准化和验证

## 配置说明

### 基本配置结构
```yaml
log_tailer:
  # 基本设置
  check_interval: 1s                # 检查间隔时间
  read_buffer_size: 64KB            # 读取缓冲区大小
  max_line_length: 1MB              # 最大单行长度

  # 日志源配置
  log_sources:
    - path: "/var/log/ytsaurus/master.log"
      pattern: "*.log"
      follow_mode: tail             # 跟踪模式: tail/scan
      encoding: "utf-8"
      log_format: "json"            # 日志格式: json/text/yson

    - path: "/var/log/ytsaurus/node"
      pattern: "*.log"
      recursive: true
      exclude_patterns: ["*.tmp", "*.bak"]

  # 日志轮转配置
  rotation:
    enabled: true
    max_file_size: 100MB            # 最大文件大小
    max_files: 10                   # 最大保留文件数
    compress_rotated: true          # 压缩轮转文件
    retention_period: 7d            # 保留时间

  # 输出配置
  output:
    type: "file"                    # 输出类型: file/kafka/elasticsearch
    destination: "/var/log/aggregated"
    compression: "gzip"             # 压缩格式
    batch_size: 1000                # 批处理大小
    flush_interval: 5s              # 刷新间隔
```

### 高级配置
```yaml
log_tailer:
  # 过滤配置
  filters:
    - name: "level_filter"
      type: "regex"
      pattern: "ERROR|WARN"
      action: "include"

    - name: "exclude_debug"
      type: "level"
      levels: ["DEBUG"]
      action: "exclude"

  # 解析配置
  parsing:
    timestamp_format: "%Y-%m-%d %H:%M:%S"
    field_separator: "\t"
    extract_fields:
      - name: "timestamp"
        pattern: "^(\\d{4}-\\d{2}-\\d{2} \\d{2}:\\d{2}:\\d{2})"
      - name: "level"
        pattern: "\\[(TRACE|DEBUG|INFO|WARN|ERROR|FATAL)\\]"
      - name: "message"
        pattern: "\\] (.*)$"

  # 健康检查配置
  health_check:
    enabled: true
    check_interval: 30s
    max_inactive_time: 300s         # 最大非活跃时间
    restart_dead_writers: true      # 重启死掉的写入器

  # 性能配置
  performance:
    max_readers: 50                 # 最大读取器数量
    read_timeout: 5s                # 读取超时时间
    io_thread_count: 4              # IO 线程数
    processing_queue_size: 10000    # 处理队列大小
```

## 使用方法

### 启动服务
```bash
# 从构建目录启动
./yt/yt/server/all/ytserver-all --config log_tailer.config.yson

# 或使用特定配置
./ytserver-log-tailer --config config.yson
```

### 配置文件示例
```yaml
# log_tailer.yson
{
  check_interval = 1000;            # 1秒
  read_buffer_size = 65536;         # 64KB

  log_sources = [
    {
      path = "/var/log/ytsaurus";
      pattern = "*.log";
      follow_mode = "tail";
      encoding = "utf-8";
    }
  ];

  rotation = {
    enabled = true;
    max_file_size = 104857600;      # 100MB
    max_files = 10;
    compress_rotated = true;
  };

  output = {
    type = "file";
    destination = "/var/log/collected";
    batch_size = 1000;
    flush_interval = 5000;          # 5秒
  };
}
```

### 监控和控制
```bash
# 查看服务状态
curl http://log-tailer:8080/status

# 获取统计信息
curl http://log-tailer:8080/statistics

# 重新加载配置
curl -X POST http://log-tailer:8080/reload_config

# 查看活跃的日志读取器
curl http://log-tailer:8080/readers
```

### 日志验证
```bash
# 验证日志文件是否被正确读取
tail -f /var/log/ytsaurus/master.log | grep "Log Tailer"

# 检查轮转日志
ls -la /var/log/ytsaurus/*.log.*

# 验证输出格式
head -n 5 /var/log/collected/aggregated.log
```

## 实现原理

### 日志跟踪机制
1. **文件监控**: 使用 inotify 或轮询机制监控文件变化
2. **增量读取**: 只读取新增的日志内容，避免重复处理
3. **位置管理**: 维护每个文件的读取位置和偏移量
4. **事件处理**: 处理文件创建、删除、轮转等事件

### 日志轮转处理
1. **大小检测**: 定期检查日志文件大小
2. **重命名操作**: 安全地重命名当前日志文件
3. **新文件创建**: 创建新的日志文件继续写入
4. **旧文件压缩**: 压缩和归档旧日志文件

### 健康检查机制
1. **活跃度监控**: 监控日志文件的最后修改时间
2. **写入检测**: 检测日志写入进程是否正常工作
3. **异常恢复**: 自动重启异常的日志写入进程
4. **告警通知**: 发送健康状态告警

### 性能优化
1. **异步IO**: 使用异步IO提高读取性能
2. **缓冲机制**: 智能缓冲减少IO操作
3. **批量处理**: 批量处理提高传输效率
4. **内存管理**: 优化内存使用和垃圾回收

## 监控和调试

### 关键指标
- 日志读取速度和字节数
- 处理延迟和队列长度
- 错误率和重试次数
- 内存和CPU使用情况
- 文件监控状态

### 监控端点
```bash
# 服务健康状态
curl http://log-tailer:8080/health

# 详细的性能指标
curl http://log-tailer:8080/metrics

# 配置信息
curl http://log-tailer:8080/config
```

### 日志配置
```yaml
logging:
  level: info
  log_file: "/var/log/log_tailer.log"
  log_rotation: true
  max_log_size: 100MB
  max_log_files: 5

  # 组件级别日志
  components:
    log_reader: debug
    file_monitor: info
    rotation: warn
```

### 调试工具
```bash
# 启用调试模式
export LOG_TAILER_DEBUG=true

# 查看文件监控事件
inotifywatch -v /var/log/ytsaurus/

# 分析日志文件
tail -f /var/log/log_tailer.log | grep "ERROR"

# 性能分析
strace -p <pid> -e trace=read,write
```

## 性能优化

### 读取性能优化
- 使用内存映射文件
- 调整缓冲区大小
- 优化文件监控策略
- 实施预读机制

### 处理性能优化
- 多线程并行处理
- 批量数据处理
- 智能缓存策略
- 异步事件处理

### 网络传输优化
- 数据压缩传输
- 批量网络发送
- 连接复用
- 断线重连机制

## 故障排除

### 常见问题
1. **日志文件未检测**: 检查文件权限和监控配置
2. **读取性能差**: 优化缓冲区大小和IO策略
3. **内存泄漏**: 检查文件句柄和内存管理
4. **配置错误**: 验证配置文件语法和逻辑

### 调试步骤
1. 检查服务启动日志
2. 验证文件路径和权限
3. 测试日志文件访问
4. 分析性能瓶颈
5. 检查网络连接状态

### 恢复策略
- 自动重启机制
- 状态恢复和重连
- 数据完整性验证
- 告警和通知系统

## 安全考虑

### 访问控制
- 限制日志文件访问权限
- 实施网络安全隔离
- 控制管理接口访问
- 审计日志访问行为

### 数据保护
- 敏感信息脱敏
- 传输加密保护
- 安全存储管理
- 数据备份策略

## 相关组件

- **Master Services**: 主节点服务日志
- **Node Services**: 节点服务日志
- **Job Proxy**: 作业代理日志
- **HTTP Proxy**: HTTP代理日志
- **Monitoring System**: 监控和告警系统

## 最佳实践

### 部署建议
- 分布式部署减少网络延迟
- 合理配置资源限制
- 启用高可用模式
- 实施负载均衡

### 运维管理
- 定期监控性能指标
- 建立告警机制
- 实施自动化运维
- 制定应急响应预案

### 数据管理
- 制定数据保留策略
- 实施分层存储
- 优化查询性能
- 确保数据一致性

## 版本历史

- 初始版本支持基本日志收集
- 增加日志轮转和过滤功能
- 增强性能和稳定性
- 增加监控和调试功能
- 优化资源使用和错误处理