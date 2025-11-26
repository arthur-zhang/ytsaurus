# archive - 归档文件读写库

## 概述

archive 是一个用于处理模型归档文件的 C++ 库，提供了高效的归档文件创建和读取功能。该库支持压缩存储，特别适用于机器学习模型的存储和管理。

## 核心功能

### 1. 归档文件写入（TArchiveWriter）

提供将多个数据项写入归档文件的功能：
- **数据压缩**：可选择是否压缩存储数据，节省存储空间
- **键值对存储**：通过键值对的方式组织数据
- **同义词支持**：允许为已存在的键创建别名（同义词）
- **流式写入**：支持从输入流直接写入数据
- **内存对齐**：默认16字节对齐，优化访问性能（DEVTOOLS-4384）

### 2. 归档文件读取（TArchiveReader）

提供从归档文件中读取数据的功能：
- **索引访问**：支持通过索引或键名访问数据
- **流式读取**：返回输入流对象，支持大数据的流式处理
- **直接读取**：支持直接读取为 TBlob 对象
- **压缩检测**：可检测归档是否被压缩
- **前缀过滤**：支持按前缀和后缀过滤键名

### 3. 目录归档读取（TDirectoryModelsArchiveReader）

提供从目录结构读取归档数据的功能：
- **目录映射**：将文件系统目录映射为归档结构
- **内存锁定**：可选择是否将数据锁定在内存中
- **所有权管理**：可选择是否拥有数据块的所有权
- **路径规范化**：自动处理路径分隔符和格式

## 文件说明

### 核心头文件
- **yarchive.h**：主要的归档读写功能
  - `TArchiveWriter`：归档写入器类
  - `TArchiveReader`：归档读取器类
- **models_archive_reader.h**：模型归档读取器接口
  - `IModelsArchiveReader`：抽象基类，定义标准接口

### 实现文件
- **yarchive.cpp**：归档读写功能的具体实现
- **models_archive_reader.cpp**：基础读取器实现

### 目录读取器
- **directory_models_archive_reader.h/.cpp**：目录归档读取器实现
- **directory_models_archive_reader_ut.cpp**：单元测试

### 测试文件
- **yarchive_ut.cpp**：主要功能单元测试
- **ut/**：包含更多测试用例

## 使用示例

### 创建归档文件

```cpp
#include "yarchive.h"
#include <util/stream/file.h>

// 创建文件输出流
TFileOutput out("models.archive");

// 创建归档写入器，启用压缩
TArchiveWriter writer(&out, true);

// 添加数据
TStringInput data1("model data 1");
writer.Add("model1", &data1);

TStringInput data2("model data 2");
writer.Add("model2", &data2);

// 添加同义词
writer.AddSynonym("model1", "latest_model");

// 完成写入
writer.Finish();
```

### 读取归档文件

```cpp
#include "yarchive.h"
#include <util/stream/file.h>

// 读取归档文件
TBlob archiveData = TBlob::FromFile("models.archive");
TArchiveReader reader(archiveData);

// 检查键是否存在
if (reader.Has("model1")) {
    // 获取数据流
    auto stream = reader.ObjectByKey("model1");
    // 处理数据...
}

// 获取数据块
TBlob blob = reader.BlobByKey("model2");

// 遍历所有键
for (size_t i = 0; i < reader.Count(); ++i) {
    TString key = reader.KeyByIndex(i);
    // 处理每个键...
}

// 前缀过滤
auto filteredKeys = reader.FilterByPrefix("model", ".bin");
```

### 从目录读取

```cpp
#include "directory_models_archive_reader.h"

// 创建目录读取器
TDirectoryModelsArchiveReader dirReader("/path/to/models");

// 读取数据（与归档文件接口相同）
if (dirReader.Has("model.txt")) {
    TBlob data = dirReader.BlobByKey("model.txt");
}
```

## 实现原理

### 归档格式
- **头部信息**：存储归档元数据（压缩标志、项数量等）
- **索引表**：键名到数据偏移量的映射
- **数据块**：实际存储的数据，可选择压缩

### 压缩机制
- 使用高效的压缩算法减少存储空间
- 支持流式压缩，适合大数据处理
- 压缩标志存储在头部，读取时自动解压

### 内存管理
- 支持内存锁定，防止数据被换出
- 支持所有权转移，优化内存使用
- 使用 TBlob 进行高效的内存块管理

## 应用场景

1. **机器学习模型存储**
   - 保存和加载训练好的模型
   - 模型版本管理
   - 模型参数的批量存储

2. **数据归档系统**
   - 大批量文件的归档存储
   - 数据备份和恢复
   - 数据传输打包

3. **资源管理系统**
   - 游戏资源打包
   - 静态资源管理
   - 配置文件集合

4. **缓存系统**
   - 计算结果缓存
   - 中间数据存储
   - 预处理结果保存

## 性能特征

- **高效压缩**：显著减少存储空间占用
- **快速访问**：通过索引快速定位数据
- **内存优化**：支持流式访问，避免全量加载
- **并发安全**：读取器支持并发访问

## 依赖项

- 核心库：util（基础工具库）
- 内存管理：TBlob、THolder
- 流处理：IInputStream/IOutputStream
- 文件系统：TFile（可选，用于文件操作）

## 注意事项

1. 写入完成后必须调用 `Finish()` 方法
2. 归档文件一旦创建，不能追加内容
3. 大数据建议使用流式接口处理
4. 内存锁定功能需要谨慎使用，避免内存不足