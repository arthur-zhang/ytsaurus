# Pipe IO (管道输入输出)

Pipe IO 是 YTsaurus 中提供管道通信功能的库，支持命名管道和匿名管道的创建、管理和异步IO操作。

## 概述

Pipe IO 库提供以下核心功能：
- 命名管道（FIFO）的创建和管理
- 匿名管道的创建和操作
- 异步读写支持
- 管道IO调度器
- 伪终端（PTY）支持

## 核心组件

### 1. TNamedPipe (命名管道)
命名管道的封装，支持跨进程通信：

```cpp
class TNamedPipe : public TRefCounted {
public:
    // 创建新的命名管道
    static TNamedPipePtr Create(
        const TString& path,
        int permissions = 0660,
        std::optional<int> capacity = {});

    // 从现有路径连接命名管道
    static TNamedPipePtr FromPath(const TString& path);

    // 创建异步读取器
    NNet::IConnectionReaderPtr CreateAsyncReader();

    // 创建异步写入器
    NNet::IConnectionWriterPtr CreateAsyncWriter(
        NNet::EDeliveryFencedMode deliveryFencedMode =
        NNet::EDeliveryFencedMode::None);

    // 获取管道路径
    TString GetPath() const;
};
```

### 2. TPipe (匿名管道)
匿名管道的封装，用于父子进程间通信：

```cpp
class TPipe : public TNonCopyable {
public:
    static const int InvalidFD = -1;

    // 关闭读端文件描述符
    void CloseReadFD();

    // 关闭写端文件描述符
    void CloseWriteFD();

    // 创建异步读取器
    NNet::IConnectionReaderPtr CreateAsyncReader();

    // 创建异步写入器
    NNet::IConnectionWriterPtr CreateAsyncWriter();

    // 释放文件描述符所有权
    int ReleaseReadFD();
    int ReleaseWriteFD();

    // 获取文件描述符
    int GetReadFD() const;
    int GetWriteFD() const;
};
```

### 3. TPipeFactory (管道工厂)
用于批量创建匿名管道：

```cpp
class TPipeFactory {
public:
    explicit TPipeFactory(int minFD = 0);

    // 创建新的管道
    TPipe Create();

    // 清理所有保留的文件描述符
    void Clear();
};
```

### 4. TPipeIODispatcher (管道IO调度器)
管理管道的IO操作调度：

```cpp
// 配置结构
struct TPipeIODispatcherConfig : public NYTree::TYsonStruct {
    // 调度器配置参数
    // ...
};

// 动态配置
struct TPipeIODispatcherDynamicConfig : public NYTree::TYsonStruct {
    // 运行时可更新的配置
    // ...
};
```

### 5. TPTY (伪终端)
提供伪终端支持：

```cpp
// 创建伪终端
TPTYPtr CreatePTY(int rows = 24, int cols = 80);

// 获取主从设备
int GetMasterFD() const;
int GetSlaveFD() const;
```

## 使用方法

### 创建命名管道
```cpp
// 创建新的命名管道
auto pipe = TNamedPipe::Create("/tmp/mypipe", 0666);

// 创建异步读写器
auto reader = pipe->CreateAsyncReader();
auto writer = pipe->CreateAsyncWriter();

// 异步读取
auto readFuture = reader->Read();
readFuture.Subscribe([](const TErrorOr<TSharedRef>& result) {
    if (result.IsOK()) {
        auto data = result.Value();
        // 处理数据
    }
});

// 异步写入
auto data = TSharedRef::FromString("Hello, World!");
auto writeFuture = writer->Write(data);
```

### 连接现有命名管道
```cpp
// 连接到已存在的命名管道
auto pipe = TNamedPipe::FromPath("/tmp/existing_pipe");
auto reader = pipe->CreateAsyncReader();

// 读取数据
auto readFuture = reader->Read();
WaitFor(readFuture).ThrowOnError();
auto data = WaitFor(readFuture).ValueOrThrow();
```

### 使用匿名管道
```cpp
// 创建管道工厂
TPipeFactory factory;

// 创建匿名管道
TPipe pipe = factory.Create();

// 获取文件描述符
int readFD = pipe.GetReadFD();
int writeFD = pipe.GetWriteFD();

// 创建异步读写器
auto reader = pipe.CreateAsyncReader();
auto writer = pipe.CreateAsyncWriter();

// 在fork后使用
if (fork() == 0) {
    // 子进程：关闭写端，使用读端
    pipe.CloseWriteFD();
    // 从管道读取
} else {
    // 父进程：关闭读端，使用写端
    pipe.CloseReadFD();
    // 向管道写入
}
```

### 管道IO调度器配置
```cpp
// 获取调度器实例
auto dispatcher = TPipeIODispatcher::Get();

// 配置调度器
auto config = New<TPipeIODispatcherConfig>();
config->SetWorkerThreadCount(4);
config->SetBufferSize(64 * 1024);

// 更新配置
dispatcher->Configure(config);
```

### 使用伪终端
```cpp
// 创建伪终端
auto pty = CreatePTY(24, 80);

int masterFD = pty->GetMasterFD();
int slaveFD = pty->GetSlaveFD();

// 在slave端运行shell
if (fork() == 0) {
    close(masterFD);
    // 设置slave为控制终端
    // 运行shell或程序
} else {
    close(slaveFD);
    // 在master端进行IO
}
```

## 配置

### TNamedPipeConfig
```cpp
struct TNamedPipeConfig : public NYTree::TYsonStruct {
    TString Path;    // 管道路径
    int FD = 0;      // 文件描述符
    bool Write = false; // 是否为写模式
};
```

### 调度器配置
```yaml
pipe_io_dispatcher:
  worker_thread_count: 4         # 工作线程数
  buffer_size: 65536            # 缓冲区大小
  max_pending_operations: 1000  # 最大挂起操作数
```

## 性能优化

### 1. 缓冲区管理
- 合理设置缓冲区大小
- 使用内存池减少分配
- 批量读写减少系统调用

### 2. 异步IO
- 使用异步IO避免阻塞
- 并行处理多个管道
- 合理配置工作线程数

### 3. 文件描述符管理
- 及时关闭不需要的FD
- 使用工厂批量管理FD
- 设置合理的FD下限

## 最佳实践

### 1. 错误处理
```cpp
try {
    auto pipe = TNamedPipe::Create("/tmp/mypipe");
    auto reader = pipe->CreateAsyncReader();
    auto data = WaitFor(reader->Read()).ValueOrThrow();
} catch (const TErrorException& e) {
    YT_LOG_ERROR(e, "Pipe operation failed");
}
```

### 2. 资源管理
```cpp
// 使用RAII自动管理资源
{
    auto pipe = TNamedPipe::Create("/tmp/mypipe");
    // pipe会在作用域结束时自动清理
}
```

### 3. 并发安全
```cpp
// 每个线程使用独立的读写器
auto reader = pipe->CreateAsyncReader();
auto writer = pipe->CreateAsyncWriter();

// 避免共享同一个读写器
```

## 应用场景

### 1. 进程间通信
- 父子进程数据交换
- 管道命令实现
- 数据流处理

### 2. 外部程序集成
- 与系统命令交互
- 实时数据流处理
- 日志收集

### 3. 测试框架
- 模拟输入输出
- 进程行为测试
- 集成测试

## 依赖项

- YTsaurus 核心库 (`yt/yt/core/`)
- 网络库 (`yt/yt/core/net/`)
- YTree 库 (`yt/yt/core/ytree/`)

## 注意事项

1. **权限管理**: 确保创建的管道有正确的权限
2. **文件描述符限制**: 注意系统FD限制
3. **并发访问**: 避免多个写入者同时写入
4. **缓冲区大小**: 根据需求调整缓冲区
5. **错误处理**: 妥善处理IO错误和断开连接
6. **资源清理**: 及时关闭不需要的文件描述符
7. **死锁避免**: 合理设计读写流程避免死锁