# GPU (GPU管理)

GPU 库是 YTsaurus 中用于管理和监控 GPU 设备的组件，提供 GPU 信息收集、状态监控和资源管理功能。

## 概述

GPU 库提供以下核心功能：
- GPU 设备信息收集
- GPU 利用率和性能监控
- GPU 内存使用情况跟踪
- 网络设备（RDMA）信息管理
- 网络服务级别配置

## 核心组件

### 1. IGpuInfoProvider (GPU信息提供器)
GPU 信息获取的主要接口：

```cpp
struct IGpuInfoProvider : public TRefCounted {
    // 获取 GPU 信息
    virtual std::vector<TGpuInfo> GetGpuInfos(TDuration timeout) const = 0;

    // 获取 RDMA 设备信息
    virtual std::vector<TRdmaDeviceInfo> GetRdmaDeviceInfos(TDuration timeout) const = 0;

    // 应用网络服务级别
    virtual void ApplyNetworkServiceLevel(
        const std::vector<TString>& deviceIds,
        TNetworkPriority networkServiceLevel,
        TDuration timeout) = 0;
};
```

### 2. GPU 信息提供器实现
- **NvidiaSmiGpuInfoProvider**: 通过 nvidia-smi 获取信息
- **GpuAgentGpuInfoProvider**: 通过 GPU Agent 获取信息
- **NvManagerGpuInfoProvider**: 通过 NV Manager 获取信息

### 3. TGpuInfo (GPU信息结构)
包含 GPU 的详细状态信息：

```cpp
struct TGpuInfo {
    TInstant UpdateTime;           // 更新时间
    int Index;                     // GPU索引
    TString Name;                  // GPU名称

    // 利用率信息
    double UtilizationGpuRate;     // GPU利用率
    double UtilizationMemoryRate;  // 内存利用率
    double SMUtilizationRate;      // SM流处理器利用率
    double SMOccupancyRate;        // SM占用率
    double TensorActivityRate;     // Tensor核心活动率
    double DramActivityRate;       // DRAM活动率

    // 内存信息
    i64 MemoryUsed;                // 已使用内存
    i64 MemoryTotal;               // 总内存

    // 功耗信息
    double PowerDraw;              // 当前功耗
    double PowerLimit;             // 功耗限制

    // 时钟信息
    i64 ClocksSM;                  // 当前SM时钟
    i64 ClocksMaxSM;               // 最大SM时钟

    // 网络吞吐量
    double NvlinkRxByteRate;       // NVLink接收速率
    double NvlinkTxByteRate;       // NVLink发送速率
    double PcieRxByteRate;         // PCIe接收速率
    double PcieTxByteRate;         // PCIe发送速率

    // 降速状态
    TEnumIndexedArray<ESlowdownType, bool> Slowdowns;

    // 卡死状态
    struct {
        bool Status;                           // 是否卡死
        std::optional<TInstant> LastTransitionTime; // 最后状态转换时间
    } Stuck;
};
```

### 4. TRdmaDeviceInfo (RDMA设备信息)
RDMA 网络设备的信息：

```cpp
struct TRdmaDeviceInfo {
    TString Name;             // 设备名称
    TString DeviceId;         // 设备ID
    double RxByteRate;        // 接收速率
    double TxByteRate;        // 发送速率
};
```

## 配置

### 基础配置
```cpp
struct TGpuInfoProviderConfigBase : public NYTree::TYsonStruct {
    // 获取GPU信息的超时时间
    TDuration GpuInfoFetchingTimeout;

    // 获取RDMA设备信息的超时时间
    TDuration RdmaInfoFetchingTimeout;
};
```

### GPU Agent 配置
```cpp
struct TGpuAgentGpuInfoProviderConfig : public TGpuInfoProviderConfigBase {
    // GPU Agent 地址
    TString GpuAgentAddress;

    // GPU Agent 端口
    int GpuAgentPort;
};
```

### NV Manager 配置
```cpp
struct TNvManagerGpuInfoProviderConfig : public TGpuInfoProviderConfigBase {
    // NV Manager 地址
    TString NvManagerAddress;

    // NV Manager 端口
    int NvManagerPort;
};
```

## 使用方法

### 创建 GPU 信息提供器
```cpp
// 创建 Nvidia SMI 提供器
auto config = New<TNvidiaSmiGpuInfoProviderConfig>();
config->SetGpuInfoFetchingTimeout(TDuration::Seconds(10));
auto provider = CreateGpuInfoProvider(*config);

// 创建 GPU Agent 提供器
auto agentConfig = New<TGpuAgentGpuInfoProviderConfig>();
agentConfig->SetGpuAgentAddress("localhost");
agentConfig->SetGpuAgentPort(9090);
auto agentProvider = CreateGpuInfoProvider(*agentConfig);
```

### 获取 GPU 信息
```cpp
// 获取 GPU 信息
try {
    auto gpuInfos = provider->GetGpuInfos(TDuration::Seconds(5));

    for (const auto& gpu : gpuInfos) {
        Cout << "GPU " << gpu.Index << ": " << gpu.Name << Endl;
        Cout << "  Utilization: " << gpu.UtilizationGpuRate * 100 << "%" << Endl;
        Cout << "  Memory: " << gpu.MemoryUsed / (1024*1024) << "MB / "
             << gpu.MemoryTotal / (1024*1024) << "MB" << Endl;
        Cout << "  Power: " << gpu.PowerDraw << "W / " << gpu.PowerLimit << "W" << Endl;
    }
} catch (const std::exception& e) {
    Cerr << "Failed to get GPU info: " << e.what() << Endl;
}
```

### 获取 RDMA 设备信息
```cpp
auto rdmaDevices = provider->GetRdmaDeviceInfos(TDuration::Seconds(5));
for (const auto& device : rdmaDevices) {
    Cout << "RDMA Device: " << device.Name << Endl;
    Cout << "  RX Rate: " << device.RxByteRate << " bytes/s" << Endl;
    Cout << "  TX Rate: " << device.TxByteRate << " bytes/s" << Endl;
}
```

### 配置网络服务级别
```cpp
std::vector<TString> deviceIds = {"gpu0", "gpu1"};
TNetworkPriority priority = 3; // 高优先级

provider->ApplyNetworkServiceLevel(
    deviceIds,
    priority,
    TDuration::Seconds(10));
```

## 降速类型

系统监控多种降速原因：

```cpp
enum class ESlowdownType {
    HW,           // 硬件限流
    HWPowerBrake,  // 硬件功耗限制
    HWThermal,     // 硬件温度限制
    SWThermal      // 软件温度限制
};
```

## 性能指标

### GPU 利用率指标
- **GPU 利用率**: 整体 GPU 使用率
- **SM 利用率**: 流处理器使用率
- **SM 占用率**: 流处理器占用率
- **Tensor 活动率**: Tensor 核心活动率
- **DRAM 活动率**: 内存活动率

### 内存指标
- **已使用内存**: 当前 GPU 内存使用量
- **总内存**: GPU 总内存容量
- **内存利用率**: 内存使用百分比

### 功耗指标
- **当前功耗**: 实时功耗
- **功耗限制**: 最大允许功耗

### 网络指标
- **NVLink 带宽**: GPU 间高速互联带宽
- **PCIe 带宽**: 与主机通信带宽
- **RDMA 带宽**: 远程直接内存访问带宽

## 最佳实践

### 1. 定期监控
```cpp
// 设置定时任务
class GpuMonitor {
public:
    void Start() {
        Executor_ = New<TPeriodicExecutor>(
            GetSyncInvoker(),
            BIND(&GpuMonitor::Monitor, this),
            TDuration::Seconds(30));
        Executor_->Start();
    }

private:
    void Monitor() {
        auto infos = Provider_->GetGpuInfos(TDuration::Seconds(10));
        // 处理GPU信息
    }

    IGpuInfoProviderPtr Provider_;
    TPeriodicExecutorPtr Executor_;
};
```

### 2. 错误处理
```cpp
auto provider = CreateGpuInfoProvider(config);

try {
    auto gpuInfos = provider->GetGpuInfos(TDuration::Seconds(5));
    // 检查 GPU 状态
    for (const auto& gpu : gpuInfos) {
        if (gpu.Stuck.Status) {
            YT_LOG_ERROR("GPU %v is stuck!", gpu.Index);
            // 采取措施
        }

        // 检查降速状态
        for (auto [type, active] : gpu.Slowdowns) {
            if (active) {
                YT_LOG_WARNING("GPU %v slowdown: %v", gpu.Index, type);
            }
        }
    }
} catch (const TErrorException& e) {
    YT_LOG_ERROR(e, "Failed to get GPU info");
}
```

### 3. 性能优化
- 合理设置超时时间
- 批量获取信息而非频繁查询
- 使用缓存减少重复请求

## 依赖项

- YTsaurus 核心库 (`yt/yt/core/`)
- YTree 库 (`yt/yt/core/ytree/`)
- YSON 库 (`yt/yt/core/yson/`)
- Nvidia 驱动和 CUDA 工具包（nvidia-smi）

## 注意事项

1. **权限要求**: 需要 root 权限或适当的用户组权限
2. **驱动依赖**: 必须安装正确的 Nvidia 驱动
3. **网络配置**: RDMA 功能需要正确配置 InfiniBand
4. **监控开销**: 避免过于频繁的查询
5. **错误恢复**: 实现适当的错误处理和重试机制