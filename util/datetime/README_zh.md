# 日期时间处理库

本模块提供高效的日期时间处理功能，包括时间解析、格式化、时区处理等功能。

## 功能特性

### 时间解析
- 多种时间格式支持
- 高性能解析器
- 错误处理机制
- 自定义格式

### 时间格式化
- 标准格式输出
- 自定义格式模板
- 国际化支持
- 批量格式化

### 时间计算
- 时间差计算
- 时间加减
- 工作日计算
- 时区转换

## 主要组件

### 核心文件
- **base.h/cpp** - 基础时间类和函数
- **parser.h** - 时间解析器
- **parser.rl6** - Ragel 解析器定义
- **cputimer.h/cpp** - CPU 定时器
- **process_uptime.h/cpp** - 进程运行时间

### 常量定义
- **constants.h/cpp** - 时间常量

### 测试和基准
- **base_ut.cpp** - 单元测试
- **parser_ut.cpp** - 解析器测试
- **benchmark/** - 性能基准测试

## 使用方法

### 基础时间操作
```cpp
#include "util/datetime/base.h"

// 获取当前时间
TInstant now = TInstant::Now();

// 创建时间对象
TInstant time = TInstant::Seconds(1609459200);  // 2021-01-01

// 时间转换
ui64 seconds = time.Seconds();
ui64 milliSeconds = time.MilliSeconds();
```

### 时间解析
```cpp
#include "util/datetime/parser.h"

// 解析标准格式
TInstant parsed = ParseIso8601("2021-01-01T00:00:00Z");

// 解析自定义格式
TInstant time2 = ParseHttpDate("Mon, 01 Jan 2021 00:00:00 GMT");

// 解析相对时间
TDuration duration = ParseDuration("1h30m");
```

### 时间格式化
```cpp
// ISO8601 格式
TString iso = InstantToString(now, "UTC");  // 2021-01-01T00:00:00.000000Z

// 自定义格式
TString custom = FormatInstant(now, "%Y-%m-%d %H:%M:%S");

// 人类可读格式
TString human = HumanReadable(now);
```

### 时间计算
```cpp
// 时间差
TDuration diff = now - earlier;

// 时间加减
TInstant later = now + TDuration::Hours(24);
TInstant earlier = now - TDuration::Minutes(30);

// 比较时间
if (now > earlier) {
    // 处理逻辑
}
```

### CPU 定时器
```cpp
#include "util/datetime/cputimer.h"

// 创建 CPU 定时器
TCPUTimer timer;

// 开始计时
timer.Start();

// 执行代码
DoSomeWork();

// 停止计时
timer.Stop();

// 获取 CPU 时间
double cpuSeconds = timer.GetCPUTime();
double wallSeconds = timer.GetWallTime();
```

## 支持的时间格式

### ISO8601 格式
- `2021-01-01T00:00:00Z`
- `2021-01-01T00:00:00+08:00`
- `2021-01-01T00:00:00.123456789Z`

### HTTP 日期格式
- `Mon, 01 Jan 2021 00:00:00 GMT`
- `Monday, 01-Jan-21 00:00:00 GMT`
- `Mon Jan  1 00:00:00 2021`

### 相对时间格式
- `1h30m` - 1小时30分钟
- `2d5s` - 2天5秒
- `500ms` - 500毫秒

## 性能特性

### 解析性能
- ISO8601 解析：~200ns
- HTTP 日期解析：~150ns
- 相对时间解析：~50ns

### 格式化性能
- 标准格式化：~100ns
- 自定义格式化：~200ns
- 批量格式化：~50ns/个

## 时区支持

### 时区列表
```cpp
// 支持的时区
std::vector<TString> zones = GetSupportedTimeZones();
```

### 时区转换
```cpp
// 转换到特定时区
TString localTime = InstantToString(now, "Asia/Shanghai");

// 解析带时区的时间
TInstant time = ParseIso8601("2021-01-01T00:00:00+08:00");
```

## 错误处理

### 异常类型
```cpp
try {
    TInstant time = ParseIso8601("invalid-date");
} catch (const TDateTimeException& e) {
    // 处理解析错误
    std::cerr << "Parse error: " << e.what() << std::endl;
}
```

## 测试

### 单元测试
```bash
# 运行基础测试
./ut/datetime_ut

# 运行解析器测试
./ut/parser_ut

# 运行特定测试
./ut/datetime_ut --gtest_filter="InstantTest.*"
```

### 性能基准测试
```bash
cd util/datetime/benchmark
python run_benchmark.py
```

## 最佳实践

1. **性能优化**
   - 重用时间对象
   - 批量处理时间
   - 使用缓存

2. **时间精度**
   - 注意精度丢失
   - 使用合适的时间单位
   - 避免频繁转换

3. **时区处理**
   - 统一使用 UTC
   - 明确时区转换
   - 处理夏令时

## 配置选项

### 编译时配置
```cpp
// 禁用某些格式
#define Y_DISABLE_DEPRECATED_PARSERS

// 启用调试
#define Y_DATETIME_DEBUG
```

## 依赖项

- 标准 C++ 库
- C++11 或更高版本
- 无外部依赖

## 平台支持

- Linux (x86_64, ARM64)
- macOS (x86_64, ARM64)
- Windows (x86_64)

## 注意事项

1. **时间精度**
   - 不同平台精度可能不同
   - 注意舍入误差

2. **时区数据**
   - 定期更新时区数据
   - 处理时区变更

3. **线程安全**
   - 大部分操作线程安全
   - 注意共享状态

## 版本历史

- v3.0: 添加更多时间格式支持
- v2.5: 性能优化
- v2.0: 重构 API
- v1.0: 初始版本