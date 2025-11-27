# Orchid Server 组件

## 概述

Orchid Server 是 YTsaurus 系统中的内部监控和管理服务。它提供了通过 HTTP 接口访问系统内部状态和指标的能力，支持实时监控、调试、配置管理等功能。Orchid 是 YTsaurus 运维和监控系统的重要组成部分。

## 核心功能

- **内部监控**: 暴露内部状态和指标
- **HTTP 接口**: 提供基于 HTTP 的访问接口
- **实时数据**: 支持实时数据查询和订阅
- **配置管理**: 在线修改系统配置
- **调试支持**: 提供调试和诊断信息

## 关键组件

### Orchid Service (orchid_service.h/cpp)
- 核心服务实现
- 处理 HTTP 请求
- 管理数据访问权限

## 使用方法

```bash
# 访问 Orchid 服务
curl http://master:10000/orchid/

# 查看系统状态
curl http://master:10000/orchid/sys

# 查看特定组件
curl http://master:10000/orchid/cypress_manager
```

## 配置参数

```yaml
orchid_server:
  enable: true
  port: 10000
  bind_address: "0.0.0.0"
  enable_cors: true
```

## 相关文档
- [监控指南](../../../docs/monitoring.md)
- [Orchid 使用手册](../../../docs/orchid-guide.md)