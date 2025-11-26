# 命令行参数解析（Getopt）库

功能强大的命令行参数解析和处理库。

## 概述

该库提供了完整的命令行参数解析功能，支持短选项、长选项、参数验证、自动补全等高级特性。适用于构建功能丰富的命令行工具和应用程序。

## 核心特性

### 选项处理
- **短选项**: 支持 `-a`, `-b value` 格式
- **长选项**: 支持 `--option`, `--option=value` 格式
- **参数类型**: 支持无参数、必需参数、可选参数
- **默认值**: 支持设置选项的默认值

### 高级功能
- **自动补全**: 智能的命令行自动补全
- **帮助生成**: 自动生成格式化的帮助信息
- **参数验证**: 内置的参数类型和值验证
- **模式选择**: 支持互斥选项和选项组

### 开发友好
- **类型安全**: 强类型的参数处理
- **错误处理**: 详细的错误信息和异常处理
- **扩展性**: 支持自定义选项类型和验证器

## 主要组件

### 核心头文件
```cpp
#include <library/cpp/getopt/last_getopt.h>      // 主要解析器
#include <library/cpp/getopt/modchooser.h>       // 模式选择器
#include <library/cpp/getopt/opt.h>              // 选项定义
#include <library/cpp/getopt/opt2.h>             // 扩展选项
```

### 基础类
- **TOpts**: 选项集合和管理
- **TOption**: 单个选项的定义和配置
- **TMainClassArgs**: 主应用程序基类

## 使用示例

### 基本用法
```cpp
#include <library/cpp/getopt/last_getopt.h>

class TMyApp: public NLastGetopt::TMainClassArgs {
    bool Verbose_ = false;
    size_t Count_ = 1;
    TString Output_;

protected:
    void RegisterOptions(NLastGetopt::TOpts& opts) override {
        opts.AddHelpOption('h');

        opts.AddLongOption('v', "verbose")
            .Help("enable verbose output")
            .StoreTrue(&Verbose_);

        opts.AddLongOption('c', "count")
            .RequiredArgument("N")
            .DefaultValue("1")
            .Help("repeat operation N times")
            .StoreResult(&Count_);

        opts.AddLongOption('o', "output")
            .RequiredArgument("FILE")
            .Help("output to FILE")
            .StoreResult(&Output_);
    }

public:
    int Run() override {
        if (Verbose_) {
            Cerr << "Verbose mode enabled" << Endl;
        }
        // 执行应用程序逻辑
        return 0;
    }
};

int main(int argc, char** argv) {
    return TMyApp().Run(argc, argv);
}
```

### 高级选项配置
```cpp
void RegisterOptions(NLastGetopt::TOpts& opts) override {
    // 设置程序标题
    opts.SetTitle("My Application -- does something useful");

    // 版本选项
    opts.AddLongOption('V', "version")
        .Help("print version and exit")
        .IfPresentDisableCompletion()
        .NoArgument()
        .Handler([]() {
            Cerr << "MyApp 1.0.0" << Endl;
            exit(0);
        });

    // 带选择的选项
    opts.AddLongOption("mode")
        .RequiredArgument("MODE")
        .Help("operation mode")
        .Choices({
            {"fast", "fast mode"},
            {"safe", "safe mode"},
            {"debug", "debug mode"}
        })
        .StoreResult(&Mode_);

    // 带验证的数字选项
    opts.AddLongOption("port")
        .RequiredArgument("PORT")
        .Help("server port")
        .StoreResult(&Port_)
        .Validator([](const TString& value) {
            int port = FromString<int>(value);
            if (port < 1 || port > 65535) {
                throw NLastGetopt::TException("Port must be between 1 and 65535");
            }
        });
}
```

### 自动补全支持
```cpp
// 自定义补全器
Y_COMPLETER(MyCompleter) {
    // 根据已有参数调整补全选项
    for (int i = 0; i < argc; ++i) {
        if (TStringBuf(argv[i]) == "--mode" && i + 1 < argc) {
            TString mode = argv[i + 1];
            if (mode == "server") {
                AddCompletion("port");
                AddCompletion("bind-address");
            } else if (mode == "client") {
                AddCompletion("server-url");
                AddCompletion("timeout");
            }
            break;
        }
    }
}

void RegisterOptions(NLastGetopt::TOpts& opts) override {
    opts.AddCompletionOption("myapp");  // 启用补全

    opts.AddLongOption("file")
        .RequiredArgument("PATH")
        .Help("input file path")
        .Completer(NLastGetopt::NComp::File());  // 文件路径补全

    opts.AddLongOption("port")
        .RequiredArgument("PORT")
        .Help("server port")
        .Completer(NLastGetopt::NComp::Choice({
            {"8080", "HTTP default"},
            {"80", "HTTP alternate"},
            {"443", "HTTPS"}
        }));
}
```

### 模式选择器
```cpp
#include <library/cpp/getopt/modchooser.h>

class TAdvancedApp: public NLastGetopt::TMainClassArgs {
    using TModeChooser = NLastGetopt::TModChooser<TAdvancedApp>;

    TModeChooser ModeChooser_;

    // 不同模式的处理函数
    int ServerMode() { /* 服务器模式逻辑 */ }
    int ClientMode() { /* 客户端模式逻辑 */ }
    int AdminMode()  { /* 管理模式逻辑 */ }

protected:
    void RegisterOptions(NLastGetopt::TOpts& opts) override {
        ModeChooser_.Init(opts, this, &TAdvancedApp::ServerMode)
            .AddMode("server", &TAdvancedApp::ServerMode, "run as server")
            .AddMode("client", &TAdvancedApp::ClientMode, "run as client")
            .AddMode("admin", &TAdvancedApp::AdminMode, "run administration tool");

        // 全局选项
        opts.AddHelpOption('h');
        opts.AddLongOption('v', "verbose").StoreTrue(&Verbose_);
    }

public:
    int Run() override {
        return ModeChooser_.Run();
    }
};
```

## 选项类型

### 基础选项
```cpp
// 无参数选项（标志）
opts.AddLongOption('v', "verbose")
    .StoreTrue(&Verbose_);

// 必需参数选项
opts.AddLongOption('f', "file")
    .RequiredArgument("FILENAME")
    .StoreResult(&Filename_);

// 可选参数选项
opts.AddLongOption("optimize")
    .OptionalArgument("LEVEL")
    .DefaultValue("2")
    .StoreResult(&OptimizeLevel_);
```

### 复杂选项
```cpp
// 选择列表
opts.AddLongOption("format")
    .RequiredArgument("FORMAT")
    .Choices({
        {"json", "JSON format"},
        {"xml", "XML format"},
        {"text", "plain text"}
    })
    .StoreResult(&Format_);

// 带处理器的选项
opts.AddLongOption("config")
    .RequiredArgument("FILE")
    .Handler([this](const TString& value) {
        LoadConfigFile(value);
    });

// 条件选项
opts.AddLongOption("debug")
    .IfPresentDisableCompletion()
    .NoArgument()
    .Handler([this]() {
        EnableDebugMode();
    });
```

## 输入验证

### 内置验证器
```cpp
// 数值范围验证
opts.AddLongOption("port")
    .RequiredArgument("PORT")
    .StoreResult(&Port_)
    .Validator([](const TString& value) {
        int port = FromString<int>(value);
        if (port < 1 || port > 65535) {
            throw NLastGetopt::TException("Invalid port number");
        }
    });

// 文件存在验证
opts.AddLongOption("input")
    .RequiredArgument("FILE")
    .StoreResult(&InputFile_)
    .Validator([](const TString& value) {
        if (!NFs::Exists(value)) {
            throw NLastGetopt::TException("File does not exist: " + value);
        }
    });
```

### 自定义验证
```cpp
class TMyValidator: public NLastGetopt::IOptionValidator {
public:
    void Validate(const TString& value) const override {
        if (value.empty()) {
            throw NLastGetopt::TException("Value cannot be empty");
        }
        // 自定义验证逻辑
    }
};

opts.AddLongOption("custom")
    .RequiredArgument("VALUE")
    .StoreResult(&CustomValue_)
    .Validator(MakeHolder<TMyValidator>());
```

## 帮助和文档

### 自动帮助生成
```cpp
void RegisterOptions(NLastGetopt::TOpts& opts) override {
    // 程序描述
    opts.SetTitle("My Application -- a sample command-line tool");

    // 选项分组
    auto& inputOpts = opts.AddSection("Input Options");
    inputOpts.AddLongOption('i', "input")
        .RequiredArgument("FILE")
        .Help("specify input file");

    auto& outputOpts = opts.AddSection("Output Options");
    outputOpts.AddLongOption('o', "output")
        .RequiredArgument("FILE")
        .Help("specify output file");

    // 示例用法
    opts.AddSection("Examples")
        .AddExample("process file", "--input data.txt --output result.txt")
        .AddExample("verbose mode", "-v --input data.txt");
}
```

## 错误处理

### 异常处理
```cpp
int main(int argc, char** argv) {
    try {
        return TMyApp().Run(argc, argv);
    } catch (const NLastGetopt::TException& e) {
        Cerr << "Error: " << e.what() << Endl;
        return 1;
    } catch (const std::exception& e) {
        Cerr << "Unexpected error: " << e.what() << Endl;
        return 2;
    }
}
```

## 实际应用示例

### 网络客户端工具
```cpp
class THttpClient: public NLastGetopt::TMainClassArgs {
    TString Url_;
    TString Method_ = "GET";
    TVector<TString> Headers_;
    TMaybe<TString> PostData_;
    size_t Timeout_ = 30000;
    bool FollowRedirects_ = false;

protected:
    void RegisterOptions(NLastGetopt::TOpts& opts) override {
        opts.SetTitle("HTTP Client -- make HTTP requests");

        opts.AddHelpOption();

        opts.AddLongOption('X', "method")
            .RequiredArgument("METHOD")
            .DefaultValue("GET")
            .ChoicesWithCompletion({
                {"GET", "GET request"},
                {"POST", "POST request"},
                {"PUT", "PUT request"},
                {"DELETE", "DELETE request"}
            })
            .StoreResult(&Method_);

        opts.AddLongOption('H', "header")
            .RequiredArgument("HEADER")
            .Help("add custom header")
            .AppendTo(&Headers_);

        opts.AddLongOption('d', "data")
            .RequiredArgument("DATA")
            .Help("request body data")
            .StoreResult(&PostData_);

        opts.AddLongOption('t', "timeout")
            .RequiredArgument("SECONDS")
            .DefaultValue("30")
            .Help("request timeout")
            .StoreResult(&Timeout_);

        opts.AddLongOption('L', "location")
            .Help("follow redirects")
            .StoreTrue(&FollowRedirects_);

        // 位置参数（URL）
        opts.SetFreeArgsNum(1);
        opts.SetFreeArgTitle(0, "URL", "request URL");
    }

public:
    int Run() override {
        // 获取URL位置参数
        Url_ = ParseFreeArgs()[0];

        // 执行HTTP请求逻辑
        MakeHttpRequest();
        return 0;
    }
};
```

## 最佳实践

### 选项命名
- 使用短选项（单字符）表示常用选项
- 使用长选项描述性名称
- 保持命名一致性
- 提供有意义的默认值

### 错误处理
- 提供清晰的错误消息
- 使用适当的异常类型
- 验证输入参数
- 提供使用示例

### 性能考虑
- 延迟初始化复杂选项
- 缓存验证结果
- 避免不必要的字符串操作

## 扩展功能

### 自定义选项类型
```cpp
class TCustomOption: public NLastGetopt::TOption {
public:
    TCustomOption(const char* name, char shortName)
        : TOption(name, shortName)
    {}

    // 自定义解析逻辑
    void Parse(const TString& value) const override {
        // 实现自定义解析
    }
};
```

### 插件系统
```cpp
// 支持插件扩展选项
class TPluginManager {
public:
    void RegisterPlugin(const TString& name, IPlugin* plugin) {
        plugin->RegisterOptions(opts_);
    }
};
```

## 注意事项

1. **内存管理**: 确保选项生命周期正确
2. **线程安全**: 选项解析通常不是线程安全的
3. **国际化**: 考虑多语言支持
4. **向后兼容**: 保持选项接口的稳定性

## 构建和依赖

- **CMake**: 支持 CMake 构建系统
- **兼容性**: 兼容 C++11 及以上标准
- **依赖**: 最小化外部依赖
- **平台**: 支持主流操作系统

这个库为 YTsaurus 项目中的命令行工具提供了统一的参数处理接口，大大简化了命令行应用程序的开发。