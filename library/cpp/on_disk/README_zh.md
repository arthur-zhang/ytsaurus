# On Disk 磁盘数据结构库

## 项目概述

On Disk 是一个专门用于处理磁盘上数据结构的 C++ 库，提供了高效的数据存储、索引和查询功能。该库包含多个子模块，支持分块数据存储、Aho-Corasick 多模式匹配算法和 TAR 归档文件处理。

### 核心功能
- **分块数据存储**：高效的数据分块读写机制
- **Aho-Corasick 算法**：磁盘上的多模式字符串匹配
- **TAR 归档支持**：完整的 TAR 文件读写操作
- **内存映射访问**：零拷贝的大文件访问模式
- **高性能索引**：优化的索引结构和查询算法

## 目录结构

### chunks/ 目录
分块数据读写模块，提供高效的数据分块存储和访问机制。

#### 主要文件
- **reader.h/reader.cpp** - 分块数据读取器
- **writer.h/writer.cpp** - 分块数据写入器
- **chunked_helpers.h/chunked_helpers.cpp** - 分块数据辅助工具
- **chunks_ut.cpp** - 单元测试
- **ut/ya.make** - 测试构建配置
- **ya.make** - 主构建配置

#### 核心功能
- **TChunkedDataReader** - 分块数据读取类
- **TChunkedDataWriter** - 分块数据写入类
- **内存对齐**：支持数据的内存对齐优化
- **版本兼容**：支持多版本格式兼容

### aho_corasick/ 目录
Aho-Corasick 多模式匹配算法的磁盘实现，用于高效的字符串搜索。

#### 主要文件
- **reader.h** - Aho-Corasick 读取器实现
- **writer.h** - Aho-Corasick 写入器实现
- **common.h** - 通用定义和常量
- **helpers.h** - 辅助函数和工具

#### 核心功能
- **TMappedAhoCorasick** - 内存映射的 Aho-Corasick 实现
- **多容器支持**：支持不同类型的输出容器
- **模板化设计**：支持不同的字符串类型和输出类型
- **数据验证**：内置的数据完整性检查

### tar_archive/ 目录
TAR 归档文件处理模块，基于 libarchive 库提供 C++ 封装。

#### 主要文件
- **archive_writer.h/archive_writer.cpp** - TAR 归档写入器
- **archive_iterator.h/archive_iterator.cpp** - TAR 归档迭代器
- **archive_windows.h** - Windows 平台支持
- **README.md** - 英文说明文档
- **ya.make** - 构建配置

#### 核心功能
- **TArchiveWriter** - TAR 归档写入器
- **TArchiveIterator** - TAR 归档读取迭代器
- **多格式支持**：支持多种压缩和编码格式
- **跨平台兼容**：支持 Linux 和 Windows 平台

## 使用示例

### 分块数据读写示例
```cpp
#include <library/cpp/on_disk/chunks/reader.h>
#include <library/cpp/on_disk/chunks/writer.h>

// 写入分块数据
void WriteChunkedData() {
    TFileOutput file("data.chunks");
    TChunkedDataWriter writer(file);

    // 写入第一个块
    writer << "Block 1 data";
    writer.NewBlock();

    // 写入第二个块
    writer << "Block 2 data";
    writer.NewBlock();

    // 写入第三个块
    writer.WriteBinary<int>(42);

    // 写入文件尾部
    writer.WriteFooter();
}

// 读取分块数据
void ReadChunkedData() {
    TBlob blob = TBlob::FromFile("data.chunks");
    TChunkedDataReader reader(blob);

    for (size_t i = 0; i < reader.GetBlocksCount(); ++i) {
        const void* blockData = reader.GetBlock(i);
        size_t blockSize = reader.GetBlockLen(i);

        printf("Block %zu: %.*s\n", i, (int)blockSize, (const char*)blockData);

        // 获取块的 Blob 对象
        TBlob blockBlob = reader.GetBlob(i);

        // 获取类型化区域
        if (i == 2) { // 第三个块包含 int 数据
            auto intRegion = reader.GetRegion<int>(i);
            if (!intRegion.empty()) {
                printf("Integer value: %d\n", intRegion[0]);
            }
        }
    }
}
```

### Aho-Corasick 多模式匹配示例
```cpp
#include <library/cpp/on_disk/aho_corasick/reader.h>
#include <library/cpp/on_disk/aho_corasick/writer.h>

using namespace std;

// 构建并使用 Aho-Corasick 自动机
void BuildAndSearchAhoCorasick() {
    // 构建模式集合
    vector<string> patterns = {
        "hello",
        "world",
        "test",
        "pattern"
    };

    // 创建 Aho-Corasick 写入器
    TBufferOutput buffer;
    TAhoCorasickWriter<string, ui32> writer(buffer);

    // 添加模式
    for (size_t i = 0; i < patterns.size(); ++i) {
        writer.AddPattern(patterns[i], (ui32)i);
    }

    // 构建自动机
    writer.Build();

    // 创建内存映射的读取器
    TBlob blob = TBlob::FromStream(buffer);
    TDefaultMappedAhoCorasick automaton(blob);

    // 搜索字符串
    string text = "hello world, this is a test pattern";
    auto results = automaton.AhoSearch(text);

    // 输出匹配结果
    for (const auto& result : results) {
        printf("Pattern found at position %u: pattern id %u\n",
               result.first, result.second);
    }

    // 检查是否包含特定模式
    bool containsHello = automaton.AhoContains("hello");
    bool containsMissing = automaton.AhoContains("missing");

    printf("Contains 'hello': %s\n", containsHello ? "true" : "false");
    printf("Contains 'missing': %s\n", containsMissing ? "true" : "false");
}
```

### TAR 归档操作示例
```cpp
#include <library/cpp/on_disk/tar_archive/archive_writer.h>
#include <library/cpp/on_disk/tar_archive/archive_iterator.h>

// 创建 TAR 归档
void CreateTarArchive() {
    TArchiveWriter writer("archive.tar.gz");

    // 从字符串创建文件
    TString fileContent = "Hello, this is file content!";
    writer.WriteFile("test.txt", TBlob::FromString(fileContent));

    // 从流创建文件
    TFileInput inputFile("source.txt");
    writer.WriteFileFrom("source.txt", GetFileLength("source.txt"), inputFile);

    // 创建目录（如果内容为空）
    writer.WriteFile("empty_dir/", TBlob());
}

// 读取 TAR 归档
void ReadTarArchive() {
    TArchiveIterator arch("archive.tar.gz");

    for (const auto& file : arch) {
        if (file.IsRegular()) {
            printf("File: %s\n", file.GetPath().c_str());
            printf("Size: %zu\n", file.GetSize());

            // 读取文件内容
            TString content = file.GetStream().ReadAll();
            printf("Content: %s\n", content.c_str());
        } else if (file.IsDirectory()) {
            printf("Directory: %s\n", file.GetPath().c_str());
        }
    }
}

// 过滤特定文件
void FilterTarFiles() {
    TArchiveIterator arch("archive.tar.gz");

    for (const auto& file : arch) {
        if (file.IsRegular() && file.GetPath().EndsWith(".txt")) {
            printf("Text file: %s\n", file.GetPath().c_str());

            // 处理文本文件
            TString content = file.GetStream().ReadAll();
            ProcessTextFile(file.GetPath(), content);
        }
    }
}
```

## 实现原理

### 分块数据存储
#### 数据结构设计
```cpp
class TChunkedDataWriter {
private:
    IOutputStream& Slave;           // 底层输出流
    size_t Offset;                  // 当前偏移量
    TVector<ui64> Offsets;          // 每个块的偏移量
    TVector<ui64> Lengths;          // 每个块的长度
    static const ui64 Version = 1;  // 格式版本
};
```

#### 核心算法
- **分块机制**：将数据分割为固定大小的块
- **索引管理**：维护块的位置和长度信息
- **内存对齐**：确保块按指定边界对齐
- **版本控制**：支持向后兼容的格式升级

### Aho-Corasick 磁盘实现
#### 自动机结构
```cpp
template <class TStringType, class O, class C>
class TMappedAhoCorasick {
private:
    const TBlob Blob;                    // 数据映射
    const char* const AhoVertexes;       // 顶点数据
    const ui32 VertexAmount;             // 顶点数量
    const ui32* const Id2Offset;         // ID 到偏移量映射
    const TAhoVertexType Root;           // 根顶点
};
```

#### 核心特性
- **内存映射**：避免数据复制，直接访问磁盘数据
- **哈希表优化**：使用高效的哈希表存储转移函数
- **输出容器**：支持多种输出数据结构
- **数据验证**：内置完整性检查机制

#### 算法优化
- **预计算**：构建时预计算所有转移函数
- **失败链接**：优化的失败指针计算
- **输出链接**：高效的输出链接遍历
- **空间优化**：紧凑的数据布局

### TAR 归档处理
#### 基于 libarchive 的封装
- **C++ 接口**：提供面向对象的 C++ 接口
- **RAII 管理**：自动资源管理和异常安全
- **迭代器模式**：方便的文件遍历机制
- **流式处理**：支持大文件的流式读写

## 应用场景

### 大数据处理
- **日志分析**：使用 Aho-Corasick 进行关键词搜索
- **数据挖掘**：在海量文本中查找模式
- **ETL 流程**：高效的数据转换和处理
- **数据归档**：大文件的压缩归档存储

### 文件系统
- **搜索引擎**：全文索引和搜索功能
- **版本控制**：文件版本管理和差异存储
- **备份系统**：增量备份和归档管理
- **内容分发**：文件打包和分发

### 网络安全
- **入侵检测**：网络流量中的恶意模式检测
- **内容过滤**：网页和邮件内容过滤
- **病毒扫描**：文件中的病毒特征匹配
- **日志审计**：安全日志的模式匹配

### 数据库系统
- **全文搜索**：数据库的全文索引实现
- **模式匹配**：复杂的字符串模式查询
- **数据压缩**：高效的存储压缩算法
- **缓存管理**：磁盘缓存的数据组织

## 性能特性

### 时间复杂度
- **分块读取**：O(1) - 直接偏移访问
- **Aho-Corasick 搜索**：O(n + m) - n 为文本长度，m 为总模式长度
- **TAR 遍历**：O(k) - k 为文件数量

### 空间复杂度
- **分块存储**：O(1) 额外空间
- **Aho-Corasick**：O(总模式长度)
- **TAR 处理**：O(1) 额外空间

### 内存使用
- **零拷贝访问**：使用内存映射避免数据复制
- **按需加载**：只加载需要的数据块
- **缓存友好**：优化的数据访问模式

## 配置选项

### 分块配置
```cpp
// 内存对齐边界
static inline size_t PaddingSize(size_t size, size_t boundary);

// 写入器配置
TChunkedDataWriter writer(outputStream);
writer.NewBlock();  // 创建新块
writer.WriteFooter(); // 写入结束标记
```

### Aho-Corasick 配置
```cpp
// 版本控制
static ui32 GetVersion() { return 3; }

// 块数量
static size_t GetBlockCount() { return 4; }

// 自定义输出容器
TMappedAhoCorasick<TString, MyOutputType, MyContainer> automaton(blob);
```

### TAR 归档配置
```cpp
// 自动检测格式
TArchiveWriter writer("archive.tar.gz");

// 手动指定格式
TArchiveWriter writer("archive.tar", "tar", "gzip", "utf-8");

// 从流创建文件
writer.WriteFileFrom(path, size, inputStream);
```

## 最佳实践

### 性能优化
- **批量操作**：减少小块数据的频繁读写
- **内存映射**：对大文件使用内存映射访问
- **预取策略**：预先访问可能需要的数据块
- **缓存管理**：合理使用内存缓存热点数据

### 错误处理
- **异常安全**：使用 RAII 确保资源正确释放
- **数据验证**：读取时验证数据完整性
- **版本兼容**：处理不同版本格式的兼容性
- **边界检查**：防止缓冲区溢出和越界访问

### 资源管理
- **及时释放**：不再使用的资源及时释放
- **文件关闭**：确保文件句柄正确关闭
- **内存清理**：避免内存泄漏和悬挂指针
- **线程安全**：多线程环境下的正确使用

## 扩展性

### 自定义容器
- **输出容器**：实现自定义输出数据结构
- **字符串类型**：支持不同的字符串编码
- **存储格式**：扩展新的存储格式支持
- **压缩算法**：集成新的压缩算法

### 平台支持
- **跨平台兼容**：支持主流操作系统
- **编译器支持**：兼容主流 C++ 编译器
- **架构支持**：支持不同 CPU 架构
- **大文件支持**：处理超大文件和超大块数据