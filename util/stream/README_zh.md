# 流处理库

本模块提供高效的流处理功能，包括缓冲流、文件流、格式化输出等组件。

## 功能特性

### 流接口
- 统一的流接口设计
- 缓冲 I/O 支持
- 异步读取操作
- 内存映射文件

### 缓冲管理
- 可配置缓冲区大小
- 自动缓冲区管理
- 内存对齐支持
- 零拷贝优化

### 文件操作
- 高效文件读写
- 直接 I/O 支持
- 大文件处理
- 文件格式化

## 主要组件

### 核心流
- **buffer.h/cpp** - 缓冲流实现
- **buffered.h/cpp** - 带缓冲的流
- **file.h/cpp** - 文件流
- **direct_io.h/cpp** - 直接 I/O 流

### 格式化
- **format.h/cpp** - 流格式化工具

### 工具类
- **aligned.h/cpp** - 内存对齐工具

## 使用方法

### 缓冲流
```cpp
#include "util/stream/buffer.h"

// 创建缓冲区流
TBufferedOutput output(4096);  // 4KB 缓冲区

// 写入数据
output.Write("Hello, ");
output.Write("World!");

// 刷新缓冲区
output.Finish();
```

### 带缓冲的流
```cpp
#include "util/stream/buffered.h"

// 包装已有流
TBuffered<TFileOutput> buffered(fileOutput, 8192);

// 批量写入
for (int i = 0; i < 1000; ++i) {
    buffered << "Data " << i << "\n";
}

// 自动刷新时写入
buffered.Finish();
```

### 文件流
```cpp
#include "util/stream/file.h"

// 输出文件流
TFileOutput fileOut("output.txt");
fileOut << "Hello, File!" << Endl;

// 输入文件流
TFileInput fileIn("input.txt");
TString line;
while (fileIn.ReadLine(line)) {
    ProcessLine(line);
}

// 追加模式
TFileOutput appendFile("log.txt", OpenMode::ForAppend);
```

### 直接 I/O
```cpp
#include "util/stream/direct_io.h"

// 创建直接 I/O 文件流
TDirectFileOutput file("data.bin", OpenMode::Create);

// 对齐的缓冲区
TAlignedBuffer buffer(4096);

// 写入数据
file.Write(buffer.Data(), buffer.Size());
```

### 流格式化
```cpp
#include "util/stream/format.h"

// 使用格式化器
TFormattedOutput out;

// 格式化输出
out << "Name: " << name << "\n"
    << "Age: " << age << "\n"
    << "Score: " << Format("%.2f", score) << "\n";

//十六进制输出
out << Hex(data, size) << "\n";

// 二进制输出
out << Bin(value) << "\n";
```

## 流接口设计

### 输入流
```cpp
class IInputStream {
public:
    // 读取数据
    size_t Read(void* buf, size_t len);

    // 读取到字符串
    size_t ReadLine(TString& line);

    // 读取单个字符
    char ReadChar();

    // 跳过数据
    void Skip(size_t len);

    // 检查结束
    bool Finished() const;
};
```

### 输出流
```cpp
class IOutputStream {
public:
    // 写入数据
    void Write(const void* buf, size_t len);

    // 写入字符串
    void Write(const TString& str);

    // 刷新
    void Flush();

    // 完成
    void Finish();
};
```

## 性能优化

### 缓冲策略
```cpp
// 自定义缓冲区大小
constexpr size_t OptimalBufferSize = 64 * 1024;  // 64KB

TBufferedOutput fileOutput(fileHandle, OptimalBufferSize);
```

### 批量操作
```cpp
// 批量写入
std::vector<TString> chunks = PrepareChunks();
for (const auto& chunk : chunks) {
    output.Write(chunk);
}
output.Flush();  // 一次性刷新
```

### 内存对齐
```cpp
#include "util/stream/aligned.h"

// 对齐缓冲区
TAlignedBuffer buffer(4096);  // 4KB 对齐
void* alignedPtr = buffer.Data();  // 保证对齐
```

## 高级功能

### 流链
```cpp
// 链式组合多个流
TBuffered<TGZippedOutput<TFileOutput>>
    compressedFile("data.gz");

compressedFile << largeData;
compressedFile.Finish();
```

### 异步流
```cpp
// 异步写入（如果支持）
TAsyncOutput asyncOutput(output);
asyncOutput.WriteAsync(data, size);
```

### 内存映射
```cpp
// 内存映射文件流
TMappedFileInput mappedFile("large.bin");
const void* data = mappedFile.Map();
size_t size = mappedFile.Length();

// 直接访问内存
ProcessData(static_cast<const char*>(data), size);
```

## 格式化选项

### 数字格式
```cpp
// 小数格式
out << Fixed(3.14159, 2);     // 3.14
out << Scientific(12345, 2);   // 1.23e+04

// 进制转换
out << Hex(255);               // 0xFF
out << Oct(8);                 // 010
out << Bin(5);                 // 101
```

### 字符串格式
```cpp
// 填充和对齐
out << LeftPad("Hello", 10, '-');  // "Hello-----"
out << RightPad("World", 10, '-'); // "-----World"
out << Center("Hi", 10, ' ');      // "    Hi    "

// 大小写转换
out << Upper("hello");  // "HELLO"
out << Lower("WORLD");  // "world"
```

## 错误处理

### 异常类型
```cpp
try {
    TFileInput file("nonexistent.txt");
} catch (const TFileError& e) {
    std::cerr << "File error: " << e.what() << std::endl;
}
```

### 错误恢复
```cpp
// 容错读取
TFileInput file("data.txt");
try {
    file.Read(buffer, size);
} catch (const TIOError&) {
    // 尝试恢复
    file.Seek(0, SeekDir::Begin);
    file.Read(buffer, size);
}
```

## 性能基准

### 测试指标
- 顺序读取：> 1 GB/s（SSD）
- 顺序写入：> 800 MB/s（SSD）
- 缓冲读取：~10 GB/s（内存）
- 格式化输出：~500 MB/s

### 运行基准测试
```bash
# 运行流性能测试
./ut/stream_perf

# 测试不同缓冲区大小
./ut/stream_perf --buffer-size 4096
```

## 最佳实践

1. **缓冲区大小**
   - 使用 64KB 作为默认大小
   - 根据访问模式调整
   - 考虑缓存行大小

2. **错误处理**
   - 检查所有 I/O 操作
   - 实现重试机制
   - 提供有意义的错误信息

3. **资源管理**
   - 使用 RAII 管理资源
   - 及时关闭文件
   - 避免资源泄露

## 测试

### 单元测试
```bash
# 运行所有测试
./ut/stream_ut

# 运行特定组件测试
./ut/stream_ut --gtest_filter="BufferTest.*"
```

### 集成测试
```bash
# 测试大文件处理
./test/stream_large_file.py

# 测试并发访问
./test/stream_concurrency.py
```

## 平台支持

### Linux
- 完整功能支持
- 直接 I/O 优化
- 异步 I/O 支持

### macOS
- 基础功能支持
- 兼容性保证

### Windows
- Windows API 封装
- 性能优化

## 依赖项

- 标准 C++ 库
- 平台 I/O 库
- C++11 或更高版本

## 版本历史

- v3.0: 添加异步 I/O 支持
- v2.5: 性能优化
- v2.0: 重构流接口
- v1.0: 初始版本