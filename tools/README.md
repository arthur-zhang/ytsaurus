# YTsaurus 开发工具集 (Development Tools)

## 概述

此目录包含 YTsaurus 项目开发和维护过程中使用的各种工具。这些工具帮助提高开发效率、代码质量，并简化构建和部署流程。

## 工具分类

### 代码质量工具

#### C++ 风格检查器 (cpp_style_checker/)
- **功能** - C++ 代码风格和质量检查
- **特性**：
  - 统一的代码风格检查
  - 自定义规则支持
  - 集成到 CI/CD 流程
  - 自动修复建议

#### Python 代码检查
- **flake8_linter/** - Flake8 Python 代码风格检查
- **black_linter/** - Black Python 代码格式化工具
- **ruff_linter/** - Ruff 快速 Python 代码检查器

### 构建工具

#### Python 编译器
- **py2cc/** - Python 2 到 C++ 转译器
- **py3cc/** - Python 3 到 C++ 转译器
  - 性能优化
  - 代码混淆
  - 部署简化

#### 资源处理工具
- **rescompiler/** - 资源编译器
  - 将资源文件嵌入可执行文件
  - 支持 C/C++ 头文件生成
  - 压缩和优化选项

- **rescompressor/** - 资源压缩器
  - 减少资源文件大小
  - 多种压缩算法支持
  - 批量处理能力

- **rorescompiler/** - 只读资源编译器
  - 创建只读资源段
  - 内存映射支持
  - 运行时优化

### 系统工具

#### 存档工具 (archiver/)
- **功能** - 高效文件存档和压缩
- **支持格式**：
  - 自定义 YTsaurus 格式
  - 标准格式支持（zip, tar, gzip）
  - 增量备份

#### ELF 处理工具 (fix_elf/)
- **功能** - ELF 可执行文件处理
- **特性**：
  - 路径修复
  - RPATH 调整
  - 依赖关系分析
  - 符号表优化

### 测试和分析工具

#### 枚举解析器 (enum_parser/)
- **功能** - 枚举定义解析和代码生成
- **用途**：
  - 自动生成枚举字符串转换
  - 支持 C++/Python/Go
  - JSON/YAML 导出

#### Go 测试挖掘器 (go_test_miner/)
- **功能** - Go 测试用例提取和分析
- **特性**：
  - 自动发现测试
  - 测试覆盖率分析
  - 性能基准提取
  - 依赖关系图

## 主要用途

### 开发流程集成
- **预提交检查** - 确保代码质量
- **CI/CD 集成** - 自动化构建和测试
- **持续监控** - 代码质量跟踪

### 构建优化
- **资源嵌入** - 减少部署文件数量
- **代码转换** - 提高运行时性能
- **二进制优化** - 减小可执行文件大小

### 部署和维护
- **依赖管理** - 自动处理依赖关系
- **配置管理** - 统一配置格式
- **版本控制** - 自动化版本管理

## 使用方法

### 代码质量检查
```bash
# C++ 代码检查
./tools/cpp_style_checker/check.sh src/

# Python 代码格式化
./tools/black_linter/format.sh python/

# Python 代码检查
./tools/ruff_linter/check.sh python/
```

### 资源处理
```bash
# 编译资源
./tools/rescompiler/rescompiler -i resources/ -o resources.cpp

# 压缩资源
./tools/rescompressor/compress.sh input_dir output_dir
```

### 构建辅助
```bash
# 修复 ELF 路径
./tools/fix_elf/fix_binary.sh ./output/bin/

# 解析枚举定义
./tools/enum_parser/parse.py enum_def.yml
```

## 开发指南

### 添加新工具
1. 在 tools/ 下创建目录
2. 编写工具脚本
3. 添加到 CMakeLists.txt
4. 编写使用文档
5. 添加测试用例

### 工具标准
- 提供命令行接口
- 支持批处理模式
- 包含详细错误信息
- 遵循 Unix 哲学

### 维护原则
- 保持工具独立性
- 提供清晰的接口
- 定期更新和优化
- 完善的文档

## 最佳实践

### 工具设计
- **单一职责** - 每个工具专注于一个功能
- **可配置性** - 支持配置文件和命令行参数
- **可扩展性** - 易于添加新功能
- **向后兼容** - 保持接口稳定

### 性能优化
- **并行处理** - 利用多核 CPU
- **内存效率** - 处理大文件
- **缓存机制** - 避免重复计算
- **增量处理** - 只处理变更部分

### 错误处理
- **清晰错误信息** - 便于问题定位
- **恢复机制** - 支持错误恢复
- **日志记录** - 详细操作日志
- **退出码** - 标准退出码约定

## 集成方案

### Git Hooks
```bash
# 预提交钩子
#!/bin/sh
./tools/cpp_style_checker/check.sh
./tools/black_linter/format.sh
```

### CI/CD 流程
```yaml
# GitHub Actions 示例
- name: Code Quality Check
  run: |
    ./tools/cpp_style_checker/check.sh
    ./tools/ruff_linter/check.sh
```

### IDE 集成
- **VS Code** - 通过任务和扩展集成
- **IntelliJ** - 使用外部工具配置
- **Vim/Emacs** - 通过插件或命令集成

## 未来规划

### 工具增强
- 添加更多语言支持
- 提高自动化程度
- 增强 UI 交互
- 云原生支持

### 平台支持
- Windows 原生支持
- macOS 优化
- 容器化部署
- 跨平台兼容性

### 生态集成
- 与主流 IDE 深度集成
- 支持更多版本控制系统
- 云服务集成
- 第三方工具对接