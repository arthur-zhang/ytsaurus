# Disk Manager (磁盘管理器)

磁盘管理器是 YTsaurus 分布式存储系统中的核心组件，负责管理集群节点的磁盘设备、监控磁盘状态并提供磁盘热插拔功能。

## 概述

磁盘管理器提供了统一的磁盘管理接口，支持：
- 磁盘设备发现和状态监控
- 磁盘故障检测和自动恢复
- 磁盘热插拔支持
- 多种存储类型管理（HDD、SSD、NVMe等）

## 核心组件

### 1. 磁盘信息提供器 (Disk Info Provider)
- **文件**: `disk_info_provider.h/cpp`
- **功能**: 提供磁盘信息的获取和缓存
- **主要接口**:
  - `GetYTDiskInfos()`: 获取 YT 磁盘信息
  - `UpdateDiskCache()`: 更新磁盘缓存
  - `RecoverDisk()`: 恢复故障磁盘
  - `FailDisk()`: 标记磁盘为故障状态

### 2. 热插拔管理器 (Hotswap Manager)
- **文件**: `hotswap_manager.h/cpp`
- **功能**: 管理磁盘的热插拔操作
- **主要接口**:
  - `Reconfigure()`: 动态重配置
  - `GetDiskInfoProvider()`: 获取磁盘信息提供器
  - `PopulateAlerts()`: 填充告警信息
  - `GetOrchidService()`: 获取 Orchid 监控服务

### 3. 磁盘管理器代理 (Disk Manager Proxy)
- **文件**: `disk_manager_proxy.h/cpp`
- **功能**: 提供磁盘管理的远程调用接口
- **说明**: 包含代理实现和存根，用于跨进程通信

## 数据结构

### 磁盘状态 (EDiskState)
```cpp
enum class EDiskState {
    Unknown = 0,     // 未知状态
    OK = 1,          // 正常状态
    Failed = 2,      // 故障状态
    RecoverWait = 3  // 等待恢复
};
```

### 存储类型 (EStorageClass)
```cpp
enum class EStorageClass {
    Unknown = 0,  // 未知类型
    Hdd = 1,      // 机械硬盘
    Ssd = 2,      // 固态硬盘
    Nvme = 3,     // NVMe 硬盘
    Virt = 4      // 虚拟磁盘
};
```

### 恢复策略 (ERecoverPolicy)
```cpp
enum class ERecoverPolicy {
    RecoverAuto = 0,   // 自动恢复
    RecoverMount = 1,  // 重新挂载
    RecoverLayout = 2, // 重建布局
    RecoverDisk = 3    // 更换物理磁盘
};
```

### 磁盘信息 (TDiskInfo)
```cpp
struct TDiskInfo {
    std::string DiskId;                    // 磁盘ID
    std::string DevicePath;                // 设备路径
    std::string DeviceName;                // 设备名称
    std::string DiskModel;                 // 磁盘型号
    THashSet<std::string> PartitionFsLabels; // 分区文件系统标签
    EDiskState State;                      // 磁盘状态
    EStorageClass StorageClass;            // 存储类型
};
```

## 配置

### 磁盘信息提供器配置 (TDiskInfoProviderConfig)
- 配置磁盘信息提供器的行为参数
- 支持动态更新

### 热插拔管理器配置 (THotswapManagerConfig)
- 配置热插拔功能的参数
- 支持运行时动态重配置

## 使用方法

### 创建磁盘信息提供器
```cpp
auto diskManagerProxy = CreateDiskManagerProxy(proxyConfig);
auto config = New<TDiskInfoProviderConfig>();
auto diskInfoProvider = CreateDiskInfoProvider(diskManagerProxy, config);
```

### 创建热插拔管理器
```cpp
auto config = New<THotswapManagerConfig>();
auto hotswapManager = CreateHotswapManager(config);
```

### 获取磁盘信息
```cpp
auto diskInfos = WaitFor(diskInfoProvider->GetYTDiskInfos())
    .ValueOrThrow();
for (const auto& diskInfo : diskInfos) {
    std::cout << "Disk: " << diskInfo.DiskId
              << " State: " << diskInfo.State << std::endl;
}
```

## 监控和告警

磁盘管理器通过 Orchid 提供监控接口：
- 磁盘状态实时监控
- 磁盘使用率统计
- 故障告警信息
- 热插拔操作日志

## 错误处理

- 所有异步操作返回 `TFuture`，支持错误处理
- 使用 `TError` 对象传递详细错误信息
- 支持错误码和错误消息的组合

## 依赖项

- YT 核心库 (`yt/yt/core/`)
- 内存管理库 (`library/cpp/yt/memory/`)
- 类型系统库 (`library/cpp/yt/misc/`)
- 并发库 (`yt/yt/core/actions/`)

## 实现原理

1. **磁盘发现**: 通过系统调用和设备文件发现磁盘
2. **状态监控**: 定期检查磁盘健康状态
3. **故障恢复**: 根据配置策略自动恢复故障磁盘
4. **热插拔**: 监听设备事件，支持磁盘热插拔
5. **缓存机制**: 缓存磁盘信息减少系统调用开销

## 注意事项

1. 磁盘操作需要 root 权限
2. 热插拔功能需要内核支持
3. 恢复策略需要谨慎选择，避免数据丢失
4. 配置更改支持动态生效，无需重启服务