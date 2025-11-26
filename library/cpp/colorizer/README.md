# colorizer

终端颜色输出库，提供了完整的 ANSI 颜色代码支持，用于在支持颜色的终端中输出彩色文本，增强命令行工具的可读性。

## 功能描述

colorizer 库实现了 ECMA-48 (ANSI) 颜色代码系统，允许开发者在终端中输出彩色文本。它提供了丰富的颜色选择、文本样式和自动检测终端支持的功能。

## 核心特性

- **ANSI 颜色支持**：完整的 16 色和 256 色支持
- **文本样式**：支持粗体、斜体、下划线等样式
- **自动检测**：自动检测终端是否支持颜色
- **跨平台**：支持 Linux、macOS、Windows (需要现代终端)
- **安全输出**：对不支持颜色的终端自动去除颜色代码
- **性能优化**：最小化运行时开销

## 颜色系统

### 基本颜色 (ANSI 16色)
```cpp
enum EAnsiCode: i8 {
    RESET,              // 重置所有样式

    // 前景色
    FG_DEFAULT,         // 默认前景色
    FG_BLACK,           // 黑色
    FG_RED,             // 红色
    FG_GREEN,           // 绿色
    FG_YELLOW,          // 黄色
    FG_BLUE,            // 蓝色
    FG_MAGENTA,         // 洋红
    FG_CYAN,            // 青色
    FG_WHITE,           // 白色
    FG_LIGHT_BLACK,     // 亮黑色(灰)
    FG_LIGHT_RED,       // 亮红色
    FG_LIGHT_GREEN,     // 亮绿色
    FG_LIGHT_YELLOW,    // 亮黄色
    FG_LIGHT_BLUE,      // 亮蓝色
    FG_LIGHT_MAGENTA,   // 亮洋红
    FG_LIGHT_CYAN,      // 亮青色
    FG_LIGHT_WHITE,     // 亮白色

    // 背景色 (对应前缀 BG_)
    BG_BLACK,           // 黑色背景
    BG_RED,             // 红色背景
    // ... 其他背景色

    // 文本样式
    ST_LIGHT,           // 亮色/粗体
    ST_DARK,            // 暗色
    ST_NORMAL,          // 正常
    ITALIC_ON,          // 斜体开启
    ITALIC_OFF,         // 斜体关闭
    UNDERLINE_ON,       // 下划线开启
    UNDERLINE_OFF,      // 下划线关闭
};
```

## 主要组件

### 基本颜色使用
```cpp
#include <library/cpp/colorizer/colors.h>

using namespace NColorizer;

// 直接使用颜色代码
Cout << FG_RED << "错误: " << RESET << "操作失败" << Endl;
Cout << FG_GREEN << "成功: " << RESET << "操作完成" << Endl;

// 使用样式
Cout << ST_LIGHT << "重要提示" << RESET << Endl;
Cout << UNDERLINE_ON << "链接文本" << UNDERLINE_OFF << RESET << Endl;
```

### 自动颜色检测
```cpp
// AutoColors 会自动检测终端是否支持颜色
void PrintMessage(const TString& msg) {
    Cout << AutoColors(FG_YELLOW) << msg << AutoColors(RESET) << Endl;
}

// 在不支持颜色的终端中不会输出颜色代码
// 在支持颜色的终端中会输出黄色文本
```

### 复合样式
```cpp
// 组合多种样式
Cout << FG_BLUE << BG_WHITE << UNDERLINE_ON
     << "蓝色背景白色文字带下划线"
     << RESET << Endl;

// 亮色文本
Cout << ST_LIGHT << FG_RED << "亮红色文本" << RESET << Endl;
```

## 使用示例

### 日志系统
```cpp
class ColoredLogger {
public:
    enum ELevel {
        DEBUG,
        INFO,
        WARNING,
        ERROR,
        FATAL
    };

    static void Log(ELevel level, const TString& message) {
        using namespace NColorizer;

        switch (level) {
            case DEBUG:
                Cout << AutoColors(FG_LIGHT_BLACK) << "[DEBUG] "
                     << AutoColors(RESET) << message << Endl;
                break;
            case INFO:
                Cout << AutoColors(FG_GREEN) << "[INFO] "
                     << AutoColors(RESET) << message << Endl;
                break;
            case WARNING:
                Cout << AutoColors(FG_YELLOW) << "[WARNING] "
                     << AutoColors(RESET) << message << Endl;
                break;
            case ERROR:
                Cout << AutoColors(FG_RED) << "[ERROR] "
                     << AutoColors(RESET) << message << Endl;
                break;
            case FATAL:
                Cout << AutoColors(ST_LIGHT) << AutoColors(FG_RED)
                     << "[FATAL] " << AutoColors(RESET) << message << Endl;
                break;
        }
    }
};
```

### 进度显示
```cpp
class ProgressBar {
private:
    int total_;
    int current_ = 0;
    int width_ = 50;

public:
    ProgressBar(int total) : total_(total) {}

    void Update(int increment = 1) {
        current_ += increment;
        float progress = float(current_) / total_;

        // 计算进度条长度
        int filled = int(progress * width_);
        int empty = width_ - filled;

        using namespace NColorizer;

        // 绘制进度条
        Cout << "\r[";
        Cout << BG_GREEN << TString(filled, ' ') << AutoColors(RESET);
        Cout << BG_LIGHT_BLACK << TString(empty, ' ') << AutoColors(RESET);
        Cout << "] " << int(progress * 100) << "%";
        Cout.flush();

        if (current_ >= total_) {
            Cout << Endl;
        }
    }
};
```

### 代码高亮
```cpp
class SyntaxHighlighter {
public:
    static TString HighlightCode(const TString& code) {
        using namespace NColorizer;
        TString result;

        // 简单的语法高亮示例
        for (char ch : code) {
            if (isdigit(ch)) {
                result += AutoColors(FG_CYAN);
                result += ch;
                result += AutoColors(RESET);
            } else if (isalpha(ch)) {
                result += AutoColors(FG_GREEN);
                result += ch;
                result += AutoColors(RESET);
            } else if (isspace(ch)) {
                result += ch;
            } else {
                result += AutoColors(FG_RED);
                result += ch;
                result += AutoColors(RESET);
            }
        }

        return result;
    }
};
```

### 表格显示
```cpp
class ColoredTable {
private:
    struct Cell {
        TString content;
        EAnsiCode fgColor;
        EAnsiCode bgColor;
    };

    TVector<TVector<Cell>> rows_;
    int colWidth_ = 15;

public:
    void AddRow(const TVector<Cell>& row) {
        rows_.push_back(row);
    }

    void Print() {
        using namespace NColorizer;

        // 打印表头
        Cout << ST_LIGHT;
        for (const auto& row : rows_) {
            for (const auto& cell : row) {
                Cout << setw(colWidth_) << left << cell.content.substr(0, colWidth_);
            }
            Cout << Endl;
            break; // 只打印第一行作为表头
        }
        Cout << RESET;

        // 打印分隔线
        Cout << TString(colWidth_ * rows_[0].size(), '-') << Endl;

        // 打印数据行
        for (size_t i = 1; i < rows_.size(); ++i) {
            for (const auto& cell : rows_[i]) {
                Cout << cell.fgColor << cell.bgColor;
                Cout << setw(colWidth_) << left << cell.content.substr(0, colWidth_);
                Cout << RESET;
            }
            Cout << Endl;
        }
    }
};
```

## 高级功能

### 颜色主题
```cpp
class ColorTheme {
public:
    struct Theme {
        EAnsiCode errorColor = FG_RED;
        EAnsiCode warningColor = FG_YELLOW;
        EAnsiCode infoColor = FG_BLUE;
        EAnsiCode successColor = FG_GREEN;
        EAnsiCode highlightColor = FG_CYAN;
    };

    static void ApplyTheme(const Theme& theme) {
        // 保存主题到全局变量或配置
        SetGlobalTheme(theme);
    }

    static EAnsiCode GetColor(const TString& type) {
        const Theme& theme = GetGlobalTheme();
        if (type == "error") return theme.errorColor;
        if (type == "warning") return theme.warningColor;
        if (type == "info") return theme.infoColor;
        if (type == "success") return theme.successColor;
        if (type == "highlight") return theme.highlightColor;
        return FG_DEFAULT;
    }
};
```

### 条件着色
```cpp
class ConditionalColorizer {
public:
    template <typename T>
    static void PrintComparison(T a, T b) {
        using namespace NColorizer;

        if (a > b) {
            Cout << AutoColors(FG_GREEN) << a << AutoColors(RESET);
        } else if (a < b) {
            Cout << AutoColors(FG_RED) << a << AutoColors(RESET);
        } else {
            Cout << AutoColors(FG_YELLOW) << a << AutoColors(RESET);
        }

        Cout << " vs ";

        Cout << AutoColors(FG_GREEN) << b << AutoColors(RESET);
        Cout << Endl;
    }
};
```

### 彩虹效果
```cpp
class RainbowEffect {
private:
    static const EAnsiCode RAINBOW_COLORS[];
    static const int COLOR_COUNT = 7;

public:
    static void PrintRainbow(const TString& text) {
        using namespace NColorizer;

        for (size_t i = 0; i < text.size(); ++i) {
            EAnsiCode color = RAINBOW_COLORS[i % COLOR_COUNT];
            Cout << AutoColors(color) << text[i];
        }
        Cout << AutoColors(RESET) << Endl;
    }

    static void PrintGradient(const TString& text,
                             EAnsiCode startColor,
                             EAnsiCode endColor) {
        // 实现渐变效果
        // 这里需要将颜色插值
        // 简化版本：交替使用两种颜色
        using namespace NColorizer;

        for (size_t i = 0; i < text.size(); ++i) {
            EAnsiCode color = (i % 2 == 0) ? startColor : endColor;
            Cout << AutoColors(color) << text[i];
        }
        Cout << AutoColors(RESET) << Endl;
    }
};
```

## 配置和环境

### 环境变量
```bash
# 强制启用颜色
export FORCE_COLOR=1

# 禁用颜色
export NO_COLOR=1

# 设置颜色模式 (auto/always/never)
export CLICOLOR_FORCE=1
```

### 运行时检测
```cpp
class ColorSupport {
public:
    static bool IsColorSupported() {
        // 检查环境变量
        if (getenv("NO_COLOR")) {
            return false;
        }
        if (getenv("FORCE_COLOR") || getenv("CLICOLOR_FORCE")) {
            return true;
        }

        // 检查是否是终端
        if (!isatty(fileno(stdout))) {
            return false;
        }

        // 检查 TERM 环境变量
        const char* term = getenv("TERM");
        if (term &&
            (strstr(term, "color") != nullptr ||
             strstr(term, "xterm") != nullptr ||
             strstr(term, "screen") != nullptr)) {
            return true;
        }

        return false;
    }
};
```

## 平台特性

### Windows 支持
```cpp
#ifdef _WIN32
class WindowsConsole {
public:
    static void EnableVirtualTerminal() {
        // 启用 Windows 10+ 的虚拟终端序列
        HANDLE hOut = GetStdHandle(STD_OUTPUT_HANDLE);
        DWORD dwMode = 0;
        GetConsoleMode(hOut, &dwMode);
        dwMode |= ENABLE_VIRTUAL_TERMINAL_PROCESSING;
        SetConsoleMode(hOut, dwMode);
    }
};
#endif
```

### macOS 终端
```cpp
class MacTerminal {
public:
    static bool IsDarkMode() {
        // 检查 macOS 是否在暗色模式
        NSString* appearance = [[NSUserDefaults standardUserDefaults]
                               stringForKey:@"AppleInterfaceStyle"];
        return [appearance isEqualToString:@"Dark"];
    }
};
```

## 最佳实践

### 性能考虑
```cpp
// 使用 constexpr 编译时优化
constexpr bool ENABLE_COLORS = true;

// 预定义颜色字符串避免重复创建
class PredefinedColors {
public:
    static const TString Red() { return ENABLE_COLORS ? "\x1b[31m" : ""; }
    static const TString Reset() { return ENABLE_COLORS ? "\x1b[0m" : ""; }
};
```

### 可访问性
```cpp
class AccessibleOutput {
public:
    enum EMode {
        COLOR,      // 使用颜色
        MONOCHROME, // 使用符号标记
        SYMBOLIC    // 使用文本标记
    };

    static void PrintAlert(EMode mode, const TString& message) {
        switch (mode) {
            case COLOR:
                Cout << AutoColors(FG_RED) << message << AutoColors(RESET);
                break;
            case MONOCHROME:
                Cout << "[!] " << message;
                break;
            case SYMBOLIC:
                Cout << "ERROR: " << message;
                break;
        }
        Cout << Endl;
    }
};
```

### 错误处理
```cpp
class SafeColorizer {
public:
    static void SafePrint(EAnsiCode color, const TString& text) {
        try {
            Cout << AutoColors(color) << text << AutoColors(RESET);
        } catch (...) {
            // 如果颜色输出失败，输出纯文本
            Cout << text;
        }
    }
};
```

## 应用场景

### 命令行工具
- **编译器输出**：错误和警告使用不同颜色
- **测试框架**：通过/失败用颜色区分
- **代码格式化**：语法高亮显示
- **diff 工具**：增删改用颜色标识

### 系统监控
- **状态指示**：正常/警告/错误状态
- **性能指标**：使用颜色表示性能等级
- **日志分析**：不同级别日志用颜色区分

### 调试工具
- **断点标记**：特殊位置用颜色标识
- **变量高亮**：重要变量突出显示
- **调用栈**：不同层级用颜色区分