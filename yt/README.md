# YTsaurus 核心系统 (YTsaurus Core System)

## 概述

此目录包含 YTsaurus 分布式存储和处理平台的核心实现。YTsaurus 是一个企业级的大数据处理平台，支持分布式文件系统、NoSQL 数据库、MapReduce 计算框架等功能。

## 系统架构

YTsaurus 采用微服务架构，主要包含以下核心组件：

### 服务器组件 (server/)
分布式系统的主要服务：
- **Master** - 主节点，负责元数据管理和集群协调
- **Scheduler** - 任务调度器，负责任务分配和资源管理
- **Node** - 工作节点，负责数据存储和计算执行
- **RPC Proxy** - RPC 代理，提供客户端访问接口
- **HTTP Proxy** - HTTP 代理，提供 REST API 访问
- **Query Tracker** - 查询追踪器，管理 SQL 查询执行
- **Cell Balancer** - 单元平衡器，优化 tablet 分布

### 客户端库 (client/)
多语言客户端 SDK：
- **C++ Client** - 功能最完整的客户端实现
- **Python Client** - Python 绑定和接口
- **Java Client** - Java 语言客户端
- **Go Client** - Go 语言客户端

## 核心功能

### 分布式存储
- **文件系统** - 类似 HDFS 的分布式文件系统
- **表存储** - 结构化数据表存储
- **版本控制** - 数据版本管理和快照
- **复制和容错** - 数据自动复制和故障恢复

### 数据处理
- **MapReduce** - 分布式计算框架
- **SQL 查询** - YQL 查询引擎集成
- **流处理** - 实时数据处理
- **批处理** - 大规模批处理作业

### 事务支持
- **ACID 事务** - 分布式事务保证
- **原子操作** - 原子的读写操作
- **隔离级别** - 可配置的隔离级别
- **一致性保证** - 强一致性模型

## 目录结构详解

### 核心库 (core/)
系统基础组件和工具：
- **通信框架** - RPC 通信和序列化
- **数据结构** - 核心数据类型定义
- **并发控制** - 线程和协程管理
- **日志系统** - 结构化日志记录

### 共享库 (ytlib/)
共享功能库：
- **客户端实现** - 客户端核心逻辑
- **协议处理** - YTsaurus 协议实现
- **工具函数** - 通用工具和辅助函数

### 测试套件 (tests/)
全面的测试框架：
- **单元测试** - 组件级别测试
- **集成测试** - 端到端功能测试
- **性能测试** - 基准测试和压力测试
- **兼容性测试** - 版本兼容性验证

### 工具集 (tools/)
运维和开发工具：
- **命令行工具** - YT CLI 工具集
- **管理工具** - 集群管理工具
- **调试工具** - 问题诊断工具
- **性能分析** - 性能分析工具

## 技术特性

### 高可用性
- **无单点故障** - 所有关键组件都有冗余
- **自动故障转移** - 节点故障自动恢复
- **数据复制** - 多副本数据存储
- **一致性协议** - Raft 一致性算法

### 可扩展性
- **水平扩展** - 支持数千节点集群
- **弹性伸缩** - 动态添加/移除节点
- **负载均衡** - 智能负载分布
- **数据分片** - 自动数据分片

### 性能优化
- **向量化执行** - 批量数据处理
- **列式存储** - 列式数据格式
- **内存优化** - 高效内存管理
- **网络优化** - 零拷贝网络 I/O

## 使用示例

### 命令行操作
```bash
# 创建表
yt create table //home/user/my_table

# 写入数据
yt write-table //home/user/my_table < data.yson

# 读取数据
yt read-table //home/user/my_table

# 运行 MapReduce 作业
yt mapreduce --mapper mapper.py --reducer reducer.py input_table output_table
```

### C++ 客户端
```cpp
#include <yt/client/api/client.h>
#include <yt/client/api/transaction.h>

auto client = CreateClient("localhost");
auto transaction = client->StartTransaction(NYT::NTransactionClient::ETransactionType::Master);

// 写入数据
auto writer = transaction->CreateTableWriter("//tmp/table");
writer->WriteRow(row);
writer->Close();

// 提交事务
transaction->Commit();
```

### Python 客户端
```python
import yt

yt.init("localhost")

# 写入数据
yt.write_table("//tmp/table", [{"key": "value"}])

# 读取数据
for row in yt.read_table("//tmp/table"):
    print(row)
```

## 部署架构

### 集群组件
```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   Master    │     │  Scheduler  │     │ RPC Proxy   │
│   (3+)      │     │   (2+)      │     │   (2+)      │
└─────────────┘     └─────────────┘     └─────────────┘
       │                     │                     │
       └─────────────────────┼─────────────────────┘
                             │
    ┌────────────────────────┼────────────────────────┐
    │                        │                        │
┌───▼────┐            ┌─────▼────┐             ┌─────▼────┐
│ Node 1 │   ...      │  Node N  │     ...     │ Node M   │
│ (Data) │            │ (Compute)│             │ (Mix)    │
└────────┘            └──────────┘             └──────────┘
```

### 数据流转
1. **客户端请求** → RPC Proxy
2. **元数据查询** → Master
3. **数据操作** → Node
4. **任务调度** → Scheduler
5. **计算执行** → Node

## 配置管理

### 集群配置
- **拓扑配置** - 集群节点和角色定义
- **存储配置** - 数据存储策略
- **网络配置** - 网络和安全设置
- **资源配额** - 资源限制和配额

### 运行时配置
- **动态配置** - 运行时参数调整
- **特性开关** - 功能特性开关
- **性能调优** - 性能相关参数
- **安全策略** - 访问控制和认证

## 监控和运维

### 监控指标
- **系统指标** - CPU、内存、磁盘、网络
- **业务指标** - QPS、延迟、错误率
- **数据指标** - 存储使用、副本数
- **作业指标** - 任务执行统计

### 日志管理
- **结构化日志** - JSON 格式日志
- **日志聚合** - 集中式日志收集
- **日志分析** - 日志查询和分析
- **告警系统** - 自动告警通知

### 运维工具
- **集群管理** - 节点生命周期管理
- **数据管理** - 数据备份和恢复
- **升级管理** - 滚动升级支持
- **故障处理** - 故障诊断和恢复

## 开发指南

### 构建系统
```bash
# 配置构建
cmake -G Ninja -DCMAKE_BUILD_TYPE=Release \
      -DCMAKE_TOOLCHAIN_FILE=../ytsaurus/clang.toolchain \
      ../ytsaurus

# 构建
ninja ytserver-all

# 运行测试
./yt/yt/tests/integration/run_tests.sh
```

### 代码贡献
1. Fork 项目仓库
2. 创建功能分支
3. 实现功能并添加测试
4. 提交 Pull Request
5. 代码审查和合并

## 版本信息

### 当前版本
- **协议版本** - RpcProxyProtocolVersion.txt
- **兼容性** - 向后兼容保证
- **发布周期** - 定期发布周期

### 版本特性
- 分布式事务支持
- 多租户隔离
- 实时流处理
- 机器学习集成