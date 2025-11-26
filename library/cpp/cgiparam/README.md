# cgiparam

CGI 参数解析库，提供了完整的 CGI/HTTP 查询参数和表单数据的解析功能，支持 URL 编码解码和多种数据格式。

## 功能描述

cgiparam 库专门用于处理 Web 应用中的 CGI 参数，包括 URL 查询字符串、表单数据、Cookie 等的解析和生成。它提供了简洁的 API 来处理各种编码格式的参数数据。

## 核心特性

- **完整解析**：支持完整的 CGI 参数解析
- **多值支持**：支持同名参数的多个值
- **URL 编码**：自动处理 URL 编码和解码
- **灵活接口**：提供多种便捷的访问方法
- **高性能**：优化的字符串处理算法
- **标准兼容**：完全符合 CGI/HTTP 标准

## 主要组件

### TCgiParameters
核心参数解析类，继承自 TMultiMap：

```cpp
class TCgiParameters: public TMultiMap<TString, TString> {
public:
    // 构造函数
    TCgiParameters() = default;
    explicit TCgiParameters(const TStringBuf cgiParamStr);

    // 参数操作
    size_t EraseAll(const TStringBuf name);
    size_t NumOfValues(const TStringBuf name) const noexcept;

    // 解析方法
    void Scan(const TStringBuf cgiParStr, bool form = true);
    void ScanAdd(const TStringBuf cgiParStr);
    void ScanAddUnescaped(const TStringBuf cgiParStr);
    void ScanAddAll(const TStringBuf cgiParStr);
    void ScanAddAllUnescaped(const TStringBuf cgiParStr);

    // 输出方法
    TString Print() const;
    char* Print(char* res) const;

    // 便捷访问
    TString Get(const TStringBuf name) const;
    bool Has(const TStringBuf name) const;
    i32 GetI32(const TStringBuf name, i32 def = 0) const;
    i64 GetI64(const TStringBuf name, i64 def = 0) const;
    double GetDouble(const TStringBuf name, double def = 0.0) const;
};
```

## 使用示例

### 基本解析
```cpp
#include <library/cpp/cgiparam/cgiparam.h>

// 解析查询字符串
TString query = "name=John&age=25&city=New+York";
TCgiParameters params(query);

// 获取单个值
TString name = params.Get("name");  // "John"
TString city = params.Get("city");  // "New York"

// 获取数值类型
int age = params.GetI32("age");     // 25
```

### 处理多值参数
```cpp
// 解析多选框或重复参数
TString query = "tags=cpp&tags=python&tags=java";
TCgiParameters params(query);

// 获取所有值
auto values = params.GetAll("tags");
// values = {"cpp", "python", "java"}

// 检查参数是否存在
if (params.Has("tags")) {
    Cout << "Found " << params.NumOfValues("tags") << " tags" << Endl;
}
```

### 表单数据处理
```cpp
// 解析表单数据
TString formData = "username=admin&password=secret&action=login";
TCgiParameters params(formData);

// 安全地获取敏感参数
TString username = params.Get("username");
if (params.Has("password")) {
    // 处理登录逻辑
    if (ValidateLogin(username, params.Get("password"))) {
        // 登录成功
    }
}
```

### URL 编码处理
```cpp
// 自动处理 URL 编码
TString encoded = "search=C%2B%2B+tutorial&lang=en_US";
TCgiParameters params(encoded);

// 自动解码
TString search = params.Get("search");  // "C++ tutorial"
TString lang = params.Get("lang");      // "en_US"
```

### 参数构建和输出
```cpp
// 构建参数
TCgiParameters params;
params.Insert("page", "1");
params.Insert("limit", "50");
params.Insert("sort", "date");

// 输出为查询字符串
TString queryString = params.Print();
// "page=1&limit=50&sort=date"

// 输出到缓冲区
char buffer[256];
params.Print(buffer);
```

### 数组参数处理
```cpp
// 处理数组索引参数
TString arrayData = "items[0]=apple&items[1]=orange&items[2]=banana";
TCgiParameters params(arrayData);

// 提取数组值
TVector<TString> items;
for (int i = 0; params.Has(TString::Join("items[", i, "]")); ++i) {
    items.push_back(params.Get(TString::Join("items[", i, "]")));
}
// items = {"apple", "orange", "banana"}
```

## 高级功能

### 条件解析
```cpp
class ConditionalParser {
public:
    static TCgiParameters ParseQueryString(const TString& url) {
        // 提取查询部分
        size_t pos = url.find('?');
        if (pos != TString::npos) {
            return TCgiParameters(url.substr(pos + 1));
        }
        return TCgiParameters();
    }

    static TCgiParameters ParsePostData(IInputStream* input, size_t length) {
        // 读取 POST 数据
        TString data;
        data.resize(length);
        input->Read(&data[0], length);
        return TCgiParameters(data);
    }
};
```

### 参数验证
```cpp
class ParameterValidator {
public:
    static bool ValidateEmail(const TCgiParameters& params, const TString& paramName) {
        if (!params.Has(paramName)) {
            return false;
        }

        TString email = params.Get(paramName);
        // 简单的邮箱验证
        return email.find('@') != TString::npos &&
               email.find('.') != TString::npos;
    }

    static bool ValidateRange(const TCgiParameters& params,
                            const TString& paramName,
                            int min, int max) {
        if (!params.Has(paramName)) {
            return false;
        }

        int value = params.GetI32(paramName);
        return value >= min && value <= max;
    }
};
```

### 参数转换
```cpp
class ParameterConverter {
public:
    // 转换为 JSON
    static NJson::TJsonValue ToJson(const TCgiParameters& params) {
        NJson::TJsonValue json;
        for (const auto& [key, value] : params) {
            json[key] = value;
        }
        return json;
    }

    // 从 JSON 构建
    static TCgiParameters FromJson(const NJson::TJsonValue& json) {
        TCgiParameters params;
        for (const auto& [key, value] : json.GetMap()) {
            params.Insert(key, value.GetString());
        }
        return params;
    }

    // 转换为映射
    static THashMap<TString, TString> ToHashMap(const TCgiParameters& params) {
        THashMap<TString, TString> result;
        for (const auto& [key, value] : params) {
            result[key] = value;
        }
        return result;
    }
};
```

## 编码处理

### URL 编码
```cpp
// 手动编码/解码
TString encoded = UrlEncode("Hello World!");     // "Hello+World%21"
TString decoded = UrlDecode("Hello+World%21");   // "Hello World!"

// 路径编码
TString pathEncoded = UrlEncodePath("/docs/api/v1/users");
// "/docs/api/v1/users" (路径分隔符不编码)
```

### 特殊字符处理
```cpp
// 处理特殊字符
TString special = "name=John&email=john@example.com";
TCgiParameters params;
params.ScanAddUnescaped(special);  // 不进行额外解码
```

## 应用场景

### Web 服务器
```cpp
class WebHandler {
public:
    void HandleRequest(IInputStream* input, IOutputStream* output) {
        // 解析请求参数
        TString queryString = GetQueryString(input);
        TCgiParameters params(queryString);

        // 处理请求
        if (params.Get("action") == "search") {
            HandleSearch(params, output);
        } else if (params.Get("action") == "upload") {
            HandleUpload(params, input, output);
        }
    }

private:
    void HandleSearch(const TCgiParameters& params, IOutputStream* output) {
        TString query = params.Get("q");
        int page = params.GetI32("page", 1);
        int limit = Min(params.GetI32("limit", 10), 100);

        // 执行搜索
        auto results = SearchEngine.Search(query, page, limit);

        // 返回结果
        OutputJson(output, results);
    }
};
```

### API 网关
```cpp
class APIGateway {
public:
    TCgiParameters ProcessRequest(const TCgiParameters& request) {
        TCgiParameters response;

        // 验证 API 密钥
        if (!ValidateAPIKey(request.Get("api_key"))) {
            response.Insert("error", "Invalid API key");
            return response;
        }

        // 路由请求
        TString endpoint = request.Get("endpoint");
        if (endpoint == "search") {
            response = HandleSearch(request);
        } else if (endpoint == "create") {
            response = HandleCreate(request);
        }

        return response;
    }
};
```

### 表单处理
```cpp
class FormProcessor {
public:
    struct UserRegistration {
        TString username;
        TString email;
        TString password;
        TVector<TString> interests;
    };

    static UserRegistration ParseRegistrationForm(const TCgiParameters& form) {
        UserRegistration user;

        user.username = form.Get("username");
        user.email = form.Get("email");
        user.password = form.Get("password");

        // 解析兴趣列表
        for (size_t i = 0; i < form.NumOfValues("interests"); ++i) {
            user.interests.push_back(form.GetAll("interests")[i]);
        }

        return user;
    }

    static bool ValidateForm(const UserRegistration& user) {
        // 验证用户名
        if (user.username.size() < 3 || user.username.size() > 20) {
            return false;
        }

        // 验证邮箱
        if (!IsValidEmail(user.email)) {
            return false;
        }

        // 验证密码
        if (!IsStrongPassword(user.password)) {
            return false;
        }

        return true;
    }
};
```

## 性能优化

### 字符串视图优化
```cpp
// 使用 StringBuf 避免不必要的拷贝
class FastParamParser {
public:
    static TStringBuf GetValue(const TCgiParameters& params,
                             const TStringBuf key) {
        auto range = params.equal_range(TString(key));
        if (range.first != range.second) {
            return range.first->second;
        }
        return TStringBuf();
    }
};
```

### 批量处理
```cpp
// 批量参数处理
class BatchProcessor {
public:
    static THashMap<TString, TString> ExtractCommonParams(
        const TCgiParameters& params,
        const TVector<TString>& paramNames) {

        THashMap<TString, TString> result;
        for (const auto& name : paramNames) {
            if (params.Has(name)) {
                result[name] = params.Get(name);
            }
        }
        return result;
    }
};
```

## 安全考虑

### 参数验证
```cpp
class SecurityValidator {
public:
    // 防止 SQL 注入
    static TString SanitizeSQL(const TCgiParameters& params, const TString& name) {
        TString value = params.Get(name);
        // 移除危险字符
        value = StringReplace(value, "'", "''");
        value = StringReplace(value, ";", "");
        return value;
    }

    // XSS 防护
    static TString EscapeHTML(const TCgiParameters& params, const TString& name) {
        TString value = params.Get(name);
        // HTML 转义
        value = StringReplace(value, "<", "&lt;");
        value = StringReplace(value, ">", "&gt;");
        value = StringReplace(value, "&", "&amp;");
        return value;
    }
};
```

### 长度限制
```cpp
class ParameterSizeGuard {
public:
    static TCgiParameters ValidateSize(const TCgiParameters& params,
                                      size_t maxParamSize = 1024,
                                      size_t maxTotalSize = 10240) {
        TCgiParameters filtered;
        size_t totalSize = 0;

        for (const auto& [key, value] : params) {
            if (key.size() <= maxParamSize && value.size() <= maxParamSize &&
                totalSize + key.size() + value.size() <= maxTotalSize) {
                filtered.Insert(key, value);
                totalSize += key.size() + value.size();
            }
        }

        return filtered;
    }
};
```

## 调试和测试

### 参数调试
```cpp
class ParameterDebugger {
public:
    static void PrintParameters(const TCgiParameters& params,
                               IOutputStream* output = &Cout) {
        *output << "=== CGI Parameters ===" << Endl;
        for (const auto& [key, value] : params) {
            *output << key << " = " << value << Endl;
        }
        *output << "Total parameters: " << params.size() << Endl;
    }

    static bool CompareParameters(const TCgiParameters& a,
                                 const TCgiParameters& b) {
        if (a.size() != b.size()) {
            return false;
        }

        for (const auto& [key, value] : a) {
            if (!b.Has(key) || b.Get(key) != value) {
                return false;
            }
        }

        return true;
    }
};
```

### 单元测试
```cpp
// 测试用例
Y_UNIT_TEST_SUITE(CgiParametersTest) {
    Y_UNIT_TEST(BasicParsing) {
        TCgiParameters params("name=John&age=25");
        UNIT_ASSERT_EQUAL(params.Get("name"), "John");
        UNIT_ASSERT_EQUAL(params.GetI32("age"), 25);
    }

    Y_UNIT_TEST(UrlDecoding) {
        TCgiParameters params("msg=Hello+World%21");
        UNIT_ASSERT_EQUAL(params.Get("msg"), "Hello World!");
    }

    Y_UNIT_TEST(MultiValues) {
        TCgiParameters params("tags=cpp&tags=python");
        UNIT_ASSERT_EQUAL(params.NumOfValues("tags"), 2);
    }
}
```