# CHYT ClickHouse 集成

CHYT (ClickHouse on YTsaurus) 是 YTsaurus 的 ClickHouse 分布式分析引擎集成组件，提供高性能的 OLAP 查询能力。

## 目录结构

- **client/** - 客户端库
  - 提供 CHYT 的客户端接口
  - 支持 C++ 和 Python 客户端

- **controller/** - 控制器组件
  - 管理 CHYT 集群的生命周期
  - 处理查询路由和负载均衡

- **server/** - 服务端实现
  - `bootstrap.cpp/h` - 服务启动引导程序
  - `ch_to_yt_converter.cpp/h` - ClickHouse 到 YTsaurus 的数据转换器
  - `clickhouse_config.cpp/h` - ClickHouse 配置管理
  - `clickhouse_invoker.cpp/h` - ClickHouse 服务调用器
  - `clickhouse_server.cpp/h` - 主服务实现
  - `clickhouse_service.cpp/h` - 服务接口定义
  - `cluster_nodes.cpp` - 集群节点管理
  - `bin/` - 可执行文件目录

- **tests/** - 测试套件
  - 单元测试和集成测试
  - 性能测试用例

- **trampoline/** - 跳板程序
  - 用于服务启动和管理

- **构建配置**
  - `CMakeLists.txt` - 主构建配置
  - `CMakeLists.*.txt` - 各平台特定的构建配置
  - `ya.make` - YaTool 构建配置

## 功能特性

### 查询引擎集成
- 无缝集成 ClickHouse 查询引擎
- 支持 SQL 标准和 ClickHouse 扩展语法
- 优化的查询执行计划

### 数据互操作性
- YTsaurus 表到 ClickHouse 的自动映射
- 数据类型自动转换
- 支持分布式表查询

### 集群管理
- 动态集群扩展和收缩
- 故障自动恢复
- 负载均衡优化

## 使用方法

### 构建 CHYT
```bash
# 使用 CMake 构建
mkdir build && cd build
cmake -G Ninja -DCMAKE_BUILD_TYPE=Release ../ytsaurus/chyt
ninja

# 使用 ya make 构建
ya make chyt
```

### 启动 CHYT 服务
```bash
# 启动控制器
./controller/bin/chyt-controller --config config.yaml

# 启动服务实例
./server/bin/clickhouse_server --config config.yaml
```

### 执行查询
```sql
-- 通过 CHYT 接口查询 YTsaurus 表
SELECT * FROM `yt://my_table` WHERE date > '2023-01-01'
```

## 架构设计

### 核心组件
1. **控制器 (Controller)**：管理整个 CHYT 集群
2. **服务实例 (Server)**：执行 ClickHouse 查询
3. **数据转换器**：处理 YTsaurus 和 ClickHouse 之间的数据转换
4. **配置管理器**：管理集群和服务配置

### 数据流程
1. 客户端发送查询请求
2. 控制器解析查询并生成执行计划
3. 服务实例执行查询操作
4. 数据转换器处理结果格式
5. 返回查询结果给客户端

## 依赖项

- ClickHouse 核心引擎
- YTsaurus 客户端库
- CMake 3.22+ 或 YaTool
- Clang-18 编译器

## 性能优化

- 查询缓存机制
- 并行执行优化
- 数据本地化策略
- 索引下推优化

## 监控和运维

- 详细的性能指标收集
- 分布式追踪支持
- 自动化故障恢复
- 灵活的配置热更新