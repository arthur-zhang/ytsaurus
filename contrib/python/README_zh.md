# Python 第三方库集合

本目录包含 YTsaurus 项目依赖的所有 Python 第三方库。这些库提供了丰富的功能，包括数据处理、网络通信、测试框架、异步编程等。

## 目录结构

### 核心数据处理库
- **boto3** - AWS SDK for Python
  - S3 存储操作
  - DynamoDB 数据库访问
  - 其他 AWS 服务集成

- **botocore** - Boto3 的核心库
- **cloudpickle** - Python 对象序列化
  - 支持复杂对象类型
  - 分布式计算中使用

### 网络和异步编程
- **aiohttp** - 异步 HTTP 客户端/服务器
  - 基于 asyncio
  - Web 服务器和客户端
  - WebSocket 支持

- **aiohappyeyeballs** - 异步连接管理
- **aiosignal** - 异步信号处理
- **anyio** - 异步 I/O 兼容层

### Web 框架
- **cheroot** - 高性能 HTTP 服务器
- **click** - 命令行界面创建工具
- **flask** - Web 微框架（可能存在）

### 测试框架
- **allure-pytest** - Allure 测试报告生成器
- **allure-python-commons** - Allure 公共库
- **pytest** - Python 测试框架
- **atomicwrites** - 原子文件写入

### 数据验证和序列化
- **attrs** - Python 类增强
- **Automat** - 自动机状态机
- **cffi** - C Foreign Function Interface
- **certifi** - Mozilla CA 证书包

### 字符串和编码处理
- **chardet** - 字符编码检测
- **charset-normalizer** - 字符集规范化
- **Brotli** - Brotli 压缩算法

### 开发工具
- **APScheduler** - 高级 Python 调度器
- **argcomplete** - 命令行参数自动完成
- **asttokens** - AST 和源码映射
- **beniget** - AST 分析器

### 系统工具
- **appnope** - App Nap 禁用（macOS）
- **colorama** - 跨平台彩色终端输出

### 消息队列
- **confluent-kafka** - Apache Kafka 客户端
  - 高性能消息处理
  - 生产者和消费者支持

### 可能存在的其他库（根据需要）
- **numpy** - 数值计算
- **pandas** - 数据分析
- **matplotlib** - 数据可视化
- **requests** - HTTP 库
- **pyyaml** - YAML 解析器
- **jinja2** - 模板引擎

## 使用方法

### 安装依赖
```bash
# 使用 requirements.txt
pip install -r requirements.txt

# 使用 setup.py
python setup.py install

# 使用 pip 直接安装
pip install <package_name>
```

### 导入和使用
```python
# 使用 aiohttp
import aiohttp
import asyncio

async def fetch_url(url):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            return await response.text()

# 使用 boto3
import boto3

s3 = boto3.client('s3')
response = s3.get_object(Bucket='my-bucket', Key='my-key')
```

## 版本管理

### Python 版本支持
- Python 3.8+
- 推荐使用 Python 3.9 或更高版本

### 库版本策略
- 使用稳定版本
- 避免预发布版本
- 定期更新安全补丁

## 构建集成

### CMake 集成
```cmake
# CMakeLists.txt 示例
find_package(Python3 COMPONENTS Interpreter REQUIRED)

# 安装 Python 依赖
execute_process(
    COMMAND ${Python3_EXECUTABLE} -m pip install -r requirements.txt
    WORKING_DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}
)
```

### 虚拟环境
```bash
# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/macOS
# 或
venv\Scripts\activate  # Windows

# 安装依赖
pip install -r requirements.txt
```

## 性能优化

### 异步编程最佳实践
```python
import asyncio
import aiohttp

async def main():
    # 并发请求
    tasks = []
    async with aiohttp.ClientSession() as session:
        for url in urls:
            task = asyncio.create_task(fetch(session, url))
            tasks.append(task)

        results = await asyncio.gather(*tasks)
        return results

# 运行异步代码
asyncio.run(main())
```

### 内存优化
```python
# 使用生成器处理大数据
def process_large_file(filename):
    with open(filename) as f:
        for line in f:
            yield process_line(line)

# 使用内存视图
import memoryview
data = memoryview(byte_array)
```

## 测试

### 运行测试
```bash
# 使用 pytest
pytest tests/

# 生成覆盖率报告
pytest --cov=src tests/

# 使用 Allure 生成报告
pytest --alluredir=reports tests/
allure serve reports/
```

### 测试配置
```ini
# pytest.ini
[tool:pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = -v --tb=short
```

## 调试和诊断

### 日志配置
```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)
logger.info("This is an info message")
```

### 性能分析
```python
# 使用 cProfile
python -m cProfile -s time myscript.py

# 使用 line_profiler
kernprof -l -v myscript.py
```

## 安全考虑

### 安全更新
定期更新库以修复安全漏洞：
```bash
pip list --outdated
pip install --upgrade <package_name>
```

### 敏感信息处理
- 使用环境变量存储密钥
- 避免硬编码凭证
- 使用 .env 文件管理配置

## 故障排除

### 常见问题

1. **依赖冲突**
   ```bash
   # 检查冲突
   pip check

   # 解决冲突
   pip install --upgrade pip
   pip install --force-reinstall <package>
   ```

2. **安装失败**
   ```bash
   # 清理缓存
   pip cache purge

   # 使用国内镜像
   pip install -i https://pypi.tuna.tsinghua.edu.cn/simple <package>
   ```

3. **导入错误**
   - 检查 Python 路径
   - 验证安装
   - 查看错误详情

## 维护指南

### 添加新库
1. 评估许可证兼容性
2. 创建目录
3. 下载源码
4. 更新 requirements.txt
5. 编写测试
6. 更新文档

### 更新库
1. 检查版本兼容性
2. 测试新版本
3. 更新版本号
4. 运行回归测试
5. 更新变更日志

### 移除库
1. 检查依赖关系
2. 移除代码
3. 更新文档
4. 清理配置

## 资源链接

- [PyPI - Python 包索引](https://pypi.org/)
- [Python 官方文档](https://docs.python.org/)
- [aiohttp 文档](https://aiohttp.readthedocs.io/)
- [boto3 文档](https://boto3.amazonaws.com/documentation/)
- [pytest 文档](https://pytest.org/en/stable/)