# Random Provider - 随机数生成器

随机数生成器库为 YTsaurus 系统提供统一的随机数和 UUID 生成服务，支持确定性测试和多种随机算法。

## 🎯 核心功能

### 随机数提供者接口

```cpp
#include <library/cpp/random_provider/random_provider.h>

// 随机数提供者接口
class IRandomProvider: public TThrRefBase, public TCommonRNG<ui64, IRandomProvider> {
public:
    virtual TGUID GenGuid() noexcept = 0;
    virtual TGUID GenUuid4() noexcept = 0;
    virtual ui64 GenRand() noexcept = 0;
};
```

### 基础使用

```cpp
// 创建默认随机数提供者（系统熵源）
TIntrusivePtr<IRandomProvider> provider = CreateDefaultRandomProvider();

// 生成随机数
ui64 randomValue = provider->GenRand();

// 生成 GUID（Microsoft 风格）
TGUID guid = provider->GenGuid();

// 生成 UUID v4（RFC 4122 标准）
TGUID uuid4 = provider->GenUuid4();

// 作为随机数生成器使用
ui32 random32 = provider->Uniform(1000);  // 0-999
double randomDouble = provider->GenRandReal();  // [0.0, 1.0)
```

### 确定性随机数（用于测试）

```cpp
// 创建确定性随机数提供者
TIntrusivePtr<IRandomProvider> deterministic = CreateDeterministicRandomProvider(12345);

// 相同种子产生相同的序列
ui64 value1 = deterministic->GenRand();
ui64 value2 = deterministic->GenRand();

// 创建相同种子的另一个提供者
TIntrusivePtr<IRandomProvider> sameSeed = CreateDeterministicRandomProvider(12345);
// value3 == value1, value4 == value2
ui64 value3 = sameSeed->GenRand();
ui64 value4 = sameSeed->GenRand();
```

## 🚀 使用场景

### 1. 唯一标识符生成

```cpp
// 分布式系统中的节点标识
class DistributedNode {
    TGUID nodeId;
    TIntrusivePtr<IRandomProvider> randomProvider;

public:
    DistributedNode(TIntrusivePtr<IRandomProvider> provider)
        : randomProvider(provider)
        , nodeId(randomProvider->GenUuid4()) {}

    TGUID GetNodeId() const { return nodeId; }
};

// 事务 ID 生成
TGUID GenerateTransactionId(TIntrusivePtr<IRandomProvider> provider) {
    return provider->GenUuid4();
}
```

### 2. 负载均衡和随机选择

```cpp
// 随机负载均衡器
template<typename T>
class RandomLoadBalancer {
    TVector<T> servers;
    TIntrusivePtr<IRandomProvider> randomProvider;

public:
    RandomLoadBalancer(TIntrusivePtr<IRandomProvider> provider)
        : randomProvider(provider) {}

    void AddServer(const T& server) {
        servers.push_back(server);
    }

    T SelectServer() {
        if (servers.empty()) {
            throw yexception() << "No servers available";
        }
        size_t index = randomProvider->Uniform(servers.size());
        return servers[index];
    }
};
```

### 3. 随机采样

```cpp
// 水库采样算法
template<typename T>
class ReservoirSampler {
    TVector<T> samples;
    size_t maxSamples;
    size_t count = 0;
    TIntrusivePtr<IRandomProvider> randomProvider;

public:
    ReservoirSampler(size_t maxSamples, TIntrusivePtr<IRandomProvider> provider)
        : maxSamples(maxSamples)
        , randomProvider(provider) {}

    void Add(const T& item) {
        if (count < maxSamples) {
            samples.push_back(item);
        } else {
            // 随机替换
            size_t index = randomProvider->Uniform(count + 1);
            if (index < maxSamples) {
                samples[index] = item;
            }
        }
        ++count;
    }

    const TVector<T>& GetSamples() const { return samples; }
};
```

### 4. 密钥和令牌生成

```cpp
// 安全令牌生成
class TokenGenerator {
    TIntrusivePtr<IRandomProvider> randomProvider;
    static constexpr size_t TOKEN_SIZE = 32;

public:
    TokenGenerator(TIntrusivePtr<IRandomProvider> provider)
        : randomProvider(provider) {}

    TString GenerateSecureToken() {
        TString token;
        token.reserve(TOKEN_SIZE);

        for (size_t i = 0; i < TOKEN_SIZE; ++i) {
            // 生成可打印字符
            char c = '!' + randomProvider->Uniform('~' - '!' + 1);
            token += c;
        }

        return token;
    }

    TGUID GenerateSessionId() {
        return randomProvider->GenUuid4();
    }
};
```

### 5. 随机延迟和抖动

```cpp
// 带抖动的重试延迟
class JitteredDelay {
    TIntrusivePtr<IRandomProvider> randomProvider;
    TDuration baseDelay;

public:
    JitteredDelay(TDuration baseDelay, TIntrusivePtr<IRandomProvider> provider)
        : baseDelay(baseDelay)
        , randomProvider(provider) {}

    TDuration GetNextDelay(int attempt) {
        // 指数退避 + 随机抖动
        TDuration exponential = baseDelay * (1 << min(attempt, 10));
        double jitter = randomProvider->GenRandReal();  // [0.0, 1.0)
        return TDuration::MicroSeconds(exponential.MicroSeconds() * (0.5 + jitter));
    }
};
```

## 📊 随机数质量

### 统计特性
- **均匀分布**: 确保所有值以相等概率出现
- **长周期**: 确定性随机数生成器具有长周期
- **低相关性**: 连续生成的随机数之间相关性极低
- **高熵**: 系统随机数使用高质量熵源

### 安全特性
- **密码学安全**: 默认提供者使用系统安全随机数生成器
- **防预测**: 确定性随机数仅在测试中使用
- **熵源多样化**: 结合多种熵源提高随机性质量

## ⚡ 性能优化

### 缓存优化
```cpp
// 重用随机数提供者实例
class RandomUtils {
    static TIntrusivePtr<IRandomProvider> GetProvider() {
        static TIntrusivePtr<IRandomProvider> provider = CreateDefaultRandomProvider();
        return provider;
    }

public:
    static ui64 FastRandom() {
        static thread_local TIntrusivePtr<IRandomProvider> threadProvider;
        if (!threadProvider) {
            threadProvider = CreateDefaultRandomProvider();
        }
        return threadProvider->GenRand();
    }
};
```

### 批量生成
```cpp
// 批量 UUID 生成
TVector<TGUID> GenerateBatchUuids(size_t count, TIntrusivePtr<IRandomProvider> provider) {
    TVector<TGUID> guids;
    guids.reserve(count);

    for (size_t i = 0; i < count; ++i) {
        guids.push_back(provider->GenUuid4());
    }

    return guids;
}
```

## 🔗 相关模块

- **guid**: GUID 处理和转换
- **crypto**: 密码学相关功能
- **testing**: 测试框架中的随机化
- **netliba**: 网络中的随机连接选择

## 📈 最佳实践

### 1. 选择合适的随机数类型

```cpp
// 安全敏感场景：使用默认提供者
TGUID sessionId = CreateDefaultRandomProvider()->GenUuid4();

// 性能敏感场景：使用确定性提供者（仅在测试中）
auto testProvider = CreateDeterministicRandomProvider(seed);

// 分布式唯一标识：总是使用 UUID v4
TGUID distributedId = provider->GenUuid4();
```

### 2. 避免常见错误

```cpp
// 错误：重复创建提供者
for (int i = 0; i < 1000; ++i) {
    auto provider = CreateDefaultRandomProvider();  // 性能差
    values[i] = provider->GenRand();
}

// 正确：重用提供者
auto provider = CreateDefaultRandomProvider();
for (int i = 0; i < 1000; ++i) {
    values[i] = provider->GenRand();
}
```

### 3. 测试中的确定性

```cpp
// 测试基类提供确定性随机数
class RandomTestBase {
protected:
    TIntrusivePtr<IRandomProvider> randomProvider;

public:
    RandomTestBase(ui64 testSeed = 12345)
        : randomProvider(CreateDeterministicRandomProvider(testSeed)) {}

    ui64 NextRandom() {
        return randomProvider->GenRand();
    }
};
```

随机数生成器库为 YTsaurus 提供了可靠的随机数和唯一标识符生成能力，支持从系统安全随机到测试确定性随机数的各种需求。