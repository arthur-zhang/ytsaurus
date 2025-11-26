# Min Hash Digest (最小哈希摘要)

## 项目概述

Min Hash Digest 模块实现了基于最小哈希算法的数据指纹技术。该模块用于高效地计算和比较数据集合的相似性，特别适用于大规模数据的去重、相似性检测和增量同步等场景。

## 核心功能

### 最小哈希算法
- **数据指纹生成**: 为数据集合生成紧凑的哈希指纹
- **相似性估计**: 通过哈希指纹快速估计集合间的相似度
- **增量更新**: 支持数据集合的增量更新和指纹维护
- **内存高效**: 使用固定大小的哈希集合表示任意大小的数据

### 写入和删除跟踪
- **写入哈希跟踪**: 跟踪数据写入操作的最小哈希值
- **删除墓碑跟踪**: 跟踪数据删除操作的墓碑标记
- **双重哈希**: 分别维护写入和删除操作的哈希集合
- **冲突检测**: 检测写入和删除操作之间的潜在冲突

## 主要接口

### 核心类：TMinHashDigest

```cpp
class TMinHashDigest
    : public TRefCounted
{
public:
    TMinHashDigest() = default;

    bool IsInitialized() const;
    void Initialize(TSharedRef data);

    static TSharedRef Build(
        const std::map<TFingerprint, ui64>& writeMinHashes,
        const std::map<TFingerprint, ui64>& deleteTombstoneMinHashes);
};
```

#### 主要方法

```cpp
// 检查是否已初始化
bool IsInitialized() const;

// 使用数据初始化摘要
void Initialize(TSharedRef data);

// 构建摘要数据（静态方法）
static TSharedRef Build(
    const std::map<TFingerprint, ui64>& writeMinHashes,              // 写入操作最小哈希
    const std::map<TFingerprint, ui64>& deleteTombstoneMinHashes);  // 删除墓碑最小哈希
```

#### 类型定义

```cpp
// 哈希指纹类型
using TFingerprint = FarmHash;  // 基于 FarmHash 的指纹

// 哈希值映射
using THashMap = std::map<TFingerprint, ui64>;
```

## 使用方法

### 基本使用示例

```cpp
#include <yt/yt/library/min_hash_digest/public.h>
#include <yt/yt/library/min_hash_digest/min_hash_digest.h>

using namespace NYT;

// 创建写入哈希集合
std::map<TFingerprint, ui64> writeHashes;
writeHashes[Fingerprint("item1")] = 1;
writeHashes[Fingerprint("item2")] = 2;
writeHashes[Fingerprint("item3")] = 3;

// 创建删除墓碑哈希集合
std::map<TFingerprint, ui64> deleteHashes;
deleteHashes[Fingerprint("old_item1")] = 1;
deleteHashes[Fingerprint("old_item2")] = 2;

// 构建摘要数据
auto digestData = TMinHashDigest::Build(writeHashes, deleteHashes);

// 创建摘要对象
auto digest = New<TMinHashDigest>();
digest->Initialize(digestData);

if (digest->IsInitialized()) {
    Cout << "MinHash digest initialized successfully" << Endl;
}
```

### 数据相似性检测示例

```cpp
class DataSimilarityDetector {
public:
    // 计算数据集合的指纹
    static std::map<TFingerprint, ui64> ComputeFingerprint(const std::vector<TString>& data) {
        std::map<TFingerprint, ui64> fingerprints;

        for (const auto& item : data) {
            auto fingerprint = ComputeItemFingerprint(item);
            auto hashValue = ComputeHashValue(item);
            fingerprints[fingerprint] = hashValue;
        }

        return fingerprints;
    }

    // 计算两个数据集合的相似度
    static double ComputeSimilarity(const std::vector<TString>& data1,
                                   const std::vector<TString>& data2) {
        auto fingerprints1 = ComputeFingerprint(data1);
        auto fingerprints2 = ComputeFingerprint(data2);

        return ComputeJaccardSimilarity(fingerprints1, fingerprints2);
    }

    // 创建数据摘要
    static TMinHashDigestPtr CreateDigest(const std::vector<TString>& data) {
        auto fingerprints = ComputeFingerprint(data);
        auto digestData = TMinHashDigest::Build(fingerprints, {});

        auto digest = New<TMinHashDigest>();
        digest->Initialize(digestData);

        return digest;
    }

private:
    static TFingerprint ComputeItemFingerprint(const TString& item) {
        return FarmHash(item.data(), item.size());
    }

    static ui64 ComputeHashValue(const TString& item) {
        return std::hash<TString>{}(item);
    }

    static double ComputeJaccardSimilarity(const std::map<TFingerprint, ui64>& set1,
                                          const std::map<TFingerprint, ui64>& set2) {
        std::set<TFingerprint> intersection;
        std::set<TFingerprint> unionSet;

        // 计算交集
        for (const auto& [fp, _] : set1) {
            if (set2.find(fp) != set2.end()) {
                intersection.insert(fp);
            }
        }

        // 计算并集
        for (const auto& [fp, _] : set1) {
            unionSet.insert(fp);
        }
        for (const auto& [fp, _] : set2) {
            unionSet.insert(fp);
        }

        return unionSet.empty() ? 0.0 :
               static_cast<double>(intersection.size()) / unionSet.size();
    }
};
```

### 增量数据同步示例

```cpp
class IncrementalDataSync {
public:
    IncrementalDataSync() {
        currentDigest_ = New<TMinHashDigest>();
    }

    // 初始化数据集合
    void Initialize(const std::vector<TString>& initialData) {
        auto fingerprints = ComputeFingerprints(initialData);
        auto digestData = TMinHashDigest::Build(fingerprints, {});
        currentDigest_->Initialize(digestData);
        currentData_ = initialData;
    }

    // 添加新数据
    void AddData(const std::vector<TString>& newData) {
        auto newFingerprints = ComputeFingerprints(newData);
        auto updatedFingerprints = MergeFingerprints(
            GetCurrentFingerprints(), newFingerprints);

        auto digestData = TMinHashDigest::Build(updatedFingerprints, {});
        currentDigest_->Initialize(digestData);

        currentData_.insert(currentData_.end(), newData.begin(), newData.end());
    }

    // 删除数据
    void RemoveData(const std::vector<TString>& dataToRemove) {
        std::map<TFingerprint, ui64> deleteTombstones;
        for (const auto& item : dataToRemove) {
            auto fp = ComputeFingerprint(item);
            deleteTombstones[fp] = ComputeHashValue(item);
        }

        auto currentFingerprints = GetCurrentFingerprints();

        // 从当前指纹中移除被删除的数据
        for (const auto& item : dataToRemove) {
            auto fp = ComputeFingerprint(item);
            currentFingerprints.erase(fp);
        }

        auto digestData = TMinHashDigest::Build(currentFingerprints, deleteTombstones);
        currentDigest_->Initialize(digestData);

        // 从当前数据中移除
        auto it = std::remove_if(currentData_.begin(), currentData_.end(),
            [&dataToRemove](const TString& item) {
                return std::find(dataToRemove.begin(), dataToRemove.end(), item) != dataToRemove.end();
            });
        currentData_.erase(it, currentData_.end());
    }

    // 检测变更
    bool HasChanges(const TMinHashDigestPtr& otherDigest) {
        // 简化的变更检测逻辑
        return CompareDigests(currentDigest_, otherDigest);
    }

private:
    std::map<TFingerprint, ui64> ComputeFingerprints(const std::vector<TString>& data) {
        std::map<TFingerprint, ui64> fingerprints;
        for (const auto& item : data) {
            auto fp = ComputeFingerprint(item);
            fingerprints[fp] = ComputeHashValue(item);
        }
        return fingerprints;
    }

    std::map<TFingerprint, ui64> GetCurrentFingerprints() {
        return ComputeFingerprints(currentData_);
    }

    std::map<TFingerprint, ui64> MergeFingerprints(
        const std::map<TFingerprint, ui64>& existing,
        const std::map<TFingerprint, ui64>& newFingerprints) {
        std::map<TFingerprint, ui64> merged = existing;
        merged.insert(newFingerprints.begin(), newFingerprints.end());
        return merged;
    }

    TFingerprint ComputeFingerprint(const TString& item) {
        return FarmHash(item.data(), item.size());
    }

    ui64 ComputeHashValue(const TString& item) {
        return std::hash<TString>{}(item);
    }

    bool CompareDigests(const TMinHashDigestPtr& digest1, const TMinHashDigestPtr& digest2) {
        // 简化的比较逻辑
        return digest1->IsInitialized() && digest2->IsInitialized();
    }

    TMinHashDigestPtr currentDigest_;
    std::vector<TString> currentData_;
};
```

### 大规模数据去重示例

```cpp
class LargeScaleDeduplicator {
public:
    // 处理大规模数据分块
    void ProcessDataChunk(const std::vector<TString>& chunk, int chunkId) {
        auto chunkFingerprints = ComputeChunkFingerprints(chunk);

        // 存储分块指纹
        chunkFingerprints_[chunkId] = chunkFingerprints;

        // 创建分块摘要
        auto digestData = TMinHashDigest::Build(chunkFingerprints, {});
        chunkDigests_[chunkId] = digestData;
    }

    // 检测重复数据
    std::vector<int> FindDuplicateChunks(int targetChunkId, double similarityThreshold = 0.8) {
        std::vector<int> duplicateChunks;

        if (chunkDigests_.find(targetChunkId) == chunkDigests_.end()) {
            return duplicateChunks;
        }

        auto targetDigest = New<TMinHashDigest>();
        targetDigest->Initialize(chunkDigests_[targetChunkId]);
        auto targetFingerprints = chunkFingerprints_[targetChunkId];

        for (const auto& [chunkId, digestData] : chunkDigests_) {
            if (chunkId == targetChunkId) continue;

            auto compareDigest = New<TMinHashDigest>();
            compareDigest->Initialize(digestData);
            auto compareFingerprints = chunkFingerprints_[chunkId];

            double similarity = ComputeChunkSimilarity(
                targetFingerprints, compareFingerprints);

            if (similarity >= similarityThreshold) {
                duplicateChunks.push_back(chunkId);
            }
        }

        return duplicateChunks;
    }

    // 合并相似的分块
    std::vector<TString> MergeSimilarChunks(const std::vector<int>& chunkIds) {
        std::set<TString> uniqueItems;

        for (int chunkId : chunkIds) {
            if (chunkData_.find(chunkId) != chunkData_.end()) {
                for (const auto& item : chunkData_[chunkId]) {
                    uniqueItems.insert(item);
                }
            }
        }

        return std::vector<TString>(uniqueItems.begin(), uniqueItems.end());
    }

private:
    std::map<TFingerprint, ui64> ComputeChunkFingerprints(const std::vector<TString>& chunk) {
        std::map<TFingerprint, ui64> fingerprints;
        for (const auto& item : chunk) {
            auto fp = FarmHash(item.data(), item.size());
            auto hashValue = std::hash<TString>{}(item);
            fingerprints[fp] = hashValue;
        }
        return fingerprints;
    }

    double ComputeChunkSimilarity(const std::map<TFingerprint, ui64>& chunk1,
                                 const std::map<TFingerprint, ui64>& chunk2) {
        std::set<TFingerprint> intersection;
        std::set<TFingerprint> unionSet;

        for (const auto& [fp, _] : chunk1) {
            if (chunk2.find(fp) != chunk2.end()) {
                intersection.insert(fp);
            }
            unionSet.insert(fp);
        }

        for (const auto& [fp, _] : chunk2) {
            unionSet.insert(fp);
        }

        return unionSet.empty() ? 0.0 :
               static_cast<double>(intersection.size()) / unionSet.size();
    }

    std::map<int, std::map<TFingerprint, ui64>> chunkFingerprints_;
    std::map<int, TSharedRef> chunkDigests_;
    std::map<int, std::vector<TString>> chunkData_;
};
```

## 配置说明

### 算法参数

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| FormatVersion | i32 | 1 | 数据格式版本号 |

### 性能调优参数

```cpp
// 推荐的哈希集合大小
constexpr size_t RECOMMENDED_HASH_SIZE = 1024;

// 相似度阈值
constexpr double DEFAULT_SIMILARITY_THRESHOLD = 0.7;

// 内存使用限制（字节）
constexpr size_t MAX_MEMORY_USAGE = 64 * 1024 * 1024;  // 64MB
```

## 性能考虑

### 时间复杂度
- **指纹计算**: O(n)，其中 n 为数据项数量
- **相似度计算**: O(min(|S1|, |S2|))，其中 S1, S2 为两个数据集合
- **摘要构建**: O(n)，线性时间复杂度

### 空间复杂度
- **内存使用**: O(k)，其中 k 为唯一指纹数量
- **存储空间**: 固定大小，不随原数据大小线性增长
- **网络传输**: 紧凑的二进制格式，传输效率高

### 优化策略
1. **分批处理**: 将大数据集分批处理，避免内存溢出
2. **并行计算**: 并行计算不同数据块的指纹
3. **增量更新**: 只重新计算变更部分，避免全量重计算
4. **缓存优化**: 缓存计算结果，避免重复计算

## 最佳实践

### 1. 数据预处理
```cpp
class DataPreprocessor {
public:
    static std::vector<TString> PreprocessData(const std::vector<TString>& rawData) {
        std::vector<TString> processedData;

        for (const auto& item : rawData) {
            auto processed = ProcessItem(item);
            if (!processed.empty()) {
                processedData.push_back(processed);
            }
        }

        // 去重
        std::sort(processedData.begin(), processedData.end());
        processedData.erase(std::unique(processedData.begin(), processedData.end()),
                           processedData.end());

        return processedData;
    }

private:
    static TString ProcessItem(const TString& item) {
        // 标准化处理：去空格、转小写、规范化格式
        TString trimmed = item;
        trimmed.Trim();

        // 可以添加更多的标准化逻辑
        return to_lower(trimmed);
    }
};
```

### 2. 分层摘要
```cpp
class HierarchicalDigest {
public:
    // 构建分层摘要
    void BuildHierarchicalDigest(const std::vector<TString>& data) {
        // 第一层：原始数据摘要
        itemLevelDigest_ = CreateDigest(data);

        // 第二层：分块摘要
        auto chunks = SplitIntoChunks(data, 1000);
        for (const auto& chunk : chunks) {
            auto chunkDigest = CreateDigest(chunk);
            chunkDigests_.push_back(chunkDigest);
        }

        // 第三层：整体摘要
        auto allFingerprints = ComputeAllFingerprints(data);
        topLevelDigest_ = TMinHashDigest::Build(allFingerprints, {});
    }

    // 快速相似性检查
    bool IsLikelySimilar(const HierarchicalDigest& other) {
        // 先比较顶层摘要
        if (!CompareTopLevelDigests(topLevelDigest_, other.topLevelDigest_)) {
            return false;
        }

        // 比较分块摘要
        return CompareChunkDigests(chunkDigests_, other.chunkDigests_);
    }

private:
    TSharedRef itemLevelDigest_;
    std::vector<TSharedRef> chunkDigests_;
    TSharedRef topLevelDigest_;

    // ... 其他辅助方法
};
```

### 3. 持久化存储
```cpp
class DigestStorage {
public:
    void SaveDigest(const TString& key, const TMinHashDigestPtr& digest) {
        if (!digest->IsInitialized()) {
            throw std::invalid_argument("Cannot save uninitialized digest");
        }

        // 这里可以实现将摘要保存到数据库或文件系统
        auto serializedData = SerializeDigest(digest);
        storage_[key] = serializedData;
    }

    TMinHashDigestPtr LoadDigest(const TString& key) {
        if (storage_.find(key) == storage_.end()) {
            return nullptr;
        }

        auto serializedData = storage_[key];
        auto digest = New<TMinHashDigest>();
        digest->Initialize(serializedData);

        return digest;
    }

private:
    std::map<TString, TSharedRef> storage_;

    TSharedRef SerializeDigest(const TMinHashDigestPtr& digest) {
        // 实现摘要序列化逻辑
        // 这里返回模拟数据
        return TSharedRef::Allocate(0);
    }
};
```

## 依赖项

- **YT Memory**: 内存管理和引用计数支持
- **FarmHash**: 高质量哈希函数实现
- **Standard Library**: STL 容器和算法

## 注意事项

### 1. 哈希冲突
- FarmHash 提供低冲突率，但仍需考虑冲突可能性
- 对于高精度要求的场景，可以增加哈希位数
- 考虑使用多个哈希函数降低冲突概率

### 2. 数据一致性
- 确保相同输入产生相同指纹
- 考虑数据编码和字符集的一致性
- 处理边界情况和异常数据

### 3. 内存管理
- 大数据集可能导致内存压力
- 合理设置批次大小避免内存溢出
- 及时释放不再使用的数据

### 4. 并发安全
- 当前实现不是线程安全的
- 多线程环境下需要额外的同步机制
- 考虑使用原子操作或读写锁

### 5. 版本兼容性
- 格式版本号用于向后兼容性检查
- 不同版本的数据格式可能不兼容
- 升级时需要考虑数据迁移策略

### 6. 安全考虑
- 哈希值可能暴露数据特征
- 敏感数据需要额外的安全处理
- 考虑使用加密哈希函数增强安全性