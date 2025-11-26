# Testing 测试框架

YTsaurus 综合测试框架，集成了单元测试、集成测试、性能基准测试和模拟测试工具。

## 📋 项目概述

Testing 库为 YTsaurus 提供了完整的测试基础设施，基于 Google Test/GMock 构建，并添加了专门的扩展功能，支持从简单的单元测试到复杂的性能基准测试的各种测试需求。

### 🎯 核心特性

- **单元测试**: 基于 Google Test 的强大单元测试框架
- **模拟测试**: Google Mock 集成，支持接口模拟
- **基准测试**: 内置性能基准测试工具
- **测试扩展**: YTsaurus 特定的测试工具和宏
- **参数化测试**: 支持参数化测试用例
- **测试钩子**: 测试环境初始化和清理
- **Google Benchmark**: 集成 Google Benchmark 框架
- **CI集成**: 与 Arcadia CI 系统深度集成

## 🏗️ 架构设计

### 测试框架结构

```
Testing Framework
├── GTest              # Google Test 集成
│   ├── gtest.h/.cpp          # 核心测试框架
│   ├── matchers.h/.cpp       # 自定义匹配器
│   ├── main.h/.cpp           # 测试主函数
│   ├── friend.h              # 测试友元访问
│   └── ut/                   # 单元测试示例
├── Benchmark           # 性能基准测试
│   ├── bench.h/.cpp           # 基准测试核心
│   ├── main/main.cpp          # 基准测试主程序
│   └── dummy.cpp              # 空实现
├── GBenchmark         # Google Benchmark 集成
│   ├── benchmark.h           # Google Benchmark 封装
│   └── main.cpp              # 主程序
├── Hooks              # 测试钩子
│   ├── hook.h/.cpp            # 测试钩子实现
│   └── yt_initialize_hook.h   # YT 初始化钩子
└── Common             # 通用工具
    ├── env.h                  # 环境变量工具
    └── scope.h                # 作用域工具
```

### 测试类型

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Unit Tests    │    │ Integration     │    │ Performance     │
│                 │    │ Tests           │    │ Benchmarks      │
├─────────────────┤    ├─────────────────┤    ├─────────────────┤
│ • Function      │    │ • Component     │    │ • CPU           │
│ • Class         │    │ • Service       │    │ • Memory        │
│ • Module        │    │ • System        │    │ • I/O           │
└─────────────────┘    └─────────────────┘    └─────────────────┘

┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Mock Tests    │    │ Parameterized   │    │ Property Tests  │
│                 │    │ Tests           │    │                 │
├─────────────────┤    ├─────────────────┤    ├─────────────────┤
│ • Interface     │    │ • Data-driven   │    │ • Fuzzy         │
│ • Dependency    │    │ • Configurable  │    │ • Generative    │
│ • External      │    │ • Matrix        │    │ • Invariant     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 💻 使用方法

### 基础单元测试

```cpp
#include <library/cpp/testing/gtest/gtest.h>

class Calculator {
public:
    int Add(int a, int b) { return a + b; }
    int Subtract(int a, int b) { return a - b; }
    int Multiply(int a, int b) { return a * b; }
    double Divide(int a, int b) {
        if (b == 0) throw std::runtime_error("Division by zero");
        return static_cast<double>(a) / b;
    }
};

// 基础测试用例
TEST(CalculatorTest, BasicOperations) {
    Calculator calc;

    EXPECT_EQ(calc.Add(2, 3), 5);
    EXPECT_EQ(calc.Subtract(5, 3), 2);
    EXPECT_EQ(calc.Multiply(4, 5), 20);
    EXPECT_DOUBLE_EQ(calc.Divide(10, 2), 5.0);
}

// 异常测试
TEST(CalculatorTest, DivisionByZero) {
    Calculator calc;

    EXPECT_THROW(calc.Divide(10, 0), std::runtime_error);
    EXPECT_NO_THROW(calc.Divide(10, 1));
}

// 测试夹具
class CalculatorTest : public ::testing::Test {
protected:
    void SetUp() override {
        calc_ = std::make_unique<Calculator>();
    }

    void TearDown() override {
        calc_.reset();
    }

    std::unique_ptr<Calculator> calc_;
};

TEST_F(CalculatorTest, UsingFixture) {
    ASSERT_NE(calc_, nullptr);

    EXPECT_EQ(calc_->Add(100, 200), 300);
    EXPECT_EQ(calc_->Multiply(6, 7), 42);
}
```

### 参数化测试

```cpp
#include <library/cpp/testing/gtest/gtest.h>

class StringTest : public ::testing::TestWithParam<std::string> {
protected:
    void SetUp() override {
        input_ = GetParam();
    }

    std::string input_;
};

TEST_P(StringTest, LengthCalculation) {
    size_t expectedLength = input_.length();
    EXPECT_EQ(input_.length(), expectedLength);
}

TEST_P(StringTest, EmptyCheck) {
    bool isEmpty = input_.empty();
    EXPECT_EQ(isEmpty, input_.length() == 0);
}

INSTANTIATE_TEST_SUITE_P(
    StringTestInstances,
    StringTest,
    ::testing::Values(
        "",
        "hello",
        "YTsaurus",
        "Very long string with many words",
        "1234567890!@#$%^&*()"
    )
);

// 自定义参数化测试
struct TestParams {
    int a;
    int b;
    int expected;
    bool shouldThrow;
};

class ArithmeticTest : public ::testing::TestWithParam<TestParams> {
};

TEST_P(ArithmeticTest, Addition) {
    auto params = GetParam();
    Calculator calc;

    if (params.shouldThrow) {
        EXPECT_ANY_THROW(calc.Divide(params.a, params.b));
    } else {
        EXPECT_EQ(calc.Add(params.a, params.b), params.expected);
    }
}

INSTANTIATE_TEST_SUITE_P(
    ArithmeticTestInstances,
    ArithmeticTest,
    ::testing::Values(
        TestParams{1, 2, 3, false},
        TestParams{-5, 5, 0, false},
        TestParams{0, 0, 0, false},
        TestParams{10, 0, 0, true}  // Division by zero
    )
);
```

### 模拟测试 (Mock Tests)

```cpp
#include <library/cpp/testing/gtest/gtest.h>
#include <gmock/gmock.h>

// 接口定义
class IDatabase {
public:
    virtual ~IDatabase() = default;
    virtual bool Connect(const std::string& connectionString) = 0;
    virtual int ExecuteQuery(const std::string& query) = 0;
    virtual std::string FetchResult(int resultId) = 0;
    virtual void Disconnect() = 0;
};

// 模拟实现
class MockDatabase : public IDatabase {
public:
    MOCK_METHOD(bool, Connect, (const std::string& connectionString), (override));
    MOCK_METHOD(int, ExecuteQuery, (const std::string& query), (override));
    MOCK_METHOD(std::string, FetchResult, (int resultId), (override));
    MOCK_METHOD(void, Disconnect, (), (override));
};

// 使用模拟的测试
class DataService {
public:
    DataService(IDatabase* db) : db_(db) {}

    std::string GetUser(int userId) {
        if (!db_->Connect("connection_string")) {
            return "Connection failed";
        }

        int resultId = db_->ExecuteQuery("SELECT name FROM users WHERE id = " + std::to_string(userId));
        if (resultId < 0) {
            db_->Disconnect();
            return "Query failed";
        }

        std::string result = db_->FetchResult(resultId);
        db_->Disconnect();
        return result;
    }

private:
    IDatabase* db_;
};

TEST(DataServiceTest, SuccessfulUserRetrieval) {
    // 创建模拟对象
    auto mockDb = std::make_unique<MockDatabase>();

    // 设置期望行为
    EXPECT_CALL(*mockDb, Connect("connection_string"))
        .WillOnce(::testing::Return(true));

    EXPECT_CALL(*mockDb, ExecuteQuery(::testing::_))
        .WillOnce(::testing::Return(123));

    EXPECT_CALL(*mockDb, FetchResult(123))
        .WillOnce(::testing::Return("John Doe"));

    EXPECT_CALL(*mockDb, Disconnect())
        .Times(1);

    // 测试
    DataService service(mockDb.get());
    std::string result = service.GetUser(42);

    EXPECT_EQ(result, "John Doe");
}

TEST(DataServiceTest, ConnectionFailure) {
    auto mockDb = std::make_unique<MockDatabase>();

    EXPECT_CALL(*mockDb, Connect("connection_string"))
        .WillOnce(::testing::Return(false));

    // Connect 失败时不应该调用其他方法
    EXPECT_CALL(*mockDb, ExecuteQuery(::testing::_))
        .Times(0);

    EXPECT_CALL(*mockDb, FetchResult(::testing::_))
        .Times(0);

    EXPECT_CALL(*mockDb, Disconnect())
        .Times(0);

    DataService service(mockDb.get());
    std::string result = service.GetUser(42);

    EXPECT_EQ(result, "Connection failed");
}
```

### 性能基准测试

```cpp
#include <library/cpp/testing/benchmark/bench.h>
#include <library/cpp/testing/gbenchmark/benchmark.h>
#include <algorithm>
#include <vector>

// 使用内置基准测试框架
void SortVectorBenchmark(NBench::NCpu::TParams& params) {
    const size_t size = 10000;
    std::vector<int> data(size);

    // 准备测试数据
    for (size_t i = 0; i < size; ++i) {
        data[i] = size - i;  // 逆序
    }

    // 基准测试代码
    for (size_t i = 0; i < params.Iterations(); ++i) {
        std::vector<int> testData = data;  // 复制数据
        std::sort(testData.begin(), testData.end());

        // 防止编译器优化
        NBench::DoNotOptimize(testData.data());
        NBench::Clobber();
    }
}

// 注册基准测试
NBench::NCpu::TRegistar SortVectorRegistar("SortVector", SortVectorBenchmark);

// 使用 Google Benchmark
static void BM_StringCreation(benchmark::State& state) {
    for (auto _ : state) {
        std::string created_string = "Hello, World!";
        benchmark::DoNotOptimize(created_string);
    }
}
BENCHMARK(BM_StringCreation);

static void BM_StringCopy(benchmark::State& state) {
    std::string x = "Hello, World!";
    for (auto _ : state) {
        std::string copy = x;
        benchmark::DoNotOptimize(copy);
    }
}
BENCHMARK(BM_StringCopy);

// 参数化基准测试
static void BM_VectorPushBack(benchmark::State& state) {
    int n = state.range(0);
    std::vector<int> data;
    data.reserve(n);

    for (auto _ : state) {
        data.clear();
        for (int i = 0; i < n; ++i) {
            data.push_back(i);
        }
        benchmark::DoNotOptimize(data);
    }
}
BENCHMARK(BM_VectorPushBack)->Arg(1000)->Arg(10000)->Arg(100000);

// 自定义基准测试
class PerformanceTest {
public:
    void RunBenchmark() {
        const int iterations = 1000000;

        // 预热
        for (int i = 0; i < 100; ++i) {
            DoWork(i);
        }

        // 测试
        auto start = std::chrono::high_resolution_clock::now();

        for (int i = 0; i < iterations; ++i) {
            DoWork(i);
        }

        auto end = std::chrono::high_resolution_clock::now();
        auto duration = std::chrono::duration_cast<std::chrono::microseconds>(end - start);

        std::cout << "Benchmark completed:" << std::endl;
        std::cout << "Iterations: " << iterations << std::endl;
        std::cout << "Total time: " << duration.count() << " μs" << std::endl;
        std::cout << "Average per iteration: " << duration.count() / iterations << " μs" << std::endl;
    }

private:
    void DoWork(int value) {
        // 模拟一些计算工作
        volatile int result = value * value + 42;
        benchmark::DoNotOptimize(result);
    }
};

TEST(PerformanceTest, CustomBenchmark) {
    PerformanceTest perfTest;
    perfTest.RunBenchmark();
}
```

### 测试环境设置和钩子

```cpp
#include <library/cpp/testing/hook/hook.h>

class TestEnvironment : public ::testing::Environment {
public:
    void SetUp() override {
        // 全局测试环境初始化
        std::cout << "Setting up test environment" << std::endl;

        // 初始化日志系统
        InitLogger();

        // 设置测试数据库
        SetupTestDatabase();

        // 准备测试数据
        PrepareTestData();
    }

    void TearDown() override {
        // 全局测试环境清理
        std::cout << "Tearing down test environment" << std::endl;

        CleanupTestDatabase();
        ShutdownLogger();
    }

private:
    void InitLogger() {
        // 初始化测试日志
    }

    void SetupTestDatabase() {
        // 设置测试数据库
    }

    void PrepareTestData() {
        // 准备测试数据
    }

    void CleanupTestDatabase() {
        // 清理测试数据库
    }

    void ShutdownLogger() {
        // 关闭日志系统
    }
};

// 注册测试环境
TEST(MyTestSuite, SampleTest) {
    EXPECT_EQ(2 + 2, 4);
}

// 测试主函数
int main(int argc, char** argv) {
    // 注册测试环境
    ::testing::AddGlobalTestEnvironment(new TestEnvironment());

    // 初始化 Google Test
    ::testing::InitGoogleTest(&argc, argv);

    // 运行所有测试
    return RUN_ALL_TESTS();
}
```

### 自定义匹配器

```cpp
#include <library/cpp/testing/gtest/matchers.h>

// 自定义匹配器：检查字符串是否为有效的电子邮件
MATCHER_P(IsValidEmail, expectedDomain, "") {
    if (arg.empty()) return false;

    auto atPos = arg.find('@');
    if (atPos == std::string::npos) return false;

    auto domain = arg.substr(atPos + 1);
    return domain == expectedDomain;
}

TEST(EmailValidationTest, CustomMatcher) {
    EXPECT_THAT("john@example.com", IsValidEmail("example.com"));
    EXPECT_THAT("jane@test.org", IsValidEmail("test.org"));
    EXPECT_THAT("invalid-email", Not(IsValidEmail("example.com")));
    EXPECT_THAT("wrong@domain.com", Not(IsValidEmail("example.com")));
}

// 自定义匹配器：检查数值范围
MATCHER(IsInRange, "") {
    return (arg >= 0 && arg <= 100);
}

MATCHER_P(IsInRange, range, "") {
    return (arg >= range.first && arg <= range.second);
}

TEST(RangeTest, CustomRangeMatcher) {
    EXPECT_THAT(50, IsInRange());
    EXPECT_THAT(150, Not(IsInRange()));

    std::pair<int, int> range = {10, 90};
    EXPECT_THAT(50, IsInRange(range));
    EXPECT_THAT(5, Not(IsInRange(range)));
    EXPECT_THAT(95, Not(IsInRange(range)));
}
```

## 🔧 高级特性

### 测试参数化

```cpp
#include <library/cpp/testing/gtest/gtest.h>

// 使用测试参数
TEST(ParametrizedTest, UsingTestParam) {
    // 通过命令行参数获取测试配置
    auto timeout = NGTest::GetTestParam("TIMEOUT");
    auto retryCount = NGTest::GetTestParam("RETRY_COUNT");

    int timeoutMs = timeout ? std::stoi(std::string(timeout.value())) : 5000;
    int retries = retryCount ? std::stoi(std::string(retryCount.value())) : 3;

    std::cout << "Using timeout: " << timeoutMs << "ms" << std::endl;
    std::cout << "Using retry count: " << retries << std::endl;

    // 执行测试
    EXPECT_TRUE(PerformOperationWithRetry(retries, timeoutMs));
}

bool PerformOperationWithRetry(int retries, int timeoutMs) {
    for (int i = 0; i < retries; ++i) {
        if (DoOperation(timeoutMs)) {
            return true;
        }
        std::this_thread::sleep_for(std::chrono::milliseconds(100));
    }
    return false;
}
```

### 测试工具和辅助函数

```cpp
#include <library/cpp/testing/common/scope.h>
#include <library/cpp/testing/common/env.h>

// 作用域工具示例
TEST(ScopeTest, AutoCleanup) {
    bool cleanupCalled = false;

    {
        auto cleanup = MakeGuard([&cleanupCalled]() {
            cleanupCalled = true;
        });

        // 在作用域内执行操作
        EXPECT_FALSE(cleanupCalled);
    } // cleanup 自动调用

    EXPECT_TRUE(cleanupCalled);
}

// 环境变量测试
TEST(EnvironmentTest, TestEnvironmentVariables) {
    // 设置测试环境变量
    SetEnv("TEST_MODE", "UNIT_TEST");

    auto testMode = GetEnv("TEST_MODE");
    ASSERT_TRUE(testMode);
    EXPECT_EQ(*testMode, "UNIT_TEST");

    // 清理
    UnsetEnv("TEST_MODE");
}

// 测试辅助函数
class TestHelper {
public:
    // 创建临时文件
    static std::string CreateTempFile(const std::string& content) {
        std::string tempPath = "/tmp/test_" + std::to_string(std::time(nullptr));
        std::ofstream file(tempPath);
        file << content;
        file.close();
        return tempPath;
    }

    // 比较文件内容
    static bool CompareFiles(const std::string& file1, const std::string& file2) {
        std::ifstream f1(file1);
        std::ifstream f2(file2);

        return std::equal(
            std::istreambuf_iterator<char>(f1),
            std::istreambuf_iterator<char>(),
            std::istreambuf_iterator<char>(f2)
        );
    }

    // 生成随机字符串
    static std::string GenerateRandomString(size_t length) {
        const std::string chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789";
        std::string result;
        result.reserve(length);

        std::random_device rd;
        std::mt19937 gen(rd());
        std::uniform_int_distribution<> dis(0, chars.size() - 1);

        for (size_t i = 0; i < length; ++i) {
            result += chars[dis(gen)];
        }

        return result;
    }
};

TEST(FileOperationsTest, TempFileOperations) {
    // 创建临时文件
    std::string content = "Test content for temporary file";
    std::string tempFile = TestHelper::CreateTempFile(content);

    // 验证文件内容
    std::ifstream file(tempFile);
    std::string readContent((std::istreambuf_iterator<char>(file)),
                           std::istreambuf_iterator<char>());

    EXPECT_EQ(content, readContent);

    // 清理
    std::remove(tempFile.c_str());
}
```

### 异步测试

```cpp
#include <library/cpp/threading/future/future.h>
#include <library/cpp/testing/gtest/gtest.h>

class AsyncTest : public ::testing::Test {
protected:
    void SetUp() override {
        executor_ = NThreading::CreateLocallyExecutor();
    }

    void TearDown() override {
        executor_.reset();
    }

    NThreading::ILocallyExecutorPtr executor_;
};

TEST_F(AsyncTest, FutureOperations) {
    // 创建异步操作
    auto future = NThreading::Async([this]() -> int {
        std::this_thread::sleep_for(std::chrono::milliseconds(100));
        return 42;
    });

    // 等待结果
    int result = future.GetValueSync();
    EXPECT_EQ(result, 42);
}

TEST_F(AsyncTest, MultipleAsyncOperations) {
    std::vector<NThreading::TFuture<int>> futures;

    // 启动多个异步任务
    for (int i = 0; i < 10; ++i) {
        futures.push_back(NThreading::Async([i]() -> int {
            std::this_thread::sleep_for(std::chrono::milliseconds(50 * (i + 1)));
            return i * i;
        }));
    }

    // 等待所有任务完成
    auto allDone = NThreading::WaitAll(futures);
    allDone.WaitSync();

    // 验证结果
    for (int i = 0; i < 10; ++i) {
        int result = futures[i].GetValueSync();
        EXPECT_EQ(result, i * i);
    }
}
```

## 🧪 测试运行和配置

### CMake 配置

```cmake
# CMakeLists.txt
cmake_minimum_required(VERSION 3.22)
project(MyProjectTests)

# 查找依赖
find_package(GTest REQUIRED)
find_package(GMock REQUIRED)
find_package(Threads REQUIRED)

# 包含测试库
include_directories(${CMAKE_SOURCE_DIR}/library/cpp/testing)

# 创建测试可执行文件
add_executable(unit_tests
    test_main.cpp
    calculator_test.cpp
    database_test.cpp
)

# 链接库
target_link_libraries(unit_tests
    GTest::GTest
    GTest::Main
    GMock::GMock
    Threads::Threads
    ${YTSURUS_LIBRARIES}
)

# 启用测试
enable_testing()
add_test(NAME unit_tests COMMAND unit_tests)

# 基准测试
add_executable(benchmark_tests
    benchmark_main.cpp
    performance_bench.cpp
)

target_link_libraries(benchmark_tests
    benchmark::benchmark
    benchmark::benchmark_main
    Threads::Threads
)
```

### 运行测试

```bash
# 运行所有测试
./unit_tests

# 运行特定测试套件
./unit_tests --gtest_filter=CalculatorTest.*

# 运行特定测试
./unit_tests --gtest_filter=CalculatorTest.BasicOperations

# 详细输出
./unit_tests --gtest_print_time=1 --gtest_output=xml:test_results.xml

# 重复测试
./unit_tests --gtest_repeat=5

# 基准测试
./benchmark_tests --benchmark_filter=String.*
```

## 📊 测试覆盖率

### 代码覆盖率配置

```cmake
# 启用代码覆盖率
if(CMAKE_BUILD_TYPE STREQUAL "Debug")
    if(CMAKE_CXX_COMPILER_ID STREQUAL "GNU" OR CMAKE_CXX_COMPILER_ID STREQUAL "Clang")
        target_compile_options(unit_tests PRIVATE --coverage)
        target_link_libraries(unit_tests PRIVATE --coverage)
    endif()
endif()
```

```bash
# 生成覆盖率报告
mkdir -p coverage
lcov --capture --directory . --output-file coverage/coverage.info
lcov --remove coverage/coverage.info '/usr/*' '*/test/*' --output-file coverage/filtered.info
genhtml coverage/filtered.info --output-directory coverage/html

# 查看覆盖率报告
open coverage/html/index.html
```

## 📈 最佳实践

### 测试设计原则

1. **FIRST 原则**：
   - **Fast**: 测试应该快速执行
   - **Independent**: 测试应该独立，不互相依赖
   - **Repeatable**: 测试应该可重复，结果一致
   - **Self-Validating**: 测试应该自动验证结果
   - **Timely**: 测试应该及时编写

2. **测试金字塔**：
   - 大量单元测试（70%）
   - 适量集成测试（20%）
   - 少量端到端测试（10%）

3. **命名规范**：
   - 测试套件：`[ClassName]Test`
   - 测试用例：`[MethodName]_[Scenario]_[ExpectedResult]`
   - 描述性命名，清晰表达测试意图

### 测试组织

```cpp
// 好的测试组织示例
class UserServiceTest : public ::testing::Test {
protected:
    void SetUp() override {
        // 准备测试数据
        userRepo_ = std::make_unique<MockUserRepository>();
        userService_ = std::make_unique<UserService>(userRepo_.get());
    }

    void TearDown() override {
        userService_.reset();
        userRepo_.reset();
    }

    // 测试辅助方法
    User CreateTestUser(int id, const std::string& email) {
        return User{id, "Test User", email};
    }

    std::unique_ptr<MockUserRepository> userRepo_;
    std::unique_ptr<UserService> userService_;
};

TEST_F(UserServiceTest, Create_ValidUser_ReturnsUserId) {
    // Arrange
    User testUser = CreateTestUser(1, "test@example.com");
    EXPECT_CALL(*userRepo_, Save(testUser))
        .WillOnce(::testing::Return(123));

    // Act
    int userId = userService_->Create(testUser);

    // Assert
    EXPECT_EQ(userId, 123);
}
```

### 性能测试最佳实践

```cpp
// 性能测试最佳实践
class PerformanceBenchmark : public ::benchmark::Fixture {
protected:
    void SetUp(const ::benchmark::State& state) override {
        // 准备测试数据
        size_ = state.range(0);
        data_.resize(size_);
        std::iota(data_.begin(), data_.end(), 0);
    }

    std::vector<int> data_;
    size_t size_;
};

BENCHMARK_DEFINE_F(PerformanceBenchmark, Sort)(benchmark::State& state) {
    for (auto _ : state) {
        state.PauseTiming();
        auto testData = data_;  // 复制数据
        state.ResumeTiming();

        std::sort(testData.begin(), testData.end());

        benchmark::DoNotOptimize(testData);
        benchmark::ClobberMemory();
    }

    state.SetBytesProcessed(static_cast<int64_t>(state.iterations()) *
                           size_ * sizeof(int));
}

BENCHMARK_REGISTER_F(PerformanceBenchmark, Sort)
    ->Arg(1000)
    ->Arg(10000)
    ->Arg(100000)
    ->Arg(1000000);
```

## 🔗 相关模块

- **Threading**: 并发测试工具
- **Logger**: 测试日志记录
- **FileSystem**: 文件系统测试工具
- **TimeProvider**: 时间测试工具
- **Memory**: 内存测试工具

Testing 库为 YTsaurus 提供了全面的测试基础设施，支持从简单的单元测试到复杂的性能基准测试，确保代码质量和系统可靠性。框架的设计遵循现代软件测试的最佳实践，为开发者提供了强大而易用的测试工具集。