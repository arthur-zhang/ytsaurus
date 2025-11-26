# Dockertest

## 概述

Dockertest 模块为 YTsaurus Go 客户端提供集成测试支持，使用 Testcontainers 框架在 Docker 容器中运行完整的 YTsaurus 集群。该模块使得开发者能够在隔离的环境中快速搭建测试用的 YTsaurus 集群，进行端到端测试和集成测试。

## 功能特性

- **自动化集群部署**：自动启动和配置 YTsaurus 集群容器
- **灵活配置**：支持多种集群配置选项
- **端口管理**：自动分配可用端口
- **环境变量设置**：自动配置测试环境变量
- **资源清理**：测试完成后自动清理容器资源
- **卷挂载**：支持挂载本地卷到容器

## 核心组件

### YTsaurusContainer 结构体

```go
type YTsaurusContainer struct {
    testcontainers.Container  // 嵌入的 Testcontainers 容器

    Proxy   string            // 代理地址
    Cluster string            // 集群 ID
}
```

## 使用方法

### 基本用法

```go
package main

import (
    "context"
    "testing"
    "time"

    "go.ytsaurus.tech/yt/go/dockertest"
    "go.ytsaurus.tech/yt/go/yt"
)

func TestYTsaurusIntegration(t *testing.T) {
    ctx := context.Background()

    // 创建 YTsaurus 容器
    container, err := dockertest.InitYTsaurusContainer(ctx)
    if err != nil {
        t.Fatalf("初始化容器失败: %v", err)
    }
    defer container.Terminate(ctx)

    // 等待集群就绪
    time.Sleep(5 * time.Second)

    // 创建 YTsaurus 客户端
    yc, err := yt.New(&yt.Config{
        Proxy: container.Proxy,
        Token: "test-token",
    })
    if err != nil {
        t.Fatalf("创建客户端失败: %v", err)
    }
    defer yc.Close()

    // 执行测试...
}
```

### 高级配置

```go
func TestAdvancedConfiguration(t *testing.T) {
    ctx := context.Background()

    // 创建带高级配置的容器
    container, err := dockertest.InitYTsaurusContainer(ctx,
        // 启用动态表
        dockertest.WithDynamicTables(),
        // 添加从 Master 节点
        dockertest.WithSecondaryMasterCells(2),
        // 自定义集群名称
        dockertest.WithClusterName("test-cluster"),
        // 配置 RPC 代理
        dockertest.WithRPCProxies(2),
        // 配置 HTTP 代理
        dockertest.WithHTTPProxiesCount(2),
        // 配置节点数量
        dockertest.WithNodesCount(5),
        // 配置发现服务器
        dockertest.WithDiscoveryServers(3),
    )
    if err != nil {
        t.Fatalf("初始化容器失败: %v", err)
    }
    defer container.Terminate(ctx)

    // 使用容器进行测试...
}
```

### 卷挂载

```go
func TestVolumeMount(t *testing.T) {
    ctx := context.Background()

    // 设置卷挂载环境变量
    os.Setenv("YT_VOLUME", "/path/to/local/volume")
    defer os.Unsetenv("YT_VOLUME")

    // 初始化容器时会自动挂载卷
    container, err := dockertest.InitYTsaurusContainer(ctx)
    if err != nil {
        t.Fatalf("初始化容器失败: %v", err)
    }
    defer container.Terminate(ctx)

    // 使用容器进行测试...
}
```

### 自定义容器请求

```go
func TestCustomContainer(t *testing.T) {
    ctx := context.Background()

    // 直接使用 RunContainer 进行更细粒度的控制
    container, err := dockertest.RunContainer(ctx,
        dockertest.WithClusterName("custom-cluster"),
        dockertest.WithNodesCount(3),
    )
    if err != nil {
        t.Fatalf("运行容器失败: %v", err)
    }
    defer container.Terminate(ctx)

    // 手动设置环境变量
    os.Setenv("YT_PROXY", container.Proxy)
    os.Setenv("YT_ID", container.Cluster)
    defer func() {
        os.Unsetenv("YT_PROXY")
        os.Unsetenv("YT_ID")
    }()

    // 使用容器进行测试...
}
```

## 配置选项

### 集群配置

| 选项 | 类型 | 描述 | 默认值 |
|------|------|------|--------|
| WithDynamicTables() | - | 启用动态表支持 | 禁用 |
| WithSecondaryMasterCells(count) | int | 设置从 Master 节点数量 | 0 |
| WithClusterName(name) | string | 设置集群名称 | 随机 GUID |
| WithNodesCount(count) | int | 设置计算节点数量 | 1 |
| WithRPCProxies(count) | int | 设置 RPC 代理数量 | 0 |
| WithHTTPProxiesCount(count) | int | 设置 HTTP 代理数量 | 1 |
| WithDiscoveryServers(count) | int | 设置发现服务器数量 | 1 |

### 存储配置

| 选项 | 类型 | 描述 |
|------|------|------|
| WithVolumeMount(volume) | string | 挂载本地卷到容器中的 /home/yt |

## 环境变量

测试容器会自动设置以下环境变量：

- `YT_PROXY`：代理服务器地址
- `YT_ID`：集群标识符
- `YT_VOLUME`：（可选）挂载的卷路径

## 性能考虑

### 启动时间

- 默认启动超时：10 分钟
- 集群完全就绪可能需要额外时间
- 动态表初始化会增加启动时间

### 资源需求

- **最小内存**：2GB RAM
- **推荐内存**：4GB RAM 或更多
- **磁盘空间**：至少 1GB 可用空间
- **CPU**：至少 2 个核心

## 最佳实践

### 1. 测试组织

```go
func TestSuite(t *testing.T) {
    // 设置全局测试容器
    ctx := context.Background()
    container, err := dockertest.InitYTsaurusContainer(ctx)
    if err != nil {
        t.Fatalf("初始化容器失败: %v", err)
    }
    defer container.Terminate(ctx)

    // 运行子测试
    t.Run("TestCreate", func(t *testing.T) {
        testCreate(t, container)
    })

    t.Run("TestRead", func(t *testing.T) {
        testRead(t, container)
    })
}
```

### 2. 错误处理

```go
func initContainer(ctx context.Context) (*dockertest.YTsaurusContainer, error) {
    container, err := dockertest.InitYTsaurusContainer(ctx)
    if err != nil {
        return nil, fmt.Errorf("初始化 YTsaurus 容器失败: %w", err)
    }

    // 等待集群完全就绪
    if err := waitForClusterReady(ctx, container); err != nil {
        container.Terminate(ctx)
        return nil, err
    }

    return container, nil
}
```

### 3. 资源清理

```go
func cleanupContainer(container *dockertest.YTsaurusContainer) {
    if container != nil {
        ctx, cancel := context.WithTimeout(context.Background(), 30*time.Second)
        defer cancel()

        if err := container.Terminate(ctx); err != nil {
            log.Printf("清理容器失败: %v", err)
        }
    }
}
```

## 故障排除

### 常见问题

1. **端口冲突**
   - 确保没有其他进程占用所需端口
   - 模块会自动分配可用端口

2. **Docker 未运行**
   - 确保 Docker 守护进程正在运行
   - 检查 Docker 权限

3. **镜像拉取失败**
   - 确保能够访问 `ghcr.io/ytsaurus/local:dev`
   - 检查网络连接

4. **内存不足**
   - 增加可用内存
   - 减少集群组件数量

### 调试技巧

```go
// 启用详细日志
import "github.com/testcontainers/testcontainers-go/log"

log.Logger = log.TestLogger(log.T)

// 获取容器日志
logs, err := container.Logs(ctx)
if err != nil {
    return err
}
defer logs.Close()

// 读取日志内容
scanner := bufio.NewScanner(logs)
for scanner.Scan() {
    fmt.Println(scanner.Text())
}
```

## 依赖项

- `github.com/testcontainers/testcontainers-go`：Testcontainers Go 库
- `go.ytsaurus.tech/yt/go/guid`：GUID 生成工具
- Docker：容器运行环境

## 注意事项

1. **资源占用**：容器会占用大量系统资源
2. **网络依赖**：需要能够访问 Docker Hub 或镜像仓库
3. **清理**：确保在测试完成后正确清理容器
4. **并发**：避免同时运行过多容器
5. **隔离性**：每个测试应使用独立的容器实例

## 扩展功能

### 自定义镜像

```go
func TestCustomImage(t *testing.T) {
    req := testcontainers.ContainerRequest{
        Image: "custom-ytsaurus:latest",
        // 其他配置...
    }

    container, err := testcontainers.GenericContainer(ctx, testcontainers.GenericContainerRequest{
        ContainerRequest: req,
        Started: true,
    })
    // ...
}
```

### 网络配置

```go
func TestNetworkConfig(t *testing.T) {
    // 创建自定义网络
    network, err := testcontainers.GenericNetwork(ctx, testcontainers.GenericNetworkRequest{
        NetworkRequest: testcontainers.NetworkRequest{
            Name: "test-network",
        },
    })
    if err != nil {
        t.Fatal(err)
    }
    defer network.Remove(ctx)

    // 在自定义网络中创建容器
    container, err := dockertest.InitYTsaurusContainer(ctx,
        testcontainers.WithNetwork(network),
    )
    // ...
}
```