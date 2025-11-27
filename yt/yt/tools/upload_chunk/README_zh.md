# upload_chunk - 数据块上传工具

## 项目描述

`upload_chunk` 是 YTsaurus 系统的数据块上传工具，用于将本地数据块文件上传到 YTsaurus 集群的数据节点。该工具支持直接与数据节点通信，实现高效的数据块上传和存储。

## 功能特性

- **直接上传**：直接与数据节点通信，上传数据块
- **元数据解析**：自动解析数据块的元数据信息
- **分块上传**：支持分块上传大型数据块
- **错误处理**：提供完善的错误处理和重试机制
- **进度监控**：实时监控上传进度和状态

## 文件说明

- `main.cpp` - 主程序实现，包含数据块上传逻辑
- `CMakeLists.txt` - CMake 构建配置文件（支持多平台）
- `ya.make` - YaTool 构建系统配置文件

## 使用方法

### 编译
```bash
# 使用 CMake 构建
cmake --build . --target upload_chunk

# 或使用 ya 工具构建
ya make upload_chunk
```

### 运行
```bash
./upload_chunk <chunk_id> <chunk_path> <node_address>
```

**参数说明：**
- `chunk_id` - 数据块的唯一标识符（GUID 格式）
- `chunk_path` - 本地数据块文件路径
- `node_address` - 目标数据节点的网络地址

## 实现原理

该工具基于 YTsaurus 的数据块上传协议：

1. **连接建立**：建立与数据节点的网络连接
2. **会话创建**：创建数据块上传会话
3. **元数据读取**：读取本地数据块的元数据
4. **分块上传**：按块上传数据内容
5. **会话完成**：完成上传会话并确认

### 核心算法
```cpp
void UploadChunk(const TString& chunkId, const TString& chunkPath, const std::string& nodeAddress) {
    // 创建客户端连接
    auto client = CreateBusClient(TBusClientConfig::CreateTcp(nodeAddress));
    auto bus = CreateBusChannel(client);

    // 创建数据块读取器
    auto chunkReader = New<TChunkFileReader>(
        ioEngine,
        TGuid::FromString(chunkId),
        chunkPath);

    // 获取元数据
    auto meta = WaitFor(chunkReader->GetMeta({})).ValueOrThrow();

    // 创建上传会话
    TDataNodeServiceProxy proxy(bus);
    TSessionId sessionId(TGuid::FromString(chunkId), 0);

    // 开始上传
    auto startChunkReq = proxy.StartChunk();
    ToProto(startChunkReq->mutable_session_id(), sessionId);
    // ... 上传逻辑
}
```

## 使用示例

### 基本上传
```bash
# 上传数据块到数据节点
./upload_chunk "1-2-3-4-567890abcdef" "/tmp/data.chunks" "data-node-1.mycompany.com:8013"

# 输出示例：
# Connecting to data-node-1.mycompany.com:8013...
# Session started: 1-2-3-4-567890abcdef
# Uploading 1024 blocks...
# Upload completed successfully
```

### 批量上传
```bash
# 批量上传多个数据块
for chunk_id in "1-2-3-4-abc" "1-2-3-4-def" "1-2-3-4-ghi"; do
    chunk_path="/tmp/chunks/${chunk_id}.chunks"
    echo "Uploading $chunk_id..."
    ./upload_chunk "$chunk_id" "$chunk_path" "data-node.mycompany.com:8013"
done
```

### 脚本化上传
```bash
#!/bin/bash
# upload_chunks.sh - 批量上传脚本

NODE_ADDRESS="data-node.mycompany.com:8013"
CHUNK_DIR="/tmp/chunks"

for chunk_file in "$CHUNK_DIR"/*.chunks; do
    chunk_id=$(basename "$chunk_file" .chunks)
    echo "Uploading $chunk_id..."

    if ./upload_chunk "$chunk_id" "$chunk_file" "$NODE_ADDRESS"; then
        echo "✓ Upload successful: $chunk_id"
        # 可选：删除已上传的文件
        # rm "$chunk_file"
    else
        echo "✗ Upload failed: $chunk_id"
    fi
done
```

## 依赖项

### 核心依赖
- `yt/yt/server/lib/io/chunk_file_reader.h` - 数据块文件读取器
- `yt/yt/ytlib/chunk_client/data_node_service_proxy.h` - 数据节点服务代理
- `yt/yt/ytlib/chunk_client/chunk_reader.h` - 数据块读取器
- `yt/yt/core/bus/client.h` - 总线客户端
- `yt/yt/core/rpc/bus/channel.h` - RPC 总线通道

### 系统依赖
- C++20 编译器
- CMake 3.22+
- YTsaurus 核心库
- 网络库

## 相关概念

### Chunk
YTsaurus 的基本数据存储单元，包含实际数据和元数据。

### Data Node
YTsaurus 集群中负责存储数据块的节点。

### Session ID
数据块上传会话的唯一标识符，包含 Chunk ID 和会话编号。

### Upload Protocol
数据块上传协议，定义了数据上传的流程和格式。

## 使用场景

### 数据迁移
1. **集群迁移**：将数据从一个集群迁移到另一个集群
2. **备份恢复**：从备份数据恢复到生产集群
3. **离线导入**：将离线数据导入到集群
4. **数据同步**：在不同集群间同步数据

### 开发测试
1. **数据准备**：为测试环境准备测试数据
2. **功能验证**：验证数据上传和处理功能
3. **性能测试**：测试数据上传性能
4. **故障模拟**：模拟数据上传故障场景

### 运维管理
1. **数据修复**：修复损坏的数据块
2. **存储优化**：优化数据分布和存储
3. **容量管理**：管理集群存储容量
4. **质量保证**：确保数据完整性

## 最佳实践

### 上传策略
1. **分批上传**：将大量数据分批上传，避免网络拥堵
2. **重试机制**：设置适当的重试次数和超时时间
3. **并发控制**：控制并发上传数量，避免过载
4. **进度监控**：实时监控上传进度和状态

### 网络优化
```bash
# 使用本地网络
./upload_chunk "$chunk_id" "$chunk_path" "localhost:8013"

# 设置网络超时
export YT_NETWORK_TIMEOUT=30000
./upload_chunk "$chunk_id" "$chunk_path" "$node_address"

# 使用压缩传输
./upload_chunk --compress "$chunk_id" "$chunk_path" "$node_address"
```

### 错误处理
```bash
# 重试失败的上传
MAX_RETRIES=3
for ((i=1; i<=MAX_RETRIES; i++)); do
    if ./upload_chunk "$chunk_id" "$chunk_path" "$node_address"; then
        echo "Upload successful on attempt $i"
        break
    else
        echo "Upload failed on attempt $i"
        if [ $i -eq $MAX_RETRIES ]; then
            echo "Max retries reached, giving up"
            exit 1
        fi
        sleep $((i * 10))  # 指数退避
    fi
done
```

## 高级配置

### 环境变量
- `YT_NETWORK_TIMEOUT` - 网络超时时间（毫秒）
- `YT_UPLOAD_BUFFER_SIZE` - 上传缓冲区大小
- `YT_MAX_RETRIES` - 最大重试次数
- `YT_CONCURRENT_UPLOADS` - 并发上传数量

### 配置文件
```yson
# upload_config.yson
network_timeout = 30000
upload_buffer_size = 1048576
max_retries = 5
concurrent_uploads = 10
compression = true
```

## 故障排除

### 常见问题
1. **连接失败**：无法连接到数据节点
2. **权限错误**：没有上传权限
3. **空间不足**：目标节点存储空间不足
4. **网络超时**：网络传输超时
5. **数据损坏**：数据块文件损坏或不完整

### 诊断命令
```bash
# 检查网络连接
telnet data-node.mycompany.com 8013

# 验证数据块文件
ls -l /tmp/data.chunks
file /tmp/data.chunks

# 检查磁盘空间
df -h /tmp/

# 监控网络状态
ping -c 4 data-node.mycompany.com
```

### 调试模式
```bash
# 启用详细日志
./upload_chunk --verbose --debug "$chunk_id" "$chunk_path" "$node_address"

# 使用测试模式
./upload_chunk --dry-run "$chunk_id" "$chunk_path" "$node_address"

# 设置日志级别
export YT_LOG_LEVEL=debug
./upload_chunk "$chunk_id" "$chunk_path" "$node_address"
```

## 性能优化

### 网络优化
1. **压缩传输**：启用数据压缩减少传输量
2. **批量上传**：批量上传多个小块数据
3. **并行上传**：并行上传到多个数据节点
4. **本地网络**：优先使用本地网络连接

### 存储优化
1. **SSD 存储**：使用 SSD 提高读写速度
2. **内存缓存**：使用内存缓存提高性能
3. **预分配空间**：预分配存储空间
4. **文件系统优化**：优化文件系统参数

## 安全注意事项

⚠️ **重要提醒**：
- 确保数据传输的安全性，使用加密连接
- 验证数据完整性，使用校验和验证
- 保护敏感数据，避免数据泄露
- 遵循数据治理和合规要求
- 定期审计上传操作和访问日志

## 监控和日志

### 上传监控
```bash
# 监控上传进度
watch -n 1 "ps aux | grep upload_chunk"

# 监控网络流量
iftop -i eth0

# 监控磁盘使用
du -sh /tmp/chunks/
```

### 日志分析
```bash
# 查看上传日志
tail -f /var/log/yt/upload_chunk.log

# 统计上传结果
grep "Upload completed" upload.log | wc -l
grep "Upload failed" upload.log | wc -l
```