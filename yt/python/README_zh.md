# YTsaurus Python 客户端库

本目录包含 YTsaurus 的 Python 客户端库和相关工具。

## 目录结构

- **client/** - 轻量级客户端库
  - 提供基本的 YTsaurus 操作功能
  - 不包含 RPC 功能，适用于简单场景

- **client_lite/** - 精简客户端
  - 最小化的客户端实现
  - 仅包含核心功能

- **client_with_rpc/** - 完整 RPC 客户端
  - 包含完整的 RPC 功能
  - 支持所有 YTsaurus 操作

- **contrib/** - 第三方依赖
  - Python 客户端所需的第三方库

- **examples/** - 示例代码
  - 各种使用场景的示例
  - 包含最佳实践演示

- **packages/** - Python 包源码
  - `ytsaurus-client` - PyPI 发布的客户端包
  - `ytsaurus-local` - 本地开发版本
  - `ytsaurus-yson` - YSON 格式支持
  - `ytsaurus-rpc-driver` - RPC 驱动

- **yt/** - 核心库源码
  - 主要的 Python 库实现

## 功能特性

### 客户端功能
- **数据操作**: 读取、写入、删除数据
- **表操作**: 创建、修改、删除表
- **MapReduce**: 分布式计算任务
- **事务支持**: ACID 事务操作
- **查询功能**: SQL 查询支持

### 数据格式支持
- **YSON**: YTsaurus 原生数据格式
- **JSON**: 标准 JSON 格式支持
- **YAML**: YAML 格式支持
- **Protobuf**: Protocol Buffers 支持

## 使用方法

### 安装客户端
```bash
# 使用 pip 安装
pip install ytsaurus-client

# 或从源码安装
pip install -e .
```

### 基本使用示例
```python
import yt

# 连接到集群
client = yt.YtClient(proxy="<cluster-proxy>")

# 读取数据
data = client.read_table("//tmp/my_table")

# 写入数据
client.write_table("//tmp/output_table", data)

# 运行 MapReduce 操作
client.run_map_reduce(
    mapper="cat",
    source_table="//tmp/input",
    destination_table="//tmp/output"
)

# 执行查询
result = client.select_rows("SELECT * FROM `//tmp/my_table` WHERE value > 10")
```

## 开发环境设置

### 准备工作
```bash
# 设置环境变量
export SOURCE_ROOT=<源码目录>
export BUILD_ROOT=<构建目录>
export PYTHON_ROOT=<Python模块目录>

# 创建模块目录
mkdir "$PYTHON_ROOT"

# 安装依赖
pip3 install wheel
pip install -e yt/python/packages
```

### 构建步骤
```bash
# 1. 构建原生库
cd "$BUILD_ROOT"
ninja yson_lib driver_lib driver_rpc_lib

# 2. 生成 Proto 模块
generate_python_proto --source-root "$SOURCE_ROOT" --output "$PYTHON_ROOT"

# 3. 准备 Python 模块
prepare_python_modules \
    --source-root "$SOURCE_ROOT" \
    --build-root "$BUILD_ROOT" \
    --output-path "$PYTHON_ROOT" \
    --prepare-bindings-libraries
```

### 使用开发版本
```bash
# 将模块路径添加到 PYTHONPATH
export PYTHONPATH="$PYTHON_ROOT:$PYTHONPATH"

# 现在可以使用开发版本的库了
python -c "import yt; print('YTsaurus Python client loaded')"
```

## 打包发布

### 构建 Wheel 包
```bash
# 纯 Python 库
python3 setup.py bdist_wheel --universal

# 二进制库
python3 setup.py bdist_wheel --py-limited-api cp34
```

### 发布到 PyPI
```bash
# 上传到测试 PyPI
twine upload --repository testpypi dist/*.whl

# 上传到正式 PyPI
twine upload dist/*.whl
```

## 文档生成

### 生成 HTML 文档
```bash
# 安装文档工具
pip install sphinx sphinx-argparse

# 生成文档
cd "$PYTHON_ROOT"
PYTHONPATH="$PYTHON_ROOT" sphinx-apidoc -F -o "$DOCS_ROOT" yt
PYTHONPATH="$PYTHON_ROOT" sphinx-build -b html "$DOCS_ROOT" "$DOCS_ROOT/_html"
```

## 依赖项

### 运行时依赖
- Python 3.8+
- requests (HTTP 客户端)
- pyyaml (YAML 支持)
- lz4 (压缩支持)

### 开发依赖
- CMake 3.22+
- Clang-18
- Protocol Buffers
- Ninja 构建系统

## 实现原理

### 架构设计
Python 客户端采用分层架构：

1. **传输层**: 处理与 YTsaurus 集群的通信
2. **协议层**: 实现 YTsaurus RPC 协议
3. **API 层**: 提供高级编程接口
4. **工具层**: 提供便利功能和工具

### 性能优化
- **连接池**: 复用 HTTP 连接
- **批量操作**: 支持批量读写操作
- **压缩传输**: 自动压缩大数据
- **异步支持**: 支持异步操作模式

### 错误处理
- **重试机制**: 自动重试失败的操作
- **超时控制**: 可配置的操作超时
- **错误分类**: 详细的错误类型和原因

## 最佳实践

### 性能优化建议
1. 使用批量操作减少网络往返
2. 合理设置读取缓冲区大小
3. 使用压缩减少传输数据量
4. 复用客户端实例

### 资源管理
1. 及时关闭不再使用的客户端
2. 使用上下文管理器管理资源
3. 合理设置连接池大小

### 错误处理
1. 始终检查操作返回状态
2. 使用 try-except 处理异常
3. 实现适当的重试逻辑

更多详细文档请参考：https://ytsaurus.tech/docs/zh/api/python/start