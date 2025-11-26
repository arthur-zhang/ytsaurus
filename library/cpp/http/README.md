# HTTP 库

完整的 HTTP 客户端和服务器实现库。

## 概述

该库提供了完整的 HTTP 协议实现，包括 HTTP 客户端、服务器、解析器等组件。支持 HTTP/1.1 协议，提供了高性能、易用的 HTTP 接口。

## 核心组件

### HTTP 客户端
位于 `fetch/` 目录：
- **HTTP 请求**: 支持 GET、POST、PUT、DELETE 等方法
- **连接管理**: 智能的连接池和重用机制
- **HTTPS 支持**: 完整的 TLS/SSL 支持
- **代理支持**: HTTP 代理和 SOCKS 代理

### HTTP 服务器
位于 `server/` 目录：
- **请求处理**: 高效的 HTTP 请求处理
- **路由系统**: 灵活的路由配置
- **静态文件**: 静态文件服务
- **WebSocket**: WebSocket 协议支持

### HTTP 解析器
位于 `push_parser/` 目录：
- **流式解析**: 高效的流式 HTTP 解析
- **内存友好**: 低内存占用的解析算法
- **错误处理**: 完善的错误检测和恢复

### HTTP I/O
位于 `io/` 目录：
- **网络通信**: 底层的网络 I/O 处理
- **异步处理**: 非阻塞的异步 I/O
- **缓冲管理**: 智能的数据缓冲

## 使用示例

### HTTP 客户端
```cpp
#include <http/fetch.h>

// 简单的 GET 请求
auto response = HttpFetch("https://api.example.com/data");

// 带参数的请求
THttpRequest request;
request.SetMethod("POST");
request.SetUrl("https://api.example.com/submit");
request.SetBody("{\"key\":\"value\"}");
request.SetHeader("Content-Type", "application/json");

auto response = HttpFetch(request);

// 异步请求
auto future = AsyncHttpFetch("https://api.example.com/data");
auto response = future.GetValue();
```

### HTTP 服务器
```cpp
#include <http/server.h>

class TMyHttpServer: public THttpServer {
public:
    void HandleRequest(const THttpRequest& request, THttpResponse& response) override {
        if (request.GetPath() == "/api/data") {
            response.SetStatusCode(200);
            response.SetBody("{\"status\":\"ok\"}");
        } else {
            response.SetStatusCode(404);
            response.SetBody("Not Found");
        }
    }
};

TMyHttpServer server;
server.SetPort(8080);
server.Start();
```

### HTTP 解析
```cpp
#include <http/push_parser.h>

class THttpHandler {
public:
    void OnMethod(const TString& method) {
        std::cout << "Method: " << method << std::endl;
    }

    void OnUrl(const TString& url) {
        std::cout << "URL: " << url << std::endl;
    }

    void OnHeader(const TString& name, const TString& value) {
        std::cout << "Header: " << name << ": " << value << std::endl;
    }
};

TPushHttpParser parser;
parser.SetHandler(&THttpHandler());
parser.Parse(httpData);
```

## 主要特性

### 协议支持
- **HTTP/1.1**: 完整的 HTTP/1.1 协议支持
- **HTTPS**: TLS/SSL 加密通信
- **Keep-Alive**: 连接保持和重用
- **Chunked**: 分块传输编码

### 性能优化
- **异步 I/O**: 非阻塞的异步网络通信
- **连接池**: 智能的连接管理和重用
- **内存池**: 高效的内存分配和重用
- **零拷贝**: 最小化数据拷贝操作

### 安全性
- **证书验证**: SSL/TLS 证书验证
- **安全头**: 安全相关的 HTTP 头处理
- **输入验证**: 防止恶意输入攻击
- **超时控制**: 请求和响应超时保护

## 应用场景

### API 客户端
```cpp
class TApiClient {
private:
    TString baseUrl_;
    TString apiKey_;

public:
    TApiClient(const TString& baseUrl, const TString& apiKey)
        : baseUrl_(baseUrl), apiKey_(apiKey)
    {}

    TJsonDocument GetData(const TString& endpoint) {
        THttpRequest request;
        request.SetUrl(baseUrl_ + endpoint);
        request.SetHeader("Authorization", "Bearer " + apiKey_);

        auto response = HttpFetch(request);
        return TJsonDocument::Parse(response.GetBody());
    }
};
```

### 微服务通信
```cpp
// 服务间通信
class TServiceClient {
public:
    THttpResponse CallService(const TString& service, const TJsonDocument& request) {
        THttpRequest httpReq;
        httpReq.SetMethod("POST");
        httpReq.SetUrl(GetServiceUrl(service));
        httpReq.SetBody(request.ToString());
        httpReq.SetHeader("Content-Type", "application/json");

        return HttpFetch(httpReq);
    }
};
```

### 文件上传下载
```cpp
// 文件上传
THttpResponse UploadFile(const TString& url, const TString& filePath) {
    THttpRequest request;
    request.SetMethod("POST");
    request.SetUrl(url);

    // 添加文件
    THttpFormData formData;
    formData.AddFile("file", filePath);
    request.SetBody(formData);

    return HttpFetch(request);
}

// 文件下载
void DownloadFile(const TString& url, const TString& outputPath) {
    auto response = HttpFetch(url);

    TFile file(outputPath, CreateAlways | WR_ONLY);
    file.Write(response.GetBody());
}
```

## 配置选项

### 客户端配置
```cpp
THttpClientConfig config;
config.SetTimeout(30000);           // 30秒超时
config.SetMaxRetries(3);            // 最大重试次数
config.SetUserAgent("MyApp/1.0");   // User-Agent
config.SetProxy("http://proxy:8080"); // 代理设置

THttpClient client(config);
```

### 服务器配置
```cpp
THttpServerConfig config;
config.SetPort(8080);
config.SetMaxConnections(1000);
config.SetKeepAliveTimeout(300000);  // 5分钟
config.SetStaticDir("/var/www");     // 静态文件目录

THttpServer server(config);
```

## 错误处理

### 异常类型
```cpp
try {
    auto response = HttpFetch("https://example.com");
} catch (const THttpException& e) {
    std::cerr << "HTTP Error: " << e.what() << std::endl;
} catch (const TNetworkException& e) {
    std::cerr << "Network Error: " << e.what() << std::endl;
} catch (const TTimeoutException& e) {
    std::cerr << "Timeout Error: " << e.what() << std::endl;
}
```

### 重试机制
```cpp
TRetryPolicy retryPolicy;
retryPolicy.SetMaxAttempts(3);
retryPolicy.SetBackoff(1000);  // 1秒

auto response = HttpFetchWithRetry(url, retryPolicy);
```

## 中间件支持

### 请求中间件
```cpp
class TAuthMiddleware: public IHttpMiddleware {
public:
    void ProcessRequest(THttpRequest& request) override {
        // 添加认证头
        request.SetHeader("Authorization", GetAuthToken());
    }
};

THttpClient client;
client.AddMiddleware(MakeHolder<TAuthMiddleware>());
```

### 响应中间件
```cpp
class TLoggingMiddleware: public IHttpMiddleware {
public:
    void ProcessResponse(const THttpResponse& response) override {
        std::cout << "Response: " << response.GetStatusCode() << std::endl;
    }
};
```

## 最佳实践

### 连接管理
```cpp
// 使用连接池
THttpClient client;
client.EnableConnectionPool();
client.SetMaxConnectionsPerHost(10);
```

### 超时设置
```cpp
// 合理的超时设置
THttpRequest request;
request.SetConnectTimeout(10000);    // 10秒连接超时
request.SetReadTimeout(30000);       // 30秒读取超时
request.SetTotalTimeout(60000);      // 60秒总超时
```

### 错误处理
```cpp
// 健壮的错误处理
auto response = HttpFetch(url);

if (!response.IsSuccess()) {
    if (response.GetStatusCode() == 401) {
        // 处理认证错误
    } else if (response.GetStatusCode() >= 500) {
        // 处理服务器错误
    } else {
        // 处理其他错误
    }
}
```

## 性能优化

### 批量请求
```cpp
// 并发请求
TVector<TFuture<THttpResponse>> futures;
for (const auto& url : urls) {
    futures.push_back(AsyncHttpFetch(url));
}

for (auto& future : futures) {
    auto response = future.GetValue();
    ProcessResponse(response);
}
```

### 缓存机制
```cpp
// HTTP 缓存
class THttpCache {
private:
    THashMap<TString, THttpResponse> cache_;

public:
    THttpResponse Get(const TString& url) {
        auto it = cache_.find(url);
        if (it != cache_.end() && !IsExpired(it->second)) {
            return it->second;
        }

        auto response = HttpFetch(url);
        cache_[url] = response;
        return response;
    }
};
```

## 测试和调试

### Mock 服务器
```cpp
class TMockHttpServer: public THttpServer {
public:
    void HandleRequest(const THttpRequest& request, THttpResponse& response) override {
        if (request.GetPath() == "/test") {
            response.SetStatusCode(200);
            response.SetBody("{\"test\": \"ok\"}");
        }
    }
};
```

### 调试工具
```cpp
// 启用调试日志
SetHttpLogLevel("debug");

// 请求跟踪
EnableHttpTracing();

// 性能分析
EnableHttpProfiling();
```

这个 HTTP 库为 YTsaurus 项目提供了完整的网络通信能力，支持从简单的 HTTP 请求到复杂的微服务架构等各种应用场景。