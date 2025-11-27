# Cron 定时任务

本目录包含 YTsaurus 系统的定时任务和计划任务脚本，用于系统的自动化维护和管理。

## 目录结构

- **clear_tmp/** - 临时文件清理
  - 定时清理系统临时文件
  - 释放磁盘空间，维护系统性能

- **prune_offline_cluster_nodes/** - 离线节点清理
  - 清理长时间离线的集群节点
  - 维护集群拓扑的健康状态

- **snapshot_processing/** - 快照处理
  - 定时处理系统快照
  - 快照的创建、归档和清理

- **requirements.txt** - Python 依赖
  - 定义定时任务脚本所需的 Python 包

- **ya.make** - 构建配置
  - 定义定时任务组件的构建规则

## 功能特性

### 自动化维护
- 定时清理临时文件和日志
- 自动处理系统快照
- 清理无效的集群节点

### 资源管理
- 磁盘空间监控和清理
- 无效资源回收
- 系统性能优化

### 任务调度
- 基于 Cron 的任务调度
- 支持复杂的调度规则
- 任务执行日志记录

## 使用方法

### 安装定时任务
```bash
# 复制定时任务脚本到系统目录
sudo cp cron/scripts/* /etc/cron.d/

# 或使用 crontab 安装
crontab cron/crontab.conf
```

### 手动执行任务
```bash
# 清理临时文件
python cron/clear_tmp/clear_tmp.py

# 处理快照
python cron/snapshot_processing/process_snapshots.py

# 清理离线节点
python cron/prune_offline_cluster_nodes/prune_nodes.py
```

### 配置任务参数
在相应的配置文件中设置：
- 清理周期
- 保留策略
- 通知设置

## 定时任务列表

### clear_tmp
- **执行频率**：每日凌晨执行
- **功能**：清理超过指定时间的临时文件
- **保留策略**：保留最近 7 天的文件

### prune_offline_cluster_nodes
- **执行频率**：每小时检查一次
- **功能**：标记并清理离线超过阈值时间的节点
- **阈值设置**：默认 24 小时

### snapshot_processing
- **执行频率**：根据配置定期执行
- **功能**：
  - 创建系统快照
  - 归档历史快照
  - 清理过期快照

## 依赖项

- Python 3.8+
- YTsaurus Python 客户端库
- Cron 服务 (系统守护进程)

## 监控和日志

- 任务执行日志存储在 `/var/log/ytsaurus/cron/`
- 支持邮件通知失败任务
- 集成到系统监控体系

## 安全考虑

- 任务执行使用最小权限原则
- 敏感操作需要额外验证
- 定期审核任务配置