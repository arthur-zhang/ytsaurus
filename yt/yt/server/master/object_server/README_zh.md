# Object Server 组件

## 概述

Object Server 是 YTsaurus 系统中最基础的对象管理组件。它为整个系统提供了统一的对象标识、生命周期管理、引用计数、版本控制等基础功能。所有 YTsaurus 中的实体（节点、Chunk、账户等）都是 Object Server 管理的对象。

## 核心功能

- **对象标识**: 为所有对象分配唯一 ID
- **生命周期管理**: 管理对象的创建和删除
- **引用计数**: 跟踪对象的引用关系
- **持久化**: 对象状态的持久化和恢复
- **类型系统**: 统一的对象类型管理

## 关键组件

### Object Manager (object_manager.h/cpp)
- 核心对象管理器
- 管理所有系统对象
- 处理对象的创建、删除、修改

### Object Proxy (object_proxy.h/cpp)
- 对象代理基类
- 提供 RPC 接口
- 处理远程访问

## 使用方法

```cpp
// 创建对象
auto object = objectManager->CreateObject(
    EObjectType::Node,
    attributes
);

// 获取对象
auto object = objectManager->FindObject(objectId);

// 删除对象
objectManager->DestroyObject(object);
```

## 相关文档
- [对象系统设计](../../../docs/object-system.md)
- [Master 架构](../../../docs/master-architecture.md)