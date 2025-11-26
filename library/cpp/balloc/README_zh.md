# balloc - 高性能内存分配器

## 概述

balloc 是一个高性能的自定义内存分配器，专为多线程环境设计，提供了比标准 malloc 更快的内存分配和释放性能。该分配器使用线程本地存储和 NUMA 感知技术，显著降低了内存分配的延迟和锁竞争。

## 核心特性

### 1. 线程本地存储（TLS）
每个线程维护自己的内存池，避免线程间的锁竞争：
- **零竞争设计**：每个线程独立管理自己的内存
- **快速路径**：大多数分配操作无需加锁
- **线程安全**：完全线程安全的内存管理

### 2. NUMA 感知
支持 NUMA 架构，优化内存访问性能：
- **CPU 感知**：自动检测当前 CPU 和 NUMA 节点
- **本地分配**：优先从本地 NUMA 节点分配内存
- **亲和性优化**：减少跨 NUMA 节点的内存访问

### 3. 内存池管理
使用分层内存池策略：
- **小块分配**：使用预分配的内存池
- **大块分配**：直接使用 mmap
- **内存对齐**：保证适当的内存对齐
- **缓存友好**：优化内存访问模式

### 4. 动态控制
支持运行时启用/禁用：
- **动态切换**：可以在运行时切换到系统 malloc
- **透明切换**：切换对应用程序透明
- **调试模式**：支持调试时的内存填充

## 目录结构

### 核心实现
- **balloc.cpp**：主实现文件，包含 malloc/free 的重写
- **malloc-info.cpp**：内存信息相关功能

### 库文件（lib/）
- **balloc.h**：核心分配器实现和内部数据结构
  - `TAllocHeader`：分配头部信息
  - `TLS`：线程本地存储结构
  - 内存分配和释放的核心逻辑
- **alloc_stats.h/.cpp**：分配统计功能
  - 内存使用统计
  - 线程分配统计
  - mmap 计数器

### 配置文件（setup/）
包含分配器的配置和初始化代码

### 可选功能（optional/）
提供额外的可选功能和扩展

## 实现原理

### 分配策略
1. **小块内存**（< PAGE_ELEM/2）
   - 使用预分配的内存池
   - 按大小分级管理
   - 快速分配和释放

2. **大块内存**（>= PAGE_ELEM/2）
   - 直接使用 mmap
   - 按页对齐
   - 使用 munmap 释放

### 内存布局
```
[AllocHeader][User Data]
AllocHeader 包含：
- 分配大小（包含签名位）
- 指向内存块的指针
- 签名信息（用于验证）
```

### 签名机制
- **ALIVE_SIGNATURE**（0xa...）：由 balloc 管理的内存
- **DISABLED_SIGNATURE**（0xb...）：由系统 malloc 管理的内存
- **签名验证**：防止内存损坏和重复释放

## 性能优化

### 1. 快速路径优化
- 使用 Y_LIKELY/Y_UNLIKELY 提示分支预测
- 内联小函数减少调用开销
- 避免不必要的锁操作

### 2. 内存对齐
- 默认按 sizeof(TAllocHeader) 对齐
- 支持 SIMD 对齐要求
- 优化缓存行利用

### 3. 批量操作
- 预分配大块内存
- 减少系统调用次数
- 使用内存池减少碎片

## 调试功能

### 内存填充
- 释放时填充 0xde
- 检测使用已释放内存
- 调试模式下的额外检查

### 统计信息
```cpp
// 启用统计
NAllocStats::EnableAllocStats(true);

// 获取线程最大分配
i64 maxAlloc = NAllocStats::GetThreadAllocMax();

// 获取 mmap 计数
ui64 mmapCount = NAllocStats::GetMmapCounter();
```

## 使用方式

### 1. 预编译方式
将 balloc 编译为动态库，通过 LD_PRELOAD 使用：
```bash
LD_PRELOAD=./libballoc.so ./your_program
```

### 2. 静态链接
直接链接到应用程序：
```cpp
// 包含头文件
#include <library/cpp/balloc/lib/balloc.h>

// 直接使用 malloc/free，会被重定向到 balloc
void* ptr = malloc(1024);
free(ptr);
```

### 3. 动态控制
```cpp
// 禁用 balloc，回退到系统 malloc
NBalloc::Disable();

// 重新启用 balloc
NBalloc::Enable();

// 检查是否禁用
if (NBalloc::IsDisabled()) {
    // 使用系统 malloc
}
```

## 性能数据

典型的性能提升：
- **单线程**：比 glibc malloc 快 2-3 倍
- **多线程**：比 glibc malloc 快 5-10 倍（减少锁竞争）
- **内存碎片**：显著减少内存碎片
- **缓存友好**：更好的局部性

## 平台支持

### 支持的架构
- x86_64
- i386
- arm64
- ppc64

### 支持的系统
- Linux（完全支持）
- FreeBSD（部分支持）
- macOS（部分支持）
- Android（bionic）

## 注意事项

1. **内存对齐**：确保正确对齐，避免 SIMD 错误
2. **NUMA 配置**：合理配置 NUMA 策略
3. **内存泄漏**：使用工具检测内存泄漏
4. **调试模式**：生产环境关闭调试功能
5. **与其他分配器冲突**：避免同时使用多个分配器

## 依赖项

- 系统库：pthread、dl、m
- 内核特性：mmap、munmap
- 可选：NUMA 支持、VDSO getcpu

## 故障排除

### 常见问题
1. **初始化失败**：检查 TLS 初始化
2. **性能不佳**：检查 NUMA 配置
3. **内存损坏**：启用调试模式
4. **兼容性问题**：检查与第三方库的兼容性

### 调试技巧
- 使用 `DBG_FILL_MEMORY` 检测野指针
- 启用统计信息监控内存使用
- 使用 valgrind 检测内存错误