# Config 配置管理库

## 项目描述

Config 库是 YTsaurus 中的统一配置管理系统，提供强大的配置文件解析、处理和转换功能。该库支持多种配置格式（JSON、INI、Lua、Markup），并提供了灵活的配置项访问和类型转换机制。

通过统一的设计接口，Config 库使得应用程序可以轻松处理各种来源的配置数据，支持复杂的嵌套结构、类型安全的配置访问，以及配置验证和错误处理。

## 核心特性

### 📋 多格式支持
- **JSON**: 标准 JSON 格式配置文件
- **INI**: 传统 INI 配置格式
- **Lua**: Lua 脚本配置文件
- **Markup**: YTsaurus 自定义标记格式
- **自动检测**: 智能识别配置文件格式

### 🔧 类型安全
- 强类型配置值访问
- 自动类型转换
- 编译时类型检查
- 运行时类型验证

### 🎯 灵活访问
- 支持嵌套配置结构
- 点分隔符路径访问
- 数组和字典操作
- 默认值支持

### ⚡ 高性能处理
- 高效的解析器实现
- 内存优化的数据结构
- 流式处理支持
- 配置预处理机制

## 主要组件

### 1. 配置核心类 (TConfig)
```cpp
class TConfig {
public:
    TConfig();                              // 默认构造
    TConfig(IValue* v);                     // 值构造

    // 类型检查
    template <class T>
    bool IsA() const;                       // 检查是否为指定类型
    bool IsNumeric() const;                 // 检查是否为数值类型
    bool IsNull() const noexcept;           // 检查是否为空值

    // 值访问
    template <class T>
    const T& Get() const;                   // 获取类型化值
    template <class T>
    T As() const;                           // 类型转换
    template <class T>
    T As(T def) const;                      // 带默认值的类型转换

    // 字典操作（假设值为字典类型）
    bool Has(const TStringBuf& key) const;  // 检查键是否存在
    const TConfig& operator[](const TStringBuf& key) const; // 键访问
    const TConfig& At(const TStringBuf& key) const;         // 带边界检查的键访问

    // 数组操作（假设值为数组类型）
    const TConfig& operator[](size_t index) const;  // 索引访问
    size_t GetArraySize() const;                     // 获取数组大小

    // 格式解析
    static TConfig FromIni(IInputStream& in, const TGlobals& g = TGlobals());
    static TConfig FromJson(IInputStream& in, const TGlobals& g = TGlobals());
    static TConfig FromLua(IInputStream& in, const TGlobals& g = TGlobals());
    static TConfig FromMarkup(IInputStream& in, const TGlobals& g = TGlobals());

    // 输出
    void ToJson(IOutputStream& out) const;    // JSON 输出
    void DumpJson(IOutputStream& out) const;  // 格式化 JSON 输出
    void DumpLua(IOutputStream& out) const;   // Lua 格式输出

private:
    TIntrusivePtr<IValue> V_;                 // 值对象
};
```

### 2. 值接口 (IValue)
```cpp
class IValue: public TAtomicRefCount<IValue> {
public:
    virtual ~IValue() = default;

    // 类型信息
    virtual bool IsA(const std::type_info& info) const = 0;
    virtual TString TypeName() const = 0;
    virtual void* Ptr() const = 0;

    // 值转换
    virtual ui64 AsUInt() const = 0;          // 转换为无符号整数
    virtual i64 AsInt() const = 0;            // 转换为有符号整数
    virtual double AsDouble() const = 0;      // 转换为浮点数
    virtual bool AsBool() const = 0;          // 转换为布尔值
    virtual TString AsString() const = 0;     // 转换为字符串

    // 输出
    virtual void ToJson(IOutputStream& out) const = 0; // JSON 输出
};
```

### 3. 数组类型 (TArray)
```cpp
struct TArray: public TDeque<TConfig> {
    const TConfig& Index(size_t index) const; // 安全索引访问
    const TConfig& At(size_t index) const;    // 带边界检查的访问
};
```

### 4. 字典类型 (TDict)
```cpp
struct TDict: public THashMap<TString, TConfig> {
    const TConfig& Find(const TStringBuf& key) const; // 查找键
    const TConfig& At(const TStringBuf& key) const;   // 带边界检查的访问
};
```

### 5. 异常类层次
```cpp
class TConfigError: public TWithBackTrace<yexception> {
    // 基础配置错误
};

class TConfigParseError: public TConfigError {
    // 配置解析错误
};

class TTypeMismatch: public TConfigError {
    // 类型不匹配错误
};
```

## 支持的配置格式

### 1. JSON 格式
```json
{
    "server": {
        "host": "localhost",
        "port": 8080,
        "ssl": true
    },
    "database": {
        "connection": "postgresql://user:pass@localhost/db",
        "timeout": 30.5
    },
    "features": ["auth", "logging", "metrics"]
}
```

### 2. INI 格式
```ini
[server]
host = localhost
port = 8080
ssl = true

[database]
connection = postgresql://user:pass@localhost/db
timeout = 30.5

[features]
auth = true
logging = true
metrics = true
```

### 3. Lua 格式
```lua
server = {
    host = "localhost",
    port = 8080,
    ssl = true
}

database = {
    connection = "postgresql://user:pass@localhost/db",
    timeout = 30.5
}

features = {"auth", "logging", "metrics"}
```

### 4. Markup 格式
```markup
server {
    host "localhost"
    port 8080
    ssl true
}

database {
    connection "postgresql://user:pass@localhost/db"
    timeout 30.5
}

features {
    auth
    logging
    metrics
}
```

## 使用示例

### 基本配置读取
```cpp
#include <library/cpp/config/config.h>
using namespace NConfig;

// 从文件读取配置
TFileInput file("config.json");
TConfig config = TConfig::FromJson(file);

// 访问配置项
TString host = config["server"]["host"].Get<TString>();
int port = config["server"]["port"].Get<int>();
bool ssl = config["server"]["ssl"].Get<bool>();

// 带默认值的访问
double timeout = config["database"]["timeout"].As(30.0);
TString backupPath = config["backup"]["path"].As<TString>("/tmp/backup");
```

### 类型转换和验证
```cpp
// 类型安全访问
try {
    int port = config["server"]["port"].Get<int>();
    if (port < 1 || port > 65535) {
        throw yexception() << "Invalid port number: " << port;
    }
} catch (const TTypeMismatch& e) {
    throw yexception() << "Port must be a number: " << e.what();
}

// 灵活的类型转换
TString portStr = config["server"]["port"].As<TString>();
double portAsDouble = config["server"]["port"].As<double>();
```

### 数组和字典操作
```cpp
// 数组操作
if (config.Has("features")) {
    const TArray& features = config["features"].Get<TArray>();
    for (size_t i = 0; i < features.size(); ++i) {
        TString feature = features[i].Get<TString>();
        Cout << "Feature: " << feature << Endl;
    }
}

// 字典操作
const TDict& serverConfig = config["server"].Get<TDict>();
for (const auto& [key, value] : serverConfig) {
    Cout << "Config key: " << key << Endl;
}
```

### 多格式支持
```cpp
// 自动检测格式
TConfig DetectAndLoad(const TString& filename) {
    TFileInput file(filename);

    if (filename.EndsWith(".json")) {
        return TConfig::FromJson(file);
    } else if (filename.EndsWith(".ini")) {
        return TConfig::FromIni(file);
    } else if (filename.EndsWith(".lua")) {
        return TConfig::FromLua(file);
    } else if (filename.EndsWith(".markup")) {
        return TConfig::FromMarkup(file);
    } else {
        return TConfig::FromStream(file); // 自动检测
    }
}

// 字符串直接解析
TString jsonStr = R"({"key": "value", "number": 42})";
TConfig config = TConfig::ReadJson(jsonStr);
```

### 配置预处理和全局变量
```cpp
// 设置全局变量
TConfig::TGlobals globals;
globals["ENV"] = NJson::TJsonValue("production");
globals["VERSION"] = NJson::TJsonValue("1.2.3");

// 使用全局变量解析配置
TFileInput file("config.lua");
TConfig config = TConfig::FromLua(file, globals);
```

### 配置序列化和输出
```cpp
// 输出为 JSON
TStringOutput jsonOut;
config.DumpJson(jsonOut);
Cout << "Pretty JSON: " << jsonOut.Str() << Endl;

// 输出为 Lua
TStringOutput luaOut;
config.DumpLua(luaOut);
Cout << "Lua format: " << luaOut.Str() << Endl;
```

## 高级功能

### 1. 配置合并
```cpp
// 配置合并（使用 Or 操作符）
TConfig baseConfig = TConfig::FromJson(TFileInput("base.json"));
TConfig userConfig = TConfig::FromJson(TFileInput("user.json"));
TConfig finalConfig = userConfig.Or(baseConfig);
```

### 2. 动态配置访问
```cpp
// 动态路径访问
TConfig GetValueByPath(const TConfig& config, const TString& path) {
    TVector<TString> parts = StringSplitter(path).Split('.');
    TConfig current = config;

    for (const auto& part : parts) {
        if (!current.Has(part)) {
            return TConfig(); // 返回空配置
        }
        current = current[part];
    }

    return current;
}

// 使用示例
TString dbHost = GetValueByPath(config, "database.connection.host").As<TString>();
```

### 3. 配置验证框架
```cpp
// 配置验证器
class ConfigValidator {
public:
    void Require(const TConfig& config, const TString& path, const std::type_info& type) {
        TConfig value = GetValueByPath(config, path);
        if (value.IsNull() || !value.IsA(type)) {
            throw yexception() << "Required config missing or wrong type: " << path;
        }
    }

    void ValidateRange(const TConfig& config, const TString& path, int min, int max) {
        int value = config[path].Get<int>();
        if (value < min || value > max) {
            throw yexception() << "Config value out of range: " << path << " = " << value;
        }
    }
};

// 使用验证器
ConfigValidator validator;
validator.Require(config, "server.port", typeid(int));
validator.ValidateRange(config, "server.port", 1, 65535);
```

### 4. 配置热重载
```cpp
// 配置热重载管理器
class ConfigManager {
private:
    TConfig config_;
    TString filename_;
    std::chrono::steady_clock::time_point lastModified_;

public:
    ConfigManager(const TString& filename) : filename_(filename) {
        ReloadConfig();
    }

    void ReloadConfig() {
        try {
            TFile file(filename_);
            auto newModified = std::chrono::steady_clock::now();

            TConfig newConfig = DetectAndLoad(filename_);
            config_ = newConfig;
            lastModified_ = newModified;

            Cout << "Config reloaded successfully" << Endl;
        } catch (const std::exception& e) {
            Cerr << "Failed to reload config: " << e.what() << Endl;
        }
    }

    const TConfig& GetConfig() const { return config_; }

    void CheckForUpdates() {
        TFile file(filename_);
        if (file.GetModificationTime() > lastModified_) {
            ReloadConfig();
        }
    }
};
```

## 错误处理

### 异常类型
```cpp
try {
    TConfig config = TConfig::FromJson(input);
    int port = config["server"]["port"].Get<int>();
} catch (const TConfigParseError& e) {
    // 配置解析错误
    Cerr << "Failed to parse config: " << e.what() << Endl;
} catch (const TTypeMismatch& e) {
    // 类型不匹配错误
    Cerr << "Type mismatch: " << e.what() << Endl;
} catch (const TConfigError& e) {
    // 其他配置错误
    Cerr << "Config error: " << e.what() << Endl;
}
```

### 安全访问模式
```cpp
// 安全的配置访问模板
template <typename T>
T SafeGetConfig(const TConfig& config, const TString& path, T defaultValue = T{}) {
    try {
        TConfig value = GetValueByPath(config, path);
        return value.IsNull() ? defaultValue : value.As<T>();
    } catch (const std::exception&) {
        return defaultValue;
    }
}

// 使用示例
int port = SafeGetConfig<int>(config, "server.port", 8080);
TString host = SafeGetConfig<TString>(config, "server.host", "localhost");
```

## 性能优化

### 1. 缓存机制
```cpp
// 配置值缓存
class CachedConfig {
private:
    TConfig config_;
    THashMap<TString, std::any> cache_;

public:
    template <typename T>
    T GetCached(const TString& path, T defaultValue = T{}) {
        auto it = cache_.find(path);
        if (it != cache_.end()) {
            return std::any_cast<T>(it->second);
        }

        T value = SafeGetConfig<T>(config_, path, defaultValue);
        cache_[path] = value;
        return value;
    }
};
```

### 2. 延迟加载
```cpp
// 延迟配置加载
class LazyConfig {
private:
    mutable TConfig config_;
    mutable bool loaded_ = false;
    TString filename_;

    void EnsureLoaded() const {
        if (!loaded_) {
            config_ = DetectAndLoad(filename_);
            loaded_ = true;
        }
    }

public:
    LazyConfig(const TString& filename) : filename_(filename) {}

    const TConfig& GetConfig() const {
        EnsureLoaded();
        return config_;
    }
};
```

## 最佳实践

### 1. 配置文件组织
```json
{
    "application": {
        "name": "myapp",
        "version": "1.0.0",
        "environment": "${ENV:development}"
    },
    "server": {
        "host": "${HOST:localhost}",
        "port": 8080,
        "workers": 4
    },
    "logging": {
        "level": "INFO",
        "file": "/var/log/myapp.log"
    }
}
```

### 2. 配置验证
```cpp
// 启动时配置验证
void ValidateApplicationConfig(const TConfig& config) {
    // 必需项检查
    if (!config.Has("application.name")) {
        throw yexception() << "Application name is required";
    }

    // 类型检查
    if (!config["server"]["port"].IsA<int>()) {
        throw yexception() << "Server port must be an integer";
    }

    // 范围检查
    int port = config["server"]["port"].Get<int>();
    if (port < 1 || port > 65535) {
        throw yexception() << "Invalid port number: " << port;
    }
}
```

### 3. 环境特定配置
```cpp
// 环境配置管理
class EnvironmentConfig {
public:
    static TConfig LoadForEnvironment(const TString& env) {
        TConfig::TGlobals globals;
        globals["ENV"] = NJson::TJsonValue(env);

        // 加载基础配置
        TFileInput baseFile("config/base.json");
        TConfig config = TConfig::FromJson(baseFile, globals);

        // 加载环境特定配置
        TString envFile = "config/" + env + ".json";
        if (TFileExists(envFile)) {
            TFileInput file(envFile);
            TConfig envConfig = TConfig::FromJson(file, globals);
            config = envConfig.Or(config);
        }

        return config;
    }
};
```

## 测试支持

### 1. 测试配置生成
```cpp
// 测试用配置生成器
class TestConfigBuilder {
private:
    NJson::TJsonValue config_;

public:
    TestConfigBuilder& SetString(const TString& path, const TString& value) {
        SetNestedValue(config_, path, value);
        return *this;
    }

    TestConfigBuilder& SetInt(const TString& path, int value) {
        SetNestedValue(config_, path, value);
        return *this;
    }

    TestConfigBuilder& SetBool(const TString& path, bool value) {
        SetNestedValue(config_, path, value);
        return *this;
    }

    TConfig Build() {
        TString json = NJson::WriteJson(config_, false);
        return TConfig::ReadJson(json);
    }
};

// 使用示例
TConfig testConfig = TestConfigBuilder()
    .SetString("server.host", "localhost")
    .SetInt("server.port", 8080)
    .SetBool("debug", true)
    .Build();
```

## 总结

Config 配置管理库为 YTsaurus 系统提供了完整而强大的配置处理能力。通过统一的接口设计、多格式支持和类型安全的访问机制，该库大大简化了配置管理工作。

无论是简单的键值对配置还是复杂的多层嵌套结构，Config 库都能提供灵活、高效、安全的解决方案。其丰富的功能和良好的扩展性使其成为配置管理的理想选择。