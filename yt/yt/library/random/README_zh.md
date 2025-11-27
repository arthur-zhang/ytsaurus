# Random (随机数生成)

Random 是 YTsaurus 中提供的随机数生成工具库，包含伯努利采样器和离散分布生成器。

## 概述

Random 库提供以下核心功能：
- 伯努利采样器
- 加权随机选择
- 确定性随机数生成
- 可持久化的采样状态

## 核心组件

### 1. TBernoulliSampler (伯努利采样器)
用于概率采样的工具类：

```cpp
class TBernoulliSampler {
public:
    // 默认构造
    TBernoulliSampler() = default;

    // 带采样率和种子的构造
    explicit TBernoulliSampler(
        std::optional<double> samplingRate,
        std::optional<ui64> seed = std::nullopt);

    // 采样（依赖历史状态）
    bool Sample();

    // 带盐的采样（确定性）
    bool Sample(ui64 salt);

    // 持久化状态
    void Persist(const TStreamPersistenceContext& context);

private:
    std::optional<double> SamplingRate_;
    std::optional<ui64> Seed_;
    std::mt19937 Generator_;
    std::bernoulli_distribution Distribution_;
};
```

### 2. 离散分布函数
基于权重的随机选择函数：

```cpp
// 根据权重随机选择索引
int DiscreteDistribution(std::vector<double> weights);
```

## 使用方法

### 伯努利采样
```cpp
#include <yt/yt/library/random/bernoulli_sampler.h>

using namespace NYT;

// 创建采样器（10%采样率）
TBernoulliSampler sampler(0.1);

// 随机采样
if (sampler.Sample()) {
    // 10%概率执行
    ProcessItem();
}

// 带种子的采样器（确定性）
TBernoulliSampler deterministicSampler(0.1, 12345);
bool result1 = deterministicSampler.Sample(42);  // 总是返回相同结果
bool result2 = deterministicSampler.Sample(42);  // 与result1相同

// 序列采样（依赖历史）
bool result3 = deterministicSampler.Sample();    // 依赖前序状态
bool result4 = deterministicSampler.Sample();    // 可能与result3不同
```

### 加权随机选择
```cpp
#include <yt/yt/library/random/discrete_distribution.h>

// 定义选项权重
std::vector<double> weights = {
    10.0,  // 选项A：10%概率
    20.0,  // 选项B：20%概率
    50.0,  // 选项C：50%概率
    20.0   // 选项D：20%概率
};

// 随机选择
int selectedIndex = DiscreteDistribution(weights);
std::vector<std::string> options = {"A", "B", "C", "D"};
std::cout << "Selected: " << options[selectedIndex] << std::endl;
```

### 数据流采样
```cpp
class DataSampler {
public:
    DataSampler(double samplingRate, ui64 seed = 0)
        : Sampler_(samplingRate, seed)
    { }

    bool ShouldSample(const std::string& key) {
        // 使用键作为盐，确保相同键总是有相同结果
        ui64 salt = ComputeHash(key);
        return Sampler_.Sample(salt);
    }

    void ProcessDataStream(const std::vector<std::string>& items) {
        for (const auto& item : items) {
            if (ShouldSample(item)) {
                ProcessItem(item);
            }
        }
    }

private:
    TBernoulliSampler Sampler_;

    ui64 ComputeHash(const std::string& str) {
        // 简单哈希函数
        ui64 hash = 5381;
        for (char c : str) {
            hash = ((hash << 5) + hash) + c;
        }
        return hash;
    }

    void ProcessItem(const std::string& item) {
        // 处理采样的项
        std::cout << "Processing: " << item << std::endl;
    }
};
```

### 实验分组
```cpp
class ExperimentManager {
public:
    ExperimentManager(double experimentRate)
        : Sampler_(experimentRate)
    { }

    bool IsInExperiment(const std::string& userId) {
        // 确保用户总是属于同一组
        ui64 salt = std::hash<std::string>{}(userId);
        return Sampler_.Sample(salt);
    }

    void ProcessUser(const std::string& userId) {
        if (IsInExperiment(userId)) {
            // 实验组逻辑
            ProcessExperimentUser(userId);
        } else {
            // 对照组逻辑
            ProcessControlUser(userId);
        }
    }

private:
    TBernoulliSampler Sampler_;

    void ProcessExperimentUser(const std::string& userId) {
        std::cout << userId << " in experiment group" << std::endl;
    }

    void ProcessControlUser(const std::string& userId) {
        std::cout << userId << " in control group" << std::endl;
    }
};
```

### A/B 测试
```cpp
class ABTestManager {
public:
    enum class Group {
        A,
        B
    };

    ABTestManager() {
        // 50/50分配
        Weights_ = {1.0, 1.0};
    }

    Group AssignUser(const std::string& userId) {
        // 确保同一用户总是分配到相同组
        ui64 hash = std::hash<std::string>{}(userId);

        // 使用确定性采样
        TBernoulliSampler sampler(0.5, hash);
        return sampler.Sample() ? Group::A : Group::B;
    }

    void ProcessRequest(const std::string& userId, const Request& request) {
        Group group = AssignUser(userId);

        if (group == Group::A) {
            HandleGroupA(request);
        } else {
            HandleGroupB(request);
        }
    }

private:
    std::vector<double> Weights_;

    void HandleGroupA(const Request& request) {
        // A组处理逻辑
    }

    void HandleGroupB(const Request& request) {
        // B组处理逻辑
    }
};
```

## 应用场景

### 1. 日志采样
```cpp
class LoggerSampler {
public:
    LoggerSampler(double samplingRate)
        : Sampler_(samplingRate)
    { }

    void LogDebug(const std::string& message) {
        if (Sampler_.Sample()) {
            YT_LOG_DEBUG(message);
        }
    }

    void LogInfo(const std::string& message) {
        if (Sampler_.Sample()) {
            YT_LOG_INFO(message);
        }
    }

private:
    TBernoulliSampler Sampler_;
};
```

### 2. 负载测试
```cpp
class LoadGenerator {
public:
    LoadGenerator(double requestRate, double samplingRate)
        : RequestRate_(requestRate)
        , Sampler_(samplingRate)
    { }

    void GenerateLoad() {
        std::thread worker([this]() {
            while (running_) {
                if (Sampler_.Sample()) {
                    SendRequest();
                }
                std::this_thread::sleep_for(
                    std::chrono::milliseconds(1000 / RequestRate_));
            }
        });
        worker.detach();
    }

    void Stop() {
        running_ = false;
    }

private:
    double RequestRate_;
    TBernoulliSampler Sampler_;
    std::atomic<bool> running_{true};

    void SendRequest() {
        // 发送请求
    }
};
```

### 3. 缓存预热
```cpp
class CacheWarmer {
public:
    CacheWarmer(double warmupRate)
        : Sampler_(warmupRate)
    { }

    void WarmCache(const std::vector<std::string>& keys) {
        for (const auto& key : keys) {
            if (Sampler_.Sample()) {
                Preload(key);
            }
        }
    }

private:
    TBernoulliSampler Sampler_;

    void Preload(const std::string& key) {
        // 预加载缓存项
    }
};
```

## 性能考虑

### 1. 随机数生成器性能
- 使用 Mersenne Twister (std::mt19937) 算法
- 对于高性能场景，考虑预生成随机数

### 2. 内存使用
- 采样器状态很小，适合大量创建
- 可以使用单例模式减少开销

### 3. 分布函数优化
```cpp
class FastRandomSelector {
public:
    FastRandomSelector(const std::vector<double>& weights) {
        // 预计算累积分布
        double sum = 0;
        for (double w : weights) {
            sum += w;
            CumulativeWeights_.push_back(sum);
        }
        TotalWeight_ = sum;
    }

    int Select() {
        double r = RandomDouble() * TotalWeight_;
        auto it = std::lower_bound(
            CumulativeWeights_.begin(),
            CumulativeWeights_.end(),
            r);
        return it - CumulativeWeights_.begin();
    }

private:
    std::vector<double> CumulativeWeights_;
    double TotalWeight_;

    double RandomDouble() {
        // 快速随机数生成
        static thread_local std::mt19937 generator(std::random_device{}());
        static thread_local std::uniform_real_distribution<double> distribution(0.0, 1.0);
        return distribution(generator);
    }
};
```

## 最佳实践

### 1. 种子管理
```cpp
class RandomManager {
public:
    static RandomManager& Get() {
        static RandomManager instance;
        return instance;
    }

    ui64 GetSeed() const {
        return Seed_;
    }

    ui64 NextSeed() {
        return ++Seed_;
    }

private:
    RandomManager() : Seed_(std::chrono::high_resolution_clock::now().time_since_epoch().count()) {}

    std::atomic<ui64> Seed_;
};

// 使用
ui64 seed = RandomManager::Get().NextSeed();
TBernoulliSampler sampler(0.1, seed);
```

### 2. 线程安全
```cpp
class ThreadSafeSampler {
public:
    ThreadSafeSampler(double samplingRate)
        : SamplingRate_(samplingRate)
    {}

    bool Sample() {
        // 每个线程使用独立的采样器
        thread_local TBernoulliSampler sampler(SamplingRate_);
        return sampler.Sample();
    }

private:
    double SamplingRate_;
};
```

### 3. 采样率调整
```cpp
class AdaptiveSampler {
public:
    AdaptiveSampler(double baseRate)
        : BaseRate_(baseRate)
        , CurrentRate_(baseRate)
        , Sampler_(baseRate)
    {}

    bool Sample() {
        if (Sampler_.Sample()) {
            ++SuccessCount_;
            return true;
        } else {
            ++FailureCount_;
            return false;
        }
    }

    void AdjustRate() {
        // 每1000次采样调整一次
        if ((SuccessCount_ + FailureCount_) >= 1000) {
            double actualRate = static_cast<double>(SuccessCount_) /
                              (SuccessCount_ + FailureCount_);

            // 调整到接近目标率
            if (actualRate < BaseRate_ * 0.9) {
                CurrentRate_ = std::min(CurrentRate_ * 1.1, 1.0);
            } else if (actualRate > BaseRate_ * 1.1) {
                CurrentRate_ = std::max(CurrentRate_ * 0.9, 0.001);
            }

            // 更新采样器
            Sampler_ = TBernoulliSampler(CurrentRate_);

            // 重置计数
            SuccessCount_ = 0;
            FailureCount_ = 0;
        }
    }

private:
    double BaseRate_;
    double CurrentRate_;
    TBernoulliSampler Sampler_;
    int SuccessCount_ = 0;
    int FailureCount_ = 0;
};
```

## 注意事项

1. **确定性**: 使用相同的种子和盐会得到相同结果
2. **线程安全**: 每个线程应使用独立的采样器
3. **精度**: 浮点数精度可能影响采样率的准确性
4. **性能**: Mersenne Twerry 适合一般用途，特殊场景考虑其他算法
5. **持久化**: 采样器状态可以持久化以保持一致性

## 依赖项

- C++ 标准库 (`<random>`)
- YTsaurus 核心库 (`yt/yt/core/`)