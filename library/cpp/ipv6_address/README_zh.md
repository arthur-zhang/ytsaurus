# IPv6 地址处理库

## 项目概述

IPv6 地址处理库提供了统一的 IP 地址表示和操作功能，支持 IPv4 和 IPv6 地址的无缝处理。该库使用 128 位整数统一表示 IP 地址，提供了丰富的构造、转换、比较和序列化功能，为网络应用程序提供强大的 IP 地址处理能力。

## 核心特性

### 统一地址表示
- **IPv4/IPv6 统一**：使用 128 位整数统一表示两种 IP 地址
- **类型区分**：通过枚举类型区分 IPv4 和 IPv6 地址
- **自动转换**：支持 IPv4 到 IPv6 的映射和转换
- **作用域支持**：支持 IPv6 地址的作用域 ID

### 丰富的构造方式
- **字节构造**：支持从字节序列构造地址
- **字符串解析**：支持多种格式的地址字符串解析
- **网络结构**：支持从 sockaddr 等网络结构构造
- **数值构造**：支持从 128 位整数直接构造

### 完整的操作接口
- **比较运算**：支持所有比较操作符
- **类型检查**：提供地址类型检查和验证
- **格式转换**：支持多种字符串格式的输出
- **网络集成**：与系统网络 API 无缝集成

## 主要类

### TIpv6Address
核心的 IP 地址类，统一处理 IPv4 和 IPv6 地址。

#### 构造方式
```cpp
// 默认构造
TIpv6Address addr1;

// IPv4 地址构造（点分十进制）
TIpv6Address ipv4Addr(192, 168, 1, 1);

// IPv6 地址构造（16 位段）
TIpv6Address ipv6Addr(0x2001, 0xdb8, 0, 0, 0, 0, 0, 0x1);

// 带作用域 ID 的 IPv6 地址
TIpv6Address ipv6WithScope(0xfe80, 0, 0, 0, 0, 0, 0, 0x1, 1); // 作用域 ID = 1

// 从字符串构造
bool ok;
TIpv6Address fromString = TIpv6Address::FromString("192.168.1.1", ok);
TIpv6Address fromV6String = TIpv6Address::FromString("2001:db8::1", ok);

// 从网络结构构造
sockaddr_in addr4;
// ... 填充 addr4
TIpv6Address fromSockaddr(addr4);

sockaddr_in6 addr6;
// ... 填充 addr6
TIpv6Address fromSockaddr6(addr6);
```

#### 常用操作
```cpp
TIpv6Address addr = TIpv6Address::FromString("192.168.1.1");

// 基本属性检查
bool isValid = addr.IsValid();        // 是否为有效地址
bool isNull = addr.IsNull();          // 是否为空地址
bool isIpv6 = addr.IsIpv6();          // 是否为 IPv6 地址

// 类型转换
ui128 numericValue = static_cast<ui128>(addr);  // 转换为数值
TIpv6Address::TIpType type = addr.Type();       // 获取地址类型

// 比较操作
TIpv6Address otherAddr = TIpv6Address::FromString("192.168.1.2");
bool isEqual = (addr == otherAddr);
bool isLess = (addr < otherAddr);
bool isGreater = (addr > otherAddr);

// 字符串转换
bool ok;
TString str = addr.ToString(&ok);    // 转换为字符串
TString strWithScope = addr.ToString(true, &ok);  // 包含作用域 ID

// 作用域 ID 操作
if (addr.IsIpv6()) {
    addr.SetScopeId(1);               // 设置作用域 ID
    ui32 scopeId = addr.ScopeId();    // 获取作用域 ID
}
```

### THostAddressAndPort
主机地址和端口的组合类，用于表示网络端点。

```cpp
// 构造地址和端口组合
TIpv6Address ip = TIpv6Address::FromString("192.168.1.1");
THostAddressAndPort endpoint(ip, 8080);

// 检查有效性
bool isValid = endpoint.IsValid();

// 字符串转换
TString endpointStr = endpoint.ToString();

// 支持作用域 ID 选项
THostAddressAndPortPrintOptions options;
options.PrintScopeId = true;
TString strWithScope = endpoint.ToString(options);
```

## 使用示例

### 基本地址操作
```cpp
#include <library/cpp/ipv6_address/ipv6_address.h>

void BasicAddressOperations() {
    // 创建不同类型的地址
    TIpv6Address localhost = TIpv6Address(127, 0, 0, 1);
    TIpv6Address ipv6Loopback = TIpv6Address(0, 0, 0, 0, 0, 0, 0, 0, 1);

    // 从字符串构造
    bool ok;
    TIpv6Address googleDns = TIpv6Address::FromString("8.8.8.8", ok);
    if (ok) {
        Cout << "Successfully parsed Google DNS: " << googleDns.ToString() << Endl;
    }

    TIpv6Address ipv6Google = TIpv6Address::FromString("2001:4860:4860::8888", ok);
    if (ok) {
        Cout << "Successfully parsed Google IPv6 DNS: " << ipv6Google.ToString() << Endl;
    }

    // 类型检查
    if (googleDns.IsIpv6()) {
        Cout << "Google DNS is IPv6" << Endl;
    } else {
        Cout << "Google DNS is IPv4" << Endl;
    }

    // 比较
    TIpv6Address addr1 = TIpv6Address::FromString("192.168.1.1", ok);
    TIpv6Address addr2 = TIpv6Address::FromString("192.168.1.2", ok);

    if (addr1 < addr2) {
        Cout << addr1.ToString() << " is less than " << addr2.ToString() << Endl;
    }
}
```

### 地址转换和映射
```cpp
void AddressConversion() {
    // IPv4 到 IPv6 映射
    TIpv6Address ipv4Addr = TIpv6Address::FromString("192.168.1.1");
    TIpv6Address mapped = ipv4Addr.TryToExtractIpv4From6();

    if (mapped.IsValid()) {
        Cout << "Extracted IPv4: " << mapped.ToString() << Endl;
    }

    // 检查是否为 IPv4 映射到 IPv6
    TIpv6Address v4Mapped = TIpv6Address::FromString("::ffff:192.168.1.1", ok);
    if (v4Mapped.Isv4MappedTov6()) {
        Cout << "Address is IPv4-mapped IPv6" << Endl;
    }

    // 地址标准化
    TIpv6Address normalized = v4Mapped.Normalized();
    Cout << "Normalized: " << normalized.ToString() << Endl;
}
```

### 网络编程集成
```cpp
void NetworkIntegration() {
    TIpv6Address addr = TIpv6Address::FromString("192.168.1.100");
    ui16 port = 8080;

    // 转换为 sockaddr 结构
    sockaddr_in addr4;
    sockaddr_in6 addr6;
    const sockaddr* sockAddrPtr;
    socklen_t sockAddrSize;

    addr.ToSockaddrAndSocklen(addr4, addr6, sockAddrPtr, sockAddrSize, port);

    // 创建网络地址对象
    NAddr::IRemoteAddr* remoteAddr = ToIRemoteAddr(addr, port);
    if (remoteAddr) {
        // 使用 remoteAddr 进行网络操作
        Cout << "Created remote address successfully" << Endl;
        delete remoteAddr;
    }

    // 转换为系统地址结构
    if (addr.IsIpv6()) {
        in6_addr in6;
        addr.ToIn6Addr(in6);
        // 使用 in6 地址结构
    } else {
        in_addr in4;
        addr.ToInAddr(in4);
        // 使用 in4 地址结构
    }
}
```

### 地址解析
```cpp
void AddressParsing() {
    // 解析主机和端口
    bool ok;
    auto [endpoint, hostname, port] = ParseHostAndMayBePortFromString(
        "192.168.1.1:8080", 80, ok);

    if (ok && endpoint.IsValid()) {
        Cout << "Parsed endpoint: " << endpoint.ToString() << Endl;
    }

    // 解析 IPv6 地址
    std::tie(endpoint, hostname, port) = ParseHostAndMayBePortFromString(
        "[2001:db8::1]:443", 443, ok);

    if (ok && endpoint.IsValid()) {
        Cout << "Parsed IPv6 endpoint: " << endpoint.ToString() << Endl;
    }

    // 解析主机名（返回需要解析的主机名）
    std::tie(endpoint, hostname, port) = ParseHostAndMayBePortFromString(
        "example.com:80", 80, ok);

    if (ok && !hostname.empty()) {
        Cout << "Need to resolve hostname: " << hostname << Endl;
        Cout << "Port: " << port << Endl;
    }
}
```

### 地址集合操作
```cpp
void AddressSetOperations() {
    // 创建地址集合
    TIpv6AddressesSet addressSet;

    // 添加地址
    addressSet.insert(TIpv6Address::FromString("192.168.1.1", ok));
    addressSet.insert(TIpv6Address::FromString("192.168.1.2", ok));
    addressSet.insert(TIpv6Address::FromString("2001:db8::1", ok));

    // 查找地址
    TIpv6Address target = TIpv6Address::FromString("192.168.1.1", ok);
    auto it = addressSet.find(target);

    if (it != addressSet.end()) {
        Cout << "Address found in set" << Endl;
    }

    // 遍历地址集合
    for (const auto& addr : addressSet) {
        Cout << "Address: " << addr.ToString() << Endl;
    }
}
```

### 序列化支持
```cpp
void SerializationExample() {
    TIpv6Address addr = TIpv6Address::FromString("2001:db8::1");

    // 保存到流
    TStringOutput out;
    addr.Save(&out);

    // 从流加载
    TStringInput in(out.Str());
    TIpv6Address loaded;
    loaded.Load(&in);

    Cout << "Original: " << addr.ToString() << Endl;
    Cout << "Loaded: " << loaded.ToString() << Endl;
}
```

## 实现原理

### 统一表示法
- **128 位存储**：所有地址都使用 128 位整数存储
- **类型标记**：使用枚举值区分 IPv4 和 IPv6
- **作用域支持**：IPv6 地址支持作用域 ID
- **零成本抽象**：编译时优化，运行时开销最小

### 地址编码
- **IPv4 编码**：存储在 128 位整数的低 32 位
- **IPv6 编码**：直接使用完整的 128 位空间
- **映射地址**：IPv4 映射到 IPv6 使用标准映射格式
- **比较策略**：IPv4 地址在比较时优先级更高

### 字符串解析
- **格式识别**：自动识别 IPv4 和 IPv6 格式
- **错误处理**：提供安全的解析接口
- **标准化**：输出标准化的地址格式
- **作用域处理**：支持 IPv6 作用域 ID 的解析和输出

## 支持的格式

### IPv4 格式
- **点分十进制**：`192.168.1.1`
- **数值构造**：四个 8 位参数
- **网络字节序**：与标准网络 API 兼容

### IPv6 格式
- **标准表示**：`2001:db8::1`
- **完整表示**：`2001:0db8:0000:0000:0000:0000:0000:0001`
- **压缩零**：使用 `::` 压缩连续的零
- **作用域 ID**：`fe80::1%eth0`

### 组合格式
- **地址和端口**：`192.168.1.1:8080`
- **IPv6 和端口**：`[2001:db8::1]:443`
- **主机名解析**：`example.com:80`

## 性能特征

### 时间复杂度
- **构造操作**：O(1)
- **比较操作**：O(1)
- **字符串转换**：O(n) - n 为地址字符串长度
- **哈希计算**：O(1)

### 空间复杂度
- **地址存储**：固定 16 字节 + 4 字节类型信息
- **字符串输出**：最多 45 字符（IPv6 完整格式）
- **序列化大小**：固定 20 字节

### 内存效率
- **对齐优化**：16 字节对齐，提高缓存效率
- **无动态分配**：构造和析构不涉及堆分配
- **拷贝友好**：支持零拷贝的移动语义

## 应用场景

### 网络编程
- **服务端开发**：处理客户端连接地址
- **客户端开发**：连接到远程服务器
- **代理服务**：转发网络请求
- **负载均衡**：基于地址的流量分发

### 网络安全
- **访问控制**：基于 IP 的访问权限控制
- **防火墙规则**：定义网络访问规则
- **入侵检测**：识别可疑的网络地址
- **DDoS 防护**：基于地址的流量限制

### 网络监控
- **流量分析**：统计网络流量分布
- **连接跟踪**：监控网络连接状态
- **性能监控**：分析网络性能指标
- **故障诊断**：定位网络问题

### 网络工具
- **网络扫描**：端口扫描和网络发现
- **路由分析**：分析网络路由路径
- **DNS 解析**：域名到地址的解析
- **网络配置**：网络接口配置管理

## 最佳实践

### 错误处理
```cpp
// 使用安全的字符串解析
bool ok;
TIpv6Address addr = TIpv6Address::FromString(userInput, ok);
if (!ok || !addr.IsValid()) {
    Cerr << "Invalid IP address: " << userInput << Endl;
    return;
}

// 检查地址类型
if (addr.IsIpv6()) {
    // 处理 IPv6 特定逻辑
} else {
    // 处理 IPv4 特定逻辑
}
```

### 性能优化
```cpp
// 预定义常用地址
constexpr TIpv6Address LOCALHOST = Get127001();
constexpr TIpv6Address IPV6_LOOPBACK = Get1();

// 使用 const引用避免拷贝
void ProcessAddress(const TIpv6Address& addr) {
    // 处理地址
}

// 批量处理
void ProcessAddresses(const TVector<TIpv6Address>& addresses) {
    for (const TIpv6Address& addr : addresses) {
        // 处理每个地址
    }
}
```

### 类型安全
```cpp
// 检查地址有效性
if (!addr.IsValid()) {
    // 处理无效地址
}

// 检查地址类型
switch (addr.Type()) {
    case TIpv6Address::Ipv4:
        // IPv4 处理逻辑
        break;
    case TIpv6Address::Ipv6:
        // IPv6 处理逻辑
        break;
    default:
        // 错误处理
        break;
}

// 安全的地址比较
if (addr == otherAddr && addr.Type() == otherAddr.Type()) {
    // 类型和值都相同
}
```

### 调试和日志
```cpp
// 调试输出
void DebugPrintAddress(const TIpv6Address& addr) {
    bool ok;
    TString str = addr.ToString(&ok);
    if (ok) {
        Cout << "Address: " << str
             << " (Type: " << addr.Type()
             << ", Valid: " << addr.IsValid() << ")" << Endl;
    } else {
        Cout << "Invalid address" << Endl;
    }
}

// 结构化日志
void LogAddress(const TIpv6Address& addr, const TString& context) {
    LOG_INFO_S(context << " - IP: " << addr.ToString()
                     << ", Type: " << (addr.IsIpv6() ? "IPv6" : "IPv4"));
}
```