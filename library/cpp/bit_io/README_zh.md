# bit_io - 高性能位级 I/O 库

## 概述

bit_io 是一个高性能的位级输入输出库，专门用于处理非字节对齐的数据。该库提供了高效的位读写操作，支持任意位数的读写，特别适用于压缩算法、编码器和数据压缩场景。

## 核心特性

### 1. 高性能位操作
- **未对齐内存访问**：使用 ReadUnaligned 快速读取位数据
- **编译时优化**：模板参数支持编译时确定位数
- **位级精度**：支持 1-64 位的任意位数操作
- **批量处理**：优化的位读写操作，减少函数调用开销

### 2. 灵活的输入输出
- **多种输入源**：支持 vector、数组、指针等多种输入
- **流式输出**：支持向流中写入位数据
- **缓冲管理**：自动管理内部缓冲区
- **偏移跟踪**：精确跟踪位和字节偏移

### 3. 安全性保证
- **边界检查**：自动检测并处理缓冲区越界
- **溢出保护**：防止读取超出数据范围
- **错误处理**：提供 EOF 检测和错误状态

## 文件说明

### 核心组件
- **bitinput.h/.cpp**：位输入接口
  - `TBitInput`：位读取器类
  - 支持模板化编译时优化
  - 提供安全的位读取操作

- **bitoutput.h/.cpp**：位输出接口
  - `TBitOutputBase`：位写入器基类
  - 支持流式写入和缓冲
  - 优化的写入性能

### 实现细节
- **bitinput_impl.h/.cpp**：位输入实现
  - 底层的位读取逻辑
  - 处理内存对齐和边界情况
  - 优化的位掩码操作

## 使用示例

### 基本位读取

```cpp
#include <library/cpp/bit_io/bitinput.h>
#include <vector>

// 创建位输入流
std::vector<char> data = {0x12, 0x34, 0x56, 0x78};
NBitIO::TBitInput input(data);

// 读取固定位数（编译时优化）
ui32 value;
if (input.ReadK<12>(value)) {  // 读取12位
    // 处理值
}

// 读取可变位数
ui64 result;
if (input.ReadSafe(result, 20)) {  // 读取20位
    // 处理结果
}

// 检查EOF
if (input.Eof()) {
    // 到达数据末尾
}
```

### 基本位写入

```cpp
#include <library/cpp/bit_io/bitoutput.h>
#include <util/stream/file.h>

// 写入文件
TFileOutput file("output.bin");
NBitIO::TBitOutputBase<decltype(&file)> output(&file);

// 写入位数据
output.Write(0x123, 12);  // 写入低12位
output.Write(0x456, 16);  // 写入低16位

// 写入字序列（带标志位）
ui64 data = 0x12345678;
output.WriteWords<7>(data);  // 按7位分块写入

// 刷新缓冲区
ui64 paddedBits = output.Flush();
```

### 压缩算法应用

```cpp
// 示例：简单的变长整数编码
void WriteVarInt(NBitIO::TBitOutputBase* output, ui64 value) {
    if (value < 0x80) {
        output->Write(value, 8);  // 1字节
    } else if (value < 0x4000) {
        output->Write(0x80, 2);   // 标志位
        output->Write(value, 14); // 2字节
    } else {
        output->Write(0xC0, 2);   // 标志位
        output->Write(value, 30); // 4字节
    }
}

ui64 ReadVarInt(NBitIO::TBitInput* input) {
    ui64 marker;
    input->ReadK<2>(marker);

    if (marker == 0) {  // 00
        ui64 value;
        input->ReadK<6>(value);
        return value;
    } else if (marker == 2) {  // 10
        ui64 value;
        input->ReadK<14>(value);
        return value;
    } else {  // 11
        ui64 value;
        input->ReadK<30>(value);
        return value;
    }
}
```

### 位标志处理

```cpp
// 处理位标志
struct Flags {
    bool FlagA : 1;
    bool FlagB : 1;
    bool FlagC : 1;
    ui8 Value : 5;
};

void SerializeFlags(NBitIO::TBitOutputBase* output, const Flags& f) {
    output->Write(f.FlagA, 1);
    output->Write(f.FlagB, 1);
    output->Write(f.FlagC, 1);
    output->Write(f.Value, 5);
}

Flags DeserializeFlags(NBitIO::TBitInput* input) {
    Flags f;
    input->ReadK<1>(f.FlagA);
    input->ReadK<1>(f.FlagB);
    input->ReadK<1>(f.FlagC);
    input->ReadK<5>(f.Value);
    return f;
}
```

## 性能优化

### 1. 编译时优化
```cpp
// 使用模板参数在编译时确定位数
template <ui32 Bits>
void ReadFixed(NBitIO::TBitInput* input, ui32& value) {
    input->ReadK<Bits>(value);  // 编译器优化
}

// 而不是运行时
void ReadVariable(NBitIO::TBitInput* input, ui32& value, ui32 bits) {
    input->ReadSafe(value, bits);  // 运行时检查
}
```

### 2. 批量操作
```cpp
// 批量读取
std::vector<ui32> values(1000);
NBitIO::TBitInput input(data);

for (size_t i = 0; i < values.size(); ++i) {
    input->ReadK<20>(values[i]);  // 固定20位
}
```

### 3. 内存对齐
- 库内部处理未对齐访问
- 使用 ReadUnaligned 提高性能
- 自动缓存行对齐优化

## 实现细节

### 位存储格式
```
字节:  [7 6 5 4 3 2 1 0][15 14 13 ... 8][23 ... 16]...
位偏移:  0                8                 16
```

### 读取优化
1. **64位加载**：一次加载8字节
2. **位移操作**：使用位移提取所需位
3. **掩码操作**：快速位掩码
4. **边界预取**：提前处理边界情况

### 写入优化
1. **缓冲累积**：64位缓冲区
2. **批量写入**：满字节后批量写入
3. **延迟刷新**：减少系统调用

## 偏移管理

### 位偏移
```cpp
NBitIO::TBitInput input(data);

// 获取当前字节偏移
ui64 byteOffset = input.GetOffset();

// 获取当前位偏移（0-7）
ui64 bitOffset = input.GetBitOffset();
```

### 写入偏移
```cpp
NBitIO::TBitOutputBase output(&storage);

// 获取当前写入位置
ui64 currentPos = output.GetOffset();

// 获取位偏移
ui64 bitPos = output.GetBitOffset();

// 获取字节余数
ui64 remainder = output.GetByteReminder();
```

## 应用场景

### 1. 压缩算法
- Huffman 编码
- 算术编码
- 行程编码
- LZW 压缩

### 2. 数据编码
- Base64 变种
- 自定义编码
- 协议解析
- 文件格式

### 3. 密码学
- 位级加密
- 流密码
- 密钥派生
- 哈希函数

### 4. 图像/视频处理
- 位图操作
- 像素处理
- 压缩格式
- 颜色编码

## 最佳实践

### 1. 性能考虑
- 使用固定位数时优先使用模板参数
- 批量处理减少函数调用
- 避免频繁的小位读写

### 2. 错误处理
- 总是检查 Read* 的返回值
- 处理 EOF 情况
- 验证输入数据长度

### 3. 内存管理
- 及时刷新写入缓冲区
- 注意对齐要求
- 处理大数据块

### 4. 可移植性
- 注意字节序问题
- 测试不同平台
- 验证边界情况

## 注意事项

1. 最多支持64位操作
2. 写入后必须调用 Flush()
3. 读取失败时不会自动恢复位置
4. 大端小端由平台决定
5. 未对齐访问在某些架构可能较慢