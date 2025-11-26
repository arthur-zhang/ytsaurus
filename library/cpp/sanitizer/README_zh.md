# Sanitizer - 内存安全工具库

## 项目概述

Sanitizer 库为 YTsaurus 项目提供了内存安全检测和调试工具的支持集成。该库主要用于编译时和运行时的内存安全检查，包括 AddressSanitizer (ASan)、ThreadSanitizer (TSan)、MemorySanitizer (MSan) 和 UndefinedBehaviorSanitizer (UBSan) 等工具的配置和集成。

## 核心功能

### 内存安全检测工具
- **AddressSanitizer (ASan)**: 检测内存访问错误（缓冲区溢出、使用已释放内存等）
- **ThreadSanitizer (TSan)**: 检测数据竞争和多线程问题
- **MemorySanitizer (MSan)**: 检测未初始化内存的使用
- **UndefinedBehaviorSanitizer (UBSan)**: 检测未定义行为

### 编译配置支持
- CMake 构建系统配置
- 编译标志和链接选项管理
- 调试信息集成
- 运行时环境配置

## 重要文件说明

### 构建配置

- **`CMakeLists.txt`**: CMake 构建配置文件，定义了 sanitizer 工具的编译选项和依赖关系

```cmake
# 示例 CMake 配置
if(ENABLE_SANITIZERS)
    if(ENABLE_ASAN)
        set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -fsanitize=address")
        set(CMAKE_EXE_LINKER_FLAGS "${CMAKE_EXE_LINKER_FLAGS} -fsanitize=address")
    endif()

    if(ENABLE_TSAN)
        set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -fsanitize=thread")
        set(CMAKE_EXE_LINKER_FLAGS "${CMAKE_EXE_LINKER_FLAGS} -fsanitize=thread")
    endif()
endif()
```

## 使用指南

### 1. 编译时启用 Sanitizer

```bash
# 使用 AddressSanitizer 编译
cmake -DCMAKE_BUILD_TYPE=Debug -DENABLE_ASAN=ON ../ytsaurus
ninja

# 使用 ThreadSanitizer 编译
cmake -DCMAKE_BUILD_TYPE=Debug -DENABLE_TSAN=ON ../ytsaurus
ninja

# 启用多个 sanitizer
cmake -DCMAKE_BUILD_TYPE=Debug -DENABLE_ASAN=ON -DENABLE_UBSAN=ON ../ytsaurus
ninja
```

### 2. 运行时配置

```bash
# ASan 运行时选项
export ASAN_OPTIONS=detect_stack_use_after_return=1:strict_string_checks=1:detect_odr_violation=1

# TSan 运行时选项
export TSAN_OPTIONS=report_signal_unsafe=1:history_size=7

# MSan 运行时选项
export MSAN_OPTIONS=poison_in_dtor=1:report_umrs=1
```

## 应用场景

### 1. 开发调试

在开发阶段使用 sanitizer 工具捕获潜在的内存安全问题：

```cpp
// 使用 ASan 检测的示例代码
void TestBufferOverflow() {
    char buffer[10];
    // 这会导致缓冲区溢出，ASan 会报告
    buffer[10] = 'x';  // ASan error: stack-buffer-overflow
}

void TestUseAfterFree() {
    int* ptr = new int(42);
    delete ptr;
    // 这会导致使用已释放内存，ASan 会报告
    *ptr = 100;  // ASan error: heap-use-after-free
}
```

### 2. 多线程调试

使用 ThreadSanitizer 检测数据竞争：

```cpp
// TSan 检测数据竞争示例
int shared_data = 0;

void ThreadFunction() {
    shared_data++;  // 潜在的数据竞争
}

void TestDataRace() {
    std::thread t1(ThreadFunction);
    std::thread t2(ThreadFunction);

    t1.join();
    t2.join();  // TSan 会报告数据竞争
}
```

### 3. 内存初始化检查

使用 MemorySanitizer 检测未初始化内存：

```cpp
// MSan 检测未初始化内存示例
int GetUninitializedValue() {
    int value;  // 未初始化
    return value;  // MSan 会报告使用未初始化内存
}
```

### 4. 未定义行为检测

使用 UBSan 检测各种未定义行为：

```cpp
// UBSan 检测示例
int SignedIntegerOverflow() {
    int x = INT_MAX;
    return x + 1;  // UBSan error: signed integer overflow
}

int InvalidShift() {
    int x = 1;
    return x << 32;  // UBSan error: shift count out of range
}
```

## 配置选项

### AddressSanitizer 配置

```bash
# 常用 ASan 选项
ASAN_OPTIONS="detect_stack_use_after_return=1:\
detect_container_overflow=1:\
strict_string_checks=1:\
detect_odr_violation=1:\
alloc_dealloc_mismatch=1:\
quarantine_size_mb=256"
```

### ThreadSanitizer 配置

```bash
# 常用 TSan 选项
TSAN_OPTIONS="report_signal_unsafe=1:\
history_size=7:\
race_detection=1:\
halt_on_error=0"
```

### MemorySanitizer 配置

```bash
# 常用 MSan 选项
MSAN_OPTIONS="poison_in_dtor=1:\
report_umrs=1:\
wrap_signals=1"
```

## 最佳实践

### 1. 持续集成集成

```yaml
# CI/CD 配置示例
sanitizer_checks:
  stage: test
  script:
    - cmake -DCMAKE_BUILD_TYPE=Debug -DENABLE_ASAN=ON ../ytsaurus
    - ninja
    - ./run_tests_asan
  artifacts:
    reports:
      junit: sanitizer_reports.xml
  allow_failure: true
```

### 2. 渐进式部署

```cmake
# 条件性启用 sanitizer
option(ENABLE_SANITIZERS "Enable sanitizer checks" OFF)

if(ENABLE_SANITIZERS AND CMAKE_BUILD_TYPE STREQUAL "Debug")
    if(NOT APPLE)  # macOS 上某些 sanitizer 可能有兼容性问题
        set(ENABLE_ASAN ON CACHE BOOL "Enable AddressSanitizer")
        set(ENABLE_UBSAN ON CACHE BOOL "Enable UndefinedBehaviorSanitizer")
    endif()
endif()
```

### 3. 性能影响管理

```cpp
// 条件编译影响性能的检查
#ifdef ENABLE_ASAN
    // 在启用 ASan 时进行额外检查
    void ValidateMemoryAccess(void* ptr, size_t size) {
        // ASan 会自动检查，这里可以添加额外的验证
        assert(ptr != nullptr && size > 0);
    }
#else
    void ValidateMemoryAccess(void* ptr, size_t size) {
        // 生产环境中的轻量级检查
        Y_UNUSED(ptr);
        Y_UNUSED(size);
    }
#endif
```

## 故障排除

### 常见问题和解决方案

1. **ASan 和 TSan 不能同时使用**
   ```bash
   # 错误：不能同时启用
   cmake -DENABLE_ASAN=ON -DENABLE_TSAN=ON  # 不支持

   # 正确：选择其中一个
   cmake -DENABLE_ASAN=ON  # 或
   cmake -DENABLE_TSAN=ON
   ```

2. **链接器错误**
   ```bash
   # 确保链接时也包含 sanitizer 标志
   export LDFLAGS="-fsanitize=address"
   ```

3. **性能开销过大**
   ```bash
   # 仅在特定模块启用
   cmake -DENABLE_ASAN=ON -DASAN_TARGETS=core_lib
   ```

## 相关模块

- **testing**: 单元测试框架集成
- **memory_management**: 内存管理工具
- **debugging**: 调试工具和实用程序
- **profiling**: 性能分析工具

这个 sanitizer 库为 YTsaurus 项目提供了全面的内存安全保障，帮助开发者在开发和测试阶段及时发现和修复内存安全相关的 bug，提高系统的稳定性和可靠性。