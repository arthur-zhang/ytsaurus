# YTSys - YTsaurus 系统工具库

## 概述

`ytsys` 包提供了 YTsaurus 系统相关的工具和数据结构定义。该包包含集群角色定义、网络工具、节点类型、系统常量等系统级功能。

## 核心组件

### 1. 集群角色定义

定义了 YTsaurus 集群中各种组件的角色：

```go
type ClusterRole string

const (
    RoleNode              ClusterRole = "node"               // 数据节点
    RolePrimaryMaster     ClusterRole = "primary_master"     // 主 Master
    RoleSecondaryMaster   ClusterRole = "secondary_master"   // 备 Master
    RoleTimestampProvider ClusterRole = "timestamp_provider" // 时间戳服务
    RoleHTTPProxy         ClusterRole = "http_proxy"         // HTTP 代理
    RoleRPCProxy          ClusterRole = "rpc_proxy"          // RPC 代理
    RoleScheduler         ClusterRole = "scheduler"          // 调度器
    RoleControllerAgent   ClusterRole = "controller_agent"   // 控制器代理
    RoleQueueAgent        ClusterRole = "queue_agent"        // 队列代理
)
```

### 2. 节点类型和标签

```go
// 节点类型
const (
    FlavorData   = "data"    // 数据节点
    FlavorExec   = "exec"    // 计算节点
    FlavorTablet = "tablet"  // Tablet 节点
)

// 节点标签
const (
    TabletCommonTag = "tablet_common" // Tablet 通用标签
    GPUTag         = "gpu"           // GPU 标签
    GPUProdTag     = "gpu_prod"      // 生产环境 GPU 标签
)

type PhysicalHost = string
```

### 3. 代理角色类型

```go
type YTProxyRole string

const (
    ProxyRoleDefault          YTProxyRole = "default"
    ProxyRoleMasterCache      YTProxyRole = "master_cache"
    ProxyRoleRpc              YTProxyRole = "rpc"
    ProxyRoleSecondaryMaster  YTProxyRole = "secondary_master"
)
```

### 4. 系统工具

提供系统工具和验证函数：

```go
// 网络工具
func ParseHostPort(s string) (string, int, error)
func SplitHostPort(hostPort string) (host string, port int, err error)
func JoinHostPort(host string, port int) string

// 地址验证
func IsValidAddress(addr string) bool
func IsValidHostPort(hostPort string) bool
func IsValidPort(port int) bool
```

## 数据类型定义

### Agent 信息

```go
type AgentInfo struct {
    Version      string    `yson:"version"`       // 代理版本
    StartTime    time.Time `yson:"start_time"`    // 启动时间
    Pid          int       `yson:"pid"`           // 进程ID
    Hostname     string    `yson:"hostname"`      // 主机名
    User         string    `yson:"user"`          // 用户
    Uptime       string    `yson:"uptime"`        // 运行时间
    Environment  string    `yson:"environment"`   // 环境
    YAMLConfig   string    `yson:"yaml_config"`   // YAML 配置
    Statistics   string    `yson:"statistics"`    // 统计信息
}
```

### 客户端统计信息

```go
type ClientStatistics struct {
    Version          string `yson:"version"`          // 版本
    StartTime        string `yson:"start_time"`       // 启动时间
    Uptime           string `yson:"uptime"`           // 运行时间
    User             string `yson:"user"`             // 用户
    Hostname         string `yson:"hostname"`         // 主机名
    Pid              int    `yson:"pid"`              // 进程ID
    ThreadCount      int    `yson:"thread_count"`     // 线程数
    FdCount          int    `yson:"fd_count"`         // 文件描述符数
    MemoryUsage      int64  `yson:"memory_usage"`     // 内存使用量
    MemoryLimit      int64  `yson:"memory_limit"`     // 内存限制
    CpuUsage         int64  `yson:"cpu_usage"`        // CPU 使用量
    TrafficIn        int64  `yson:"traffic_in"`       // 入站流量
    TrafficOut       int64  `yson:"traffic_out"`      // 出站流量
    RequestCount     int64  `yson:"request_count"`    // 请求计数
    RequestQueueSize int    `yson:"request_queue_size"` // 请求队列大小
}
```

### 数据完整性信息

```go
type DataIntegrityInfo struct {
    Host                string    `yson:"host"`                  // 主机
    MediumType          string    `yson:"medium_type"`          // 存储类型
    Location            string    `yson:"location"`             // 位置
    VerifyProgress      int       `yson:"verify_progress"`      // 验证进度
    LastVerificationTime time.Time `yson:"last_verification_time"` // 最后验证时间
    ChunkCount          int       `yson:"chunk_count"`          // Chunk 数量
    CorruptedChunkCount int       `yson:"corrupted_chunk_count"` // 损坏 Chunk 数量
}
```

## 网络和地址工具

### 地址解析

```go
package main

import (
    "fmt"
    "go.ytsaurus.tech/yt/go/ytsys"
)

func main() {
    // 解析主机端口
    host, port, err := ytsys.ParseHostPort("localhost:8080")
    if err != nil {
        panic(err)
    }

    fmt.Printf("主机: %s, 端口: %d\n", host, port)

    // 验证地址
    if ytsys.IsValidAddress("192.168.1.1:9000") {
        fmt.Println("地址有效")
    }

    // 验证端口
    if ytsys.IsValidPort(8080) {
        fmt.Println("端口有效")
    }

    // 组合主机端口
    addr := ytsys.JoinHostPort("localhost", 8080)
    fmt.Printf("组合地址: %s\n", addr)
}
```

### 网络工具使用

```go
package main

import (
    "fmt"
    "net"
    "go.ytsaurus.tech/yt/go/ytsys"
)

func main() {
    // 解析网络地址
    addr := "192.168.1.100:9000"
    host, port, err := ytsys.ParseHostPort(addr)
    if err != nil {
        fmt.Printf("解析失败: %v\n", err)
        return
    }

    fmt.Printf("主机: %s\n", host)
    fmt.Printf("端口: %d\n", port)

    // 验证主机可达性
    if net.ParseIP(host) != nil {
        fmt.Printf("%s 是有效的 IP 地址\n", host)
    }

    // 检查端口范围
    if port > 0 && port <= 65535 {
        fmt.Printf("%d 是有效的端口号\n", port)
    }
}
```

## 系统信息获取

### 客户端统计

```go
package main

import (
    "fmt"
    "go.ytsaurus.tech/yt/go/ytsys"
)

func main() {
    // 创建客户端统计信息
    stats := ytsys.ClientStatistics{
        Version:      "1.0.0",
        Hostname:     "worker-01",
        Pid:          12345,
        ThreadCount:  8,
        MemoryUsage:  1024 * 1024 * 1024, // 1GB
        RequestCount: 1000000,
    }

    fmt.Printf("客户端统计信息:\n")
    fmt.Printf("  版本: %s\n", stats.Version)
    fmt.Printf("  主机: %s\n", stats.Hostname)
    fmt.Printf("  PID: %d\n", stats.Pid)
    fmt.Printf("  线程数: %d\n", stats.ThreadCount)
    fmt.Printf("  内存使用: %d MB\n", stats.MemoryUsage/1024/1024)
    fmt.Printf("  请求计数: %d\n", stats.RequestCount)
}
```

### 代理信息

```go
package main

import (
    "fmt"
    "time"
    "go.ytsaurus.tech/yt/go/ytsys"
)

func main() {
    // 创建代理信息
    agent := ytsys.AgentInfo{
        Version:     "21.3.0",
        StartTime:   time.Now().Add(-time.Hour * 24),
        Pid:         54321,
        Hostname:    "proxy-server-01",
        User:        "ytuser",
        Environment: "production",
    }

    fmt.Printf("代理信息:\n")
    fmt.Printf("  版本: %s\n", agent.Version)
    fmt.Printf("  启动时间: %s\n", agent.StartTime.Format(time.RFC3339))
    fmt.Printf("  进程ID: %d\n", agent.Pid)
    fmt.Printf("  主机名: %s\n", agent.Hostname)
    fmt.Printf("  用户: %s\n", agent.User)
    fmt.Printf("  环境: %s\n", agent.Environment)
}
```

## 数据完整性验证

```go
package main

import (
    "fmt"
    "time"
    "go.ytsaurus.tech/yt/go/ytsys"
)

func main() {
    // 创建数据完整性信息
    integrity := ytsys.DataIntegrityInfo{
        Host:                "storage-node-01",
        MediumType:          "hdd",
        Location:            "/data/1",
        VerifyProgress:      75,
        LastVerificationTime: time.Now().Add(-time.Hour * 2),
        ChunkCount:          100000,
        CorruptedChunkCount: 5,
    }

    fmt.Printf("数据完整性信息:\n")
    fmt.Printf("  主机: %s\n", integrity.Host)
    fmt.Printf("  存储类型: %s\n", integrity.MediumType)
    fmt.Printf("  位置: %s\n", integrity.Location)
    fmt.Printf("  验证进度: %d%%\n", integrity.VerifyProgress)
    fmt.Printf("  最后验证时间: %s\n", integrity.LastVerificationTime.Format(time.RFC3339))
    fmt.Printf("  Chunk 总数: %d\n", integrity.ChunkCount)
    fmt.Printf("  损坏 Chunk 数: %d\n", integrity.CorruptedChunkCount)

    // 计算损坏率
    corruptionRate := float64(integrity.CorruptedChunkCount) / float64(integrity.ChunkCount) * 100
    fmt.Printf("  损坏率: %.2f%%\n", corruptionRate)
}
```

## 集群角色管理

```go
package main

import (
    "fmt"
    "go.ytsaurus.tech/yt/go/ytsys"
)

func main() {
    // 定义集群组件
    components := []struct {
        Role   ytsys.ClusterRole
        Count  int
        Status string
    }{
        {ytsys.RoleNode, 100, "运行中"},
        {ytsys.RolePrimaryMaster, 1, "运行中"},
        {ytsys.RoleSecondaryMaster, 2, "运行中"},
        {ytsys.RoleHTTPProxy, 5, "运行中"},
        {ytsys.RoleRPCProxy, 3, "运行中"},
        {ytsys.RoleScheduler, 2, "运行中"},
        {ytsys.RoleControllerAgent, 4, "运行中"},
    }

    fmt.Println("集群组件状态:")
    for _, comp := range components {
        fmt.Printf("  %s: %d 个 (%s)\n", comp.Role, comp.Count, comp.Status)
    }

    // 检查关键组件
    criticalRoles := []ytsys.ClusterRole{
        ytsys.RolePrimaryMaster,
        ytsys.RoleScheduler,
        ytsys.RoleHTTPProxy,
    }

    fmt.Println("\n关键组件检查:")
    for _, role := range criticalRoles {
        var found bool
        var count int
        for _, comp := range components {
            if comp.Role == role {
                found = true
                count = comp.Count
                break
            }
        }
        if found {
            fmt.Printf("  %s: %d 个 ✓\n", role, count)
        } else {
            fmt.Printf("  %s: 缺失 ✗\n", role)
        }
    }
}
```

## 节点标签和类型管理

```go
package main

import (
    "fmt"
    "go.ytsaurus.tech/yt/go/ytsys"
)

func main() {
    // 节点标签示例
    nodeTags := map[string][]string{
        "node-01": {ytsys.TabletCommonTag, "fast_storage"},
        "node-02": {ytsys.GPUTag, ytsys.GPUProdTag},
        "node-03": {ytsys.TabletCommonTag},
        "node-04": {"compute_optimized"},
    }

    fmt.Println("节点标签分布:")
    for node, tags := range nodeTags {
        fmt.Printf("  %s: %v\n", node, tags)
    }

    // 节点类型统计
    flavorCount := map[string]int{
        ytsys.FlavorData:   50,
        ytsys.FlavorExec:   30,
        ytsys.FlavorTablet: 20,
    }

    fmt.Println("\n节点类型分布:")
    for flavor, count := range flavorCount {
        fmt.Printf("  %s: %d 个\n", flavor, count)
    }

    // 检查特定标签的节点
    gpuNodes := []string{}
    tabletNodes := []string{}

    for node, tags := range nodeTags {
        for _, tag := range tags {
            if tag == ytsys.GPUTag {
                gpuNodes = append(gpuNodes, node)
            }
            if tag == ytsys.TabletCommonTag {
                tabletNodes = append(tabletNodes, node)
            }
        }
    }

    fmt.Printf("\nGPU 节点: %v\n", gpuNodes)
    fmt.Printf("Tablet 节点: %v\n", tabletNodes)
}
```

## 使用示例

### 集群状态监控

```go
package main

import (
    "fmt"
    "go.ytsaurus.tech/yt/go/ytsys"
)

type ClusterStatus struct {
    Nodes       int
    Masters     int
    Proxies     int
    Schedulers  int
    Controllers int
}

func main() {
    // 模拟集群状态
    status := ClusterStatus{
        Nodes:       100,
        Masters:     3,
        Proxies:     8,
        Schedulers:  2,
        Controllers: 4,
    }

    fmt.Println("YTsaurus 集群状态:")
    fmt.Printf("  数据节点: %d\n", status.Nodes)
    fmt.Printf("  Master 节点: %d\n", status.Masters)
    fmt.Printf("  代理节点: %d\n", status.Proxies)
    fmt.Printf("  调度器: %d\n", status.Schedulers)
    fmt.Printf("  控制器: %d\n", status.Controllers)

    // 检查集群健康状态
    if status.Masters >= 3 && status.Schedulers >= 1 {
        fmt.Println("✓ 集群状态健康")
    } else {
        fmt.Println("✗ 集群状态异常")
    }
}
```

### 地址验证工具

```go
package main

import (
    "fmt"
    "go.ytsaurus.tech/yt/go/ytsys"
)

func validateClusterNodes(nodes []string) {
    fmt.Println("验证集群节点地址:")
    for _, node := range nodes {
        host, port, err := ytsys.ParseHostPort(node)
        if err != nil {
            fmt.Printf("  ✗ %s: 解析失败 - %v\n", node, err)
            continue
        }

        if !ytsys.IsValidHostPort(node) {
            fmt.Printf("  ✗ %s: 无效的主机端口组合\n", node)
            continue
        }

        if !ytsys.IsValidPort(port) {
            fmt.Printf("  ✗ %s: 无效的端口 %d\n", node, port)
            continue
        }

        fmt.Printf("  ✓ %s (主机: %s, 端口: %d)\n", node, host, port)
    }
}

func main() {
    clusterNodes := []string{
        "node-01.yt.local:9000",
        "node-02.yt.local:9001",
        "invalid-address",          // 无效地址
        "node-03.yt.local:99999",   // 无效端口
        "192.168.1.100:9000",       // 有效 IP 地址
    }

    validateClusterNodes(clusterNodes)
}
```

## 最佳实践

### 1. 地址验证

```go
// 推荐：使用系统工具验证地址
if !ytsys.IsValidHostPort(hostPort) {
    return fmt.Errorf("无效的主机端口地址: %s", hostPort)
}

// 推荐：解析后再使用
host, port, err := ytsys.ParseHostPort(hostPort)
if err != nil {
    return err
}
```

### 2. 集群角色管理

```go
// 推荐：使用常量定义角色
role := ytsys.RoleScheduler

// 不推荐：使用字符串字面量
role := "scheduler"
```

### 3. 系统监控

```go
// 推荐：定期收集统计信息
func collectSystemStats() *ytsys.ClientStatistics {
    return &ytsys.ClientStatistics{
        Hostname:    getHostname(),
        Pid:         os.Getpid(),
        MemoryUsage: getCurrentMemoryUsage(),
        // ... 其他统计信息
    }
}
```

## 注意事项

1. **地址格式**：确保主机端口地址格式正确
2. **端口范围**：端口号必须在有效范围内 (1-65535)
3. **角色一致性**：使用定义的角色常量而不是字符串
4. **统计信息**：定期更新系统统计信息
5. **数据完整性**：监控数据完整性验证结果

## 相关依赖

- `go.ytsaurus.tech/yt/go/ypath`: 路径处理
- `go.ytsaurus.tech/yt/go/yson`: YSON 序列化

## 更多信息

详细的系统架构和组件说明请参考 [YTsaurus 系统文档](https://ytsaurus.tech/docs/en/overview/architecture)。