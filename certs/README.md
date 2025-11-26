# 证书文件目录 (Certificates)

## 概述

此目录包含 YTsaurus 项目所需的证书和公钥基础设施相关文件。

## 文件说明

### 证书文件
- **cacert.pem** - 根证书颁发机构（CA）证书文件，包含受信任的证书颁发机构列表，用于SSL/TLS连接验证

### 构建配置文件
- **CMakeLists.txt** - 通用CMake构建配置文件，定义证书的安装规则
- **CMakeLists.darwin-arm64.txt** - macOS ARM64架构专用构建配置
- **CMakeLists.darwin-x86_64.txt** - macOS x86_64架构专用构建配置
- **CMakeLists.linux-aarch64.txt** - Linux ARM64架构专用构建配置
- **CMakeLists.linux-x86_64.txt** - Linux x86_64架构专用构建配置

### 构建脚本
- **ya.make** - YaMake构建系统配置文件，用于传统的Yandex构建流程

## 使用说明

### 构建时使用
这些证书文件在构建YTsaurus项目时会被自动引用：
- cacert.pem用于客户端和服务器的SSL连接验证
- 平台特定的CMakeLists文件确保在不同操作系统上正确安装证书

### 运行时使用
运行时，YTsaurus组件会使用这些证书来：
- 验证其他服务的SSL证书
- 建立加密通信通道
- 确保服务间通信的安全性

## 安全注意事项

1. **证书更新** - cacert.pem应定期更新以包含最新的CA证书
2. **自定义证书** - 生产环境可能需要替换为自定义的证书文件
3. **权限控制** - 确保证书文件具有适当的文件权限

## 维护说明

- 证书文件来源于受信任的证书颁发机构
- 更新证书时，需要同时更新所有平台特定的配置文件
- 构建系统会自动处理不同架构的证书部署