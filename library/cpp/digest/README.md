# digest 哈希和摘要算法模块

[digest](.) 是 YTsaurus 中专门提供各种哈希和摘要算法的 C++ 库集合。该模块包含了从经典的 MD5 到现代的 Argon2 密码哈希函数，以及多种高性能的非密码学哈希算法，为不同场景提供最佳的哈希解决方案。

## 📋 项目描述

`digest` 模块提供了一套完整的哈希和摘要算法工具集，涵盖了密码学哈希、校验和哈希、高性能通用哈希等多种类型。每个子模块都专注于特定的哈希算法，为开发者提供最适合其应用场景的选择。

### 核心价值

- **全面的算法支持**：从传统到现代的多种哈希算法
- **高性能实现**：针对不同平台优化的高效实现
- **安全可靠**：密码学算法采用行业标准实现
- **易于使用**：统一的接口设计，简单易用的API
- **跨平台兼容**：支持多种操作系统和CPU架构

## 🏗️ 模块架构

### 子模块概览

```
digest/
├── md5/          # MD5 哈希算法
├── crc32c/       # CRC32C 校验和算法
├── murmur/       # MurmurHash 非密码学哈希
├── argonish/     # Argon2 密码哈希函数
├── lower_case/   # 大小写敏感哈希
├── old_crc/      # 传统 CRC 算法
└── sfh/          # SuperFastHash 快速哈希
```

## 🚀 核心模块详解

### 1. MD5 模块

**算法类型**：密码学哈希
**输出长度**：128位 (16字节)
**用途**：数据完整性校验、文件指纹、数据去重

#### 核心接口
```cpp
class MD5 {
public:
    // 构造和初始化
    MD5();
    void Init();

    // 增量更新
    MD5& Update(const void* data, size_t len);
    MD5& Update(TStringBuf data);
    MD5& Update(const TArrayRef<const ui8> data);

    // 最终化
    void Pad();
    ui8* Final(ui8[16]);              // 16字节原始输出
    char* End(char* buf);             // 32字符十六进制字符串
    char* End_b64(char* buf);         // Base64编码
    ui64 EndHalfMix();                // 8字节混合输出

    // 流式处理
    MD5& Update(IInputStream* in);

    // 静态便捷函数
    static TString Calc(TStringBuf data);           // 十六进制输出
    static TString CalcRaw(TStringBuf data);        // 原始输出
    static TString File(const TString& filename);   // 文件哈希
    static ui64 CalcHalfMix(TStringBuf data);       // 混合哈希

    // 验证函数
    static bool IsMD5(TStringBuf data);
};
```

#### 使用示例
```cpp
#include <library/cpp/digest/md5/md5.h>

// 基础哈希计算
TString data = "Hello, World!";
TString hash = MD5::Calc(data);
Cout << "MD5: " << hash << Endl;  // 32字符十六进制

// 流式处理
MD5 md5;
md5.Update("Part1, ");
md5.Update("Part2!");
char result[33];
Cout << "Stream MD5: " << md5.End(result) << Endl;

// 文件哈希
TString fileHash = MD5::File("/path/to/file.txt");
Cout << "File MD5: " << fileHash << Endl;

// 原始输出
TString rawHash = MD5::CalcRaw(data);
Cout << "Raw MD5 length: " << rawHash.size() << Endl;  // 16字节

// 8字节混合哈希（用于哈希表）
ui64 shortHash = MD5::CalcHalfMix(data);
```

### 2. CRC32C 模块

**算法类型**：校验和算法
**输出长度**：32位
**特点**：硬件加速、线程安全

#### 核心接口
```cpp
// 基础CRC32C计算
ui32 Crc32c(const void* p, size_t size) noexcept;

// 扩展CRC32C计算
ui32 Crc32cExtend(ui32 init, const void* data, size_t n) noexcept;

// CRC32C合并
ui32 Crc32cCombine(ui32 blockACrc, ui32 blockBCrc, size_t blockBSize) noexcept;

// 硬件支持检测
bool HaveFastCrc32c() noexcept;
```

#### 使用示例
```cpp
#include <library/cpp/digest/crc32c/crc32c.h>

// 基础校验和计算
TString data = "CRC32C test data";
ui32 crc = Crc32c(data.data(), data.size());
Cout << "CRC32C: " << Hex(crc) << Endl;

// 分块计算和合并
TString part1 = data.substr(0, 10);
TString part2 = data.substr(10);
ui32 crc1 = Crc32c(part1.data(), part1.size());
ui32 crc2 = Crc32c(part2.data(), part2.size());
ui32 combinedCrc = Crc32cCombine(crc1, crc2, part2.size());

// 检查硬件支持
if (HaveFastCrc32c()) {
    Cout << "Hardware-accelerated CRC32C available" << Endl;
}
```

### 3. MurmurHash 模块

**算法类型**：非密码学哈希
**输出长度**：32位或64位
**特点**：高性能、良好的分布特性

#### 核心模板
```cpp
template <class T>
class TMurmurHash2A {
public:
    explicit TMurmurHash2A(TValue seed = 0);

    // 增量更新
    TMurmurHash2A& Update(const void* buf, size_t len) noexcept;

    // 获取最终哈希值
    TValue Value() const noexcept;
};
```

#### 使用示例
```cpp
#include <library/cpp/digest/murmur/murmur.h>

// 32位 MurmurHash
TMurmurHash2A<ui32> hasher32(0x12345678);
hasher32.Update("data part 1", 12);
hasher32.Update("data part 2", 12);
ui32 hash32 = hasher32.Value();

// 64位 MurmurHash
TMurmurHash2A<ui64> hasher64(0x123456789ABCDEF0);
hasher64.Update(largeData, largeDataSize);
ui64 hash64 = hasher64.Value();

Cout << "MurmurHash32: " << Hex(hash32) << Endl;
Cout << "MurmurHash64: " << Hex(hash64) << Endl;
```

### 4. Argonish (Argon2) 模块

**算法类型**：密码学密钥派生函数
**算法变体**：Argon2d, Argon2i, Argon2id
**特点**：抗GPU/ASIC攻击、可调参数

#### 算法变体说明

- **Argon2d**：数据依赖版本，最大化抗GPU攻击
- **Argon2i**：数据独立版本，最大化抗侧信道攻击
- **Argon2id**：混合版本，平衡两种威胁模型

#### 核心接口
```cpp
namespace NArgonish {
    enum class EArgon2Type : ui32 {
        Argon2d = 0,
        Argon2i = 1,
        Argon2id = 2
    };

    class IArgon2Base {
    public:
        virtual ~IArgon2Base();
        virtual void Hash(const void* pwd, size_t pwdlen,
                         const void* salt, size_t saltlen,
                         void* out, size_t outlen) = 0;
    };

    class TArgon2Factory {
    public:
        THolder<IArgon2Base> Create(EArgon2Type type,
                                   ui32 tcost,    // 时间成本
                                   ui32 mcost,    // 内存成本 (KB)
                                   ui32 threads); // 并行线程数
    };
}
```

#### 高性能特性
- **CPU指令集优化**：支持 SSE2, SSSE3, SSE41, AVX2
- **多线程支持**：使用 OpenMP 而非 pthread
- **编译时优化**：constexpr 和模板优化无用分支
- **向量化 Blake2B**：包括 AVX2 优化版本

#### 使用示例
```cpp
#include <library/cpp/digest/argonish/argon2.h>

// 创建 Argon2 实例
NArgonish::TArgon2Factory factory;
ui32 tcost = 2;        // 迭代次数
ui32 mcost = 1024;     // 内存成本 (1MB)
ui32 threads = 4;      // 并行线程数

auto argon2d = factory.Create(NArgonish::EArgon2Type::Argon2d,
                             tcost, mcost, threads);

// 计算密码哈希
TString password = "my_secure_password";
TString salt = "random_salt_value";
ui8 output[32];  // 输出长度

argon2d->Hash(password.data(), password.size(),
              salt.data(), salt.size(),
              output, sizeof(output));

// 输出十六进制结果
TString hexOutput;
hexOutput.reserve(sizeof(output) * 2);
for (ui8 byte : output) {
    hexOutput += Sprintf("%02x", byte);
}
Cout << "Argon2d hash: " << hexOutput << Endl;
```

### 5. SuperFastHash (SFH) 模块

**算法类型**：非密码学快速哈希
**输出长度**：32位
**特点**：极高性能，适合哈希表

#### 核心接口
```cpp
inline ui32 SuperFastHash(const void* d, size_t l) noexcept;
```

#### 使用示例
```cpp
#include <library/cpp/digest/sfh/sfh.h>

// 快速哈希计算
TString data = "SuperFastHash test";
ui32 hash = SuperFastHash(data.data(), data.size());

// 用于哈希表键
struct TStringHash {
    size_t operator()(const TString& key) const {
        return SuperFastHash(key.data(), key.size());
    }
};

THashMap<TString, int, TStringHash> hashMap;
hashMap["key1"] = 1;
hashMap["key2"] = 2;
```

## 🎯 应用场景

### 1. 数据完整性验证

#### 文件校验
```cpp
// MD5 用于文件完整性检查
TString calculateFileMD5(const TString& filePath) {
    return MD5::File(filePath);
}

bool verifyFileIntegrity(const TString& filePath, const TString& expectedMD5) {
    TString actualMD5 = calculateFileMD5(filePath);
    return actualMD5 == expectedMD5;
}
```

#### 网络传输校验
```cpp
// CRC32C 用于网络数据包校验
class NetworkPacket {
private:
    TString data;
    ui32 checksum;

public:
    void finalize() {
        checksum = Crc32c(data.data(), data.size());
    }

    bool verify() const {
        return Crc32c(data.data(), data.size()) == checksum;
    }
};
```

### 2. 密码学应用

#### 密码哈希
```cpp
// Argon2 用于密码存储
TString hashPassword(const TString& password, const TString& salt) {
    NArgonish::TArgon2Factory factory;
    auto argon2id = factory.Create(NArgonish::EArgon2Type::Argon2id, 3, 65536, 4);

    ui8 output[32];
    argon2id->Hash(password.data(), password.size(),
                   salt.data(), salt.size(),
                   output, sizeof(output));

    return TString(reinterpret_cast<char*>(output), sizeof(output));
}
```

#### 密钥派生
```cpp
// 从主密码派生多个密钥
TString deriveKey(const TString& masterPassword,
                  const TString& purpose,
                  size_t keyLength) {
    auto argon2id = factory.Create(NArgonish::EArgon2Type::Argon2id, 2, 32768, 2);

    std::vector<ui8> key(keyLength);
    argon2id->Hash(masterPassword.data(), masterPassword.size(),
                   purpose.data(), purpose.size(),
                   key.data(), key.size());

    return TString(reinterpret_cast<char*>(key.data()), key.size());
}
```

### 3. 数据结构应用

#### 哈希表优化
```cpp
// MurmurHash 用于自定义哈希表
template <typename K, typename V>
class OptimizedHashMap {
private:
    struct Entry {
        K key;
        V value;
        bool occupied = false;
    };

    std::vector<Entry> entries;
    size_t mask;

public:
    OptimizedHashMap(size_t initialSize) {
        size_t size = 1;
        while (size < initialSize) size <<= 1;
        entries.resize(size);
        mask = size - 1;
    }

    V* find(const K& key) {
        TMurmurHash2A<ui64> hasher;
        hasher.Update(&key, sizeof(K));
        ui64 hash = hasher.Value();

        size_t index = hash & mask;
        while (entries[index].occupied && entries[index].key != key) {
            index = (index + 1) & mask;
        }

        return entries[index].occupied ? &entries[index].value : nullptr;
    }
};
```

#### 布隆过滤器
```cpp
class SimpleBloomFilter {
private:
    std::vector<bool> bits;
    size_t numHashes;

public:
    SimpleBloomFilter(size_t size, size_t hashCount)
        : bits(size), numHashes(hashCount) {}

    void add(const TString& item) {
        TMurmurHash2A<ui64> hasher;
        for (size_t i = 0; i < numHashes; ++i) {
            hasher.Update(&i, sizeof(i));
            hasher.Update(item.data(), item.size());
            size_t index = hasher.Value() % bits.size();
            bits[index] = true;
        }
    }

    bool mightContain(const TString& item) const {
        TMurmurHash2A<ui64> hasher;
        for (size_t i = 0; i < numHashes; ++i) {
            hasher.Update(&i, sizeof(i));
            hasher.Update(item.data(), item.size());
            size_t index = hasher.Value() % bits.size();
            if (!bits[index]) {
                return false;
            }
        }
        return true;
    }
};
```

### 4. 缓存和去重

#### 内容去重
```cpp
class ContentDeduplicator {
private:
    THashMap<ui64, TString> contentByHash;

public:
    TString addContent(const TString& content) {
        ui64 hash = MD5::CalcHalfMix(content);
        auto it = contentByHash.find(hash);

        if (it != contentByHash.end()) {
            return it->second; // 返回已存在的内容
        }

        contentByHash[hash] = content;
        return content; // 新内容，存储并返回
    }
};
```

#### 缓存键生成
```cpp
class CacheKeyGenerator {
public:
    static ui64 generateKey(const TString& operation,
                           const std::vector<TString>& params) {
        TMurmurHash2A<ui64> hasher;
        hasher.Update(operation.data(), operation.size());

        for (const auto& param : params) {
            hasher.Update(param.data(), param.size());
            hasher.Update("|", 1); // 分隔符
        }

        return hasher.Value();
    }
};
```

## ⚡ 性能优化

### 1. 硬件加速检测

```cpp
class OptimizedHashProcessor {
public:
    OptimizedHashProcessor() {
        checkHardwareSupport();
    }

    ui32 computeCRC32C(const void* data, size_t size) {
        if (hasFastCRC32C) {
            return Crc32c(data, size);
        } else {
            // 软件回退实现
            return computeCRC32CSoftware(data, size);
        }
    }

private:
    bool hasFastCRC32C = false;

    void checkHardwareSupport() {
        hasFastCRC32C = HaveFastCrc32c();
        if (hasFastCRC32C) {
            Cout << "Using hardware-accelerated CRC32C" << Endl;
        }
    }

    ui32 computeCRC32CSoftware(const void* data, size_t size) {
        // 软件实现作为回退
        // ... 实现细节
        return 0;
    }
};
```

### 2. 批量哈希计算

```cpp
class BatchHashProcessor {
public:
    std::vector<TString> batchMD5(const std::vector<TString>& inputs) {
        std::vector<TString> results;
        results.reserve(inputs.size());

        for (const auto& input : inputs) {
            results.push_back(MD5::Calc(input));
        }

        return results;
    }

    std::vector<ui64> batchMurmurHash(const std::vector<TString>& inputs) {
        std::vector<ui64> results;
        results.reserve(inputs.size());

        for (const auto& input : inputs) {
            TMurmurHash2A<ui64> hasher;
            hasher.Update(input.data(), input.size());
            results.push_back(hasher.Value());
        }

        return results;
    }
};
```

### 3. 内存池优化

```cpp
class MemoryOptimizedHasher {
private:
    static constexpr size_t BUFFER_SIZE = 4096;
    alignas(64) std::array<ui8, BUFFER_SIZE> buffer; // 缓存行对齐

public:
    ui64 hashLargeData(IInputStream* input) {
        TMurmurHash2A<ui64> hasher;

        while (!input->Exhausted()) {
            size_t bytesRead = input->Load(buffer.data(), buffer.size());
            hasher.Update(buffer.data(), bytesRead);
        }

        return hasher.Value();
    }
};
```

## 🔗 最佳实践

### 1. 算法选择指南

| 应用场景 | 推荐算法 | 理由 |
|---------|---------|------|
| 文件校验 | MD5, CRC32C | MD5广泛支持，CRC32C速度快 |
| 密码存储 | Argon2id | 抗GPU攻击，内存硬 |
| 哈希表键 | MurmurHash, SuperFastHash | 高性能，分布好 |
| 数据去重 | MD5 | 128位，冲突概率极低 |
| 网络校验 | CRC32C | 硬件加速，快速 |
| 随机数生成 | MurmurHash | 良好的随机特性 |

### 2. 安全考虑

```cpp
// 安全的密码哈希实现
class SecurePasswordHasher {
private:
    static constexpr ui32 DEFAULT_T_COST = 3;
    static constexpr ui32 DEFAULT_M_COST = 65536;  // 64MB
    static constexpr ui32 DEFAULT_THREADS = 4;
    static constexpr size_t SALT_SIZE = 16;
    static constexpr size_t HASH_SIZE = 32;

public:
    struct PasswordHash {
        TString salt;
        TString hash;
        ui32 tCost, mCost, threads;
    };

    PasswordHash hashPassword(const TString& password) {
        PasswordHash result;

        // 生成随机盐
        result.salt = generateRandomSalt(SALT_SIZE);
        result.tCost = DEFAULT_T_COST;
        result.mCost = DEFAULT_M_COST;
        result.threads = DEFAULT_THREADS;

        // 计算 Argon2id 哈希
        NArgonish::TArgon2Factory factory;
        auto argon2id = factory.Create(NArgonish::EArgon2Type::Argon2id,
                                      result.tCost, result.mCost, result.threads);

        result.hash.resize(HASH_SIZE);
        argon2id->Hash(password.data(), password.size(),
                      result.salt.data(), result.salt.size(),
                      &result.hash[0], HASH_SIZE);

        return result;
    }

    bool verifyPassword(const TString& password, const PasswordHash& storedHash) {
        NArgonish::TArgon2Factory factory;
        auto argon2id = factory.Create(NArgonish::EArgon2Type::Argon2id,
                                      storedHash.tCost, storedHash.mCost, storedHash.threads);

        std::vector<ui8> computedHash(HASH_SIZE);
        argon2id->Hash(password.data(), password.size(),
                      storedHash.salt.data(), storedHash.salt.size(),
                      computedHash.data(), HASH_SIZE);

        return std::equal(computedHash.begin(), computedHash.end(),
                         storedHash.hash.begin());
    }

private:
    TString generateRandomSalt(size_t size) {
        // 使用密码学安全的随机数生成器
        // ... 实现细节
        return TString(size, 0); // 简化示例
    }
};
```

### 3. 错误处理

```cpp
class RobustHashProcessor {
public:
    // 安全的文件哈希计算
    std::optional<TString> safeFileMD5(const TString& filePath) {
        try {
            // 检查文件存在性
            if (!TFileStat(filePath).Exists()) {
                Cerr << "File does not exist: " << filePath << Endl;
                return std::nullopt;
            }

            // 检查文件大小
            if (TFileStat(filePath).Size > MAX_FILE_SIZE) {
                Cerr << "File too large: " << filePath << Endl;
                return std::nullopt;
            }

            return MD5::File(filePath);

        } catch (const std::exception& e) {
            Cerr << "Error calculating MD5 for file " << filePath
                 << ": " << e.what() << Endl;
            return std::nullopt;
        }
    }

private:
    static constexpr size_t MAX_FILE_SIZE = 1024 * 1024 * 1024; // 1GB
};
```

## 📝 注意事项

### 1. 密码学安全性
- **MD5 不应用于安全场景**：已被证明存在碰撞攻击
- **正确使用 Argon2**：选择合适的参数平衡安全性和性能
- **盐值管理**：确保使用足够长度的随机盐值

### 2. 性能考虑
- **硬件加速**：优先使用支持硬件加速的算法
- **内存对齐**：确保数据结构正确对齐以提高性能
- **批量处理**：对于大量数据，考虑批量哈希计算

### 3. 并发安全
- **线程安全性**：大部分算法都是线程安全的，但状态对象不是
- **实例管理**：每个线程使用独立的哈希器实例

### 4. 内存使用
- **Argon2 内存消耗**：注意参数设置对内存使用的影响
- **大文件处理**：使用流式API处理大文件以控制内存使用

`digest` 模块为 YTsaurus 项目提供了全面的哈希和摘要算法支持，从基础的数据校验到高级的密码学应用，满足了不同场景下的性能和安全需求。