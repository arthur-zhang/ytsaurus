# YTsaurus Job Proxy Client 模块

## 概述

Job Proxy Client 模块定义了 YTsaurus 作业代理相关的错误代码和异常类型。该模块作为客户端库的一部分，提供了作业执行过程中可能遇到的各种错误条件的标准化分类和处理机制。

## 核心功能

### 1. 错误分类
提供了完整的作业执行错误分类系统，涵盖资源限制、执行失败、中断处理等各类异常情况。

### 2. 错误代码标准化
使用标准化的错误代码体系，便于客户端进行统一的错误处理和恢复策略。

## 错误代码定义

```cpp
YT_DEFINE_ERROR_ENUM(
    ((MemoryLimitExceeded)       (1200))  // 内存限制超出
    ((MemoryCheckFailed)         (1201))  // 内存检查失败
    ((JobTimeLimitExceeded)      (1202))  // 作业时间限制超出
    ((UnsupportedJobType)        (1203))  // 不支持的作业类型
    ((JobNotPrepared)            (1204))  // 作业未准备好
    ((UserJobFailed)             (1205))  // 用户作业失败
    ((UserJobProducedCoreFiles)  (1206))  // 用户作业产生核心转储文件
    ((ShallowMergeFailed)        (1207))  // 浅合并失败
    ((JobNotRunning)             (1208))  // 作业未运行
    ((InterruptionUnsupported)   (1209))  // 不支持中断
    ((InterruptionTimeout)       (1210))  // 中断超时
    ((UserJobPortoApiError)      (1211))  // 用户作业 Porto API 错误
    ((InterruptionFailed)        (1212))  // 中断失败
);
```

## 错误详解

### 1. 资源限制错误

#### MemoryLimitExceeded (1200) - 内存限制超出
- **触发条件**: 作业使用的内存超过了分配的限制
- **常见原因**:
  - 数据处理量超出预期
  - 内存泄漏
  - 算法效率低下
- **处理策略**:
  - 增加内存配额
  - 优化算法减少内存使用
  - 使用分区处理减少单次内存使用

#### MemoryCheckFailed (1201) - 内存检查失败
- **触发条件**: 系统无法准确检查或监控内存使用
- **常见原因**:
  - 系统资源不足
  - 权限问题
  - 监控系统故障
- **处理策略**:
  - 检查系统资源状态
  - 验证权限配置
  - 重启监控服务

#### JobTimeLimitExceeded (1202) - 作业时间限制超出
- **触发条件**: 作业执行时间超过了设定的最大时限
- **常见原因**:
  - 数据量过大
  - 算法复杂度过高
  - 系统性能问题
- **处理策略**:
  - 延长作业时间限制
  - 优化算法性能
  - 使用增量处理

### 2. 作业配置错误

#### UnsupportedJobType (1203) - 不支持的作业类型
- **触发条件**: 尝试执行系统不支持的作业类型
- **常见原因**:
  - 客户端版本过旧
  - 配置错误
  - 系统组件缺失
- **处理策略**:
  - 更新客户端版本
  - 检查作业配置
  - 安装必要的系统组件

#### JobNotPrepared (1204) - 作业未准备好
- **触发条件**: 作业在执行前未完成必要的准备工作
- **常见原因**:
  - 依赖资源未就绪
  - 初始化失败
  - 配置验证失败
- **处理策略**:
  - 检查依赖资源状态
  - 验证初始化过程
  - 重新准备作业

#### JobNotRunning (1208) - 作业未运行
- **触发条件**: 尝试对未在运行状态的作业执行操作
- **常见原因**:
  - 作业已完成或失败
  - 作业被中止
  - 状态同步问题
- **处理策略**:
  - 检查作业当前状态
  - 重新提交作业
  - 处理状态同步问题

### 3. 执行失败错误

#### UserJobFailed (1205) - 用户作业失败
- **触发条件**: 用户代码执行过程中发生错误
- **常见原因**:
  - 代码逻辑错误
  - 数据格式问题
  - 外部依赖失败
- **处理策略**:
  - 检查用户代码逻辑
  - 验证输入数据格式
  - 确保外部依赖可用

#### UserJobProducedCoreFiles (1206) - 用户作业产生核心转储文件
- **触发条件**: 用户作业崩溃并产生了核心转储文件
- **常见原因**:
  - 段错误或其他严重错误
  - 内存访问违规
  - 系统调用失败
- **处理策略**:
  - 分析核心转储文件
  - 调试用户代码
  - 修复程序错误

#### UserJobPortoApiError (1211) - 用户作业 Porto API 错误
- **触发条件**: 用户作业使用 Porto 容器管理 API 时发生错误
- **常见原因**:
  - API 调用参数错误
  - 权限不足
  - 系统资源不足
- **处理策略**:
  - 检查 API 调用参数
  - 验证权限配置
  - 确保系统资源充足

#### ShallowMergeFailed (1207) - 浅合并失败
- **触发条件**: 浅合并操作执行失败
- **常见原因**:
  - 数据格式不兼容
  - 内存不足
  - I/O 错误
- **处理策略**:
  - 检查数据格式兼容性
  - 增加内存配额
  - 检查存储系统状态

### 4. 中断处理错误

#### InterruptionUnsupported (1209) - 不支持中断
- **触发条件**: 尝试中断不支持中断操作的作业
- **常见原因**:
  - 作业类型不支持中断
  - 系统版本不支持
  - 配置禁用了中断功能
- **处理策略**:
  - 检查作业类型中断支持
  - 更新系统版本
  - 修改配置启用中断

#### InterruptionTimeout (1210) - 中断超时
- **触发条件**: 作业中断操作超时
- **常见原因**:
  - 作业无法正常响应中断
  - 系统负载过高
  - 网络问题
- **处理策略**:
  - 强制终止作业
  - 检查系统负载
  - 诊断网络问题

#### InterruptionFailed (1212) - 中断失败
- **触发条件**: 作业中断操作完全失败
- **常见原因**:
  - 作业已无法控制
  - 系统故障
  - 权限不足
- **处理策略**:
  - 强制清理作业资源
  - 诊断系统故障
  - 检查权限配置

## 使用方法

### 1. 基本错误处理

```cpp
#include <yt/yt/client/job_proxy/public.h>

using namespace NYT::NJobProxy;

try {
    // 执行作业相关操作
    ExecuteJobOperation();
} catch (const TErrorException& e) {
    switch (e.GetErrorCode()) {
        case NYT::TErrorCode(1200): // MemoryLimitExceeded
            HandleMemoryLimitExceeded(e);
            break;

        case NYT::TErrorCode(1202): // JobTimeLimitExceeded
            HandleJobTimeLimitExceeded(e);
            break;

        case NYT::TErrorCode(1205): // UserJobFailed
            HandleUserJobFailed(e);
            break;

        default:
            HandleGenericJobError(e);
            break;
    }
}
```

### 2. 错误分类处理

```cpp
// 按错误类型分类处理
class JobErrorHandler {
public:
    void HandleError(const TError& error) {
        if (IsResourceError(error)) {
            HandleResourceError(error);
        } else if (IsExecutionError(error)) {
            HandleExecutionError(error);
        } else if (IsInterruptionError(error)) {
            HandleInterruptionError(error);
        } else {
            HandleUnknownError(error);
        }
    }

private:
    bool IsResourceError(const TError& error) {
        return error.GetErrorCode() == 1200 || // MemoryLimitExceeded
               error.GetErrorCode() == 1201 || // MemoryCheckFailed
               error.GetErrorCode() == 1202;   // JobTimeLimitExceeded
    }

    bool IsExecutionError(const TError& error) {
        return error.GetErrorCode() == 1203 || // UnsupportedJobType
               error.GetErrorCode() == 1204 || // JobNotPrepared
               error.GetErrorCode() == 1205 || // UserJobFailed
               error.GetErrorCode() == 1206 || // UserJobProducedCoreFiles
               error.GetErrorCode() == 1207;   // ShallowMergeFailed
    }

    bool IsInterruptionError(const TError& error) {
        return error.GetErrorCode() == 1209 || // InterruptionUnsupported
               error.GetErrorCode() == 1210 || // InterruptionTimeout
               error.GetErrorCode() == 1211;   // InterruptionFailed
    }
};
```

### 3. 重试策略

```cpp
// 基于错误类型的智能重试策略
class JobRetryStrategy {
public:
    bool ShouldRetry(const TError& error, int attemptCount) {
        if (attemptCount >= MaxRetries) {
            return false;
        }

        return IsRetriableError(error) &&
               CanRetryWithBackoff(attemptCount);
    }

private:
    bool IsRetriableError(const TError& error) {
        // 某些错误可重试，某些不可重试
        switch (error.GetErrorCode()) {
            // 可重试的错误
            case 1201: // MemoryCheckFailed
            case 1210: // InterruptionTimeout
                return true;

            // 不可重试的错误
            case 1200: // MemoryLimitExceeded
            case 1203: // UnsupportedJobType
            case 1206: // UserJobProducedCoreFiles
                return false;

            default:
                return false;
        }
    }

    bool CanRetryWithBackoff(int attemptCount) {
        // 指数退避策略
        auto delay = TDuration::MilliSeconds(100 * (1 << attemptCount));
        return delay < MaxRetryDelay;
    }
};
```

## 最佳实践

### 1. 错误预防

```cpp
// 作业执行前的预防性检查
class JobPreExecutionChecker {
public:
    TErrorOr<void> ValidateJob(const TJobSpec& jobSpec) {
        // 检查内存需求
        if (jobSpec.MemoryLimit > SystemAvailableMemory) {
            return TError(NYT::TErrorCode(1200)) // MemoryLimitExceeded
                << "Job requires more memory than available";
        }

        // 检查作业类型支持
        if (!IsJobTypeSupported(jobSpec.Type)) {
            return TError(NYT::TErrorCode(1203)) // UnsupportedJobType
                << "Job type not supported: " << jobSpec.Type;
        }

        // 检查依赖资源
        auto dependencyCheck = CheckDependencies(jobSpec);
        if (!dependencyCheck.IsOK()) {
            return TError(NYT::TErrorCode(1204)) // JobNotPrepared
                << "Job dependencies not ready";
        }

        return TError();
    }
};
```

### 2. 监控和告警

```cpp
// 作业错误监控
class JobErrorMonitor {
private:
    std::unordered_map<int, std::atomic<i64>> errorCounts_;
    std::unordered_map<int, TInstant> lastErrorTime_;

public:
    void RecordError(int errorCode, const TError& error) {
        errorCounts_[errorCode]++;
        lastErrorTime_[errorCode] = TInstant::Now();

        // 高频错误告警
        if (ShouldTriggerAlert(errorCode)) {
            TriggerErrorAlert(errorCode, error);
        }
    }

private:
    bool ShouldTriggerAlert(int errorCode) {
        auto count = errorCounts_[errorCode].load();
        auto now = TInstant::Now();
        auto lastTime = lastErrorTime_[errorCode];

        // 5分钟内同一错误超过10次则告警
        return count > 10 && (now - lastTime) < TDuration::Minutes(5);
    }
};
```

## 扩展性

### 1. 自定义错误处理

```cpp
// 可扩展的错误处理器接口
class IJobErrorHandler {
public:
    virtual bool CanHandle(const TError& error) = 0;
    virtual TErrorOr<void> Handle(const TError& error) = 0;
};

// 实现自定义处理器
class CustomMemoryErrorHandler : public IJobErrorHandler {
public:
    bool CanHandle(const TError& error) override {
        return error.GetErrorCode() == 1200; // MemoryLimitExceeded
    }

    TErrorOr<void> Handle(const TError& error) override {
        // 自定义内存溢出处理逻辑
        return TryOptimizeMemoryUsage();
    }
};
```

## 依赖项

### 内部依赖
- `yt/yt/core/misc/public.h` - 核心公共定义

### 外部依赖
- 标准库 C++ 运行时
- 系统级错误处理机制

## 版本兼容性

- **错误代码稳定性**: 错误代码保持向后兼容
- **扩展性**: 新错误代码添加不影响现有代码

## 相关模块

- **Job Tracker Client**: 作业跟踪和管理
- **Scheduler Client**: 作业调度
- **Node Tracker Client**: 节点管理

## 参考文档

- [YTsaurus 作业执行系统](../../../docs/job-execution.md)
- [错误处理最佳实践](../../../docs/error-handling.md)
- [资源管理指南](../../../docs/resource-management.md)
- [作业调试指南](../../../docs/job-debugging.md)

## 贡献指南

在修改此模块时：
1. 保持错误代码的稳定性
2. 新增错误代码应遵循现有模式
3. 更新相关文档
4. 添加相应的错误处理逻辑
5. 确保向后兼容性