# bucket_quoter

令牌桶限流器实现，提供了基于令牌桶算法的流量控制功能，用于平滑和控制请求速率。

## 功能描述

bucket_quoter 实现了经典的令牌桶算法 (Token Bucket Algorithm)，可以平滑地控制流量，允许一定程度的突发传输，同时限制平均速率。适用于网络流量控制、API 限流等场景。

## 核心特性

- **令牌桶算法**：实现标准的令牌桶限流算法
- **平滑限流**：支持平均速率控制，允许突发
- **可配置参数**：灵活配置速率和容量
- **线程安全**：使用原子操作保证线程安全
- **高精度定时**：支持毫秒级精度控制
- **阻塞等待**：支持同步等待获取令牌

## 算法原理

令牌桶算法的工作原理：

1. **令牌生成**：以固定速率向桶中添加令牌
2. **桶容量**：桶中令牌数量有上限
3. **令牌消费**：处理请求时消耗相应数量的令牌
4. **等待策略**：令牌不足时可选择等待或拒绝

```
      ┌───────────────┐
      │  令牌生成速率  │  inflow (单位/秒)
      └──────┬────────┘
             │
             ▼
      ┌───────────────┐
      │      桶       │  ───► 最多 capacity 个令牌
      └──────┬────────┘
             │
             ▼
      ┌───────────────┐
      │   请求处理     │  每个请求消耗令牌
      └───────────────┘
```

## 主要组件

### TBucketQuoter
核心令牌桶实现类：

```cpp
class TBucketQuoter {
public:
    // 构造函数
    TBucketQuoter(
        ui64 inflow,      // 平均速率 (单位/秒)
        ui64 capacity,    // 桶容量 (单位)
        TMutex* mutex = nullptr,      // 可选互斥锁
        TCondVar* condvar = nullptr,  // 可选条件变量
        TInstant* now = nullptr       // 可选时间源
    );

    // 主要方法
    void Use(ui64 count);     // 消耗指定数量令牌
    void Sleep();             // 等待直到有令牌可用
    ui64 Available() const;   // 获取当前可用令牌数
};
```

## 使用示例

### 基本使用
```cpp
#include <library/cpp/bucket_quoter/bucket_quoter.h>

// 创建限流器：1000 字节/秒，最多累积 60 秒的配额
TBucketQuoter quoter(1000, 60000);

for (;;) {
    // 获取消息
    auto msg = GetMessage();

    // 等待令牌
    quoter.Sleep();

    // 使用令牌
    quoter.Use(msg->GetSize());

    // 发送消息
    SendMessage(msg);
}
```

### API 限流
```cpp
// 限制 API 调用：每秒 100 次请求
TBucketQuoter apiLimiter(100, 100);

void ProcessRequest(Request* req) {
    // 等待可用令牌
    apiLimiter.Sleep();

    // 处理请求
    apiLimiter.Use(1);
    HandleRequest(req);
}
```

### 多线程环境
```cpp
// 创建共享的互斥锁和条件变量
TMutex mutex;
TCondVar condvar;

// 创建限流器
TBucketQuoter quoter(1000, 5000, &mutex, &condvar);

void WorkerThread() {
    for (int i = 0; i < 100; ++i) {
        with_lock(mutex) {
            quoter.Sleep();
            quoter.Use(1);
        }
        DoWork();
    }
}
```

## 高级功能

### 自定义时间源
```cpp
// 使用自定义时间源进行测试
class MockTimeSource {
    TInstant time;
public:
    TInstant Now() const { return time; }
    void Advance(TDuration delta) { time += delta; }
};

MockTimeSource mockTime;
TBucketQuoter quoter(100, 1000, nullptr, nullptr, &mockTime.Now);

// 测试场景
mockTime.Advance(TDuration::Seconds(10));
```

### 多级限流
```cpp
// 实现多级限流策略
class MultiLevelLimiter {
    TBucketQuoter minuteLimiter;  // 分钟级限制
    TBucketQuoter secondLimiter;  // 秒级限制

public:
    MultiLevelLimiter()
        : minuteLimiter(6000, 60000)    // 100/秒 平均
        , secondLimiter(150, 300)       // 150/秒 突发
    {}

    void Acquire() {
        secondLimiter.Sleep();
        secondLimiter.Use(1);
        minuteLimiter.Sleep();
        minuteLimiter.Use(1);
    }
};
```

## 性能特性

### 时间复杂度
- **Acquire**：O(1)
- **Use**：O(1)
- **Available**：O(1)

### 空间复杂度
- **存储**：O(1) 固定大小

### 高精度
- 使用高精度计时器 (HP_TIMER)
- 支持微秒级精度
- 时间累积误差最小化

## 应用场景

### 网络流量控制
```cpp
// 限制带宽：10MB/s，允许 100MB 突发
TBucketQuoter bandwidthLimiter(10 * 1024 * 1024, 100 * 1024 * 1024);
```

### API 服务限流
```cpp
// 用户级别限流：每用户 100 请求/分钟
class UserRateLimiter {
    THashMap<ui32, TBucketQuoter> userLimiters;

public:
    bool CheckRate(ui32 userId) {
        auto& limiter = userLimiters[userId];
        if (limiter.Available() > 0) {
            limiter.Use(1);
            return true;
        }
        return false;
    }
};
```

### 数据库连接池
```cpp
// 限制数据库查询速率
TBucketQuoter dbQueryLimiter(1000, 2000);  // 平均 1000/s，突发 2000
```

### 消息队列
```cpp
// 平滑消息消费速率
TBucketQuoter consumerLimiter(500, 1000);  // 消费速率限制
```

## 配置参数

### 速率 (Inflow)
- **单位**：令牌/秒
- **范围**：1 到 2^64-1
- **建议**：根据系统容量设置

### 容量 (Capacity)
- **单位**：令牌数
- **范围**：inflow 到 2^64-1
- **建议**：通常设置为 inflow 的 10-60 倍

### 时间精度
- **默认**：毫秒级
- **最大精度**：微秒级（取决于平台）
- **建议**：根据应用需求选择

## 注意事项

1. **不是严格限流**：令牌桶允许一定程度的突发，不适合需要严格限制的场景
2. **时钟依赖**：依赖于系统时钟的准确性
3. **线程安全**：多线程使用时需要提供同步原语
4. **资源泄漏**：长时间运行需要监控令牌累积

## 调试和监控

### 状态查询
```cpp
// 获取当前状态
ui64 available = quoter.Available();
ui64 capacity = quoter.GetCapacity();
ui64 inflow = quoter.GetInflow();
```

### 性能监控
```cpp
// 计平均速率
ui64 totalUsed = 0;
TInstant startTime = Now();

// ... 运行一段时间 ...

TDuration elapsed = Now() - startTime;
double avgRate = double(totalUsed) / elapsed.Seconds();
```

## 扩展实现

### 动态限流
```cpp
class DynamicBucketQuoter : public TBucketQuoter {
public:
    void UpdateRate(ui64 newInflow) {
        SetInflow(newInflow);
    }

    void UpdateCapacity(ui64 newCapacity) {
        SetCapacity(newCapacity);
    }
};
```

### 优先级限流
```cpp
class PriorityBucketQuoter {
    TBucketQuoter highPriority;
    TBucketQuoter lowPriority;

public:
    bool Acquire(bool highPriority = false) {
        if (highPriority) {
            return highPriority.TryUse(1);
        } else {
            return lowPriority.TryUse(1);
        }
    }
};
```