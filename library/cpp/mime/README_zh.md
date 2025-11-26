# MIME 类型检测库

## 项目概述

本库提供了全面的 MIME 类型检测和转换功能，支持基于文件扩展名和 MIME 字符串的类型识别。该库包含了常见的文档、图像、音频、视频、压缩包、应用程序等多种文件类型的映射关系，适用于文件上传处理、内容类型检测、Web 服务响应头设置等场景。

## 文件说明

### 核心实现

- **`types/mime.h`** - MIME 类型定义和接口
  - `MimeTypes`: MIME 类型枚举，定义了 50+ 种常见文件类型
  - `MimeNames`: MIME 类型名称数组
  - 文件扩展名到 MIME 类型的转换函数
  - MIME 字符串到枚举类型的转换函数

- **`types/mime.cpp`** - MIME 类型映射实现
  - `TMimeTypes`: MIME 类型管理类
  - 文件扩展名和 MIME 类型的映射表
  - 高性能的哈希表查找实现
  - 支持一个类型对应多个扩展名

### 构建文件

- **`CMakeLists.txt`** - 跨平台构建配置
- **`ya.make`** - Ytsaurus 构建系统配置

## 实现原理

### MIME 类型枚举

```cpp
enum MimeTypes {
    MIME_UNKNOWN = 0,

    // 文本类型
    MIME_TEXT = 1,           // 纯文本
    MIME_HTML = 2,           // HTML
    MIME_XML = 7,            // XML
    MIME_JSON = 32,          // JSON
    MIME_CSS = 34,           // CSS
    MIME_JAVASCRIPT = 29,    // JavaScript

    // 文档类型
    MIME_PDF = 3,            // PDF
    MIME_DOC = 5,            // Word 97-2003
    MIME_DOCX = 16,          // Word 2007+
    MIME_XLS = 10,           // Excel 97-2003
    MIME_XLSX = 27,          // Excel 2007+
    MIME_PPT = 11,           // PowerPoint 97-2003
    MIME_PPTX = 28,          // PowerPoint 2007+

    // 图像类型
    MIME_IMAGE_JPG = 12,     // JPEG
    MIME_IMAGE_PNG = 14,     // PNG
    MIME_IMAGE_GIF = 15,     // GIF
    MIME_IMAGE_WEBP = 35,    // WebP
    MIME_IMAGE_SVG = 41,     // SVG
    MIME_IMAGE_ICO = 42,     // ICO

    // 音频视频
    MIME_MPEG = 6,           // MP3
    MIME_WAV = 22,           // WAV
    MIME_VIDEO_MP4 = 49,     // MP4
    MIME_VIDEO_AVI = 50,     // AVI

    // 压缩包
    MIME_ARCHIVE = 23,       // TAR/RAR/等
    MIME_GZIP = 26,          // GZIP

    // 应用程序
    MIME_EXE = 24,           // 可执行文件
    MIME_APK = 33,           // Android APK

    // 字体文件
    MIME_TTF = 45,           // TrueType
    MIME_WOFF = 43,          // WOFF
    MIME_WOFF2 = 44,         // WOFF2

    MIME_MAX                 // 类型总数
};
```

### 映射表结构

```cpp
struct TRecord {
    MimeTypes Mime;           // MIME 类型枚举
    const char* ContentType;  // MIME 字符串 (多个用 \0 分隔)
    const char* Ext;          // 文件扩展名 (多个用 \0 分隔)
};

// 示例记录
{MIME_IMAGE_JPG, "image/jpeg\0image/jpg\0", "jpeg\0jpg\0"},
{MIME_HTML, "text/html\0", "html\0htm\0shtml\0"},
```

### 哈希表查找

```cpp
class TMimeTypes {
private:
    THashMap<const char*, int> ContentTypes;  // MIME 字符串到枚举的映射
    THashMap<const char*, int> Ext;           // 扩展名到枚举的映射

public:
    const char* StrByExt(const char* ext) const {
        auto it = Ext.find(ext);
        if (it != Ext.end()) {
            return Records[it->second].ContentType;
        }
        return nullptr;
    }
};
```

## 使用示例

### 基础类型检测

```cpp
#include <library/cpp/mime/types/mime.h>

#include <iostream>

void BasicMimeDetection() {
    // 根据文件扩展名检测 MIME 类型
    const char* filename1 = "document.pdf";
    const char* mime1 = mimetypeByExt(filename1);
    std::cout << filename1 << " -> " << mime1 << std::endl;
    // 输出: document.pdf -> application/pdf

    // 根据文件扩展名检测 MIME 类型
    const char* filename2 = "image.jpg";
    const char* mime2 = mimetypeByExt(filename2);
    std::cout << filename2 << " -> " << mime2 << std::endl;
    // 输出: image.jpg -> image/jpeg

    // 根据扩展名检测（不包含文件名）
    const char* extension = "txt";
    const char* mime3 = mimetypeByExt("", extension);
    std::cout << "Extension '" << extension << "' -> " << mime3 << std::endl;
    // 输出: Extension 'txt' -> text/plain
}
```

### MIME 字符串转换

```cpp
void MimeTypeStringConversion() {
    // MIME 字符串转换为枚举
    MimeTypes type1 = mimeByStr("image/png");
    std::cout << "image/png -> " << ToString(type1) << std::endl;
    // 输出: image/png -> IMAGE_PNG

    // 使用 TStringBuf 版本（避免字符串拷贝）
    TStringBuf mimeStr = "application/json";
    MimeTypes type2 = mimeByStr(mimeStr);
    std::cout << mimeStr << " -> " << ToString(type2) << std::endl;
    // 输出: application/json -> JSON

    // 枚举转换为字符串
    const char* str1 = strByMime(MIME_PDF);
    std::cout << "MIME_PDF -> " << str1 << std::endl;
    // 输出: MIME_PDF -> application/pdf
}
```

### 文件处理应用

```cpp
#include <library/cpp/mime/types/mime.h>
#include <util/folder/dirut.h>
#include <util/stream/file.h>

class FileTypeProcessor {
public:
    struct FileInfo {
        TString FilePath;
        TString Extension;
        MimeTypes MimeType;
        TString MimeString;
    };

    // 批量处理文件类型检测
    TVector<FileInfo> ProcessFiles(const TVector<TString>& files) {
        TVector<FileInfo> results;
        results.reserve(files.size());

        for (const auto& file : files) {
            FileInfo info;
            info.FilePath = file;
            info.Extension = GetFileExtension(file);
            info.MimeType = mimeByStr(mimetypeByExt(file.c_str()));
            info.MimeString = strByMime(info.MimeType);

            results.push_back(info);
        }

        return results;
    }

    // 按类型分组文件
    THashMap<MimeTypes, TVector<TString>> GroupByType(const TVector<FileInfo>& files) {
        THashMap<MimeTypes, TVector<TString>> groups;

        for (const auto& file : files) {
            groups[file.MimeType].push_back(file.FilePath);
        }

        return groups;
    }

    // 检查是否为图像文件
    bool IsImageFile(const TString& filename) {
        MimeTypes type = mimeByStr(mimetypeByExt(filename.c_str()));
        return type == MIME_IMAGE_JPG || type == MIME_IMAGE_PNG ||
               type == MIME_IMAGE_GIF || type == MIME_IMAGE_WEBP ||
               type == MIME_IMAGE_SVG || type == MIME_IMAGE_BMP ||
               type == MIME_IMAGE_TIFF;
    }

    // 检查是否为文档文件
    bool IsDocumentFile(const TString& filename) {
        MimeTypes type = mimeByStr(mimetypeByExt(filename.c_str()));
        return type == MIME_PDF || type == MIME_DOC || type == MIME_DOCX ||
               type == MIME_ODT || type == MIME_RTF;
    }

private:
    TString GetFileExtension(const TString& filename) {
        size_t dotPos = filename.find_last_of('.');
        if (dotPos != TString::npos && dotPos + 1 < filename.size()) {
            return filename.substr(dotPos + 1);
        }
        return "";
    }
};
```

### Web 服务集成

```cpp
#include <library/cpp/mime/types/mime.h>

class WebFileServer {
public:
    struct HttpResponse {
        int StatusCode;
        THashMap<TString, TString> Headers;
        TString Body;
    };

    // 文件下载响应
    HttpResponse ServeFile(const TString& filePath) {
        HttpResponse response;

        // 读取文件
        TFileInput file(filePath);
        TString content = file.ReadAll();
        response.Body = content;

        // 设置 Content-Type 头
        const char* mimeType = mimetypeByExt(filePath.c_str());
        response.Headers["Content-Type"] = mimeType ? mimeType : "application/octet-stream";

        // 设置其他有用的头
        response.Headers["Content-Length"] = ToString(content.size());
        response.Headers["Cache-Control"] = "public, max-age=3600";

        response.StatusCode = 200;
        return response;
    }

    // 文件上传处理
    bool ValidateUploadedFile(const TString& filename, const TString& content) {
        MimeTypes detectedType = mimeByStr(mimetypeByExt(filename.c_str()));

        // 检查是否允许上传的文件类型
        if (!IsAllowedFileType(detectedType)) {
            return false;
        }

        // 检查文件大小（这里简单示例）
        if (content.size() > 50 * 1024 * 1024) { // 50MB
            return false;
        }

        return true;
    }

    // 生成安全的下载文件名
    TString GenerateSafeFileName(const TString& originalName) {
        MimeTypes type = mimeByStr(mimetypeByExt(originalName.c_str()));

        // 根据类型生成安全的文件名
        time_t now = time(nullptr);
        TString timestamp = ToString(now);

        switch (type) {
            case MIME_IMAGE_JPG:
                return "image_" + timestamp + ".jpg";
            case MIME_IMAGE_PNG:
                return "image_" + timestamp + ".png";
            case MIME_PDF:
                return "document_" + timestamp + ".pdf";
            default:
                return "file_" + timestamp;
        }
    }

private:
    bool IsAllowedFileType(MimeTypes type) {
        // 定义允许的文件类型
        static const THashSet<MimeTypes> allowedTypes = {
            MIME_IMAGE_JPG, MIME_IMAGE_PNG, MIME_IMAGE_GIF, MIME_IMAGE_WEBP,
            MIME_PDF, MIME_DOC, MIME_DOCX, MIME_XLS, MIME_XLSX,
            MIME_TXT, MIME_JSON, MIME_XML, MIME_CSV
        };

        return allowedTypes.contains(type);
    }
};
```

### 文件类型统计

```cpp
class FileTypeAnalyzer {
public:
    struct TypeStatistics {
        MimeTypes Type;
        size_t Count;
        size_t TotalSize;
        double SizePercentage;
    };

    // 分析目录中的文件类型分布
    TVector<TypeStatistics> AnalyzeDirectory(const TString& dirPath) {
        TVector<TypeStatistics> stats;
        THashMap<MimeTypes, size_t> typeCount;
        THashMap<MimeTypes, size_t> typeSize;
        size_t totalSize = 0;

        // 遍历目录中的文件
        TDirIterator dir(dirPath);
        for (const auto& entry : dir) {
            if (entry.IsFile()) {
                TString filename = entry.GetName();
                size_t fileSize = entry.GetSize();

                MimeTypes type = mimeByStr(mimetypeByExt(filename.c_str()));
                typeCount[type]++;
                typeSize[type] += fileSize;
                totalSize += fileSize;
            }
        }

        // 构建统计结果
        for (const auto& [type, count] : typeCount) {
            TypeStatistics stat;
            stat.Type = type;
            stat.Count = count;
            stat.TotalSize = typeSize[type];
            stat.SizePercentage = totalSize > 0 ? (double)typeSize[type] / totalSize * 100 : 0;

            stats.push_back(stat);
        }

        // 按文件数量排序
        std::sort(stats.begin(), stats.end(),
                  [](const TypeStatistics& a, const TypeStatistics& b) {
                      return a.Count > b.Count;
                  });

        return stats;
    }

    // 打印分析报告
    void PrintReport(const TVector<TypeStatistics>& stats) {
        std::cout << "File Type Analysis Report\n";
        std::cout << "=========================\n\n";

        std::cout << "Type\t\tCount\tSize\tSize%\n";
        std::cout << "----\t\t-----\t----\t-----\n";

        for (const auto& stat : stats) {
            const char* typeName = strByMime(stat.Type);
            std::cout << typeName << "\t"
                      << stat.Count << "\t"
                      << FormatFileSize(stat.TotalSize) << "\t"
                      << std::fixed << std::setprecision(1) << stat.SizePercentage << "%\n";
        }
    }

private:
    TString FormatFileSize(size_t size) {
        if (size < 1024) {
            return ToString(size) + "B";
        } else if (size < 1024 * 1024) {
            return ToString(size / 1024) + "KB";
        } else if (size < 1024 * 1024 * 1024) {
            return ToString(size / (1024 * 1024)) + "MB";
        } else {
            return ToString(size / (1024 * 1024 * 1024)) + "GB";
        }
    }
};
```

## 支持的文件类型

### 文本类型
- **纯文本**: `.txt`, `.asc` → `text/plain`
- **HTML**: `.html`, `.htm`, `.shtml` → `text/html`
- **XML**: `.xml`, `.rss` → `text/xml`, `application/xml`
- **JSON**: `.json` → `application/json`
- **CSS**: `.css` → `text/css`
- **JavaScript**: `.js` → `application/javascript`
- **Markdown**: `.md` → `text/markdown`
- **RTF**: `.rtf` → `text/rtf`

### 文档类型
- **PDF**: `.pdf` → `application/pdf`
- **Microsoft Word**: `.doc` → `application/msword`
- **Microsoft Word 2007+**: `.docx` → `application/vnd.openxmlformats-officedocument.wordprocessingml.document`
- **Microsoft Excel**: `.xls` → `application/vnd.ms-excel`
- **Microsoft Excel 2007+**: `.xlsx` → `application/vnd.openxmlformats-officedocument.spreadsheetml.sheet`
- **Microsoft PowerPoint**: `.ppt` → `application/vnd.ms-powerpoint`
- **Microsoft PowerPoint 2007+**: `.pptx` → `application/vnd.openxmlformats-officedocument.presentationml.presentation`
- **OpenDocument Text**: `.odt` → `application/vnd.oasis.opendocument.text`
- **OpenDocument Spreadsheet**: `.ods` → `application/vnd.oasis.opendocument.spreadsheet`
- **OpenDocument Presentation**: `.odp` → `application/vnd.oasis.opendocument.presentation`

### 图像类型
- **JPEG**: `.jpg`, `.jpeg` → `image/jpeg`
- **PNG**: `.png` → `image/png`
- **GIF**: `.gif` → `image/gif`
- **BMP**: `.bmp` → `image/bmp`
- **WebP**: `.webp` → `image/webp`
- **SVG**: `.svg` → `image/svg+xml`
- **TIFF**: `.tiff`, `.tif` → `image/tiff`
- **ICO**: `.ico` → `image/x-icon`
- **PNM**: `.pnm`, `.pgm`, `.ppm`, `.pbm` → `image/x-portable-anymap`

### 音频视频类型
- **MP3**: `.mp3`, `.mpa`, `.mp2` → `audio/mpeg`
- **WAV**: `.wav` → `audio/x-wav`
- **MP4**: `.mp4` → `video/mp4`
- **AVI**: `.avi` → `video/x-msvideo`

### 压缩包类型
- **TAR**: `.tar` → `application/x-tar`
- **GZIP**: `.gz`, `.gzip` → `application/x-gzip`
- **RAR**: `.rar` → `application/x-rar`
- **BZIP2**: `.bzip2` → `application/x-bzip2`

### 应用程序类型
- **可执行文件**: `.exe` → `application/octet-stream`
- **Android APK**: `.apk` → `application/vnd.android.package-archive`
- **CHM 帮助文件**: `.chm` → `application/x-chm`

### 字体文件
- **TrueType**: `.ttf` → `font/ttf`
- **WOFF**: `.woff` → `font/woff`
- **WOFF2**: `.woff2` → `font/woff2`

### 其他类型
- **EPUB 电子书**: `.epub` → `application/epub+zip`
- **LaTeX**: `.tex` → `application/x-tex`
- **DjVu**: `.djvu`, `.djv` → `image/vnd.djvu`
- **FB2ZIP**: `.fb2zip` → `application/zip`
- **CBOR**: `.cbor` → `application/cbor`
- **CSV**: `.csv` → `text/csv`
- **Web Manifest**: `.webmanifest` → `application/manifest+json`

## 应用场景

### 1. Web 开发

- **文件上传服务**: 验证上传文件的 MIME 类型
- **内容管理系统**: 自动识别文件类型
- **CDN 服务**: 设置正确的 Content-Type 头
- **静态文件服务器**: 提供文件类型识别

### 2. 文件处理系统

- **文档转换服务**: 根据文件类型选择转换器
- **图像处理**: 识别图像格式进行处理
- **数据导入导出**: 处理不同格式的数据文件
- **备份系统**: 按文件类型分类存储

### 3. 安全应用

- **文件扫描器**: 识别潜在危险的文件类型
- **访问控制**: 基于文件类型设置访问权限
- **内容过滤**: 过滤不允许的文件类型
- **病毒扫描**: 针对特定文件类型的扫描

### 4. 数据分析

- **存储分析**: 分析不同文件类型的存储使用
- **流量分析**: 分析网络流量中的文件类型分布
- **用户行为分析**: 分析用户上传下载的文件类型偏好

### 5. 企业应用

- **文档管理系统**: 自动分类和组织文档
- **邮件系统**: 识别邮件附件类型
- **协作平台**: 文件类型识别和处理
- **电子政务**: 处理各种格式的政务文件

## 性能特性

### 查找性能

- **哈希表查找**: O(1) 平均时间复杂度
- **内存高效**: 共享字符串常量，减少内存占用
- **缓存友好**: 紧凑的数据结构，提高缓存命中率
- **初始化快速**: 延迟初始化，启动时间短

### 内存使用

- **静态映射表**: 编译时确定的映射关系
- **字符串池**: 共享 MIME 字符串常量
- **最小化拷贝**: 使用字符串视图避免不必要的拷贝
- **预估内存占用**: < 50KB 包含所有映射数据

### 扩展性

- **易于扩展**: 添加新的 MIME 类型只需在映射表中添加记录
- **向后兼容**: 新增类型不影响现有代码
- **版本化**: 支持不同版本的 MIME 标准

## 最佳实践

### 1. 错误处理

```cpp
// ✅ 好的错误处理
const char* mime = mimetypeByExt(filename);
if (!mime || strcmp(mime, "application/octet-stream") == 0) {
    // 未知类型，使用魔法数字检测
    mime = DetectMimeByContent(filename);
}

// ✅ 使用枚举进行类型检查
MimeTypes type = mimeByStr(mime);
if (type == MIME_UNKNOWN) {
    LogWarning("Unknown MIME type for file: " << filename);
}
```

### 2. 性能优化

```cpp
// ✅ 批量处理时使用缓存
class MimeCache {
private:
    THashMap<TString, const char*> cache_;

public:
    const char* GetMime(const TString& filename) {
        auto it = cache_.find(filename);
        if (it != cache_.end()) {
            return it->second;
        }

        const char* mime = mimetypeByExt(filename.c_str());
        cache_[filename] = mime;
        return mime;
    }
};

// ✅ 避免重复字符串拷贝
void ProcessFiles(const TVector<TString>& files) {
    for (const auto& file : files) {
        // 直接使用 c_str() 避免拷贝
        const char* mime = mimetypeByExt(file.c_str());
        ProcessFileWithMime(file, mime);
    }
}
```

### 3. 类型安全

```cpp
// ✅ 使用枚举进行比较
if (mimeType == MIME_IMAGE_JPG || mimeType == MIME_IMAGE_PNG) {
    ProcessImageFile(filename);
}

// ❌ 避免直接字符串比较（易出错）
if (strcmp(mimeString, "image/jpeg") == 0 ||
    strcmp(mimeString, "image/png") == 0) {
    ProcessImageFile(filename);
}
```

### 4. 可维护性

```cpp
// ✅ 封装常用功能
class FileTypeHelper {
public:
    static bool IsImage(MimeTypes type) {
        return type >= MIME_IMAGE_JPG && type <= MIME_IMAGE_ICON;
    }

    static bool IsDocument(MimeTypes type) {
        return type == MIME_PDF || type == MIME_DOC || type == MIME_DOCX ||
               type == MIME_ODT || type == MIME_RTF;
    }

    static bool IsArchive(MimeTypes type) {
        return type == MIME_ARCHIVE || type == MIME_GZIP;
    }
};

// 使用封装的功能
if (FileTypeHelper::IsImage(mimeType)) {
    HandleImageFile(filename);
}
```

## 配置和扩展

### 添加新 MIME 类型

```cpp
// 在 mime.cpp 的 Records 数组中添加
{MIME_NEW_TYPE, "application/new-type\0", "new\0newfile\0"},

// 在 mime.h 的枚举中添加
MIME_NEW_TYPE = 51,  // 在 MIME_MAX 之前
```

### 自定义 MIME 映射

```cpp
class CustomMimeTypes {
private:
    THashMap<TString, TString> customMapping_;

public:
    void AddMapping(const TString& extension, const TString& mimeType) {
        customMapping_[extension] = mimeType;
    }

    const char* GetCustomMime(const TString& extension) {
        auto it = customMapping_.find(extension);
        if (it != customMapping_.end()) {
            return it->second.c_str();
        }

        // 回退到标准映射
        return mimetypeByExt(extension.c_str());
    }
};
```