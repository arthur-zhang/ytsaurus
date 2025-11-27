# Data Node RPC Request

## 项目描述

Data Node RPC Request 是一个专业的测试和调试工具，用于直接向 YTsaurus 数据节点（Data Node）发送 RPC 请求。该工具支持多种数据操作请求类型，主要用于性能测试、问题诊断和数据分析等场景。它能够绕过上层架构，直接与数据节点通信，提供更精细的控制和更详细的调试信息。

## 功能特性

- **直接通信**：绕过中间层，直接与数据节点通信
- **多种请求类型**：支持 LookupRows 和 GetChunkFragmentSet 等请求
- **灵活配置**：丰富的命令行参数支持各种测试场景
- **详细输出**：提供完整的请求和响应信息
- **性能测试**：支持高并发请求测试

## 支持的请求类型

### 1. LookupRows（行查找）
- 根据 key 值查找表中的行
- 支持表模式验证
- 返回完整的行数据

### 2. GetChunkFragmentSet（块片段集获取）
- 获取数据块的特定片段
- 支持 Direct I/O 模式
- 精确控制读取位置和长度

## 文件说明

- `main.cpp` - 主程序源代码，实现 RPC 请求客户端
- `ya.make` - 构建配置文件
- `CMakeLists.*.txt` - CMake 构建配置文件

## 使用方法

### 编译

```bash
# 使用 ya 工具构建
ya make -t data_node_rpc_request

# 或使用 CMake 构建
cmake --build . --target data_node_rpc_request
```

### 命令行参数

#### 通用参数
- `--data-node-request` - 请求类型（LookupRows 或 GetChunkFragmentSet）
- `--host-address` - 数据节点地址（格式：host:port）
- `--chunk-id` - 数据块 ID

#### LookupRows 专用参数
- `--key` - 查询的 key 值（单个 int64 值）
- `--table-id` - 表 ID
- `--table-revision` - 表挂载版本号
- `--table-schema` - 表模式（YSON 格式）

#### GetChunkFragmentSet 专用参数
- `--read-session-id` - 读取会话 ID
- `--use-direct-io` - 是否使用 Direct I/O
- `--fragment-length` - 片段长度
- `--block-index` - 块索引
- `--block-offset` - 块内偏移

### 使用示例

#### LookupRows 示例

```bash
./data_node_rpc_request \
    --data-node-request LookupRows \
    --host-address node1.ytsaurus:9012 \
    --chunk-id 12345678-1234-1234-1234-123456789abc \
    --key 42 \
    --table-id 87654321-4321-4321-4321-cba987654321 \
    --table-revision 100 \
    --table-schema "[{name=id;type=int64;sort_order=ascending}]"
```

#### GetChunkFragmentSet 示例

```bash
./data_node_rpc_request \
    --data-node-request GetChunkFragmentSet \
    --host-address node1.ytsaurus:9012 \
    --chunk-id 12345678-1234-1234-1234-123456789abc \
    --read-session-id abcdef01-2345-6789-abcd-ef0123456789 \
    --use-direct-io \
    --fragment-length 4096 \
    --block-index 0 \
    --block-offset 1024
```

## 实现原理

### 核心架构

1. **RPC 客户端**：基于 YTsaurus RPC 框架
2. **请求构建**：根据参数构建不同类型的请求
3. **协议处理**：处理 WireProtocol 数据序列化
4. **响应解析**：解析服务器响应并格式化输出

### 数据流程

```
命令行参数 → RPC 请求构建 → 数据节点 → 响应解析 → 输出结果
```

### 关键组件

- `TDataNodeServiceProxy` - 数据节点服务代理
- `TWireProtocolWriter` - 协议数据写入器
- `TWireProtocolReader` - 协议数据读取器
- `TRowBuffer` - 行数据缓冲区

## 高级用法

### 批量测试

可以编写脚本进行批量测试：

```bash
#!/bin/bash

for key in {1..100}; do
    echo "Testing key: $key"
    ./data_node_rpc_request \
        --data-node-request LookupRows \
        --host-address node1:9012 \
        --chunk-id $CHUNK_ID \
        --key $key \
        --table-id $TABLE_ID \
        --table-revision 100 \
        --table-schema "$TABLE_SCHEMA"
done
```

### 性能基准测试

使用时间戳测量响应时间：

```bash
start=$(date +%s%N)
./data_node_rpc_request [参数...]
end=$(date +%s%N)
echo "Response time: $(((end-start)/1000000)) ms"
```

## 输出说明

### LookupRows 输出
- `Fetched rows` - 获取的行数
- `Requested schema` - 请求的模式信息
- `Fetched row` - 实际获取的行数据（详细信息）

### GetChunkFragmentSet 输出
- 请求状态和错误信息
- 数据片段相关信息
- I/O 操作统计

## 注意事项

### 使用限制

- 需要 Data Node 服务运行并可访问
- Chunk ID 必须存在且有效
- 网络连接需要稳定

### 性能考虑

- Direct I/O 可以提高大块读取性能
- 合理设置请求大小避免超时
- 批量请求时控制并发数

### 安全性

- 工具主要用于测试和调试
- 生产环境使用需谨慎
- 确保网络安全和访问控制

## 故障排除

### 常见错误

1. **连接失败**
   - 检查主机地址和端口
   - 确认 Data Node 服务状态
   - 检查防火墙设置

2. **无效的 Chunk ID**
   - 验证 Chunk ID 格式
   - 确认 Chunk 存在
   - 检查权限

3. **请求超时**
   - 增加超时时间
   - 检查网络延迟
   - 减小请求大小

### 调试技巧

```bash
# 启用详细日志
export YT_LOG_LEVEL=debug

# 使用 strace 跟踪系统调用
strace -o trace.log ./data_node_rpc_request [参数...]

# 使用 tcpdump 抓包分析
tcpdump -i eth0 host <data_node_ip> and port <port>
```

## 依赖项

- **yt/yt/ytlib/api** - YTsaurus API 客户端
- **yt/yt/ytlib/chunk_client** - 数据块客户端库
- **yt/yt/ytlib/transaction_supervisor** - 事务管理库
- **yt/yt/client/table_client** - 表客户端库
- **yt/yt/client/tablet_client** - Tablet 客户端库
- **yt/yt/core/rpc** - RPC 框架库
- **library/cpp/getopt** - 命令行参数解析库

## 相关概念

- **Data Node** - YTsaurus 存储节点
- **Chunk** - 数据存储单元
- **WireProtocol** - YTsaurus 内部数据传输协议
- **Direct I/O** - 绕过系统缓存的直接 I/O 模式
- **Table Schema** - 表结构定义

## 最佳实践

1. **测试环境准备**
   - 使用专用的测试环境
   - 准备合适的测试数据
   - 配置监控和日志

2. **请求优化**
   - 批量操作提高效率
   - 合理设置读取大小
   - 使用连接池减少开销

3. **结果分析**
   - 记录详细的响应时间
   - 分析错误模式和原因
   - 持续优化测试策略