# 第三方依赖库目录 (Contrib)

## 概述

此目录包含 YTsaurus 项目依赖的所有第三方库、工具和组件。这些依赖项经过精心选择和配置，以确保 YTsaurus 的稳定性和性能。

## 目录结构

### 核心依赖
- **libs/** - C/C++ 第三方库集合，包含：
  - Boost C++ 库
  - Protocol Buffers
  - Apache Thrift
  - zlib, bzip2, lz4 等压缩库
  - OpenSSL 加密库
  - 其他系统级依赖

### 语言绑定和工具
- **python/** - Python 依赖库和模块
  - 数据处理库（pandas, numpy）
  - 网络框架（requests, aiohttp）
  - 测试工具（pytest, unittest）
  - 构建工具（setuptools, pip）

- **java/** - Java 依赖库和 Maven 项目
  - Apache Hadoop 集成
  - Spark 连接器
  - Spring Framework
  - 其他 Java 生态系统工具

- **go/** - Go 语言依赖
  - gRPC 库
  - Protobuf Go 绑定
  - Go 标准库扩展

### 集成组件
- **clickhouse/** - ClickHouse 数据库集成
  - ClickHouse 源代码
  - 构建配置
  - 集成测试

- **ydb/** - Yandex Database 集成组件
  - YDB SDK
  - 连接器
  - 示例代码

### 开发工具
- **tools/** - 开发和构建工具
  - 代码生成器
  - 测试工具
  - 性能分析工具
  - 调试辅助工具

### 特殊目录
- **deprecated/** - 已弃用的依赖库
  - 保留用于向后兼容
  - 不建议在新项目中使用

- **restricted/** - 受限制的许可证组件
  - GPL 或其他限制性许可证
  - 需要特别注意使用条款

## 构建配置

### 平台特定配置
- **CMakeLists.txt** - 通用构建配置
- **CMakeLists.darwin-arm64.txt** - macOS Apple Silicon 配置
- **CMakeLists.darwin-x86_64.txt** - macOS Intel 配置
- **CMakeLists.linux-aarch64.txt** - Linux ARM64 配置
- **CMakeLists.linux-x86_64.txt** - Linux x86_64 配置

## 依赖管理策略

### 版本控制
- 使用固定版本确保构建稳定性
- 定期更新到经过测试的版本
- 维护版本兼容性矩阵

### 构建优化
- 使用预编译二进制文件加速构建
- 支持增量构建
- 优化链接过程

### 安全考虑
- 定期更新安全补丁
- 使用经过审核的版本
- 监控安全漏洞公告

## 主要依赖详情

### 核心系统库
1. **Protocol Buffers** - 数据序列化框架
2. **gRPC** - 远程过程调用框架
3. **Apache Arrow** - 内存列式格式
4. **PicoSHA2** - SHA-2 哈希算法实现

### 数据处理库
1. **RocksDB** - 高性能键值存储
2. **Apache ORC** - 列式存储格式
3. **Parquet** - 列式存储格式支持

### 网络和通信
1. **libcurl** - HTTP 客户端库
2. **zmq** - ZeroMQ 消息队列
3. **nginx** - Web 服务器和代理

## 使用指南

### 添加新依赖
1. 评估许可证兼容性
2. 在相应目录添加源代码
3. 更新 CMakeLists.txt
4. 编写构建脚本
5. 添加测试用例

### 更新依赖
1. 检查版本兼容性
2. 运行回归测试
3. 更新文档
4. 提交变更

## 最佳实践

### 依赖选择
- 选择活跃维护的项目
- 优先使用 Apache 2.0/BSD/MIT 许可证
- 避免过度依赖

### 维护策略
- 定期审查依赖清单
- 移除未使用的依赖
- 保持依赖库更新

### 性能优化
- 链接时优化（LTO）
- 使用 Profile Guided Optimization
- 优化编译器标志