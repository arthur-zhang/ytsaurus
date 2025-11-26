# DWARF 调试信息回溯解析库

基于 DWARF 调试信息的高性能回溯地址解析库。

## 概述

该库提供了基于 DWARF 调试信息的回溯地址解析功能，能够将内存地址转换为可读的源代码位置信息，包括文件名、行号、列号和函数名。支持内联函数的完整解析。

## 核心特性

### 调试信息解析
- **DWARF 格式支持**: 完整的 DWARF 调试信息解析
- **内联函数**: 支持内联函数的层级解析
- **符号解析**: 精确的地址到符号映射
- **跨平台**: 支持 Linux 和 macOS 平台

### 线程安全设计
- **锁版本**: `ResolveBacktraceLocked` 提供线程安全保证
- **非锁版本**: `ResolveBacktrace` 用于单线程环境
- **内存安全**: 避免并发使用时的内存泄漏问题

### 高精度信息
- **源代码位置**: 精确的文件名、行号、列号
- **函数信息**: 完整的函数名和地址信息
- **调用层级**: 完整的调用栈层级信息

## 主要组件

### 核心数据结构
```cpp
struct TLineInfo {
    TString FileName;      // 源文件名
    int Line;             // 行号
    int Col;              // 列号
    TString FunctionName; // 函数名
    uintptr_t Address;    // 内存地址
    int Index;            // 调用栈索引
};

struct TError {
    int Code;             // 错误代码
    TString Message;      // 错误消息
};
```

### 回调机制
```cpp
enum class EResolving {
    Continue = 0,         // 继续解析
    Break = 1,           // 停止解析
};

using TCallback = std::function<EResolving(const TLineInfo&)>;
```

### 核心函数
```cpp
// 解析回溯地址，为每个内联函数调用回调
TMaybe<TError> ResolveBacktrace(TArrayRef<const void* const> backtrace, TCallback callback);

// 线程安全版本的回溯解析
TMaybe<TError> ResolveBacktraceLocked(TArrayRef<const void* const> backtrace, TCallback callback);
```

## 使用示例

### 基本用法
```cpp
#include <dwarf_backtrace/backtrace.h>

void PrintBacktraceInfo(const std::vector<void*>& backtrace) {
    auto error = NDwarf::ResolveBacktrace(backtrace,
        [](const NDwarf::TLineInfo& info) {
            std::cout << "File: " << info.FileName
                     << ", Line: " << info.Line
                     << ", Function: " << info.FunctionName
                     << std::endl;
            return NDwarf::EResolving::Continue;
        });

    if (error) {
        std::cerr << "解析错误: " << error->Message << std::endl;
    }
}
```

### 限制解析深度
```cpp
void PrintTop5Frames(const std::vector<void*>& backtrace) {
    int frameCount = 0;
    auto error = NDwarf::ResolveBacktrace(backtrace,
        [&frameCount](const NDwarf::TLineInfo& info) {
            if (frameCount++ >= 5) {
                return NDwarf::EResolving::Break;
            }

            std::cout << "Frame " << info.Index << ": "
                     << info.FunctionName << std::endl;
            return NDwarf::EResolving::Continue;
        });
}
```

### 多线程环境使用
```cpp
void ThreadSafeBacktraceAnalysis(const std::vector<void*>& backtrace) {
    auto error = NDwarf::ResolveBacktraceLocked(backtrace,
        [](const NDwarf::TLineInfo& info) {
            // 线程安全的回溯处理
            ProcessFrameInfo(info);
            return NDwarf::EResolving::Continue;
        });
}
```

## 实现架构

### 依赖库集成
- **libbacktrace**: 核心回溯解析库
- **DWARF 解析器**: 调试信息解析
- **平台适配**: 不同平台的特殊处理

### 内存管理
- **静态互斥锁**: 保护并发访问
- **状态管理**: 单独的解析状态
- **资源释放**: 自动资源清理

### 错误处理
- **Maybe 类型**: 安全的错误传播
- **详细错误信息**: 包含错误代码和消息
- **优雅降级**: 解析失败时的回退机制

## 平台支持

### Linux 平台
- **x86_64**: 完整支持
- **aarch64**: 完整支持
- **glibc**: 基于 glibc 的符号解析

### macOS 平台
- **x86_64**: 完整支持
- **arm64**: 完整支持
- **dyld**: 基于 dyld 的符号解析

### 构建配置
每个平台都有对应的 CMakeLists 配置：
- `CMakeLists.linux-x86_64.txt`
- `CMakeLists.linux-aarch64.txt`
- `CMakeLists.darwin-x86_64.txt`
- `CMakeLists.darwin-arm64.txt`

## 性能优化

### 解析策略
- **延迟解析**: 按需解析调试信息
- **缓存机制**: 避免重复解析
- **批量处理**: 高效的批量地址处理

### 内存效率
- **流式处理**: 不占用大量内存
- **及时释放**: 处理完成后立即释放资源
- **最小分配**: 减少内存分配次数

## 应用场景

### 调试工具
- **崩溃报告**: 生成详细的崩溃堆栈信息
- **性能分析**: 函数调用性能分析
- **内存泄漏**: 内存泄漏位置定位

### 日志系统
- **错误日志**: 自动附加调用栈信息
- **调试日志**: 可选的详细调用信息
- **性能监控**: 关键路径的性能追踪

### 开发工具
- **IDE 集成**: 代码导航和调试
- **代码分析**: 静态代码分析
- **测试工具**: 单元测试的调用验证

## 技术细节

### DWARF 格式支持
- **DWARF2**: 基础 DWARF 格式
- **DWARF3**: 增强的调试信息
- **DWARF4**: 最新的调试信息标准
- **DWARF5**: 最新版本的实验性支持

### 内联函数处理
- **层级解析**: 完整的内联调用链
- **地址映射**: 内联函数的地址映射
- **源码定位**: 内联函数的源码位置

### 符号解析
- **函数符号**: 函数入口地址解析
- **变量符号**: 变量位置信息
- **类型信息**: 复杂数据类型的解析

## 最佳实践

### 使用建议
1. **多线程环境**: 优先使用 `ResolveBacktraceLocked`
2. **性能考虑**: 避免频繁的回溯解析
3. **错误处理**: 始终检查返回的错误信息
4. **资源管理**: 及时释放不需要的资源

### 注意事项
- **调试信息**: 需要编译时包含调试信息
- **二进制兼容**: 不同版本可能存在兼容性问题
- **内存使用**: 大型程序的回溯可能消耗较多内存
- **线程安全**: 注意并发使用的线程安全问题

## 测试和验证

### 单元测试
包含完整的单元测试覆盖：
- **基础功能测试**: 基本解析功能验证
- **边界情况测试**: 异常情况处理验证
- **性能测试**: 大规模数据处理测试

### 集成测试
与 YTsaurus 系统的集成测试确保：
- **兼容性**: 与现有系统的兼容性
- **稳定性**: 长期运行的稳定性
- **性能**: 在生产环境的性能表现