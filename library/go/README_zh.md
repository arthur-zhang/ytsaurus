# Go 语言库

本目录包含 YTsaurus 的 Go 语言支持库，提供通用的 Go 语言工具和组件。

## 目录结构

### 核心组件
- **core/** - 核心库
  - 基础数据结构和算法
  - 通用工具函数
  - 错误处理机制

- **x/** - 扩展库
  - 实验性功能
  - 高级工具集
  - 特定领域组件

### 工具库
- **blockcodecs/** - 块编解码器
  - 各种压缩算法实现
  - 数据编码/解码工具
  - 性能优化的编解码器

- **httputil/** - HTTP 工具
  - HTTP 客户端封装
  - 请求/响应处理工具
  - 中间件支持

- **ptr/** - 指针工具
  - 指针操作辅助函数
  - 安全的指针转换
  - 内存管理工具

- **slices/** - 切片工具
  - 切片操作函数集
  - 高效的切片处理
  - 并发安全操作

- **test/** - 测试工具
  - 测试辅助函数
  - Mock 和断言工具
  - 基准测试支持

## 功能特性

### 高性能编解码
- 支持多种压缩算法（LZ4、Snappy、Zstd）
- 零拷贝优化
- 流式处理支持
- 并发安全设计

### HTTP 工具集
- 简化的 HTTP 客户端
- 自动重试和熔断
- 请求/响应拦截器
- 连接池管理

### 实用工具
- 类型安全的指针操作
- 高效的切片处理
- 内存池管理
- 错误链追踪

## 使用方法

### 安装依赖
```bash
# 获取模块
go get github.com/ytsaurus/ytsaurus/library/go/...

# 更新依赖
go mod tidy
```

### 使用编解码器
```go
package main

import (
    "fmt"
    "github.com/ytsaurus/ytsaurus/library/go/blockcodecs"
)

func main() {
    // 创建编码器
    encoder := blockcodecs.NewLZ4Encoder()

    // 编码数据
    data := []byte("Hello, YTsaurus!")
    encoded, err := encoder.Encode(data)
    if err != nil {
        panic(err)
    }

    // 解码数据
    decoder := blockcodecs.NewLZ4Decoder()
    decoded, err := decoder.Decode(encoded)
    if err != nil {
        panic(err)
    }

    fmt.Printf("Original: %s\n", data)
    fmt.Printf("Decoded: %s\n", decoded)
}
```

### 使用 HTTP 工具
```go
package main

import (
    "context"
    "fmt"
    "github.com/ytsaurus/ytsaurus/library/go/httputil"
)

func main() {
    // 创建 HTTP 客户端
    client := httputil.NewClient(httputil.Config{
        Timeout:       30 * time.Second,
        RetryCount:    3,
        RetryInterval: time.Second,
    })

    // 发送请求
    ctx := context.Background()
    resp, err := client.Get(ctx, "https://api.example.com/data")
    if err != nil {
        panic(err)
    }
    defer resp.Body.Close()

    // 处理响应
    fmt.Printf("Status: %s\n", resp.Status)
}
```

### 使用切片工具
```go
package main

import (
    "fmt"
    "github.com/ytsaurus/ytsaurus/library/go/slices"
)

func main() {
    // 创建切片
    data := []int{1, 2, 3, 4, 5}

    // 过滤元素
    filtered := slices.Filter(data, func(x int) bool {
        return x%2 == 0
    })

    // 转换元素
    transformed := slices.Map(filtered, func(x int) string {
        return fmt.Sprintf("num_%d", x)
    })

    fmt.Printf("Filtered: %v\n", filtered)     // [2 4]
    fmt.Printf("Transformed: %v\n", transformed) // [num_2 num_4]
}
```

## 组件详细说明

### blockcodecs
支持多种编解码器：
- **LZ4**: 极快的压缩算法
- **Snappy**: 适中的压缩比和速度
- **Zstd**: 高压缩比算法
- **Gzip**: 通用压缩算法

特性：
- 流式压缩/解压
- 并发安全
- 内存池优化
- 自适应缓冲区

### httputil
功能特性：
- 自动 JSON 处理
- 请求/响应日志
- 限流和熔断
- 健康检查端点
- 指标收集

### ptr
指针工具函数：
- `Value()` - 解引用指针
- `Ref()` - 创建值的指针
- `Equal()` - 比较指针值
- `IsEmpty()` - 检查空指针

### slices
切片操作函数：
- `Map()` - 映射转换
- `Filter()` - 过滤元素
- `Reduce()` - 归约操作
- `Chunk()` - 分块处理
- `Unique()` - 去重
- `Shuffle()` - 随机打乱

## 性能优化

### 内存管理
- 使用对象池减少分配
- 预分配切片容量
- 避免不必要的拷贝

### 并发处理
- 无锁数据结构
- 协程池管理
- 工作窃取算法

### 基准测试
```bash
# 运行所有基准测试
go test ./... -bench=. -benchmem

# 运行特定组件测试
go test ./blockcodecs -bench=LZ4
```

## 测试

### 单元测试
```bash
# 运行所有测试
go test ./...

# 运行特定包测试
go test ./core

# 生成覆盖率报告
go test -coverprofile=coverage.out ./...
go tool cover -html=coverage.out
```

### 集成测试
```bash
# 运行集成测试
make test-integration

# 运行性能测试
make test-performance
```

## 最佳实践

1. **错误处理**
   ```go
   // 使用辅助函数简化错误处理
   result, err := someOperation()
   if err != nil {
       return fmt.Errorf("operation failed: %w", err)
   }
   ```

2. **资源管理**
   ```go
   // 使用 defer 确保资源释放
   resource, err := acquireResource()
   if err != nil {
       return err
   }
   defer resource.Close()
   ```

3. **并发编程**
   ```go
   // 使用带缓冲的通道避免死锁
   ch := make(chan Data, 100)
   go producer(ch)
   consumer(ch)
   ```

## 版本兼容性

- Go 版本要求：1.18+
- 向后兼容：保持 API 稳定性
- 模块版本：语义化版本控制

## 贡献指南

1. Fork 项目仓库
2. 创建功能分支
3. 添加测试用例
4. 确保通过所有测试
5. 提交 Pull Request

## 许可证

本库遵循 Apache 2.0 许可证。详见 LICENSE 文件。