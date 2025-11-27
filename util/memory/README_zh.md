# 内存管理库

本模块提供高效的内存管理工具和组件，包括内存池、分配器、Blob 处理等功能。

## 功能特性

### 内存池管理
- 高性能内存池实现
- 支持不同大小的内存块
- 线程安全设计
- 内存使用统计

### 内存分配器
- 多种分配策略
- 内存对齐支持
- 大内存块管理
- 内存映射支持

### Blob 处理
- 动态大小缓冲区
- 引用计数管理
- 零拷贝优化
- 序列化支持

## 主要组件

### 核心文件
- **pool.h/cpp** - 内存池实现
- **blob.h/cpp** - Blob 数据结构
- **addstorage.h/cpp** - 存储追加器
- **mmapalloc.h/cpp** - 内存映射分配器
- **segmented_string_pool.h/cpp** - 分段字符串池

### 工具函数
- **alloc.h/cpp** - 分配器接口
- **small_allocator.h** - 小对象分配器

## 使用方法

### 内存池使用
```cpp
#include "util/memory/pool.h"

// 创建内存池
TMemoryPool pool(1024);  // 初始大小 1KB

// 分配内存
void* ptr = pool.Allocate(256);

// 分配并对齐内存
void* aligned_ptr = pool.AllocateAligned(64, 64);

// 获取已使用内存大小
size_t used = pool.Used();

// 重置内存池（保留内存）
pool.Clear();
```

### Blob 使用
```cpp
#include "util/memory/blob.h"

// 创建 Blob
TBlob blob = TBlob::FromBuffer(data, size);

// 子 Blob
TBlob subBlob = blob.SubBlob(offset, length);

// 转换为字符串
TString str = blob.AsString();

// 检查是否为空
if (blob.Empty()) {
    // 处理空 Blob
}
```

### 存储追加器
```cpp
#include "util/memory/addstorage.h"

// 创建追加器
TAddStorage storage;

// 追加数据
storage.Append(data, size);

// 获取缓冲区
const char* buffer = storage.Data();
size_t totalSize = storage.Size();

// 重置
storage.Clear();
```

### 分段字符串池
```cpp
#include "util/memory/segmented_string_pool.h"

// 创建字符串池
TSegmentedStringPool pool;

// 分配字符串
size_t offset = pool.AppendString("Hello, World!");

// 获取字符串
TStringBuf str = pool.GetString(offset);

// 批量分配
std::vector<size_t> offsets;
pool.AppendStrings({"str1", "str2", "str3"}, offsets);
```

## 性能特性

### 内存池优化
- 预分配内存块
- 分级大小管理
- 快速分配/释放
- 减少内存碎片

### Blob 优化
- 引用计数避免拷贝
- 零拷贝切片操作
- 小对象优化
- 缓存友好布局

### 性能指标
- 内存分配：< 100 ns
- Blob 创建：< 50 ns
- 内存池操作：< 10 ns

## 线程安全

### 内存池
- 默认非线程安全
- 提供线程安全版本
- 使用原子操作优化

### Blob
- 只读操作线程安全
- 引用计数原子操作
- 无锁读取路径

## 内存对齐

### 对齐支持
```cpp
// 对齐分配
void* ptr = pool.AllocateAligned(size, alignment);

// 检查对齐
bool is_aligned = IsAligned(ptr, alignment);

// 获取对齐大小
size_t aligned_size = AlignUp(size, alignment);
```

## 调试功能

### 内存泄漏检测
```cpp
#ifdef NDEBUG
    // 调试模式下启用泄漏检测
    pool.EnableLeakDetection();
#endif
```

### 内存统计
```cpp
// 获取内存使用统计
TMemoryStats stats = pool.GetStats();
std::cout << "Used: " << stats.Used << std::endl;
std::cout << "Allocated: " << stats.Allocated << std::endl;
```

## 测试

### 单元测试
```bash
# 运行所有测试
./ut/memory_ut

# 运行特定组件测试
./ut/memory_ut --gtest_filter="BlobTest.*"
```

### 性能测试
```bash
# 运行性能基准测试
./ut/memory_perf

# 内存分配基准
./ut/memory_perf --benchmark="Allocate"
```

## 最佳实践

1. **内存池使用**
   - 选择合适的初始大小
   - 批量分配减少开销
   - 定期清理不需要的内存

2. **Blob 使用**
   - 尽可能使用引用
   - 避免频繁的小 Blob
   - 使用 SubBlob 代替拷贝

3. **性能优化**
   - 使用内存对齐
   - 预分配缓冲区
   - 重用对象

## 平台支持

- Linux (x86_64, ARM64)
- macOS (x86_64, ARM64)
- Windows (x86_64)

## 依赖项

- 标准 C++ 库
- C++11 或更高版本
- 系统内存管理接口（mmap）

## 注意事项

1. **内存池生命周期**
   - 确保在所有对象释放前销毁
   - 避免悬空指针

2. **线程安全**
   - 默认实现非线程安全
   - 需要时使用同步机制

3. **内存限制**
   - 监控内存使用
   - 设置合理的限制

## 版本历史

- v3.0: 添加线程安全支持
- v2.5: 优化小对象分配
- v2.0: 添加内存映射支持
- v1.0: 初始版本