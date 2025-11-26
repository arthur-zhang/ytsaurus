# Containers 高性能容器库

## 项目描述

Containers 库是 YTsaurus 中的高性能容器组件集合，提供了多种专门优化的数据结构和容器实现。该库包含针对特定场景优化的容器，如栈分配向量、环形缓冲区、紧凑向量、高效哈希表等，旨在提供比标准容器更好的性能和内存效率。

通过精心的设计和优化，这些容器在保持标准容器接口兼容性的同时，在各种使用场景下提供了卓越的性能表现。

## 核心特性

### 🚀 高性能优化
- **零分配设计**: 部分容器支持栈分配，避免动态内存分配
- **缓存友好**: 优化的内存布局和访问模式
- **SIMD 优化**: 利用向量化指令加速操作
- **分支预测优化**: 减少分支预测失败

### 💾 内存效率
- **紧凑存储**: 减少内存占用和存储开销
- **预分配策略**: 智能的内存预分配机制
- **原地操作**: 支持原地修改和构建
- **内存池**: 可配置的内存分配策略

### 🔧 专用设计
- **场景特化**: 针对特定使用场景优化
- **接口兼容**: 与标准容器接口保持兼容
- **类型安全**: 强类型设计和编译时检查
- **异常安全**: 完整的异常安全保证

### 📊 丰富选择
- **栈向量**: 小容量时的栈分配优化
- **环形缓冲区**: 固定大小的循环队列
- **紧凑向量**: 紧凑内存布局的向量
- **高效哈希**: 基于 Google Abseil 的扁平哈希表

## 主要组件

### 1. 栈分配向量 (TStackVec)
```cpp
template <typename T, size_t CountOnStack = 256,
          bool UseFallbackAlloc = true, class Alloc = std::allocator<T>>
class TStackVec;

// 便捷别名
template <typename T, class Alloc = std::allocator<T>>
using TSmallVec = TStackVec<T, 16, true, Alloc>;

template <typename T, size_t CountOnStack = 256>
using TStackOnlyVec = TStackVec<T, CountOnStack, false>;
```

#### 核心特性
- **栈分配**: 默认在栈上预分配指定数量元素
- **堆回退**: 超过栈容量时自动切换到堆分配
- **零开销**: 栈容量内零动态分配开销
- **兼容性**: 继承 TVector，保持接口兼容

#### 使用示例
```cpp
// 小数组优化，默认栈分配 256 个元素
TStackVec<int, 256> vec;
vec.push_back(1);
vec.push_back(2);

// 超过栈容量时自动使用堆分配
for (int i = 0; i < 1000; ++i) {
    vec.push_back(i);
}

// 小型向量，栈分配 16 个元素
TSmallVec<double> smallVec;
smallVec.push_back(3.14);

// 仅栈分配版本，不使用堆回退
TStackOnlyVec<char, 128> stackOnlyVec;
```

### 2. 环形缓冲区 (TRingBuffer)
```cpp
template <typename T>
class TSimpleRingBuffer {
public:
    TSimpleRingBuffer(size_t maxSize);

    // 访问操作
    size_t FirstIndex() const;
    size_t AvailSize() const;
    size_t TotalSize() const;
    bool IsAvail(size_t index) const;
    const T& operator[](size_t index) const;
    T& operator[](size_t index);

    // 修改操作
    void PushBack(const T& t);
    void Clear();
};

template <typename T, size_t maxSize>
class TStaticRingBuffer: public TSimpleRingBuffer<T>;
```

#### 核心特性
- **固定大小**: 固定容量的循环缓冲区
- **自动覆盖**: 满时自动覆盖最旧的数据
- **索引追踪**: 维护总插入数量的索引
- **O(1) 操作**: 所有操作都是常数时间复杂度

#### 使用示例
```cpp
// 动态大小环形缓冲区
TSimpleRingBuffer<int> ringBuffer(100);
ringBuffer.PushBack(1);
ringBuffer.PushBack(2);

// 静态大小环形缓冲区
TStaticRingBuffer<double, 50> staticRing;

// 访问元素
size_t firstIdx = ringBuffer.FirstIndex();
size_t availSize = ringBuffer.AvailSize();

for (size_t i = firstIdx; i < firstIdx + availSize; ++i) {
    if (ringBuffer.IsAvail(i)) {
        int value = ringBuffer[i];
        // 处理值
    }
}
```

### 3. 紧凑向量 (TCompactVector)
```cpp
template <typename T>
class TCompactVector {
    // 紧凑内存布局的向量实现
};
```

#### 核心特性
- **紧凑存储**: 最小化内存占用
- **缓存友好**: 优化的内存布局
- **快速迭代**: 高效的遍历操作

### 4. Abseil 扁平哈希表 (TFlatHashMap)
```cpp
template <typename Key, typename Value, typename Hash = std::hash<Key>>
class TFlatHashMap;

template <typename Key, typename Hash = std::hash<Key>>
class TFlatHashSet;
```

#### 核心特性
- **扁平存储**: 减少内存开销
- **开放寻址**: 高效的冲突解决策略
- **缓存优化**: 优化的探针序列
- **快速查找**: 优于标准哈希表的性能

#### 使用示例
```cpp
#include <library/cpp/containers/absl_flat_hash/flat_hash_map.h>

TFlatHashMap<TString, int> wordCount;
wordCount["hello"] = 1;
wordCount["world"] = 2;

TFlatHashSet<int> uniqueNumbers;
uniqueNumbers.insert(42);
uniqueNumbers.insert(123);

// 标准兼容的操作
for (const auto& [key, value] : wordCount) {
    Cout << key << ": " << value << Endl;
}
```

### 5. 栈数组 (TStackArray)
```cpp
template <typename T, size_t Size>
class TStackArray {
    // 固定大小栈数组
};
```

#### 核心特性
- **固定大小**: 编译时确定大小
- **栈分配**: 完全在栈上分配
- **零运行时开销**: 与原生数组性能相同
- **边界检查**: 可选的边界检查

### 6. 页面向量 (TPagedVector)
```cpp
template <typename T, size_t PageSize = 4096 / sizeof(T)>
class TPagedVector {
    // 分页存储的大容量向量
};
```

#### 核心特性
- **分页存储**: 大数据量的分页管理
- **延迟分配**: 按需分配页面内存
- **高效插入**: 局部性优化的插入操作
- **大容量支持**: 支持超大容量向量

### 7. 排序向量 (TSortedVector)
```cpp
template <typename T, typename Compare = std::less<T>>
class TSortedVector {
    // 始终保持排序的向量
};
```

#### 核心特性
- **自动排序**: 插入时自动维护排序
- **二分查找**: 高效的查找操作
- **范围查询**: 支持高效的范围查询
- **唯一性**: 可选的唯一性约束

### 8. 位序列 (TBitSequence)
```cpp
class TBitSequence {
    // 高效的位序列操作
};
```

#### 核心特性
- **位级操作**: 高效的位操作支持
- **压缩存储**: 紧凑的位存储
- **批量操作**: 支持批量位操作
- **快速查询**: 位查询和设置优化

## 性能对比

### 内存使用对比

| 容器类型 | 内存开销 | 适用场景 |
|----------|----------|----------|
| std::vector | 中等 | 通用 |
| TStackVec | 小容量时零开销 | 小数组 |
| TCompactVector | 最小 | 紧凑存储 |
| TFlatHashMap | 小于 std::unordered_map | 高效哈希 |

### 操作性能对比

| 操作 | std::vector | TStackVec | TFlatHashMap |
|------|-------------|-----------|--------------|
| push_back | O(1)* | O(1) | - |
| 访问 | O(1) | O(1) | O(1) |
| 查找 | O(n) | O(n) | O(1) |
| 插入 | O(n) | O(n) | O(1) |

*均摊时间复杂度

## 使用场景

### 1. 性能敏感的临时容器
```cpp
// 使用 TStackVec 避免动态分配
void ProcessSmallDataSet() {
    TStackVec<double, 64> tempData;  // 栈分配 64 个元素

    for (int i = 0; i < 50; ++i) {
        tempData.push_back(calculate(i));
    }

    std::sort(tempData.begin(), tempData.end());
    processSortedData(tempData);
}
```

### 2. 固定大小的缓存
```cpp
// 使用环形缓冲区实现 LRU 缓存
template <typename K, typename V, size_t Size>
class LRUCache {
private:
    struct CacheEntry {
        K key;
        V value;
    };

    TStaticRingBuffer<CacheEntry, Size> ringBuffer;
    TFlatHashMap<K, V> cacheMap;

public:
    void Put(const K& key, const V& value) {
        CacheEntry entry{key, value};
        ringBuffer.PushBack(entry);
        cacheMap[key] = value;
    }

    std::optional<V> Get(const K& key) {
        auto it = cacheMap.find(key);
        return it != cacheMap.end() ? std::make_optional(it->second) : std::nullopt;
    }
};
```

### 3. 高频数据结构
```cpp
// 使用 TFlatHashMap 提升查找性能
class FrequencyCounter {
private:
    TFlatHashMap<TString, size_t> wordFrequencies;

public:
    void CountWords(const TVector<TString>& words) {
        for (const auto& word : words) {
            wordFrequencies[word]++;
        }
    }

    size_t GetFrequency(const TString& word) const {
        auto it = wordFrequencies.find(word);
        return it != wordFrequencies.end() ? it->second : 0;
    }
};
```

### 4. 内存受限环境
```cpp
// 使用紧凑向量节省内存
class CompactMatrix {
private:
    TCompactVector<float> data;
    size_t rows_, cols_;

public:
    CompactMatrix(size_t rows, size_t cols)
        : rows_(rows), cols_(cols), data(rows * cols) {}

    float& operator()(size_t row, size_t col) {
        return data[row * cols_ + col];
    }

    const float& operator()(size_t row, size_t col) const {
        return data[row * cols_ + col];
    }
};
```

## 最佳实践

### 1. 容器选择指南
```cpp
// 根据数据特征选择合适的容器
template <typename T>
auto ChooseContainer(size_t expectedSize) {
    if (expectedSize <= 16) {
        return TSmallVec<T>{};           // 小数据，栈优化
    } else if (expectedSize <= 256) {
        return TStackVec<T, 256>{};       // 中等数据，栈分配
    } else {
        return TVector<T>{};              // 大数据，标准向量
    }
}

// 根据操作模式选择哈希容器
template <typename K, typename V>
auto ChooseHashMap(size_t expectedElements) {
    if (expectedElements < 1000) {
        return std::unordered_map<K, V>{}; // 小数据集
    } else {
        return TFlatHashMap<K, V>{};        // 大数据集，性能优化
    }
}
```

### 2. 性能优化技巧
```cpp
// 预分配优化
void OptimizeVectorUsage() {
    TStackVec<int, 1000> vec;
    vec.reserve(500);  // 预分配避免重复分配

    // 批量插入
    TVector<int> source = generateData();
    vec.insert(vec.end(), source.begin(), source.end());
}

// 局部性优化
void ProcessDataInBlocks() {
    constexpr size_t BLOCK_SIZE = 64;
    TStackVec<int, BLOCK_SIZE> block;

    for (size_t i = 0; i < totalData; i += BLOCK_SIZE) {
        block.clear();
        size_t blockSize = Min(BLOCK_SIZE, totalData - i);

        // 批量处理提高缓存效率
        for (size_t j = 0; j < blockSize; ++j) {
            block.push_back(data[i + j]);
        }

        ProcessBlock(block);
    }
}
```

### 3. 内存管理策略
```cpp
// 自定义分配器策略
template <typename T>
class PoolAllocator {
private:
    TStackVec<T, 1024> pool_;  // 对象池
    size_t nextAvailable_ = 0;

public:
    T* allocate(size_t count) {
        if (nextAvailable_ + count <= pool_.capacity()) {
            T* ptr = &pool_[nextAvailable_];
            nextAvailable_ += count;
            return ptr;
        }
        return new T[count];  // 回退到标准分配
    }

    void deallocate(T* ptr, size_t count) {
        // 简化的回收策略
        if (ptr >= &pool_[0] && ptr < &pool_[pool_.capacity()]) {
            // 池中内存，无需释放
        } else {
            delete[] ptr;
        }
    }
};
```

## 高级特性

### 1. 自定义扩容策略
```cpp
// 自定义扩容策略的向量
template <typename T>
class SmartVector {
private:
    TStackVec<T, 64> data_;
    size_t nextCapacity_ = 64;

    void smartReserve(size_t needed) {
        if (data_.capacity() >= needed) return;

        // 智能扩容策略
        size_t newCapacity = Max(needed, data_.size() * 2);
        newCapacity = Max(newCapacity, nextCapacity_);

        data_.reserve(newCapacity);
        nextCapacity_ = newCapacity * 2;
    }

public:
    void push_back(const T& item) {
        smartReserve(data_.size() + 1);
        data_.push_back(item);
    }
};
```

### 2. 类型特化优化
```cpp
// 针对特定类型的优化
template <>
class TStackVec<bool, 256> {
private:
    TStaticRingBuffer<bool, 256> bitBuffer_;
    TBitSequence bitData_;

public:
    void push_back(bool value) {
        if (bitBuffer_.AvailSize() < 256) {
            bitBuffer_.PushBack(value);
        } else {
            bitData_.push_back(value);
        }
    }

    bool operator[](size_t index) const {
        if (index < bitBuffer_.AvailSize()) {
            return bitBuffer_[bitBuffer_.FirstIndex() + index];
        } else {
            return bitData_[index - bitBuffer_.AvailSize()];
        }
    }
};
```

### 3. 并发优化
```cpp
// 线程安全的环形缓冲区
template <typename T>
class ConcurrentRingBuffer {
private:
    TStaticRingBuffer<T, 1024> buffer_;
    std::mutex mutex_;
    std::condition_variable notEmpty_;
    std::condition_variable notFull_;

public:
    void Push(const T& item) {
        std::unique_lock<std::mutex> lock(mutex_);

        notFull_.wait(lock, [this] {
            return buffer_.AvailSize() < buffer_.capacity();
        });

        buffer_.PushBack(item);
        notEmpty_.notify_one();
    }

    T Pop() {
        std::unique_lock<std::mutex> lock(mutex_);

        notEmpty_.wait(lock, [this] {
            return buffer_.AvailSize() > 0;
        });

        T item = buffer_[buffer_.FirstIndex()];
        // 简化实现，实际需要更复杂的索引管理
        return item;
    }
};
```

## 测试和基准

### 性能基准测试
```cpp
void BenchmarkContainers() {
    constexpr size_t N = 1000000;
    constexpr size_t REPEATS = 100;

    // 基准测试 TStackVec vs std::vector
    auto benchmarkStackVec = [&]() {
        auto start = std::chrono::high_resolution_clock::now();

        for (size_t r = 0; r < REPEATS; ++r) {
            TStackVec<int, 1000> vec;
            for (size_t i = 0; i < N; ++i) {
                vec.push_back(i);
            }
        }

        auto end = std::chrono::high_resolution_clock::now();
        return std::chrono::duration<double>(end - start).count();
    };

    auto benchmarkStdVector = [&]() {
        auto start = std::chrono::high_resolution_clock::now();

        for (size_t r = 0; r < REPEATS; ++r) {
            std::vector<int> vec;
            for (size_t i = 0; i < N; ++i) {
                vec.push_back(i);
            }
        }

        auto end = std::chrono::high_resolution_clock::now();
        return std::chrono::duration<double>(end - start).count();
    };

    double stackVecTime = benchmarkStackVec();
    double stdVectorTime = benchmarkStdVector();

    Cout << "TStackVec: " << stackVecTime << "s" << Endl;
    Cout << "std::vector: " << stdVectorTime << "s" << Endl;
    Cout << "Speedup: " << stdVectorTime / stackVecTime << "x" << Endl;
}
```

## 限制和注意事项

### 使用限制
- **栈空间限制**: TStackVec 的栈大小受限于栈空间
- **类型要求**: 某些容器对类型有特殊要求
- **兼容性**: 虽然接口兼容，但行为可能有细微差异

### 最佳实践建议
- **容量预估**: 合理预估容器大小以优化性能
- **局部性**: 保持数据访问的局部性
- **异常安全**: 注意容器的异常安全保证

## 总结

Containers 库为 YTsaurus 系统提供了丰富的高性能容器选择。通过针对特定场景的优化设计，这些容器在保持标准容器接口兼容性的同时，在各种应用场景下都能提供更好的性能表现。

无论是追求零分配的小容器优化，还是需要高效查找的大数据结构，这个库都能提供合适的解决方案。通过合理选择和使用这些容器，开发者可以显著提升应用程序的性能和内存效率。