# 网络工具库

本模块提供网络编程相关的工具和封装，包括地址处理、套接字操作、网络接口管理等功能。

## 功能特性

### 网络地址处理
- IP 地址解析和格式化
- 端点地址管理
- 网络地址转换
- 地址验证

### 套接字操作
- 套接字封装
- I/O 向量处理
- 连接管理
- 异步 I/O 支持

### 网络接口
- 网络接口查询
- IP 地址绑定
- 路由信息获取
- 网络状态监控

## 主要组件

### 核心文件
- **address.h/cpp** - 网络地址处理
- **endpoint.h/cpp** - 网络端点管理
- **hostip.h/cpp** - 主机 IP 解析
- **ip.h/cpp** - IP 地址工具
- **socket.h** - 套接字封装（如果存在）

### 工具函数
- **init.h/cpp** - 网络库初始化
- **interface.h/cpp** - 网络接口操作
- **iovec.h/cpp** - I/O 向量处理

## 使用方法

### IP 地址处理
```cpp
#include "util/network/address.h"

// 创建 IPv4 地址
TIPv4Address addr("192.168.1.1");

// 创建 IPv6 地址
TIPv6Address addr6("2001:db8::1");

// 地址解析
TNetworkAddress resolved = ResolveHost("example.com", 80);

// 地址格式化
TString str = addr.ToString();  // "192.168.1.1"

// 地址比较
if (addr1 == addr2) {
    // 地址相同
}
```

### 网络端点
```cpp
#include "util/network/endpoint.h"

// 创建端点
TNetworkEndpoint endpoint("192.168.1.1", 8080);

// 带协议的端点
TNetworkEndpoint endpoint2("tcp://example.com:443");

// 获取地址和端口
TString host = endpoint.GetHost();
ui16 port = endpoint.GetPort();

// 端点转换
struct sockaddr_storage storage;
endpoint.ToSockaddr(&storage);
```

### 主机名解析
```cpp
#include "util/network/hostip.h"

// 解析主机名
std::vector<TString> ips = ResolveHost("example.com");

// 获取本地 IP
TString localIP = GetLocalIP("eth0");

// 检查 IP 是否有效
bool isValid = IsValidIP("192.168.1.1");
```

### 网络接口
```cpp
#include "util/network/interface.h"

// 获取所有网络接口
std::vector<TNetworkInterface> interfaces = GetNetworkInterfaces();

// 查找特定接口
TNetworkInterface eth0 = GetInterfaceByName("eth0");

// 获取接口 IP
std::vector<TString> ips = eth0.GetIPAddresses();

// 检查接口状态
if (eth0.IsUp()) {
    // 接口已启用
}
```

### I/O 向量处理
```cpp
#include "util/network/iovec.h"

// 创建 I/O 向量数组
std::vector<iovec> iov(3);

iov[0].iov_base = data1;
iov[0].iov_len = len1;

iov[1].iov_base = data2;
iov[1].iov_len = len2;

iov[2].iov_base = data3;
iov[2].iov_len = len3;

// 使用 I/O 向量读写
ssize_t written = writev(sockfd, iov.data(), iov.size());
```

### 网络初始化
```cpp
#include "util/network/init.h"

// 初始化网络库（Windows 需要调用）
InitializeNetwork();

// 清理网络库
CleanupNetwork();
```

## 地址格式支持

### IPv4 地址
- 点分十进制：`192.168.1.1`
 CIDR 表示法：`192.168.1.0/24`

### IPv6 地址
- 标准格式：`2001:db8::1`
- 压缩格式：`::1`
- IPv4 映射：`::ffff:192.168.1.1`

### URL 格式
- TCP: `tcp://host:port`
- UDP: `udp://host:port`
- SSL: `ssl://host:port`

## 错误处理

### 异常类型
```cpp
#include "util/network/errors.h"

try {
    TNetworkAddress addr("invalid-address");
} catch (const TNetworkException& e) {
    // 处理网络错误
    std::cerr << "Network error: " << e.what() << std::endl;
}
```

### 错误码
- `NE_RESOLVE_FAILED` - 域名解析失败
- `NE_INVALID_ADDRESS` - 无效的地址格式
- `NE_SOCKET_ERROR` - 套接字错误
- `NE_CONNECTION_FAILED` - 连接失败

## 性能特性

### 优化策略
- 地址解析缓存
- 批量操作支持
- 零拷贝设计
- 异步 I/O 支持

### 性能指标
- 地址解析：~100μs
- 地址格式化：~10μs
- 套接字操作：系统调用级别

## 测试

### 单元测试
```bash
# 运行所有网络测试
./ut/network_ut

# 运行地址测试
./ut/network_ut --gtest_filter="AddressTest.*"

# 运行端点测试
./ut/network_ut --gtest_filter="EndpointTest.*"
```

### 集成测试
```bash
# 测试实际网络操作
./test/network_integration.py
```

## 最佳实践

1. **地址处理**
   - 使用 TNetworkAddress 而非原始字符串
   - 缓存解析结果
   - 验证地址有效性

2. **错误处理**
   - 检查所有网络操作的返回值
   - 处理超时情况
   - 实现重试机制

3. **性能优化**
   - 使用连接池
   - 批量处理请求
   - 避免频繁的域名解析

## 平台支持

### Linux 支持
- 完整的网络功能
- 高级特性支持
- 性能优化

### macOS 支持
- 基础网络功能
- 兼容性保证

### Windows 支持
- Winsock 封装
- Windows 特定优化

## 配置选项

### 编译时配置
```cpp
// 启用 IPv6
#define Y_ENABLE_IPV6 1

// 启用异步 I/O
#define Y_ENABLE_ASYNC_IO 1
```

## 安全考虑

1. **地址验证**
   - 防止恶意输入
   - 验证地址范围
   - 处理特例地址

2. **连接安全**
   - 使用 SSL/TLS
   - 验证证书
   - 实现超时机制

## 依赖项

- 标准 C++ 库
- 平台网络库
- C++11 或更高版本

## 版本历史

- v3.0: 添加 IPv6 支持
- v2.5: 性能优化
- v2.0: 重构 API
- v1.0: 初始版本