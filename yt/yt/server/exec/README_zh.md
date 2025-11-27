# 执行器服务 (Executor Service)

## 概述

Executor Service 是 YTsaurus 分布式存储系统中的用户作业执行器，负责在计算节点上安全地执行用户程序和作业。它作为 Job Proxy 的客户端组件，提供进程隔离、资源限制、标准输入输出管理和作业同步等功能，确保用户作业在受控环境中安全运行。

## 功能特性

### 核心功能
- **作业执行**: 启动和管理用户作业进程
- **进程隔离**: 提供安全的进程隔离和沙箱环境
- **资源限制**: 实施 CPU、内存、文件描述符等资源限制
- **IO 管理**: 处理用户作业的标准输入、输出和错误流
- **作业同步**: 与 Job Proxy 协调作业生命周期管理

### 高级特性
- **安全执行**: 限制用户作业的系统访问权限
- **资源监控**: 实时监控作业资源使用情况
- **优雅终止**: 支持作业的正常和异常终止处理
- **错误处理**: 完善的错误检测和报告机制
- **日志管理**: 统一的日志收集和管理

## 架构设计

### 组件架构
```
Executor Service
├── Program Entry (程序入口)
├── Job Synchronizer (作业同步器)
│   ├── Synchronizer Client (同步器客户端)
│   └── Communication Channel (通信通道)
├── Process Manager (进程管理器)
│   ├── Process Creation (进程创建)
│   ├── Resource Limits (资源限制)
│   └── Signal Handling (信号处理)
├── IO Manager (IO 管理器)
│   ├── Stdin/Stdout/Stderr (标准IO)
│   ├── Pipe Management (管道管理)
│   └── Buffer Control (缓冲控制)
└── Error Handler (错误处理器)
    ├── Exit Code Mapping (退出码映射)
    └── Error Reporting (错误报告)
```

### 关键组件说明

#### 1. Job Synchronizer (作业同步器)
- 与 Job Proxy 建立通信连接
- 同步作业准备和执行状态
- 接收控制指令和更新作业状态

#### 2. Process Manager (进程管理器)
- 创建和配置用户作业进程
- 设置进程属性和环境变量
- 管理进程生命周期和资源限制

#### 3. IO Manager (IO 管理器)
- 处理标准输入输出流的重定向
- 管理管道连接和数据传输
- 缓冲控制和流控制

#### 4. Error Handler (错误处理器)
- 捕获和处理各种执行错误
- 映射系统错误到标准退出码
- 生成详细的错误报告

## 配置说明

### 基本配置结构
```yaml
executor:
  # 作业标识
  job_id: "job-12345"

  # 执行器配置
  executor:
    # 资源限制
    resource_limits:
      cpu_limit: 4                  # CPU 核心数
      memory_limit: 8GB             # 内存限制
      max_open_files: 1024          # 最大文件描述符数
      max_user_processes: 100       # 最大进程数

    # 时间限制
    time_limit:
      cpu_time: 3600s              # CPU 时间限制
      wall_time: 7200s             # 实际时间限制

    # 工作目录
    working_directory: "/tmp/job_work_dir"

    # 环境变量
    environment:
      - "PATH=/usr/bin:/bin"
      - "HOME=/tmp/job_home"
      - "TMPDIR=/tmp/job_tmp"

  # 同步器连接配置
  synchronizer:
    connection:
      address: "localhost:9010"
      timeout: 5000ms
      retry_count: 3
```

### 高级配置
```yaml
executor:
  # 安全配置
  security:
    enable_sandbox: true            # 启用沙箱模式
    allowed_paths:                  # 允许访问的路径
      - "/usr/bin"
      - "/lib"
      - "/tmp"
    blocked_syscalls:               # 禁止的系统调用
      - "ptrace"
      - "mount"

  # IO 配置
  io:
    stdin_buffer_size: 1MB          # 标准输入缓冲区大小
    stdout_buffer_size: 4MB         # 标准输出缓冲区大小
    stderr_buffer_size: 2MB         # 标准错误缓冲区大小
    merge_output: false             # 是否合并标准输出和错误

  # 监控配置
  monitoring:
    enable_resource_monitoring: true
    monitoring_interval: 1s
    log_resource_usage: true
```

## 使用方法

### 基本执行
```bash
# 执行简单命令
./ytserver-exec --job-id job-001 -- \
  ls -la /tmp

# 执行用户脚本
./ytserver-exec --job-id job-002 -- \
  /bin/bash /path/to/script.sh

# 带环境变量的执行
./ytserver-exec --job-id job-003 \
  --env PATH=/custom/path \
  --env CUSTOM_VAR=value \
  -- python my_script.py
```

### 配置文件执行
```bash
# 使用配置文件
./ytserver-exec --config executor.config.yson

# 配置文件示例
```
```yson
{
  job_id = "job-12345";
  executor = {
    resource_limits = {
      cpu_limit = 2;
      memory_limit = "4GB";
    };
    working_directory = "/tmp/job_work";
    environment = ["PATH=/usr/bin", "HOME=/tmp"];
  };
  synchronizer = {
    connection = {
      address = "localhost:9010";
      timeout = 5000;
    };
  };
  command = ["python", "script.py"];
}
```

### 作业同步
```cpp
// C++ 客户端同步示例
#include <yt/yt/server/exec/user_job_synchronizer.h>

// 创建同步器客户端
auto synchronizer = CreateUserJobSynchronizerClient(config);

// 通知执行器已准备就绪
synchronizer->NotifyExecutorPrepared();
```

### 资源监控
```bash
# 查看作业资源使用情况
cat /proc/<pid>/status

# 监控 CPU 使用
top -p <pid>

# 监控内存使用
cat /proc/<pid>/statm
```

## 实现原理

### 作业执行流程
1. **初始化**: 解析配置参数和环境设置
2. **资源设置**: 设置进程资源限制和安全限制
3. **进程创建**: 使用 fork/exec 创建用户作业进程
4. **IO 重定向**: 设置标准输入输出的重定向
5. **同步通知**: 通知 Job Proxy 执行器已准备就绪
6. **执行监控**: 监控作业执行状态和资源使用
7. **结果收集**: 收集作业输出和退出状态
8. **清理资源**: 清理临时文件和资源

### 进程隔离机制
1. **文件系统隔离**: 限制文件系统访问权限
2. **网络隔离**: 控制网络连接和端口访问
3. **进程隔离**: 限制进程间通信和信号
4. **资源隔离**: 实施 CPU、内存等资源限制

### 错误处理机制
1. **启动错误**: 处理进程创建和初始化错误
2. **运行时错误**: 捕获和处理运行时异常
3. **资源错误**: 处理资源耗尽和限制违规
4. **通信错误**: 处理与 Job Proxy 通信失败

### 退出码映射
```
100 - ExecutorStderrOpenError: 标准错误打开失败
101 - ExecutorStderrDuplicateError: 标准错误重定向失败
102 - ExecutorError: 执行器初始化错误
103 - ExecveError: 系统调用 execve 失败
104 - JobProxyNotificationError: Job Proxy 通知失败
```

## 监控和调试

### 关键指标
- 作业执行时间和成功率
- 资源使用情况 (CPU、内存、IO)
- 错误类型和频率统计
- 进程创建和终止数量
- 网络连接状态

### 调试信息
```bash
# 启用详细日志
./ytserver-exec --log-level debug --job-id job-debug

# 查看进程信息
ps aux | grep ytserver-exec

# 查看系统调用
strace -p <pid>

# 查看网络连接
netstat -p | grep <pid>
```

### 性能分析
```bash
# CPU 性能分析
perf record -p <pid>
perf report

# 内存使用分析
valgrind --tool=massif ./ytserver-exec ...

# 系统调用统计
strace -c ./ytserver-exec ...
```

## 安全考虑

### 进程隔离
- 使用 chroot 限制文件系统访问
- 设置适当的用户权限和组权限
- 限制可执行文件和库的访问

### 资源保护
- 设置严格的资源限制防止滥用
- 监控异常的资源使用模式
- 实现资源配额和公平调度

### 网络安全
- 限制网络连接和端口访问
- 防止网络攻击和恶意流量
- 实施网络隔离和防火墙规则

## 性能优化

### 启动优化
- 预分配和复用资源
- 优化进程创建流程
- 减少初始化开销

### IO 优化
- 使用高效的缓冲策略
- 优化管道和数据传输
- 实施流控制和背压处理

### 资源管理优化
- 动态调整资源限制
- 优化内存分配策略
- 实施 CPU 亲和性设置

## 故障排除

### 常见问题
1. **进程启动失败**: 检查权限、路径和依赖
2. **资源限制违规**: 调整资源限制配置
3. **IO 重定向错误**: 检查管道和文件权限
4. **同步通信失败**: 检查网络连接和超时设置

### 调试步骤
1. 检查配置文件和环境变量
2. 查看详细的错误日志
3. 验证文件权限和路径
4. 测试网络连接和通信
5. 分析系统资源使用情况

### 恢复策略
- 自动重试机制
- 优雅降级处理
- 状态恢复和重连

## 相关组件

- **Job Proxy**: 作业代理服务，负责作业调度和管理
- **Node Service**: 节点服务，提供资源管理和监控
- **Scheduler**: 调度器，负责任务分配和调度

## 最佳实践

### 部署建议
- 合理配置资源限制
- 设置适当的超时时间
- 启用详细日志记录

### 运维管理
- 定期监控性能指标
- 建立告警和通知机制
- 实施自动化运维脚本

### 安全实践
- 定期更新安全补丁
- 实施最小权限原则
- 加强访问控制和审计

## 版本历史

- 初始版本支持基本作业执行功能
- 增加资源限制和监控功能
- 增强安全隔离机制
- 性能优化和稳定性改进