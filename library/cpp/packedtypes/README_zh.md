# Packed Types 紧凑数据类型库

## 项目概述

Packed Types 是一个专门用于紧凑数据表示的 C++ 库，提供了多种高效的数值编码和解码方案。该库主要用于数据存储、网络传输和内存优化，通过特殊的编码方式减少数据占用的空间。

### 核心功能
- **紧凑浮点数编码**：高效的浮点数压缩表示
- **变长整数编码**：可变长度的整数编码方案
- **ZigZag 编码**：有符号整数的压缩编码
- **定点数表示**：高精度的定点数运算
- **序列化优化**：针对序列化场景的优化

## 文件说明

### 核心头文件
- **packedfloat.h/packedfloat.cpp** - 紧凑浮点数编码
- **longs.h/longs.cpp** - 变长整数编码实现
- **zigzag.h** - ZigZag 编码方案
- **fixed_point.h** - 定点数表示

### 测试文件
- **packedfloat_ut.cpp** - 紧凑浮点数测试
- **longs_ut.cpp** - 变长整数测试
- **zigzag_ut.cpp** - ZigZag 编码测试
- **packed_ut.cpp** - 综合测试

## 使用示例

### 紧凑浮点数编码
```cpp
#include <library/cpp/packedtypes/packedfloat.h>

void PackedFloatExample() {
    float value = 3.14159f;

    // 编码为紧凑表示
    ui32 packed = PackFloat(value);

    // 解码还原
    float unpacked = UnpackFloat(packed);

    printf("Original: %f\n", value);
    printf("Packed: %u\n", packed);
    printf("Unpacked: %f\n", unpacked);
}
```

### 变长整数编码
```cpp
#include <library/cpp/packedtypes/longs.h>

void VarIntExample() {
    ui64 value = 123456789012345ULL;

    // 计算编码后的字节长度
    size_t encodedSize = GetVarIntSize(value);

    // 编码到缓冲区
    char buffer[10];
    size_t bytesWritten = WriteVarInt(buffer, value);

    // 从缓冲区解码
    ui64 decoded;
    size_t bytesRead = ReadVarInt(buffer, &decoded);

    printf("Original: %llu\n", value);
    printf("Encoded size: %zu bytes\n", encodedSize);
    printf("Decoded: %llu\n", decoded);
}
```

### ZigZag 编码
```cpp
#include <library/cpp/packedtypes/zigzag.h>

void ZigZagExample() {
    i32 value = -123;

    // ZigZag 编码
    ui32 encoded = ZigZagEncode32(value);

    // ZigZag 解码
    i32 decoded = ZigZagDecode32(encoded);

    printf("Original: %d\n", value);
    printf("ZigZag encoded: %u\n", encoded);
    printf("ZigZag decoded: %d\n", decoded);
}
```

## 实现原理

### 变长整数编码
- **字节表示**：每个字节使用 7 位表示数值，1 位作为标志位
- **高位标志**：最高位表示是否还有后续字节
- **小端编码**：低位字节在前，高位字节在后

### ZigZag 编码
- **符号映射**：将有符号整数映射为无符号整数
- **绝对值优化**：小数值的绝对值占用更少空间
- **对称编码**：正数和负数对称分布

### 浮点数压缩
- **指数优化**：对浮点数的指数部分进行优化
- **尾数压缩**：根据精度要求压缩尾数部分
- **特殊值处理**：特殊处理 0、无穷大和 NaN

## 应用场景

### 数据存储
- **数据库索引**：紧凑的索引存储
- **文件格式**：高效的数据文件格式
- **内存映射**：减少内存占用
- **缓存优化**：提高缓存命中率

### 网络传输
- **协议优化**：减少网络传输量
- **序列化**：高效的序列化方案
- **RPC 通信**：减少通信开销
- **流式传输**：优化流式数据处理

### 嵌入式系统
- **资源受限**：内存和存储受限的环境
- **实时系统**：快速编码解码操作
- **传感器数据**：传感器数据的压缩存储
- **IoT 设备**：物联网设备的数据处理

## 性能特性

### 空间效率
- **小整数优化**：小整数占用更少字节
- **浮点数压缩**：浮点数的高效压缩
- **内存对齐**：优化的内存布局
- **缓存友好**：提高缓存访问效率

### 时间效率
- **快速编码**：优化的编码算法
- **快速解码**：高效的解码路径
- **分支优化**：减少条件分支
- **SIMD 优化**：向量化操作支持

## 最佳实践

### 选择合适的编码
- **数据特征分析**：根据数据分布选择编码
- **性能测试**：实际测试编码效果
- **空间时间权衡**：平衡空间和时间效率
- **兼容性考虑**：考虑解码端的兼容性

### 错误处理
- **边界检查**：检查编码边界
- **溢出处理**：处理数值溢出情况
- **错误恢复**：提供错误恢复机制
- **调试支持**：提供调试信息