# CUDA Core Dump Injection

## 项目描述

CUDA Core Dump Injection 是一个动态链接库（.so 文件），用于拦截和修改 Linux 系统的文件操作调用。该工具专门设计用于处理 GPU 核心转储文件的生成过程，通过拦截 `ftell`、`write` 和 `fwrite` 等系统调用来控制文件位置跟踪和字节计数。

## 功能特性

- **系统调用拦截**：动态拦截标准 C 库的文件操作函数
- **文件描述符跟踪**：为每个文件描述符维护写入字节数统计
- **特定管道处理**：专门处理 GPU 核心转储管道（yt_gpu_core_dump_pipe）
- **透明代理**：对原始调用保持完全兼容，不影响正常功能
- **跨平台支持**：支持 Linux 和 macOS 的多个架构

## 文件说明

- `cuda_core_dump_injection.c` - 主要实现代码，包含系统调用拦截逻辑
- `ya.make` - 构建配置文件，定义了动态库的构建规则
- `CMakeLists.*.txt` - CMake 构建配置文件，支持不同平台

## 实现原理

### 核心机制

该工具使用 LD_PRELOAD 技术在运行时拦截系统调用：

1. **动态符号解析**：使用 `dlsym(RTLD_NEXT, ...)` 获取原始函数地址
2. **延迟绑定**：首次调用时才解析原始函数，提高性能
3. **透明代理**：保持原始函数的所有行为和错误码

### 拦截的函数

#### `ftell` 函数
- 拦截标准 C 库的 `ftell` 调用
- 对于 GPU 核心转储管道，返回内部维护的字节计数而非实际位置
- 通过 `/proc/self/fd/` 确定文件路径

#### `write` 函数
- 拦截低级 `write` 系统调用
- 更新对应文件描述符的字节计数
- 最多跟踪 1024 个文件描述符

#### `fwrite` 函数
- 拦截标准 C 库的 `fwrite` 调用
- 更新 FILE 流对应的文件描述符字节计数
- 正确处理 `size × count` 的总字节数

### 数据结构

```c
// 文件描述符到写入字节数的映射
size_t FdToBytesWritten[MAX_FILE_DESCRIPTORS_PER_PROCESS];
```

## 使用方法

### 编译

```bash
# 使用 ya 工具构建
ya make -t cuda_core_dump_injection

# 或使用 CMake 构建
cmake --build . --target cuda_core_dump_injection
```

### 使用方式

1. **LD_PRELOAD 注入**：
```bash
LD_PRELOAD=./cuda_core_dump_injection.so your_program
```

2. **调试应用**：
```bash
export LD_PRELOAD=/path/to/cuda_core_dump_injection.so
run_your_gpu_application
```

## 应用场景

### GPU 核心转储处理

该工具主要用于：

1. **位置修正**：修正管道文件的 `ftell` 返回值
2. **字节统计**：准确跟踪写入的数据量
3. **兼容性**：确保应用程序与特殊管道的正常交互

### 调试和分析

- GPU 应用程序的调试
- 核心转储文件生成过程的监控
- 文件操作行为的分析

## 技术细节

### 限制和注意事项

- **文件描述符限制**：最多跟踪 1024 个文件描述符
- **特定路径**：仅对包含 "yt_gpu_core_dump_pipe" 的文件路径进行特殊处理
- **Linux 特定**：部分功能（如 `/proc/self/fd/`）仅适用于 Linux 系统

### 性能影响

- 首次调用有轻微延迟（符号解析）
- 后续调用几乎无性能损失
- 内存开销很小（仅数组存储）

### 错误处理

- 保持原始错误码不变
- 处理符号解析失败的情况
- 安全的缓冲区操作

## 安全考虑

- 该工具仅用于调试和开发目的
- 生产环境使用需谨慎评估
- 确保 LD_PRELOAD 设置的安全性
- 验证注入代码的来源和完整性

## 调试技巧

### 验证注入成功

```bash
# 使用 ldd 检查预加载
LD_DEBUG=libs your_program 2>&1 | grep cuda_core_dump_injection

# 检查符号拦截
LD_PRELOAD=./cuda_core_dump_injection.so strace -e trace=write,fwrite,ftell your_program
```

### 日志输出

可以在关键位置添加 `printf` 或 `syslog` 调用来调试拦截行为。

## 依赖项

- 标准 C 库（glibc）
- Linux 系统（推荐）或 macOS
- 动态链接器支持
- `dlfcn.h` 头文件支持

## 相关概念

- **LD_PRELOAD**：Linux 动态链接器功能
- **dlsym**：动态符号解析
- **文件描述符**：Unix I/O 抽象
- **核心转储**：程序崩溃时的内存快照

## 故障排除

### 常见问题

1. **符号解析失败**：检查目标函数是否存在
2. **权限问题**：确保有读取 `/proc/self/fd/` 的权限
3. **架构不匹配**：确保动态库与目标程序架构一致

### 调试命令

```bash
# 检查动态库信息
file cuda_core_dump_injection.so
ldd cuda_core_dump_injection.so

# 查看实际调用
strace -f -e trace=write,fwrite,ftell -o trace.log your_program
```