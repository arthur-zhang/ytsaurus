# Go 第三方库集合

本目录包含 YTsaurus 项目依赖的 Go 语言第三方库。这些库通过 Go modules 管理，提供了 Go 生态系统的集成能力。

## 目录结构

### 主要组件

- **go.mod** - Go 模块定义文件
- **go.sum** - 依赖校验和文件
- **vendor/** - vendor 目录（如果使用）

### 可能包含的库

#### 基础库
- **golang.org/x/** - Go 官方扩展包
  - net/ - 网络扩展
  - sys/ - 系统调用
  - text/ - 文本处理

#### 网络和 RPC
- **google.golang.org/grpc** - gRPC Go 版本
- **google.golang.org/protobuf** - Protocol Buffers Go 版本
- **github.com/gorilla/** - Web 工具包
- **github.com/gin-gonic/gin** - Web 框架

#### 数据处理
- **github.com/go-redis/redis** - Redis 客户端
- **database/sql** - 数据库接口
- **github.com/jmoiron/sqlx** - SQL 扩展

#### 测试工具
- **github.com/stretchr/testify** - 断言库
- **github.com/golang/mock** - Mock 生成工具

#### 日志和监控
- **github.com/sirupsen/logrus** - 结构化日志
- **go.opentelemetry.io/otel** - OpenTelemetry
- **github.com/prometheus/client_golang** - Prometheus 客户端

## 使用方法

### 初始化模块
```bash
# 初始化 Go 模块
go mod init github.com/ytsaurus/ytsaurus/contrib/go

# 下载依赖
go mod download

# 整理依赖
go mod tidy
```

### 导入和使用
```go
package main

import (
    "context"
    "log"
    "google.golang.org/grpc"
    "github.com/sirupsen/logrus"
)

func main() {
    // 使用日志库
    log := logrus.New()
    log.Info("Starting application")

    // 使用 gRPC
    conn, err := grpc.Dial("localhost:8080", grpc.WithInsecure())
    if err != nil {
        log.Fatal(err)
    }
    defer conn.Close()
}
```

## 构建配置

### Makefile 示例
```makefile
.PHONY: build test clean

# 构建
build:
	go build -o app ./cmd/app

# 测试
test:
	go test -v ./...

# 生成 Mock
mock:
	go generate ./...

# 整理代码
fmt:
	go fmt ./...

# 检查
vet:
	go vet ./...
```

### Docker 集成
```dockerfile
FROM golang:1.19-alpine AS builder
WORKDIR /app
COPY go.mod go.sum ./
RUN go mod download
COPY . .
RUN CGO_ENABLED=0 go build -o app ./cmd/app

FROM alpine:latest
RUN apk --no-cache add ca-certificates
WORKDIR /root/
COPY --from=builder /app/app .
CMD ["./app"]
```

## 版本管理

### Go 版本支持
- Go 1.19+（推荐 1.20+）
- 使用 Go modules 管理依赖

### 依赖管理
```bash
# 查看依赖
go list -m all

# 更新依赖
go get -u ./...

# 查找可用更新
go list -u -m all
```

## 性能优化

### pprof 分析
```go
import (
    "net/http"
    _ "net/http/pprof"
)

func main() {
    // 启动 pprof 服务
    go func() {
        log.Println(http.ListenAndServe("localhost:6060", nil))
    }()

    // 应用程序逻辑
}
```

### 基准测试
```go
func BenchmarkMyFunction(b *testing.B) {
    for i := 0; i < b.N; i++ {
        MyFunction()
    }
}
```

## 测试

### 单元测试
```go
package mypackage_test

import (
    "testing"
    "github.com/stretchr/testify/assert"
)

func TestMyFunction(t *testing.T) {
    result := MyFunction(1, 2)
    assert.Equal(t, 3, result)
}
```

### 集成测试
```bash
# 运行所有测试
go test -v ./...

# 生成覆盖率报告
go test -coverprofile=coverage.out ./...
go tool cover -html=coverage.out -o coverage.html
```

## 最佳实践

1. **错误处理**
   ```go
   value, err := someFunction()
   if err != nil {
       log.Errorf("Error: %v", err)
       return
   }
   ```

2. **并发编程**
   ```go
   // 使用 channel
   ch := make(chan Result, 100)
   go func() {
       ch <- process()
   }()

   result := <-ch
   ```

3. **资源管理**
   ```go
   // 使用 defer
   file, err := os.Open(filename)
   if err != nil {
       return err
   }
   defer file.Close()
   ```

## CI/CD 集成

### GitHub Actions
```yaml
name: Go CI
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v2
    - name: Set up Go
      uses: actions/setup-go@v2
      with:
        go-version: 1.20
    - name: Run tests
      run: |
        go test -v ./...
        go test -race -coverprofile=coverage.out ./...
```

## 资源链接
- [Go 官方网站](https://golang.org/)
- [Go modules 文档](https://golang.org/cmd/go/#hdr-Module_support)
- [gRPC Go 文档](https://grpc.io/docs/languages/go/)