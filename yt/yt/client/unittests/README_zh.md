# Unit Tests - 单元测试

本目录包含 YTsaurus 客户端的单元测试套件，用于验证各个组件的正确性和稳定性。

## 测试覆盖范围

### 主要测试模块
- **Object Client测试**：验证对象操作的正确性
- **Table Client测试**：测试表读写操作
- **Transaction Client测试**：验证事务功能
- **Queue Client测试**：测试消息队列功能
- **Schema测试**：验证Schema兼容性

### 测试类型
- **功能测试**：验证各功能的正确性
- **性能测试**：测试性能指标
- **并发测试**：测试多线程环境下的行为
- **错误处理测试**：验证错误处理的正确性

## 运行测试

```bash
# 运行所有单元测试
./yt/yt/scripts/run_unittests.sh

# 运行特定测试
./path/to/test_binary
```

测试是保证 YTsaurus 质量的重要手段，确保代码修改不会引入回归问题。