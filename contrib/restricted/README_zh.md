# 受限制的许可证组件

本目录包含使用受限制许可证（如 GPL、LGPL、AGPL 等）的第三方组件。使用这些组件需要特别注意许可证合规性要求。

## ⚠️ 重要声明

**使用前请注意：**
- 这些组件的许可证可能对您的项目产生法律影响
- 使用前请仔细阅读并理解相应许可证条款
- 如有疑问，请咨询法律专业人士
- 某些组件可能需要额外的许可或商业授权

## 目录结构

### GPL 组件
- **gpl-libraries/** - 使用 GPL 许可证的库
- **gpl-tools/** - GPL 许可证的工具

### LGPL 组件
- **lgpl-components/** - 使用 LGPL 许可证的组件

### AGPL 组件
- **agpl-services/** - AGPL 许可证的服务组件

### 其他限制性许可证
- **commercial-licensed/** - 商业许可证组件
- **patent-encumbered/** - 涉及专利的组件

## 许可证类型说明

### GPL (General Public License)
- **特点**：强 Copyleft，要求衍生作品也使用 GPL
- **影响**：使用 GPL 代码的项目必须开源
- **版本**：GPLv2, GPLv3

### LGPL (Lesser General Public License)
- **特点**：较弱的 Copyleft
- **影响**：可以通过动态链接方式使用
- **适用**：库和组件

### AGPL (Affero General Public License)
- **特点**：最严格的 Copyleft
- **影响**：即使通过网络服务使用也必须开源
- **注意**：对 SaaS 服务有特殊要求

### 商业许可证
- **特点**：需要购买商业授权
- **费用**：可能需要支付许可费用
- **限制**：使用条款由供应商定义

## 常见组件示例

### 数据库组件
- **MySQL Connector** - GPL v2
- **PostgreSQL JDBC Driver** - BSD（可接受）

### 图像处理
- **ImageMagick** - GPL v3
- **FFmpeg** - GPL/LPG

### 加密库
- **OpenSSL** - Apache 2.0（可接受）
- **GnuPG** - GPL v3

## 使用指南

### 合规性检查清单
- [ ] 识别所有使用的组件
- [ ] 理解每个组件的许可证
- [ ] 评估对项目的影响
- [ ] 获得必要的法律审查
- [ ] 确保遵守所有要求

### 替代方案
1. 寻找具有友好许可证的替代品
2. 使用服务而非直接集成
3. 购买商业授权
4. 重新设计架构以避免依赖

### 代码隔离
```cpp
// 示例：通过动态链接隔离 LGPL 组件
#ifdef USE_LGPL_COMPONENT
    void* handle = dlopen("lgpl_library.so", RTLD_LAZY);
    typedef void (*lGPLFunction)();
    lgplFunction func = (lGPLFunction)dlsym(handle, "function");
    func();
    dlclose(handle);
#endif
```

## 风险管理

### 法律风险
- **许可证侵权** - 未经授权使用
- **版权问题** - 未遵守要求
- **专利风险** - 侵犯第三方专利

### 缓解措施
- **许可证扫描** - 自动化检测
- **法律审查** - 专业意见
- **文档记录** - 保存所有许可信息
- **监控更新** - 跟踪许可证变更

## 最佳实践

### 1. 评估阶段
```bash
# 使用许可证扫描工具
scancode-license --output json src/

# 生成依赖报告
license-checker --json dependencies.json
```

### 2. 开发阶段
```cmake
# 条件编译限制组件
option(USE_GPL_COMPONENTS "Enable GPL components" OFF)

if(USE_GPL_COMPONENTS)
    add_subdirectory(restricted/gpl-components)
endif()
```

### 3. 部署阶段
- 明确声明使用的组件
- 提供许可证文本
- 确保源码可获取（如果需要）

## 工具和资源

### 许可证扫描工具
- **FOSSA** - Facebook 开源代码分析
- **Black Duck** - 商业扫描工具
- **Scancode** - 开源扫描工具
- **FOSSology** - 开源许可证分析

### 参考资料
- [OSADL 许可证列表](https://www.osadl.org/)
- [SPDX 许可证列表](https://spdx.org/licenses/)
- [FSF 许可证指南](https://www.fsf.org/licensing/)

## 决策流程

### 使用决策树
```
是否需要该组件？
    ↓
是否有替代方案？
    ↓
替代方案是否满足需求？
    ↓
是否有商业授权预算？
    ↓
是否接受开源要求？
    ↓
使用组件
```

### 示例决策

**场景1**：内部使用工具
- ✅ 可以使用 GPL 组件

**场景2**：开源产品
- ❌ 避免使用 GPL，考虑 Apache 2.0 或 MIT

**场景3**：商业 SaaS 产品
- ❌ 避免 AGPL
- ⚠️ 谨慎使用 GPL
- ✅ 可考虑 LGPL（动态链接）

## 文档要求

### 必须包含的文档
1. 组件许可证文本
2. 使用声明
3. 获取源码的方法
4. 修改记录（如果适用）

### 示例声明
```
本产品使用以下第三方组件：

组件名称：XXX
许可证：GPL v3
获取源码：https://github.com/xxx/xxx
```

## 联系信息

如有关于许可证的问题：
- 法律部门：legal@company.com
- 开源合规：opensource@company.com

## 更新日志

- 2024-01-01：添加组件许可证清单
- 2024-02-01：更新风险评估
- 2024-03-01：添加替代方案文档

---

**最后提醒**：本 README 仅提供指导信息，不构成法律建议。请根据具体情况咨询专业法律人士。