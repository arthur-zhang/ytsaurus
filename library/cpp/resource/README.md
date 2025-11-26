# Resource - 资源管理

资源管理库提供嵌入式资源的存储和访问功能，支持将各种静态数据（如配置文件、模板、二进制资源）编译到可执行文件中。

## 🎯 核心功能

### 资源存储和检索

```cpp
#include <library/cpp/resource/resource.h>

using namespace NResource;

// 检查资源是否存在
bool exists = Has("config/template.xml");

// 查找资源
TString config = Find("config/settings.json");
TString templateData = Find("templates/email.html");

// 精确匹配查找
TString content;
bool found = FindExact("scripts/migration.sql", &content);

// 模糊匹配查找
TResources matching;
FindMatch("config/", &matching);  // 查找所有以 "config/" 开头的资源
```

### 资源遍历

```cpp
// 获取资源总数
size_t totalResources = Count();

// 获取所有资源键
TVector<TStringBuf> allKeys = ListAllKeys();

// 按索引访问资源
for (size_t i = 0; i < Count(); ++i) {
    TStringBuf key = KeyByIndex(i);
    TString data = Find(key);
    // 处理资源...
}
```

## 🚀 使用场景

### 1. 配置文件管理

```cpp
class ConfigManager {
    TVector<TString> configPaths;

public:
    void LoadDefaultConfigs() {
        // 加载内置配置
        if (Has("config/default.yaml")) {
            LoadConfigFromString(Find("config/default.yaml"));
        }

        if (Has("config/production.yaml")) {
            LoadConfigFromString(Find("config/production.yaml"));
        }
    }

    TString GetTemplate(const TString& name) {
        TString resourcePath = "templates/" + name + ".html";
        if (Has(resourcePath)) {
            return Find(resourcePath);
        }
        return "";  // 模板不存在
    }
};
```

### 2. 初始化脚本

```cpp
class DatabaseMigrator {
public:
    void RunMigrations() {
        TResources migrations;
        FindMatch("migrations/", &migrations);

        for (const auto& migration : migrations) {
            if (migration.Key.StartsWith("migrations/")) {
                ExecuteMigration(migration.Data);
                cout << "执行迁移: " << migration.Key << endl;
            }
        }
    }

private:
    void ExecuteMigration(const TString& sql) {
        // 执行 SQL 迁移脚本
        Database->Execute(sql);
    }
};
```

### 3. 静态资源服务

```cpp
class StaticResourceServer {
public:
    TString GetStaticFile(const TString& path) {
        TString resourcePath = "static/" + path;

        if (Has(resourcePath)) {
            return Find(resourcePath);
        }

        // 返回 404 页面
        if (Has("static/404.html")) {
            return Find("static/404.html");
        }

        return "<h1>404 Not Found</h1>";
    }

    bool HasStaticFile(const TString& path) {
        return Has("static/" + path);
    }
};
```

## 📊 资源管理特性

### 编译时嵌入
- **零依赖运行时资源**: 所有资源在编译时嵌入到二进制文件中
- **跨平台兼容**: 支持不同操作系统和架构
- **压缩优化**: 大型资源可以自动压缩以减小二进制大小

### 内存效率
- **延迟加载**: 资源只在首次访问时加载到内存
- **共享存储**: 相同资源只存储一份
- **内存映射**: 大文件使用内存映射技术

### 安全性
- **只读访问**: 嵌入资源在运行时不可修改
- **完整性保护**: 资源在编译时验证完整性
- **访问控制**: 可以控制特定资源的访问权限

## ⚡ 最佳实践

### 1. 资源组织

```
resources/
├── config/
│   ├── default.yaml
│   ├── production.yaml
│   └── development.yaml
├── templates/
│   ├── email.html
│   ├── report.html
│   └── error.html
├── scripts/
│   ├── init.sql
│   └── migration.sql
├── static/
│   ├── css/
│   ├── js/
│   └── images/
└── i18n/
    ├── en.json
    └── zh.json
```

### 2. 构建系统集成

#### ya.make 文件配置
```make
LIBRARY()
OWNER(user1)
RESOURCE(
    path/to/file1 /key/in/program/1
    path/to/file2 /key2
    config/default.yaml /config/default.yaml
    templates/email.html /templates/email.html
)
END()
```

### 3. 错误处理

```cpp
// 安全的资源访问
TString SafeGetResource(const TString& path) {
    try {
        if (Has(path)) {
            return Find(path);
        }
        return "";  // 资源不存在
    } catch (const std::exception& e) {
        Cerr << "获取资源失败 " << path << ": " << e.what() << endl;
        return "";
    }
}

// 带默认值的资源获取
TString GetResourceWithDefault(const TString& path, const TString& defaultValue) {
    TString content;
    if (FindExact(path, &content)) {
        return content;
    }
    return defaultValue;
}
```

### 4. 资源缓存

```cpp
class ResourceCache {
    THashMap<TString, TString> cache;

public:
    const TString& Get(const TString& path) {
        auto it = cache.find(path);
        if (it != cache.end()) {
            return it->second;
        }

        if (Has(path)) {
            TString content = Find(path);
            cache[path] = content;
            return cache[path];
        }

        static const TString empty;
        return empty;
    }

    void Preload(const TVector<TString>& paths) {
        for (const auto& path : paths) {
            if (Has(path)) {
                cache[path] = Find(path);
            }
        }
    }
};
```

## 🔗 相关模块

- **config**: 配置文件解析
- **yconf**: 配置管理
- **protobuf**: 资源序列化
- **testing**: 测试资源管理

资源管理库为 YTsaurus 提供了可靠的嵌入式资源存储和访问能力，简化了应用程序的部署和分发。