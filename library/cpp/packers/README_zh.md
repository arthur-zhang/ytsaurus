# Packers 序列化打包库

## 项目概述

Packers 是一个高效的序列化和数据打包库，提供了多种数据格式的编码和解码功能。该库专注于高性能的数据序列化，支持 Protobuf、内存区域等多种数据结构的处理。

### 核心功能
- **Protobuf 打包**：高效的 Protobuf 消息序列化
- **内存区域打包**：内存区域数据的压缩打包
- **二进制序列化**：高效的二进制数据编码
- **流式处理**：支持流式数据处理
- **压缩优化**：内置数据压缩支持

## 文件说明

### 核心文件
- **packers.h/packers.cpp** - 主要打包器实现
- **proto_packer.h/proto_packer.cpp** - Protobuf 消息打包器
- **region_packer.h/region_packer.cpp** - 内存区域打包器

### 测试文件
- **ut/packers_ut.cpp** - 主要打包器测试
- **ut/proto_packer_ut.cpp** - Protobuf 打包器测试
- **ut/region_packer_ut.cpp** - 区域打包器测试

## 使用示例

### 基础数据打包
```cpp
#include <library/cpp/packers/packers.h>

void BasicPackingExample() {
    TBufferOutput output;
    TPacker packer(output);

    // 打包不同类型的数据
    packer.PackInt32(42);
    packer.PackString("Hello, World!");
    packer.PackDouble(3.14159);

    // 获取打包后的数据
    TBlob packedData = output.Blob();
}
```

### Protobuf 消息打包
```cpp
#include <library/cpp/packers/proto_packer.h>
#include "your_proto.pb.h"

void ProtobufPackingExample() {
    YourMessage message;
    message.set_id(123);
    message.set_name("Example");

    // 创建 Proto 打包器
    TBufferOutput output;
    TProtoPacker packer(output);

    // 打包 Protobuf 消息
    packer.PackMessage(message);

    // 获取打包数据
    TBlob packedData = output.Blob();

    // 解包
    TBufferInput input(packedData);
    TProtoUnpacker unpacker(input);
    YourMessage unpackedMessage;
    unpacker.UnpackMessage(&unpackedMessage);
}
```

### 内存区域打包
```cpp
#include <library/cpp/packers/region_packer.h>

void RegionPackingExample() {
    TVector<char> data = {/* some data */};
    TRegion region(data.data(), data.size());

    // 创建区域打包器
    TBufferOutput output;
    TRegionPacker packer(output);

    // 打包内存区域
    packer.PackRegion(region);

    // 解包
    TBufferInput input(output.Blob());
    TRegionUnpacker unpacker(input);
    TRegion unpackedRegion = unpacker.UnpackRegion();
}
```

## 实现原理

### 二进制编码
- **类型标记**：为每种数据类型分配标记
- **变长编码**：使用变长编码减少空间占用
- **字节对齐**：优化的内存对齐策略
- **压缩优化**：可配置的数据压缩

### 流式处理
- **增量处理**：支持增量数据打包
- **缓冲管理**：高效的缓冲区管理
- **回滚支持**：支持打包过程回滚
- **验证机制**：内置数据完整性验证

### 性能优化
- **零拷贝**：减少不必要的数据拷贝
- **内存池**：使用内存池减少分配开销
- **SIMD 优化**：向量化数据操作
- **分支预测**：优化分支预测效率

## 应用场景

### 网络通信
- **协议实现**：网络协议的数据打包
- **RPC 框架**：远程过程调用的参数传递
- **消息队列**：消息队列的数据序列化
- **实时通信**：实时数据的快速序列化

### 数据存储
- **文件格式**：自定义文件格式的数据存储
- **数据库存储**：数据库记录的序列化
- **缓存系统**：缓存数据的压缩存储
- **日志系统**：日志数据的高效存储

### 分布式系统
- **数据同步**：节点间的数据同步
- **状态复制**：系统状态的复制传输
- **负载均衡**：负载数据的打包传输
- **集群通信**：集群节点间的通信

## 性能特性

### 序列化性能
- **高速编码**：微秒级的数据编码
- **高速解码**：高效的数据解码路径
- **内存效率**：低内存占用和高缓存命中率
- **CPU 效率**：优化的 CPU 使用率

### 空间效率
- **紧凑编码**：高度紧凑的数据表示
- **压缩支持**：可选的数据压缩功能
- **元数据优化**：最小化元数据开销
- **重复数据优化**：重复数据的去重

## 最佳实践

### 性能优化
- **批量操作**：批量处理多个数据项
- **预分配缓冲区**：预先分配足够大的缓冲区
- **复用打包器**：复用打包器对象减少分配
- **避免小对象**：减少频繁的小对象创建

### 错误处理
- **版本兼容**：处理不同版本的兼容性
- **边界检查**：检查数据边界和长度
- **异常安全**：保证异常情况下的安全性
- **资源管理**：正确管理内存资源

### 调试支持
- **调试信息**：提供详细的调试信息
- **数据验证**：验证打包和解包的数据一致性
- **性能监控**：监控打包和解包的性能
- **日志记录**：记录关键操作和错误