# Program (程序框架)

Program 是 YTsaurus 中提供的应用程序框架，为开发命令行工具和服务提供了统一的基础设施。

## 概述

Program 框架提供以下核心功能：
- 命令行参数解析
- 配置文件管理
- 版本和构建信息处理
- 优雅的错误处理和退出机制
- 多种程序 Mixin 支持

## 核心组件

### 1. TProgram (程序基类)
所有程序的基础类：

```cpp
class TProgram {
public:
    TProgram();
    virtual ~TProgram();

    // 运行程序（永不返回）
    [[noreturn]]
    int Run(int argc, const char** argv);

    // 处理版本和构建信息
    void HandleVersionAndBuild();

    // 非优雅终止程序
    [[noreturn]]
    static void Abort(int code) noexcept;

    template <class E>
        requires std::is_enum_v<E>
    [[noreturn]]
    static void Abort(E exitCode) noexcept;

protected:
    NLastGetopt::TOpts Opts_;  // 命令行选项

    // 必须实现的运行方法
    virtual void DoRun() = 0;

    // 错误处理
    virtual void OnError(const TString& message) noexcept;

    // 退出处理
    [[noreturn]]
    void Exit(int code) noexcept;

    // 版本信息
    [[noreturn]]
    void PrintYTVersionAndExit();
    [[noreturn]]
    virtual void PrintVersionAndExit();
    [[noreturn]]
    void PrintBuildAndExit();
};
```

### 2. TProgramConfigMixin (配置 Mixin)
提供配置文件支持：

```cpp
template <class TConfig, class TDynamicConfig = void>
class TProgramConfigMixin : public virtual TProgramMixinBase {
protected:
    explicit TProgramConfigMixin(
        NLastGetopt::TOpts& opts,
        bool required = true,
        const TString& argumentName = "config");

    // 获取配置
    const TConfigPtr& GetConfig() const;
    const TDynamicConfigPtr& GetDynamicConfig() const;

    // 配置更新回调
    virtual void OnDynamicConfigChanged(
        const TDynamicConfigPtr& oldConfig,
        const TDynamicConfigPtr& newConfig);
};
```

### 3. TProgramMixinBase (Mixin 基类)
所有 Mixin 的基础：

```cpp
class TProgramMixinBase {
protected:
    // 获取程序选项
    NLastGetopt::TOpts& GetOpts();

    // 获取程序对象
    TProgram* GetProgram();
};
```

### 4. 专用 Mixin 类

#### TProgramPDeathSigMixin
处理父进程死亡信号：
```cpp
class TProgramPDeathSigMixin : public virtual TProgramMixinBase {
protected:
    TProgramPDeathSigMixin(NLastGetopt::TOpts& opts);
    void EnableParentDeathSignal(int signal = SIGHUP);
};
```

#### TProgramSetsidMixin
创建新会话：
```cpp
class TProgramSetsidMixin : public virtual TProgramMixinBase {
protected:
    TProgramSetsidMixin(NLastGetopt::TOpts& opts);
    void CreateNewSession();
};
```

## 使用方法

### 基本程序
```cpp
#include <yt/yt/library/program/program.h>

class MyProgram : public NYT::TProgram {
public:
    MyProgram() {
        // 添加命令行选项
        Opts_.AddLongOption('v', "verbose", "Enable verbose output")
            .SetFlag(&Verbose_);
    }

protected:
    void DoRun() override {
        // 获取解析结果
        const auto& parseResult = GetOptsParseResult();

        if (Verbose_) {
            Cerr << "Verbose mode enabled" << Endl;
        }

        // 获取剩余参数
        auto freeArgs = parseResult.GetFreeArgs();
        for (const auto& arg : freeArgs) {
            ProcessFile(arg);
        }

        // 正常退出
        Exit(0);
    }

private:
    bool Verbose_ = false;

    void ProcessFile(const TString& path) {
        Cerr << "Processing: " << path << Endl;
    }
};

int main(int argc, const char** argv) {
    MyProgram program;
    return program.Run(argc, argv);
}
```

### 带配置文件的程序
```cpp
#include <yt/yt/library/program/program_config_mixin.h>

struct TMyConfig : public NYTree::TYsonStruct {
    TString InputPath;
    TString OutputPath;
    int ThreadCount = 1;

    REGISTER_YSON_STRUCT(TMyConfig);

    static void Register(TRegistrar registrar) {
        registrar.Parameter("input_path", &TThis::InputPath)
            .Default();
        registrar.Parameter("output_path", &TThis::OutputPath)
            .Default();
        registrar.Parameter("thread_count", &TThis::ThreadCount)
            .Default(1);
    }
};

class MyConfiguredProgram : public TProgram,
                           public TProgramConfigMixin<TMyConfig> {
public:
    MyConfiguredProgram()
        : TProgramConfigMixin<TMyConfig>(Opts_)
    { }

protected:
    void DoRun() override {
        const auto& config = GetConfig();

        if (!config->InputPath) {
            throw std::runtime_error("Input path is required");
        }

        std::cout << "Input: " << config->InputPath << std::endl;
        std::cout << "Output: " << config->OutputPath << std::endl;
        std::cout << "Threads: " << config->ThreadCount << std::endl;

        ProcessFiles(*config);
        Exit(0);
    }

private:
    void ProcessFiles(const TMyConfig& config) {
        // 实现文件处理逻辑
    }
};

int main(int argc, const char** argv) {
    MyConfiguredProgram program;
    return program.Run(argc, argv);
}
```

### 带动态配置的程序
```cpp
struct TMyDynamicConfig : public NYTree::TYsonStruct {
    std::optional<int> LogLevel;
    std::optional<int> MaxConnections;

    REGISTER_YSON_STRUCT(TMyDynamicConfig);

    static void Register(TRegistrar registrar) {
        registrar.Parameter("log_level", &TThis::LogLevel);
        registrar.Parameter("max_connections", &TThis::MaxConnections);
    }
};

class MyDynamicProgram : public TProgram,
                         public TProgramConfigMixin<TMyConfig, TMyDynamicConfig> {
public:
    MyDynamicProgram()
        : TProgramConfigMixin<TMyConfig, TMyDynamicConfig>(Opts_)
    { }

protected:
    void DoRun() override {
        StartConfigWatcher();

        // 程序主循环
        while (true) {
            DoWork();
            Sleep(TDuration::Seconds(1));
        }
    }

    void OnDynamicConfigChanged(
        const TMyDynamicConfigPtr& oldConfig,
        const TMyDynamicConfigPtr& newConfig) override {

        if (newConfig->LogLevel &&
            (!oldConfig->LogLevel || *newConfig->LogLevel != *oldConfig->LogLevel)) {
            SetLogLevel(*newConfig->LogLevel);
        }

        if (newConfig->MaxConnections) {
            UpdateMaxConnections(*newConfig->MaxConnections);
        }
    }
};
```

### 使用系统 Mixin
```cpp
class MyDaemonProgram : public TProgram,
                        public TProgramConfigMixin<TMyConfig>,
                        public TProgramSetsidMixin,
                        public TProgramPDeathSigMixin {
public:
    MyDaemonProgram()
        : TProgramConfigMixin<TMyConfig>(Opts_)
        , TProgramSetsidMixin(Opts_)
        , TProgramPDeathSigMixin(Opts_)
    { }

protected:
    void DoRun() override {
        // 创建新会话
        CreateNewSession();

        // 启用父进程死亡信号
        EnableParentDeathSignal();

        // 守护进程主逻辑
        RunDaemon();
    }
};
```

## 命令行选项

### 内置选项

#### 版本信息
- `--version`: 打印程序版本
- `--yt-version`: 打印 YT 版本
- `--build`: 打印构建信息
- `--build --yson`: 以 YSON 格式打印构建信息

#### 配置文件相关
- `--config <file>`: 指定配置文件路径
- `--config-schema`: 打印配置模式
- `--config-template`: 打印配置模板
- `--config-actual`: 打印实际配置
- `--config-unrecognized`: 打印未识别的配置项
- `--config-unrecognized-strategy`: 设置未识别项处理策略

### 添加自定义选项
```cpp
// 标志选项
Opts_.AddLongOption('d', "debug", "Enable debug mode")
    .SetFlag(&DebugMode_);

// 带参数选项
Opts_.AddLongOption('p', "port", "Server port")
    .RequiredArgument("PORT")
    .StoreResult(&Port_);

// 可选参数
Opts_.AddLongOption("timeout", "Request timeout (seconds)")
    .OptionalArgument("SECONDS")
    .DefaultValue(30)
    .StoreResult(&Timeout_);

// 回调处理
Opts_.AddLongOption("dump-config", "Dump configuration")
    .Handler0([&] { DumpConfig(); });
```

## 构建信息

### 获取构建信息
```cpp
// 程序启动时
void HandleVersionAndBuild() {
    if (PrintYTVersion_) {
        PrintYTVersionAndExit();
    }

    if (PrintVersion_) {
        PrintVersionAndExit();
    }

    if (PrintBuild_) {
        PrintBuildAndExit();
    }
}

// 自定义版本信息
void PrintVersionAndExit() override {
    if (UseYson_) {
        NYson::TYsonWriter writer(&Cout, NYson::EYsonFormat::Text);
        writer.OnBeginMap();
        writer.OnKeyedItem("version");
        writer.OnStringScalar("1.0.0");
        writer.OnKeyedItem("build_date");
        writer.OnStringScalar(__DATE__);
        writer.OnEndMap();
    } else {
        Cout << "MyProgram version 1.0.0" << Endl;
    }
    Exit(0);
}
```

## 错误处理

### 异常处理
```cpp
void DoRun() override {
    try {
        // 程序逻辑
        DoWork();
    } catch (const std::exception& e) {
        OnError(TString("Error: ") + e.what());
        Exit(1);
    }
}

void OnError(const TString& message) noexcept override {
    try {
        Cerr << message << Endl;
        if (CrashOnError_) {
            // 生成 core dump
            std::abort();
        }
    } catch (...) {
        // 忽略错误处理中的错误
    }
}
```

### 优雅退出
```cpp
// 正常退出
Exit(0);

// 带错误码退出
Exit(1);

// 枚举类型退出码
enum class EExitCode {
    Success = 0,
    Error = 1,
    ConfigError = 2,
};
Exit(EExitCode::ConfigError);

// 紧急退出（不调用析构函数）
Abort(1);
```

## 最佳实践

### 1. 配置管理
```cpp
// 提供默认配置
struct TMyConfig : public NYTree::TYsonStruct {
    bool EnableFeature = true;

    static void Register(TRegistrar registrar) {
        registrar.Parameter("enable_feature", &TThis::EnableFeature)
            .Default(true)
            .Describe("Enable experimental feature");
    }
};

// 验证配置
void DoRun() override {
    const auto& config = GetConfig();

    if (config->EnableFeature && !IsFeatureSupported()) {
        throw std::runtime_error("Feature not supported");
    }
}
```

### 2. 日志集成
```cpp
#include <yt/yt/core/logging/log.h>

class MyProgram : public TProgram {
protected:
    void DoRun() override {
        // 初始化日志
        NLogging::TLogManager::Get()->ConfigureFromEnv();

        auto Logger = NLogging::TLogger("MyProgram");

        try {
            YT_LOG_INFO("Starting program");
            DoWork();
            YT_LOG_INFO("Program finished successfully");
        } catch (const std::exception& e) {
            YT_LOG_ERROR(e, "Program failed");
            Exit(1);
        }
    }
};
```

### 3. 信号处理
```cpp
#include <csignal>

class MyProgram : public TProgram {
public:
    MyProgram() {
        std::signal(SIGINT, [](int) {
            std::cout << "Received SIGINT, shutting down..." << std::endl;
            // 设置全局退出标志
        });

        std::signal(SIGTERM, [](int) {
            std::cout << "Received SIGTERM, shutting down..." << std::endl;
            // 设置全局退出标志
        });
    }
};
```

## 依赖项

- YTsaurus 核心库 (`yt/yt/core/`)
- GetOpt 库 (`library/cpp/getopt/`)
- YTree 库 (`yt/yt/core/ytree/`)
- 系统退出库 (`library/cpp/yt/system/`)

## 注意事项

1. **Run 方法**: `Run` 方法永不返回，会调用 `Exit` 终止程序
2. **内存管理**: 使用 `Abort` 时不会调用析构函数
3. **信号安全**: 在信号处理中只能调用异步信号安全函数
4. **配置验证**: 在 `DoRun` 开始时验证配置的完整性
5. **退出代码**: 使用有意义的退出代码，0 表示成功，非 0 表示错误类型