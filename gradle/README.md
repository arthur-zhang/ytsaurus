# Gradle 构建工具目录 (Gradle Build Tool)

## 概述

此目录包含 YTsaurus Java 组件使用的 Gradle 构建系统配置。Gradle 是一个高级构建自动化工具，用于管理 Java 项目的编译、测试和部署。

## 目录结构

### Gradle Wrapper (wrapper/)
Gradle Wrapper 是 Gradle 的一个功能，它允许在没有预装 Gradle 的机器上构建项目。

#### Wrapper 文件说明
- **gradle-wrapper.jar** - Gradle Wrapper 的可执行 JAR 文件
- **gradle-wrapper.properties** - Wrapper 配置文件，包含：
  - Gradle 版本信息
  - 下载 URL 配置
  - 本地存储路径设置

## 主要功能

### 构建管理
- **依赖解析** - 自动下载和管理项目依赖
- **编译配置** - 灵活的编译选项配置
- **任务定义** - 自定义构建任务
- **多模块支持** - 支持大型多模块项目

### Java 集成
- **Maven 兼容** - 完全兼容 Maven 仓库
- **增量构建** - 只编译修改的部分
- **并行构建** - 利用多核 CPU 加速构建
- **测试集成** - 支持 JUnit、TestNG 等测试框架

## 使用方法

### 基本构建命令
```bash
# 编译项目
./gradlew build

# 运行测试
./gradlew test

# 清理构建产物
./gradlew clean

# 生成 JAR 包
./gradlew jar

# 安装到本地仓库
./gradlew install
```

### 开发命令
```bash
# 查看可用任务
./gradlew tasks

# 查看项目依赖
./gradlew dependencies

# 生成项目报告
./gradlew projectReport

# 运行特定测试
./gradlew test --tests "*TestClassName"
```

## 配置说明

### Gradle 属性 (gradle.properties)
项目的 Gradle 属性配置：
- JVM 内存设置
- 并行构建选项
- 仓库配置
- 版本定义

### 构建脚本 (build.gradle)
主要构建配置文件：
- 插件声明
- 仓库配置
- 依赖管理
- 任务定义

### 设置文件 (settings.gradle)
项目设置配置：
- 模块定义
- 项目名称
- 构建目录配置

## 项目特性

### 多模块支持
YTsaurus Java 项目使用多模块结构：
- `ytsaurus-client` - Java 客户端库
- `ytsaurus-spark` - Spark 集成
- `ytsaurus-hadoop` - Hadoop 兼容层
- `ytsaurus-examples` - 示例代码

### 依赖管理
- **版本管理** - 统一版本管理
- **范围控制** - 精确控制依赖范围
- **冲突解决** - 自动解决版本冲突
- **传递依赖** - 智能处理传递依赖

### 构建优化
- **缓存机制** - 本地和远程构建缓存
- **增量编译** - 只编译变更文件
- **并行处理** - 多任务并行执行
- **资源优化** - 优化资源使用

## 集成工具

### IDE 集成
- **IntelliJ IDEA** - 原生 Gradle 支持
- **Eclipse** - 通过插件支持
- **VS Code** - Java Extension Pack 支持

### CI/CD 集成
- **Jenkins** - Gradle 插件
- **GitHub Actions** - 官方 Action
- **GitLab CI** - 内置支持
- **TeamCity** - 专用插件

## 最佳实践

### 构建性能优化
1. **启用并行构建** - 设置 `org.gradle.parallel=true`
2. **配置内存** - 合理设置 JVM 堆大小
3. **使用构建缓存** - 启用本地和远程缓存
4. **避免不必要的任务** - 只运行需要的任务

### 依赖管理
1. **使用 BOM** - 统一版本管理
2. **排除不需要的依赖** - 减少构建时间
3. **固定版本** - 避免使用动态版本
4. **定期更新** - 保持依赖更新

### 项目维护
1. **保持构建脚本简洁** - 使用约定优于配置
2. **文档化** - 为自定义任务添加文档
3. **测试构建** - 确保构建在所有环境正常工作
4. **监控构建** - 跟踪构建性能

## 故障排除

### 常见问题
1. **内存不足** - 增加 JVM 堆大小
2. **网络问题** - 配置代理或镜像
3. **版本冲突** - 检查依赖树
4. **缓存问题** - 清理 Gradle 缓存

### 调试技巧
- 使用 `--info` 查看详细信息
- 使用 `--debug` 获取调试输出
- 检查 `~/.gradle` 目录
- 查看构建扫描报告