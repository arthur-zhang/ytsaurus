# 系统接口库

本模块提供系统级功能的封装和抽象，包括进程管理、文件系统操作、系统信息获取等功能。

## 功能特性

### 系统信息
- CPU 信息获取
- 内存使用统计
- 系统负载监控
- 进程信息查询

### 文件系统
- 文件路径处理
- 目录操作
- 文件属性查询
- 符号链接处理

### 进程管理
- 进程创建和管理
- 线程操作
- 信号处理
- 资源限制

### 系统调用封装
- 跨平台兼容性
- 错误处理优化
- 性能增强

## 主要组件

### 核心文件
- **compiler.h/cpp** - 编译器相关功能
- **backtrace.h/cpp** - 堆栈跟踪
- **atexit.h/cpp** - 退出处理
- **byteorder.h/cpp** - 字节序处理
- **align.h/cpp** - 内存对齐
- **compat.h/cpp** - 兼容性层

### 系统接口
- **sysinfo.h** - 系统信息接口
- **pidfile.h** - PID 文件管理
- **daemon.h** - 守护进程支持
- **thread.h** - 线程管理

## 使用方法

### 堆栈跟踪
```cpp
#include "util/system/backtrace.h"

// 获取当前堆栈
std::vector<void*> frames;
CaptureBacktrace(frames, 32);

// 打印堆栈
PrintBacktrace(frames);

// 获取符号信息
std::string symbol = GetSymbolName(frames[0]);
```

### 编译器特性检测
```cpp
#include "util/system/compiler.h"

// 检查编译器
#if defined(Y_COMPILER_CLANG)
    // Clang 特定代码
#elif defined(Y_COMPILER_GCC)
    // GCC 特定代码
#endif

// 检查特性
#if defined(Y_HAS_BUILTIN_EXPECT)
    // 使用 __builtin_expect
#endif
```

### 字节序处理
```cpp
#include "util/system/byteorder.h"

// 检测字节序
bool is_little = IsLittleEndian();

// 转换字节序
uint32_t value = 0x12345678;
uint32_t swapped = SwapBytes(value);

// 读取网络字节序
uint16_t net_value = ReadNetworkUint16(data);
```

### 内存对齐
```cpp
#include "util/system/align.h"

// 对齐大小
size_t aligned = AlignUp(size, alignment);

// 检查对齐
bool is_aligned = IsAligned(ptr, alignment);

// 获取对齐偏移
size_t offset = AlignOffset(ptr, alignment);
```

### 退出处理
```cpp
#include "util/system/atexit.h"

// 注册退出函数
int handler_id = AtExit([]() {
    std::cout << "Exiting..." << std::endl;
});

// 取消注册
RemoveAtExit(handler_id);
```

## 平台特性

### Linux 支持
- epoll 事件机制
- inotify 文件监控
- splice 零拷贝
- 内存映射优化

### macOS 支持
- kqueue 事件机制
- FSEvents 文件监控
- Grand Central Dispatch
- Foundation 集成

### Windows 支持
- IOCP 异步 I/O
- 完成端口
- Windows API 封装
- Unicode 支持

## 性能优化

### 编译时优化
- 常量折叠
- 内联优化
- 分支预测提示
- SIMD 指令使用

### 运行时优化
- 缓存友好的数据结构
- 避免系统调用
- 批量操作
- 零拷贝技术

## 调试功能

### 调试宏
```cpp
// 断言
Y_ASSERT(condition);

// 未实现提示
Y_UNIMPLEMENTED();

// 不可达代码
Y_UNREACHABLE();
```

### 日志支持
```cpp
// 系统日志
SYSLOG_ERROR("Error occurred");
SYSLOG_INFO("Information");

// 结构化日志
STRUCT_LOG(INFO, "Key", key, "Value", value);
```

## 测试

### 单元测试
```bash
# 运行所有测试
./ut/system_ut

# 运行特定测试
./ut/system_ut --gtest_filter="BacktraceTest.*"
```

### 压力测试
```bash
# 堆栈跟踪压力测试
./ut/backtrace_stress

# 文件系统性能测试
./ut/fs_perf
```

## 最佳实践

1. **错误处理**
   - 使用统一的错误码
   - 提供详细的错误信息
   - 区分可恢复和不可恢复错误

2. **性能考虑**
   - 减少系统调用次数
   - 使用批量操作
   - 考虑缓存影响

3. **可移植性**
   - 使用抽象接口
   - 避免平台特定代码
   - 处理差异行为

## 配置选项

### 编译时配置
```cpp
// 启用调试
#define Y_ENABLE_DEBUG 1

// 禁用某些功能
#define Y_NO_BACKTRACE 0
```

### 运行时配置
```bash
# 设置堆栈跟踪深度
export Y_BACKTRACE_DEPTH=32

# 启用详细日志
export Y_LOG_LEVEL=DEBUG
```

## 依赖项

- 标准 C++ 库
- 平台特定的系统库
- C++11 或更高版本

## 版本兼容性

- Linux 内核 3.10+
- macOS 10.12+
- Windows 10+

## 注意事项

1. **线程安全**
   - 部分函数非线程安全
   - 需要时使用同步机制

2. **资源管理**
   - 及时释放资源
   - 避免资源泄露

3. **信号处理**
   - 异步信号安全函数
   - 避免死锁

## 版本历史

- v3.0: 添加 Windows 支持
- v2.5: 性能优化
- v2.0: 重构 API
- v1.0: 初始版本