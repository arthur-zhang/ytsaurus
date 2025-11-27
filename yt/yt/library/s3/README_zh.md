# S3 (Amazon S3 客户端)

S3 是 YTsaurus 中实现的 Amazon S3 兼容对象存储客户端，提供了完整的 S3 API 访问功能。

## 概述

S3 客户端提供以下核心功能：
- 兼容 Amazon S3 REST API
- 完整的对象存储操作（PUT、GET、DELETE）
- 多部分上传支持
- Bucket 管理功能
- SSL/TLS 安全连接
- 异步操作支持

## 核心组件

### 1. IClient (S3 客户端接口)
主要的 S3 客户端接口：

```cpp
struct IClient : public TRefCounted {
    // 启动客户端（必须在使用前调用）
    virtual TFuture<void> Start() = 0;

    // Bucket 操作
    virtual TFuture<TListBucketsResponse> ListBuckets(const TListBucketsRequest& request) = 0;
    virtual TFuture<TPutBucketResponse> PutBucket(const TPutBucketRequest& request) = 0;
    virtual TFuture<TDeleteBucketResponse> DeleteBucket(const TDeleteBucketRequest& request) = 0;

    // 对象操作
    virtual TFuture<TListObjectsResponse> ListObjects(const TListObjectsRequest& request) = 0;
    virtual TFuture<TPutObjectResponse> PutObject(const TPutObjectRequest& request) = 0;
    virtual TFuture<TGetObjectResponse> GetObject(const TGetObjectRequest& request) = 0;
    virtual TFuture<TGetObjectStreamResponse> GetObjectStream(const TGetObjectStreamRequest& request) = 0;
    virtual TFuture<TDeleteObjectResponse> DeleteObject(const TDeleteObjectRequest& request) = 0;
    virtual TFuture<TDeleteObjectsResponse> DeleteObjects(const TDeleteObjectsRequest& request) = 0;

    // 多部分上传
    virtual TFuture<TCreateMultipartUploadResponse> CreateMultipartUpload(const TCreateMultipartUploadRequest& request) = 0;
    virtual TFuture<TUploadPartResponse> UploadPart(const TUploadPartRequest& request) = 0;
    virtual TFuture<TCompleteMultipartUploadResponse> CompleteMultipartUpload(const TCompleteMultipartUploadRequest& request) = 0;
    virtual TFuture<TAbortMultipartUploadResponse> AbortMultipartUpload(const TAbortMultipartUploadRequest& request) = 0;

    // 对象元数据
    virtual TFuture<THeadObjectResponse> HeadObject(const THeadObjectRequest& request) = 0;
};
```

### 2. 配置类

#### TS3ClientConfig (客户端配置)
```cpp
struct TS3ClientConfig : public NYTree::TYsonStruct {
    // S3 端点配置
    TString Endpoint;
    TString Region;
    bool UseVirtualAddressing = true;

    // 连接配置
    int ConnectionPoolSize = 10;
    int RequestTimeout = 30000;  // 毫秒

    // 重试配置
    int RetryCount = 3;
    TDuration RetryDelay = TDuration::MilliSeconds(1000);

    REGISTER_YSON_STRUCT(TS3ClientConfig);
};
```

#### TS3ConnectionConfig (连接配置)
```cpp
struct TS3ConnectionConfig : public NYTree::TYsonStruct {
    // 代理配置
    std::optional<TString> ProxyHost;
    int ProxyPort = 0;
    std::optional<TString> ProxyUser;
    std::optional<TString> ProxyPassword;

    // 请求配置
    TDuration ConnectTimeout = TDuration::Seconds(30);
    TDuration ReadTimeout = TDuration::Seconds(300);

    REGISTER_YSON_STRUCT(TS3ConnectionConfig);
};
```

### 3. 凭据提供器
```cpp
struct ICredentialsProvider : public TRefCounted {
    virtual TFuture<TString> GetAccessKey() = 0;
    virtual TFuture<TString> GetSecretKey() = 0;
    virtual TFuture<TString> GetSessionToken() = 0;
};
```

## 使用方法

### 基本客户端创建
```cpp
#include <yt/yt/library/s3/client.h>
#include <yt/yt/library/s3/credential_provider.h>

using namespace NYT::NS3;

// 创建配置
auto config = New<TS3ClientConfig>();
config->SetEndpoint("s3.amazonaws.com");
config->SetRegion("us-east-1");
config->SetUseVirtualAddressing(true);

// 创建凭证提供器（示例：静态凭证）
auto credentialProvider = CreateStaticCredentialsProvider(
    "YOUR_ACCESS_KEY",
    "YOUR_SECRET_KEY");

// 创建 SSL 上下文配置
auto sslConfig = New<NCrypto::TSslContextConfig>();

// 创建客户端
auto poller = NConcurrency::CreatePoller();
auto invoker = GetSyncInvoker();

auto client = CreateClient(
    config,
    credentialProvider,
    sslConfig,
    poller,
    invoker);

// 启动客户端
WaitFor(client->Start()).ThrowOnError();
```

### Bucket 操作
```cpp
// 创建 Bucket
TPutBucketRequest putRequest;
putRequest.Bucket = "my-test-bucket";
putRequest.Acl = EBucketAcl::Private;

auto putResponse = WaitFor(client->PutBucket(putRequest))
    .ValueOrThrow();

// 列出所有 Bucket
TListBucketsRequest listRequest;
auto listResponse = WaitFor(client->ListBuckets(listRequest))
    .ValueOrThrow();

for (const auto& bucket : listResponse.Buckets) {
    std::cout << "Bucket: " << bucket.Name
              << " Created: " << bucket.CreationDate << std::endl;
}

// 删除 Bucket
TDeleteBucketRequest deleteRequest;
deleteRequest.Bucket = "my-test-bucket";

auto deleteResponse = WaitFor(client->DeleteBucket(deleteRequest))
    .ValueOrThrow();
```

### 对象操作
```cpp
// 上传对象
TString data = "Hello, S3!";
auto dataRef = TSharedRef::FromString(data);

TPutObjectRequest putRequest;
putRequest.Bucket = "my-test-bucket";
putRequest.Key = "test/file.txt";
putRequest.Data = dataRef;
putRequest.ContentMd5 = ComputeMD5(data);

auto putResponse = WaitFor(client->PutObject(putRequest))
    .ValueOrThrow();
std::cout << "ETag: " << putResponse.ETag << std::endl;

// 下载对象
TGetObjectRequest getRequest;
getRequest.Bucket = "my-test-bucket";
getRequest.Key = "test/file.txt";
getRequest.Range = "bytes=0-4";  // 可选：范围请求

auto getResponse = WaitFor(client->GetObject(getRequest))
    .ValueOrThrow();

std::cout << "Data: " << TStringBuf(
    getResponse.Data.Begin(),
    getResponse.Data.Size()) << std::endl;
std::cout << "Size: " << getResponse.Data.Size() << std::endl;

// 流式下载大对象
TGetObjectStreamRequest streamRequest;
streamRequest.Bucket = "my-test-bucket";
streamRequest.Key = "large-file.dat";

auto streamResponse = WaitFor(client->GetObjectStream(streamRequest))
    .ValueOrThrow();

// 读取流
auto stream = streamResponse.Stream;
std::vector<char> buffer(4096);
size_t totalBytes = 0;

while (true) {
    size_t bytesRead = stream->Read(buffer.data(), buffer.size());
    if (bytesRead == 0) break;

    totalBytes += bytesRead;
    ProcessData(buffer.data(), bytesRead);
}

std::cout << "Total bytes read: " << totalBytes << std::endl;
```

### 多部分上传（大文件）
```cpp
// 开始多部分上传
TCreateMultipartUploadRequest createRequest;
createRequest.Bucket = "my-test-bucket";
createRequest.Key = "large-file.dat";

auto createResponse = WaitFor(client->CreateMultipartUpload(createRequest))
    .ValueOrThrow();
TString uploadId = createResponse.UploadId;

// 上传分片
constexpr size_t PART_SIZE = 5 * 1024 * 1024; // 5MB
std::vector<TCompleteMultipartUploadRequest::TPart> parts;
TFileInput file("large-file.dat");
size_t partNumber = 1;
std::vector<char> buffer(PART_SIZE);

while (!file.eof()) {
    size_t bytesRead = file.Read(buffer.data(), buffer.size());
    if (bytesRead == 0) break;

    auto partData = TSharedRef::FromString(TString(buffer.data(), bytesRead));

    TUploadPartRequest partRequest;
    partRequest.Bucket = "my-test-bucket";
    partRequest.Key = "large-file.dat";
    partRequest.UploadId = uploadId;
    partRequest.PartIndex = partNumber;
    partRequest.Data = partData;
    partRequest.ContentMd5 = ComputeMD5(TString(buffer.data(), bytesRead));

    auto partResponse = WaitFor(client->UploadPart(partRequest))
        .ValueOrThrow();

    TCompleteMultipartUploadRequest::TPart part;
    part.PartIndex = partNumber;
    part.ETag = partResponse.ETag;
    parts.push_back(part);

    ++partNumber;
}

// 完成多部分上传
TCompleteMultipartUploadRequest completeRequest;
completeRequest.Bucket = "my-test-bucket";
completeRequest.Key = "large-file.dat";
completeRequest.UploadId = uploadId;
completeRequest.Parts = parts;

auto completeResponse = WaitFor(client->CompleteMultipartUpload(completeRequest))
    .ValueOrThrow();

std::cout << "Upload completed. ETag: " << completeResponse.ETag << std::endl;
```

### 对象列表
```cpp
// 列出对象（带分页）
TString continuationToken;
do {
    TListObjectsRequest listRequest;
    listRequest.Bucket = "my-test-bucket";
    listRequest.Prefix = "logs/";  // 可选：前缀过滤
    if (!continuationToken.empty()) {
        listRequest.ContinuationToken = continuationToken;
    }

    auto listResponse = WaitFor(client->ListObjects(listRequest))
        .ValueOrThrow();

    for (const auto& object : listResponse.Objects) {
        std::cout << "Key: " << object.Key
                  << " Size: " << object.Size
                  << " Last Modified: " << object.LastModified
                  << " ETag: " << object.ETag << std::endl;
    }

    continuationToken = listResponse.NextContinuationToken.value_or("");
} while (!continuationToken.empty());
```

### 批量删除
```cpp
// 批量删除对象
TDeleteObjectsRequest deleteRequest;
deleteRequest.Bucket = "my-test-bucket";
deleteRequest.Objects = {"file1.txt", "file2.txt", "file3.txt"};

auto deleteResponse = WaitFor(client->DeleteObjects(deleteRequest))
    .ValueOrThrow();

for (const auto& error : deleteResponse.Errors) {
    std::cerr << "Failed to delete " << error.Key
              << ": " << error.Code << " - " << error.Message << std::endl;
}
```

### 错误处理
```cpp
try {
    auto response = WaitFor(client->GetObject(getRequest))
        .ValueOrThrow();
    ProcessObject(response.Data);
} catch (const TErrorException& e) {
    if (e.GetErrorCode() == EErrorCode::S3ApiError) {
        auto s3Error = dynamic_cast<const TS3Error&>(e);
        std::cerr << "S3 API Error: " << s3Error.GetErrorCode()
                  << " - " << s3Error.GetMessage() << std::endl;
        std::cerr << "HTTP Status: " << s3Error.GetHttpStatusCode() << std::endl;
    } else {
        throw;
    }
}
```

## 高级功能

### 1. 自定义重试策略
```cpp
class CustomRetryPolicy {
public:
    bool ShouldRetry(const TError& error, int attempt) {
        if (attempt >= MaxRetries_) {
            return false;
        }

        // 可重试的错误码
        std::set<int> retryableCodes = {
            429, // Too Many Requests
            500, // Internal Server Error
            502, // Bad Gateway
            503, // Service Unavailable
            504  // Gateway Timeout
        };

        if (error.GetErrorCode() == EErrorCode::S3ApiError) {
            auto s3Error = dynamic_cast<const TS3Error&>(error);
            return retryableCodes.count(s3Error.GetHttpStatusCode()) > 0;
        }

        return false;
    }

    TDuration GetRetryDelay(int attempt) {
        // 指数退避
        return TDuration::MilliSeconds(1000 * (1 << attempt));
    }

private:
    static constexpr int MaxRetries_ = 5;
};
```

### 2. 进度监控
```cpp
class UploadProgressTracker {
public:
    UploadProgressTracker(int64 totalSize)
        : TotalSize_(totalSize)
    { }

    void OnPartUploaded(int partNumber, int64 partSize) {
        UploadedSize_ += partSize;
        double progress = (double)UploadedSize_ / TotalSize_ * 100;

        std::cout << "Part " << partNumber << " uploaded. "
                  << "Progress: " << std::fixed << std::setprecision(1)
                  << progress << "% (" << UploadedSize_ << "/" << TotalSize_ << ")"
                  << std::endl;
    }

private:
    int64 TotalSize_;
    int64 UploadedSize_ = 0;
};
```

## 性能优化

### 1. 连接池优化
```cpp
// 根据负载调整连接池大小
auto config = New<TS3ClientConfig>();
config->SetConnectionPoolSize(50);  // 高并发场景
config->SetRequestTimeout(10000);  // 较短超时
```

### 2. 并行上传
```cpp
// 并行上传多个小对象
std::vector<TFuture<TPutObjectResponse>> futures;
for (const auto& file : files) {
    TPutObjectRequest request;
    request.Bucket = bucket;
    request.Key = file.Key;
    request.Data = file.Data;

    futures.push_back(client->PutObject(request));
}

// 等待所有上传完成
auto results = WaitFor(AllSucceeded(futures)).ValueOrThrow();
for (const auto& response : results) {
    std::cout << "Uploaded with ETag: " << response.ETag << std::endl;
}
```

### 3. 预签名URL
```cpp
// 生成预签名URL（需要扩展实现）
class PresignedUrlGenerator {
public:
    TString GenerateGetUrl(const TString& bucket, const TString& key, TDuration expiration) {
        // 生成带签名的URL
        // 实现细节省略...
        return GenerateUrl("GET", bucket, key, expiration);
    }

    TString GeneratePutUrl(const TString& bucket, const TString& key, TDuration expiration) {
        return GenerateUrl("PUT", bucket, key, expiration);
    }

private:
    TString GenerateUrl(const TString& method, const TString& bucket,
                        const TString& key, TDuration expiration) {
        // 实现AWS签名版本4
        // ...
        return signedUrl;
    }
};
```

## 最佳实践

### 1. 错误处理
- 总是检查响应状态
- 实现适当的重试机制
- 记录详细的错误信息
- 处理网络超时

### 2. 性能考虑
- 使用连接池减少连接开销
- 批量操作减少请求次数
- 异步操作提高并发性
- 合理设置超时时间

### 3. 安全考虑
- 使用 HTTPS 连接
- 安全存储访问密钥
- 实现适当的访问控制
- 验证数据完整性（MD5）

## 依赖项

- YTsaurus 核心库 (`yt/yt/core/`)
- HTTP 库 (`yt/yt/core/http/`)
- 加密库 (`yt/yt/core/crypto/`)
- 并发库 (`yt/yt/core/concurrency/`)
- Poco XML 库

## 注意事项

1. **区域兼容性**: 确保客户端区域与 S3 存储区域匹配
2. **API 版本**: 当前实现基于 S3 API 某特定版本
3. **权限管理**: 确保访问密钥有适当的权限
4. **存储成本**: 注意监控 S3 存储成本和请求费用
5. **数据一致性**: S3 的最终一致性模型
6. **大小限制**: 单个对象大小限制为 5TB
7. **多部分上传**: 大文件必须使用多部分上传