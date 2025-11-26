# archive

高效的压缩存档库，提供了创建和读取压缩存档文件的功能，支持多种压缩算法。

## 功能描述

该模块提供了一个完整的存档系统，能够将多个文件和数据流压缩打包到一个存档文件中，并支持高效的随机访问和索引查找。

## 核心特性

- **压缩支持**：可选的数据压缩功能，显著减少存储空间
- **快速访问**：支持按键名快速定位和提取文件
- **同义词支持**：允许为一个文件创建多个访问键名
- **内存效率**：优化的内存使用和流式处理
- **跨平台**：支持多种操作系统和架构

## 主要组件

### TArchiveWriter
存档写入器，用于创建压缩存档：
- `Add(key, src)` - 添加文件到存档
- `AddSynonym(existingKey, newKey)` - 为已有文件添加别名
- `Flush()` - 刷新缓冲区
- `Finish()` - 完成存档创建

### TArchiveReader
存档读取器，用于读取压缩存档：
- `Count()` - 获取存档中文件数量
- `KeyByIndex(n)` - 按索引获取文件名
- `Has(key)` - 检查文件是否存在
- `ObjectByKey(key)` - 获取文件输入流
- `ObjectBlobByKey(key)` - 获取文件数据块

### TDirectoryModelsArchiveReader
目录模型的存档读取器实现：
- 支持从文件系统目录读取模型文件
- 提供统一的存档接口
- 适用于机器学习模型管理

## 使用示例

### 创建存档
```cpp
#include <library/cpp/archive/yarchive.h>

// 创建存档写入器
TArchiveWriter writer(&outputStream, true); // 启用压缩

// 添加文件
writer.Add("model.bin", &modelStream);
writer.Add("config.json", &configStream);

// 添加同义词
writer.AddSynonym("model.bin", "latest_model");

// 完成创建
writer.Finish();
```

### 读取存档
```cpp
// 创建存档读取器
TArchiveReader reader(archiveBlob);

// 检查文件存在性
if (reader.Has("model.bin")) {
    // 获取文件流
    auto stream = reader.ObjectByKey("model.bin");
    // 处理文件内容...
}

// 遍历所有文件
for (size_t i = 0; i < reader.Count(); ++i) {
    TString key = reader.KeyByIndex(i);
    auto blob = reader.ObjectBlobByKey(key);
    // 处理文件...
}
```

## 压缩算法

- 支持多种压缩算法（通过配置选择）
- 默认使用高效的压缩算法
- 可根据数据特征选择最优压缩方式

## 内存管理

- **流式处理**：支持大文件的流式读写
- **内存映射**：对某些格式使用内存映射提高性能
- **缓冲优化**：智能缓冲策略平衡内存和性能

## 应用场景

- 机器学习模型存储和分发
- 软件包管理和部署
- 备份和归档系统
- 资源文件打包（游戏、应用等）
- 数据传输和同步

## 性能特点

- **高压缩比**：相比简单文件合并节省大量空间
- **快速随机访问**：O(1) 复杂度的文件查找
- **低内存占用**：流式处理避免大内存分配
- **并发安全**：支持多线程读取

## 文件格式

存档文件采用二进制格式，包含：
- 文件头信息
- 压缩元数据
- 文件索引表
- 压缩的数据块