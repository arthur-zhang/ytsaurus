# Go 客户端库

YTsaurus 的 Go 客户端库，提供完整的 Go 语言接口，用于与 YTsaurus 分布式存储和计算平台进行交互。

## 目录结构

### 核心模块

- **yt/** - 主客户端库
  - 核心客户端实现
  - 表操作、文件操作、MapReduce 接口
  - 事务管理和锁机制

- **yson/** - YSON 序列化
  - YSON 格式的 Go 实现
  - 支持编码和解码操作
  - 与 Python/C++ 客户端兼容

- **ypath/** - 路径处理
  - YPath 路径解析和操作
  - 支持复杂路径表达式
  - 路径规范化和验证

- **proto/** - Protocol Buffers 定义
  - gRPC 服务定义
  - 消息格式定义
  - 跨语言兼容性保证

### 工具库

- **guid/** - GUID 生成器
  - 全局唯一标识符生成
  - 与 YTsaurus GUID 格式兼容

- **crc64/** - CRC64 校验
  - 数据完整性校验
  - 高性能校验和计算

- **compression/** - 压缩算法
  - 多种压缩算法支持
  - 与服务端压缩兼容

- **ratelimit/** - 限流器
  - 请求频率控制
  - 防止过载保护

- **ytlock/** - 分布式锁
  - 分布式互斥锁实现
  - 支持超时和重试

- **ytlog/** - 日志库
  - 结构化日志记录
  - 集成 YTsaurus 日志系统

### 特殊组件

- **mapreduce/** - MapReduce 框架
  - Go 语言 MapReduce 实现
  - 作业提交和管理
  - 数据流处理

- **bus/** - 消息总线
  - 异步消息传递
  - 事件驱动架构支持

- **blobtable/** - Blob 表接口
  - 大对象存储接口
  - 二进制数据处理

- **skiff/** - Skiff 格式支持
  - 高效的列式存储格式
  - 数据交换格式

### 支持工具

- **examples/** - 示例代码
  - 各种使用场景的示例
  - 最佳实践演示

- **genproto/** - 代码生成工具
  - Protocol Buffers 代码生成
  - 自动化工具链

- **dockertest/** - Docker 测试
  - 容器化测试环境
  - 集成测试支持

- **migrate/** - 数据迁移
  - 版本迁移工具
  - 兼容性处理

- **deps/** - 依赖管理
  - 第三方依赖
  - 版本锁定文件

- **yttest/** - 测试工具
  - 测试框架和工具
  - 模拟服务端

- **ytwalk/** - 文件系统遍历
  - 递归文件系统操作
  - 批量处理工具

### 配置文件

- **go.mod** - Go 模块定义
  - 模块依赖管理
  - 版本控制

- **go.sum** - 依赖校验和
  - 确保依赖完整性

- **ya.make** - 构建配置
  - 集成 YaTool 构建系统

## 功能特性

### 数据操作
- 表的创建、读取、写入、删除
- 支持批量操作和事务
- 动态表和静态表支持
- 数据压缩和编码

### 分布式计算
- MapReduce 作业提交
- 运行操作支持
- 任务监控和管理

### 文件系统
- 文件上传下载
- 目录操作
- 符号链接支持

### 高级特性
- 分布式事务
- 多版本并发控制 (MVCC)
- 原子操作保证
- 故障恢复机制

## 使用方法

### 安装依赖
```bash
go mod download
go mod tidy
```

### 基本使用示例
```go
package main

import (
    "context"
    "fmt"
    "go.ytsaurus.tech/yt/go/yt"
    "go.ytsaurus.tech/yt/go/ypath"
)

func main() {
    // 创建客户端
    yc, err := yt.New(context.Background(), yt.Config{
        Proxy: "localhost:8000",
        Token: "your-token",
    })
    if err != nil {
        panic(err)
    }

    // 读取表
    var rows []MyStruct
    err = yc.ReadTable(context.Background(), ypath.Path("//tmp/my_table"), &rows)
    if err != nil {
        panic(err)
    }

    fmt.Printf("Read %d rows\n", len(rows))
}
```

### MapReduce 示例
```go
package main

import (
    "context"
    "go.ytsaurus.tech/yt/go/mapreduce"
    "go.ytsaurus.tech/yt/go/yt"
)

func main() {
    yc := getClient() // 获取客户端

    // 提交 MapReduce 作业
    op, err := mapreduce.Start(yc, mapreduce.Spec{
        InputTable:  []ypath.YPath{"//tmp/input"},
        OutputTable: []ypath.YPath{"//tmp/output"},
        Mapper: &MyMapper{},
        Reducer: &MyReducer{},
    })
    if err != nil {
        panic(err)
    }

    // 等待完成
    err = op.Wait()
    if err != nil {
        panic(err)
    }
}
```

## 性能优化

### 连接池
- 使用连接池减少连接开销
- 合理设置池大小
- 支持连接复用

### 批量操作
- 批量读取和写入
- 减少网络往返
- 提高吞吐量

### 并发控制
- 使用 Go 协程并发处理
- 合理设置并发度
- 避免过度并发

## 依赖项

- Go 1.18+
- Protocol Buffers v3
- gRPC
- YTsaurus 集群 (运行时)

## 最佳实践

1. **错误处理**
   - 始终检查错误返回
   - 使用上下文管理超时
   - 实现重试机制

2. **资源管理**
   - 及时关闭客户端连接
   - 使用 defer 确保资源释放
   - 避免资源泄露

3. **性能优化**
   - 使用连接池
   - 批量操作数据
   - 合理设置缓冲区大小

4. **测试**
   - 使用 yttest 包进行单元测试
   - 集成测试使用真实集群或模拟环境
   - 性能测试验证优化效果