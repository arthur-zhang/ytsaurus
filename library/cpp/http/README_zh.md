# HTTP 处理库

## 项目概述

HTTP 处理库是一个功能完整的 C++ HTTP 协议实现，提供了 HTTP 客户端、服务器和协议处理的核心组件。该库支持 HTTP/1.1 协议，包含 Keep-Alive 连接、HTTPS 支持、压缩传输等高级特性，为构建高性能网络应用程序提供了坚实基础。

## 架构设计

### 模块结构
- **`/server/`** - HTTP 服务器实现
- **`/simple/`** - 简化 HTTP 客户端
- **`/fetch/`** - HTTP 抓取和爬虫功能
- **`/io/`** - HTTP I/O 流处理
- **`/misc/`** - HTTP 协议工具和常量
- **`/push_parser/`** - 推式 HTTP 解析器

## 核心组件

### HTTP 服务器 (`/server/`)

#### 主要类
- **`THttpServer`** - 主服务器类
  - 支持多线程处理
  - 可配置的工作队列
  - 优雅关闭机制
  - 连接管理和超时控制

- **`TClientRequest`** - 客户端请求处理（已弃用）
- **`TRequestReplier`** - 现代请求响应处理器

#### 关键文件
- **`http.h`** - 服务器核心接口定义
- **`conn.h`** - 连接管理
- **`options.h`** - 服务器配置选项
- **`response.h`** - HTTP 响应构建

### HTTP 客户端 (`/simple/`)

#### 客户端类型
- **`TKeepAliveHttpClient`** - 支持连接复用的客户端
  - 线程不安全
  - 连接池支持
  - 自动重连机制
  - HTTPS 证书验证

- **`TSimpleHttpClient`** - 简单客户端
  - 线程安全
  - 每次请求关闭连接
  - HTTP 状态码异常处理

- **`TRedirectableHttpClient`** - 支持重定向的客户端

#### 关键特性
- GET/POST/PUT/DELETE 等所有 HTTP 方法支持
- 自定义请求头
- 响应流处理
- 取消令牌支持
- HTTPS/TLS 加密

### HTTP I/O 流 (`/io/`)

#### 核心类
- **`THttpInput`** - HTTP 输入流
  - 自动头部解析
  - 分块传输解码
  - 内容解压缩
  - Trailer 处理

- **`THttpOutput`** - HTTP 输出流
  - 头部管理
  - 压缩传输
  - 分块编码
  - Keep-Alive 支持

#### 支持功能
- **压缩支持**：gzip、deflate、br（brotli）
- **传输编码**：chunked、identity
- **内容编码**：自动压缩/解压缩
- **协议特性**：Keep-Alive、HTTP/1.1

### HTTP 抓取 (`/fetch/`)

#### 功能模块
- **`THttpFetcher`** - 网页抓取器
- **`THttpParser`** - HTTP 响应解析器
- **`THttpFSM`** - 有限状态机解析器
- **`THttpAgent`** - 用户代理管理

#### 特性
- 高性能状态机解析
- 摘要认证支持
- 扩展 HTTP 状态码
- HREF 语言处理
- 容错和重试机制

### 协议工具 (`/misc/`)

#### 实用工具
- **HTTP 状态码**：标准状态码常量
- **日期处理**：HTTP 日期格式解析
- **请求解析**：请求数据结构
- **编码支持**：字符集转换

## 使用示例

### HTTP 服务器
```cpp
#include <library/cpp/http/server/http.h>

class MyHttpRequestHandler: public THttpServer::ICallBack {
public:
    TClientRequest* CreateClient() override {
        return new MyRequestReplier();
    }

    void OnListenStart() override {
        Cerr << "Server started" << Endl;
    }
};

class MyRequestReplier: public TRequestReplier {
public:
    bool DoReply(const TReplyParams& params) override {
        THttpInput& input = params.Input;
        THttpOutput& output = params.Output;

        // 发送响应
        output << "HTTP/1.1 200 OK\r\n";
        output << "Content-Type: text/plain\r\n";
        output << "Connection: keep-alive\r\n\r\n";
        output << "Hello, World!";

        return true;
    }
};

// 创建并启动服务器
THttpServerOptions options;
options.Port = 8080;
options.MaxConnections = 1000;

MyHttpRequestHandler handler;
THttpServer server(&handler, options);
server.Start();
server.Wait();
```

### HTTP 客户端
```cpp
#include <library/cpp/http/simple/http_client.h>

// Keep-Alive 客户端
TKeepAliveHttpClient client("api.example.com", 443);

// GET 请求
TString response;
auto code = client.DoGet("/api/data", &response);
if (code == 200) {
    Cout << "Response: " << response << Endl;
}

// POST 请求
TString jsonBody = R"({"name": "test", "value": 123})";
THeaders headers = {
    {"Content-Type", "application/json"},
    {"Authorization", "Bearer token123"}
};

code = client.DoPost("/api/create", jsonBody, nullptr, headers);

// 简单客户端（线程安全）
TSimpleHttpClient simpleClient("api.example.com", 443);
simpleClient.DoGet("/api/data", &response);
```

### HTTP I/O 流
```cpp
#include <library/cpp/http/io/stream.h>

// HTTP 输入流
TSocket socket = ConnectToServer();
THttpInput httpInput(&socket);

// 获取响应头
const THttpHeaders& headers = httpInput.Headers();
const TString& firstLine = httpInput.FirstLine();

// 读取响应体
char buffer[1024];
size_t bytesRead = httpInput.Read(buffer, sizeof(buffer));

// 检查压缩支持
if (httpInput.AcceptEncoding("gzip")) {
    TString bestScheme = httpInput.BestCompressionScheme();
}

// HTTP 输出流
THttpOutput httpOutput(&socket);
httpOutput.EnableCompression(true);
httpOutput.EnableKeepAlive(true);

httpOutput << "HTTP/1.1 200 OK\r\n";
httpOutput << "Content-Type: application/json\r\n\r\n";
httpOutput << jsonData;
```

## 实现原理

### 高性能设计
1. **零拷贝**：最小化内存复制操作
2. **异步 I/O**：非阻塞网络操作
3. **连接池**：复用 TCP 连接
4. **内存池**：减少内存分配开销

### 协议兼容性
1. **HTTP/1.1**：完整的 HTTP/1.1 支持
2. **RFC 标准**：严格遵循 RFC 7230-7235
3. **TLS/HTTPS**：OpenSSL 集成
4. **压缩算法**：gzip、deflate、brotli

### 错误处理
1. **异常安全**：RAII 资源管理
2. **重试机制**：网络错误自动重试
3. **超时控制**：连接和读写超时
4. **优雅关闭**：安全的服务器关闭

## 应用场景

### Web 服务
- **RESTful API**：构建高性能 Web API
- **微服务**：服务间通信
- **Web 框架**：作为底层 HTTP 库
- **负载均衡**：HTTP 代理和网关

### 数据抓取
- **网络爬虫**：大规模网页抓取
- **API 集成**：第三方服务对接
- **监控采集**：系统监控数据收集
- **数据同步**：分布式系统数据同步

### 代理服务
- **正向代理**：客户端代理
- **反向代理**：服务器代理
- **HTTP 隧道**：网络隧道
- **缓存服务**：HTTP 缓存代理

## 性能特点

### 高并发
- **多线程**：支持数千并发连接
- **事件驱动**：高效的 I/O 多路复用
- **连接复用**：Keep-Alive 和连接池
- **零拷贝**：优化数据传输路径

### 低延迟
- **内存预分配**：减少运行时分配
- **批量操作**：合并小的 I/O 操作
- **缓存友好**：优化数据结构布局
- **系统调用优化**：减少系统调用次数

### 可扩展性
- **模块化设计**：易于扩展新功能
- **插件架构**：支持自定义处理器
- **配置灵活**：丰富的配置选项
- **平台兼容**：跨平台支持

## 安全特性

### HTTPS/TLS
- **证书验证**：服务器证书验证
- **客户端证书**：双向认证支持
- **加密套件**：现代加密算法
- **协议版本**：TLS 1.2+ 支持

### 输入验证
- **长度限制**：防止缓冲区溢出
- **格式验证**：HTTP 协议验证
- **编码检查**：字符编码验证
- **头部过滤**：恶意头部过滤

### 访问控制
- **IP 限制**：基于 IP 的访问控制
- **速率限制**：请求频率限制
- **超时保护**：防止慢速攻击
- **资源限制**：连接数和内存限制