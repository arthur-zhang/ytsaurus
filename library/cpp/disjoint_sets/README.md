# disjoint_sets 不相交集数据结构

[disjoint_sets](.) 是 YTsaurus 中提供高效不相交集（并查集）数据结构的 C++ 库。该模块实现了经典的并查集算法，支持按秩合并和路径压缩优化，为图算法、连通性分析、集合划分等场景提供了强大的基础设施支持。

## 📋 项目描述

`disjoint_sets` 模块提供了 `TDisjointSets` 类，实现了维护动态分区集合的高效数据结构。通过结合按秩合并（Union by Rank）和路径压缩（Path Compression）两种优化技术，该实现能够在接近常数时间内完成查找和合并操作。

### 核心价值

- **高性能**：接近 O(α(n)) 的时间复杂度，其中 α(n) 是反阿克曼函数
- **内存高效**：紧凑的数据结构，最小化内存使用
- **动态扩展**：支持运行时扩展集合数量
- **标准实现**：基于经典的并查集算法，稳定可靠

## 🏗️ 算法原理

### 并查集数据结构

并查集（Disjoint Set Union，DSU）是一种维护多个不相交集合的数据结构，支持两种基本操作：

1. **Find（查找）**：确定元素所属的集合（找到集合的代表元素）
2. **Union（合并）**：将两个不同的集合合并为一个集合

### 核心优化技术

#### 1. 路径压缩 (Path Compression)
在查找过程中，将访问的节点直接指向根节点，减少后续查找的时间复杂度。

```cpp
TElement CanonicSetElement(TElement item) const {
    if (Parents[item] != item)
        Parents[item] = CanonicSetElement(Parents[item]);  // 路径压缩
    return Parents[item];
}
```

#### 2. 按秩合并 (Union by Rank)
将秩较小的树合并到秩较大的树下，保持树的平衡性，避免退化为链表。

```cpp
void UnionSets(TElement item1, TElement item2) {
    // ... 查找代表元素
    if (Ranks[canonic1] < Ranks[canonic2]) {
        Parents[canonic1] = canonic2;  // 秩小的合并到秩大的
        Sizes[canonic2] += Sizes[canonic1];
    } else {
        Parents[canonic2] = canonic1;
        Sizes[canonic1] += Sizes[canonic2];
        Ranks[canonic2] += Ranks[canonic1] == Ranks[canonic2] ? 1 : 0;
    }
}
```

## 🚀 核心特性

### 数据结构设计

```cpp
class TDisjointSets {
private:
    mutable TVector<TElement> Parents;  // 父节点指针数组
    TVector<size_t> Ranks;              // 秩数组（树的近似高度）
    TVector<size_t> Sizes;              // 集合大小数组
    size_t NumberOfSets;                // 当前集合数量

public:
    using TElement = size_t;            // 元素类型定义
};
```

### 核心操作接口

#### 1. 构造和初始化
```cpp
// 创建指定数量的不相交集
TDisjointSets(size_t setCount);

// 动态扩展集合数量
void Expand(size_t newSetCount);
```

#### 2. 查找操作
```cpp
// 查找元素所属集合的代表元素（带路径压缩）
TElement CanonicSetElement(TElement item) const;

// 获取元素所在集合的大小
size_t SizeOfSet(TElement item) const;
```

#### 3. 合并操作
```cpp
// 合并两个元素所在的集合
void UnionSets(TElement item1, TElement item2);
```

#### 4. 状态查询
```cpp
// 获取初始集合数量
size_t InitialSetCount() const;

// 获取当前集合数量
size_t SetCount() const;
```

## 💡 使用示例

### 基础使用

```cpp
#include <library/cpp/disjoint_sets/disjoint_sets.h>

#include <iostream>
#include <vector>

int main() {
    // 创建 10 个不相交集合
    TDisjointSets ds(10);

    std::cout << "初始集合数量: " << ds.SetCount() << std::endl;  // 10

    // 合并一些集合
    ds.UnionSets(0, 1);
    ds.UnionSets(2, 3);
    ds.UnionSets(1, 2);  // 间接合并 0,1,2,3

    std::cout << "合并后集合数量: " << ds.SetCount() << std::endl;  // 7

    // 检查元素是否在同一集合中
    bool sameSet = ds.CanonicSetElement(0) == ds.CanonicSetElement(3);
    std::cout << "元素 0 和 3 在同一集合: " << (sameSet ? "是" : "否") << std::endl;

    // 获取集合大小
    size_t setSize = ds.SizeOfSet(0);
    std::cout << "元素 0 所在集合的大小: " << setSize << std::endl;  // 4

    return 0;
}
```

### 连通性分析

```cpp
#include <library/cpp/disjoint_sets/disjoint_sets.h>
#include <util/generic/vector.h>

// 图的连通分量分析
class GraphConnectivityAnalyzer {
private:
    struct Edge {
        size_t u, v;
    };

    TVector<Edge> edges;
    size_t vertexCount;

public:
    GraphConnectivityAnalyzer(size_t vertices) : vertexCount(vertices) {}

    void addEdge(size_t u, size_t v) {
        edges.push_back({u, v});
    }

    // 使用并查集分析连通分量
    TVector<TVector<size_t>> findConnectedComponents() {
        TDisjointSets ds(vertexCount);

        // 合并所有边连接的顶点
        for (const auto& edge : edges) {
            ds.UnionSets(edge.u, edge.v);
        }

        // 收集连通分量
        THashMap<size_t, TVector<size_t>> components;
        for (size_t i = 0; i < vertexCount; ++i) {
            size_t root = ds.CanonicSetElement(i);
            components[root].push_back(i);
        }

        TVector<TVector<size_t>> result;
        for (const auto& [root, component] : components) {
            result.push_back(component);
        }

        return result;
    }

    // 检查图是否连通
    bool isConnected() {
        if (vertexCount == 0) return true;

        TDisjointSets ds(vertexCount);
        for (const auto& edge : edges) {
            ds.UnionSets(edge.u, edge.v);
        }

        return ds.SetCount() == 1;
    }

    // 检查两个顶点是否连通
    bool areConnected(size_t u, size_t v) {
        TDisjointSets ds(vertexCount);
        for (const auto& edge : edges) {
            ds.UnionSets(edge.u, edge.v);
        }

        return ds.CanonicSetElement(u) == ds.CanonicSetElement(v);
    }
};
```

### Kruskal 最小生成树算法

```cpp
#include <library/cpp/disjoint_sets/disjoint_sets.h>

struct Edge {
    size_t u, v;
    int weight;
};

class KruskalMST {
public:
    static TVector<Edge> findMST(size_t vertexCount, TVector<Edge> edges) {
        // 按权重排序边
        std::sort(edges.begin(), edges.end(),
                 [](const Edge& a, const Edge& b) {
                     return a.weight < b.weight;
                 });

        TDisjointSets ds(vertexCount);
        TVector<Edge> mst;

        for (const auto& edge : edges) {
            // 如果边连接不同的连通分量，则加入MST
            if (ds.CanonicSetElement(edge.u) != ds.CanonicSetElement(edge.v)) {
                mst.push_back(edge);
                ds.UnionSets(edge.u, edge.v);

                // 如果已经包含所有顶点，则完成
                if (mst.size() == vertexCount - 1) {
                    break;
                }
            }
        }

        return mst;
    }

    static int calculateMSTWeight(const TVector<Edge>& mst) {
        int totalWeight = 0;
        for (const auto& edge : mst) {
            totalWeight += edge.weight;
        }
        return totalWeight;
    }
};
```

### 等价关系处理

```cpp
class EquivalenceRelationProcessor {
private:
    TDisjointSets ds;

public:
    EquivalenceRelationProcessor(size_t initialSize) : ds(initialSize) {}

    // 添加等价关系
    void addEquivalence(size_t a, size_t b) {
        ds.UnionSets(a, b);
    }

    // 检查等价性
    bool areEquivalent(size_t a, size_t b) {
        return ds.CanonicSetElement(a) == ds.CanonicSetElement(b);
    }

    // 获取等价类
    TVector<TVector<size_t>> getEquivalenceClasses() {
        THashMap<size_t, TVector<size_t>> classes;
        size_t totalElements = ds.InitialSetCount();

        for (size_t i = 0; i < totalElements; ++i) {
            size_t representative = ds.CanonicSetElement(i);
            classes[representative].push_back(i);
        }

        TVector<TVector<size_t>> result;
        for (const auto& [rep, elements] : classes) {
            result.push_back(elements);
        }

        return result;
    }

    // 动态添加新元素
    size_t addElement() {
        size_t newSize = ds.InitialSetCount() + 1;
        ds.Expand(newSize);
        return newSize - 1;  // 返回新元素的索引
    }
};
```

## 🎯 应用场景

### 1. 图算法应用

#### 连通性检查
```cpp
// 网络连通性分析
class NetworkAnalyzer {
public:
    static bool isNetworkConnected(size_t nodeCount,
                                  const TVector<std::pair<size_t, size_t>>& connections) {
        TDisjointSets ds(nodeCount);

        for (const auto& [u, v] : connections) {
            ds.UnionSets(u, v);
        }

        return ds.SetCount() == 1;
    }

    static size_t countNetworkComponents(size_t nodeCount,
                                        const TVector<std::pair<size_t, size_t>>& connections) {
        TDisjointSets ds(nodeCount);

        for (const auto& [u, v] : connections) {
            ds.UnionSets(u, v);
        }

        return ds.SetCount();
    }
};
```

#### 环检测
```cpp
// 无向图环检测
class CycleDetector {
public:
    static bool hasCycle(size_t vertexCount, const TVector<std::pair<size_t, size_t>>& edges) {
        TDisjointSets ds(vertexCount);

        for (const auto& [u, v] : edges) {
            // 如果两个端点已经在同一集合中，添加这条边会形成环
            if (ds.CanonicSetElement(u) == ds.CanonicSetElement(v)) {
                return true;
            }
            ds.UnionSets(u, v);
        }

        return false;
    }

    static TVector<std::pair<size_t, size_t>> findSpanningTree(
            size_t vertexCount, const TVector<std::pair<size_t, size_t>>& edges) {
        TDisjointSets ds(vertexCount);
        TVector<std::pair<size_t, size_t>> spanningTree;

        for (const auto& [u, v] : edges) {
            if (ds.CanonicSetElement(u) != ds.CanonicSetElement(v)) {
                spanningTree.push_back({u, v});
                ds.UnionSets(u, v);

                if (spanningTree.size() == vertexCount - 1) {
                    break;
                }
            }
        }

        return spanningTree;
    }
};
```

### 2. 集合划分和聚类

#### 动态聚类
```cpp
class DynamicClusterer {
private:
    struct ClusterInfo {
        size_t id;
        TVector<size_t> elements;
    };

    TDisjointSets ds;
    TVector<ClusterInfo> clusters;

public:
    DynamicClusterer(size_t initialElements) : ds(initialElements) {
        // 初始时每个元素是一个单独的簇
        for (size_t i = 0; i < initialElements; ++i) {
            clusters.push_back({i, {i}});
        }
    }

    // 合并两个簇
    void mergeClusters(size_t cluster1, size_t cluster2) {
        size_t elem1 = clusters[cluster1].elements[0];
        size_t elem2 = clusters[cluster2].elements[0];
        ds.UnionSets(elem1, elem2);
        updateClusterInfo();
    }

    // 获取所有簇
    TVector<ClusterInfo> getClusters() {
        updateClusterInfo();
        return clusters;
    }

    // 获取元素所属的簇
    size_t getClusterOfElement(size_t element) {
        size_t root = ds.CanonicSetElement(element);
        for (size_t i = 0; i < clusters.size(); ++i) {
            if (!clusters[i].elements.empty() &&
                ds.CanonicSetElement(clusters[i].elements[0]) == root) {
                return i;
            }
        }
        return SIZE_MAX;
    }

private:
    void updateClusterInfo() {
        THashMap<size_t, TVector<size_t>> elementGroups;
        size_t totalElements = ds.InitialSetCount();

        for (size_t i = 0; i < totalElements; ++i) {
            size_t root = ds.CanonicSetElement(i);
            elementGroups[root].push_back(i);
        }

        clusters.clear();
        size_t clusterId = 0;
        for (const auto& [root, elements] : elementGroups) {
            clusters.push_back({clusterId++, elements});
        }
    }
};
```

### 3. 字符串等价类处理

```cpp
// 基于某种规则的字符串等价处理
class StringEquivalenceProcessor {
private:
    THashMap<TString, size_t> stringToIndex;
    TVector<TString> indexToString;
    TDisjointSets ds;

public:
    StringEquivalenceProcessor() : ds(0) {}

    // 添加字符串
    size_t addString(const TString& str) {
        if (stringToIndex.find(str) != stringToIndex.end()) {
            return stringToIndex[str];
        }

        size_t index = indexToString.size();
        stringToIndex[str] = index;
        indexToString.push_back(str);

        ds.Expand(index + 1);
        return index;
    }

    // 添加等价关系
    void addEquivalence(const TString& str1, const TString& str2) {
        size_t idx1 = addString(str1);
        size_t idx2 = addString(str2);
        ds.UnionSets(idx1, idx2);
    }

    // 检查等价性
    bool areEquivalent(const TString& str1, const TString& str2) {
        auto it1 = stringToIndex.find(str1);
        auto it2 = stringToIndex.find(str2);

        if (it1 == stringToIndex.end() || it2 == stringToIndex.end()) {
            return false;
        }

        return ds.CanonicSetElement(it1->second) == ds.CanonicSetElement(it2->second);
    }

    // 获取等价类
    TVector<TVector<TString>> getEquivalenceClasses() {
        THashMap<size_t, TVector<TString>> classes;

        for (size_t i = 0; i < indexToString.size(); ++i) {
            size_t root = ds.CanonicSetElement(i);
            classes[root].push_back(indexToString[i]);
        }

        TVector<TVector<TString>> result;
        for (const auto& [root, strings] : classes) {
            result.push_back(strings);
        }

        return result;
    }
};
```

## ⚡ 性能优化

### 1. 内存优化

```cpp
// 紧凑的并查集实现
class CompactDisjointSets {
private:
    TVector<size_t> parent;  // 使用最低位存储秩信息
    size_t setCount;

    // 使用位操作压缩存储秩信息
    static constexpr size_t RANK_BITS = 16;
    static constexpr size_t RANK_MASK = (1 << RANK_BITS) - 1;
    static constexpr size_t PARENT_SHIFT = RANK_BITS;

public:
    CompactDisjointSets(size_t n) : parent(n), setCount(n) {
        for (size_t i = 0; i < n; ++i) {
            parent[i] = i << PARENT_SHIFT;  // 秩为0
        }
    }

    size_t find(size_t x) {
        if ((parent[x] >> PARENT_SHIFT) != x) {
            parent[x] = find(parent[x] >> PARENT_SHIFT) << PARENT_SHIFT;
        }
        return parent[x] >> PARENT_SHIFT;
    }

    void unite(size_t x, size_t y) {
        size_t px = find(x);
        size_t py = find(y);
        if (px == py) return;

        size_t rankX = parent[px] & RANK_MASK;
        size_t rankY = parent[py] & RANK_MASK;

        if (rankX < rankY) {
            parent[px] = (py << PARENT_SHIFT) | rankX;
        } else if (rankX > rankY) {
            parent[py] = (px << PARENT_SHIFT) | rankY;
        } else {
            parent[py] = (px << PARENT_SHIFT) | rankY;
            parent[px] = (parent[px] & ~RANK_MASK) | (rankX + 1);
        }

        --setCount;
    }
};
```

### 2. 批量操作优化

```cpp
// 批量合并优化
class BatchDisjointSets {
private:
    TDisjointSets ds;

public:
    BatchDisjointSets(size_t n) : ds(n) {}

    // 批量合并多个元素对
    void batchUnion(const TVector<std::pair<size_t, size_t>>& pairs) {
        // 收集所有需要合并的元素
        TVector<size_t> elements;
        for (const auto& [u, v] : pairs) {
            elements.push_back(u);
            elements.push_back(v);
        }

        // 预先进行路径压缩
        for (size_t elem : elements) {
            ds.CanonicSetElement(elem);
        }

        // 执行合并操作
        for (const auto& [u, v] : pairs) {
            ds.UnionSets(u, v);
        }
    }

    // 批量查找
    TVector<size_t> batchFind(const TVector<size_t>& elements) {
        TVector<size_t> results;
        results.reserve(elements.size());

        for (size_t elem : elements) {
            results.push_back(ds.CanonicSetElement(elem));
        }

        return results;
    }
};
```

## 🔗 最佳实践

### 1. 错误处理

```cpp
class SafeDisjointSets {
private:
    TDisjointSets ds;
    size_t maxElements;

public:
    SafeDisjointSets(size_t initialSize, size_t maxSize = SIZE_MAX)
        : ds(initialSize), maxElements(maxSize) {}

    // 安全的合并操作
    bool safeUnion(size_t a, size_t b) {
        if (a >= ds.InitialSetCount() || b >= ds.InitialSetCount()) {
            return false;  // 元素索引超出范围
        }

        try {
            ds.UnionSets(a, b);
            return true;
        } catch (const std::exception& e) {
            // 记录错误日志
            std::cerr << "Union operation failed: " << e.what() << std::endl;
            return false;
        }
    }

    // 安全的查找操作
    std::optional<size_t> safeFind(size_t a) {
        if (a >= ds.InitialSetCount()) {
            return std::nullopt;
        }

        return ds.CanonicSetElement(a);
    }

    // 安全的扩展操作
    bool safeExpand(size_t newSize) {
        if (newSize > maxElements) {
            return false;  // 超过最大元素限制
        }

        try {
            ds.Expand(newSize);
            return true;
        } catch (const std::exception& e) {
            std::cerr << "Expand operation failed: " << e.what() << std::endl;
            return false;
        }
    }
};
```

### 2. 调试和验证

```cpp
// 带调试功能的并查集
class DebuggableDisjointSets {
private:
    TDisjointSets ds;
    mutable THashMap<size_t, TVector<size_t>> cache;

public:
    DebuggableDisjointSets(size_t n) : ds(n) {}

    void UnionSets(size_t a, size_t b) {
        cache.clear();  // 清除缓存
        ds.UnionSets(a, b);
    }

    size_t CanonicSetElement(size_t a) const {
        return ds.CanonicSetElement(a);
    }

    // 验证数据结构的一致性
    bool validate() const {
        size_t n = ds.InitialSetCount();
        THashMap<size_t, TVector<size_t>> groups;

        // 检查所有元素的根节点一致性
        for (size_t i = 0; i < n; ++i) {
            size_t root = ds.CanonicSetElement(i);
            groups[root].push_back(i);
        }

        // 验证集合数量
        if (groups.size() != ds.SetCount()) {
            std::cerr << "Set count mismatch: expected " << groups.size()
                     << ", got " << ds.SetCount() << std::endl;
            return false;
        }

        // 验证集合大小
        for (const auto& [root, elements] : groups) {
            size_t expectedSize = ds.SizeOfSet(elements[0]);
            if (elements.size() != expectedSize) {
                std::cerr << "Size mismatch for set " << root
                         << ": expected " << expectedSize
                         << ", got " << elements.size() << std::endl;
                return false;
            }
        }

        return true;
    }

    // 打印当前状态
    void printState() const {
        std::cout << "DisjointSets State:" << std::endl;
        std::cout << "  Total sets: " << ds.SetCount() << std::endl;
        std::cout << "  Total elements: " << ds.InitialSetCount() << std::endl;

        THashMap<size_t, TVector<size_t>> groups;
        for (size_t i = 0; i < ds.InitialSetCount(); ++i) {
            size_t root = ds.CanonicSetElement(i);
            groups[root].push_back(i);
        }

        for (const auto& [root, elements] : groups) {
            std::cout << "  Set " << root << " (size " << elements.size() << "): ";
            for (size_t elem : elements) {
                std::cout << elem << " ";
            }
            std::cout << std::endl;
        }
    }
};
```

## 📝 注意事项

### 1. 时间复杂度
- **Find操作**：接近 O(α(n))，其中 α(n) 是反阿克曼函数
- **Union操作**：接近 O(α(n))
- **总体复杂度**：在实际应用中可以认为是常数时间

### 2. 空间复杂度
- **存储空间**：O(n)，需要存储父节点、秩和大小信息
- **内存使用**：每个元素约需要 3 个 size_t 的空间

### 3. 线程安全
- **非线程安全**：`TDisjointSets` 类不是线程安全的
- **并发访问**：多线程环境下需要额外的同步机制

### 4. 元素索引
- **索引范围**：元素索引从 0 开始
- **动态扩展**：支持运行时扩展，但扩展不会缩小
- **索引有效性**：调用方需要确保索引在有效范围内

`disjoint_sets` 模块为 YTsaurus 项目提供了高效、可靠的不相交集数据结构实现，是图算法、连通性分析、聚类等应用的重要基础设施。