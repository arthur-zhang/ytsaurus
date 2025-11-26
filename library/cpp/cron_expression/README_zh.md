# Cron Expression Cron 表达式库

## 项目描述

Cron Expression 库是 YTsaurus 中的高性能 Cron 表达式解析和计算库，提供完整的时间调度表达式支持。该库实现了标准的 Cron 表达式语法，并扩展了秒级精度和年字段的支持，能够精确计算给定时间点的下一个或上一个触发时间。

基于 GitHub 上的 supertinycron 项目实现，该库提供了丰富的 Cron 表达式功能，支持各种复杂的时间调度需求，是任务调度、定时器和自动化系统的核心组件。

## 核心特性

### ⏰ 完整的 Cron 支持
- **7 个字段**: 秒、分、时、日、月、周、年
- **灵活语法**: 支持标准 Cron 表达式语法
- **特殊字符**: 支持星号、范围、步长、列表等
- **扩展功能**: 支持 L、W、# 等高级特性

### 🚀 高性能计算
- **精确计算**: 基于时区无关的民用时间计算
- **双向查询**: 支持计算下一个和上一个触发时间
- **高效算法**: 优化的时间计算算法
- **最小开销**: 快速的解析和计算过程

### 🔧 丰富的语法
- **标准语法**: 完全兼容标准 Cron 表达式
- **预定义表达式**: 支持 @yearly、@monthly 等预定义表达式
- **特殊字符**: 支持 L（最后）、W（工作日）、#（第N个）等
- **灵活字段**: 支持可选的秒字段和年字段

### 🌍 国际化支持
- **英文月份**: 支持 JAN-DEC 月份名称
- **英文星期**: 支持 SUN-SAT 星期名称
- **数字表示**: 支纯数字表示法
- **混合使用**: 支持数字和名称混合使用

## 字段定义

### Cron 表达式格式
```
秒 分 时 日 月 周 [年]

字段名称        是否必需    允许值                允许特殊字符
----------     ----------   --------------        --------------------------
秒             否           0-59                  * / , -
分             是           0-59                  * / , -
时             是           0-23                  * / , -
日             是           1-31                  * / , - L W
月             是           1-12 或 JAN-DEC       * / , -
周             是           0-6 或 SUN-SAT       * / , - L #
年             否           1970–2199             * / , -
```

### 特殊字符说明

#### 1. 星号 `*`
- 表示匹配该字段的所有值
- 示例：`*` 在月字段表示每个月

#### 2. 连字符 `-`
- 定义值的范围
- 示例：`2000-2010` 在年字段表示 2000 到 2010 年

#### 3. 斜杠 `/`
- 指定范围内的增量
- 示例：`3-59/15` 在分字段表示从第 3 分钟开始，每 15 分钟执行一次
- 示例：`*/40` 表示分钟值匹配 0 或 40 时执行

#### 4. 逗号 `,`
- 分隔列表中的项目
- 示例：`MON,WED,FRI` 在周字段表示周一、周三、周五

#### 5. 字符 `L`
- 表示"最后"
- 在周字段：`5L` 表示最后一个周五
- 在日字段：表示月的最后一天
- 负数：`L-3` 表示倒数第 3 天

#### 6. 字符 `W`
- 仅用于日字段，表示最近的工作日
- 示例：`15W` 表示最接近 15 日的工作日
- 示例：`LW` 表示月的最后一个工作日

#### 7. 井号 `#`
- 仅用于周字段，表示第几个
- 示例：`6#3` 表示第 3 个周五
- 示例：`6#-1` 等同于 `6L`（最后一个周五）

## 预定义表达式

| 表达式 | 描述 | 等价表达式 |
|--------|------|-----------|
| `@annually` | 每年 1 月 1 日午夜运行一次 | `0 0 0 1 1 *` |
| `@yearly` | 每年 1 月 1 日午夜运行一次 | `0 0 0 1 1 *` |
| `@monthly` | 每月 1 日午夜运行一次 | `0 0 0 1 * *` |
| `@weekly` | 每周日午夜运行一次 | `0 0 0 * * 0` |
| `@daily` | 每天午夜运行一次 | `0 0 0 * * *` |
| `@hourly` | 每小时开始运行一次 | `0 0 * * * *` |
| `@minutely` | 每分钟开始运行一次 | `0 * * * * *` |
| `@secondly` | 每秒运行一次 | `* * * * * * *` |

## 核心接口

### TCronExpression 类
```cpp
#include <library/cpp/cron_expression/cron_expression.h>
#include <library/cpp/timezone_conversion/civil.h>

class TCronExpression {
public:
    // 构造函数
    TCronExpression(const TStringBuf cronUnparsedExpr);
    ~TCronExpression();

    // 计算下一个触发时间
    NDatetime::TCivilSecond CronNext(NDatetime::TCivilSecond date);

    // 计算上一个触发时间
    NDatetime::TCivilSecond CronPrev(NDatetime::TCivilSecond date);

private:
    class TImpl;
    THolder<TImpl> Impl;
};
```

### 使用示例
```cpp
#include <library/cpp/cron_expression/cron_expression.h>

void BasicUsage() {
    // 创建 Cron 表达式
    TCronExpression cron("0 0 12 * * *");  // 每天中午 12 点

    // 计算下一个触发时间
    NDatetime::TCivilSecond now = NDatetime::TCivilSecond::Now();
    NDatetime::TCivilSecond next = cron.CronNext(now);

    Cout << "下次执行时间: " << next << Endl;

    // 计算上一个触发时间
    NDatetime::TCivilSecond prev = cron.CronPrev(now);
    Cout << "上次执行时间: " << prev << Endl;
}
```

## 高级使用示例

### 1. 复杂时间调度
```cpp
void ComplexScheduling() {
    // 每 15 分钟执行，仅在工作日（周一到周五）的 9 点到 17 点之间
    TCronExpression workHoursCron("*/15 9-17 * * MON-FRI");

    // 每月最后一个工作日的下午 5 点
    TCronExpression monthEndCron("0 0 17 LW * ?");

    // 每个季度第一个月的第 1 个周一上午 9 点
    TCronExpression quarterlyCron("0 0 9 1 1,4,7,10 MON#1");

    // 每周五、周日晚上 8 点
    TCronExpression weekendCron("0 0 20 * * FRI,SUN");
}
```

### 2. 特殊日期处理
```cpp
void SpecialDates() {
    // 每月 15 号最接近的工作日
    TCronExpression paydayCron("0 0 9 15W * *");

    // 每月倒数第 3 天
    TCronExpression endOfMonthCron("0 0 23 L-3 * *");

    // 每年 6 月的第 3 个周五
    TCronExpression summerFridayCron("0 0 12 * 6 6#3");

    // 每个工作日的上班时间（9:00 AM）
    TCronExpression workdayStartCron("0 0 9 * * MON-FRI");
}
```

### 3. 频繁任务调度
```cpp
void FrequentTasks() {
    // 每 30 秒执行一次
    TCronExpression halfMinute("*/30 * * * * *");

    // 每 5 分钟执行一次
    TCronExpression fiveMinute("0 */5 * * * *");

    // 每 2 小时执行一次
    TCronExpression twoHour("0 0 */2 * * *");

    // 每秒执行一次（慎用！）
    TCronExpression everySecond("* * * * * * *");
}
```

### 4. 定时任务管理器
```cpp
class ScheduledTaskManager {
private:
    struct Task {
        TString name;
        TCronExpression cron;
        std::function<void()> callback;
        NDatetime::TCivilSecond nextRun;
    };

    TVector<Task> tasks_;

public:
    void AddTask(const TString& name, const TString& cronExpr,
                 std::function<void()> callback) {
        Task task;
        task.name = name;
        task.cron = TCronExpression(cronExpr);
        task.callback = callback;
        task.nextRun = task.cron.CronNext(NDatetime::TCivilSecond::Now());

        tasks_.push_back(task);
    }

    void ProcessDueTasks() {
        NDatetime::TCivilSecond now = NDatetime::TCivilSecond::Now();

        for (auto& task : tasks_) {
            if (now >= task.nextRun) {
                try {
                    Cout << "执行任务: " << task.name << Endl;
                    task.callback();
                } catch (const std::exception& e) {
                    Cerr << "任务执行失败: " << task.name << " - " << e.what() << Endl;
                }

                // 计算下次执行时间
                task.nextRun = task.cron.CronNext(now);
            }
        }
    }

    void PrintNextRuns() const {
        Cout << "=== 任务调度表 ===" << Endl;
        for (const auto& task : tasks_) {
            Cout << task.name << ": " << task.nextRun << Endl;
        }
    }
};
```

### 5. 时间窗口验证
```cpp
class TimeWindowValidator {
private:
    TCronExpression cron_;

public:
    TimeWindowValidator(const TString& cronExpr)
        : cron_(cronExpr) {}

    bool IsValidTime(NDatetime::TCivilSecond time) const {
        // 检查给定时间是否在调度窗口内
        NDatetime::TCivilSecond prev = cron_.CronPrev(time);
        NDatetime::TCivilSecond next = cron_.CronNext(prev);

        return time == next;
    }

    TVector<NDatetime::TCivilSecond> GetNextRuns(
        NDatetime::TCivilSecond start,
        size_t count) const {
        TVector<NDatetime::TCivilSecond> runs;
        NDatetime::TCivilSecond current = start;

        for (size_t i = 0; i < count; ++i) {
            current = cron_.CronNext(current);
            runs.push_back(current);
        }

        return runs;
    }

    bool IsWithinBusinessHours(NDatetime::TCivilSecond time) const {
        // 检查是否在工作时间内（9:00-17:00，周一到周五）
        TCronExpression businessHours("0 0 9-17 * * MON-FRI");
        TCronExpression afterHours("0 0 18-23,0-8 * * SAT,SUN");

        NDatetime::TCivilSecond prev = businessHours.CronPrev(time);
        NDatetime::TCivilSecond next = businessHours.CronNext(prev);

        return time == next;
    }
};
```

### 6. 配置驱动的调度
```cpp
class ConfigurableScheduler {
private:
    struct ScheduleConfig {
        TString name;
        TString cron;
        TString description;
    };

    TVector<ScheduleConfig> configs_;

public:
    void LoadConfig(const TString& configFile) {
        // 从配置文件加载调度配置
        // 配置格式：
        // task_name = "0 0 12 * * *" # 每天中午
        // backup_task = "0 0 2 1 * *" # 每月1号凌晨2点
    }

    void CreateScheduleManager() {
        ScheduledTaskManager manager;

        for (const auto& config : configs_) {
            auto callback = [config]() {
                Cout << "执行配置任务: " << config.name << Endl;
                Cout << "描述: " << config.description << Endl;
                // 执行具体任务逻辑
            };

            manager.AddTask(config.name, config.cron, callback);
        }

        manager.PrintNextRuns();
    }
};
```

## 性能特性

### 计算效率
- **时间复杂度**: O(1) 对于大部分常见表达式
- **空间复杂度**: O(1) 常数空间复杂度
- **解析开销**: 一次性解析，后续查询零开销
- **内存使用**: 最小化内存分配

### 准确性保证
- **时区处理**: 使用民用时间，避免时区问题
- **边界情况**: 正确处理月边界、闰年等
- **特殊日期**: 准确处理最后一个周五等工作日概念
- **精度保证**: 秒级精度的时间计算

## 最佳实践

### 1. 表达式设计原则
```cpp
// 好的表达式设计
class CronExpressionDesigner {
public:
    // 使用明确的表达式避免歧义
    static TString EveryHourOnTheHour() {
        return "0 0 * * * *";  // 清晰明确
        // 而不是 "* 0 * * * *"  // 可能混淆
    }

    // 为工作负载选择合适的频率
    static TString DatabaseBackup() {
        return "0 0 2 * * *";  // 每天凌晨2点，低负载时段
    }

    // 避免过于频繁的调度
    static TString HealthCheck() {
        return "0 */5 * * * *";  // 每5分钟检查，而不是每秒
    }

    // 使用预定义表达式提高可读性
    static TString DailyReport() {
        return "@daily";  // 比 "0 0 0 * * *" 更清晰
    }
};
```

### 2. 错误处理和验证
```cpp
class SafeCronScheduler {
private:
    TCronExpression cron_;
    mutable std::mutex mutex_;

public:
    SafeCronScheduler(const TString& expr)
        : cron_(expr) {}

    bool TryGetNextTime(NDatetime::TCivilSecond current,
                       NDatetime::TCivilSecond& result) const {
        try {
            std::lock_guard<std::mutex> lock(mutex_);
            result = cron_.CronNext(current);
            return true;
        } catch (const std::exception& e) {
            Cerr << "计算下一个执行时间失败: " << e.what() << Endl;
            return false;
        }
    }

    void ValidateExpression(const TString& expr) const {
        try {
            TCronExpression test(expr);
            // 测试几个时间点确保表达式有效
            NDatetime::TCivilSecond now = NDatetime::TCivilSecond::Now();
            test.CronNext(now);
            test.CronPrev(now);
        } catch (const std::exception& e) {
            throw std::runtime_error("无效的 Cron 表达式: " + expr + " - " + e.what());
        }
    }
};
```

### 3. 性能优化
```cpp
class OptimizedScheduler {
private:
    struct CachedCron {
        TCronExpression cron;
        mutable NDatetime::TCivilSecond lastQuery;
        mutable NDatetime::TCivilSecond lastResult;
        mutable bool cacheValid = false;
    };

    THashMap<TString, CachedCron> cache_;

public:
    NDatetime::TCivilSecond GetNextTime(const TString& cronExpr,
                                       NDatetime::TCivilSecond current) {
        auto& cached = cache_[cronExpr];

        if (!cached.cacheValid || current > cached.lastQuery) {
            cached.lastResult = cached.cron.CronNext(current);
            cached.lastQuery = current;
            cached.cacheValid = true;
        }

        return cached.lastResult;
    }

    void ClearCache() {
        for (auto& [key, cached] : cache_) {
            cached.cacheValid = false;
        }
    }
};
```

## 常见用例

### 1. 数据处理管道
```cpp
// ETL 任务调度
class ETPipelineScheduler {
public:
    void SetupSchedule() {
        // 每小时增量数据抽取
        scheduleManager_.AddTask("incremental_extract",
            "0 0 * * * *",
            []() { ExtractIncrementalData(); });

        // 每天凌晨全量数据清洗
        scheduleManager_.AddTask("full_clean",
            "@daily",
            []() { CleanData(); });

        // 每周数据归档
        scheduleManager_.AddTask("archive_data",
            "0 0 3 * * 0",  // 周日凌晨3点
            []() { ArchiveData(); });
    }
};
```

### 2. 系统维护任务
```cpp
class MaintenanceScheduler {
public:
    void SetupMaintenanceTasks() {
        // 每日健康检查
        scheduleManager_.AddTask("health_check",
            "*/30 * * * * *",  // 每30秒
            []() { RunHealthCheck(); });

        // 每月日志轮转
        scheduleManager_.AddTask("log_rotation",
            "0 0 1 * * *",    // 每月1号凌晨
            []() { RotateLogs(); });

        // 每季度系统优化
        scheduleManager_.AddTask("system_optimization",
            "0 0 2 1 1,4,7,10 *",  // 每季度第一天凌晨2点
            []() { OptimizeSystem(); });
    }
};
```

## 测试和调试

### 表达式验证
```cpp
void TestCronExpressions() {
    struct TestCase {
        TString expression;
        TString input;
        TString expected;
    };

    TVector<TestCase> testCases = {
        {"*/15 * 1-4 * * *", "2012-07-01_09:53:50", "2012-07-02_01:00:00"},
        {"0 */2 1-4 * * *", "2012-07-01_09:00:00", "2012-07-02_01:00:00"},
        {"0 0 7 ? * MON-FRI", "2009-09-26_00:42:55", "2009-09-28_07:00:00"},
        {"0 */40 * * * *", "2004-09-01_23:46:00", "2004-09-02_00:00:00"},
        {"0 30 23 30 1/3 ?", "2011-04-30_23:30:00", "2011-07-30_23:30:00"}
    };

    for (const auto& test : testCases) {
        TCronExpression cron(test.expression);
        NDatetime::TCivilSecond input = ParseCivilTime(test.input);
        NDatetime::TCivilSecond result = cron.CronNext(input);
        NDatetime::TCivilSecond expected = ParseCivilTime(test.expected);

        if (result == expected) {
            Cout << "✓ " << test.expression << " 通过" << Endl;
        } else {
            Cout << "✗ " << test.expression << " 失败" << Endl;
            Cout << "  期望: " << expected << Endl;
            Cout << "  实际: " << result << Endl;
        }
    }
}
```

## 限制和注意事项

### 功能限制
- **年字段范围**: 限制在 1970-2199 年
- **时区处理**: 使用民用时间，需要外部时区转换
- **性能考虑**: 极其频繁的表达式可能影响性能

### 使用建议
- **合理频率**: 避免过于频繁的调度（如每秒）
- **表达式测试**: 在生产环境前充分测试表达式
- **错误处理**: 实现适当的错误处理机制
- **资源管理**: 监控调度任务的资源使用

## 总结

Cron Expression 库为 YTsaurus 系统提供了强大而灵活的时间调度功能。通过完整的 Cron 表达式支持和高效的计算算法，该库能够满足各种复杂的定时任务需求。

无论是简单的每日任务，还是复杂的基于工作日的调度，该库都能提供准确、可靠的解决方案。其清晰的接口设计和丰富的功能特性，使其成为构建任务调度系统、定时器和自动化工具的理想选择。