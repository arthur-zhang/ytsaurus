# GenProto

## 概述

GenProto 是 YTsaurus Go 客户端的 Protocol Buffers 代码生成工具，负责将 `.proto` 文件编译成 Go 代码。该模块自动化了从 Protocol Buffers 定义文件生成 Go 类型定义和处理代码的过程，确保 Go 客户端与 YTsaurus 系统之间的协议兼容性。

## 功能特性

- **自动化生成**：使用脚本自动批量处理多个 `.proto` 文件
- **模块化输出**：生成符合 Go 模块规范的代码
- **多源支持**：支持从多个目录收集 `.proto` 文件
- **依赖管理**：通过 `go:generate` 和 build tags 管理工具依赖
- **CI/CD 集成**：支持 GitHub Actions 等持续集成环境

## 文件结构

```
genproto/
├── genproto.sh     # 代码生成脚本
└── deps.go         # Go 依赖声明和 generate 指令
```

## 核心组件

### 1. genproto.sh

主要的代码生成脚本，执行以下任务：

- 查找所有 `.proto` 文件
- 调用 `protoc` 编译器生成 Go 代码
- 设置正确的模块路径
- 处理不同的源目录

### 2. deps.go

Go 工具依赖声明文件：

```go
//go:build tools
// +build tools

package tools

import (
    _ "google.golang.org/protobuf/cmd/protoc-gen-go"
)

//go:generate go install google.golang.org/protobuf/cmd/protoc-gen-go
//go:generate ./genproto.sh
```

## 支持的 Protocol Buffer 路径

脚本处理以下目录中的 `.proto` 文件：

1. **RPC 代理**
   - `yt/yt_proto/yt/client/api/rpc_proxy/`

2. **核心总线**
   - `yt/yt_proto/yt/core/bus/proto/`

3. **RPC 协议**
   - `yt/yt_proto/yt/core/rpc/proto/`

4. **分布式追踪**
   - `yt/yt_proto/yt/core/tracing/proto/`

5. **YSON 协议**
   - `yt/yt_proto/yt/core/yson/proto/`

6. **YTree 属性**
   - `yt/yt_proto/yt/core/ytree/proto/attributes.proto`

7. **错误处理**
   - `yt/yt_proto/yt/core/misc/proto/error.proto`

8. **GUID**
   - `yt/yt_proto/yt/core/misc/proto/guid.proto`

9. **测试服务**
   - `yt/yt/core/rpc/unittests/lib/test_service.proto`

10. **混沌客户端**
    - `yt/yt_proto/yt/client/chaos_client/proto/`

11. **数据统计**
    - `yt/yt_proto/yt/client/chunk_client/proto/data_statistics.proto`

12. **时间戳映射**
    - `yt/yt_proto/yt/client/hive/proto/timestamp_map.proto`

## 使用方法

### 1. 本地生成

在项目根目录执行：

```bash
cd yt/go/genproto
./genproto.sh
```

或使用 `go generate`：

```bash
go generate ./genproto
```

### 2. 环境准备

确保已安装必要的工具：

```bash
# 安装 Protocol Buffers 编译器
# Ubuntu/Debian
sudo apt-get install protobuf-compiler

# macOS
brew install protobuf

# 或从源码编译
# https://github.com/protocolbuffers/protobuf
```

### 3. 依赖安装

```bash
# 安装 Go protobuf 插件
go install google.golang.org/protobuf/cmd/protoc-gen-go@latest

# 确保 GOPATH/bin 在 PATH 中
export PATH=$PATH:$(go env GOPATH)/bin
```

## 生成过程详解

### 脚本执行流程

1. **环境检查**
   ```bash
   set -e          # 遇到错误立即退出
   set -o pipefail # 管道中任何命令失败都视为失败
   set -x          # 显示执行的命令
   ```

2. **Git 工作目录确定**
   ```bash
   # 支持本地开发环境和 GitHub Actions
   if [[ -z "${GITHUB_WORKSPACE}" ]]; then
       GIT_WORK_DIR=$(git rev-parse --show-toplevel)
   else
       GIT_WORK_DIR="${GITHUB_WORKSPACE}"
   fi
   ```

3. **Proto 文件查找和编译**
   ```bash
   # 对每个目录执行
   protoc --go_opt=module=go.ytsaurus.tech \
           --go_out=. \
           -I ./yt \
           $(find ./path/to/proto/files -iname "*.proto")
   ```

### 输出结构

生成的代码将放在以下位置：
```
yt/go/proto/
├── go.ytsaurus.tech/yt/
│   ├── client/api/rpc_proxy/
│   ├── core/bus/
│   ├── core/rpc/
│   ├── core/tracing/
│   └── ...
```

## 最佳实践

### 1. 定期更新

```bash
# 在 Protocol Buffer 文件更新后
git pull origin main
go generate ./genproto
git add yt/go/proto/
git commit -m "Update generated protobuf code"
```

### 2. CI/CD 集成

在 `.github/workflows/build.yml` 中添加：

```yaml
- name: Generate protobuf code
  run: |
    cd yt/go/genproto
    ./genproto.sh
    git diff --exit-code || (echo "Generated code is out of date" && exit 1)
```

### 3. 版本控制

```bash
# 确保 .gitignore 不包含生成的代码
# 生成的代码应该提交到版本控制

# 检查是否有未提交的更改
git status --porcelain | grep "proto/"
```

## 故障排除

### 常见问题

1. **protoc 命令未找到**
   ```bash
   # 检查安装
   which protoc
   protoc --version

   # 重新安装
   sudo apt-get install protobuf-compiler
   ```

2. **protoc-gen-go 插件未找到**
   ```bash
   # 检查安装
   which protoc-gen-go

   # 重新安装
   go install google.golang.org/protobuf/cmd/protoc-gen-go@latest
   ```

3. **模块路径错误**
   ```bash
   # 确保在正确的目录执行
   pwd  # 应该在 ytsaurus/yt/go/genproto

   # 检查 go.mod 文件
   cat ../go.mod | grep module
   ```

4. **权限问题**
   ```bash
   # 确保脚本可执行
   chmod +x genproto.sh

   # 检查文件权限
   ls -la genproto.sh
   ```

### 调试技巧

1. **详细输出**
   ```bash
   bash -x genproto.sh
   ```

2. **单个目录测试**
   ```bash
   # 测试特定目录
   protoc --go_opt=module=go.ytsaurus.tech \
           --go_out=. \
           -I ./yt \
           ./yt/yt_proto/yt/core/rpc/proto/rpc.proto
   ```

3. **清理和重新生成**
   ```bash
   # 删除生成的代码
   rm -rf yt/go/proto/go.ytsaurus.tech

   # 重新生成
   ./genproto.sh
   ```

## 性能优化

### 1. 并行生成

脚本可以修改为并行处理多个目录：

```bash
# 并行执行多个 protoc 命令
for dir in "${directories[@]}"; do
    (
        protoc --go_opt=module=go.ytsaurus.tech \
               --go_out=. \
               -I ./yt \
               $(find "$dir" -iname "*.proto") &
    )
done

wait  # 等待所有后台任务完成
```

### 2. 增量更新

只重新生成修改过的文件：

```bash
# 检查修改的 .proto 文件
git diff --name-only HEAD~1 | grep "\.proto$"

# 只生成修改的文件
protoc --go_opt=module=go.ytsaurus.tech \
       --go_out=. \
       -I ./yt \
       modified_file.proto
```

## 开发指南

### 添加新的 Proto 路径

1. 在 `genproto.sh` 中添加新行：
   ```bash
   (cd $GIT_WORK_DIR && protoc --go_opt=module=go.ytsaurus.tech --go_out=. -I ./yt $(find ./yt/yt_proto/yt/new/module -iname "*.proto"))
   ```

2. 确保 `.proto` 文件正确
3. 运行生成脚本
4. 检查生成的代码
5. 提交更改

### 自定义生成选项

```bash
# 添加更多选项
protoc --go_opt=module=go.ytsaurus.tech \
       --go_opt=paths=source_relative \
       --go_out=. \
       -I ./yt \
       $(find . -iname "*.proto")
```

## 相关资源

- [Protocol Buffers 官方文档](https://developers.google.com/protocol-buffers)
- [Go Protocol Buffers 插件](https://github.com/protocolbuffers/protobuf-go)
- [YTsaurus Protocol 定义](https://github.com/ytsaurus/ytsaurus/tree/main/yt/yt_proto)
- [Go Generate 文档](https://blog.golang.org/generate)