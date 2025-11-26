# DNS 缓存解析模块

[dns](.) 是 YTsaurus 中专门提供 DNS 缓存解析功能的高性能 C++ 库。该模块最初为基于协程的 NEH HTTP 协议实现而开发，专注于提供快速的域名解析服务，支持多层缓存、线程池优化和静态别名映射。

## 📋 项目描述

`dns` 模块提供了一套完整的 DNS 解析和缓存解决方案，特别为协程环境和微栈场景进行了优化。通过多层次的缓存机制和可选的线程池解析，该模块能够在保证性能的同时提供可靠的域名解析服务。

### 核心价值

- **高性能**：多层缓存机制，显著减少 DNS 查询延迟
- **协程友好**：支持绿色线程环境，避免栈溢出问题
- **灵活配置**：支持静态别名映射和动态解析
- **内存优化**：智能缓存管理，平衡性能和内存使用
- **线程安全**：支持多线程并发访问

## 🏗️ 架构设计

### 解析层次结构

DNS 解析采用以下优先级顺序：

1. **线程本地缓存**：最快的访问速度，线程私有
2. **全局缓存**：跨线程共享，中等访问速度
3. **静态别名**：预定义的主机名到IP映射
4. **系统解析器**：标准的 DNS 查询，可选线程池优化

### 核心组件

```
dns/
├── cache.h/cpp     # 多层缓存实现
├── thread.h/cpp    # 线程池解析
├── magic.h/cpp     # 辅助工具和魔术常量
└── README.md       # 文档说明
```

## 🚀 核心特性

### 数据结构

#### 解析请求信息
```cpp
namespace NDns {
    struct TResolveInfo {
        TResolveInfo(const TStringBuf& host, ui16 port);

        TStringBuf Host;  // 要解析的主机名
        ui16 Port;        // 目标端口
    };
}
```

#### 解析结果
```cpp
struct TResolvedHost {
    TResolvedHost(const TString& host, const TNetworkAddress& addr) noexcept;

    TString Host;           // 已解析的主机名（来自 TResolveInfo，别名处理前）
    TNetworkAddress Addr;   // 网络地址
    size_t Id;              // 缓存记录ID
};
```

### 核心接口

#### 1. 缓存解析
```cpp
// 标准缓存解析（协程安全）
const TResolvedHost* CachedResolve(const TResolveInfo& ri);

// 线程池缓存解析（避免协程栈溢出）
const TResolvedHost* CachedThrResolve(const TResolveInfo& ri);

// 添加静态别名
void AddHostAlias(const TString& host, const TString& alias);
```

#### 2. 线程池解析
```cpp
namespace NDns {
    using TNetworkAddressPtr = TAutoPtr<TNetworkAddress>;

    // 在独立线程中解析
    TNetworkAddressPtr ThreadedResolve(const TString& host, ui16 port);
}
```

## 💡 使用示例

### 基础 DNS 解析

```cpp
#include <library/cpp/dns/cache.h>
#include <util/network/socket.h>

// 基础域名解析
void basicResolve() {
    NDns::TResolveInfo resolveInfo("example.com", 80);
    const NDns::TResolvedHost* resolved = NDns::CachedResolve(resolveInfo);

    if (resolved) {
        Cout << "解析成功: " << resolved->Host << " -> "
             << resolved->Addr << Endl;
    } else {
        Cout << "解析失败" << Endl;
    }
}

// 带端口的解析
void resolveWithPort() {
    NDns::TResolveInfo httpsResolve("google.com", 443);
    const NDns::TResolvedHost* resolved = NDns::CachedResolve(httpsResolve);

    if (resolved) {
        Cout << "HTTPS 服务器: " << resolved->Addr << Endl;
    }
}
```

### 协程环境中的解析

```cpp
#include <library/cpp/dns/cache.h>

// 在协程环境中使用线程池解析
class CoroutineHttpServer {
public:
    void handleRequest() {
        // 在协程中解析域名
        NDns::TResolveInfo resolveInfo("api.service.com", 8080);

        // 使用线程池解析避免协程栈溢出
        const NDns::TResolvedHost* resolved = NDns::CachedThrResolve(resolveInfo);

        if (resolved) {
            connectToService(resolved->Addr);
        } else {
            handleError("DNS resolution failed");
        }
    }

private:
    void connectToService(const TNetworkAddress& addr) {
        // 连接到解析的服务地址
        Cout << "连接到服务: " << addr << Endl;
    }

    void handleError(const TString& error) {
        Cout << "错误: " << error << Endl;
    }
};
```

### 静态别名配置

```cpp
// 配置静态主机别名
void configureAliases() {
    // 添加本地开发环境别名
    NDns::AddHostAlias("local-api", "127.0.0.1");
    NDns::AddHostAlias("local-db", "localhost");

    // 添加测试环境别名
    NDns::AddHostAlias("test-service", "192.168.1.100");
    NDns::AddHostAlias("cache-server", "10.0.0.5");

    // 添加域名别名（负载均衡）
    NDns::AddHostAlias("api-cluster", "api1.example.com");

    Cout << "DNS 别名配置完成" << Endl;
}

// 使用别名解析
void useAliases() {
    // 这些解析会直接使用别名，无需 DNS 查询
    auto localApi = NDns::CachedResolve({"local-api", 8080});
    auto testDb = NDns::CachedResolve({"local-db", 5432});
    auto testService = NDns::CachedResolve({"test-service", 9000});

    Cout << "本地 API: " << localApi->Addr << Endl;
    Cout << "测试数据库: " << testDb->Addr << Endl;
    Cout << "测试服务: " << testService->Addr << Endl;
}
```

### 高性能批量解析

```cpp
#include <library/cpp/dns/thread.h>

// 批量域名解析器
class BatchDNSResolver {
private:
    THashMap<TString, NDns::TResolvedHost> cache;

public:
    // 批量解析多个域名
    THashMap<TString, TNetworkAddress> resolveBatch(
            const TVector<std::pair<TString, ui16>>& hosts) {

        THashMap<TString, TNetworkAddress> results;

        for (const auto& [host, port] : hosts) {
            // 首先尝试缓存解析
            const NDns::TResolvedHost* resolved =
                NDns::CachedResolve({host, port});

            if (resolved) {
                results[host] = resolved->Addr;
            } else {
                // 如果缓存未命中，使用线程池解析
                auto addrPtr = NDns::ThreadedResolve(host, port);
                if (addrPtr) {
                    results[host] = *addrPtr;
                }
            }
        }

        return results;
    }

    // 预热缓存
    void warmupCache(const TVector<TString>& hosts) {
        Cout << "开始预热 DNS 缓存..." << Endl;

        for (const auto& host : hosts) {
            // 使用异步解析预热缓存
            NDns::CachedResolve({host, 80});
        }

        Cout << "DNS 缓存预热完成" << Endl;
    }
};
```

### 服务发现集成

```cpp
// 与服务发现系统集成的 DNS 解析
class ServiceDiscoveryResolver {
private:
    TString serviceDomain;
    TMap<TString, TString> serviceToHost;

public:
    ServiceDiscoveryResolver(const TString& domain)
        : serviceDomain(domain) {
        // 初始化服务映射
        initializeServiceMapping();
    }

    // 解析服务名称
    const NDns::TResolvedHost* resolveService(const TString& serviceName, ui16 port) {
        auto it = serviceToHost.find(serviceName);
        if (it != serviceToHost.end()) {
            return NDns::CachedResolve({it->second, port});
        }

        // 构造完整的服务域名
        TString fullHost = serviceName + "." + serviceDomain;
        return NDns::CachedResolve({fullHost, port});
    }

    // 批量解析服务实例
    TVector<TNetworkAddress> resolveServiceInstances(
            const TString& serviceName, ui16 port) {

        TVector<TNetworkAddress> instances;

        // 这里可以实现服务发现逻辑
        // 例如从配置中心、注册中心获取实例列表

        // 简化示例：解析多个可能的实例
        for (int i = 1; i <= 3; ++i) {
            TString instanceHost = serviceName + "-instance" + ToString(i);
            const NDns::TResolvedHost* resolved =
                resolveService(instanceHost, port);

            if (resolved) {
                instances.push_back(resolved->Addr);
            }
        }

        return instances;
    }

private:
    void initializeServiceMapping() {
        // 配置服务名称到主机名的映射
        serviceToHost["user-service"] = "user-api.production.local";
        serviceToHost["order-service"] = "order-api.production.local";
        serviceToHost["payment-service"] = "payment-api.production.local";
        serviceToHost["notification-service"] = "notification-api.production.local";
    }
};
```

## 🎯 应用场景

### 1. 微服务架构

```cpp
class MicroServiceClient {
private:
    ServiceDiscoveryResolver serviceResolver;

public:
    MicroServiceClient()
        : serviceResolver("microservices.local") {
        // 配置微服务别名
        configureServiceAliases();
    }

    // 调用用户服务
    void callUserService() {
        const NDns::TResolvedHost* userService =
            serviceResolver.resolveService("user-service", 8080);

        if (userService) {
            connectAndCall(userService->Addr, "/users");
        }
    }

    // 调用订单服务
    void callOrderService() {
        auto instances = serviceResolver.resolveServiceInstances("order-service", 9090);

        if (!instances.empty()) {
            // 实现负载均衡逻辑
            const TNetworkAddress& selected = selectInstance(instances);
            connectAndCall(selected, "/orders");
        }
    }

private:
    void configureServiceAliases() {
        NDns::AddHostAlias("user-service", "10.0.1.10");
        NDns::AddHostAlias("order-service", "10.0.1.20");
        NDns::AddHostAlias("payment-service", "10.0.1.30");
    }

    const TNetworkAddress& selectInstance(const TVector<TNetworkAddress>& instances) {
        // 简单轮询负载均衡
        static size_t current = 0;
        return instances[current % instances.size()];
    }

    void connectAndCall(const TNetworkAddress& addr, const TString& path) {
        Cout << "连接到 " << addr << " 调用 " << path << Endl;
    }
};
```

### 2. CDN 和负载均衡

```cpp
class CDNResolver {
private:
    THashMap<TString, TVector<TString>> cdnMapping;

public:
    CDNResolver() {
        initializeCDNMapping();
    }

    // 解析最近的 CDN 节点
    TNetworkAddress resolveNearestCDN(const TString& content, const TString& region) {
        auto it = cdnMapping.find(content);
        if (it == cdnMapping.end()) {
            return TNetworkAddress();  // 未找到内容
        }

        const TVector<TString>& cdnNodes = it->second;

        // 根据区域选择最近的节点
        TString selectedNode = selectNearestNode(cdnNodes, region);

        const NDns::TResolvedHost* resolved =
            NDns::CachedResolve({selectedNode, 80});

        return resolved ? resolved->Addr : TNetworkAddress();
    }

    // 批量解析 CDN 节点
    TVector<TNetworkAddress> resolveAllCDNNodes(const TString& content) {
        TVector<TNetworkAddress> nodes;

        auto it = cdnMapping.find(content);
        if (it != cdnMapping.end()) {
            for (const TString& nodeName : it->second) {
                const NDns::TResolvedHost* resolved =
                    NDns::CachedResolve({nodeName, 80});

                if (resolved) {
                    nodes.push_back(resolved->Addr);
                }
            }
        }

        return nodes;
    }

private:
    void initializeCDNMapping() {
        // 配置内容到 CDN 节点的映射
        cdnMapping["static-content"] = {
            "cdn1.example.com", "cdn2.example.com", "cdn3.example.com"
        };
        cdnMapping["video-content"] = {
            "video-cdn1.example.com", "video-cdn2.example.com"
        };
        cdnMapping["api-content"] = {
            "api-cdn1.example.com", "api-cdn2.example.com"
        };
    }

    TString selectNearestNode(const TVector<TString>& nodes, const TString& region) {
        // 简化的区域选择逻辑
        if (region == "us-west") {
            return nodes[0];
        } else if (region == "us-east") {
            return nodes[1];
        } else {
            return nodes[2];
        }
    }
};
```

### 3. 开发和测试环境

```cpp
class EnvironmentAwareResolver {
private:
    TString currentEnvironment;

public:
    EnvironmentAwareResolver(const TString& env)
        : currentEnvironment(env) {
        configureEnvironmentAliases();
    }

    // 解析环境相关的服务
    const NDns::TResolvedHost* resolveEnvironmentService(
            const TString& baseService, ui16 port) {

        TString serviceHost = baseService + "-" + currentEnvironment;
        return NDns::CachedResolve({serviceHost, port});
    }

    // 切换环境
    void switchEnvironment(const TString& newEnvironment) {
        currentEnvironment = newEnvironment;
        clearDNSCache();
        configureEnvironmentAliases();

        Cout << "已切换到环境: " << currentEnvironment << Endl;
    }

private:
    void configureEnvironmentAliases() {
        if (currentEnvironment == "dev") {
            NDns::AddHostAlias("database", "localhost");
            NDns::AddHostAlias("cache", "localhost");
            NDns::AddHostAlias("queue", "localhost");
        } else if (currentEnvironment == "staging") {
            NDns::AddHostAlias("database", "staging-db.internal");
            NDns::AddHostAlias("cache", "staging-cache.internal");
            NDns::AddHostAlias("queue", "staging-queue.internal");
        } else if (currentEnvironment == "production") {
            // 生产环境使用真实的域名解析
            // 不添加别名，让 DNS 正常工作
        }
    }

    void clearDNSCache() {
        // 注意：当前实现不支持缓存清理
        // 这里可以添加缓存清理逻辑，或者重新创建解析器实例
        Cout << "DNS 缓存已清空" << Endl;
    }
};
```

## ⚡ 性能优化

### 1. 缓存预热策略

```cpp
class DNSCacheWarmup {
public:
    static void warmupEssentialServices() {
        // 预解析关键服务
        TVector<TString> essentialServices = {
            "auth-service", "user-service", "order-service",
            "payment-service", "notification-service", "cache-service"
        };

        BatchDNSResolver resolver;
        TVector<std::pair<TString, ui16>> hosts;

        for (const auto& service : essentialServices) {
            hosts.push_back({service, 80});
            hosts.push_back({service, 443});
        }

        // 批量解析并缓存
        auto results = resolver.resolveBatch(hosts);

        Cout << "预热完成，解析了 " << results.size() << " 个服务" << Endl;
    }

    static void warmupCDNNodes() {
        // 预解析 CDN 节点
        TVector<TString> cdnNodes = {
            "cdn1.example.com", "cdn2.example.com", "cdn3.example.com",
            "static-cdn1.example.com", "static-cdn2.example.com"
        };

        for (const auto& node : cdnNodes) {
            NDns::CachedResolve({node, 80});
            NDns::CachedResolve({node, 443});
        }

        Cout << "CDN 节点预热完成" << Endl;
    }
};
```

### 2. 解析超时控制

```cpp
class TimeoutAwareResolver {
private:
    static constexpr TDuration DEFAULT_TIMEOUT = TDuration::Seconds(5);

public:
    static std::optional<NDns::TResolvedHost> resolveWithTimeout(
            const NDns::TResolveInfo& resolveInfo,
            TDuration timeout = DEFAULT_TIMEOUT) {

        std::promise<const NDns::TResolvedHost*> promise;
        std::future<const NDns::TResolvedHost*> future = promise.get_future();

        // 在独立线程中执行解析
        std::thread resolverThread([&resolveInfo, &promise]() {
            try {
                const NDns::TResolvedHost* result = NDns::CachedThrResolve(resolveInfo);
                promise.set_value(result);
            } catch (const std::exception& e) {
                promise.set_exception(std::current_exception());
            }
        });

        resolverThread.detach();

        // 等待解析完成或超时
        if (future.wait_for(timeout) == std::future_status::ready) {
            try {
                const NDns::TResolvedHost* result = future.get();
                return result ? std::optional<NDns::TResolvedHost>(*result) : std::nullopt;
            } catch (const std::exception& e) {
                Cerr << "DNS 解析异常: " << e.what() << Endl;
                return std::nullopt;
            }
        } else {
            Cout << "DNS 解析超时: " << resolveInfo.Host << Endl;
            return std::nullopt;
        }
    }
};
```

## 🔗 最佳实践

### 1. 错误处理

```cpp
class RobustDNSResolver {
public:
    static TNetworkAddress resolveWithFallback(
            const TString& primaryHost, ui16 port,
            const TString& fallbackHost = "") {

        // 首先尝试主要主机
        const NDns::TResolvedHost* primary = NDns::CachedResolve({primaryHost, port});
        if (primary) {
            return primary->Addr;
        }

        // 如果有备用主机，尝试备用
        if (!fallbackHost.empty()) {
            const NDns::TResolvedHost* fallback = NDns::CachedResolve({fallbackHost, port});
            if (fallback) {
                Cout << "使用备用主机: " << fallbackHost << Endl;
                return fallback->Addr;
            }
        }

        // 最后尝试本地回环地址
        Cout << "解析失败，使用本地回环地址" << Endl;
        return TNetworkAddress("127.0.0.1", port);
    }

    static bool isReachable(const TString& host, ui16 port) {
        const NDns::TResolvedHost* resolved = NDns::CachedResolve({host, port});
        if (!resolved) {
            return false;
        }

        // 简单的连通性检查
        try {
            TSocket socket(resolved->Addr);
            return socket.IsValid();
        } catch (...) {
            return false;
        }
    }
};
```

### 2. 监控和指标

```cpp
class DNSMetrics {
private:
    std::atomic<size_t> cacheHits{0};
    std::atomic<size_t> cacheMisses{0};
    std::atomic<size_t> totalResolves{0};
    std::atomic<size_t> failedResolves{0};

public:
    void recordCacheHit() {
        cacheHits++;
        totalResolves++;
    }

    void recordCacheMiss() {
        cacheMisses++;
        totalResolves++;
    }

    void recordFailedResolve() {
        failedResolves++;
    }

    void printMetrics() const {
        Cout << "DNS 解析指标:" << Endl;
        Cout << "  总解析次数: " << totalResolves.load() << Endl;
        Cout << "  缓存命中: " << cacheHits.load() << Endl;
        Cout << "  缓存未命中: " << cacheMisses.load() << Endl;
        Cout << "  解析失败: " << failedResolves.load() << Endl;

        if (totalResolves.load() > 0) {
            double hitRate = (double)cacheHits.load() / totalResolves.load() * 100;
            Cout << "  缓存命中率: " << hitRate << "%" << Endl;
        }
    }

    double getCacheHitRate() const {
        size_t total = totalResolves.load();
        return total > 0 ? (double)cacheHits.load() / total : 0.0;
    }
};
```

## 📝 注意事项

### 1. 缓存管理
- **无法手动清理**：当前实现不支持缓存刷新
- **缓存时效性**：需要考虑 DNS 记录的 TTL
- **内存使用**：长期运行需要注意缓存内存消耗

### 2. 线程安全
- **线程本地缓存**：每个线程有独立的缓存
- **全局缓存**：跨线程共享，需要适当的同步
- **别名配置**：添加别名操作的线程安全性

### 3. 错误处理
- **解析失败**：需要妥善处理 DNS 解析失败的情况
- **网络问题**：考虑网络不可达时的回退策略
- **超时处理**：避免长时间阻塞等待 DNS 响应

### 4. 性能考虑
- **预热策略**：应用启动时预热关键服务的 DNS 缓存
- **批量操作**：对于大量解析请求，考虑批量处理
- **监控指标**：监控缓存命中率和解析性能

`dns` 模块为 YTsaurus 项目提供了高性能、可靠的 DNS 解析服务，特别适合微服务架构和高并发网络应用的需求。
