# 示例代码集合

本目录包含 YTsaurus 系统的各种示例代码和演示程序，帮助开发者快速理解和使用系统功能。

## 目录结构

- **comment_service/** - 评论服务示例
  - 完整的微服务应用示例
  - 展示如何使用 YTsaurus 构建分布式服务
  - 包含数据模型、API 设计、服务部署等

- **rpc_proxy_sample/** - RPC 代理示例
  - RPC 代理服务的演示代码
  - 展示 YTsaurus RPC 框架的使用方法
  - 包含客户端和服务端实现

- **scheduling_demo/** - 调度演示
  - 任务调度系统的示例
  - 展示如何使用 YTsaurus 的调度功能
  - 包含作业提交、执行、监控的完整流程

- **CMakeLists.txt** - CMake 构建配置
  - 定义示例代码的构建规则

- **ya.make** - YaTool 构建配置
  - 兼容 YaTool 构建系统

## 示例说明

### comment_service
评论服务是一个完整的示例应用，展示：
- 数据存储设计
- RESTful API 实现
- 服务发现和负载均衡
- 错误处理和重试机制
- 监控和日志记录

主要组件：
- 数据模型定义
- API 端点实现
- 服务注册和发现
- 配置管理
- 测试用例

### rpc_proxy_sample
RPC 代理示例展示：
- YTsaurus RPC 协议使用
- 服务接口定义
- 客户端连接管理
- 请求路由和转发
- 性能优化技巧

主要文件：
- 服务接口定义 (.proto)
- 服务端实现
- 客户端封装
- 配置文件
- 性能测试

### scheduling_demo
调度演示展示：
- MapReduce 作业编写
- 任务提交和管理
- 资源申请和调度
- 执行结果处理
- 错误处理和重试

主要功能：
- 数据准备阶段
- Map 任务实现
- Reduce 任务实现
- 结果收集和分析

## 快速开始

### 构建示例
```bash
# 使用 CMake 构建
mkdir build && cd build
cmake -DCMAKE_BUILD_TYPE=Release ../examples
ninja

# 使用 ya make 构建
ya make examples
```

### 运行示例

#### 评论服务
```bash
# 启动服务
./comment_service/bin/comment_service --config config.yaml

# 测试 API
curl -X POST http://localhost:8080/comments \
  -H "Content-Type: application/json" \
  -d '{"text": "Hello YTsaurus!", "author": "user1"}'
```

#### RPC 代理
```bash
# 启动服务端
./rpc_proxy_sample/bin/server --port 9000

# 运行客户端
./rpc_proxy_sample/bin/client --server localhost:9000
```

#### 调度演示
```bash
# 提交作业
./scheduling_demo/bin/submit_job \
  --input /path/to/input \
  --output /path/to/output \
  --mapper ./mapper.py \
  --reducer ./reducer.py
```

## 学习路径

1. **初学者**
   - 从 RPC 代理示例开始
   - 理解基本的客户端-服务端交互
   - 学习配置和错误处理

2. **进阶开发者**
   - 研究评论服务示例
   - 理解微服务架构设计
   - 学习服务治理最佳实践

3. **高级用户**
   - 深入调度演示
   - 掌握分布式计算模式
   - 优化性能和资源利用

## 技术栈

- **编程语言**：C++, Python
- **构建工具**：CMake, YaTool
- **通信协议**：gRPC, HTTP/REST
- **序列化**：Protocol Buffers
- **测试框架**：Google Test, pytest

## 扩展建议

基于这些示例，你可以：
1. 修改和扩展现有功能
2. 集成到自己的项目中
3. 作为新项目的基础模板
4. 学习分布式系统设计模式

## 常见问题

### 如何连接到本地 YTsaurus 集群？
```cpp
auto client = NYT::CreateClient("localhost:8000");
```

### 如何处理大规模数据？
使用分片和批处理策略：
```cpp
TReadTableOptions options;
options.SetChunkSize(1024 * 1024); // 1MB chunks
```

### 如何优化性能？
- 使用批量操作
- 合理设置缓冲区大小
- 利用本地性优化
- 启用压缩