# C 语言库

本目录包含 YTsaurus 的 C 语言接口库，提供与 C 语言应用程序的集成能力。

## 目录结构

- **cyson/** - C YSON 库
  - YSON（YTsaurus Native Object Notation）格式的 C 语言实现
  - 提供 YSON 数据的序列化和反序列化功能
  - 支持流式处理和内存操作

## 功能特性

### YSON 处理
- **序列化**: 将 C 数据结构转换为 YSON 格式
- **反序列化**: 从 YSON 格式读取数据到 C 结构
- **流式处理**: 支持大文件的流式读写
- **内存管理**: 高效的内存使用和管理

### 跨语言兼容
- 与 Python/C++/Java/Go 客户端完全兼容
- 标准的 C 接口，易于集成
- 支持所有主流平台（Linux、macOS、Windows）

## 使用方法

### 编译安装
```bash
# 使用 ya make 构建
ya make library/c

# 使用 CMake 构建
cmake --build . --target cyson
```

### 基本使用示例
```c
#include "library/c/cyson/cyson.h"
#include <stdio.h>

int main() {
    // 创建输入流
    const char* yson_data = "{key=value}";
    yson_input_stream* stream = yson_input_stream_from_string(
        yson_data, strlen(yson_data));

    // 创建读取器
    yson_reader* reader = yson_reader_new(stream);

    // 读取数据
    yson_event event;
    while (yson_reader_next(reader, &event)) {
        // 处理 YSON 事件
        printf("Event type: %d\n", event.type);
    }

    // 清理资源
    yson_reader_free(reader);
    yson_input_stream_free(stream);

    return 0;
}
```

### 文件操作示例
```c
// 从文件读取 YSON
FILE* file = fopen("data.yson", "rb");
yson_input_stream* stream = yson_input_stream_from_file(file, 4096);
yson_reader* reader = yson_reader_new(stream);

// 处理数据...

// 清理
yson_reader_free(reader);
yson_input_stream_free(stream);
fclose(file);
```

## API 参考

### 输入流操作
- `yson_input_stream_from_string()` - 从字符串创建输入流
- `yson_input_stream_from_file()` - 从文件创建输入流
- `yson_input_stream_from_fd()` - 从文件描述符创建输入流

### 读取器操作
- `yson_reader_new()` - 创建 YSON 读取器
- `yson_reader_next()` - 读取下一个 YSON 事件
- `yson_reader_free()` - 释放读取器资源

### 输出流操作
- `yson_output_stream_to_file()` - 创建文件输出流
- `yson_output_stream_to_buffer()` - 创建内存缓冲输出流

### 写入器操作
- `yson_writer_new()` - 创建 YSON 写入器
- `yson_writer_write_*()` - 写入各种 YSON 数据类型
- `yson_writer_free()` - 释放写入器资源

## 依赖项

- C99 兼容的编译器
- 标准 C 库
- YTsaurus 核心库（运行时）

## 性能特性

- **零拷贝**: 尽可能避免内存拷贝
- **流式处理**: 支持处理超大文件
- **内存效率**: 优化的内存使用模式
- **线程安全**: 部分操作支持多线程

## 错误处理

```c
// 检查错误
if (yson_reader_has_error(reader)) {
    const char* error_msg = yson_reader_get_error(reader);
    fprintf(stderr, "YSON error: %s\n", error_msg);
}
```

## 最佳实践

1. **资源管理**
   - 始终调用相应的 free 函数释放资源
   - 使用 RAII 模式管理对象生命周期

2. **错误处理**
   - 检查所有可能失败的操作
   - 提供详细的错误信息

3. **性能优化**
   - 使用适当的缓冲区大小
   - 重用流和读取器对象
   - 批量处理数据

4. **线程安全**
   - 每个线程使用独立的读取器/写入器
   - 共享数据时使用适当的同步机制

## 示例项目

完整的使用示例请参考：
- `examples/c/yson_reader/` - YSON 读取示例
- `examples/c/yson_writer/` - YSON 写入示例
- `examples/c/integration/` - 与其他语言的集成示例

## 版本兼容性

- 当前版本：1.0.0
- 向后兼容：支持所有 1.x 版本
- ABI 稳定性：保证主版本内的 ABI 兼容性