# Master 组件单元测试

## 概述

本目录包含了 YTsaurus Master 组件的单元测试套件。这些测试确保了 Master 服务各个组件的正确性和稳定性，涵盖了从基础对象管理到复杂事务处理的所有核心功能。

## 测试覆盖范围

### 核心组件测试
- **Cell Master 测试**: Master Cell 的功能测试
- **Cell Server 测试**: Tablet Cell 管理测试
- **Chunk Server 测试**: 数据块管理测试
- **Cypress Server 测试**: 命名空间测试
- **Transaction Server 测试**: 事务处理测试

### 功能模块测试
- **Object Server 测试**: 对象管理测试
- **Security Server 测试**: 安全和权限测试
- **Table Server 测试**: 表管理测试
- **Tablet Server 测试**: Tablet 管理测试
- **Hive 测试**: 集群协调测试

### 集成测试
- **多组件协作测试**: 测试组件间的交互
- **事务一致性测试**: 验证事务一致性
- **故障恢复测试**: 测试故障场景恢复
- **性能压力测试**: 验证系统性能

## 运行测试

### 运行所有单元测试
```bash
# 在构建目录下运行
./yt/yt/server/master/unittests/run_all_tests.sh
```

### 运行特定测试
```bash
# 运行 Cell Master 测试
./yt/yt/server/master/unittests/cell_master_tests

# 运行 Cypress 测试
./yt/yt/server/master/unittests/cypress_server_tests
```

### 运行测试套件
```bash
# 运行基础组件测试
./yt/yt/server/master/unittests/basic_tests --gtest_filter="Basic*"

# 运行事务测试
./yt/yt/server/master/unittests/transaction_tests --gtest_filter="Transaction*"
```

## 测试框架

使用的测试框架：
- **Google Test**: C++ 单元测试框架
- **Google Mock**: C++ Mock 对象框架
- **YT Test Utilities**: YTsaurus 测试工具库

## 测试配置

测试可以通过环境变量配置：

```bash
# 设置测试数据目录
export YT_TEST_DATA_DIR=/tmp/yt_test

# 设置测试超时
export YT_TEST_TIMEOUT=300s

# 启用详细输出
export YT_TEST_VERBOSE=1
```

## 测试数据

测试使用的数据位于 `test_data/` 目录：
- `schemas/`: 测试用的 Schema 定义
- `configs/`: 测试配置文件
- `mock_data/`: Mock 数据文件

## 调试测试

### 调试失败测试
```bash
# 使用 gdb 调试
gdb --args ./unittests/cell_master_tests --gtest_filter="FailedTest"

# 输出详细日志
./unittests/cypress_tests --gtest_filter="FailingTest" --gtest_output=xml
```

### 内存泄漏检测
```bash
# 使用 Valgrind 检测内存泄漏
valgrind --leak-check=full ./unittests/object_server_tests
```

## 贡献指南

添加新测试时：
1. 测试文件命名：`<component>_tests.cpp`
2. 测试类命名：`T<Component>Test`
3. 测试方法命名：`Test<Functionality>_<Scenario>`

示例：
```cpp
class TCellManagerTest : public ::testing::Test {
protected:
    void SetUp() override {
        // 初始化测试环境
    }
};

TEST_F(TCellManagerTest, TestCreateCell_ValidInput_Success) {
    // 测试用例实现
}
```

## 持续集成

这些测试是 CI/CD 流水线的一部分，每次代码提交都会运行：
- 在 Pull Request 创建时自动运行
- 每日自动运行完整测试套件
- 性能回归测试定期运行

## 相关文档
- [测试指南](../../../docs/testing-guide.md)
- [贡献指南](../../../docs/contributing.md)
- [调试指南](../../../docs/debugging.md)