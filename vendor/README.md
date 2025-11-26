# Vendor 目录 (第三方依赖管理)

## 概述

此目录包含 YTsaurus Go 项目的第三方依赖库（vendor dependencies）。使用 vendor 目录是为了确保构建的可重现性和依赖版本的一致性，避免依赖外部仓库的变更影响构建。

## 管理策略

### Vendor 管理
- **Go Modules 集成** - 与 Go modules 系统协同工作
- **版本锁定** - 锁定特定版本的依赖库
- **离线构建** - 支持完全离线的构建过程
- **安全审计** - 包含完整的依赖树用于安全检查

## 主要依赖库

### 核心 Go 库
- **golang.org/** - Go 官方扩展库
  - `x/net` - 网络协议扩展
  - `x/sys` - 系统调用接口
  - `x/text` - 文本处理扩展
  - `x/tools` - 开发工具集

### 云服务集成
- **cloud.google.com/** - Google Cloud Platform 客户端库
- **google.golang.org/** - Google Go 语言库
  - `grpc` - gRPC 通信框架
  - `protobuf` - Protocol Buffers 支持
  - `api` - Google API 客户端

### 监控和追踪
- **go.opentelemetry.io/** - OpenTelemetry 可观测性框架
  - 追踪和指标收集
  - 分布式追踪支持
  - 性能监控

### 工具库
- **go.uber.org/** - Uber Go 语言工具库
  - `zap` - 高性能日志库
  - `dig` - 依赖注入框架
  - `atomic` - 原子操作工具

### 社区库
- **github.com/** - GitHub 上的开源库
  - 包含 60+ 个项目
  - 涵盖各种功能需求

## 目录结构详解

### API 和协议
- **google.golang.org/grpc** - gRPC 框架
- **google.golang.org/protobuf** - Protocol Buffers
- **github.com/gogo/protobuf** - Protocol Buffers 扩展

### 日志和监控
- **go.uber.org/zap** - 结构化日志
- **go.opentelemetry.io** - 可观测性
- **github.com/prometheus** - Prometheus 指标

### 数据处理
- **github.com/olekukonko/tablewriter** - 表格格式化
- **github.com/spf13/cobra** - CLI 框架
- **github.com/spf13/viper** - 配置管理

### 测试工具
- **github.com/stretchr/testify** - 测试断言库
- **github.com/golang/mock** - Mock 生成工具

## 使用方法

### 构建时使用
Go 构建系统会自动使用 vendor 目录：
```bash
go build -mod=vendor ./...
```

### 开发时管理
```bash
# 更新依赖
go mod tidy
go mod vendor

# 检查依赖
go mod verify
```

## 版本管理

### 依赖更新流程
1. 修改 go.mod 文件
2. 运行 `go mod tidy`
3. 执行 `go mod vendor`
4. 提交变更到版本控制

### 版本锁定
- 每个依赖都有明确版本
- 使用 `go.sum` 文件验证完整性
- 支持语义化版本控制

## 安全考虑

### 依赖扫描
- 定期扫描已知漏洞
- 使用自动化工具检查
- 及时更新有问题的依赖

### 许可证管理
- 检查所有依赖的许可证
- 确保许可证兼容性
- 维护许可证清单

## 最佳实践

### 依赖管理
1. **最小化依赖** - 只包含必要的库
2. **定期更新** - 保持依赖最新
3. **版本测试** - 更新后充分测试
4. **文档记录** - 记录重要依赖用途

### 构建优化
1. **编译优化** - 利用 build tags
2. **静态链接** - 减少运行时依赖
3. **交叉编译** - 支持多平台构建
4. **增量构建** - 只重建变更部分

### 维护策略
1. **自动化** - 使用 CI/CD 自动管理
2. **监控** - 跟踪依赖健康状态
3. **审计** - 定期审计依赖
4. **清理** - 移除未使用的依赖

## 故障排除

### 常见问题
- **版本冲突** - 使用 `go mod why` 分析
- **构建失败** - 检查 vendor 目录完整性
- **运行时错误** - 验证依赖版本兼容性

### 调试技巧
- 使用 `go list -m all` 查看依赖树
- 检查 `go.mod` 和 `go.sum` 文件
- 验证 vendor 目录哈希值

## 相关工具

### Go Modules 命令
- `go mod download` - 下载依赖
- `go mod graph` - 显示依赖图
- `go mod verify` - 验证依赖
- `go mod why` - 解释依赖原因

### 第三方工具
- `govendor` - Vendor 管理工具
- `dep` - 依赖管理工具（已弃用）
- `glide` - 依赖管理工具（已弃用）

## 迁移说明

### 从其他管理器迁移
项目已从以下工具迁移到 Go modules：
- Glide
- Dep
- Gopath 管理方式

### 保持兼容性
- 保留旧的 import 路径
- 使用 vendor alias 解决冲突
- 提供迁移指南