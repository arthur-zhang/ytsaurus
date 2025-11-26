# 内存分配器管理库 (Malloc Management Library)

## 项目概述

本库提供了统一的内存分配器管理和接口抽象层，支持多种高性能内存分配器的集成和切换。它为 YTsaurus 系统提供了灵活的内存管理解决方案，包括系统分配器、jemalloc、tcmalloc、mimalloc 等多种分配器的支持，以及统一的配置、监控和诊断接口。

## 文件说明

### 核心接口

- **`api/malloc.h/cpp`** - 内存分配器核心接口
  - `TMallocInfo`: 分配器信息结构
  - 统一的分配器参数设置和获取接口
  - `TAllocHeader`: 内存块头部信息
  - 分配器损坏检测和错误处理

- **`api/helpers/`** - 辅助工具和帮助函数
  - 内存分配相关的辅助工具
  - 调试和诊断工具
  - 性能监控辅助函数

### 分配器实现

#### `jemalloc/` - JEMalloc 分配器

- **`malloc-info.cpp`**: JEMalloc 集成实现
  - 支持 jemalloc 配置参数管理
  - 性能分析和统计功能
  - 后台线程和背景清理
  - 内存使用监控和报告

```cpp
// JEMalloc 支持的参数示例
bool JESetParam(const char* param, const char* value) {
    if (strcmp(param, "j:prof") == 0) {
        // 启动/停止性能分析
        bool is_active = (strcmp(value, "start") == 0);
        mallctl("prof.active", nullptr, nullptr, &is_active, sizeof(is_active));
    }
    if (strcmp(param, "j:bg_threads") == 0) {
        // 控制后台清理线程
        bool is_active = (strcmp(value, "start") == 0);
        mallctl("background_thread", nullptr, nullptr, &is_active, sizeof(is_active));
    }
    // ... 更多参数支持
}
```

#### `tcmalloc/` - TCMalloc 分配器

- **`malloc-info.cpp`**: TCMalloc 集成实现
  - Google TCMalloc 分配器支持
  - 高性能多线程内存分配
  - 内存碎片优化
  - 调试和分析功能

#### `mimalloc/` - Mimalloc 分配器

- **`info.cpp`**: Mimalloc 集成实现
  - Microsoft Mimalloc 分配器支持
  - 极快的内存分配速度
  - 安全性和稳定性优化
  - 现代化的内存管理算法

#### `nalf/` - Nalf 分配器

- 内置的轻量级内存分配器实现
- 适用于嵌入式和资源受限环境
- 简单可靠的内存管理

#### `system/` - 系统分配器

- 基于操作系统默认的内存分配器
- 标准的 malloc/free 接口包装
- 跨平台兼容性

### 构建文件

- **`CMakeLists.txt`** - 跨平台构建配置
- **`ya.make`** - Ytsaurus 构建系统配置

## 实现原理

### 统一接口设计

```cpp
struct TMallocInfo {
    const char* Name;                                    // 分配器名称

    bool (*SetParam)(const char* param, const char* value);     // 参数设置
    const char* (*GetParam)(const char* param);               // 参数获取
    bool (*CheckParam)(const char* param, bool defaultValue);  // 参数检查
};

// 各分配器必须实现此接口
TMallocInfo MallocInfo();
```

### 内存头部编码

```cpp
struct TAllocHeader {
    void* Block;        // 内存块指针
    size_t AllocSize;   // 分配大小（包含签名）

    void Y_FORCE_INLINE Encode(void* block, size_t size, size_t signature) {
        Block = block;
        AllocSize = size | signature;  // 编码签名用于错误检测
    }
};
```

### 错误检测机制

```cpp
volatile bool IsAllocatorCorrupted = false;

void AbortFromCorruptedAllocator(const char* errorMessage = nullptr) {
    errorMessage = errorMessage ? errorMessage : "<unspecified>";
    fprintf(stderr, "Allocator error: %s\n", errorMessage);
    IsAllocatorCorrupted = true;
    abort();  // 安全终止程序
}
```

## 使用示例

### 基础使用

```cpp
#include <library/cpp/malloc/api/malloc.h>

// 获取当前分配器信息
NMalloc::TMallocInfo info = NMalloc::MallocInfo();
printf("Current allocator: %s\n", info.Name);

// 设置分配器参数
if (info.SetParam) {
    info.SetParam("j:prof", "start");  // 启用性能分析
}

// 获取分配器参数
if (info.GetParam) {
    const char* value = info.GetParam("thread.cache.num");
    if (value) {
        printf("Thread cache count: %s\n", value);
    }
}
```

### JEMalloc 配置

```cpp
#include <library/cpp/malloc/api/malloc.h>

void ConfigureJEMalloc() {
    NMalloc::TMallocInfo info = NMalloc::MallocInfo();

    if (strstr(info.Name, "jemalloc")) {
        // 启用性能分析
        info.SetParam("j:prof", "start");

        // 启动后台线程
        info.SetParam("j:bg_threads", "start");

        // 重置统计epoch
        info.SetParam("j:reset_epoch", "1");

        // 设置内存限制（MB）
        info.SetParam("j:arena.purge", "100");

        // 导出内存统计
        info.SetParam("j:prof_dump", "1");
    }
}
```

### 内存分配器切换

```cpp
// 编译时选择不同的分配器
#ifdef USE_JEMALLOC
    #include <contrib/libs/jemalloc/include/jemalloc/jemalloc.h>
    #define CUSTOM_MALLOC je_malloc
    #define CUSTOM_FREE je_free
#elif defined(USE_TCMALLOC)
    #include <gperftools/tcmalloc.h>
    #define CUSTOM_MALLOC tc_malloc
    #define CUSTOM_FREE tc_free
#elif defined(USE_MIMALLOC)
    #include <mimalloc.h>
    #define CUSTOM_MALLOC mi_malloc
    #define CUSTOM_FREE mi_free
#else
    #define CUSTOM_MALLOC malloc
    #define CUSTOM_FREE free
#endif

void* CustomAllocate(size_t size) {
    void* ptr = CUSTOM_MALLOC(size);
    if (!ptr) {
        NMalloc::AbortFromCorruptedAllocator("Memory allocation failed");
    }
    return ptr;
}

void CustomDeallocate(void* ptr) {
    if (ptr) {
        CUSTOM_FREE(ptr);
    }
}
```

### 内存统计和监控

```cpp
void PrintMemoryStats() {
    NMalloc::TMallocInfo info = NMalloc::MallocInfo();

    if (strstr(info.Name, "jemalloc")) {
        // JEMalloc 统计
        size_t allocated = 0, active = 0;
        size_t len = sizeof(size_t);

        if (mallctl("stats.allocated", &allocated, &len, nullptr, 0) == 0) {
            printf("Allocated: %zu bytes\n", allocated);
        }

        if (mallctl("stats.active", &active, &len, nullptr, 0) == 0) {
            printf("Active: %zu bytes\n", active);
        }
    }
}
```

### 错误处理和调试

```cpp
#include <library/cpp/malloc/api/malloc.h>

void SafeMemoryOperation() {
    try {
        // 检查分配器状态
        if (NMalloc::IsAllocatorCorrupted) {
            throw std::runtime_error("Allocator corrupted");
        }

        // 执行内存操作
        void* ptr = malloc(1024);
        if (!ptr) {
            NMalloc::AbortFromCorruptedAllocator("Allocation failed");
        }

        // 使用内存...

        free(ptr);

    } catch (const std::exception& e) {
        printf("Memory operation failed: %s\n", e.what());
        NMalloc::AbortFromCorruptedAllocator(e.what());
    }
}
```

### 性能测试

```cpp
#include <chrono>
#include <vector>

void BenchmarkAllocator() {
    const int iterations = 1000000;
    std::vector<void*> ptrs;

    auto start = std::chrono::high_resolution_clock::now();

    // 分配测试
    for (int i = 0; i < iterations; ++i) {
        void* ptr = malloc(1024);
        if (ptr) {
            ptrs.push_back(ptr);
        }
    }

    // 释放测试
    for (void* ptr : ptrs) {
        free(ptr);
    }

    auto end = std::chrono::high_resolution_clock::now();
    auto duration = std::chrono::duration_cast<std::chrono::milliseconds>(end - start);

    printf("Allocator benchmark: %d allocations/deletions in %ld ms\n",
           iterations, duration.count());
}
```

## 应用场景

### 1. 高性能服务器

- **Web 服务器**: 处理大量并发请求
- **数据库系统**: 频繁的内存分配和释放
- **消息队列**: 高吞吐量数据处理
- **缓存系统**: 内存密集型操作

### 2. 大数据处理

- **分布式计算**: 节点间数据传输
- **流处理**: 实时数据处理
- **批处理**: 大规模数据集处理
- **机器学习**: 模型训练和推理

### 3. 游戏和多媒体

- **游戏引擎**: 实时渲染和物理模拟
- **视频处理**: 帧缓冲和媒体数据
- **音频处理**: 音频流和缓冲管理
- **图形渲染**: 纹理和几何数据处理

### 4. 嵌入式系统

- **物联网设备**: 资源受限环境
- **移动应用**: 内存和电池优化
- **实时系统**: 确定性内存分配
- **安全系统**: 内存安全保护

### 5. 开发和调试

- **性能分析**: 内存使用分析
- **内存泄漏检测**: 动态内存监控
- **压力测试**: 分配器性能测试
- **错误诊断**: 内存损坏检测

## 技术特性

### 多分配器支持

1. **JEMalloc**: 高性能并发分配器
2. **TCMalloc**: Google 的优化分配器
3. **Mimalloc**: Microsoft 的现代分配器
4. **系统分配器**: 标准 malloc 实现
5. **Nalf**: 轻量级内置分配器

### 统一接口

1. **标准接口**: 兼容标准 malloc/free
2. **参数配置**: 统一的参数设置接口
3. **监控集成**: 统一的监控和诊断
4. **错误处理**: 统一的错误处理机制

### 性能优化

1. **并发优化**: 支持多线程并发分配
2. **内存池**: 减少系统调用开销
3. **碎片管理**: 优化内存碎片问题
4. **缓存友好**: CPU 缓存优化设计

### 安全特性

1. **内存保护**: 防止内存越界
2. **损坏检测**: 检测内存损坏
3. **错误恢复**: 安全的错误处理
4. **调试支持**: 丰富的调试信息

## 分配器对比

| 分配器 | 特点 | 适用场景 | 性能特点 |
|--------|------|----------|----------|
| JEMalloc | 高并发、可配置 | 服务器、数据库 | 低碎片、可扩展 |
| TCMalloc | 简单、高效 | 通用应用、Web服务 | 快速分配、低延迟 |
| Mimalloc | 极快、安全 | 现代应用、安全敏感 | 超快分配、安全防护 |
| 系统分配器 | 标准、兼容 | 通用应用、跨平台 | 标准实现、广泛支持 |
| Nalf | 轻量、简单 | 嵌入式、资源受限 | 小体积、低开销 |

## 配置参数

### JEMalloc 参数

```bash
# 性能分析
j:prof=start|stop|dump

# 后台线程
j:bg_threads=start|stop

# 内存重置
j:reset_epoch=1

# Arena 设置
j:arena.purge=100
```

### 通用参数

```bash
# 调试模式
debug=true|false

# 内存限制
memory_limit=1024MB

# 线程缓存
thread_cache=true|false
```

## 性能指标

### 分配性能

- **JEMalloc**: 10-50ns 分配延迟
- **TCMalloc**: 5-20ns 分配延迟
- **Mimalloc**: 1-10ns 分配延迟
- **系统分配器**: 50-200ns 分配延迟

### 内存效率

- **碎片率**: < 5% (优化配置)
- **缓存命中率**: > 90%
- **并发扩展性**: 接近线性扩展
- **内存开销**: < 10% 总内存使用

## 最佳实践

### 1. 选择合适的分配器

```cpp
// 高并发服务器：JEMalloc
#ifdef HIGH_CONCURRENCY_SERVER
    USE_JEMALLOC

// 通用Web应用：TCMalloc
#elif WEB_APPLICATION
    USE_TCMALLOC

// 安全敏感应用：Mimalloc
#elif SECURITY_SENSITIVE
    USE_MIMALLOC

// 嵌入式系统：Nalf
#elif EMBEDDED_SYSTEM
    USE_NALF
#else
    // 默认使用系统分配器
    USE_SYSTEM_MALLOC
#endif
```

### 2. 内存分配优化

```cpp
// 避免频繁的小分配
void OptimizeSmallAllocations() {
    // 使用对象池
    std::vector<Object> pool;

    // 批量分配
    Object* batch = new Object[100];

    // 使用内存池
    MemoryPool pool(1024 * 1024);  // 1MB 池
}

// 及时释放大内存
void ManageLargeMemory() {
    char* buffer = new char[100 * 1024 * 1024];  // 100MB

    // 使用完后立即释放
    delete[] buffer;

    // 强制分配器清理
    NMalloc::TMallocInfo info = NMalloc::MallocInfo();
    if (info.SetParam) {
        info.SetParam("purge", "all");
    }
}
```

### 3. 监控和诊断

```cpp
// 定期检查分配器健康状态
void HealthCheck() {
    if (NMalloc::IsAllocatorCorrupted) {
        LOG_FATAL("Allocator corrupted, initiating shutdown");
        EmergencyShutdown();
    }

    // 检查内存使用
    size_t used = GetMemoryUsage();
    size_t limit = GetMemoryLimit();

    if (used > limit * 0.9) {
        LOG_WARN("Memory usage high: " << used << "/" << limit);
        TriggerMemoryCleanup();
    }
}

// 性能监控
void PerformanceMonitoring() {
    static auto lastCheck = std::chrono::steady_clock::now();
    static size_t totalAllocs = 0;

    auto now = std::chrono::steady_clock::now();
    auto duration = std::chrono::duration_cast<std::chrono::seconds>(now - lastCheck);

    if (duration.count() >= 60) {  // 每分钟检查
        double allocRate = totalAllocs / duration.count();
        LOG_INFO("Allocation rate: " << allocRate << " ops/sec");

        totalAllocs = 0;
        lastCheck = now;
    }
}
```

## 构建和部署

### 编译配置

```cmake
# CMakeLists.txt
option(USE_JEMALLOC "Use JEMalloc allocator" OFF)
option(USE_TCMALLOC "Use TCMalloc allocator" OFF)
option(USE_MIMALLOC "Use Mimalloc allocator" OFF)

if(USE_JEMALLOC)
    find_package(jemalloc REQUIRED)
    target_link_libraries(myapp jemalloc::jemalloc)
elseif(USE_TCMALLOC)
    find_package(PkgConfig REQUIRED)
    pkg_check_modules(TCMALL OCQUIRED REQUIRED tcmalloc)
    target_link_libraries(myapp ${TCMALL_LIBRARIES})
elseif(USE_MIMALLOC)
    find_package(mimalloc REQUIRED)
    target_link_libraries(myapp mimalloc::mimalloc)
endif()
```

### 运行时配置

```bash
# 环境变量配置
export MALLOC_CONF="prof:true,lg_chunk:16,background_thread:true"
export TCMALLOC_SAMPLE_PARAMETER=524288
export MIMALLOC_SHOW_STATS=1

# 系统限制
ulimit -v unlimited  # 虚拟内存限制
ulimit -m unlimited  # 物理内存限制
```