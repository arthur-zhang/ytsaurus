# YAML 库

YTsaurus YAML 处理库，提供 YAML 配置文件解析和生成功能。

## 📋 项目概述

YAML 库为 YTsaurus 提供了 YAML（YAML Ain't Markup Language）格式的数据序列化和反序列化支持，特别适用于配置文件、元数据描述和结构化数据交换场景。

### 🎯 核心特性

- **配置文件支持**: 解析和生成 YAML 配置文件
- **类型转换**: 自动类型转换和验证
- **类型安全**: 强类型的 YAML 数据访问
- **嵌套结构**: 支持复杂的嵌套数据结构
- **数组支持**: 完整的数组和列表支持
- **错误处理**: 详细的解析错误报告

## 🏗️ 架构设计

### 组件结构

```
YAML Library
├── Type System     # 类型系统
│   ├── TBuilder     # 类型构建器
│   ├── TConsumer    # 类型消费者
│   └── TString      # 字符串类型
└── Parsing         # 解析器
    ├── Parser       # YAML 解析器
    └── Validator    # 验证器
```

### 类型系统

```
YAML Type Hierarchy
├── Scalar Types     # 标量类型
│   ├── String       # 字符串
│   ├── Number       # 数字
│   ├── Boolean      # 布尔值
│   └── Null         # 空值
├── Collection Types # 集合类型
│   ├── Sequence     # 序列/数组
│   └── Mapping      # 映射/对象
└── Custom Types     # 自定义类型
```

## 💻 使用方法

### 基础 YAML 操作

```cpp
#include <library/cpp/yaml/as/tstring.h>
#include <util/generic/yexception.h>

// 基础字符串转换
void BasicYAMLExample() {
    // 字符串到 YAML 类型转换
    TString yamlString = R"(
# 示例配置文件
database:
  host: "localhost"
  port: 5432
  credentials:
    username: "admin"
    password: "secret"
  pools:
    - name: "read_pool"
      size: 10
      timeout: 30
    - name: "write_pool"
      size: 5
      timeout: 15

logging:
  level: "info"
  file: "/var/log/app.log"
  format: "json"
)";

    // 使用 TBuilder 处理 YAML 字符串
    NYaml::TBuilder builder;

    try {
        // 解析 YAML
        auto config = builder.Parse(yamlString);

        // 访问配置数据
        std::cout << "Database host: "
                  << config["database"]["host"].AsString() << std::endl;
        std::cout << "Database port: "
                  << config["database"]["port"].AsInt() << std::endl;
        std::cout << "Logging level: "
                  << config["logging"]["level"].AsString() << std::endl;

        // 访问数组
        const auto& pools = config["database"]["pools"];
        for (size_t i = 0; i < pools.Size(); ++i) {
            const auto& pool = pools[i];
            std::cout << "Pool " << i << ": "
                      << pool["name"].AsString()
                      << " (size: " << pool["size"].AsInt() << ")" << std::endl;
        }

    } catch (const std::exception& e) {
        std::cerr << "YAML parsing error: " << e.what() << std::endl;
    }
}
```

### 配置文件处理

```cpp
#include <library/cpp/yaml/as/tstring.h>
#include <util/stream/file.h>

// 配置文件类
class TApplicationConfig {
public:
    struct TDatabaseConfig {
        std::string Host;
        int Port;
        std::string Username;
        std::string Password;
    };

    struct TLoggingConfig {
        std::string Level;
        std::string File;
        bool EnableConsole;
    };

    bool LoadFromFile(const std::string& filename) {
        try {
            TString yamlContent;
            {
                TUnbufferedFileInput input(filename);
                TStringOutput output(yamlContent);
                TransferData(&input, &output);
            }

            NYaml::TBuilder builder;
            auto config = builder.Parse(yamlContent);

            // 解析数据库配置
            DatabaseConfig.Host = config["database"]["host"].AsString();
            DatabaseConfig.Port = config["database"]["port"].AsInt();
            DatabaseConfig.Username = config["database"]["credentials"]["username"].AsString();
            DatabaseConfig.Password = config["database"]["credentials"]["password"].AsString();

            // 解析日志配置
            LoggingConfig.Level = config["logging"]["level"].AsString();
            LoggingConfig.File = config["logging"]["file"].AsString();
            LoggingConfig.EnableConsole = config["logging"]["console"].AsBool(true); // 默认值

            return true;

        } catch (const std::exception& e) {
            std::cerr << "Failed to load config from " << filename
                      << ": " << e.what() << std::endl;
            return false;
        }
    }

    bool SaveToFile(const std::string& filename) const {
        try {
            NYaml::TConsumer consumer;

            // 构建配置结构
            consumer.BeginMap();

            // 数据库配置
            consumer.MapKey("database");
            consumer.BeginMap();

            consumer.MapKey("host");
            consumer.String(DatabaseConfig.Host);

            consumer.MapKey("port");
            consumer.Int(DatabaseConfig.Port);

            consumer.MapKey("credentials");
            consumer.BeginMap();

            consumer.MapKey("username");
            consumer.String(DatabaseConfig.Username);

            consumer.MapKey("password");
            consumer.String(DatabaseConfig.Password);

            consumer.EndMap(); // credentials
            consumer.EndMap(); // database

            // 日志配置
            consumer.MapKey("logging");
            consumer.BeginMap();

            consumer.MapKey("level");
            consumer.String(LoggingConfig.Level);

            consumer.MapKey("file");
            consumer.String(LoggingConfig.File);

            consumer.MapKey("console");
            consumer.Bool(LoggingConfig.EnableConsole);

            consumer.EndMap(); // logging
            consumer.EndMap(); // root

            // 写入文件
            TUnbufferedFileOutput output(filename);
            output << consumer.ToString();

            return true;

        } catch (const std::exception& e) {
            std::cerr << "Failed to save config to " << filename
                      << ": " << e.what() << std::endl;
            return false;
        }
    }

    void PrintConfig() const {
        std::cout << "=== Application Configuration ===" << std::endl;
        std::cout << "Database:" << std::endl;
        std::cout << "  Host: " << DatabaseConfig.Host << std::endl;
        std::cout << "  Port: " << DatabaseConfig.Port << std::endl;
        std::cout << "  Username: " << DatabaseConfig.Username << std::endl;
        std::cout << "Logging:" << std::endl;
        std::cout << "  Level: " << LoggingConfig.Level << std::endl;
        std::cout << "  File: " << LoggingConfig.File << std::endl;
        std::cout << "  Console: " << (LoggingConfig.EnableConsole ? "enabled" : "disabled") << std::endl;
    }

private:
    TDatabaseConfig DatabaseConfig;
    TLoggingConfig LoggingConfig;
};

void ConfigurationExample() {
    TApplicationConfig config;

    // 创建示例配置文件
    {
        std::ofstream configFile("app_config.yaml");
        configFile << R"(
database:
  host: "db.example.com"
  port: 5432
  credentials:
    username: "app_user"
    password: "secure_password_123"

logging:
  level: "debug"
  file: "/var/log/myapp/application.log"
  console: true
)";
    }

    // 加载配置
    if (config.LoadFromFile("app_config.yaml")) {
        std::cout << "Configuration loaded successfully!" << std::endl;
        config.PrintConfig();
    }

    // 修改配置
    // config.DatabaseConfig.Port = 3306;
    // config.LoggingConfig.Level = "info";

    // 保存配置
    // if (config.SaveToFile("app_config_modified.yaml")) {
    //     std::cout << "Configuration saved successfully!" << std::endl;
    // }
}
```

### 高级 YAML 操作

```cpp
// 复杂嵌套结构处理
void ComplexYAMLExample() {
    TString complexYaml = R"(
application:
  name: "YTsaurus Worker"
  version: "1.0.0"

clusters:
  - name: "primary"
    nodes:
      - host: "node1.cluster.local"
        port: 9000
        roles: ["master", "storage"]
        resources:
          cpu: 16
          memory: "64Gi"
          disk: "1Ti"
      - host: "node2.cluster.local"
        port: 9000
        roles: ["storage", "compute"]
        resources:
          cpu: 32
          memory: "128Gi"
          disk: "2Ti"

  - name: "secondary"
    nodes:
      - host: "node3.cluster.local"
        port: 9000
        roles: ["storage"]
        resources:
          cpu: 24
          memory: "96Gi"
          disk: "1.5Ti"

features:
  experimental_mode: true
  enable_metrics: true
  quotas:
    read_ops_per_second: 10000
    write_ops_per_second: 5000
    storage_quota_gb: 1000
)";

    NYaml::TBuilder builder;
    auto config = builder.Parse(complexYaml);

    // 解析应用信息
    std::cout << "Application: "
              << config["application"]["name"].AsString()
              << " v" << config["application"]["version"].AsString()
              << std::endl;

    // 解析集群配置
    const auto& clusters = config["clusters"];
    std::cout << "\nClusters (" << clusters.Size() << "):" << std::endl;

    for (size_t clusterIdx = 0; clusterIdx < clusters.Size(); ++clusterIdx) {
        const auto& cluster = clusters[clusterIdx];
        std::string clusterName = cluster["name"].AsString();
        std::cout << "  Cluster: " << clusterName << std::endl;

        const auto& nodes = cluster["nodes"];
        for (size_t nodeIdx = 0; nodeIdx < nodes.Size(); ++nodeIdx) {
            const auto& node = nodes[nodeIdx];
            std::cout << "    Node: " << node["host"].AsString()
                      << ":" << node["port"].AsInt() << std::endl;

            // 解析角色列表
            const auto& roles = node["roles"];
            std::cout << "      Roles: ";
            for (size_t roleIdx = 0; roleIdx < roles.Size(); ++roleIdx) {
                std::cout << roles[roleIdx].AsString();
                if (roleIdx + 1 < roles.Size()) {
                    std::cout << ", ";
                }
            }
            std::cout << std::endl;

            // 解析资源配置
            const auto& resources = node["resources"];
            std::cout << "      Resources: "
                      << "CPU=" << resources["cpu"].AsInt() << ", "
                      << "Memory=" << resources["memory"].AsString() << ", "
                      << "Disk=" << resources["disk"].AsString()
                      << std::endl;
        }
    }

    // 解析特性配置
    std::cout << "\nFeatures:" << std::endl;
    std::cout << "  Experimental Mode: "
              << (config["features"]["experimental_mode"].AsBool() ? "enabled" : "disabled")
              << std::endl;
    std::cout << "  Metrics: "
              << (config["features"]["enable_metrics"].AsBool() ? "enabled" : "disabled")
              << std::endl;

    const auto& quotas = config["features"]["quotas"];
    std::cout << "  Quotas:" << std::endl;
    std::cout << "    Read Ops/sec: " << quotas["read_ops_per_second"].AsInt() << std::endl;
    std::cout << "    Write Ops/sec: " << quotas["write_ops_per_second"].AsInt() << std::endl;
    std::cout << "    Storage Quota: " << quotas["storage_quota_gb"].AsInt() << " GB" << std::endl;
}
```

### YAML 验证和错误处理

```cpp
#include <util/generic/yexception.h>

// YAML 验证器
class TYAMLValidator {
public:
    struct TValidationResult {
        bool IsValid = true;
        std::vector<std::string> Errors;
        std::vector<std::string> Warnings;

        void AddError(const std::string& error) {
            IsValid = false;
            Errors.push_back(error);
        }

        void AddWarning(const std::string& warning) {
            Warnings.push_back(warning);
        }
    };

    static TValidationResult ValidateConfig(const NYaml::TNode& config) {
        TValidationResult result;

        // 验证必需字段
        if (!config.HasKey("database")) {
            result.AddError("Missing required 'database' section");
        }

        if (!config.HasKey("logging")) {
            result.AddError("Missing required 'logging' section");
        }

        // 验证数据库配置
        if (config.HasKey("database")) {
            const auto& db = config["database"];

            if (!db.HasKey("host")) {
                result.AddError("Database configuration missing 'host'");
            }

            if (!db.HasKey("port")) {
                result.AddError("Database configuration missing 'port'");
            } else {
                int port = db["port"].AsInt();
                if (port <= 0 || port > 65535) {
                    result.AddError("Database port must be between 1 and 65535");
                }
            }
        }

        // 验证日志配置
        if (config.HasKey("logging")) {
            const auto& logging = config["logging"];

            if (logging.HasKey("level")) {
                std::string level = logging["level"].AsString();
                std::set<std::string> validLevels = {"debug", "info", "warn", "error", "fatal"};
                if (validLevels.find(level) == validLevels.end()) {
                    result.AddError("Invalid log level: " + level);
                }
            }

            if (logging.HasKey("file")) {
                std::string logFile = logging["file"].AsString();
                if (logFile.empty()) {
                    result.AddError("Log file path cannot be empty");
                }
            }
        }

        return result;
    }

    static void PrintValidationResult(const TValidationResult& result) {
        if (result.IsValid) {
            std::cout << "✓ Configuration validation passed" << std::endl;
        } else {
            std::cout << "✗ Configuration validation failed" << std::endl;
        }

        if (!result.Errors.empty()) {
            std::cout << "\nErrors:" << std::endl;
            for (const auto& error : result.Errors) {
                std::cout << "  - " << error << std::endl;
            }
        }

        if (!result.Warnings.empty()) {
            std::cout << "\nWarnings:" << std::endl;
            for (const auto& warning : result.Warnings) {
                std::cout << "  - " << warning << std::endl;
            }
        }
    }
};

void ValidationExample() {
    // 创建有问题的配置
    TString problematicYaml = R"(
logging:
  level: "invalid_level"
  file: ""

# 缺少 database 配置
)";

    try {
        NYaml::TBuilder builder;
        auto config = builder.Parse(problematicYaml);

        // 验证配置
        auto validationResult = TYAMLValidator::ValidateConfig(config);
        TYAMLValidator::PrintValidationResult(validationResult);

    } catch (const std::exception& e) {
        std::cerr << "YAML parsing error: " << e.what() << std::endl;
    }
}
```

### 动态配置更新

```cpp
// 动态配置管理器
class TDynamicConfigManager {
public:
    TDynamicConfigManager(const std::string& configFile)
        : ConfigFile_(configFile)
    {
        LoadConfig();
        StartConfigWatcher();
    }

    ~TDynamicConfigManager() {
        StopConfigWatcher();
    }

    template <typename T>
    T GetConfigValue(const std::string& path, T defaultValue = T{}) const {
        std::lock_guard<std::mutex> lock(ConfigMutex_);

        try {
            // 简单的路径解析 (支持 "section.subsection.key")
            auto keys = SplitPath(path);
            const NYaml::TNode* current = &Config_;

            for (const auto& key : keys) {
                if (!current->HasKey(key)) {
                    return defaultValue;
                }
                current = &(*current)[key];
            }

            return current->As<T>();

        } catch (const std::exception&) {
            return defaultValue;
        }
    }

    void SetConfigValue(const std::string& path, const std::string& value) {
        std::lock_guard<std::mutex> lock(ConfigMutex_);

        // 这里应该实现动态更新逻辑
        // 简化版本只是重新加载整个配置
        LoadConfig();
    }

    std::vector<std::string> SplitPath(const std::string& path) const {
        std::vector<std::string> result;
        std::stringstream ss(path);
        std::string item;

        while (std::getline(ss, item, '.')) {
            result.push_back(item);
        }

        return result;
    }

private:
    void LoadConfig() {
        try {
            if (!std::filesystem::exists(ConfigFile_)) {
                return;
            }

            TString content;
            {
                TUnbufferedFileInput input(ConfigFile_);
                TStringOutput output(content);
                TransferData(&input, &output);
            }

            NYaml::TBuilder builder;
            Config_ = builder.Parse(content);

        } catch (const std::exception& e) {
            std::cerr << "Failed to load config: " << e.what() << std::endl;
        }
    }

    void StartConfigWatcher() {
        WatcherThread_ = std::thread([this]() {
            auto lastModified = std::filesystem::last_write_time(ConfigFile_);

            while (!StopWatcher_) {
                std::this_thread::sleep_for(std::chrono::seconds(5));

                try {
                    auto currentModified = std::filesystem::last_write_time(ConfigFile_);
                    if (currentModified != lastModified) {
                        std::cout << "Configuration file changed, reloading..." << std::endl;
                        LoadConfig();
                        lastModified = currentModified;
                        OnConfigChanged();
                    }
                } catch (const std::exception& e) {
                    std::cerr << "Config watcher error: " << e.what() << std::endl;
                }
            }
        });
    }

    void StopConfigWatcher() {
        StopWatcher_ = true;
        if (WatcherThread_.joinable()) {
            WatcherThread_.join();
        }
    }

    void OnConfigChanged() {
        std::cout << "Configuration updated:" << std::endl;
        std::cout << "  Database host: "
                  << GetConfigValue<std::string>("database.host", "N/A") << std::endl;
        std::cout << "  Log level: "
                  << GetConfigValue<std::string>("logging.level", "N/A") << std::endl;
    }

    std::string ConfigFile_;
    NYaml::TNode Config_;
    mutable std::mutex ConfigMutex_;
    std::thread WatcherThread_;
    std::atomic<bool> StopWatcher_{false};
};

void DynamicConfigExample() {
    // 创建初始配置
    {
        std::ofstream config("dynamic_config.yaml");
        config << R"(
database:
  host: "initial.db.local"
  port: 5432

logging:
  level: "info"
  file: "/var/log/app.log"
)";
    }

    TDynamicConfigManager configManager("dynamic_config.yaml");

    std::cout << "Initial config values:" << std::endl;
    std::cout << "  Database host: "
              << configManager.GetConfigValue<std::string>("database.host", "default") << std::endl;
    std::cout << "  Log level: "
              << configManager.GetConfigValue<std::string>("logging.level", "info") << std::endl;

    // 模拟运行一段时间
    std::this_thread::sleep_for(std::chrono::seconds(2));

    // 模拟配置文件更新
    std::cout << "\nUpdating configuration file..." << std::endl;
    {
        std::ofstream config("dynamic_config.yaml");
        config << R"(
database:
  host: "updated.db.local"
  port: 5432

logging:
  level: "debug"
  file: "/var/log/app.log"
)";
    }

    // 等待配置重载
    std::this_thread::sleep_for(std::chrono::seconds(6));

    std::cout << "\nUpdated config values:" << std::endl;
    std::cout << "  Database host: "
              << configManager.GetConfigValue<std::string>("database.host", "default") << std::endl;
    std::cout << "  Log level: "
              << configManager.GetConfigValue<std::string>("logging.level", "info") << std::endl;
}
```

## 🔧 高级特性

### 自定义类型支持

```cpp
// 自定义类型转换
struct TServiceConfig {
    std::string Name;
    std::vector<std::string> Endpoints;
    std::map<std::string, int> Resources;
    bool Enabled = true;
};

// 自定义 YAML 序列化/反序列化
namespace NYaml {

template <>
struct TTYamlTraits<TServiceConfig> {
    static TServiceConfig FromYaml(const TNode& node) {
        TServiceConfig config;

        config.Name = node["name"].AsString();
        config.Enabled = node["enabled"].AsBool(true);

        // 解析端点列表
        if (node.HasKey("endpoints")) {
            const auto& endpoints = node["endpoints"];
            for (size_t i = 0; i < endpoints.Size(); ++i) {
                config.Endpoints.push_back(endpoints[i].AsString());
            }
        }

        // 解析资源映射
        if (node.HasKey("resources")) {
            const auto& resources = node["resources"];
            for (const auto& key : resources.GetKeys()) {
                config.Resources[key] = resources[key].AsInt();
            }
        }

        return config;
    }

    static void ToYaml(const TServiceConfig& config, TConsumer& consumer) {
        consumer.BeginMap();

        consumer.MapKey("name");
        consumer.String(config.Name);

        consumer.MapKey("enabled");
        consumer.Bool(config.Enabled);

        consumer.MapKey("endpoints");
        consumer.BeginSequence();
        for (const auto& endpoint : config.Endpoints) {
            consumer.String(endpoint);
        }
        consumer.EndSequence();

        consumer.MapKey("resources");
        consumer.BeginMap();
        for (const auto& [key, value] : config.Resources) {
            consumer.MapKey(key);
            consumer.Int(value);
        }
        consumer.EndMap();

        consumer.EndMap();
    }
};

} // namespace NYaml

void CustomTypeExample() {
    std::vector<TServiceConfig> services = {
        {
            "web-server",
            {"http://localhost:8080", "http://localhost:8081"},
            {{"cpu", 4}, {"memory", 2048}},
            true
        },
        {
            "database",
            {"mysql://localhost:3306"},
            {{"cpu", 8}, {"memory", 8192}},
            true
        }
    };

    // 序列化服务配置
    NYaml::TConsumer consumer;
    consumer.BeginMap();
    consumer.MapKey("services");

    consumer.BeginSequence();
    for (const auto& service : services) {
        NYaml::TTYamlTraits<TServiceConfig>::ToYaml(service, consumer);
    }
    consumer.EndSequence();

    consumer.EndMap();

    std::cout << "Serialized services:\n" << consumer.ToString() << std::endl;
}
```

## 🧪 测试和验证

### 单元测试示例

```cpp
#include <library/cpp/testing/gtest/gtest.h>

class YAMLTest : public ::testing::Test {
protected:
    void SetUp() override {
        SampleYAML_ = R"(
test_string: "hello world"
test_number: 42
test_boolean: true
test_array:
  - item1
  - item2
  - item3
nested:
  key1: value1
  key2: value2
)";
    }

    TString SampleYAML_;
};

TEST_F(YAMLTest, BasicParsing) {
    NYaml::TBuilder builder;
    auto doc = builder.Parse(SampleYAML_);

    EXPECT_EQ(doc["test_string"].AsString(), "hello world");
    EXPECT_EQ(doc["test_number"].AsInt(), 42);
    EXPECT_EQ(doc["test_boolean"].AsBool(), true);

    const auto& array = doc["test_array"];
    EXPECT_EQ(array.Size(), 3);
    EXPECT_EQ(array[0].AsString(), "item1");
    EXPECT_EQ(array[1].AsString(), "item2");
    EXPECT_EQ(array[2].AsString(), "item3");
}

TEST_F(YAMLTest, NestedAccess) {
    NYaml::TBuilder builder;
    auto doc = builder.Parse(SampleYAML_);

    EXPECT_EQ(doc["nested"]["key1"].AsString(), "value1");
    EXPECT_EQ(doc["nested"]["key2"].AsString(), "value2");
}

TEST_F(YAMLTest, ErrorHandling) {
    // 测试无效 YAML
    TString invalidYAML = R"(
invalid: yaml: structure:
  - missing_quote: "unclosed string
  - extra_colon::
)";

    NYaml::TBuilder builder;
    EXPECT_THROW(builder.Parse(invalidYAML), std::exception);
}
```

## 📈 最佳实践

### 配置管理最佳实践

1. **分层配置**: 支持多级配置继承和覆盖
2. **环境变量**: 支持环境变量覆盖配置值
3. **默认值**: 为所有配置项提供合理的默认值
4. **验证**: 实施严格的配置验证规则
5. **热重载**: 支持配置文件的热重载功能

### 性能优化建议

1. **缓存解析结果**: 缓存解析后的配置对象
2. **延迟加载**: 只在需要时解析特定配置段
3. **增量更新**: 支持配置的增量更新
4. **内存管理**: 及时释放不再使用的配置对象

## 🔗 相关模块

- **JSON**: JSON 格式支持
- **Streams**: 流处理和文件操作
- **StringUtils**: 字符串处理工具
- **Threading**: 配置热重载的线程支持

YAML 库为 YTsaurus 提供了完整的 YAML 配置文件处理能力，支持复杂的嵌套结构、类型安全的访问和动态配置管理，是系统配置和元数据处理的重要工具。