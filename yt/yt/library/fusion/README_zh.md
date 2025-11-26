# Fusion (服务融合框架)

Fusion 是 YTsaurus 中的轻量级服务定位和依赖注入框架，提供了简洁高效的服务注册、定位和管理功能。

## 概述

Fusion 框架提供以下核心功能：
- 服务注册和发现
- 依赖注入
- 服务生命周期管理
- 类型安全的服务定位
- 灵活的服务目录管理

## 核心组件

### 1. IServiceLocator (服务定位器)
服务定位和查找的核心接口：

```cpp
struct IServiceLocator : public virtual TRefCounted {
    // 查找未类型化服务
    virtual void* FindUntypedService(TServiceId id) = 0;

    // 查找类型化服务（模板方法）
    template <class TServicePtr>
    TServicePtr FindService();

    // 获取服务或抛出异常
    template <class TServicePtr>
    TServicePtr GetServiceOrThrow();
};
```

### 2. IServiceRegistry (服务注册器)
服务的注册和管理接口：

```cpp
struct IServiceRegistry : public virtual TRefCounted {
    // 注册服务实例
    template <class TServicePtr>
    void RegisterService(TServicePtr service);

    // 注册工厂函数
    template <class TServicePtr, class TFactory>
    void RegisterServiceFactory(TFactory factory);
};
```

### 3. IServiceDirectory (服务目录)
提供服务目录管理功能：

```cpp
struct IServiceDirectory : public IServiceLocator, public IServiceRegistry {
    // 继承了定位器和注册器的功能
    // 提供完整的服务管理能力
};
```

### 4. TServiceId (服务标识符)
服务的唯一标识：

```cpp
class TServiceId {
public:
    explicit TServiceId(TTypeId typeId);

    // 获取类型信息
    TTypeId GetTypeId() const;

    // 比较操作符
    bool operator==(const TServiceId& other) const;
    bool operator<(const TServiceId& other) const;
};
```

## 使用方法

### 基本使用
```cpp
// 创建服务目录
auto serviceDirectory = CreateServiceDirectory();

// 注册服务
auto logger = CreateLogger();
serviceDirectory->RegisterService<ILogger>(logger);

auto configManager = CreateConfigManager();
serviceDirectory->RegisterService<IConfigManager>(configManager);

// 查找服务
auto foundLogger = serviceDirectory->FindService<ILogger>();
if (foundLogger) {
    foundLogger->Info("Service found");
}

// 获取服务（必须存在）
auto config = serviceDirectory->GetServiceOrThrow<IConfigManager>();
```

### 使用工厂函数
```cpp
// 注册工厂函数
serviceDirectory->RegisterServiceFactory<IDatabaseService>([] () {
    return CreateDatabaseService();
});

// 延迟创建
auto db = serviceDirectory->GetServiceOrThrow<IDatabaseService>();
```

### 服务特性 (Traits)
框架支持多种服务指针类型：

```cpp
// 原始指针
MyService* rawService = GetService();

// 智能指针
TIntrusivePtr<MyService> smartService = GetService();

// 自动推导服务ID
template <class TServicePtr>
struct TServiceIdTraits {
    using TUnderlying = TService;
    static TServiceId Id;
    static void* ToUntyped(TServicePtr service);
};
```

## 设计特点

### 1. 轻量级
- 最小化的代码开销
- 零运行时反射
- 编译时类型检查

### 2. 类型安全
- 基于模板的类型系统
- 编译时服务ID生成
- 强类型的接口

### 3. 高性能
- O(1) 服务查找
- 最小内存占用
- 无锁设计（单线程场景）

### 4. 灵活性
- 支持多种服务指针类型
- 可扩展的服务注册策略
- 支持服务工厂

## 高级用法

### 1. 服务分层
```cpp
// 创建分层服务目录
auto parentDir = CreateServiceDirectory();
auto childDir = CreateServiceDirectory(parentDir);

// 子目录可以访问父目录的服务
childDir->RegisterService<ILocalService>(localService);
auto parentService = childDir->FindService<IParentService>(); // 从父目录查找
```

### 2. 条件注册
```cpp
// 根据条件注册不同实现
if (UseMock) {
    serviceDirectory->RegisterService<IDataSource>(CreateMockDataSource());
} else {
    serviceDirectory->RegisterService<IDataSource>(CreateRealDataSource());
}
```

### 3. 生命周期管理
```cpp
// 服务生命周期由引用计数管理
class MyService : public TRefCounted {
public:
    ~MyService() {
        // 自动清理资源
    }
};

auto service = New<MyService>();
serviceDirectory->RegisterService<IMyService>(service);
// serviceDirectory 析构时，服务会自动释放
```

## 最佳实践

### 1. 服务设计
- 保持服务接口简洁
- 使用依赖注入而非硬编码依赖
- 实现清晰的服务边界

### 2. 注册时机
```cpp
// 在应用启动时集中注册服务
void RegisterServices(IServiceDirectoryPtr dir) {
    dir->RegisterService<ILogger>(CreateFileLogger());
    dir->RegisterService<IConfigManager>(CreateConfigManager());
    dir->RegisterService<ITransactionManager>(CreateTransactionManager());
}
```

### 3. 错误处理
```cpp
// 优雅处理服务不存在的情况
auto service = serviceDirectory->FindService<IOptionalService>();
if (!service) {
    // 使用默认实现或降级策略
    service = CreateDefaultService();
}
```

## 与其他框架比较

### vs Service Locator 模式
- **Fusion**: 类型安全，编译时检查
- **传统 Service Locator**: 运行时类型转换，易出错

### vs Dependency Injection 容器
- **Fusion**: 轻量级，最小开销
- **重型 DI 容器**: 功能丰富，但开销大

## 性能指标

- **查找时间**: O(1) 哈希查找
- **内存开销**: 每个服务约 16 字节
- **编译时间**: 模板实例化开销
- **运行时开销**: 近乎零，仅在需要时创建服务

## 扩展性

### 自定义服务定位策略
```cpp
class CachingServiceLocator : public IServiceLocator {
public:
    void* FindUntypedService(TServiceId id) override {
        auto it = cache_.find(id);
        if (it != cache_.end()) {
            return it->second;
        }
        auto* service = underlying_->FindUntypedService(id);
        if (service) {
            cache_[id] = service;
        }
        return service;
    }

private:
    THashMap<TServiceId, void*> cache_;
    IServiceLocatorPtr underlying_;
};
```

## 依赖项

- YTsaurus 核心库 (`yt/yt/core/`)
- 类型系统 (`library/cpp/yt/misc/`)
- 内存管理库 (`library/cpp/yt/memory/`)

## 注意事项

1. **循环依赖**: 避免服务间的循环依赖
2. **生命周期**: 注意服务的生命周期管理
3. **线程安全**: 当前实现主要用于单线程场景
4. **类型一致性**: 确保注册和查找时使用一致的类型
5. **性能**: 避免在热路径频繁查找服务

## 使用场景

- **应用初始化**: 配置和管理应用组件
- **插件系统**: 动态加载和管理插件
- **测试环境**: 注入 Mock 服务进行单元测试
- **模块化架构**: 解耦不同模块间的依赖关系