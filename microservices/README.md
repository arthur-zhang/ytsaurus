# 微服务组件

本目录包含 YTsaurus 系统的微服务架构组件，提供各种独立的服务功能。

## 目录结构

- **bulk_acl_checker/** - 批量 ACL 检查服务
  - 高效的访问控制列表检查
  - 支持批量权限验证
  - 提供高性能权限查询接口

- **bulk_acl_checker_roren/** - RoRen 批量 ACL 检查
  - 基于 RoRen 框架的 ACL 检查实现
  - 针对特定场景优化的版本

- **id_to_path_mapping/** - ID 路径映射服务
  - 对象 ID 到路径的映射管理
  - 支持缓存和快速查询
  - 维护命名空间一致性

- **resource_usage/** - 资源使用统计服务
  - 集群资源使用情况统计
  - 实时资源监控
  - 资源配额管理

- **resource_usage_roren/** - RoRen 资源使用统计
  - 基于 RoRen 框架的资源统计实现
  - 轻量级资源监控方案

- **lib/** - 公共库
  - 微服务共享的库文件
  - 通用工具和接口定义
  - 基础设施代码

- **ytmsvc_initializer/** - 微服务初始化器
  - 微服务启动和初始化
  - 配置加载和验证
  - 依赖注入管理

- **构建配置**
  - `CMakeLists.txt` - CMake 构建配置
  - `ya.make` - YaTool 构建配置

## 功能特性

### 批量 ACL 检查
- **高效验证**：批量检查权限请求
- **缓存机制**：权限信息缓存
- **并发处理**：支持高并发查询
- **细粒度控制**：支持多种权限类型

### ID 路径映射
- **快速查找**：ID 到路径的快速映射
- **双向索引**：支持反向查询
- **增量更新**：动态更新映射关系
- **一致性保证**：确保数据一致性

### 资源使用统计
- **实时监控**：实时资源使用情况
- **历史数据**：保存历史使用记录
- **告警机制**：资源超限告警
- **预测分析**：资源使用趋势预测

## 使用方法

### 构建微服务
```bash
# 使用 CMake 构建
mkdir build && cd build
cmake -DCMAKE_BUILD_TYPE=Release ../microservices
ninja

# 使用 ya make 构建
ya make microservices
```

### 启动服务

#### 批量 ACL 检查服务
```bash
./bulk_acl_checker/bin/bulk_acl_checker \
  --config bulk_acl_checker/config.yaml \
  --port 8080
```

#### ID 路径映射服务
```bash
./id_to_path_mapping/bin/id_to_path_mapping \
  --config config.yaml \
  --port 8081
```

#### 资源使用统计服务
```bash
./resource_usage/bin/resource_usage \
  --config config.yaml \
  --port 8082
```

### 使用 API

#### ACL 检查 API
```python
import requests

# 批量检查权限
response = requests.post('http://localhost:8080/batch_check', json={
    'requests': [
        {'user': 'user1', 'object': 'path1', 'permission': 'read'},
        {'user': 'user2', 'object': 'path2', 'permission': 'write'}
    ]
})

result = response.json()
print(result)  # {'results': [True, False]}
```

#### ID 路径映射 API
```python
# ID 转路径
response = requests.get(f'http://localhost:8081/id_to_path/{object_id}')
path = response.json()['path']

# 路径转 ID
response = requests.get(f'http://localhost:8081/path_to_id/{path}')
id = response.json()['id']
```

#### 资源使用 API
```python
# 获取集群资源使用情况
response = requests.get('http://localhost:8082/resource_usage')
usage = response.json()

# 获取用户资源使用
response = requests.get(f'http://localhost:8082/user_usage/{username}')
user_usage = response.json()
```

## 配置说明

### 共同配置项
- `port` - 服务监听端口
- `cluster_name` - YTsaurus 集群名称
- `yt_proxy` - YTsaurus 代理地址
- `log_level` - 日志级别
- `metrics_port` - 指标暴露端口

### ACL 检查器配置
```yaml
acl_checker:
  cache_ttl: 300  # 缓存 TTL（秒）
  batch_size: 1000  # 批量处理大小
  max_concurrent: 100  # 最大并发数
```

### 资源统计配置
```yaml
resource_usage:
  update_interval: 60  # 更新间隔（秒）
  history_retention: 30  # 历史数据保留天数
  alert_thresholds:  # 告警阈值
    cpu: 0.8
    memory: 0.85
    disk: 0.9
```

## 监控指标

所有微服务都暴露 Prometheus 指标：
- `request_count` - 请求计数
- `request_duration` - 请求延迟
- `error_rate` - 错误率
- `cache_hit_rate` - 缓存命中率
- `active_connections` - 活跃连接数

## 部署方案

### Docker 部署
```yaml
version: '3'
services:
  bulk_acl_checker:
    image: ytsaurus/bulk_acl_checker:latest
    ports:
      - "8080:8080"
    environment:
      - YT_PROXY=localhost:8000
      - CONFIG_PATH=/app/config.yaml
```

### Kubernetes 部署
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: bulk-acl-checker
spec:
  replicas: 3
  selector:
    matchLabels:
      app: bulk-acl-checker
  template:
    metadata:
      labels:
        app: bulk-acl-checker
    spec:
      containers:
      - name: bulk-acl-checker
        image: ytsaurus/bulk_acl_checker:latest
        ports:
        - containerPort: 8080
```

## 性能优化

1. **缓存策略**
   - 使用多级缓存
   - 预加载热点数据
   - 缓存失效策略优化

2. **并发处理**
   - 合理设置线程池大小
   - 使用异步 I/O
   - 批量处理优化

3. **资源管理**
   - 内存池复用
   - 连接池管理
   - CPU 亲和性设置

## 依赖项

- YTsaurus 客户端库
- gRPC/HTTP 服务器框架
- 缓存系统 (Redis/Memory)
- 监控系统 (Prometheus)
- 日志系统 (ELK Stack)