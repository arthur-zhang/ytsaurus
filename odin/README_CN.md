# Odin 集群监控服务

Odin 是一个定期在集群上运行检查的服务，用作外部监控工具。

## 目录结构

- **bin/** - 可执行文件
  - Odin 服务的执行脚本
  - 配置文件生成器
  - 实用工具集

- **checks/** - 检查模块
  - 各种健康检查的实现
  - 自定义检查规则
  - 监控指标收集器

- **lib/** - 核心库
  - Odin 服务框架
  - 公共工具函数
  - 配置管理模块

- **packages/** - 打包文件
  - Python 包构建脚本
  - 安装和部署文件

- **tests/** - 测试套件
  - 单元测试
  - 集成测试
  - 测试工具和模拟器

- **requirements.txt** - Python 依赖
  - 定义所需的 Python 包
  - 版本锁定文件

- **ya.make** - 构建配置
  - YaTool 构建系统配置

## 功能特性

### 监控检查
- **节点健康检查**：监控集群节点的健康状态
- **服务可用性**：检查各种服务的可用性
- **性能指标**：收集性能和资源使用指标
- **自定义检查**：支持自定义监控规则

### 报告机制
- **实时告警**：异常情况实时通知
- **历史数据**：保存历史监控数据
- **趋势分析**：提供性能趋势分析
- **报告生成**：自动生成监控报告

### 分布式架构
- **多集群支持**：同时监控多个集群
- **水平扩展**：支持水平扩展部署
- **容错机制**：服务故障自动恢复
- **负载均衡**：检查任务负载均衡

## 使用方法

### 构建准备

#### 准备 Odin 库
按照 [说明文档](https://github.com/ytsaurus/ytsaurus/tree/main/yt/python#preparation-and-installation) 准备 Python 库。

假设环境变量 `SOURCE_ROOT`、`BUILD_ROOT` 和 `PYTHON_ROOT` 已定义，且 Python 虚拟环境已准备就绪。

#### 准备步骤

1. **安装额外的 Python 库**
```bash
pip install -r $SOURCE_ROOT/yt/odin/requirements.txt
```

2. **准备 Odin 模块**
```bash
$SOURCE_ROOT/yt/odin/packages/prepare_python_modules.py \
    --source-root "$SOURCE_ROOT" \
    --output-path "$PYTHON_ROOT"
```

3. **安装 Odin 模块**
```bash
cd "$PYTHON_ROOT"
cp "$SOURCE_ROOT/yt/odin/packages/setup.py" .
python3 setup.py install
```

### 运行测试

1. **安装测试所需的 Python 库**
```bash
pip install -r "${SOURCE_ROOT}/yt/odin/tests/requirements.txt"
```

2. **准备 ytserver 符号链接**
```bash
mkdir -p ${BUILD_ROOT}/yt/yt/packages/tests_package/
ln -s ${BUILD_ROOT}/yt/yt/server/all/ytserver-all \
    ${BUILD_ROOT}/yt/yt/packages/tests_package/ytserver-all
```

3. **创建测试沙箱目录**
```bash
mkdir <tests_sandbox>
export TESTS_SANDBOX="<tests_sandbox>"
```

4. **运行测试**
```bash
cd "$SOURCE_ROOT/yt/odin/tests"
YT_BUILD_ROOT="$BUILD_ROOT" \
YT_TESTS_SANDBOX="$TESTS_SANDBOX" \
python -m pytest
```

### 配置和运行服务

#### 生成配置文件
```bash
# 生成默认配置
$SOURCE_ROOT/yt/odin/bin/generate_config.py \
    --cluster my_cluster \
    --output config.yaml
```

#### 启动 Odin 服务
```bash
# 使用配置文件启动
odin-server --config config.yaml

# 或使用命令行参数
odin-server \
    --cluster localhost:8000 \
    --interval 60 \
    --checks all
```

### 添加自定义检查

1. **创建检查模块**
```python
# custom_check.py
from odin.checks import BaseCheck

class CustomCheck(BaseCheck):
    def run(self):
        # 实现检查逻辑
        result = self.perform_check()
        return {
            'status': 'OK' if result else 'FAIL',
            'message': 'Custom check result',
            'metrics': result.metrics
        }
```

2. **注册检查**
```yaml
# config.yaml
checks:
  - name: custom_check
    module: custom_check.CustomCheck
    enabled: true
    interval: 300
```

## 配置选项

### 基本配置
```yaml
cluster: "localhost:8000"  # YTsaurus 集群地址
token: "your_token"        # 认证令牌
interval: 60               # 检查间隔（秒）
timeout: 30                # 请求超时（秒）
log_level: "INFO"          # 日志级别
```

### 检查配置
```yaml
checks:
  - name: "node_health"
    enabled: true
    interval: 300
    options:
      failure_threshold: 3

  - name: "disk_space"
    enabled: true
    interval: 600
    options:
      warning_threshold: 0.8
      critical_threshold: 0.9
```

### 通知配置
```yaml
notifications:
  email:
    enabled: true
    smtp_server: "smtp.example.com"
    recipients:
      - "admin@example.com"

  slack:
    enabled: true
    webhook_url: "https://hooks.slack.com/..."
    channel: "#alerts"
```

## 监控指标

Odin 收集以下类型的指标：

### 系统指标
- CPU 使用率
- 内存使用率
- 磁盘空间
- 网络流量

### YTsaurus 指标
- Master 服务状态
- 节点在线数量
- 表操作延迟
- 作业执行时间

### 应用指标
- 服务响应时间
- 错误率
- 并发连接数
- 队列长度

## 最佳实践

1. **检查频率优化**
   - 根据重要性设置不同的检查频率
   - 避免过于频繁的检查影响系统性能
   - 在业务低峰期进行深度检查

2. **告警策略**
   - 设置合理的告警阈值
   - 使用分级告警机制
   - 避免告警风暴

3. **资源管理**
   - 监控 Odin 自身的资源使用
   - 定期清理历史数据
   - 优化检查任务的资源消耗

## 故障排查

### 常见问题

1. **检查失败**
   - 检查网络连接
   - 验证认证配置
   - 查看详细错误日志

2. **性能问题**
   - 优化检查逻辑
   - 增加并发处理
   - 使用缓存机制

3. **数据不一致**
   - 检查时间同步
   - 验证数据源
   - 检查缓存一致性

## 依赖项

- Python 3.8+
- YTsaurus Python 客户端
- 通知服务配置 (可选)
- 监控系统集成 (可选)