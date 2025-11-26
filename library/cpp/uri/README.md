# URI 库

YTsaurus URI 处理库，提供完整的 URI（统一资源标识符）解析、操作和生成功能。

## 📋 项目概述

URI 库为 YTsaurus 提供了完整的 URI 处理能力，支持 URI 解析、构建、规范化、编码解码等操作。库设计遵循 RFC 3986 标准，支持 HTTP、HTTPS、FTP、文件等各种 URI scheme。

### 🎯 核心特性

- **完整解析**: 支持 URI 各个组成部分的解析
- **标准化操作**: URI 路径规范化和解析
- **编码解码**: URL 编码和解码功能
- **参数处理**: 查询参数的解析和构建
- **安全处理**: 路径遍历攻击防护
- **跨平台**: 支持 Windows、Linux、macOS
- **高性能**: 优化的字符串操作和内存管理

## 🏗️ 架构设计

### 组件结构

```
URI Library
├── Core              # 核心组件
│   ├── TUri           # URI 主要类
│   ├── TField         # URI 字段处理
│   ├── TScheme        # 协议处理
│   └── TFeature       # 功能特性
├── Parsing           # 解析器
│   ├── TParse         # URI 解析器
│   ├── TLocation      # 位置处理
│   └── TCommon        # 通用功能
├── Encoding          # 编码处理
│   ├── TEncode        # 编码/解码
│   └── TDocCodes      # 文档编码
├── HTTP              # HTTP 支持
│   ├── THttpUrl       # HTTP URL 处理
│   └── TQArgs         # 查询参数
└── Utilities         # 工具类
    ├── TOther         # 其他工具
    └── TUriUt         # 单元测试
```

### URI 结构

```
URI Components
┌───────────────────┬─────────────────────┬─────────────────┐
│ Scheme           │ Authority           │ Path            │
│ (protocol)       │ (host:port)         │ (resource)      │
├───────────────────┼─────────────────────┼─────────────────┤
│ https://         │ example.com:8080    │ /path/to/resource│
└───────────────────┴─────────────────────┴─────────────────┘
                                           │
                                          │┌─────────────────┐
                                          ││ Query          │ │
                                          ││ param=value   │ │
                                          │└─────────────────┘│
                                          │
                                         │┌─────────────────┐│
                                         ││ Fragment       │ ││
                                         ││ #section      │ ││
                                         │└─────────────────┘││
                                         └───────────────────┘
```

## 💻 使用方法

### 基础 URI 操作

```cpp
#include <library/cpp/uri/uri.h>
#include <library/cpp/uri/parse.h>
#include <library/cpp/uri/http_url.h>

void BasicURIExample() {
    std::cout << "=== Basic URI Operations ===" << std::endl;

    // 1. 解析完整 URL
    NUri::TUri url("https://user:pass@example.com:8080/path/to/resource?param1=value1&param2=value2#section1");

    std::cout << "Parsed URL components:" << std::endl;
    std::cout << "  Scheme: " << url.GetScheme() << std::endl;
    std::cout << "  User: " << url.GetUser() << std::endl;
    std::cout << "  Password: " << url.GetPassword() << std::endl;
    std::cout << "  Host: " << url.GetHost() << std::endl;
    std::cout << "  Port: " << url.GetPort() << std::endl;
    std::cout << "  Path: " << url.GetPath() << std::endl;
    std::cout << "  Query: " << url.GetQuery() << std::endl;
    std::cout << "  Fragment: " << url.GetFragment() << std::endl;
    std::cout << "  Full URL: " << url.Print() << std::endl;

    // 2. 相对 URL 解析
    NUri::TUri baseUrl("https://example.com/base/path/");
    NUri::TUri relativeUrl("../other/resource.html");
    NUri::TUri resolvedUrl;

    if (baseUrl.Resolve(relativeUrl, resolvedUrl)) {
        std::cout << "\nRelative URL resolution:" << std::endl;
        std::cout << "  Base URL: " << baseUrl.Print() << std::endl;
        std::cout << "  Relative: " << relativeUrl.Print() << std::endl;
        std::cout << "  Resolved: " << resolvedUrl.Print() << std::endl;
    }

    // 3. URL 构建
    NUri::TUri constructedUrl;
    constructedUrl.SetScheme("https");
    constructedUrl.SetHost("ytsaurus.tech");
    constructedUrl.SetPort(443);
    constructedUrl.SetPath("/docs/getting-started");
    constructedUrl.SetQuery("lang=en&version=latest");

    std::cout << "\nConstructed URL: " << constructedUrl.Print() << std::endl;

    // 4. URL 验证和修正
    NUri::TUri testUrl("http://example.com");
    if (!testUrl.IsHost() || testUrl.GetPort() == 0) {
        // 设置默认端口
        testUrl.SetPort(80);
        std::cout << "Corrected URL: " << testUrl.Print() << std::endl;
    }
}
```

### HTTP URL 处理

```cpp
#include <library/cpp/uri/http_url.h>
#include <library/cpp/uri/qargs.h>

void HTTPURLExample() {
    std::cout << "=== HTTP URL Processing ===" << std::endl;

    // 1. HTTP URL 解析
    TString httpUrl = "https://api.ytsaurus.tech/v1/data?format=json&limit=100&offset=200#response";
    NUri::THttpUrl url(httpUrl);

    std::cout << "HTTP URL Analysis:" << std::endl;
    std::cout << "  Full URL: " << url.Get() << std::endl;
    std::cout << "  Scheme: " << url.GetScheme() << std::endl;
    std::cout << "  Host: " << url.GetHost() << std::endl;
    std::cout << "  Port: " << url.GetPort() << std::endl;
    std::cout << "  Path: " << url.GetPath() << std::endl;
    std::cout << "  Query: " << url.GetQuery() << std::endl;
    std::cout << "  Fragment: " << url.GetFragment() << std::endl;

    // 2. 查询参数处理
    NUri::TQArgs queryParams;
    queryParams.Add("format", "json");
    queryParams.Add("limit", "100");
    queryParams.Add("offset", "200");
    queryParams.AddAll("filter=status=active&sort=created_at");

    std::cout << "\nQuery Parameters:" << std::endl;
    for (const auto& param : queryParams) {
        std::cout << "  " << param.Name << " = " << param.Value << std::endl;
    }

    // 修改参数
    queryParams.Replace("limit", "50");
    queryParams.Add("include", "metadata");

    // 生成查询字符串
    TString queryString = queryParams.QueryString();
    std::cout << "\nModified query string: " << queryString << std::endl;

    // 3. URL 路径操作
    std::vector<TString> pathSegments = {
        "api", "v1", "users", "12345", "profile"
    };

    TString constructedPath = NUri::JoinPath(pathSegments);
    std::cout << "\nConstructed path: " << constructedPath << std::endl;

    // 路径解析
    std::vector<TString> parsedSegments = NUri::SplitPath("/api/v1/users/12345/profile");
    std::cout << "Parsed path segments:" << std::endl;
    for (size_t i = 0; i < parsedSegments.size(); ++i) {
        std::cout << "  [" << i << "]: " << parsedSegments[i] << std::endl;
    }

    // 4. URL 验证
    std::vector<TString> testUrls = {
        "https://example.com",
        "http://localhost:8080",
        "ftp://files.example.com/pub",
        "mailto:user@example.com",
        "file:///path/to/file.txt",
        "invalid_url",
        "http://[2001:db8::1]"  // IPv6
    };

    std::cout << "\nURL Validation:" << std::endl;
    for (const auto& testUrl : testUrls) {
        NUri::TUri url(testUrl);
        bool isValid = url.IsValid();
        std::cout << "  " << testUrl << " - " << (isValid ? "VALID" : "INVALID") << std::endl;

        if (isValid) {
            std::cout << "    Scheme: " << url.GetScheme() << std::endl;
            std::cout << "    Host: " << url.GetHost() << std::endl;
            if (url.GetPort() != 0) {
                std::cout << "    Port: " << url.GetPort() << std::endl;
            }
        }
    }
}
```

### URL 编码和解码

```cpp
#include <library/cpp/uri/encode.h>

void URLEncodingExample() {
    std::cout << "=== URL Encoding/Decoding ===" << std::endl;

    // 1. 基础编码/解码
    std::vector<std::string> testStrings = {
        "Hello World!",
        "C++ Programming",
        "日本語テスト",
        "email@example.com",
        "path/to/resource",
        "param=value&another=value",
        "100%_complete",
        "special chars: !@#$%^&*()"
    };

    std::cout << "URL Encoding Examples:" << std::endl;
    for (const auto& str : testStrings) {
        TString encoded = NUri::Encode(str);
        TString decoded = NUri::Decode(encoded);

        std::cout << "  Original: " << str << std::endl;
        std::cout << "  Encoded:  " << encoded << std::endl;
        std::cout << "  Decoded:  " << decoded << std::endl;
        std::cout << "  Match: " << (str == decoded ? "YES" : "NO") << std::endl;
        std::cout << std::endl;
    }

    // 2. 组件编码
    std::cout << "Component-specific Encoding:" << std::endl;

    TString pathComponent = "folder name/file name.txt";
    TString queryComponent = "name=John Doe&city=New York";
    TString fragmentComponent = "section 1.2";

    std::cout << "Path component:" << std::endl;
    std::cout << "  Original: " << pathComponent << std::endl;
    std::cout << "  Path encoded: " << NUri::EncodePath(pathComponent) << std::endl;
    std::cout << "  Query encoded: " << NUri::Encode(queryComponent) << std::endl;
    std::cout << "  Fragment encoded: " << NUri::Encode(fragmentComponent) << std::endl;

    // 3. 批量编码
    std::map<TString, TString> params = {
        {"name", "张三"},
        {"city", "北京"},
        {"email", "user@example.com"},
        {"description", "This is a test with special chars: !@#$%"}
    };

    TString encodedQuery;
    bool first = true;
    for (const auto& [key, value] : params) {
        if (!first) {
            encodedQuery += "&";
        }
        encodedQuery += NUri::Encode(key) + "=" + NUri::Encode(value);
        first = false;
    }

    std::cout << "\nEncoded query string: " << encodedQuery << std::endl;

    // 4. 安全解码
    TString safeEncoded = "test%20value%20%31%32%33";  // "test value 123"
    TString unsafeEncoded = "test%20value%ZZ%invalid";  // 包含无效编码

    std::cout << "\nSafe Decoding:" << std::endl;
    std::cout << "  Safe encoded: " << safeEncoded << std::endl;
    std::cout << "  Decoded: " << NUri::Decode(safeEncoded) << std::endl;

    std::cout << "  Unsafe encoded: " << unsafeEncoded << std::endl;
    try {
        TString decoded = NUri::Decode(unsafeEncoded);
        std::cout << "  Decoded: " << decoded << std::endl;
    } catch (const std::exception& e) {
        std::cout << "  Decode failed: " << e.what() << std::endl;
    }
}
```

### URL 规范化和安全性

```cpp
void URLNormalizationExample() {
    std::cout << "=== URL Normalization and Security ===" << std::endl;

    // 1. 路径规范化
    std::vector<std::string> pathsToNormalize = {
        "/a/b/c/../d",           // 应该规范化为 /a/b/d
        "/a/./b/../c/d",         // 应该规范化为 /a/c/d
        "//multiple//slashes",    // 应该规范化为 /multiple/slashes
        "/path/with/trailing/",   // 应该规范化为 /path/with/trailing
        "../../../etc/passwd",    // 危险路径
        "%2e%2e%2f%2e%2e%2f"    // URL编码的 ../../
    };

    std::cout << "Path Normalization:" << std::endl;
    for (const auto& path : pathsToNormalize) {
        TString normalized = NUri::NormalizePath(path);
        std::cout << "  Original:  " << path << std::endl;
        std::cout << "  Normalized: " << normalized << std::endl;
        std::cout << std::endl;
    }

    // 2. URL 安全检查
    std::vector<std::string> suspiciousUrls = {
        "https://example.com/../../../etc/passwd",
        "https://example.com/path/../../../secret.txt",
        "https://example.com/%2e%2e%2f%2e%2e%2fadmin",
        "https://example.com/path//to//resource",
        "https://example.com/path/./././file.txt",
        "javascript:alert('XSS')",
        "data:text/html,<script>alert('XSS')</script>"
    };

    std::cout << "URL Security Analysis:" << std::endl;
    for (const auto& url : suspiciousUrls) {
        NUri::TUri uri(url);
        bool isSafe = true;
        TString reason;

        if (!uri.IsValid()) {
            isSafe = false;
            reason = "Invalid URL format";
        } else {
            TString path = uri.GetPath();

            // 检查路径遍历
            if (path.Contains("../") || path.Contains("%2e%2e%2f") ||
                path.Contains("..\\") || path.Contains("%2e%2e%5c")) {
                isSafe = false;
                reason = "Path traversal attempt";
            }

            // 检查危险协议
            TString scheme = uri.GetScheme();
            if (scheme == "javascript" || scheme == "data" || scheme == "vbscript") {
                isSafe = false;
                reason = "Dangerous protocol";
            }
        }

        std::cout << "  " << url << std::endl;
        std::cout << "    Safe: " << (isSafe ? "YES" : "NO") << std::endl;
        if (!isSafe) {
            std::cout << "    Reason: " << reason << std::endl;
        }
        std::cout << std::endl;
    }

    // 3. URL 比较
    std::vector<std::pair<std::string, std::string>> urlPairs = {
        {"https://example.com/path", "https://example.com/path/"},
        {"HTTPS://EXAMPLE.COM/PATH", "https://example.com/path"},
        {"https://example.com/a/../b", "https://example.com/b"},
        {"https://example.com/path?param=1", "https://example.com/path?param=2"},
        {"https://example.com:80/path", "https://example.com/path"}
    };

    std::cout << "URL Comparison:" << std::endl;
    for (const auto& [url1, url2] : urlPairs) {
        NUri::TUri uri1(url1);
        NUri::TUri uri2(url2);

        if (uri1.IsValid() && uri2.IsValid()) {
            NUri::TUri norm1 = uri1.Normalize();
            NUri::TUri norm2 = uri2.Normalize();

            bool equal = norm1.Compare(norm2) == 0;
            std::cout << "  " << url1 << " vs " << url2 << std::endl;
            std::cout << "    Equal: " << (equal ? "YES" : "NO") << std::endl;
            std::cout << "    Normalized 1: " << norm1.Print() << std::endl;
            std::cout << "    Normalized 2: " << norm2.Print() << std::endl;
        }
        std::cout << std::endl;
    }
}
```

### URL 构建和修改

```cpp
void URLBuilderExample() {
    std::cout << "=== URL Building and Modification ===" << std::endl;

    // 1. URL 构建器模式
    class TURLBuilder {
    public:
        explicit TURLBuilder(const TString& scheme = "https")
            : Scheme_(scheme)
        {}

        TURLBuilder& Host(const TString& host) {
            Host_ = host;
            return *this;
        }

        TURLBuilder& Port(ui16 port) {
            Port_ = port;
            return *this;
        }

        TURLBuilder& Path(const TString& path) {
            Path_ = path;
            return *this;
        }

        TURLBuilder& AddPathSegment(const TString& segment) {
            if (!Path_.empty() && !Path_.EndsWith('/')) {
                Path_ += '/';
            }
            Path_ += segment;
            return *this;
        }

        TURLBuilder& QueryParam(const TString& name, const TString& value) {
            if (!Query_.empty()) {
                Query_ += '&';
            }
            Query_ += NUri::Encode(name) + "=" + NUri::Encode(value);
            return *this;
        }

        TURLBuilder& Fragment(const TString& fragment) {
            Fragment_ = fragment;
            return *this;
        }

        NUri::TUri Build() const {
            NUri::TUri url;
            url.SetScheme(Scheme_);
            url.SetHost(Host_);

            if (Port_ != 0) {
                url.SetPort(Port_);
            }

            if (!Path_.empty()) {
                url.SetPath(Path_);
            }

            if (!Query_.empty()) {
                url.SetQuery(Query_);
            }

            if (!Fragment_.empty()) {
                url.SetFragment(Fragment_);
            }

            return url;
        }

        TString BuildString() const {
            return Build().Print();
        }

    private:
        TString Scheme_;
        TString Host_;
        ui16 Port_ = 0;
        TString Path_;
        TString Query_;
        TString Fragment_;
    };

    // 使用构建器创建 URL
    TString apiUrl = TURLBuilder()
        .Host("api.ytsaurus.tech")
        .Port(443)
        .AddPathSegment("v1")
        .AddPathSegment("data")
        .AddPathSegment("query")
        .QueryParam("format", "json")
        .QueryParam("limit", "100")
        .QueryParam("filter", "status=active")
        .Fragment("results")
        .BuildString();

    std::cout << "Built API URL: " << apiUrl << std::endl;

    // 2. 动态 URL 修改
    NUri::TUrl baseUrl("https://example.com/api/v1");

    // 动态添加路径段
    std::vector<TString> segments = {"users", "12345", "permissions"};
    for (const auto& segment : segments) {
        TString currentPath = baseUrl.GetPath();
        if (!currentPath.EndsWith('/')) {
            currentPath += '/';
        }
        currentPath += segment;
        baseUrl.SetPath(currentPath);
    }

    std::cout << "\nModified path: " << baseUrl.Print() << std::endl;

    // 动态添加查询参数
    std::map<TString, TString> queryParams = {
        {"fields", "name,email,role"},
        {"include", "profile"},
        {"page", "1"},
        {"per_page", "20"}
    };

    TString currentQuery = baseUrl.GetQuery();
    for (const auto& [key, value] : queryParams) {
        if (!currentQuery.empty()) {
            currentQuery += '&';
        }
        currentQuery += NUri::Encode(key) + "=" + NUri::Encode(value);
    }
    baseUrl.SetQuery(currentQuery);

    std::cout << "With query params: " << baseUrl.Print() << std::endl;

    // 3. URL 模板替换
    std::cout << "\nURL Template Processing:" << std::endl;

    class TURLTemplate {
    public:
        explicit TURLTemplate(const TString& templateStr)
            : Template_(templateStr)
        {}

        TURLTemplate& SetParam(const TString& name, const TString& value) {
            Params_[name] = value;
            return *this;
        }

        TString Render() const {
            TString result = Template_;
            for (const auto& [name, value] : Params_) {
                TString placeholder = "{" + name + "}";
                size_t pos = 0;
                while ((pos = result.find(placeholder, pos)) != TString::npos) {
                    result.replace(pos, placeholder.length(), value);
                    pos += value.length();
                }
            }
            return result;
        }

    private:
        TString Template_;
        std::map<TString, TString> Params_;
    };

    // 使用模板
    TURLTemplate userTemplate("https://example.com/api/{version}/users/{userId}/profile");
    TString userUrl = userTemplate
        .SetParam("version", "v2")
        .SetParam("userId", "12345")
        .Render();

    std::cout << "Template result: " << userUrl << std::endl;

    // 4. URL 转换和重定向
    std::vector<TString> redirectUrls = {
        "http://example.com/page",
        "https://example.com/page",
        "example.com/page",
        "www.example.com/page"
    };

    std::cout << "\nURL Redirection and Conversion:" << std::endl;
    for (const auto& urlStr : redirectUrls) {
        NUri::TUri url(urlStr);
        NUri::TUri httpsUrl = url;

        // 确保使用 HTTPS
        if (httpsUrl.GetScheme() != "https") {
            httpsUrl.SetScheme("https");
        }

        // 确保有默认端口
        if (httpsUrl.GetPort() == 0 && httpsUrl.GetScheme() == "https") {
            httpsUrl.SetPort(443);
        }

        std::cout << "  Original: " << urlStr << std::endl;
        std::cout << "  HTTPS:   " << httpsUrl.Print() << std::endl;
        std::cout << std::endl;
    }
}
```

## 🔧 高级特性

### URL 缓存和性能优化

```cpp
#include <unordered_map>
#include <chrono>

void URLCacheExample() {
    std::cout << "=== URL Caching and Performance ===" << std::endl;

    // URL 解析缓存
    class TURLCache {
    public:
        using TClock = std::chrono::steady_clock;
        using TTimePoint = TClock::time_point;

        struct TCacheEntry {
            NUri::TUri Uri;
            TTimePoint LastAccess;
            size_t AccessCount;
        };

        NUri::TUri Get(const TString& urlStr) {
            auto now = TClock::now();
            auto it = Cache_.find(urlStr);

            if (it != Cache_.end()) {
                // 缓存命中
                it->second.LastAccess = now;
                it->second.AccessCount++;
                return it->second.Uri;
            }

            // 缓存未命中，解析并缓存
            NUri::TUri uri(urlStr);
            if (uri.IsValid()) {
                Cache_[urlStr] = {uri, now, 1};
            }

            return uri;
        }

        void Cleanup(size_t maxEntries, std::chrono::seconds maxAge) {
            auto now = TClock::now();
            auto cutoff = now - maxAge;

            // 清理过期条目
            for (auto it = Cache_.begin(); it != Cache_.end();) {
                if (it->second.LastAccess < cutoff) {
                    it = Cache_.erase(it);
                } else {
                    ++it;
                }
            }

            // 如果条目仍然过多，按访问频率清理
            if (Cache_.size() > maxEntries) {
                std::vector<std::pair<TString, size_t>> entries;
                for (const auto& [url, entry] : Cache_) {
                    entries.emplace_back(url, entry.AccessCount);
                }

                std::sort(entries.begin(), entries.end(),
                         [](const auto& a, const auto& b) {
                             return a.second > b.second;
                         });

                size_t toRemove = Cache_.size() - maxEntries;
                for (size_t i = entries.size() - toRemove; i < entries.size(); ++i) {
                    Cache_.erase(entries[i].first);
                }
            }
        }

        size_t Size() const {
            return Cache_.size();
        }

        void PrintStats() const {
            std::cout << "Cache statistics:" << std::endl;
            std::cout << "  Entries: " << Cache_.size() << std::endl;

            size_t totalAccess = 0;
            for (const auto& [url, entry] : Cache_) {
                totalAccess += entry.AccessCount;
            }
            std::cout << "  Total access count: " << totalAccess << std::endl;
            std::cout << "  Average access per entry: "
                      << (Cache_.empty() ? 0 : static_cast<double>(totalAccess) / Cache_.size())
                      << std::endl;
        }

    private:
        std::unordered_map<TString, TCacheEntry> Cache_;
    };

    // 性能测试
    std::vector<TString> testUrls = {
        "https://www.example.com",
        "https://api.example.com/v1/users",
        "https://static.example.com/assets/style.css",
        "https://cdn.example.com/images/logo.png",
        "https://blog.example.com/post/123",
        "https://docs.example.com/guide",
        "https://admin.example.com/dashboard",
        "https://shop.example.com/products",
        "https://forum.example.com/topics",
        "https://news.example.com/articles"
    };

    TURLCache cache;

    // 测试多次访问
    const int iterations = 10000;
    auto start = std::chrono::high_resolution_clock::now();

    for (int i = 0; i < iterations; ++i) {
        const TString& url = testUrls[i % testUrls.size()];
        NUri::TUri uri = cache.Get(url);
        // 使用解析的 URI
        (void)uri;
    }

    auto end = std::chrono::high_resolution_clock::now();
    auto duration = std::chrono::duration_cast<std::chrono::microseconds>(end - start);

    std::cout << "Performance test results:" << std::endl;
    std::cout << "  Iterations: " << iterations << std::endl;
    std::cout << "  Total time: " << duration.count() << " μs" << std::endl;
    std::cout << "  Average time per iteration: " << duration.count() / iterations << " μs" << std::endl;
    std::cout << "  Throughput: " << (iterations * 1000000.0) / duration.count() << " URLs/sec" << std::endl;

    cache.PrintStats();

    // 清理测试
    cache.Cleanup(5, std::chrono::seconds(1));
    std::cout << "\nAfter cleanup:" << std::endl;
    cache.PrintStats();
}
```

## 🧪 测试和验证

### 单元测试示例

```cpp
#include <library/cpp/testing/gtest/gtest.h>

class URITest : public ::testing::Test {
protected:
    void SetUp() override {
        TestURL_ = "https://user:pass@example.com:8080/path/to/resource?param1=value1&param2=value2#section1";
        ValidURL_ = NUri::TUri(TestURL_);
    }

    TString TestURL_;
    NUri::TUri ValidURL_;
};

TEST_F(URITest, BasicParsing) {
    ASSERT_TRUE(ValidURL_.IsValid());
    EXPECT_EQ(ValidURL_.GetScheme(), "https");
    EXPECT_EQ(ValidURL_.GetUser(), "user");
    EXPECT_EQ(ValidURL_.GetPassword(), "pass");
    EXPECT_EQ(ValidURL_.GetHost(), "example.com");
    EXPECT_EQ(ValidURL_.GetPort(), 8080);
    EXPECT_EQ(ValidURL_.GetPath(), "/path/to/resource");
    EXPECT_EQ(ValidURL_.GetQuery(), "param1=value1&param2=value2");
    EXPECT_EQ(ValidURL_.GetFragment(), "section1");
}

TEST_F(URITest, URLConstruction) {
    NUri::TUri url;
    url.SetScheme("http");
    url.SetHost("test.com");
    url.SetPort(80);
    url.SetPath("/test");

    EXPECT_EQ(url.Print(), "http://test.com/test");
}

TEST_F(URITest, PathNormalization) {
    NUri::TUri url("https://example.com/a/b/../c");
    // 规范化后的路径应该是 /a/c
    EXPECT_EQ(url.GetPath(), "/a/c");
}

TEST_F(URITest, EncodingDecoding) {
    TString original = "Hello World!";
    TString encoded = NUri::Encode(original);
    TString decoded = NUri::Decode(encoded);
    EXPECT_EQ(original, decoded);
}

TEST_F(URITest, Security) {
    std::vector<TString> maliciousUrls = {
        "https://example.com/../../../etc/passwd",
        "javascript:alert('xss')",
        "data:text/html,<script>alert('xss')</script>"
    };

    for (const auto& url : maliciousUrls) {
        NUri::TUri parsed(url);
        // 验证这些 URL 是否被正确处理或拒绝
        if (parsed.IsValid()) {
            TString path = parsed.GetPath();
            EXPECT_FALSE(path.Contains("../")) << "Path traversal not blocked: " << url;
        }
    }
}
```

## 📈 最佳实践

### 安全建议

1. **输入验证**: 始终验证外部来源的 URL
2. **路径检查**: 检查路径遍历攻击
3. **协议验证**: 限制允许的协议类型
4. **编码处理**: 正确处理 URL 编码
5. **长度限制**: 设置合理的 URL 长度限制

### 性能优化

1. **缓存解析**: 缓存频繁访问的 URL 解析结果
2. **预分配**: 为已知大小的操作预分配内存
3. **批量处理**: 批量处理多个 URL 操作
4. **避免重复编码**: 避免重复编码已编码的字符串

### 错误处理

```cpp
void RobustURLProcessing() {
    try {
        NUri::TUri url(userInput);

        if (!url.IsValid()) {
            std::cerr << "Invalid URL format" << std::endl;
            return;
        }

        // 安全检查
        TString path = url.GetPath();
        if (path.Contains("../") || path.Contains("%2e%2e%2f")) {
            std::cerr << "Path traversal attempt detected" << std::endl;
            return;
        }

        // 处理 URL
        ProcessURL(url);

    } catch (const std::exception& e) {
        std::cerr << "URL processing error: " << e.what() << std::endl;
    }
}
```

## 🔗 相关模块

- **OpenSSL**: SSL/TLS 安全连接
- **Protobuf**: Protocol Buffers 序列化
- **HTTP**: HTTP 客户端库
- **Net**: 网络通信基础
- **String**: 字符串处理工具

URI 库为 YTsaurus 提供了完整的 URL 处理能力，从基础的解析构建到高级的安全检查和性能优化，是处理网络资源和 URL 相关操作的核心工具。通过标准化的实现和安全的设计，确保了 URL 处理的可靠性和安全性。