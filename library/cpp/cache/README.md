# cache

高性能缓存库，实现了 LRU (Least Recently Used) 缓存算法和线程安全的缓存实现，用于优化内存访问和减少重复计算。

## 功能描述

cache 库提供了高效的内存缓存实现，包括 LRU 缓存、线程安全缓存等多种缓存策略。通过缓存热点数据，可以显著提升应用程序的性能，减少对慢速存储或网络资源的访问。

## 核心特性

- **LRU 缓存**：实现了高效的最近最少使用缓存淘汰算法
- **线程安全**：提供了线程安全的缓存实现
- **可配置大小**：支持基于条目数量和总大小的限制
- **灵活的键值类型**：支持任意类型的键和值
- **自定义大小计算**：允许自定义值的"大小"计算方式
- **高效实现**：使用双向链表和哈希表实现 O(1) 操作

## 主要组件

### TLRUList
LRU 缓存的核心实现：

```cpp
template <typename TKey, typename TValue, class TSizeProvider = TUniformSizeProvider<TValue>>
class TLRUList {
public:
    // 构造函数
    TLRUList(size_t maxSize, const TSizeProvider& sizeProvider = TSizeProvider());

    // 查找并移动到最前面
    TValue* Find(const TKey& key);

    // 插入或更新
    void Insert(const TKey& key, const TValue& value);
    void Insert(const TKey& key, TValue&& value);

    // 删除条目
    bool Erase(const TKey& key);

    // 获取统计信息
    size_t GetSize() const { return ItemsAmount; }
    size_t GetTotalSize() const { return TotalSize; }
};
```

### TThreadSafeCache
线程安全的缓存包装器：

```cpp
template <typename TKey, typename TValue>
class TThreadSafeCache {
private:
    TLRUList<TKey, TValue> Cache;
    TAdaptiveLock Lock;

public:
    // 线程安全的操作
    template <typename TFactory>
    TValue Get(const TKey& key, TFactory factory);

    bool Find(const TKey& key, TValue& value);
    void Insert(const TKey& key, const TValue& value);
    bool Erase(const TKey& key);
};
```

## 使用示例

### 基本 LRU 缓存
```cpp
#include <library/cpp/cache/cache.h>

// 创建缓存，最多 1000 个条目
TLRUList<TString, TVector<int>> cache(1000);

// 插入数据
TVector<int> data = {1, 2, 3, 4, 5};
cache.Insert("key1", data);

// 查找数据
if (auto* ptr = cache.Find("key1")) {
    // 使用数据，自动移动到最前面
    for (int val : *ptr) {
        Cout << val << Endl;
    }
}
```

### 自定义大小计算
```cpp
// 自定义大小提供者，计算字符串长度
struct TStringSizeProvider {
    size_t operator()(const TString& str) const {
        return str.size();
    }
};

// 创建基于总大小的缓存
TLRUList<int, TString, TStringSizeProvider> cache(1024 * 1024); // 1MB

// 插入不同大小的字符串
cache.Insert(1, "short");
cache.Insert(2, "this is a very long string...");
```

### 线程安全缓存
```cpp
#include <library/cpp/cache/thread_safe_cache.h>

// 创建线程安全的缓存
TThreadSafeCache<TString, std::shared_ptr<ExpensiveObject>> cache(1000);

// 多线程环境下安全使用
void ProcessRequest(const TString& key) {
    auto obj = cache.Get(key, []() {
        // 如果缓存中没有，创建新对象
        return std::make_shared<ExpensiveObject>();
    });

    // 使用对象
    obj->Process();
}
```

### 缓存模式实现
```cpp
template <typename TKey, typename TValue>
class CacheProxy {
private:
    TThreadSafeCache<TKey, TValue> cache_;

public:
    // 获取缓存项或计算新值
    template <typename TFunc>
    TValue GetOrCompute(const TKey& key, TFunc computeFunc) {
        TValue value;
        if (!cache_.Find(key, value)) {
            value = computeFunc(key);
            cache_.Insert(key, value);
        }
        return value;
    }

    // 预热缓存
    template <typename TIterator>
    void Warmup(TIterator begin, TIterator end, std::function<TValue(const TKey&)> computeFunc) {
        for (auto it = begin; it != end; ++it) {
            cache_.Insert(*it, computeFunc(*it));
        }
    }
};
```

## 性能特性

### 时间复杂度
- **查找**：O(1)
- **插入**：O(1)
- **删除**：O(1)
- **访问更新**：O(1)

### 空间复杂度
- **存储**：O(n) 其中 n 是缓存条目数
- **开销**：每个条目约 2-3 个指针的额外开销

### 内存使用
- **LRU 链表**：双向链表维护访问顺序
- **哈希表**：O(1) 查找的关键数据结构
- **线程安全锁**：自适应锁，减少锁竞争

## 高级功能

### 缓存统计
```cpp
template <typename TKey, typename TValue>
class InstrumentedCache {
private:
    TLRUList<TKey, TValue> cache_;
    std::atomic<size_t> hits_{0};
    std::atomic<size_t> misses_{0};

public:
    TValue* Find(const TKey& key) {
        TValue* result = cache_.Find(key);
        if (result) {
            ++hits_;
        } else {
            ++misses_;
        }
        return result;
    }

    double GetHitRate() const {
        size_t total = hits_ + misses_;
        return total > 0 ? double(hits_) / total : 0.0;
    }
};
```

### 分层缓存
```cpp
template <typename TKey, typename TValue>
class TwoLevelCache {
private:
    TLRUList<TKey, TValue> l1Cache_;  // 热数据
    TLRUList<TKey, TValue> l2Cache_;  // 温数据

public:
    TValue* Find(const TKey& key) {
        // 先查 L1 缓存
        if (auto* value = l1Cache_.Find(key)) {
            return value;
        }

        // 再查 L2 缓存
        if (auto* value = l2Cache_.Find(key)) {
            // 提升到 L1 缓存
            l1Cache_.Insert(key, std::move(*value));
            l2Cache_.Erase(key);
            return value;
        }

        return nullptr;
    }
};
```

### 带过期时间的缓存
```cpp
template <typename TKey, typename TValue>
class TTLCache {
private:
    struct CacheItem {
        TValue Value;
        TInstant ExpireTime;
    };

    TLRUList<TKey, CacheItem> cache_;

public:
    void Insert(const TKey& key, const TValue& value, TDuration ttl) {
        CacheItem item{value, TInstant::Now() + ttl};
        cache_.Insert(key, std::move(item));
    }

    TValue* Find(const TKey& key) {
        if (auto* item = cache_.Find(key)) {
            if (item->ExpireTime > TInstant::Now()) {
                return &item->Value;
            }
            cache_.Erase(key);  // 过期项
        }
        return nullptr;
    }
};
```

## 应用场景

### Web 应用
- **页面缓存**：缓存渲染的页面
- **数据库查询结果**：缓存查询结果
- **API 响应**：缓存外部 API 调用结果

### 计算密集型应用
- **计算结果缓存**：缓存复杂计算的结果
- **中间结果**：缓存算法的中间结果
- **查找表**：缓存预计算的查找表

### 系统服务
- **配置缓存**：缓存系统配置
- **元数据缓存**：缓存文件系统元数据
- **连接池**：缓存数据库连接

## 最佳实践

### 缓存大小设置
```cpp
// 根据可用内存设置缓存大小
size_t availableMemory = GetAvailableMemory();
size_t cacheSize = availableMemory * 0.1;  // 使用 10% 的内存

// 根据热点数据量设置
size_t hotDataSize = EstimateHotDataSize();
TLRUList<Key, Value> cache(hotDataSize);
```

### 缓存键设计
```cpp
// 使用组合键避免冲突
struct CacheKey {
    int UserId;
    int PageId;

    bool operator==(const CacheKey& other) const {
        return UserId == other.UserId && PageId == other.PageId;
    }
};

// 为 CacheKey 提供哈希函数
template <>
struct THash<CacheKey> {
    size_t operator()(const CacheKey& key) const {
        return CombineHashes(key.UserId, key.PageId);
    }
};
```

### 缓存失效策略
```cpp
class InvalidatableCache {
private:
    TThreadSafeCache<TKey, TValue> cache_;
    TAtomic version_{0};

public:
    void InvalidateAll() {
        AtomicIncrement(version_);
    }

    TValue* Find(const TKey& key, size_t& version) {
        if (version != AtomicGet(version_)) {
            cache_.Erase(key);  // 版本不匹配，清除缓存
            version = AtomicGet(version_);
        }
        return cache_.Find(key);
    }
};
```

## 调试和性能分析

### 缓存命中率监控
```cpp
class CacheMetrics {
private:
    std::atomic<size_t> hits_{0};
    std::atomic<size_t> misses_{0};
    std::atomic<size_t> evictions_{0};

public:
    void RecordHit() { ++hits_; }
    void RecordMiss() { ++misses_; }
    void RecordEviction() { ++evictions_; }

    void PrintStats() const {
        Cout << "Cache Stats:" << Endl;
        Cout << "  Hits: " << hits_ << Endl;
        Cout << "  Misses: " << misses_ << Endl;
        Cout << "  Hit Rate: " << GetHitRate() * 100 << "%" << Endl;
        Cout << "  Evictions: " << evictions_ << Endl;
    }
};
```

### 性能测试
```bash
# 运行缓存性能测试
./cache_ut --benchmark

# 测试不同大小的缓存性能
./cache_ut --cache-size=1000 --iterations=1000000
```

## 注意事项

1. **内存管理**：注意缓存值的内存生命周期
2. **线程安全**：多线程环境使用 TThreadSafeCache
3. **缓存一致性**：考虑缓存失效和更新策略
4. **内存泄漏**：避免循环引用导致内存泄漏
5. **性能测试**：在实际场景下测试缓存效果