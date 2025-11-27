# Docker 容器化

本目录包含 YTsaurus 系统的 Docker 容器化方案，提供完整的容器化部署和管理解决方案。

## 目录结构

- **build-env/** - 构建环境镜像
  - 包含编译环境的 Docker 镜像
  - 用于交叉编译和多平台构建

- **charts/** - Helm Charts
  - Kubernetes 部署配置
  - 包含完整的集群部署方案

- **cron/** - 定时任务容器
  - Docker 化的定时任务服务
  - 容器化的系统维护脚本

- **local/** - 本地开发环境
  - 本地开发用的 Docker Compose 配置
  - 快速搭建开发测试环境

- **sidecars/** - 旁路容器
  - 辅助功能容器
  - 监控、日志收集等边车容器

- **ya-build/** - YaTool 构建容器
  - 基于 YaTool 的构建环境
  - 标准化的构建流程

- **ytsaurus/** - 主服务容器
  - `Dockerfile` - 主服务镜像构建文件
  - `build.sh` - 自动化构建脚本
  - `setup_cluster_for_chyt.sh` - CHYT 集群设置脚本
  - `gpuagent_runner.sh` - GPU 代理运行脚本
  - `credits/` - 开源许可证信息

- **ytsaurus-bundle/** - 打包发布
  - 完整的发布包
  - 包含所有必要组件

## 功能特性

### 容器化部署
- 完整的 Docker 镜像支持
- 多架构镜像构建 (x86_64, aarch64)
- 优化的镜像大小和层数

### Kubernetes 支持
- Helm Charts 部署模板
- 自动扩缩容配置
- 高可用集群部署
- 持久化存储管理

### 开发环境
- Docker Compose 一键启动
- 集成开发环境配置
- 热重载和调试支持

## 使用方法

### 构建镜像
```bash
# 构建主服务镜像
cd docker/ytsaurus
./build.sh

# 构建所有镜像
docker build -t ytsaurus:latest -f ytsaurus/Dockerfile .
```

### 本地开发环境
```bash
# 使用 Docker Compose 启动
cd docker/local
docker-compose up -d

# 查看服务状态
docker-compose ps
```

### Kubernetes 部署
```bash
# 使用 Helm 部署
helm install ytsaurus ./docker/charts/ytsaurus \
  --set cluster.size=3 \
  --set storage.class=standard

# 或使用 kubectl 直接部署
kubectl apply -f docker/charts/ytsaurus/templates/
```

### 开发环境配置
```bash
# 设置开发环境变量
export YT_PROXY=localhost:8000
export YT_TOKEN=your_token

# 运行测试
docker exec -it ytsaurus-container bash
```

## 镜像说明

### ytsaurus:latest
- 基础服务镜像
- 包含所有核心组件
- 支持 Master, Node, Scheduler 等角色

### ytsaurus-build:latest
- 构建环境镜像
- 包含编译工具链
- 用于源码构建和定制化开发

### ytsaurus-sidecar:latest
- 辅助功能镜像
- 监控和日志收集
- 健康检查和服务发现

## 配置选项

### 环境变量
- `YT_PROXY` - 代理服务地址
- `YT_TOKEN` - 认证令牌
- `YT_CLUSTER_NAME` - 集群名称
- `YT_CONFIG_PATH` - 配置文件路径

### 存储配置
- 持久化存储类
- 存储大小和类型
- 备份策略

### 网络配置
- 服务发现
- 负载均衡
- 网络策略

## 依赖项

- Docker 20.10+
- Docker Compose 2.0+ (可选)
- Kubernetes 1.20+ (生产环境)
- Helm 3.0+ (Kubernetes 部署)

## 最佳实践

1. **镜像优化**
   - 使用多阶段构建
   - 最小化镜像层数
   - 使用 .dockerignore

2. **安全配置**
   - 非特权用户运行
   - 资源限制
   - 安全上下文配置

3. **监控运维**
   - 健康检查端点
   - 指标暴露
   - 日志聚合