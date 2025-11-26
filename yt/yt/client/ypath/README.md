# YTsaurus YPath Client 模块

## 概述

YPath Client 模块是 YTsaurus 路径操作系统的客户端接口，提供 Ytsaurus 路径解析、操作和导航功能。

## 核心功能

### 1. 路径解析
- **路径解析**: YPath 表达式解析
- **路径验证**: 路径语法验证
- **路径规范化**: 路径标准化

### 2. 路径操作
- **节点导航**: 树形结构导航
- **属性访问**: 节点属性操作
- **路径构建**: 动态路径构建

## 使用方法

```cpp
#include <yt/yt/client/ypath/public.h>

// 创建 YPath 解析器
auto ypath = TYPath("//home/user/table");
auto service = ResolveYPath(client, ypath);

// 获取属性
auto attributes = service->Get("attribute_name");

// 设置属性
service->Set("new_attribute", "value");
```

## 依赖项

### 内部依赖
- `yt/yt/core/misc/public.h`
- `yt/yt/core/ytree/public.h`

## 相关模块

- **Cypress Client**: Cypress 元数据操作
- **Object Client**: 对象路径操作

## 贡献指南

确保路径解析的正确性和性能。
