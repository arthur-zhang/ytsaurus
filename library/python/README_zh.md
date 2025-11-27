# Python 语言库

本目录包含 YTsaurus 的 Python 语言支持库，提供丰富的 Python 工具和组件集合。

## 目录结构

### 核心组件
- **cyson/** - C 扩展 YSON 库
  - 高性能的 YSON 序列化/反序列化
  - CPython 绑定
  - 优化的内存管理

- **cores/** - 核心模块
  - 基础数据结构
  - 核心算法实现
  - 系统接口封装

### 工具库
- **codecs/** - 编解码器
  - 各种数据格式的编解码
  - 压缩算法支持
  - 二进制数据处理

- **filelock/** - 文件锁
  - 跨平台文件锁定
  - 进程间同步
  - 死锁检测

- **fs/** - 文件系统工具
  - 文件操作封装
  - 路径处理
  - 目录遍历

- **pytest/** - 测试框架
  - 测试辅助工具
  - Mock 生成器
  - 测试数据管理

### 系统接口
- **prctl/** - 进程控制
  - Linux 进程控制接口
  - 资源限制管理
  - 进程属性设置

- **resource/** - 资源管理
  - 系统资源监控
  - 内存使用统计
  - CPU 使用跟踪

- **runtime/** - 运行时
  - Python 运行时工具
  - 执行环境管理
  - 性能分析

### 工具集
- **find_root/** - 根目录查找
  - 项目根目录定位
  - VCS 支持
  - 配置文件查找

- **strings/** - 字符串工具
  - 字符串处理函数
  - 编码转换
  - 模式匹配

- **symbols/** - 符号表
  - 符号解析
  - 调试信息
  - 堆栈跟踪

- **testing/** - 测试工具
  - 单元测试支持
  - 集成测试框架
  - 性能测试

## 功能特性

### 高性能 YSON 处理
- C 扩展实现，性能优异
- 与原生 Python 完全兼容
- 支持流式处理
- 内存高效的序列化

### 文件系统操作
- 跨平台文件锁定
- 原子文件操作
- 符号链接处理
- 权限管理

### 测试框架
- 丰富的测试工具
- 自动化测试生成
- 性能基准测试
- Mock 和存根支持

## 使用方法

### 安装依赖
```bash
# 安装依赖
pip install -r requirements.txt

# 开发模式安装
pip install -e .
```

### 使用 YSON
```python
import cyson

# 序列化
data = {"key": "value", "number": 42}
yson_str = cyson.serialize(data)

# 反序列化
parsed = cyson.deserialize(yson_str)
print(parsed)  # {'key': 'value', 'number': 42}
```

### 使用文件锁
```python
from library.python.filelock import FileLock

# 获取文件锁
with FileLock("/tmp/lockfile") as lock:
    # 临界区代码
    print("Lock acquired!")
    # 执行需要同步的操作
```

### 使用测试工具
```python
from library.pytest import assert_contains, assert_equals

# 使用断言
assert_contains([1, 2, 3], 2)  # 通过
assert_equals(1 + 1, 2)  # 通过

# 使用测试数据管理
from library.testing import TestData

test_data = TestData()
test_data.add_case("input1", "expected1")
```

### 使用资源管理
```python
from library.python.resource import ResourceManager

# 创建资源管理器
manager = ResourceManager()

# 监控内存使用
memory_info = manager.get_memory_usage()
print(f"Memory: {memory_info.rss} MB")

# 监控 CPU 使用
cpu_info = manager.get_cpu_usage()
print(f"CPU: {cpu_info.percent}%")
```

## 组件详细说明

### cyson - YSON 处理
高性能 YSON（YTsaurus Native Object Notation）处理器：
- **序列化**: 将 Python 对象转换为 YSON 格式
- **反序列化**: 从 YSON 格式重建 Python 对象
- **流式处理**: 支持大文件的流式读写
- **类型支持**: 支持所有 Python 内置类型

性能特性：
- 比纯 Python 实现快 10-100 倍
- 内存使用优化
- 支持 CPython 和 PyPy

### filelock - 文件锁定
跨平台的文件锁定机制：
- **进程锁**: 防止多进程同时访问
- **线程锁**: 线程级别的同步
- **超时机制**: 避免死锁
- **自动释放**: 异常安全

### fs - 文件系统工具
文件和目录操作封装：
- **原子操作**: 保证操作的原子性
- **权限管理**: 细粒度的权限控制
- **路径处理**: 跨平台路径操作
- **目录树**: 高效的目录遍历

### pytest - 测试框架
增强的测试工具集：
- **断言扩展**: 丰富的断言函数
- **Mock 工具**: 生成模拟对象
- **数据驱动**: 参数化测试
- **覆盖率**: 代码覆盖率分析

## 性能优化

### 编译 C 扩展
```bash
# 编译 cyson C 扩展
cd library/python/cyson
python setup.py build_ext --inplace

# 运行性能测试
python -m pytest cyson/tests/test_performance.py
```

### 内存优化
```python
# 使用内存池
from library.python.memory import MemoryPool

pool = MemoryPool()
obj = pool.allocate(object)
# 自动管理内存
```

## 测试

### 运行所有测试
```bash
# 运行单元测试
python -m pytest library/python/

# 运行性能测试
python -m pytest library/python/ -k performance

# 生成覆盖率报告
python -m pytest library/python/ --cov=library.python --cov-report=html
```

### 特定组件测试
```bash
# 测试 cyson
python -m pytest library/python/cyson/

# 测试 filelock
python -m pytest library/python/filelock/

# 测试 pytest 工具
python -m pytest library/python/pytest/
```

## 最佳实践

1. **错误处理**
   ```python
   from library.python.errors import wrap_errors

   @wrap_errors
   def risky_operation():
       # 可能出错的操作
       pass
   ```

2. **资源管理**
   ```python
   from library.python.contextlib import contextmanager

   @contextmanager
   def managed_resource():
       resource = acquire_resource()
       try:
           yield resource
       finally:
           resource.release()
   ```

3. **性能优化**
   ```python
   # 使用缓存装饰器
   from library.python.cache import cached

   @cached
   def expensive_computation(x):
       return compute(x)
   ```

## 版本兼容性

- Python 版本：3.8+
- 操作系统：Linux、macOS、Windows
- 架构：x86_64、ARM64

## 贡献指南

1. 遵循 PEP 8 编码规范
2. 添加适当的测试用例
3. 更新文档和类型注解
4. 确保向后兼容性

## 许可证

本库遵循 Apache 2.0 许可证。详见 LICENSE 文件。