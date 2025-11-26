# YTsaurus Object Client 模块

## 概述

Object Client 模块是 YTsaurus 对象管理系统的核心客户端接口，提供了分布式对象的生命周期管理功能。该模块支持对象的创建、读取、更新、删除，以及对象元数据管理，是 YTsaurus 存储系统的基础组件。

## 核心功能

### 1. 对象生命周期管理
- **创建对象**: 创建各种类型的分布式对象
- **读取对象**: 高效的对象内容读取
- **更新对象**: 原子性对象更新操作
- **删除对象**: 安全的对象删除

### 2. 元数据管理
- **对象属性**: 丰富的对象元数据属性
- **类型系统**: 支持多种对象类型
- **版本控制**: 对象版本管理
- **访问控制**: 对象权限和安全控制

### 3. 批量操作
- **批量读写**: 高效的批量对象操作
- **原子操作**: 多对象原子性操作
- **事务支持**: 分布式事务中的对象操作

## 主要组件

### 1. 对象助手 (helpers.h/cpp)
提供对象操作的高级辅助函数：
```cpp
class TObjectHelpers {
public:
    static NObjectClient::TObjectId CreateObject(
        NApi::IClientPtr client,
        EObjectType type,
        const NYTree::IMapNodePtr& attributes);

    static TErrorOr<void> DeleteObject(
        NApi::IClientPtr client,
        const NObjectClient::TObjectId& objectId);

    static NYTree::IYPathServicePtr GetObjectService(
        NApi::IClientPtr client,
        const NObjectClient::TObjectId& objectId);
};
```

### 2. 辅助内联函数 (helpers-inl.h)
提供内联优化的高性能辅助函数：
- **快速路径优化**: 热路径的内联优化
- **缓存友好**: CPU 缓存友好的数据结构
- **零拷贝操作**: 最小化内存拷贝的开销

## 使用方法

### 1. 基本对象操作

```cpp
#include <yt/yt/client/object_client/public.h>
#include <yt/yt/client/object_client/helpers.h>

using namespace NYT::NObjectClient;

// 创建对象
auto attributes = NYTree::BuildYsonNodeFluently()
    .BeginMap()
        .Item("name").Value("my-object")
        .Item("description").Value("Example object")
        .Item("tags").BeginList()
            .Item("test")
            .Item("example")
        .EndList()
    .EndMap();

auto objectId = TObjectHelpers::CreateObject(
    client,
    EObjectType::MapNode,
    attributes);

// 删除对象
auto deleteResult = TObjectHelpers::DeleteObject(client, objectId);
if (!deleteResult.IsOK()) {
    YT_LOG_ERROR("Failed to delete object: %v", deleteResult);
}
```

### 2. 高级对象操作

```cpp
// 对象工厂模式
class ObjectFactory {
public:
    template<typename T>
    std::shared_ptr<T> CreateTypedObject(
        NApi::IClientPtr client,
        const NYTree::IMapNodePtr& attributes = nullptr) {

        auto objectId = CreateBaseObject(client, T::ObjectType, attributes);
        return std::make_shared<T>(client, objectId);
    }

    NObjectClient::TObjectId CreateTable(
        NApi::IClientPtr client,
        const NTableClient::TTableSchema& schema) {

        auto attributes = NYTree::BuildYsonNodeFluently()
            .BeginMap()
                .Item("schema").Value(schema)
                .Item("dynamic").Value(false)
            .EndMap();

        return TObjectHelpers::CreateObject(
            client,
            EObjectType::Table,
            attributes);
    }
};

// 对象代理
class ObjectProxy {
private:
    NApi::IClientPtr client_;
    NObjectClient::TObjectId objectId_;

public:
    ObjectProxy(NApi::IClientPtr client, const NObjectClient::TObjectId& objectId)
        : client_(client)
        , objectId_(objectId)
    {}

    TFuture<NYTree::IYPathServicePtr> GetService() {
        return TObjectHelpers::GetObjectService(client_, objectId_);
    }

    TFuture<NYTree::IAttributeDictionaryPtr> GetAttributes() {
        return GetService().Apply(BIND([] (const NYTree::IYPathServicePtr& service) {
            return service->Attributes();
        }));
    }
};
```

### 3. 对象模板

```cpp
// 对象模板系统
class ObjectTemplate {
private:
    NYTree::IMapNodePtr template_;
    std::unordered_map<TString, TTemplateParameter> parameters_;

public:
    ObjectTemplate(const NYTree::IMapNodePtr& templ)
        : template_(templ)
    {}

    NObjectClient::TObjectId Instantiate(
        NApi::IClientPtr client,
        const std::unordered_map<TString, NYson::TYsonString>& values) {

        auto attributes = InstantiateTemplate(values);
        return TObjectHelpers::CreateObject(
            client,
            GetTemplateType(),
            attributes);
    }

private:
    NYTree::IMapNodePtr InstantiateTemplate(
        const std::unordered_map<TString, NYson::TYsonString>& values) {

        // 模板实例化逻辑
        auto instantiated = NYTree::CloneNode(template_);
        for (const auto& [key, value] : values) {
            ReplaceTemplateParameter(instantiated, key, value);
        }
        return instantiated->AsMap();
    }
};
```

## 性能优化

### 1. 对象缓存
```cpp
// 对象缓存管理
class ObjectCache {
private:
    TLRUCache<NObjectClient::TObjectId, CachedObject> cache_;
    TDuration ttl_;

public:
    std::optional<NYTree::IAttributeDictionaryPtr> GetAttributes(
        const NObjectClient::TObjectId& objectId) {

        auto entry = cache_.Find(objectId);
        if (entry && TInstant::Now() - entry->LastUpdated < ttl_) {
            return entry->Attributes;
        }

        return std::nullopt;
    }

    void PutAttributes(
        const NObjectClient::TObjectId& objectId,
        const NYTree::IAttributeDictionaryPtr& attributes) {

        CachedObject entry{attributes, TInstant::Now()};
        cache_.Insert(objectId, entry);
    }
};
```

### 2. 批量操作
```cpp
// 批量对象操作
class BatchObjectOperations {
public:
    TFuture<std::vector<NObjectClient::TObjectId>> CreateBatch(
        const std::vector<ObjectSpec>& specs) {

        std::vector<TFuture<NObjectClient::TObjectId>> futures;
        for (const auto& spec : specs) {
            auto future = TObjectHelpers::CreateObjectAsync(
                spec.Client,
                spec.Type,
                spec.Attributes);
            futures.push_back(future);
        }

        return AllSucceeded(std::move(futures));
    }

    TFuture<void> DeleteBatch(
        const std::vector<NObjectClient::TObjectId>& objectIds) {

        // 并发删除
        std::vector<TFuture<void>> futures;
        for (const auto& objectId : objectIds) {
            auto future = TObjectHelpers::DeleteObjectAsync(objectId);
            futures.push_back(future);
        }

        return AllSucceeded(std::move(futures));
    }
};
```

## 最佳实践

### 1. 对象命名规范
- **层次结构**: 使用路径式的对象命名
- **类型前缀**: 包含对象类型的前缀
- **环境标识**: 区分不同环境的对象

### 2. 属性管理
- **必要的属性**: 只设置必要的对象属性
- **类型一致性**: 确保属性值的类型一致性
- **版本管理**: 在属性中包含版本信息

### 3. 生命周期管理
- **及时清理**: 及时删除不再需要的对象
- **引用计数**: 实现对象的引用计数管理
- **垃圾回收**: 定期执行垃圾回收操作

## 依赖项

### 内部依赖
- `yt/yt/core/misc/public.h` - 核心公共定义

### 外部依赖
- 网络通信库
- 序列化库
- 线程库

## 相关模块

- **Cypress Client**: 元数据树管理
- **Table Client**: 表数据操作
- **Chunk Client**: 分片存储

## 参考文档

- [YTsaurus 对象系统](../../../docs/object-system.md)
- [Cypress 架构设计](../../../docs/cypress.md)
- [权限管理指南](../../../docs/permissions.md)

## 贡献指南

在修改此模块时：
1. 确保对象操作的原子性
2. 优化大规模对象操作的性能
3. 添加充分的错误处理
4. 保持向后兼容性
5. 考虑安全性影响