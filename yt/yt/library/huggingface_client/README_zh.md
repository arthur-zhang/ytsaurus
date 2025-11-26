# Huggingface Client (Huggingface 客户端)

## 项目概述

Huggingface Client 模块提供了与 Hugging Face Hub 集成的功能，允许 YTsaurus 系统访问和下载 Hugging Face 上的数据集、模型和其他资源。该客户端专注于高效地获取机器学习和数据科学相关的资源。

## 核心功能

### 数据集访问
- **Parquet 文件下载**: 自动识别并下载 Hugging Face 数据集中的 Parquet 文件
- **数据集解析**: 解析数据集结构、子集和数据分割信息
- **URL 提取**: 提取数据文件的直接下载链接
- **批量下载**: 支持批量下载多个文件

### HTTP 客户端功能
- **异步下载**: 支持异步文件下载，提高下载效率
- **重定向处理**: 自动处理 HTTP 重定向，最多支持 10 次重定向
- **认证支持**: 支持 Hugging Face API token 认证
- **自定义端点**: 支持自定义 API 端点（主要用于测试）

### 网络优化
- **连接池**: 使用连接池管理 HTTP 连接
- **并发控制**: 通过 Poller 控制并发网络操作
- **流式下载**: 支持大文件的流式下载，减少内存占用

## 主要接口

### 核心类：THuggingfaceClient

```cpp
namespace NYT::NHuggingface {

class THuggingfaceClient
{
public:
    THuggingfaceClient(
        const std::optional<std::string>& token,
        NConcurrency::IPollerPtr poller,
        const std::optional<TString>& urlOverride = std::nullopt);

    std::vector<TString> GetParquetFileUrls(const TString& dataset, const TString& subset, const TString& split);

    NConcurrency::IAsyncZeroCopyInputStreamPtr DownloadFile(const TString& url);
};

} // namespace NYT::NHuggingface
```

#### 构造函数

```cpp
// 标准构造函数
THuggingfaceClient(
    const std::optional<std::string>& token,      // Hugging Face API token（可选）
    NConcurrency::IPollerPtr poller,              // 网络轮询器
    const std::optional<TString>& urlOverride = std::nullopt);  // URL 重写（测试用）
```

#### 主要方法

```cpp
// 获取数据集的 Parquet 文件 URL 列表
std::vector<TString> GetParquetFileUrls(
    const TString& dataset,    // 数据集名称，如 "imdb"
    const TString& subset,     // 数据集子集，如 "plain_text"
    const TString& split);     // 数据分割，如 "train"

// 异步下载文件
NConcurrency::IAsyncZeroCopyInputStreamPtr DownloadFile(
    const TString& url);       // 文件下载 URL
```

## 使用方法

### 基本使用示例

```cpp
#include <yt/yt/library/huggingface_client/client.h>
#include <yt/yt/core/concurrency/poller.h>

using namespace NYT;
using namespace NYT::NHuggingface;
using namespace NYT::NConcurrency;

// 创建网络轮询器
auto poller = CreatePoller();

// 创建客户端（无 token 访问公共数据集）
auto client = std::make_unique<THuggingfaceClient>(
    std::nullopt,  // 无 token
    poller
);

try {
    // 获取 IMDb 数据集的训练文件 URL
    auto urls = client->GetParquetFileUrls("imdb", "plain_text", "train");

    Cout << "Found " << urls.size() << " Parquet files:" << Endl;
    for (const auto& url : urls) {
        Cout << "  " << url << Endl;
    }

    // 下载第一个文件
    if (!urls.empty()) {
        auto inputStream = client->DownloadFile(urls[0]);
        // 处理下载的数据流...
    }

} catch (const std::exception& e) {
    Cerr << "Error accessing Hugging Face dataset: " << e.what() << Endl;
}
```

### 带认证的客户端使用示例

```cpp
// 使用 API token 创建客户端（访问私有或受限数据集）
auto token = "hf_your_api_token_here";  // 从环境变量或配置文件获取
auto client = std::make_unique<THuggingfaceClient>(
    token,
    poller
);

try {
    // 访问需要认证的数据集
    auto urls = client->GetParquetFileUrls("private-dataset", "default", "train");

    // 处理认证数据集的文件...

} catch (const std::exception& e) {
    Cerr << "Error accessing private dataset: " << e.what() << Endl;
}
```

### 批量下载和处理示例

```cpp
class DatasetDownloader {
public:
    DatasetDownloader(const TString& token) {
        poller_ = CreatePoller();
        client_ = std::make_unique<THuggingfaceClient>(token, poller_);
    }

    void DownloadDataset(const TString& dataset,
                        const TString& subset,
                        const TString& split,
                        const TString& outputDir) {
        try {
            // 获取所有文件 URL
            auto urls = client_->GetParquetFileUrls(dataset, subset, split);
            Cout << "Downloading " << urls.size() << " files from dataset "
                 << dataset << Endl;

            // 并发下载文件
            std::vector<NConcurrency::IAsyncZeroCopyInputStreamPtr> downloadStreams;
            for (const auto& url : urls) {
                auto stream = client_->DownloadFile(url);
                downloadStreams.push_back(stream);
            }

            // 处理下载的文件
            for (size_t i = 0; i < downloadStreams.size(); ++i) {
                ProcessDownloadedFile(downloadStreams[i], urls[i], outputDir);
            }

        } catch (const std::exception& e) {
            Cerr << "Download failed: " << e.what() << Endl;
            throw;
        }
    }

private:
    void ProcessDownloadedFile(NConcurrency::IAsyncZeroCopyInputStreamPtr stream,
                              const TString& url,
                              const TString& outputDir) {
        // 提取文件名
        auto fileName = GetFileNameFromUrl(url);
        auto outputPath = NFS::CombinePaths(outputDir, fileName);

        // 写入文件
        TFileOutput fileOutput(outputPath);

        while (true) {
            auto block = stream->Read();
            if (!block) {
                break;
            }
            fileOutput.Write(block.Begin(), block.Size());
        }

        Cout << "Downloaded: " << fileName << Endl;
    }

    TString GetFileNameFromUrl(const TString& url) {
        // 从 URL 中提取文件名
        auto pos = url.find_last_of('/');
        return (pos != TString::npos) ? url.substr(pos + 1) : "downloaded_file.parquet";
    }

    NConcurrency::IPollerPtr poller_;
    std::unique_ptr<THuggingfaceClient> client_;
};
```

### 测试环境使用示例

```cpp
// 创建测试客户端（使用自定义 URL）
auto testUrl = "http://test-huggingface-endpoint.local";
auto testClient = std::make_unique<THuggingfaceClient>(
    std::nullopt,
    poller,
    testUrl  // 测试端点
);
```

## 配置说明

### 环境变量

| 变量名 | 说明 | 示例 |
|--------|------|------|
| HUGGINGFACE_TOKEN | Hugging Face API token | hf_xxxxxxxxxxxxxxxxxxxx |
| HUGGINGFACE_URL | 自定义 API 端点（测试用） | http://localhost:8080 |

### API Token 配置

1. **获取 Token**:
   - 访问 [Hugging Face Settings](https://huggingface.co/settings/tokens)
   - 创建新的 API token
   - 根据需要设置 token 权限

2. **Token 使用**:
   ```cpp
   // 从环境变量读取 token
   auto token = std::getenv("HUGGINGFACE_TOKEN");

   // 创建认证客户端
   auto client = std::make_unique<THuggingfaceClient>(
       token ? std::optional<std::string>(token) : std::nullopt,
       poller
   );
   ```

### 网络配置

```cpp
// 配置网络轮询器
auto pollerConfig = New<NConcurrency::TPollerConfig>();
pollerConfig->SetMaxConnections(100);        // 最大连接数
pollerConfig->SetConnectTimeout(TDuration::Seconds(30));  // 连接超时
pollerConfig->SetReadTimeout(TDuration::Minutes(5));      // 读取超时

auto poller = CreatePoller(pollerConfig);
```

## 性能考虑

### 下载性能
- **并发下载**: 利用异步 I/O 实现并发下载
- **流式处理**: 避免将大文件完全加载到内存
- **连接复用**: 通过连接池复用 HTTP 连接

### 内存使用
- **零拷贝**: 使用零拷贝接口减少内存复制
- **缓冲区管理**: 合理设置缓冲区大小
- **及时释放**: 及时释放已处理的内存块

### 网络优化
- **重定向处理**: 自动处理重定向，减少额外请求
- **超时控制**: 设置合理的网络超时时间
- **错误重试**: 实现网络错误的自动重试机制

## 最佳实践

### 1. 错误处理和重试

```cpp
class RobustDatasetDownloader {
public:
    void DownloadWithRetry(const TString& dataset,
                          const TString& subset,
                          const TString& split) {
        const int maxRetries = 3;
        const TDuration retryDelay = TDuration::Seconds(2);

        for (int attempt = 0; attempt <= maxRetries; ++attempt) {
            try {
                auto urls = client_->GetParquetFileUrls(dataset, subset, split);
                ProcessUrls(urls);
                return;  // 成功则返回
            } catch (const std::exception& e) {
                if (attempt == maxRetries) {
                    throw;  // 最后一次尝试失败，抛出异常
                }

                Cout << "Attempt " << attempt + 1 << " failed: " << e.what()
                     << ", retrying in " << retryDelay.Seconds() << " seconds..." << Endl;

                Sleep(retryDelay);
            }
        }
    }
};
```

### 2. 资源管理

```cpp
class ManagedHuggingfaceClient {
public:
    ManagedHuggingfaceClient(const std::string& token)
        : token_(token)
        , poller_(CreatePoller())
    {
    }

    ~ManagedHuggingfaceClient() {
        // 清理资源
        client_.reset();
        poller_.reset();
    }

    THuggingfaceClient& GetClient() {
        if (!client_) {
            client_ = std::make_unique<THuggingfaceClient>(
                token_,
                poller_
            );
        }
        return *client_;
    }

private:
    std::string token_;
    NConcurrency::IPollerPtr poller_;
    std::unique_ptr<THuggingfaceClient> client_;
};
```

### 3. 缓存和去重

```cpp
class CachedDatasetDownloader {
public:
    std::vector<TString> GetCachedUrls(const TString& dataset,
                                      const TString& subset,
                                      const TString& split) {
        auto cacheKey = dataset + "/" + subset + "/" + split;

        // 检查缓存
        if (urlCache_.find(cacheKey) != urlCache_.end()) {
            Cout << "Using cached URLs for " << cacheKey << Endl;
            return urlCache_[cacheKey];
        }

        // 获取并缓存 URL
        auto urls = client_->GetParquetFileUrls(dataset, subset, split);
        urlCache_[cacheKey] = urls;

        return urls;
    }

private:
    THashMap<TString, std::vector<TString>> urlCache_;
};
```

## 依赖项

- **YT Core**: 基础数据结构和并发支持
- **YT HTTP**: HTTP 客户端实现
- **YT Concurrency**: 异步 I/O 和网络轮询
- **Standard Library**: STL 容器和字符串处理

## 注意事项

### 1. 认证和权限
- 私有数据集需要有效的 API token
- Token 需要适当的访问权限
- 定期更新 API token 以确保安全性

### 2. 网络限制
- 某些网络环境可能限制对 Hugging Face 的访问
- 考虑使用代理服务器或 VPN
- 监控网络连接状态和下载进度

### 3. 存储考虑
- 大型数据集可能需要大量存储空间
- 考虑使用压缩和增量下载
- 实现本地缓存机制减少重复下载

### 4. 速率限制
- Hugging Face API 可能存在速率限制
- 实现适当的请求间隔和重试策略
- 监控 API 使用情况避免超限

### 5. 数据一致性
- 数据集可能随时更新
- 记录数据集版本和哈希值
- 考虑数据版本控制机制

### 6. 安全性
- 安全存储和使用 API token
- 验证下载文件的完整性
- 避免执行来自不可信来源的代码