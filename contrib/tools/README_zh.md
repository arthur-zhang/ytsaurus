# 开发工具集合

本目录包含 YTsaurus 项目使用的各种开发工具和实用程序，这些工具帮助自动化开发流程、提高开发效率。

## 工具类别

### 代码生成工具
- **protobuf-compiler** - Protocol Buffers 编译器
- **grpc-compiler** - gRPC 代码生成器
- **thrift-compiler** - Thrift 编译器
- **antlr-compiler** - ANTLR 解析器生成器

### 构建工具
- **cmake-tools** - CMake 辅助工具
- **makefile-generator** - Makefile 生成器
- **dependency-analyzer** - 依赖关系分析器

### 测试工具
- **coverage-tools** - 代码覆盖率工具
- **benchmark-runner** - 性能测试运行器
- **fuzzer** - 模糊测试工具
- **mock-generator** - Mock 代码生成器

### 格式化和检查工具
- **code-formatter** - 代码格式化工具
- **linter** - 代码风格检查器
- **static-analyzer** - 静态代码分析器

### 文档工具
- **doc-generator** - 文档生成器
- **api-doc-extractor** - API 文档提取器
- **changelog-generator** - 变更日志生成器

## 主要工具介绍

### Protocol Buffers 工具
```bash
# 生成 Python 代码
protoc --python_out=. file.proto

# 生成 C++ 代码
protoc --cpp_out=. file.proto

# 生成 gRPC 服务代码
protoc --grpc_out=. file.proto
```

### 代码格式化工具
```bash
# 格式化 C++ 代码
./tools/code-formatter --language cpp --file src/file.cpp

# 格式化 Python 代码
./tools/code-formatter --language python --file src/file.py
```

### 依赖分析器
```bash
# 分析模块依赖
./tools/dependency-analyzer --input src/ --output deps.json

# 生成依赖图
./tools/dependency-analyzer --graphviz --output deps.dot
```

### 测试覆盖率工具
```bash
# 运行覆盖率分析
./tools/coverage-tools --source src/ --test tests/

# 生成 HTML 报告
./tools/coverage-tools --html --output coverage.html
```

## 使用方法

### 工具链集成
```cmake
# CMakeLists.txt
find_program(PROTOC protoc)
find_program(CODE_FORMATTER code-formatter)

# 自定义目标
add_custom_target(format_code
    COMMAND ${CODE_FORMATTER} --language cpp ${CMAKE_CURRENT_SOURCE_DIR}
    COMMENT "Formatting code"
)
```

### 开发脚本
```bash
#!/bin/bash
# 开发环境设置脚本

# 设置路径
export PATH=$PATH:$(pwd)/contrib/tools/bin

# 代码格式化
format_all() {
    find src -name "*.cpp" -o -name "*.h" | xargs code-formatter
    find src -name "*.py" | xargs code-formatter
}

# 运行所有检查
run_checks() {
    static-analyzer src/
    linter src/
    coverage-tools --source src/ --test tests/
}
```

## 配置文件

### 工具配置
```json
{
    "formatters": {
        "cpp": {
            "style": "google",
            "indent_size": 4
        },
        "python": {
            "style": "pep8",
            "line_length": 88
        }
    },
    "linters": {
        "cpp": ["clang-tidy", "cpplint"],
        "python": ["pylint", "flake8"]
    }
}
```

## 性能优化

### 并行处理
```python
# 多进程格式化
import multiprocessing

def format_file(filepath):
    # 格式化单个文件
    pass

if __name__ == "__main__":
    files = get_source_files()
    with multiprocessing.Pool() as pool:
        pool.map(format_file, files)
```

### 增量处理
```bash
# 只处理修改的文件
git diff --name-only HEAD~1 | xargs code-formatter
```

## 自定义工具开发

### 工具模板
```python
#!/usr/bin/env python3
"""
自定义工具模板
"""

import argparse
import sys

def main():
    parser = argparse.ArgumentParser(description='自定义工具')
    parser.add_argument('--input', required=True, help='输入文件')
    parser.add_argument('--output', help='输出文件')

    args = parser.parse_args()

    # 处理逻辑
    process(args.input, args.output)

def process(input_file, output_file):
    # 实现处理逻辑
    pass

if __name__ == '__main__':
    main()
```

## 集成到 CI/CD

### GitHub Actions 示例
```yaml
- name: Run tools
  run: |
    # 格式化检查
    contrib/tools/bin/code-formatter --check src/

    # 静态分析
    contrib/tools/bin/static-analyzer src/

    # 生成文档
    contrib/tools/bin/doc-generator src/ --output docs/
```

## 维护指南

### 添加新工具
1. 创建工具目录
2. 编写工具代码
3. 添加构建脚本
4. 更新文档
5. 添加测试

### 工具更新
1. 检查上游更新
2. 测试新版本
3. 更新构建配置
4. 更新文档

## 故障排除

### 常见问题
1. **工具找不到**
   - 检查 PATH 设置
   - 验证安装路径

2. **权限问题**
   - 设置执行权限
   - 检查文件所有者

3. **版本不匹配**
   - 检查工具版本
   - 更新到兼容版本

## 最佳实践

1. **工具版本管理**
   - 锁定工具版本
   - 定期更新
   - 版本兼容性测试

2. **工具配置**
   - 使用配置文件
   - 环境变量管理
   - 默认值设置

3. **性能优化**
   - 并行处理
   - 增量更新
   - 缓存机制

## 资源链接

- [Clang 工具文档](https://clang.llvm.org/docs/)
- [Google 代码风格指南](https://google.github.io/styleguide/)
- [Python 工具生态](https://docs.python-guide.org/)