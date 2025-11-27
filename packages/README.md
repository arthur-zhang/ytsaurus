# 软件包管理

本目录包含 YTsaurus 的软件包管理和发布相关文件，负责软件的打包、版本管理和分发。

## 目录结构

- **latest/** - 最新版本目录
  - 存储最新版本的软件包
  - 版本标识和元数据
  - 发布说明和变更日志

- **ya.make.common** - 通用构建配置
  - 软件包构建的通用规则
  - YaTool 构建系统的共享配置
  - 版本和依赖管理

## 功能特性

### 版本管理
- 自动化版本标记
- 版本兼容性检查
- 发布流程管理
- 版本回滚支持

### 软件打包
- 多平台包构建
- 依赖关系解析
- 包签名验证
- 自动化测试集成

### 分发机制
- 多种分发渠道
- 自动化部署
- 增量更新支持
- 回滚机制

## 使用方法

### 创建新版本包
```bash
# 更新版本号
echo "1.2.3" > packages/latest/version

# 构建软件包
ya make packages

# 生成发布包
./packages/scripts/create_release.sh
```

### 安装软件包
```bash
# 从源码安装
ya make -t package

# 使用预编译包
./install_packages.sh --version latest
```

### 检查包依赖
```bash
# 验证依赖关系
./packages/scripts/check_deps.py

# 解析依赖树
./packages/scripts/resolve_deps.sh
```

## 包结构

### 包命名规范
- `ytsaurus-core-{version}.tar.gz` - 核心服务包
- `ytsaurus-client-{version}.tar.gz` - 客户端库包
- `ytsaurus-tools-{version}.tar.gz` - 工具集包
- `ytsaurus-examples-{version}.tar.gz` - 示例代码包

### 包内容
- `bin/` - 可执行文件
- `lib/` - 库文件
- `include/` - 头文件
- `share/` - 共享资源
- `docs/` - 文档
- `examples/` - 示例
- `tests/` - 测试文件

## 构建流程

1. **准备环境**
   - 检查依赖
   - 设置构建环境
   - 初始化构建目录

2. **编译代码**
   - 编译核心组件
   - 构建客户端库
   - 生成工具程序

3. **打包处理**
   - 收集构建产物
   - 处理依赖关系
   - 生成包元数据

4. **验证测试**
   - 安装测试
   - 功能验证
   - 性能测试

5. **发布部署**
   - 签名验证
   - 上传到仓库
   - 更新索引

## 配置说明

### 构建配置
```makefile
# ya.make.common 示例
PACKAGE_NAME = ytsaurus
PACKAGE_VERSION = $(shell cat packages/latest/version)
PACKAGE_DIR = dist/packages

# 通用构建规则
%.package: %.build
	$(call build_package,$@)
```

### 发布配置
```yaml
# release_config.yaml
repositories:
  primary: https://repo.ytsaurus.tech
  mirrors:
    - https://mirror1.ytsaurus.tech
    - https://mirror2.ytsaurus.tech

signing:
  enabled: true
  keyring: /etc/ytsaurus/keys
```

## 版本策略

### 语义化版本
- 主版本号：不兼容的 API 修改
- 次版本号：向下兼容的功能性新增
- 修订号：向下兼容的问题修正

### 发布周期
- **主版本**：6-12 个月
- **次版本**：1-3 个月
- **补丁版本**：根据需要发布

### 分支策略
- `main` - 主开发分支
- `release/x.y` - 发布分支
- `hotfix/x.y.z` - 热修复分支

## 依赖管理

### 系统依赖
- Linux 内核 >= 4.14
- GLIBC >= 2.17
- OpenSSL >= 1.1.1

### 运行时依赖
- Python 3.8+
- Java 8+ (可选)
- Go 1.18+ (可选)

### 构建依赖
- CMake 3.22+
- Clang-18
- Ninja 1.10+

## 质量保证

### 自动化测试
- 单元测试覆盖率 > 80%
- 集成测试套件
- 性能回归测试
- 安全扫描

### 包验证
- 签名验证
- 完整性校验
- 安装测试
- 运行时验证

### 持续集成
- 自动化构建流程
- 多平台测试
- 自动发布流程
- 失败通知机制

## 最佳实践

1. **版本管理**
   - 使用语义化版本
   - 维护变更日志
   - 打标签标记版本
   - 定期发布稳定版本

2. **依赖处理**
   - 明确声明依赖
   - 锁定依赖版本
   - 定期更新依赖
   - 处理安全漏洞

3. **包优化**
   - 最小化包大小
   - 去除不必要的文件
   - 压缩优化
   - 分层打包

4. **发布流程**
   - 自动化发布
   - 充分测试验证
   - 准备回滚方案
   - 监控发布状态