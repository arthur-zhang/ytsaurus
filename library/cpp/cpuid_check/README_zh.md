# CPUID Check CPU特性检查库

## 项目描述

CPUID Check 库是 YTsaurus 中的 CPU 特性检测工具，用于在程序启动时检查运行环境是否支持编译时指定的 SIMD 指令集扩展。该库确保程序在支持的硬件上安全运行，防止因指令集不兼容导致的程序崩溃。

当程序使用特定的 SIMD 指令集（如 SSE4.2、AVX、AVX2 等）编译时，该库会自动在启动时验证当前 CPU 是否支持这些指令集，如果不支持则立即报告错误并退出程序。

## 核心特性

### 🔍 自动检测
- **启动时检查**: 程序启动时自动验证 CPU 特性
- **编译时关联**: 根据编译器标志自动配置检查项
- **透明集成**: 无需修改应用程序代码
- **自动启用**: 在 Arcadia 构建系统中默认启用

### ⚡ 高效验证
- **快速检查**: 基于 CPUID 指令的快速特性检测
- **最小开销**: 检查过程开销极小
- **早期发现**: 在程序主要逻辑执行前发现问题
- **明确报告**: 提供清晰的错误信息

### 🛡️ 安全保障
- **防止崩溃**: 避免在不支持的硬件上运行
- **错误处理**: 友好的错误报告和退出机制
- **配置灵活**: 支持禁用检查功能
- **兼容性好**: 支持各种编译器和平台

### 🔧 易于使用
- **零配置**: 默认自动工作
- **可选禁用**: 支持手动禁用检查
- **构建系统集成**: 与 Arcadia 构建系统深度集成
- **调试友好**: 提供详细的错误诊断信息

## 支持的指令集

### SIMD 指令集扩展
| 指令集 | 编译器标志 | 描述 | 用途 |
|--------|------------|------|------|
| SSE4.2 | `-msse4.2` | 流式 SIMD 扩展 4.2 | 字符串处理、CRC 计算 |
| PCLMUL | `-mpclmul` | 无进位乘法 | 密码学运算 |
| AES | `-maes` | AES 指令集 | AES 加密解密 |
| AVX | `-mavx` | 高级向量扩展 | 256 位 SIMD 操作 |
| AVX2 | `-mavx2` | 高级向量扩展 2 | 整数 SIMD 扩展 |
| FMA | `-mfma` | 融合乘加 | 数学计算优化 |

### 检查逻辑
```cpp
// 检查优先级（从高到低）
if (defined(_fma_)) {
    AssertFMA();        // 检查 FMA 支持
} else if (defined(_avx2_)) {
    AssertAVX2();       // 检查 AVX2 支持
} else if (defined(_avx_)) {
    AssertAVX();        // 检查 AVX 支持
} else if (defined(_aes_)) {
    AssertAES();        // 检查 AES 支持
} else if (defined(_pclmul_)) {
    AssertPCLMUL();     // 检查 PCLMUL 支持
} else if (defined(_sse4_2_)) {
    AssertSSE42();      // 检查 SSE4.2 支持
}
```

## 实现原理

### 1. CPUID 指令检测
```cpp
namespace {
    // 报告 ISA 不支持的错误
    [[noreturn]] void ReportISAError(const char* isa) {
        err(-1, "This program was compiled for %s which is not supported on your system, exiting...", isa);
    }

    // 定义各种断言函数
    #define Y_DEF_NAME(X) \
        void Assert##X() noexcept { \
            if (!NX86::Have##X()) { \
                ReportISAError(#X); \
            } \
        }

    Y_CPU_ID_ENUMERATE_STARTUP_CHECKS(Y_DEF_NAME)
    #undef Y_DEF_NAME
}
```

### 2. 启动时检查器
```cpp
class TBuildCpuChecker {
public:
    TBuildCpuChecker() {
        Check();  // 构造时执行检查
    }

private:
    void Check() const noexcept {
        // 根据编译时标志检查相应的 CPU 特性
#if defined(_fma_)
        AssertFMA();
#elif defined(_avx2_)
        AssertAVX2();
#elif defined(_avx_)
        AssertAVX();
// ... 其他检查
#endif
    }
};
```

### 3. 自动初始化
```cpp
// 使用高优先级初始化确保在其他代码执行前完成检查
const static TBuildCpuChecker CheckCpuWeAreRunningOn INIT_PRIORITY(101);
```

## 使用方式

### 1. 默认使用（推荐）
在 Arcadia 构建系统中，该库会自动链接到所有 PROGRAM 目标：

```make
PROGRAM(my_program)  # 自动包含 CPU 特性检查
    SOURCES(main.cpp)
    CFLAGS(-mavx2)    # 使用 AVX2 指令集编译
```

程序启动时会自动检查 AVX2 支持，如果不支持会显示：
```
This program was compiled for AVX2 which is not supported on your system, exiting...
```

### 2. 手动链接
如果需要在特定库中强制启用检查：

```make
LIBRARY(my_lib)
    PEERDIR(library/cpp/cpuid_check)  # 手动链接
    CFLAGS(-msse4.2)                  # 使用 SSE4.2 指令集
```

**注意**: 这会给所有使用该库的程序添加检查开销。

### 3. 禁用检查

#### 方法一：使用 NO_CPU_CHECK() 宏
```make
PROGRAM(my_program)
    NO_CPU()          # 禁用所有 util 相关功能
    NO_PLATFORM()     # 禁用平台相关功能
    # 或者
    NO_CPU_CHECK()    # 仅禁用 CPU 特性检查
```

#### 方法二：使用构建标志
```bash
ya make -DCPU_CHECK=no  # 禁用 CPU 检查
```

#### 方法三：使用 FAKE 分配器
```make
PROGRAM(test_program)
    ALLOCATOR(FAKE)    # 禁用 CPU 检查
```

### 4. 特定场景使用

#### 性能关键库
```make
LIBRARY(performance_lib)
    CFLAGS(-mavx2)           # 需要 AVX2 支持
    PEERDIR(library/cpp/cpuid_check)  # 确保检查
```

#### 测试程序
```make
PROGRAM(unit_test)
    NO_CPU_CHECK()           # 测试程序通常不需要检查
    CFLAGS(-mavx2)           # 仍可使用 SIMD 指令
```

#### 兼容性程序
```make
PROGRAM(compatible_program)
    # 不使用特定 SIMD 指令，无需检查
    CFLAGS(-msse2)           # 使用广泛支持的 SSE2
```

## 高级配置

### 1. 自定义检查逻辑
```cpp
// 自定义 CPU 特性检查
class CustomCpuChecker {
public:
    static void CheckRequiredFeatures() {
        // 检查必需的 CPU 特性
        if (!NX86::HaveAVX2()) {
            throw std::runtime_error("AVX2 not supported");
        }

        // 检查可选的性能特性
        if (NX86::HaveFMA()) {
            EnableOptimizedPath();
        } else {
            UseFallbackPath();
        }
    }

private:
    static void EnableOptimizedPath();
    static void UseFallbackPath();
};

// 在 main 函数中调用
int main() {
    CustomCpuChecker::CheckRequiredFeatures();
    // 程序主要逻辑
}
```

### 2. 运行时特性检测
```cpp
// 运行时选择最优实现
class AdaptiveAlgorithm {
public:
    void Process(const Data& input) {
        if (NX86::HaveAVX2()) {
            ProcessAVX2(input);
        } else if (NX86::HaveSSE42()) {
            ProcessSSE42(input);
        } else {
            ProcessGeneric(input);
        }
    }

private:
    void ProcessAVX2(const Data& input);      // 最优实现
    void ProcessSSE42(const Data& input);     // 中等实现
    void ProcessGeneric(const Data& input);   // 基础实现
};
```

### 3. 特性报告工具
```cpp
// CPU 特性报告工具
class CpuFeaturesReporter {
public:
    static void PrintSupportedFeatures() {
        Cout << "支持的 CPU 特性:" << Endl;
        Cout << "  SSE4.2: " << (NX86::HaveSSE42() ? "是" : "否") << Endl;
        Cout << "  AVX: " << (NX86::HaveAVX() ? "是" : "否") << Endl;
        Cout << "  AVX2: " << (NX86::HaveAVX2() ? "是" : "否") << Endl;
        Cout << "  FMA: " << (NX86::HaveFMA() ? "是" : "否") << Endl;
        Cout << "  AES: " << (NX86::HaveAES() ? "是" : "否") << Endl;
        Cout << "  PCLMUL: " << (NX86::HavePCLMUL() ? "是" : "否") << Endl;
    }

    static bool CheckFeatureRequirement(const TString& feature) {
        if (feature == "SSE42") return NX86::HaveSSE42();
        if (feature == "AVX") return NX86::HaveAVX();
        if (feature == "AVX2") return NX86::HaveAVX2();
        if (feature == "FMA") return NX86::HaveFMA();
        if (feature == "AES") return NX86::HaveAES();
        if (feature == "PCLMUL") return NX86::HavePCLMUL();
        return false;
    }
};
```

## 最佳实践

### 1. 分发策略
```make
# 构建多个版本以支持不同硬件
PROGRAM(my_program_avx2)
    SOURCES(main.cpp)
    CFLAGS(-mavx2 -mfma)
    OUTPUT(my_program_avx2)

PROGRAM(my_program_sse42)
    SOURCES(main.cpp)
    CFLAGS(-msse4.2)
    OUTPUT(my_program_sse42)

PROGRAM(my_program_generic)
    SOURCES(main.cpp)
    CFLAGS(-msse2)
    OUTPUT(my_program)
```

### 2. 安装脚本
```bash
#!/bin/bash
# 安装时选择合适的程序版本

check_cpu_features() {
    if grep -q "avx2" /proc/cpuinfo; then
        return 2  # 支持 AVX2
    elif grep -q "sse4_2" /proc/cpuinfo; then
        return 1  # 支持 SSE4.2
    else
        return 0  # 基础支持
    fi
}

install_program() {
    case $(check_cpu_features) in
        2) install -m 755 my_program_avx2 /usr/local/bin/my_program ;;
        1) install -m 755 my_program_sse42 /usr/local/bin/my_program ;;
        0) install -m 755 my_program /usr/local/bin/my_program ;;
    esac
}

install_program
```

### 3. 错误处理增强
```cpp
// 增强的错误处理和用户友好提示
class EnhancedCpuChecker {
public:
    static void CheckWithFallback() {
        try {
            TBuildCpuChecker checker;  // 执行标准检查
        } catch (const std::exception& e) {
            ProvideHelpfulMessage(e.what());
            exit(1);
        }
    }

private:
    static void ProvideHelpfulMessage(const char* error) {
        Cout << "错误: " << error << Endl << Endl;
        Cout << "建议解决方案:" << Endl;
        Cout << "1. 升级到支持所需指令集的 CPU" << Endl;
        Cout << "2. 使用兼容版本: my_program_generic" << Endl;
        Cout << "3. 重新编译不使用高级指令集: -msse2" << Endl;
        Cout << "4. 联系系统管理员获取支持" << Endl;
    }
};
```

### 4. 测试策略
```make
# 测试不同 CPU 特性支持
TEST(cpu_check_test)
    SOURCES(cpu_check_test.cpp)
    CFLAGS(-mavx2)  # 使用最高要求的指令集

TEST(generic_compatibility_test)
    SOURCES(compatibility_test.cpp)
    NO_CPU_CHECK()  # 禁用检查，测试兼容性
    CFLAGS(-msse2)
```

## 性能影响

### 检查开销
- **启动时间**: 增加约 0.1-1ms 启动时间
- **内存占用**: 几乎为零的内存开销
- **运行时影响**: 启动后零运行时开销

### 优化建议
```cpp
// 延迟检查非关键特性
class LazyCpuChecker {
private:
    static bool HasOptionalFeatures;
    static bool Checked;

public:
    static bool HasOptionalSIMD() {
        if (!Checked) {
            HasOptionalFeatures = NX86::HaveAVX2();
            Checked = true;
        }
        return HasOptionalFeatures;
    }
};
```

## 故障排除

### 常见问题

#### 1. 误报不支持
```bash
# 检查 CPU 信息
cat /proc/cpuinfo | grep flags

# 使用工具验证
gcc -march=native -Q --help=target | grep sse
```

#### 2. 虚拟化环境
```cpp
// 虚拟化环境的特殊处理
class VirtualizationAwareChecker {
public:
    static bool IsVirtualized() {
        // 检测虚拟化环境
        return access("/proc/xen", F_OK) == 0 ||
               getenv("container") != nullptr;
    }

    static void CheckWithVirtualizationSupport() {
        if (IsVirtualized()) {
            // 虚拟化环境可能有不同的特性支持
            CheckVirtualizedFeatures();
        } else {
            TBuildCpuChecker checker;
        }
    }
};
```

#### 3. 调试信息
```cpp
// 启用调试模式
#define DEBUG_CPU_CHECK 1

#ifdef DEBUG_CPU_CHECK
#define CPU_CHECK_LOG(msg) \
    Cout << "[CPU Check] " << msg << Endl
#else
#define CPU_CHECK_LOG(msg) do {} while(0)
#endif
```

## 总结

CPUID Check 库为 YTsaurus 系统提供了重要的运行时安全保障。通过自动检查编译时指定的 CPU 特性，该库确保程序只在兼容的硬件上运行，有效防止了因指令集不兼容导致的运行时错误。

其透明的工作方式、最小的性能开销和灵活的配置选项，使其成为构建高性能、可移植应用程序的重要组件。通过合理使用该库，开发者可以充分利用现代 CPU 的 SIMD 指令集，同时保证程序的兼容性和稳定性。