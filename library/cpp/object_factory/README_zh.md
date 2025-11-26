# Object Factory 对象工厂库

## 项目概述

Object Factory 是一个通用的对象工厂模式实现库，提供了线程安全、类型安全的对象创建和管理功能。该库支持注册、创建和管理不同类型的对象实例，是构建可扩展、可配置系统的核心组件。

### 核心功能
- **动态对象创建**：运行时根据标识符创建对象
- **类型安全**：编译时类型检查，避免类型错误
- **线程安全**：支持多线程环境下的并发访问
- **参数化构造**：支持带参数的对象构造
- **注册管理**：动态注册和注销对象类型
- **单例模式**：内置单例工厂支持

## 文件说明

### 主要头文件
- **object_factory.h** - 对象工厂的完整实现

## 使用示例

### 基础对象工厂使用
```cpp
#include <library/cpp/object_factory/object_factory.h>

using namespace NObjectFactory;

// 定义产品基类
class IAnimal {
public:
    virtual ~IAnimal() {}
    virtual void MakeSound() = 0;
    virtual TString GetType() const = 0;
};

// 定义具体产品类
class Dog: public IAnimal {
public:
    void MakeSound() override {
        printf("Woof!\n");
    }

    TString GetType() const override {
        return "Dog";
    }

    FACTORY_OBJECT_NAME(Dog)  // 自动生成类型名
};

class Cat: public IAnimal {
public:
    void MakeSound() override {
        printf("Meow!\n");
    }

    TString GetType() const override {
        return "Cat";
    }

    FACTORY_OBJECT_NAME(Cat)  // 自动生成类型名
};

// 定义对象工厂类型
typedef TObjectFactory<IAnimal, TString> TAnimalFactory;

// 注册产品类型
static TAnimalFactory::TRegistrator<Dog> DogRegistrator("dog");
static TAnimalFactory::TRegistrator<Cat> CatRegistrator("cat");

// 使用工厂创建对象
void CreateAnimals() {
    // 创建狗对象
    THolder<IAnimal> dog = TAnimalFactory::MakeHolder("dog");
    if (dog) {
        dog->MakeSound();  // 输出: Woof!
    }

    // 创建猫对象
    THolder<IAnimal> cat = TAnimalFactory::MakeHolder("cat");
    if (cat) {
        cat->MakeSound();  // 输出: Meow!
    }
}
```

### 带参数的对象工厂
```cpp
#include <library/cpp/object_factory/object_factory.h>

using namespace NObjectFactory;

// 带参数的产品基类
class IShape {
public:
    virtual ~IShape() {}
    virtual double GetArea() = 0;
    virtual TString GetName() = 0;
};

// 带参数的具体实现
class Circle: public IShape {
    double radius;

public:
    Circle(double r) : radius(r) {}

    double GetArea() override {
        return 3.14159 * radius * radius;
    }

    TString GetName() override {
        return "Circle";
    }

    FACTORY_OBJECT_NAME(Circle)
};

class Rectangle: public IShape {
    double width, height;

public:
    Rectangle(double w, double h) : width(w), height(h) {}

    double GetArea() override {
        return width * height;
    }

    TString GetName() override {
        return "Rectangle";
    }

    FACTORY_OBJECT_NAME(Rectangle)
};

// 带参数的对象工厂类型
typedef TObjectFactory<IShape, TString, double> TSingleParamShapeFactory;
typedef TObjectFactory<IShape, TString, double, double> TDoubleParamShapeFactory;

// 注册带参数的产品
static TSingleParamShapeFactory::TRegistrator<Circle> CircleReg("circle");
static TDoubleParamShapeFactory::TRegistrator<Rectangle> RectReg("rectangle");

void CreateShapes() {
    // 创建圆形（单参数）
    THolder<IShape> circle = TSingleParamShapeFactory::MakeHolder("circle", 5.0);
    printf("Circle area: %.2f\n", circle->GetArea());

    // 创建矩形（双参数）
    THolder<IShape> rectangle = TDoubleParamShapeFactory::MakeHolder("rectangle", 4.0, 6.0);
    printf("Rectangle area: %.2f\n", rectangle->GetArea());
}
```

### 高级用法
```cpp
#include <library/cpp/object_factory/object_factory.h>

using namespace NObjectFactory;

// 插件系统示例
class IPlugin {
public:
    virtual ~IPlugin() {}
    virtual void Initialize() = 0;
    virtual void Execute() = 0;
    virtual TString GetVersion() = 0;
};

class DatabasePlugin: public IPlugin {
public:
    void Initialize() override {
        printf("Database plugin initialized\n");
    }

    void Execute() override {
        printf("Database plugin executing\n");
    }

    TString GetVersion() override {
        return "1.0.0";
    }

    FACTORY_OBJECT_NAME(DatabasePlugin)
};

class CachePlugin: public IPlugin {
public:
    void Initialize() override {
        printf("Cache plugin initialized\n");
    }

    void Execute() override {
        printf("Cache plugin executing\n");
    }

    TString GetVersion() override {
        return "2.1.0";
    }

    FACTORY_OBJECT_NAME(CachePlugin)
};

typedef TObjectFactory<IPlugin, TString> TPluginFactory;

static TPluginFactory::TRegistrator<DatabasePlugin> DbPluginReg;
static TPluginFactory::TRegistrator<CachePlugin> CachePluginReg;

void PluginSystemDemo() {
    // 获取所有注册的插件
    TSet<TString> keys = TPluginFactory::GetRegisteredKeys();
    printf("Registered plugins: ");
    for (const auto& key : keys) {
        printf("%s ", key.c_str());
    }
    printf("\n");

    // 检查特定插件是否存在
    if (TPluginFactory::Has("DatabasePlugin")) {
        printf("Database plugin is available\n");
    }

    // 加载并执行所有插件
    for (const auto& key : keys) {
        THolder<IPlugin> plugin = TPluginFactory::MakeHolder(key);
        if (plugin) {
            plugin->Initialize();
            plugin->Execute();
        }
    }
}
```

## 实现原理

### 工厂模式设计
Object Factory 采用了经典的工厂模式设计：

#### 核心组件
1. **IFactoryObjectCreator** - 抽象对象创建器接口
2. **TFactoryObjectCreator** - 具体对象创建器实现
3. **IObjectFactory** - 工厂基类
4. **TParametrizedObjectFactory** - 参数化工厂实现

#### 设计原则
- **开闭原则**：对扩展开放，对修改封闭
- **依赖倒置**：依赖抽象而非具体实现
- **单一职责**：每个类只负责一个职责
- **接口隔离**：客户端不依赖不需要的接口

### 类型系统
#### 编译时类型安全
```cpp
template <class TProduct, class... TArgs>
class IFactoryObjectCreator {
public:
    virtual TProduct* Create(TArgs... args) const = 0;
    virtual ~IFactoryObjectCreator() {}
};
```

#### 可变参数模板支持
- **C++11 可变参数**：支持任意数量和类型的构造参数
- **完美转发**：保持参数的值类别
- **SFINAE**：类型检查和重载解析

### 线程安全机制
#### 读写锁保护
```cpp
class IObjectFactory {
private:
    TMap<TKey, ICreatorPtr> Creators;
    TRWMutex CreatorsLock;  // 读写锁保护
};
```

#### 线程安全保证
- **读操作**：多个线程可并发读取
- **写操作**：写操作独占访问
- **注册安全**：对象注册时的线程安全
- **创建安全**：对象创建时的线程安全

### 内存管理
#### 智能指针管理
```cpp
typedef TSimpleSharedPtr<IFactoryObjectCreator<TProduct, TArgs...>> ICreatorPtr;
```

#### RAII 资源管理
- **自动清理**：析构时自动释放资源
- **异常安全**：异常情况下正确清理
- **内存泄漏防护**：避免内存泄漏

### 单例模式
#### 全局工厂实例
```cpp
template <class T>
static TProduct* Construct(const T& key, TArgs... args) {
    return Singleton<TParametrizedObjectFactory<TProduct, TKey, TArgs...>>()
        ->Create(key, std::forward<TArgs>(args)...);
}
```

#### 单例优势
- **全局访问**：提供全局访问点
- **延迟初始化**：第一次使用时初始化
- **线程安全**：线程安全的单例实现

## 应用场景

### 插件系统
- **动态加载**：运行时加载插件
- **类型注册**：插件类型自动注册
- **版本管理**：插件版本控制
- **依赖管理**：插件间依赖关系

### 游戏开发
- **实体管理**：游戏实体创建和管理
- **组件系统**：游戏组件动态添加
- **资源管理**：游戏资源按需加载
- **状态管理**：游戏状态切换

### 序列化/反序列化
- **类型映射**：字符串到类型的映射
- **动态创建**：根据类型信息创建对象
- **格式支持**：多种序列化格式支持
- **版本兼容**：不同版本的兼容处理

### 配置系统
- **驱动程序**：根据配置加载驱动
- **数据库连接**：不同数据库的连接器
- **缓存实现**：多种缓存策略选择
- **日志系统**：不同日志输出器选择

### 网络协议
- **协议栈**：动态加载网络协议
- **编解码器**：消息编解码器选择
- **传输层**：不同传输协议支持
- **压缩算法**：多种压缩算法支持

## 高级特性

### 宏定义支持
```cpp
#define FACTORY_OBJECT_NAME(Name)              \
    static TString GetTypeName() {             \
        return #Name;                          \
    }                                          \
    virtual TString GetType() const override { \
        return #Name;                          \
    }
```

#### 宏的好处
- **自动生成**：自动生成类型识别代码
- **一致性**：确保类型名的一致性
- **简化使用**：减少样板代码

### 注册器模式
```cpp
template <class Product>
class TRegistrator {
public:
    TRegistrator(const TKey& key) {
        Singleton<TParametrizedObjectFactory<TProduct, TKey, TArgs...>>()
            ->template Register<Product>(key);
    }
};
```

#### 自动注册优势
- **静态初始化**：程序启动时自动注册
- **零配置**：无需手动注册代码
- **类型安全**：编译时检查注册类型

### 类型查询和过滤
```cpp
// 获取所有注册的键
static TSet<TKey> GetRegisteredKeys();

// 按类型过滤注册的键
template <class TDerivedProduct>
static TSet<TKey> GetRegisteredKeys() {
    // 只返回可转换为指定类型的注册键
}
```

## 性能特性

### 时间复杂度
- **注册**：O(log n) - 基于 map 的插入
- **查找**：O(log n) - 基于 map 的查找
- **创建**：O(1) - 直接对象创建

### 内存使用
- **工厂开销**：每个类型存储创建器指针
- **对象开销**：标准对象创建开销
- **映射开销**：基于 map 的键值映射

### 线程性能
- **并发读取**：支持多线程并发读取
- **序列写入**：写入操作需要序列化
- **锁竞争**：最小化锁竞争时间

## 最佳实践

### 命名约定
- **类型名称**：使用描述性的类型名
- **注册键**：使用一致的命名约定
- **宏使用**：合理使用 FACTORY_OBJECT_NAME

### 错误处理
- **空指针检查**：检查 Create 返回的空指针
- **异常处理**：处理可能的异常情况
- **默认值**：提供合理的默认实现

### 性能优化
- **批量注册**：减少锁竞争
- **缓存结果**：缓存频繁创建的对象
- **延迟创建**：按需创建对象

## 注意事项

### 线程安全
- 注册操作和创建操作都是线程安全的
- 建议在程序初始化阶段完成所有注册
- 避免在多线程环境下频繁注册/注销

### 内存管理
- 工厂返回的是裸指针，需要手动管理
- 推荐使用 THolder 进行自动内存管理
- 确保对象正确析构

### 异常安全
- 构造函数抛出异常是安全的
- 工厂本身不会因构造异常而损坏
- 建议在对象构造函数中进行必要的验证