# Consistent Hashing 一致性哈希库

## 项目描述

Consistent Hashing 库是 YTsaurus 中的高性能一致性哈希算法实现。该库提供了一种将随机 64 位整数（实际上是字符串的哈希值）映射到 N 个桶/分片的方法，具有优秀的分布特性、一致性和计算效率。

与传统的圆环一致性哈希算法相比，该实现具有 O(1) 的内存和 CPU 时间复杂度，无需维护虚拟节点，在保持优秀一致性的同时提供极高的性能。

## 核心特性

### ⚡ 超高性能
- **O(1) 复杂度**: 恒定的计算时间和内存使用
- **无数据结构**: 无需维护哈希环或虚拟节点
- **位操作优化**: 基于位运算的快速算法实现
- **缓存友好**: 优化的内存访问模式

### 🎯 高一致性
- **最小重分布**: 节点数量变化时影响最小
- **均匀分布**: 所有分片概率相等
- **平滑过渡**: 分片数量变化时的平滑映射过渡

### 📊 精确数学特性
- **理论最优**: 达到数学上的最优一致性
- **边界情况处理**: 处理极端分布情况
- **可预测性**: 确定性的映射结果

### 🔧 灵活接口
- **多种输入格式**: 支持 64 位整数和双 64 位整数输入
- **不同规模**: 支持不同规模的分片数量
- **类型安全**: 强类型的接口设计

## 算法原理

### 一致性哈希要求

算法满足以下数学要求：

1. **均匀分布**: 对于任意的 x 和 n，ConsistentHashing(x, n) 返回 0 ≤ value < n，且每个值的概率相等
2. **最优一致性**: 当 n₁ < n₂ 时，P(ConsistentHashing(x, n₁) ≠ ConsistentHashing(x, n₂)) = (n₂ - n₁) / n₂

### 位块算法设计

算法将 64 位输入分为四个 16 位或 32 位块，基于数学构造实现一致性映射：

```
        (sizeof(TValue) * 8, y]  (y, 0]
a =             *             ablock
b =             *             cblock

        (sizeof(TValue) * 8, k]  (k, 0]
c =             *             cblock

d =             *
```

#### 关键参数
- **k**: 由 2^(k-1) < n ≤ 2^k 确定
- **z**: cblock 中 1 的数量
- **y**: cblock 中第一个 1 之后的位数

#### 映射规则
cblock 的位数决定使用 a- 和 b- 块的逻辑：

| cblock 位数 | 函数结果 |
|-------------|----------|
| 0           | 0        |
| 1           | 1        |
| 1?..?       | 1ablock (z 为偶数) 或 1bblock (z 为奇数)，如果可能 (< n) |

## 主要接口

### 1. 单 64 位哈希值版本
```cpp
// 将 64 位哈希值映射到 n 个分片
// 适用于 n < 65536 的场景
size_t ConsistentHashing(ui64 x, size_t n);
```

#### 参数说明
- `x`: 输入的 64 位哈希值
- `n`: 分片数量，必须大于 0

#### 返回值
- 返回 0 到 n-1 之间的分片索引

### 2. 双 64 位哈希值版本
```cpp
// 使用两个 64 位哈希值映射到 n 个分片
// 适用于 n < 4294967296 的场景
size_t ConsistentHashing(ui64 lo, ui64 hi, size_t n);
```

#### 参数说明
- `lo`: 低 64 位哈希值
- `hi`: 高 64 位哈希值
- `n`: 分片数量，必须大于 0

#### 返回值
- 返回 0 到 n-1 之间的分片索引

## 使用示例

### 基本使用
```cpp
#include <library/cpp/consistent_hashing/consistent_hashing.h>

// 基本分片映射
ui64 hashValue = 12345678901234567890ULL;
size_t numShards = 100;

size_t shardId = ConsistentHashing(hashValue, numShards);
// shardId 的范围是 [0, 99]

// 验证分布均匀性
TVector<size_t> distribution(numShards, 0);
for (size_t i = 0; i < 1000000; ++i) {
    ui64 hash = GenerateHash(i);
    size_t shard = ConsistentHashing(hash, numShards);
    distribution[shard]++;
}

// 每个分片应该有大约 10000 个元素
```

### 字符串分片
```cpp
// 字符串哈希分片
TString GetShardForString(const TString& str, size_t numShards) {
    ui64 hash = ComputeHash64(str);
    size_t shardId = ConsistentHashing(hash, numShards);
    return ToString(shardId);
}

// URL 分片示例
TString url = "https://example.com/path/to/resource";
size_t numServers = 50;
size_t serverId = ConsistentHashing(ComputeHash64(url), numServers);
```

### 数据库分片
```cpp
// 数据库表分片策略
class DatabaseSharding {
private:
    size_t numShards_;
    TVector<TString> shardConnections_;

public:
    DatabaseSharding(size_t numShards) : numShards_(numShards) {
        shardConnections_.resize(numShards);
        for (size_t i = 0; i < numShards; ++i) {
            shardConnections_[i] = "shard_" + ToString(i) + ".db";
        }
    }

    size_t GetShardId(ui64 userId) const {
        return ConsistentHashing(userId, numShards_);
    }

    TString GetShardConnection(ui64 userId) const {
        size_t shardId = GetShardId(userId);
        return shardConnections_[shardId];
    }

    template <typename KeyType>
    size_t GetShardId(const KeyType& key) const {
        ui64 hash = std::hash<KeyType>{}(key);
        return ConsistentHashing(hash, numShards_);
    }
};
```

### 缓存分片
```cpp
// 分布式缓存分片
class DistributedCache {
private:
    size_t numNodes_;
    TVector<std::shared_ptr<ICacheNode>> cacheNodes_;

public:
    DistributedCache(const TVector<std::shared_ptr<ICacheNode>>& nodes)
        : numNodes_(nodes.size()), cacheNodes_(nodes) {}

    template <typename KeyType>
    ICacheNode* GetNodeForKey(const KeyType& key) {
        ui64 hash = std::hash<KeyType>{}(key);
        size_t nodeId = ConsistentHashing(hash, numNodes_);
        return cacheNodes_[nodeId].get();
    }

    template <typename KeyType, typename ValueType>
    void Put(const KeyType& key, const ValueType& value) {
        ICacheNode* node = GetNodeForKey(key);
        node->Put(key, value);
    }

    template <typename KeyType>
    std::optional<ValueType> Get(const KeyType& key) {
        ICacheNode* node = GetNodeForKey(key);
        return node->Get(key);
    }
};
```

### 动态分片调整
```cpp
// 动态调整分片数量
class AdaptiveSharding {
private:
    size_t currentShards_;
    TVector<size_t> shardLoads_;

    size_t GetShardWithNewConfig(ui64 hash, size_t newNumShards) const {
        return ConsistentHashing(hash, newNumShards);
    }

public:
    AdaptiveSharding(size_t initialShards) : currentShards_(initialShards) {
        shardLoads_.resize(initialShards, 0);
    }

    size_t GetCurrentShardId(ui64 key) const {
        return ConsistentHashing(key, currentShards_);
    }

    // 计算分片调整时的数据迁移量
    double CalculateMigrationCost(size_t newNumShards) const {
        size_t totalTestKeys = 1000000;
        size_t migrations = 0;

        for (size_t i = 0; i < totalTestKeys; ++i) {
            ui64 hash = GenerateTestHash(i);
            size_t oldShard = GetCurrentShardId(hash);
            size_t newShard = GetShardWithNewConfig(hash, newNumShards);

            if (oldShard != newShard) {
                migrations++;
            }
        }

        return double(migrations) / totalTestKeys;
    }

    void AdjustShardCount(size_t newNumShards) {
        double migrationCost = CalculateMigrationCost(newNumShards);
        Cout << "调整分片从 " << currentShards_ << " 到 " << newNumShards
             << "，预计迁移 " << migrationCost * 100 << "% 的数据" << Endl;

        currentShards_ = newNumShards;
        shardLoads_.resize(newNumShards, 0);
    }
};
```

### 大规模分片
```cpp
// 大规模分片场景
class LargeScaleSharding {
private:
    static constexpr size_t MAX_SHARDS = 4294967296UL; // 2^32

public:
    // 使用双哈希版本支持大规模分片
    size_t GetShardIdForLargeKey(const TString& key, size_t numShards) {
        Y_ASSERT(numShards <= MAX_SHARDS);

        // 计算两个独立的 64 位哈希值
        ui64 hash1 = MurmurHash64(key);
        ui64 hash2 = CityHash64(key);

        return ConsistentHashing(hash1, hash2, numShards);
    }

    // 用于地理或其他需要大量分片的场景
    size_t GetGeoShard(double latitude, double longitude, size_t numShards) {
        // 将地理坐标转换为哈希值
        ui64 latBits = *reinterpret_cast<const ui64*>(&latitude);
        ui64 lonBits = *reinterpret_cast<const ui64*>(&longitude);

        return ConsistentHashing(latBits, lonBits, numShards);
    }
};
```

## 性能特性

### 计算复杂度
- **时间复杂度**: O(1) - 恒定时间计算
- **空间复杂度**: O(1) - 无需额外存储
- **缓存效率**: 优秀的缓存命中率
- **内存访问**: 最小化内存访问次数

### 分布质量
- **均匀性**: 理论上的完美均匀分布
- **一致性**: 最小化的重分布成本
- **平衡性**: 各分片负载高度均衡

### 扩展性对比

| 分片数量 | 传统哈希 | 圆环一致性哈希 | 本算法 |
|----------|----------|----------------|--------|
| 100      | O(n)     | O(log n)       | O(1)   |
| 1000     | O(n)     | O(log n)       | O(1)   |
| 10000    | O(n)     | O(log n)       | O(1)   |
| 100000   | O(n)     | O(log n)       | O(1)   |

## 应用场景

### 1. 数据库分片
```cpp
// 用户数据分片存储
size_t GetShardForUser(ui64 userId, size_t numShards) {
    return ConsistentHashing(userId, numShards);
}

// 分布式数据库查询路由
class DistributedDatabase {
    TVector<DatabaseShard> shards_;

public:
    DatabaseShard& GetShard(ui64 userId) {
        size_t shardId = ConsistentHashing(userId, shards_.size());
        return shards_[shardId];
    }
};
```

### 2. 缓存系统
```cpp
// 一致性哈希缓存
class ConsistentCache {
    TVector<CacheNode> nodes_;

public:
    CacheNode& GetNode(const TString& key) {
        ui64 hash = std::hash<TString>{}(key);
        size_t nodeId = ConsistentHashing(hash, nodes_.size());
        return nodes_[nodeId];
    }
};
```

### 3. 负载均衡
```cpp
// 服务器负载均衡
class LoadBalancer {
    TVector<ServerInfo> servers_;

public:
    ServerInfo& SelectServer(const RequestInfo& request) {
        ui64 hash = ComputeRequestHash(request);
        size_t serverId = ConsistentHashing(hash, servers_.size());
        return servers_[serverId];
    }
};
```

### 4. 数据分区
```cpp
// 时间序列数据分区
size_t GetPartitionForTimestamp(ui64 timestamp, size_t numPartitions) {
    return ConsistentHashing(timestamp, numPartitions);
}

// 日志文件分片
size_t GetLogFileForLog(const LogEntry& entry, size_t numFiles) {
    ui64 hash = CombineHashes(entry.timestamp, entry.serviceId, entry.level);
    return ConsistentHashing(hash, numFiles);
}
```

## 测试和验证

### 分布均匀性测试
```cpp
void TestDistributionUniformity() {
    const size_t numShards = 1000;
    const size_t numTests = 1000000;
    TVector<size_t> counts(numShards, 0);

    // 测试分布均匀性
    for (size_t i = 0; i < numTests; ++i) {
        ui64 hash = GenerateRandomHash();
        size_t shard = ConsistentHashing(hash, numShards);
        counts[shard]++;
    }

    // 计算统计特性
    double expected = double(numTests) / numShards;
    double variance = 0;
    double maxDeviation = 0;

    for (size_t count : counts) {
        double deviation = abs(count - expected);
        maxDeviation = max(maxDeviation, deviation);
        variance += pow(deviation, 2);
    }
    variance /= numShards;

    Cout << "期望值: " << expected << Endl;
    Cout << "最大偏差: " << maxDeviation << Endl;
    Cout << "方差: " << variance << Endl;
    Cout << "标准差: " << sqrt(variance) << Endl;
}
```

### 一致性测试
```cpp
void TestConsistency() {
    const size_t initialShards = 100;
    const size_t finalShards = 150;
    const size_t numTests = 100000;

    size_t changes = 0;

    for (size_t i = 0; i < numTests; ++i) {
        ui64 hash = GenerateRandomHash();
        size_t oldShard = ConsistentHashing(hash, initialShards);
        size_t newShard = ConsistentHashing(hash, finalShards);

        if (oldShard != newShard) {
            changes++;
        }
    }

    double expectedChangeRate = double(finalShards - initialShards) / finalShards;
    double actualChangeRate = double(changes) / numTests;

    Cout << "预期变化率: " << expectedChangeRate * 100 << "%" << Endl;
    Cout << "实际变化率: " << actualChangeRate * 100 << "%" << Endl;
    Cout << "偏差: " << abs(expectedChangeRate - actualChangeRate) * 100 << "%" << Endl;
}
```

### 性能基准测试
```cpp
void BenchmarkPerformance() {
    const size_t numTests = 10000000;
    TVector<ui64> hashes;
    hashes.reserve(numTests);

    // 准备测试数据
    for (size_t i = 0; i < numTests; ++i) {
        hashes.push_back(GenerateRandomHash());
    }

    // 基准测试
    auto start = std::chrono::high_resolution_clock::now();

    volatile size_t sum = 0;  // 防止编译器优化
    for (ui64 hash : hashes) {
        sum += ConsistentHashing(hash, 1000);
    }

    auto end = std::chrono::high_resolution_clock::now();
    auto duration = std::chrono::duration_cast<std::chrono::microseconds>(end - start);

    double opsPerSecond = double(numTests) / duration.count() * 1000000;

    Cout << "处理 " << numTests << " 次哈希计算耗时: " << duration.count() << " μs" << Endl;
    Cout << "性能: " << opsPerSecond << " ops/second" << Endl;
}
```

## 最佳实践

### 1. 哈希函数选择
```cpp
// 推荐的哈希函数
ui64 GetGoodHash(const TString& str) {
    // 使用高质量的 64 位哈希函数
    return MurmurHash64(str.data(), str.size());
}

ui64 GetGoodHash(ui64 value) {
    // 对 64 位整数进行哈希混合
    return wyhash64(value);
}
```

### 2. 错误处理
```cpp
// 安全的分片函数
size_t SafeGetShardId(ui64 hash, size_t numShards) {
    if (numShards == 0) {
        throw std::invalid_argument("Number of shards must be positive");
    }

    if (numShards > 4294967296UL) {
        throw std::invalid_argument("Number of shards too large for algorithm");
    }

    return ConsistentHashing(hash, numShards);
}
```

### 3. 性能优化
```cpp
// 批量处理优化
class BatchSharding {
public:
    template <typename Iterator>
    void GetShardsBatch(Iterator begin, Iterator end, size_t numShards,
                       TVector<size_t>& results) {
        results.clear();
        results.reserve(std::distance(begin, end));

        for (auto it = begin; it != end; ++it) {
            ui64 hash = ComputeHash(*it);
            results.push_back(ConsistentHashing(hash, numShards));
        }
    }
};
```

## 限制和注意事项

### 使用限制
- **最大分片数**: 单哈希版本限制在 65536 个分片，双哈希版本限制在 4294967296 个分片
- **输入质量**: 依赖输入哈希的质量，建议使用高质量哈希函数
- **分片数量**: 分片数量必须大于 0

### 性能考虑
- **哈希计算**: 总体性能取决于哈希函数的效率
- **内存局部性**: 在大量分片场景下可能影响缓存性能
- **并行处理**: 算法本身是线程安全的，可以在多线程环境中并行使用

## 总结

Consistent Hashing 库提供了一个理论最优且性能卓越的一致性哈希解决方案。通过巧妙的数学构造和位操作优化，该算法在 O(1) 复杂度下实现了完美的一致性特性，适用于各种大规模分布式系统的分片和负载均衡场景。

其简洁的接口、优秀的性能和数学上的严格保证，使其成为分布式系统设计的理想选择。