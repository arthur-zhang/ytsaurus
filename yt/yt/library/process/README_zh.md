# Process (进程管理)

Process 是 YTsaurus 中提供的进程管理库，支持创建、控制和监控子进程，提供了丰富的进程间通信功能。

## 概述

Process 库提供以下核心功能：
- 创建和管理子进程
- 进程间通信（stdin/stdout/stderr）
- 进程生命周期控制
- 异步进程操作
- 子进程包装器

## 核心组件

### 1. TProcessBase (进程基类)
所有进程管理类的基础，提供进程创建和管理的核心功能：

```cpp
class TProcessBase : public TRefCounted {
public:
    explicit TProcessBase(const TString& path);

    // 添加命令行参数
    void AddArgument(TStringBuf arg);
    void AddArguments(std::initializer_list<TStringBuf> args);
    void AddArguments(const std::vector<TString>& args);

    // 添加环境变量
    void AddEnvVar(TStringBuf var);

    // 设置工作目录
    void SetWorkingDirectory(const TString& path);

    // 创建进程组
    void CreateProcessGroup();

    // 获取IO流（纯虚函数，需子类实现）
    virtual NNet::IConnectionWriterPtr GetStdInWriter() = 0;
    virtual NNet::IConnectionReaderPtr GetStdOutReader() = 0;
    virtual NNet::IConnectionReaderPtr GetStdErrReader() = 0;

    // 启动进程
    TFuture<void> Spawn();

    // 终止进程（纯虚函数）
    virtual void Kill(int signal) = 0;

    // 获取进程信息
    int GetProcessId() const;
    bool IsStarted() const;
    bool IsFinished() const;
    TString GetCommandLine() const;
};
```

### 2. TSimpleProcess (简单进程)
简单的进程实现，适用于基本的进程操作：

```cpp
class TSimpleProcess : public TProcessBase {
public:
    explicit TSimpleProcess(
        const TString& path,
        bool copyEnv = true,
        TDuration pollPeriod = TDuration::MilliSeconds(100));

    // IO操作
    void CloseStdin();
    void Close();

    // 终止进程
    void Kill(int signal) override;

protected:
    void DoSpawn() override;
    void CleanUpParent() override;
};
```

### 3. TSubprocess (子进程包装器)
提供更高级的子进程操作接口：

```cpp
class TSubprocess {
public:
    explicit TSubprocess(TString path, bool copyEnv = true);

    // 创建当前进程的生成器
    static TSubprocess CreateCurrentProcessSpawner();

    // 添加参数
    void AddArgument(TStringBuf arg);
    void AddArguments(std::initializer_list<TStringBuf> args);

    // 执行子进程并等待完成
    TSubprocessResult Execute(
        const TSharedRef& input = TSharedRef::MakeEmpty(),
        TDuration timeout = TDuration::Max());

    // 终止进程
    void Kill(int signal);

    // 获取信息
    TString GetCommandLine() const;
    TProcessBasePtr GetProcess() const;
};
```

### 4. TSubprocessResult (执行结果)
子进程执行的结果封装：

```cpp
struct TSubprocessResult {
    TSharedRef Output;  // 标准输出
    TSharedRef Error;   // 标准错误
    TError Status;      // 执行状态
};
```

## 使用方法

### 使用 TSimpleProcess
```cpp
// 创建进程
auto process = New<TSimpleProcess("/bin/ls");

// 添加参数
process->AddArgument("-la");
process->AddArgument("/tmp");

// 设置工作目录
process->SetWorkingDirectory("/home");

// 创建进程组
process->CreateProcessGroup();

// 获取IO流
auto stdinWriter = process->GetStdInWriter();
auto stdoutReader = process->GetStdOutReader();
auto stderrReader = process->GetStdErrReader();

// 启动进程
auto spawnFuture = process->Spawn();

// 异步读取输出
auto readFuture = stdoutReader->Read();
readFuture.Subscribe([](const TErrorOr<TSharedRef>& result) {
    if (result.IsOK()) {
        auto output = result.Value();
        std::cout << TStringBuf(output.Begin(), output.Size()) << std::endl;
    }
});

// 等待进程完成
WaitFor(spawnFuture).ThrowOnError();
```

### 使用 TSubprocess
```cpp
// 简单执行
TSubprocess subprocess("/bin/echo");
subprocess.AddArgument("Hello, World!");

auto result = subprocess.Execute();
if (result.Status.IsOK()) {
    std::cout << "Output: " << TStringBuf(result.Output.Begin(), result.Output.Size()) << std::endl;
}

// 带输入的执行
TSubprocess grep("/bin/grep");
grep.AddArgument("pattern");
grep.AddArgument("-");

TString input = "line1\npattern\nline3\n";
auto inputRef = TSharedRef::FromString(input);
auto result = grep.Execute(inputRef);

// 带超时的执行
TSubprocess longRunning("/bin/sleep");
longRunning.AddArgument("10");

try {
    auto result = longRunning.Execute(TSharedRef::MakeEmpty(), TDuration::Seconds(5));
} catch (const TErrorException& e) {
    if (e.GetErrorCode() == EErrorCode::Timeout) {
        std::cout << "Process timed out" << std::endl;
        longRunning.Kill(9); // SIGKILL
    }
}
```

### 进程管理
```cpp
// 查找二进制路径
auto result = ResolveBinaryPath("ls");
if (result.IsOK()) {
    std::cout << "Found at: " << result.Value() << std::endl;
}

// 通过PID终止进程
bool killed = TryKillProcessByPid(12345, SIGTERM);
if (killed) {
    std::cout << "Process killed successfully" << std::endl;
}
```

### 便捷函数
```cpp
// 运行简单命令
RunSubprocess({"/bin/echo", "Hello"});
RunSubprocess({"/bin/ls", "-la", "/tmp"});
```

## 高级用法

### 1. 管道连接
```cpp
// 创建两个进程，通过管道连接
auto cat = New<TSimpleProcess>("/bin/cat");
cat->AddArgument("input.txt");

auto grep = New<TSimpleProcess>("/bin/grep");
grep->AddArgument("pattern");

// 连接 cat 的输出到 grep 的输入
auto catOutput = cat->GetStdOutReader();
auto grepInput = grep->GetStdInWriter();

// 启动进程
auto catFuture = cat->Spawn();
auto grepFuture = grep->Spawn();

// 转发数据
catOutput->Read().Subscribe([grepInput] (const auto& result) {
    if (result.IsOK()) {
        grepInput->Write(result.Value());
    } else {
        grepInput->Close();
    }
});
```

### 2. 批量进程管理
```cpp
class ProcessPool {
public:
    void AddProcess(const TString& path, const std::vector<TString>& args) {
        auto process = New<TSimpleProcess>(path);
        process->AddArguments(args);
        processes_.push_back(process);
    }

    TFuture<void> RunAll() {
        std::vector<TFuture<void>> futures;
        for (auto& process : processes_) {
            futures.push_back(process->Spawn());
        }
        return AllSucceeded(futures);
    }

    void KillAll(int signal) {
        for (auto& process : processes_) {
            process->Kill(signal);
        }
    }

private:
    std::vector<TSimpleProcessPtr> processes_;
};
```

### 3. 实时输出处理
```cpp
// 创建带有实时输出处理的进程
class ProcessWithOutputHandler {
public:
    ProcessWithOutputHandler(const TString& path) {
        process_ = New<TSimpleProcess>(path);
    }

    void Run() {
        auto stdoutReader = process_->GetStdOutReader();
        auto stderrReader = process_->GetStdErrReader();

        // 设置输出处理回调
        stdoutReader->Read().Subscribe(
            BIND(&ProcessWithOutputHandler::HandleStdout, this));

        stderrReader->Read().Subscribe(
            BIND(&ProcessWithOutputHandler::HandleStderr, this));

        // 启动进程
        process_->Spawn();
    }

private:
    void HandleStdout(const TErrorOr<TSharedRef>& result) {
        if (result.IsOK()) {
            auto output = result.Value();
            OnStdout(TStringBuf(output.Begin(), output.Size()));

            // 继续读取
            process_->GetStdOutReader()->Read().Subscribe(
                BIND(&ProcessWithOutputHandler::HandleStdout, this));
        }
    }

    void HandleStderr(const TErrorOr<TSharedRef>& result) {
        if (result.IsOK()) {
            auto error = result.Value();
            OnStderr(TStringBuf(error.Begin(), error.Size()));

            // 继续读取
            process_->GetStdErrReader()->Read().Subscribe(
                BIND(&ProcessWithOutputHandler::HandleStderr, this));
        }
    }

    virtual void OnStdout(TStringBuf output) {
        std::cout << output;
    }

    virtual void OnStderr(TStringBuf error) {
        std::cerr << error;
    }

    TSimpleProcessPtr process_;
};
```

## 错误处理

```cpp
// 捕获和处理进程错误
try {
    auto process = New<TSimpleProcess>("/nonexistent/path");
    auto future = process->Spawn();
    WaitFor(future).ThrowOnError();
} catch (const TErrorException& e) {
    switch (e.GetErrorCode()) {
        case EErrorCode::ProcessNotFound:
            std::cerr << "Binary not found" << std::endl;
            break;
        case EErrorCode::ProcessFailed:
            std::cerr << "Process failed: " << e.GetMessage() << std::endl;
            break;
        case EErrorCode::ProcessTimeout:
            std::cerr << "Process timed out" << std::endl;
            break;
        default:
            std::cerr << "Unknown error: " << e.GetMessage() << std::endl;
    }
}
```

## 性能考虑

### 1. 内存管理
- 使用智能指针自动管理进程生命周期
- 及时关闭不需要的文件描述符
- 批量处理减少系统调用

### 2. 并发执行
- 支持多个进程并行运行
- 使用异步IO避免阻塞
- 合理控制并发进程数量

### 3. 资源限制
- 监控进程资源使用
- 设置合理的超时时间
- 及时清理僵尸进程

## 安全注意事项

1. **路径验证**: 验证二进制文件路径的安全性
2. **参数注入**: 防止命令注入攻击
3. **权限控制**: 使用最小权限原则
4. **资源限制**: 限制进程资源使用
5. **信号处理**: 正确处理信号和进程终止

## 最佳实践

1. **错误处理**: 总是检查进程执行结果
2. **资源清理**: 确保文件描述符和进程被正确清理
3. **超时设置**: 为长时间运行的进程设置超时
4. **日志记录**: 记录进程执行的详细信息
5. **测试覆盖**: 编写充分的单元测试

## 依赖项

- YTsaurus 核心库 (`yt/yt/core/`)
- Pipe IO 库 (`yt/yt/library/pipe_io/`)
- 网络库 (`yt/yt/core/net/`)

## 注意事项

1. **平台依赖**: 某些功能可能依赖于特定操作系统
2. **信号处理**: 注意信号的跨平台差异
3. **文件描述符**: 注意系统文件描述符限制
4. **进程组**: 正确使用进程组避免孤儿进程
5. **僵尸进程**: 及时处理已终止的子进程