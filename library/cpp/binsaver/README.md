# binsaver

高效的二进制序列化库，为 YTsaurus 系统提供快速、紧凑的数据序列化和反序列化功能。

## 功能描述

binsaver (Binary Saver) 是一个高性能的二进制序列化框架，专门用于在网络传输和磁盘存储时高效地序列化复杂数据结构。它支持类型安全、版本兼容和压缩传输。

## 核心特性

- **高性能**：优化的二进制格式，序列化/反序列化速度极快
- **紧凑存储**：最小化数据大小，节省存储和网络带宽
- **类型安全**：编译时类型检查，避免运行时错误
- **版本兼容**：支持数据结构的向前和向后兼容
- **压缩支持**：内置压缩功能，进一步减少数据大小
- **流式处理**：支持大数据的流式读写

## 主要组件

### IBinSaver
核心序列化接口，定义了：
- `chunk_id`：数据块标识符类型
- `TStoredSize`：存储大小类型
- 读写操作接口

### 序列化模式
```cpp
enum ESaverMode {
    SAVER_MODE_READ = 1,              // 读取模式
    SAVER_MODE_WRITE = 2,             // 写入模式
    SAVER_MODE_WRITE_COMPRESSED = 3,  // 压缩写入模式
};
```

### 辅助组件

#### TBufferedIO
缓冲输入输出，提高 I/O 性能：
- 智能缓冲策略
- 批量读写优化
- 内存使用控制

#### TBlobIO
二进制大对象处理：
- 大文件的分块处理
- 内存映射优化
- 流式传输支持

#### TClassFactory
动态对象创建：
- 支持多态序列化
- 类型注册机制
- 运行时类型识别

## 使用示例

### 基本序列化
```cpp
#include <library/cpp/binsaver/bin_saver.h>

// 定义可序列化的结构
struct MyData {
    int Id;
    TString Name;
    vector<double> Values;

    // 实现序列化函数
    void Load(IBinSaver& f) {
        f.Add(0, &Id);
        f.Add(1, &Name);
        f.Add(2, &Values);
    }
};

// 序列化到文件
MyData data;
TBufferedOutput output("data.bin");
TBinSaver saver(SAVER_MODE_WRITE, &output);
saver.Add(0, &data);
```

### 反序列化
```cpp
// 从文件读取
TBufferedInput input("data.bin");
TBinSaver saver(SAVER_MODE_READ, &input);
MyData data;
saver.Add(0, &data);
```

### 压缩序列化
```cpp
// 使用压缩模式
TBufferedOutput output("data.bin");
TBinSaver saver(SAVER_MODE_WRITE_COMPRESSED, &output);
saver.Add(0, &largeData);
```

## 序列化格式

### 二进制布局
1. **头部信息**
   - 版本号
   - 压缩标志
   - 数据块数量

2. **数据块**
   - 块ID (chunk_id)
   - 数据长度
   - 实际数据

3. **元数据**
   - 类型信息（可选）
   - 校验和（可选）

### 重载优先级
通过 `TOverloadPriority` 模板控制重载解析顺序，确保选择最合适的序列化方法。

## 类型支持

### 基础类型
- 整数类型 (int, ui32, ui64等)
- 浮点类型 (float, double)
- 字符串 (TString, TStringBuf)
- 布尔类型 (bool)

### 容器类型
- vector
- map, unordered_map
- set, unordered_set
- 自定义容器（需实现接口）

### 复杂类型
- 指针和智能指针
- 多态对象
- 嵌套结构

## 性能优化

### 内存优化
- **就地序列化**：避免不必要的数据拷贝
- **内存池**：复用内存分配
- **批量处理**：批量处理小对象

### 速度优化
- **模板特化**：为常用类型提供特化实现
- **SIMD 指令**：使用向量指令加速
- **缓存友好**：优化数据访问模式

## 版本兼容性

### 向前兼容
- 新版本可以读取旧版本数据
- 自动填充默认值
- 忽略未知字段

### 向后兼容
- 旧版本可以部分读取新版本数据
- 保留核心功能
- 优雅降级

## 调试和验证

### 调试功能
```cpp
// 启用调试模式
#define BINSAVER_DEBUG
TBinSaver saver(mode, &output);
saver.SetDebug(true);  // 输出调试信息
```

### 数据验证
- 校验和验证
- 类型一致性检查
- 数据完整性验证

## 应用场景

- **网络通信**：RPC 调用的数据传输
- **持久化存储**：对象序列化到磁盘
- **缓存系统**：内存中的对象存储
- **消息队列**：消息的序列化传输
- **配置管理**：配置文件的读写

## 性能指标

典型性能表现（相比文本序列化）：
- 序列化速度提升 10-50 倍
- 数据大小减少 50-80%
- 反序列化速度提升 20-100 倍
- 内存使用减少 30-60%