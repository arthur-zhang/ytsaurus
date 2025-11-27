# parse_rpc_header - RPC 头部解析工具

## 项目描述

`parse_rpc_header` 是 YTsaurus 系统的 RPC 协议调试工具，专门用于解析和分析 YTsaurus RPC 消息的头部信息。该工具能够解析十六进制编码的 RPC 消息头部，帮助开发者理解和调试 RPC 通信。

## 功能特性

- **头部解析**：解析 RPC 请求和响应消息头部
- **十六进制输入**：支持十六进制编码的消息数据
- **消息类型识别**：自动识别消息类型（请求/响应/错误）
- **格式化输出**：以可读格式显示解析结果
- **协议分析**：分析 RPC 协议的详细信息

## 文件说明

- `main.cpp` - 主程序实现，包含消息解析逻辑
- `CMakeLists.txt` - CMake 构建配置文件（支持多平台）
- `ya.make` - YaTool 构建系统配置文件

## 使用方法

### 编译
```bash
# 使用 CMake 构建
cmake --build . --target parse_rpc_header

# 或使用 ya 工具构建
ya make parse_rpc_header
```

### 运行
```bash
./parse_rpc_header <hex-message-part>
```

**参数说明：**
- `hex-message-part` - 十六进制编码的消息头部数据

## 实现原理

该工具基于 YTsaurus 的 RPC 协议实现：

1. **消息构建**：将十六进制字符串转换为二进制消息
2. **类型识别**：根据消息特征判断消息类型
3. **头部解析**：解析请求或响应头部
4. **格式化输出**：将解析结果以可读格式输出

### 核心算法
```cpp
// 构建消息
auto message = BuildMessage();
auto messageType = GetMessageType(message);

// 根据类型处理
switch (messageType) {
    case EMessageType::Request:
        // 解析请求头部
        TRequestHeader header;
        TryParseRequestHeader(message, &header);
        break;
    case EMessageType::Response:
        // 解析响应头部
        TResponseHeader header;
        TryParseResponseHeader(message, &header);
        break;
    // ...
}
```

## 使用示例

### 解析请求消息
```bash
./parse_rpc_header "0a04746573741234..."
# 输出：
# Message type:    Request
# Service:        test_service
# Method:         test_method
# ...
```

### 解析响应消息
```bash
./parse_rpc_header "0a056572726f721234..."
# 输出：
# Message type:    Response
# Error:          Operation failed
# ...
```

### 调试应用场景
```bash
# 从网络抓包数据中提取消息头部
tcpdump -i eth0 -w capture.pcap
# 从抓包文件中提取十六进制数据
./parse_rpc_header $(extract_hex_from_pcap capture.pcap)
```

## 依赖项

### 核心依赖
- `yt/yt/library/program/program.h` - 程序框架
- `yt/yt/core/rpc/message.h` - RPC 消息定义
- `yt/yt/core/misc/protobuf_helpers.h` - Protobuf 辅助工具
- `yt/yt_proto/yt/core/rpc/proto/rpc.pb.h` - RPC 协议定义

### 系统依赖
- C++20 编译器
- CMake 3.22+
- YTsaurus 核心库
- Protobuf 库

## 相关概念

### RPC Protocol
YTsaurus 的远程过程调用协议，用于组件间的通信。

### Message Header
RPC 消息的头部，包含服务名、方法名、请求ID 等元信息。

### Message Types
- **Request**: 请求消息
- **Response**: 响应消息
- **Error**: 错误消息

## 使用场景

### 网络调试
1. **协议分析**：分析 YTsaurus 组件间的 RPC 通信
2. **故障排查**：定位网络通信问题
3. **性能分析**：分析 RPC 消息的大小和内容
4. **安全审计**：检查 RPC 消息的内容和格式

### 开发调试
1. **协议测试**：测试新的 RPC 功能
2. **兼容性验证**：验证协议版本的兼容性
3. **消息构造**：构造测试用的 RPC 消息
4. **格式验证**：验证消息格式的正确性

## 最佳实践

### 数据获取
1. **网络抓包**：使用 tcpdump 或 wireshark 抓取网络数据
2. **日志提取**：从系统日志中提取消息数据
3. **文件读取**：从二进制文件中读取消息数据
4. **内存导出**：从内存中导出消息数据

### 调试技巧
```bash
# 管道操作
echo "0a04746573741234" | ./parse_rpc_header

# 批量处理
cat messages.hex | while read line; do
    echo "=== Message: $line ==="
    ./parse_rpc_header "$line"
done

# 详细输出
./parse_rpc_header --verbose message.hex
```

### 结果分析
1. **验证格式**：确认消息格式的正确性
2. **检查内容**：分析消息的内容和结构
3. **对比分析**：对比正常和异常消息的差异
4. **性能评估**：评估消息大小和复杂度

## 故障排除

### 常见问题
1. **格式错误**：输入的十六进制格式不正确
2. **消息损坏**：消息数据不完整或损坏
3. **版本不兼容**：协议版本不兼容
4. **解析失败**：无法识别消息类型或结构

### 错误处理
```bash
# 验证十六进制格式
if echo "$hex_data" | grep -q "[^0-9a-fA-F]"; then
    echo "Invalid hex format"
fi

# 检查消息长度
if [ ${#hex_data} -lt 10 ]; then
    echo "Message too short"
fi
```

## 扩展功能

### 自定义解析器
可以扩展工具以支持特殊的消息格式：

```cpp
// 自定义消息处理
void CustomMessageHandler(const TSharedRef& message) {
    // 自定义解析逻辑
    // 可以添加特定的协议支持
}
```

### 输出格式
除了默认的文本输出外，还可以支持：
- JSON 格式输出
- XML 格式输出
- 结构化数据导出
- 统计信息报告

## 注意事项

⚠️ **重要提醒**：
- 输入数据必须是有效的十六进制格式
- 消息必须是完整的头部数据
- 某些消息可能包含敏感信息，注意数据安全
- 仅用于调试和学习目的，不要用于恶意用途
- 确保遵守相关法律法规和公司政策

## 法律声明

此工具仅用于合法的调试和分析目的。使用者需要确保：
- 拥有对分析数据的合法访问权限
- 遵守相关的法律法规
- 不将工具用于恶意目的
- 保护数据隐私和安全