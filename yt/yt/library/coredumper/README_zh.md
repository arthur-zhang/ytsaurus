# 核心转储库

## 概述

这个库提供了程序崩溃时生成核心转储文件的功能。它支持异步生成转储、添加备注信息，并提供 Orchid 服务接口用于远程管理。

## 功能特性

### 核心转储生成

- **异步生成**：不阻塞主线程
- **备注支持**：可添加自定义备注信息
- **事件通知**：转储完成事件
- **路径管理**：自动管理转储文件路径

### 监控接口

- **Orchid 集成**：通过 Orchid 服务管理
- **远程访问**：支持远程查看状态
- **实时监控**：转储进度监控

## 文件说明

### 核心文件

- `coredumper.h/cpp` - 核心转储接口和实现
- `config.h/cpp` - 配置定义
- `public.h` - 公共接口声明

### 构建文件

- `CMakeLists.txt` - CMake 构建配置
- `CMakeLists.*.txt` - 针对不同平台的特定构建配置
- `ya.make` - YaMake 构建系统配置

## 核心接口

### ICoreDumper

核心转储器接口：

```cpp
struct ICoreDumper : public virtual TRefCounted {
    // 生成核心转储
    virtual TCoreDump WriteCoreDump(
        const std::vector<TString>& notes,
        const TString& reason) = 0;

    // 创建 Orchid 服务
    virtual const NYTree::IYPathServicePtr&
        CreateOrchidService() const = 0;
};
```

### TCoreDump

核心转储信息：

```cpp
struct TCoreDump {
    TString Path;              // 转储文件路径
    TFuture<void> WrittenEvent; // 写入完成事件
};
```

## 使用示例

### 基本使用

```cpp
#include <yt/yt/library/coredumper/coredumper.h>

using namespace NYT::NCoreDump;

// 创建核心转储器
auto config = New<TCoreDumperConfig>();
config->CoreDumpDirectory = "/var/ytsaurus/coredumps";
config->MaxCoreDumpCount = 10;

auto coredumper = CreateCoreDumper(config);

// 生成核心转储
auto coredump = coredumper->WriteCoreDump(
    {"User report: memory leak", "Debug info"},
    "Memory leak investigation");

// 等待转储完成
WaitFor(coredump.WrittenEvent)
    .ThrowOnError();

// 获取转储文件路径
Cout << "Core dump written to: " << coredump.Path << Endl;
```

### 异常处理中使用

```cpp
try {
    // 危险操作
    DoDangerousOperation();
} catch (const std::exception& e) {
    // 生成带异常信息的转储
    auto coredump = coredumper->WriteCoreDump(
        {TString("Exception: ") + e.what()},
        "Exception in DoDangerousOperation");

    // 等待转储后重新抛出
    WaitFor(coredump.WrittenEvent);
    throw;
}
```

### Orchid 集成

```cpp
// 创建 Orchid 服务
auto orchidService = coredumper->CreateOrchidService();

// 注册到服务的 Orchid 根
orchidRoot->AddChild("coredumper", orchidService);

// 通过 Orchid 访问
// /orchid/coredumper/status
// /orchid/coredumper/dumps
```

## 配置选项

### TCoreDumperConfig

```cpp
struct TCoreDumperConfig {
    TString CoreDumpDirectory = "/tmp";        // 转储目录
    int MaxCoreDumpCount = 10;                // 最大转储数量
    TDuration MaxCoreDumpAge = TDuration::Days(7); // 最大保留时间
    bool EnableAutoCleanup = true;            // 自动清理
    bool CompressCoreDumps = false;           // 压缩转储
    TDuration WriteTimeout = TDuration::Minutes(5); // 写入超时
};
```

## 实现原理

### 转储流程

1. **触发转储**：接收转储请求
2. **创建文件**：在指定目录创建转储文件
3. **写入数据**：异步写入进程内存映像
4. **添加信息**：写入备注和元数据
5. **完成通知**：通过 Future 通知完成

### 文件管理

- **目录创建**：自动创建转储目录
- **文件命名**：使用时间戳和进程ID
- **清理策略**：基于数量和时间的清理
- **路径解析**：处理相对和绝对路径

### 异步处理

- **线程池**：使用专用线程池处理
- **队列管理**：转储请求队列
- **取消机制**：支持取消长时间运行的转储

## Orchid 接口

### 服务树结构

```
/coredumper
  ├── status
  │   ├── enabled          # 是否启用
  │   ├── dump_count       # 转储总数
  │   ├── current_dumps    # 当前转储数
  │   └── last_dump        # 最后转储信息
  ├── dumps
  │   ├── 2023-01-01_12345_001
  │   │   ├── path        # 文件路径
  │   │   ├── size        # 文件大小
  │   │   ├── timestamp   # 创建时间
  │   │   ├── reason      # 转储原因
  │   │   └── notes       # 备注信息
  │   └── ...
  └── config
      ├── directory       # 转储目录
      ├── max_count       # 最大数量
      ├── max_age         # 最大年龄
      └── compress        # 是否压缩
```

### 远程操作

- `@force_dump` - 强制生成转储
- `@cleanup` - 清理旧转储
- `@set_config` - 更新配置

## 性能考虑

### 转储影响

- **内存使用**：转储过程额外内存消耗
- **磁盘IO**：大量磁盘写入操作
- **CPU 开销**：进程镜像生成开销

### 优化策略

- **压缩存储**：减少磁盘占用
- **限制并发**：同时只允许一个转储
- **后台处理**：避免阻塞主流程

## 安全考虑

### 文件权限

- **目录权限**：确保可写权限
- **文件权限**：设置合适的访问权限
- **敏感数据**：注意转储中的敏感信息

### 资源限制

- **磁盘空间**：监控磁盘使用
- **文件数量**：限制转储数量
- **写入速度**：避免 IO 爆发

## 错误处理

### 常见错误

- `EErrorCode::PermissionDenied` - 权限不足
- `EErrorCode::DiskFull` - 磁盘空间不足
- `EErrorCode::Timeout` - 写入超时
- `EErrorCode::ProcessNotFound` - 进程不存在

### 恢复策略

- **重试机制**：自动重试失败的转储
- **降级处理**：失败时的降级方案
- **日志记录**：详细记录错误信息

## 依赖项

- YTsaurus 核心库
- YTsaurus Orchid 服务
- 系统调用接口

## 平台支持

- Linux x86_64
- Linux aarch64

## 最佳实践

### 使用建议

1. **合理配置目录**
   - 使用专用存储
   - 确保足够空间
   - 定期清理

2. **备注信息**
   - 添加有意义的上下文
   - 包含错误详情
   - 便于后续分析

3. **监控管理**
   - 监控转储频率
   - 设置告警阈值
   - 定期检查存储

### 调试技巧

1. **转储分析**
   - 使用 gdb 分析
   - 检查调用栈
   - 查看内存状态

2. **远程调试**
   - 通过 Orchid 查看状态
   - 远程触发转储
   - 下载转储文件

## 未来扩展

计划中的功能：

- **智能清理**：基于使用情况的清理策略
- **压缩格式**：支持多种压缩格式
- **增量转储**：只转储变化部分
- **分布式存储**：存储到分布式文件系统
- **自动分析**：转储后自动分析

## 故障排除

### 常见问题

1. **转储失败**
   - 检查目录权限
   - 确认磁盘空间
   - 查看错误日志

2. **文件损坏**
   - 验证写入完整性
   - 检查磁盘错误
   - 重新生成转储

3. **性能影响**
   - 调整线程优先级
   - 限制 IO 带宽
   - 优化转储策略