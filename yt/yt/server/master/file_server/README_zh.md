# File Server 组件

## 概述

File Server 是 YTsaurus 系统中负责管理文件对象（File Node）的组件。它提供了在 YTsaurus 中存储和管理二进制文件的能力，支持大文件存储、完整性校验、元数据管理等功能。File Server 构建在 Chunk Server 之上，将文件切分成多个 Chunk 进行存储，实现高效的分布式文件存储。

## 核心功能

### 1. 文件存储
- **大文件支持**: 支持存储 GB 甚至 TB 级别的文件
- **分块存储**: 自动将大文件切分成多个 Chunk 存储
- **流式上传**: 支持流式上传大文件，减少内存占用
- **断点续传**: 支持上传中断后的断点续传

### 2. 完整性保证
- **MD5 校验**: 支持 MD5 哈希校验确保数据完整性
- **校验和验证**: 每个 Chunk 都有校验和
- **数据修复**: 自动检测和修复损坏的数据
- **版本控制**: 支持文件的版本管理

### 3. 元数据管理
- **文件属性**: 管理文件的大小、创建时间、修改时间等
- **MIME 类型**: 支持文件的 MIME 类型识别
- **自定义属性**: 支持用户自定义属性
- **访问控制**: 继承 Cypress 的访问控制机制

### 4. 优化特性
- **压缩支持**: 支持文件压缩存储
- **重复检测**: 检测和去重相同内容的文件
- **缓存优化**: 智能缓存热点文件
- **预取策略**: 预取相关文件提高访问速度

## 关键组件

### File Node (file_node.h/cpp)
- 文件节点的核心实现
- 继承自 ChunkOwnerBase，管理文件的 Chunk
- 实现 MD5 哈希计算
- 支持文件上传和下载操作

### File Node Proxy (file_node_proxy.h/cpp)
- 文件节点的代理实现
- 提供 RPC 接口供客户端访问
- 处理文件操作请求（上传、下载、删除等）
- 实现访问控制和安全检查

### File Node Type Handler (file_node_type_handler.h/cpp)
- 文件节点的类型处理器
- 管理 File Node 的生命周期
- 处理节点的创建、删除和修改
- 提供类型特定的操作接口

## 文件说明

### 核心实现文件
- `file_node.cpp/h`: 文件节点核心实现
- `file_node_proxy.cpp/h`: 文件节点代理，处理 RPC 请求
- `file_node_type_handler.cpp/h`: 文件节点类型处理器

### 公共和私有定义
- `public.h/cpp`: 公共接口定义
- `private.h`: 私有定义和常量

## 使用方法

### 创建文件
```cpp
// 创建文件节点
auto fileNode = fileServer->CreateFileNode(
    parentPath,
    fileName,
    transaction
);

// 设置文件属性
fileNode->SetMimeType("application/octet-stream");
fileNode->SetCompressionCodec("lz4");

// 开始上传
auto uploadContext = fileNode->BeginUpload();
```

### 上传文件
```cpp
// 初始化上传
auto uploadContext = fileNode->BeginUpload();

// 分块上传数据
for (const auto& chunk : fileChunks) {
    fileNode->UploadChunk(chunk);
}

// 完成上传
fileNode->EndUpload(uploadContext);

// 验证完整性
auto md5Hash = fileNode->GetMD5Hash();
```

### 下载文件
```cpp
// 获取文件信息
auto fileInfo = fileNode->GetFileInfo();

// 获取文件 Chunk 列表
auto chunks = fileNode->GetChunks();

// 下载并重组文件
for (const auto& chunk : chunks) {
    auto data = chunkServer->ReadChunk(chunk);
    fileData.append(data);
}
```

### 文件操作
```cpp
// 获取文件属性
auto size = fileNode->GetSize();
auto mimeType = fileNode->GetMimeType();
auto compressedSize = fileNode->GetCompressedSize();

// 检查完整性
auto isValid = fileNode->ValidateChecksum();

// 删除文件
cypressManager->RemoveNode(fileNode);
```

## 配置参数

### File Server 配置
```yaml
file_server:
  enable_md5_verification: true
  default_compression_codec: "none"
  max_file_size: 10TB
  chunk_size: 64MB

upload:
  chunk_size: 64MB
  max_concurrent_uploads: 10
  temp_directory: "/tmp/yt_uploads"
  retry_count: 3

download:
  enable_caching: true
  cache_size: 1GB
  prefetch_enabled: true
  prefetch_window: 2
```

### 完整性配置
```yaml
integrity:
  checksum_type: "crc32c"
  md5_verification: true
  auto_repair: true
  verify_on_upload: true

compression:
  enabled_codecs:
    - "none"
    - "lz4"
    - "zstd"
  default_level: 3
  max_level: 9
```

## 实现原理

### 文件分块
1. **切分算法**: 固定大小切分，最后一块可能小于标准大小
2. **Chunk 映射**: 维护文件到 Chunk 的映射关系
3. **元数据存储**: 存储 Chunk 位置和顺序信息
4. **重组逻辑**: 下载时按顺序重组 Chunk

### 上传流程
1. **初始化**: 创建文件节点，分配元数据
2. **分块上传**: 并行上传多个 Chunk
3. **校验验证**: 验证每个 Chunk 的完整性
4. **完成提交**: 更新元数据，使文件可见

### 下载流程
1. **查询元数据**: 获取文件 Chunk 列表
2. **并行下载**: 并行下载多个 Chunk
3. **重组数据**: 按 Chunk 顺序重组文件
4. **验证完整性**: 验证文件完整性

## 性能优化

### 上传优化
- **并行上传**: 多个 Chunk 并行上传
- **流水线处理**: 上传和压缩流水线
- **压缩优化**: 智能选择压缩算法
- **批量操作**: 批量处理小文件

### 下载优化
- **并行下载**: 并行下载多个 Chunk
- **预取策略**: 预取后续 Chunk
- **缓存**: 缓存热点文件
- **本地缓存**: 客户端本地缓存

### 存储优化
- **重复检测**: 检测重复内容
- **增量存储**: 增量更新文件
- **压缩存储**: 压缩减少存储空间
- **归档**: 冷数据归档

## 监控和调试

### 关键指标
- 文件总数和总大小
- 上传/下载 QPS 和延迟
- 压缩率和存储效率
- 完整性校验统计

### 调试命令
```bash
# 查看文件信息
yt get //path/to/file

# 获取文件属性
yt get //path/to/file/@{size,mime_type,md5}

# 上传文件
yt upload local_file.txt //remote/path/file.txt

# 下载文件
yt download //remote/path/file.txt local_file.txt

# 验证文件完整性
yt verify //path/to/file
```

### 性能分析
```bash
# 查看上传统计
yt get //sys/file_server/@upload_stats

# 查看下载统计
yt get //sys/file_server/@download_stats

# 查看存储统计
yt get //sys/file_server/@storage_stats
```

## 故障处理

### 常见问题
1. **上传失败**: 检查网络连接和存储空间
2. **完整性错误**: 重新上传或触发修复
3. **权限错误**: 检查访问权限配置
4. **空间不足**: 清理无用文件

### 恢复机制
- **自动重试**: 临时故障自动重试
- **断点续传**: 中断后继续上传/下载
- **数据修复**: 自动修复损坏数据
- **备份恢复**: 从备份恢复文件

## 安全考虑

### 数据安全
- **访问控制**: 基于权限的访问控制
- **传输加密**: HTTPS/TLS 传输加密
- **存储加密**: 可选的存储加密
- **完整性保护**: 校验和和哈希保护

### 运行时安全
- **输入验证**: 严格的文件名验证
- **资源限制**: 防止资源耗尽攻击
- **审计日志**: 记录所有文件操作
- **病毒扫描**: 可选的病毒扫描集成

## 最佳实践

### 文件组织
- **合理命名**: 使用有意义的文件名
- **目录结构**: 合理组织目录层次
- **版本管理**: 使用版本控制管理文件版本
- **生命周期**: 设置文件的生命周期策略

### 性能建议
- **文件大小**: 避免过多的小文件
- **压缩**: 对文本文件启用压缩
- **批量操作**: 批量处理多个文件
- **缓存策略**: 合理设置缓存策略

### 存储建议
- **定期清理**: 定期清理临时和过期文件
- **监控使用**: 监控存储空间使用
- **备份策略**: 制定文件备份策略
- **归档策略**: 对冷数据进行归档

## 相关文档
- [文件存储设计](../../../docs/file-storage.md)
- [上传下载指南](../../../docs/file-upload-download.md)
- [数据完整性文档](../../../docs/data-integrity.md)