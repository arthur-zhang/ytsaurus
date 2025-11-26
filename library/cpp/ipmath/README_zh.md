# IP 地址数学运算库

## 项目概述

IP 地址数学运算库提供了处理 IP 地址和 IP 地址范围的高级功能，支持 IPv4 和 IPv6 地址。该库实现了 CIDR 表示法、范围运算、集合操作等功能，为网络应用程序提供强大的 IP 地址处理能力。

## 核心功能

### IP 地址范围
- **范围定义**：支持多种格式定义 IP 地址范围
- **CIDR 表示**：标准的无类域间路由表示法
- **范围运算**：包含、重叠、连续性检查
- **范围合并**：智能合并连续或重叠的范围

### IP 地址集合
- **范围集合**：维护不相交的 IP 范围集合
- **成员查询**：高效的地址包含性检查
- **批量操作**：支持批量添加 IP 范围

## 主要类

### TIpAddressRange
IP 地址范围的核心类，提供完整的范围操作功能。

#### 构造方式
```cpp
// 从起始和结束地址构造
TIpAddressRange range(TIpv6Address("192.168.1.1"), TIpv6Address("192.168.1.255"));

// 从字符串构造
TIpAddressRange range("192.168.1.1", "192.168.1.255");

// 从 CIDR 字符串构造
auto cidrRange = TIpAddressRange::FromCidrString("192.168.0.0/16");

// 从紧凑 CIDR 构造（包含节点地址）
auto compactRange = TIpAddressRange::FromCompactString("192.168.1.24/16");

// 从范围字符串构造
auto rangeRange = TIpAddressRange::FromRangeString("10.0.0.0-10.0.0.255");

// 自动格式识别
auto autoRange = TIpAddressRange::FromString("192.168.1.0/24");
```

#### Builder 模式
```cpp
// 使用流式 API 构建范围
auto range = TIpAddressRange::From("192.168.1.0")
    .To("192.168.1.255")
    .Build();

auto cidrRange = TIpAddressRange::From("10.0.0.0")
    .WithPrefix(24)  // /24 网段
    .Build();

auto maskedRange = TIpAddressRange::From("192.168.1.100")
    .WithMaskedPrefix(24)  // 自动对齐到网段边界
    .Build();
```

### TIpRangeSet
IP 地址范围集合类，维护不相交的范围集合。

```cpp
TIpRangeSet rangeSet;

// 添加单个范围
rangeSet.Add(TIpAddressRange::FromCidrString("192.168.1.0/24"));

// 批量添加范围
TVector<TIpAddressRange> ranges = {
    TIpAddressRange::FromCidrString("10.0.0.0/8"),
    TIpAddressRange::FromCidrString("172.16.0.0/12")
};
rangeSet.Add(ranges);

// 成员查询
bool contains = rangeSet.Contains(TIpv6Address("192.168.1.100"));

// 查找包含地址的范围
auto it = rangeSet.Find(TIpv6Address("192.168.1.100"));
if (it != rangeSet.End()) {
    Cout << "Address found in range: " << it->ToRangeString() << Endl;
}
```

## 使用示例

### 基本范围操作
```cpp
#include <library/cpp/ipmath/ipmath.h>

// 创建 IP 地址范围
TIpAddressRange network1 = TIpAddressRange::FromCidrString("192.168.1.0/24");
TIpAddressRange network2 = TIpAddressRange::FromCidrString("192.168.2.0/24");
TIpAddressRange host = TIpAddressRange::FromCidrString("192.168.1.100/32");

// 范围信息
Cout << "Network type: " << (int)network1.Type() << Endl;  // IPv4
Cout << "Range size: " << network1.Size() << Endl;        // 256
Cout << "Is single address: " << network1.IsSingle() << Endl;  // false
Cout << "Is complete: " << network1.IsComplete() << Endl;  // false

// 包含性检查
bool containsHost = network1.Contains(TIpv6Address("192.168.1.100"));
bool containsNetwork = network1.Contains(network2);  // false

// 重叠检查
bool overlaps = network1.Overlaps(network2);  // false

// 连续性检查
bool consecutive = network1.IsConsecutive(network2);  // true

// 范围合并
if (consecutive) {
    TIpAddressRange merged = network1.Union(network2);
    Cout << "Merged range: " << merged.ToRangeString() << Endl;
}
```

### 迭代和遍历
```cpp
// 使用迭代器遍历范围中的每个地址
TIpAddressRange smallRange = TIpAddressRange::FromCidrString("192.168.1.0/29");
for (auto it = smallRange.Begin(); it != smallRange.End(); ++it) {
    Cout << it->ToString() << Endl;
}

// 使用范围 for 循环
for (const auto& addr : smallRange) {
    Cout << addr.ToString() << Endl;
}

// 使用 ForEach 函数
smallRange.ForEach([](const TIpv6Address& addr) {
    Cout << "Processing: " << addr.ToString() << Endl;
});
```

### 复杂网络分析
```cpp
// 分析网络拓扑
class TNetworkAnalyzer {
private:
    TIpRangeSet PrivateNetworks;
    TIpRangeSet PublicNetworks;

public:
    TNetworkAnalyzer() {
        // 定义私有网络范围
        PrivateNetworks.Add(TIpAddressRange::FromCidrString("10.0.0.0/8"));
        PrivateNetworks.Add(TIpAddressRange::FromCidrString("172.16.0.0/12"));
        PrivateNetworks.Add(TIpAddressRange::FromCidrString("192.168.0.0/16"));

        // 定义公网范围（简化示例）
        PrivateNetworks.Add(TIpAddressRange::FromCidrString("0.0.0.0/0"));
    }

    bool IsPrivateAddress(const TIpv6Address& addr) {
        return PrivateNetworks.Contains(addr);
    }

    TVector<TIpAddressRange> GetContainingRanges(const TIpv6Address& addr) {
        TVector<TIpAddressRange> result;
        for (const auto& range : PrivateNetworks) {
            if (range.Contains(addr)) {
                result.push_back(range);
            }
        }
        return result;
    }

    void AnalyzeAddress(const TIpv6Address& addr) {
        Cout << "Address: " << addr.ToString() << Endl;
        Cout << "Is private: " << IsPrivateAddress(addr) << Endl;

        auto ranges = GetContainingRanges(addr);
        Cout << "Containing ranges:" << Endl;
        for (const auto& range : ranges) {
            Cout << "  - " << range.ToRangeString() << Endl;
        }
    }
};
```

### 网络访问控制
```cpp
// IP 访问控制列表
class TAccessControlList {
private:
    TIpRangeSet AllowedRanges;
    TIpRangeSet DeniedRanges;

public:
    void AllowRange(const TStringBuf cidr) {
        AllowedRanges.Add(TIpAddressRange::FromCidrString(cidr));
    }

    void DenyRange(const TStringBuf cidr) {
        DeniedRanges.Add(TIpAddressRange::FromCidrString(cidr));
    }

    bool IsAccessAllowed(const TIpv6Address& addr) {
        // 先检查是否在拒绝列表中
        if (DeniedRanges.Contains(addr)) {
            return false;
        }

        // 再检查是否在允许列表中
        return AllowedRanges.Contains(addr) || AllowedRanges.IsEmpty();
    }

    TVector<TIpAddressRange> GetMatchingRules(const TIpv6Address& addr) {
        TVector<TIpAddressRange> rules;

        for (const auto& range : DeniedRanges) {
            if (range.Contains(addr)) {
                rules.push_back(range);
            }
        }

        for (const auto& range : AllowedRanges) {
            if (range.Contains(addr)) {
                rules.push_back(range);
            }
        }

        return rules;
    }
};
```

## 实现原理

### IP 地址表示
- **统一表示**：IPv4 和 IPv6 地址统一使用 128 位表示
- **类型区分**：通过类型标识符区分 IPv4 和 IPv6
- **自动转换**：支持 IPv4 映射到 IPv6 的自动转换

### 范围存储
- **起始-结束对**：使用起始和结束地址定义范围
- **范围验证**：确保起始地址不大于结束地址
- **类型一致性**：范围内的所有地址必须为相同类型

### 集合管理
- **不相交集合**：自动合并重叠和连续的范围
- **有序存储**：使用平衡二叉树存储范围
- **高效查询**：O(log n) 时间复杂度的成员查询

### 格式解析
- **CIDR 解析**：支持标准 CIDR 表示法（如 192.168.1.0/24）
- **范围解析**：支持连字符分隔的范围表示（如 10.0.0.0-10.0.0.255）
- **紧凑格式**：支持包含节点地址的紧凑 CIDR 格式
- **自动识别**：智能识别不同的输入格式

## 支持的格式

### CIDR 表示法
- **标准格式**：`192.168.1.0/24`
- **IPv6 CIDR**：`2001:db8::/32`
- **主机地址**：`192.168.1.100/32`

### 范围表示法
- **连字符分隔**：`10.0.0.0-10.0.0.255`
- **IPv6 范围**：`2001:db8::-2001:db8::ffff`

### 紧凑表示法
- **节点 + 网段**：`192.168.1.100/24`（自动对齐到网段边界）

### 单地址
- **IPv4 地址**：`192.168.1.100`
- **IPv6 地址**：`2001:db8::1`

## 性能特征

### 时间复杂度
- **构造操作**：O(1)
- **包含性检查**：O(log n) - 集合中范围的数量
- **范围合并**：O(log n)
- **迭代操作**：O(k) - k 为范围中的地址数量

### 空间复杂度
- **范围存储**：O(m) - m 为存储的范围数量
- **集合存储**：O(m) - 自动合并减少存储空间

### 优化策略
- **自动合并**：减少范围数量，提高查询效率
- **有序存储**：使用平衡树支持快速查找
- **延迟计算**：在需要时才计算范围大小

## 应用场景

### 网络安全
- **访问控制**：基于 IP 地址的访问权限控制
- **防火墙规则**：网络防火墙的 IP 规则管理
- **入侵检测**：识别可疑的 IP 地址范围
- **DDoS 防护**：基于 IP 的流量限制

### 网络管理
- **IP 地址规划**：管理网络中的 IP 地址分配
- **子网划分**：自动计算和划分子网
- **路由管理**：管理路由表中的网络范围
- **网络监控**：监控特定网络范围的流量

### 地理位置服务
- **IP 地理映射**：将 IP 范围映射到地理位置
- **内容分发**：基于地理位置的内容分发
- **合规检查**：检查 IP 地址的合规性
- **用户分析**：分析用户的地理分布

### 负载均衡
- **流量分发**：基于 IP 的负载均衡
- **会话保持**：基于 IP 的会话亲和性
- **故障转移**：IP 范围的故障转移
- **容量规划**：基于 IP 范围的容量规划

## 最佳实践

### 错误处理
```cpp
// 使用安全的解析函数
auto maybeRange = TIpAddressRange::TryFromCidrString("192.168.1.0/24");
if (maybeRange) {
    // 解析成功
    TIpAddressRange range = *maybeRange;
} else {
    // 解析失败，处理错误
    Cerr << "Invalid CIDR format" << Endl;
}

// 使用异常处理
try {
    TIpAddressRange range = TIpAddressRange::FromCidrString("192.168.1.0/24");
} catch (const TInvalidIpRangeException& e) {
    Cerr << "Invalid IP range: " << e.what() << Endl;
}
```

### 性能优化
```cpp
// 预构建常用的 IP 范围
class TCommonRanges {
public:
    static const TIpAddressRange& Private10() {
        static TIpAddressRange range = TIpAddressRange::FromCidrString("10.0.0.0/8");
        return range;
    }

    static const TIpAddressRange& Private192_168() {
        static TIpAddressRange range = TIpAddressRange::FromCidrString("192.168.0.0/16");
        return range;
    }
};

// 批量操作优化
TVector<TIpAddressRange> ranges;
ranges.reserve(1000);  // 预分配内存

for (const auto& cidr : cidrStrings) {
    ranges.push_back(TIpAddressRange::FromCidrString(cidr));
}

TIpRangeSet rangeSet;
rangeSet.Add(ranges);  // 批量添加
```

### 类型安全
```cpp
// 检查 IP 地址类型
TIpAddressRange range = TIpAddressRange::FromCidrString("192.168.1.0/24");

if (range.Type() == TIpv6Address::IPv4) {
    // 处理 IPv4 范围
} else if (range.Type() == TIpv6Address::IPv6) {
    // 处理 IPv6 范围
}

// 避免混合不同类型的地址
try {
    // 这会抛出异常，因为不能混合 IPv4 和 IPv6
    TIpAddressRange mixed("192.168.1.1", "2001:db8::1");
} catch (const TInvalidIpRangeException& e) {
    Cerr << "Cannot mix IPv4 and IPv6 addresses" << Endl;
}
```

## 扩展和集成

### 序列化支持
```cpp
// 支持自动序列化和反序列化
TIpAddressRange range = TIpAddressRange::FromCidrString("10.0.0.0/8");

// 保存到文件
TFileOutput out("range.dat");
range.Save(out);

// 从文件加载
TFileInput in("range.dat");
TIpAddressRange loaded;
loaded.Load(in);
```

### 哈希支持
```cpp
// 可以在哈希表中使用
THashMap<TIpAddressRange, TString> rangeDescriptions;
rangeDescriptions[TIpAddressRange::FromCidrString("10.0.0.0/8")] = "Private network";
rangeDescriptions[TIpAddressRange::FromCidrString("8.8.8.8/32")] = "Google DNS";
```

### 自定义比较器
```cpp
// 使用自定义比较器
struct TRangeSizeCompare {
    bool operator()(const TIpAddressRange& lhs, const TIpAddressRange& rhs) const {
        return lhs.Size() < rhs.Size();
    }
};

TSet<TIpAddressRange, TRangeSizeCompare> sortedBySize;
```