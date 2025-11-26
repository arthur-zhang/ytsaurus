# OpenSSL 加密库封装

## 项目概述

OpenSSL 库封装是 YTsaurus 项目中对 OpenSSL 加密库的 C++ 封装实现，提供了类型安全、内存安全的加密操作接口。该封装简化了 OpenSSL 的使用，避免了常见的内存泄漏和错误处理问题。

### 核心功能
- **大整数运算**：高精度数学运算支持
- **RSA 加密**：RSA 公钥加密算法实现
- **SHA 哈希**：安全哈希算法支持
- **HMAC 消息认证**：基于哈希的消息认证码
- **SSL/TLS 通信**：安全通信协议支持
- **证书验证**：X.509 证书处理和验证

## 目录结构

### big_integer/ 目录
大整数运算模块，提供高精度数学运算功能。

#### 主要文件
- **big_integer.h/big_integer.cpp** - 大整数类实现

### crypto/ 目录
基础加密算法模块。

#### 主要文件
- **sha.h/sha.cpp** - SHA 哈希算法实现
- **rsa.h/rsa.cpp** - RSA 加密算法实现

### holders/ 目录
RAII 资源管理模块，确保 OpenSSL 资源的正确释放。

#### 主要文件
- **holder.h** - 通用 RAII 资源管理模板
- **bio.h/bio.cpp** - BIO（基本输入输出）对象管理
- **evp.h** - EVP（加密虚拟引擎）对象管理
- **hmac.h** - HMAC 对象管理
- **x509_vfy.h/x509_vfy.cpp** - X.509 证书验证对象管理

### io/ 目录
SSL/TLS 通信流处理模块。

#### 主要文件
- **stream.h/stream.cpp** - SSL 流封装实现

### init/ 目录
OpenSSL 库初始化模块。

### method/ 目录
SSL 方法配置模块。

## 使用示例

### 大整数运算示例
```cpp
#include <library/cpp/openssl/big_integer/big_integer.h>

using namespace NOpenSsl;

void BigIntegerExample() {
    // 从无符号长整型创建大整数
    TBigInteger num1 = TBigInteger::FromULong(123456789012345ULL);

    // 从内存区域创建大整数
    char data[] = {0x01, 0x02, 0x03, 0x04};
    TBigInteger num2 = TBigInteger::FromRegion(data, sizeof(data));

    // 比较运算
    if (num1 == num2) {
        printf("Numbers are equal\n");
    } else if (num1 != num2) {
        printf("Numbers are different\n");
    }

    // 获取字节数
    size_t numBytes = num1.NumBytes();
    printf("Number of bytes: %zu\n", numBytes);

    // 转换为内存区域
    char buffer[256];
    size_t written = num1.ToRegion(buffer);
    printf("Written %zu bytes\n", written);
}
```

### RSA 加密示例
```cpp
#include <library/cpp/openssl/crypto/rsa.h>

using namespace NOpenSsl;

void RsaExample() {
    // 生成 RSA 密钥对
    TRsaKey keyPair = GenerateRsaKeyPair(2048);

    // 加密数据
    TString plaintext = "Hello, OpenSSL!";
    TString ciphertext = RsaEncrypt(keyPair.GetPublicKey(), plaintext);

    // 解密数据
    TString decrypted = RsaDecrypt(keyPair.GetPrivateKey(), ciphertext);

    printf("Original: %s\n", plaintext.c_str());
    printf("Decrypted: %s\n", decrypted.c_str());
}
```

### SHA 哈希示例
```cpp
#include <library/cpp/openssl/crypto/sha.h>

using namespace NOpenSsl;

void ShaExample() {
    TString data = "Data to hash";

    // 计算 SHA-256 哈希
    TString sha256Hash = Sha256(data);

    // 计算 SHA-512 哈希
    TString sha512Hash = Sha512(data);

    printf("SHA-256: %s\n", HexEncode(sha256Hash).c_str());
    printf("SHA-512: %s\n", HexEncode(sha512Hash).c_str());
}
```

### HMAC 示例
```cpp
#include <library/cpp/openssl/holders/hmac.h>

using namespace NOpenSsl;

void HmacExample() {
    TString key = "secret_key";
    TString message = "message to authenticate";

    // 计算 HMAC-SHA256
    THmac hmac(HmacAlgorithm::SHA256, key);
    hmac.Update(message);
    TString mac = hmac.Final();

    printf("HMAC: %s\n", HexEncode(mac).c_str());
}
```

## 实现原理

### RAII 资源管理
#### THolder 模板
```cpp
template <typename TType, auto Create, auto Destroy, class... Args>
class THolder {
public:
    THolder(Args... args) {
        Ptr = Create(args...);
        if (!Ptr) {
            throw std::bad_alloc();
        }
    }

    ~THolder() noexcept {
        Destroy(Ptr);
    }

    operator TType*() noexcept {
        return Ptr;
    }

private:
    TType* Ptr;
};
```

### 类型安全封装
- **自动资源管理**：构造时分配，析构时自动释放
- **异常安全**：构造失败时抛出异常
- **防止拷贝**：禁用拷贝构造和赋值操作
- **智能指针语义**：提供类似智能指针的使用体验

## 应用场景

### 网络安全
- **HTTPS 通信**：SSL/TLS 加密通信
- **数字签名**：数据完整性验证
- **证书管理**：X.509 证书处理
- **密钥管理**：安全的密钥生成和存储

### 数据保护
- **数据加密**：敏感数据加密存储
- **数据完整性**：哈希和消息认证码
- **安全传输**：网络数据安全传输
- **访问控制**：基于证书的身份验证

### 密码学应用
- **密码学算法**：各种加密算法实现
- **随机数生成**：安全随机数生成
- **密钥派生**：基于密码的密钥派生
- **协议实现**：安全协议的底层实现

## 最佳实践

### 内存安全
- 使用 RAII 管理 OpenSSL 对象
- 避免手动调用 free 函数
- 正确处理异常情况
- 防止资源泄漏

### 错误处理
- 检查所有 OpenSSL 函数返回值
- 使用异常处理机制
- 提供有意义的错误信息
- 记录错误日志

### 性能优化
- 复用加密上下文
- 批量处理数据
- 选择合适的算法参数
- 避免不必要的内存拷贝