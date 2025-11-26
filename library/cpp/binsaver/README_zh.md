# binsaver - 二进制序列化库

## 概述

binsaver 是一个高效的二进制序列化/反序列化库，用于将 C++ 对象转换为二进制格式以便存储或传输。该库支持复杂的 C++ 数据结构，包括容器、智能指针、多态对象等，并提供了多种 I/O 后端支持。

## 核心特性

### 1. 自动序列化
- **自动推导**：自动识别可平凡复制的类型，使用直接内存拷贝
- **自定义序列化**：支持通过重载 `operator&` 实现自定义序列化逻辑
- **模板特化**：支持为特定类型提供模板特化

### 2. 广泛的类型支持
支持几乎所有的标准 C++ 类型：
- **基础类型**：int、float、double、bool 等
- **容器类**：vector、list、map、set、unordered_map 等
- **智能指针**：unique_ptr、shared_ptr、auto_ptr
- **变体类型**：std::variant、std::optional
- **字符串类**：std::string、TString
- **数组类型**：C 数组、std::array

### 3. 多种 I/O 后端
- **内存流**：在内存中序列化/反序列化
- **文件流**：直接文件 I/O
- **缓冲流**：带缓冲的 I/O，提高性能
- **块存储**：适合大型对象的分块存储
- **Blob 支持**：与 TBlob 无缝集成

## 文件说明

### 核心组件
- **bin_saver.h/.cpp**：核心序列化引擎
  - `IBinSaver`：序列化接口类
  - 支持读写和压缩写入三种模式
  - 提供类型检查和溢出保护

- **class_factory.h**：支持多态对象的序列化
  - 通过工厂模式实现动态类型创建
  - 支持虚函数和继承关系

### I/O 实现
- **mem_io.h/.cpp**：内存流实现
  - `TMemoryStream`：基本内存流
  - `THugeMemoryStream`：分块大内存流（支持 >1GB）
  - `SerializeMem`：便捷的内存序列化函数

- **buffered_io.h/.cpp**：缓冲 I/O 实现
  - 提高性能的缓冲读写
  - 批量操作优化

- **blob_io.h/.cpp**：Blob I/O 支持
  - 与 TBlob 类型集成
  - 零拷贝操作

- **util_stream_io.h/.cpp**：工具流适配器
  - 将标准流适配为二进制流

## 使用示例

### 基本序列化

```cpp
#include <library/cpp/binsaver/bin_saver.h>
#include <library/cpp/binsaver/mem_io.h>

struct Person {
    std::string Name;
    int Age;
    std::vector<std::string> Hobbies;

    // 自定义序列化（可选）
    int operator&(IBinSaver& f) {
        f.Add(1, &Name);
        f.Add(2, &Age);
        f.Add(3, &Hobbies);
        return 0;
    }
};

// 序列化到内存
TVector<char> data;
Person p{"Alice", 30, {"reading", "swimming"}};
SerializeMem(false, &data, p);  // false = 写入

// 反序列化
Person p2;
SerializeMem(true, &data, p2);  // true = 读取
```

### 文件序列化

```cpp
#include <library/cpp/binsaver/bin_saver.h>
#include <util/stream/file.h>

// 写入文件
{
    TFileOutput out("person.bin");
    IBinSaver saver(out, false);  // false = 写入模式
    saver.Add(1, &p);
}

// 从文件读取
{
    TFileInput in("person.bin");
    IBinSaver saver(in, true);  // true = 读取模式
    saver.Add(1, &p2);
}
```

### 压缩序列化

```cpp
// 使用压缩模式写入
TFileOutput out("person_compressed.bin");
IBinSaver saver(out, false, true);  // 第三个参数启用压缩
saver.Add(1, &p);
```

### 容器序列化

```cpp
#include <vector>
#include <map>
#include <library/cpp/binsaver/bin_saver.h>

// 自动序列化标准容器
std::vector<int> numbers = {1, 2, 3, 4, 5};
std::map<std::string, double> scores = {{"Alice", 95.5}, {"Bob", 87.0}};

// 任何容器都可以直接序列化
TVector<char> data;
{
    TMemoryStream stream(&data);
    IBinSaver saver(stream, false);
    saver.Add(1, &numbers);
    saver.Add(2, &scores);
}
```

### 智能指针支持

```cpp
#include <memory>

struct TreeNode {
    int Value;
    std::unique_ptr<TreeNode> Left;
    std::unique_ptr<TreeNode> Right;

    int operator&(IBinSaver& f) {
        f.Add(1, &Value);
        f.Add(2, &Left);
        f.Add(3, &Right);
        return 0;
    }
};

// 自动处理智能指针
auto tree = std::make_unique<TreeNode>();
tree->Value = 42;
tree->Left = std::make_unique<TreeNode>();
tree->Left->Value = 10;

// 直接序列化
TVector<char> data;
SerializeMem(false, &data, tree);
```

## 序列化模式

### 三种模式
1. **SAVER_MODE_READ**（1）：读取模式
2. **SAVER_MODE_WRITE**（2）：普通写入模式
3. **SAVER_MODE_WRITE_COMPRESSED**（3）：压缩写入模式

### 选择建议
- **持久化存储**：使用压缩模式节省空间
- **网络传输**：根据网络带宽选择
- **临时缓存**：使用普通模式，速度最快
- **调试场景**：使用普通模式，便于检查

## 性能优化

### 1. 平凡类型优化
```cpp
// 对于平凡可复制类型，使用直接内存拷贝
struct Point {
    float x, y, z;  // 平凡类型
};

// 自动优化为 memcpy
TVector<char> data;
SerializeMem(false, &data, point);
```

### 2. 批量序列化
```cpp
// 使用 AddMultiple 批量处理
std::vector<Point> points(1000);
IBinSaver saver(stream, false);
saver.Add(1, &points);  // 优化的向量序列化
```

### 3. 压缩选项
- 自动检测压缩效果
- 对重复数据效果好
- 对随机数据可能增加体积

## 高级特性

### 1. 版本兼容
```cpp
struct DataV1 {
    int Version;
    std::string Name;
    // ... V1 字段
};

struct DataV2 {
    int Version;
    std::string Name;
    double Score;  // V2 新增字段

    int operator&(IBinSaver& f) {
        f.Add(1, &Version);
        f.Add(2, &Name);
        if (Version >= 2) {
            f.Add(3, &Score);
        }
        return 0;
    }
};
```

### 2. 自定义序列化
```cpp
class CustomClass {
private:
    std::vector<int> internal_data_;

public:
    // 提供序列化接口
    template <class Saver>
    void Save(Saver& saver) const {
        size_t size = internal_data_.size();
        saver.Add(1, &size);
        for (size_t i = 0; i < size; ++i) {
            saver.Add(2, &internal_data_[i]);
        }
    }

    template <class Saver>
    void Load(Saver& saver) {
        size_t size;
        saver.Add(1, &size);
        internal_data_.resize(size);
        for (size_t i = 0; i < size; ++i) {
            saver.Add(2, &internal_data_[i]);
        }
    }

    int operator&(IBinSaver& f) {
        if (f.IsReading()) {
            Load(f);
        } else {
            Save(f);
        }
        return 0;
    }
};
```

## 平台支持

### 构建系统
提供多平台的 CMakeLists：
- `CMakeLists.linux-x86_64.txt`
- `CMakeLists.linux-aarch64.txt`
- `CMakeLists.darwin-x86_64.txt`
- `CMakeLists.darwin-arm64.txt`

### 兼容性
- 跨平台二进制兼容
- 支持大端和小端系统
- 32/64 位系统兼容

## 测试

### 单元测试
- **ut/**：主要功能测试
- **ut_util/**：工具函数测试

运行测试：
```bash
ya make binsaver/ut
./ut_bin_saver
```

## 最佳实践

1. **设计考虑**
   - 保持序列化接口稳定
   - 为新字段提供默认值
   - 使用版本号管理变更

2. **性能考虑**
   - 对大对象使用流式处理
   - 合理使用压缩
   - 避免频繁的小对象序列化

3. **安全考虑**
   - 验证输入数据
   - 防止缓冲区溢出
   - 谨慎处理用户输入

4. **调试技巧**
   - 使用十六进制查看器检查输出
   - 启用详细日志
   - 使用单元测试验证

## 注意事项

1. 指针和引用的序列化需要特殊处理
2. 虚函数和多态对象需要注册工厂
3. 循环引用会导致无限递归
4. 序列化格式可能随版本变化
5. 压缩模式会增加 CPU 开销