# SyncMap 同步映射库

## 项目概述

`NSyncMap` 是 YTsaurus 中的线程安全插入式哈希映射库，专门针对读多写少的工作负载进行优化。该映射在未修改状态下提供无锁的读操作，修改后的 O(n) 次读操作需要获取锁，是 YTsaurus 中高性能并发访问的核心数据结构。

## 核心功能

- **无锁读取**：读多写少场景下的高性能无锁访问
- **线程安全**：完全线程安全的并发访问支持
- **插入式设计**：只支持插入操作的内存友好设计
- **快照机制**：支持只读部分的迭代操作
- **自定义配置**：支持自定义哈希函数、比较函数和锁类型
- **内存优化**：使用引用计数和 hazard pointer 技术优化内存管理

## 主要接口

### TSyncMap 模板类

```cpp
#include <yt/yt/library/syncmap/map.h>

using namespace NYT::NConcurrency;

// 创建同步映射
TSyncMap<int, std::string> map;

// 基本操作
auto* value = map.Find(42);                           // 查找
auto [ptr, inserted] = map.FindOrInsert(42, []() {   // 查找或插入
    return std::string("hello");
});

// 就地构造
auto [ptr2, inserted2] = map.FindOrEmplace(42, "world");

// 默认值查找
auto [ptr3, inserted3] = map.FindOrDefault(99);      // 不存在时创建默认值

// 刷新脏数据
map.Flush();

// 只读迭代
map.IterateReadOnly([](const int& key, std::string& value) {
    std::cout << key << ": " << value << std::endl;
});
```

### 自定义配置

```cpp
// 使用自定义哈希函数和锁类型
struct CustomHash {
    size_t operator()(const std::string& key) const {
        return std::hash<std::string>{}(key.substr(0, 8));  // 只使用前8个字符
    }
};

// 使用读写锁
TSyncMap<std::string, int, CustomHash, std::equal_to<std::string>, TAdaptiveLock> mapWithCustomLock;

// 使用比较函数
TSyncMap<std::string, int, CustomHash, std::less<std::string>> mapWithCustomCompare;
```

## 使用方法

### 基本用法示例

```cpp
#include <yt/yt/library/syncmap/map.h>

using namespace NYT::NConcurrency;

class CacheManager {
public:
    CacheManager() {
        // 初始化缓存映射
        cache_ = std::make_unique<TSyncMap<std::string, CachedData>>();
    }

    // 获取缓存数据
    CachedData* getCache(const std::string& key) {
        auto* data = cache_->Find(key);
        if (data) {
            return data;
        }

        // 如果不存在则创建并插入
        auto [ptr, inserted] = cache_->FindOrInsert(key, [&key]() {
            return loadCacheFromStorage(key);
        });

        return ptr;
    }

    // 获取或创建缓存数据
    template<typename... Args>
    CachedData* getOrCreateCache(const std::string& key, Args&&... args) {
        auto [ptr, inserted] = cache_->FindOrEmplace(key, std::forward<Args>(args)...);
        return ptr;
    }

    // 刷新缓存
    void flushCache() {
        cache_->Flush();
    }

    // 遍历缓存
    void iterateCache(std::function<void(const std::string&, const CachedData&)> visitor) {
        cache_->IterateReadOnly([&visitor](const std::string& key, CachedData& data) {
            visitor(key, data);
        });
    }

private:
    std::unique_ptr<TSyncMap<std::string, CachedData>> cache_;

    CachedData loadCacheFromStorage(const std::string& key) {
        // 从存储加载数据的实现
        return CachedData{/* ... */};
    }
};
```

### 高性能配置管理

```cpp
#include <yt/yt/library/syncmap/map.h>

using namespace NYT::NConcurrency;

class HighPerformanceConfigManager {
public:
    HighPerformanceConfigManager() {
        // 使用自定义配置优化性能
        configMap_ = std::make_unique<TSyncMap<
            std::string,
            ConfigValue,
            FastStringHash,          // 快速字符串哈希
            std::equal_to<std::string>,
            NThreading::TSpinLock    // 使用自旋锁
        >>();
    }

    // 获取配置值
    ConfigValue* getConfig(const std::string& key) {
        // 快速查找，大多数情况下无锁
        return configMap_->Find(key);
    }

    // 设置配置值
    void setConfig(const std::string& key, const ConfigValue& value) {
        // 只支持插入，不支持更新（设计要求）
        configMap_->FindOrInsert(key, [&value]() { return value; });
    }

    // 批量加载配置
    void loadConfigurations(const std::vector<std::pair<std::string, ConfigValue>>& configs) {
        for (const auto& [key, value] : configs) {
            configMap_->FindOrInsert(key, [&value]() { return value; });
        }

        // 批量插入后刷新
        configMap_->Flush();
    }

    // 配置热重载
    void reloadConfiguration() {
        configMap_->Flush();  // 确保所有新配置都可见
    }

    // 统计配置数量
    size_t getConfigCount() const {
        std::atomic<size_t> count{0};
        configMap_->IterateReadOnly([&count](const std::string&, const ConfigValue&) {
            count.fetch_add(1, std::memory_order_relaxed);
        });
        return count.load();
    }

private:
    std::unique_ptr<TSyncMap<std::string, ConfigValue, FastStringHash, std::equal_to<std::string>, NThreading::TSpinLock>> configMap_;

    struct FastStringHash {
        size_t operator()(const std::string& key) const {
            // 快速哈希算法
            size_t hash = 5381;
            for (char c : key) {
                hash = ((hash << 5) + hash) + c;
            }
            return hash;
        }
    };
};
```

### 复杂数据结构管理

```cpp
#include <yt/yt/library/syncmap/map.h>

using namespace NYT::NConcurrency;

class SessionManager {
public:
    SessionManager() {
        sessions_ = std::make_unique<TSyncMap<std::string, SessionData>>();
    }

    // 创建会话
    SessionData* createSession(const std::string& sessionId, const UserInfo& user) {
        auto [ptr, inserted] = sessions_->FindOrEmplace(
            sessionId,
            sessionId,
            user,
            TInstant::Now(),
            generateSessionToken()
        );

        if (inserted) {
            // 新会话创建成功
            onSessionCreated(sessionId);
        }

        return ptr;
    }

    // 获取会话
    SessionData* getSession(const std::string& sessionId) {
        return sessions_->Find(sessionId);
    }

    // 批量清理过期会话
    void cleanupExpiredSessions() {
        std::vector<std::string> expiredSessions;

        // 收集过期会话
        sessions_->IterateReadOnly([&expiredSessions](const std::string& id, SessionData& session) {
            if (session.isExpired()) {
                expiredSessions.push_back(id);
            }
        });

        // 注意：SyncMap 不支持删除，所以这里只是标记为过期
        // 实际的清理可能需要在其他层次处理
        for (const auto& id : expiredSessions) {
            markSessionExpired(id);
        }
    }

    // 会话统计
    SessionStatistics getStatistics() const {
        SessionStatistics stats;
        std::atomic<size_t> totalSessions{0};
        std::atomic<size_t> activeSessions{0};

        sessions_->IterateReadOnly([&](const std::string&, SessionData& session) {
            totalSessions.fetch_add(1, std::memory_order_relaxed);
            if (!session.isExpired()) {
                activeSessions.fetch_add(1, std::memory_order_relaxed);
            }
        });

        stats.totalSessions = totalSessions.load();
        stats.activeSessions = activeSessions.load();
        return stats;
    }

private:
    std::unique_ptr<TSyncMap<std::string, SessionData>> sessions_;

    void onSessionCreated(const std::string& sessionId) {
        // 会话创建回调
        std::cout << "Session created: " << sessionId << std::endl;
    }

    void markSessionExpired(const std::string& sessionId) {
        // 标记会话过期（在 SessionData 中设置标志）
        auto* session = sessions_->Find(sessionId);
        if (session) {
            session->markExpired();
        }
    }

    std::string generateSessionToken() {
        // 生成会话令牌
        return std::to_string(std::random_device{}());
    }
};
```

## 性能考虑

- **读优化**：读操作在多数情况下是无锁的，性能极高
- **写代价**：写操作会导致后续 O(n) 次读操作需要获取锁
- **内存管理**：使用引用计数和 hazard pointer 优化内存安全
- **缓存友好**：内存布局优化，提高缓存命中率

```cpp
// 性能优化示例
class OptimizedLookupService {
public:
    OptimizedLookupService(size_t initialCapacity = 1024) {
        // 预分配空间减少动态扩容
        lookupTable_ = std::make_unique<TSyncMap<uint64_t, LookupEntry>>();

        // 预插入常用条目
        prepopulateCommonEntries();
    }

    // 高频查找操作
    LookupEntry* fastLookup(uint64_t key) {
        // 大多数情况下无锁，性能极佳
        return lookupTable_->Find(key);
    }

    // 批量更新操作
    void batchUpdate(const std::vector<std::pair<uint64_t, LookupEntry>>& entries) {
        for (const auto& [key, entry] : entries) {
            lookupTable_->FindOrInsert(key, [&entry]() { return entry; });
        }

        // 批量更新后刷新，减少锁竞争
        lookupTable_->Flush();
    }

    // 缓存预热
    void warmupCache() {
        std::vector<std::pair<uint64_t, LookupEntry>> commonEntries = loadCommonEntries();
        batchUpdate(commonEntries);
    }

    // 性能监控
    void monitorPerformance() {
        auto start = std::chrono::high_resolution_clock::now();

        // 执行大量查找操作
        for (int i = 0; i < 1000000; ++i) {
            uint64_t key = generateTestKey(i);
            auto* entry = fastLookup(key);
            (void)entry;  // 避免编译器优化
        }

        auto end = std::chrono::high_resolution_clock::now();
        auto duration = std::chrono::duration_cast<std::chrono::milliseconds>(end - start);

        std::cout << "1M lookups took: " << duration.count() << "ms" << std::endl;
    }

private:
    std::unique_ptr<TSyncMap<uint64_t, LookupEntry>> lookupTable_;

    void prepopulateCommonEntries() {
        // 预填充常用的查找条目
        std::vector<std::pair<uint64_t, LookupEntry>> commonEntries = {
            {0x1001, LookupEntry("common1")},
            {0x1002, LookupEntry("common2")},
            {0x1003, LookupEntry("common3")},
            // ...
        };

        for (const auto& [key, entry] : commonEntries) {
            lookupTable_->FindOrInsert(key, [&entry]() { return entry; });
        }
    }

    std::vector<std::pair<uint64_t, LookupEntry>> loadCommonEntries() {
        // 从持久化存储加载常用条目
        return {};  // 实现细节
    }

    uint64_t generateTestKey(int index) {
        return static_cast<uint64_t>(index * 7919) % 10000;  // 伪随机
    }
};
```

## 最佳实践

1. **读多写少**：在读远多于写的场景中使用最佳
2. **批量写入**：将多次写操作合并，减少 Flush 调用
3. **预热缓存**：在系统启动时预填充常用数据
4. **合理哈希**：使用高效的哈希函数减少冲突
5. **监控性能**：定期监控读写性能，调整使用策略

```cpp
// 最佳实践示例
class BestPracticeSyncMapUsage {
public:
    BestPracticeSyncMapUsage() {
        initializeOptimized();
    }

    void demonstrateBestPractices() {
        // 1. 预热缓存
        warmupCache();

        // 2. 批量操作
        performBatchOperations();

        // 3. 性能监控
        monitorAndOptimize();
    }

private:
    std::unique_ptr<TSyncMap<std::string, ProcessedData>> dataCache_;

    void initializeOptimized() {
        // 使用优化的配置
        dataCache_ = std::make_unique<TSyncMap<
            std::string,
            ProcessedData,
            MurmurHash3,               // 高质量哈希
            std::equal_to<std::string>,
            NThreading::TAdaptiveLock   // 自适应锁
        >>();
    }

    void warmupCache() {
        // 预加载热点数据
        auto hotData = loadHotDataFromStorage();

        for (const auto& [key, data] : hotData) {
            dataCache_->FindOrInsert(key, [&data]() { return data; });
        }

        // 预加载完成后刷新
        dataCache_->Flush();
    }

    void performBatchOperations() {
        std::vector<std::pair<std::string, ProcessedData>> batchData = loadBatchData();

        // 批量插入
        for (const auto& [key, data] : batchData) {
            dataCache_->FindOrInsert(key, [&data]() { return data; });
        }

        // 一次性刷新
        dataCache_->Flush();
    }

    void monitorAndOptimize() {
        // 定期监控性能
        auto stats = collectPerformanceStats();

        if (stats.avgLookupTime > threshold) {
            // 性能下降时进行优化
            optimizeCache();
        }
    }

    void optimizeCache() {
        // 缓存优化策略
        std::cout << "Optimizing cache performance..." << std::endl;

        // 可能的优化措施：
        // 1. 重新组织数据
        // 2. 清理无效数据
        // 3. 调整缓存大小等
        dataCache_->Flush();
    }

    struct MurmurHash3 {
        size_t operator()(const std::string& key) const {
            // MurmurHash3 的简化实现
            const uint64_t seed = 0x9747b28c;
            uint64_t hash = seed;

            for (char c : key) {
                hash ^= static_cast<uint64_t>(c);
                hash *= 0x100000001b3;  // Golden ratio prime
            }

            return hash;
        }
    };
};
```

## 依赖项

- **yt/yt/core/misc/finally**：RAII 支持
- **yt/yt/core/misc/hazard_ptr**：Hazard pointer 内存管理
- **library/cpp/yt/threading/spin_lock**：自旋锁实现
- **library/cpp/yt/memory/ref_counted**：引用计数支持
- **util/generic/hash**：哈希表实现
- **util/generic/noncopyable**：不可复制类支持

## 注意事项

- **插入式设计**：不支持删除操作，只支持插入
- **写操作影响**：写操作会影响后续读操作的性能
- **内存增长**：由于不支持删除，内存会持续增长
- **迭代一致性**：只读迭代看到的是 Flush 时的快照
- **线程安全**：完全线程安全，但要注意性能影响

该库为 YTsaurus 提供了高性能的并发访问能力，特别适用于配置缓存、会话管理等读多写少的场景。