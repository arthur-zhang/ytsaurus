# C/C++ 第三方库集合

本目录包含 YTsaurus 项目依赖的所有 C/C++ 第三方库。这些库经过精心选择和配置，以确保系统的稳定性和性能。

## 目录结构

### 核心库（部分主要库）
- **apache/** - Apache 软件基金会项目
  - apr - Apache Portable Runtime
  - arrow - Apache Arrow 列式内存格式
  - thrift - Apache Thrift RPC 框架

- **curl/** - libcurl HTTP 客户端库
  - 支持多种协议（HTTP, HTTPS, FTP 等）
  - 异步传输支持
  - SSL/TLS 加密支持

- **protobuf/** - Protocol Buffers
  - Google 的数据序列化协议
  - 高效的二进制格式
  - 多语言支持

- **grpc/** - gRPC 框架
  - 高性能 RPC 框架
  - 基于 HTTP/2
  - 支持流式传输

### 压缩库
- **brotli/** - Brotli 压缩算法
- **zlib/** - zlib 压缩库
- **lz4/** - LZ4 高速压缩算法
- **zstd/** - Zstandard 压缩算法

### 加密和安全
- **openssl/** - OpenSSL 加密库
  - SSL/TLS 协议实现
  - 加密算法支持
  - 证书管理

- **blake2/** - BLAKE2 哈希算法
- **crcutil/** - CRC 校验和工具

### 系统库
- **c-ares/** - 异步 DNS 解析
- **cxxsupp/** - C++ 支持库
- **clang18-rt/** - Clang 18 运行时
- **clang20-rt/** - Clang 20 运行时

### 数据库和存储
- **rocksdb/** - RocksDB 键值存储
- **leveldb/** - LevelDB 存储引擎

### 时间和日期
- **cctz/** - CCTZ 时区库
  - Howard Hinnant 的日期时间库
  - IANA 时区数据库支持

### 数据处理
- **double-conversion/** - 双精度浮点数转换
- **croaring/** - CRoaring 位图压缩库
- **base64/** - Base64 编解码库

### 数学库
- **clapack/** - CLAPACK 线性代数库
- **cblas/** - CBLAS 基础线性代数子程序

### 解析器和生成器
- **antlr3_cpp_runtime/** - ANTLR3 C++ 运行时
- **antlr4-c3/** - ANTLR4 C 语言绑定
- **antlr4_cpp_runtime/** - ANTLR4 C++ 运行时

### AWS 集成
- **aws-sdk-cpp/** - AWS SDK for C++
  - S3 客户端
  - DynamoDB 客户端
  - 其他 AWS 服务支持

### 调试和诊断
- **backtrace/** - 堆栈跟踪库
- **gperftools/** - Google 性能工具
- **google-perftools/** - 内存和 CPU 分析器

### 其他工具库
- **dtl/** - C++ 模板库
- **crcutil/** - CRC 计算工具
- **android_cpufeatures/** - Android CPU 特性检测

## 平台支持

### 构建配置
- **CMakeLists.txt** - 通用构建配置
- **CMakeLists.linux-x86_64.txt** - Linux x86_64 配置
- **CMakeLists.linux-aarch64.txt** - Linux ARM64 配置
- **CMakeLists.darwin-x86_64.txt** - macOS Intel 配置
- **CMakeLists.darwin-arm64.txt** - macOS Apple Silicon 配置

### 支持的架构
- x86_64 (Intel/AMD)
- ARM64 (Apple Silicon, ARM 服务器)
- 其他架构的有限支持

## 版本管理

### 版本策略
- 使用经过验证的稳定版本
- 定期更新到最新稳定版
- 维护向后兼容性

### 主要库版本
- Protocol Buffers: 3.x
- gRPC: 1.x
- OpenSSL: 1.1.x / 3.x
- Boost: 1.8x
- zlib: 1.2.x

## 构建和使用

### 集成方式
```cmake
# 在 CMakeLists.txt 中使用
find_package(Protobuf REQUIRED)
find_package(gRPC REQUIRED)

target_link_libraries(mytarget
    protobuf::libprotobuf
    gRPC::grpc++
)
```

### 编译选项
- 优化级别：-O2/-O3
- 调试信息：-g
- 位置无关代码：-fPIC

## 性能优化

### 编译时优化
- 链接时优化（LTO）
- Profile Guided Optimization（PGO）
- 向量化指令使用

### 运行时优化
- 内存池管理
- CPU 特性检测
- JIT 编译（部分库支持）

## 安全考虑

### 安全更新
- 定期更新安全补丁
- 监控 CVE 数据库
- 使用 FIPS 认证版本（如需要）

### 安全配置
- 安全的默认设置
- 加密算法选择
- 证书验证

## 许可证

### 主要许可证类型
- Apache 2.0 - 大多数新库
- BSD 3-Clause - 系统库
- MIT - 轻量级工具库
- GPL - 某些受限库（在 restricted 目录）

### 许可证合规
- 自动化许可证检查
- 依赖审计
- 法律审查

## 维护指南

### 添加新库
1. 评估许可证兼容性
2. 创建子目录
3. 添加构建脚本
4. 更新 CMakeLists.txt
5. 编写测试用例
6. 更新文档

### 更新现有库
1. 检查版本兼容性
2. 测试新版本
3. 更新构建配置
4. 运行回归测试
5. 提交变更

### 移除库
1. 检查依赖关系
2. 移除代码
3. 更新文档
4. 清理构建配置

## 故障排除

### 常见问题
1. **编译错误**
   - 检查编译器版本
   - 验证依赖关系
   - 清理构建缓存

2. **链接错误**
   - 检查库路径
   - 验证符号导出
   - 检查 ABI 兼容性

3. **运行时错误**
   - 检查库版本匹配
   - 验证运行时路径
   - 调试符号问题

### 调试技巧
- 使用详细构建输出
- 检查中间文件
- 使用调试器
- 启用诊断日志

## 联系信息

如有关于第三方库的问题：
- 提交 Issue 到 GitHub
- 发送邮件到维护团队
- 查看文档和 FAQ

## 资源链接
- [Protocol Buffers 官方文档](https://developers.google.com/protocol-buffers)
- [gRPC 官方文档](https://grpc.io/docs/)
- [OpenSSL 官方网站](https://www.openssl.org/)
- [Apache Arrow 文档](https://arrow.apache.org/docs/)