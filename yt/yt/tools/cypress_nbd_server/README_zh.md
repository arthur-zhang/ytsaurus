# Cypress NBD Server

## 项目描述

Cypress NBD Server 是一个高性能的网络块设备（NBD）服务器，它能够将存储在 YTsaurus Cypress 文件系统中的磁盘镜像文件作为网络块设备导出。该工具支持多种文件系统格式（如 ext4、squashfs），允许远程客户端通过标准 NBD 协议挂载和使用这些镜像文件。

## 功能特性

- **网络块设备导出**：通过 NBD 协议导出 Cypress 中的文件
- **多格式支持**：支持 ext4、squashfs 等多种文件系统格式
- **高并发访问**：支持多客户端同时访问
- **高效缓存**：内置缓存机制提高读取性能
- **灵活配置**：通过配置文件管理导出的文件
- **跨平台支持**：支持 Linux 和 macOS 的多个架构

## 文件说明

- `main.cpp` - 主程序源代码，实现 NBD 服务器核心功能
- `ya.make` - 构建配置文件，定义项目依赖
- `README.md` - 英文使用说明文档
- `CMakeLists.*.txt` - CMake 构建配置文件

## 使用方法

### 准备工作

#### 1. 创建 ext4 文件系统镜像

```bash
# 创建 1GB 的空镜像文件
dd if=/dev/zero of=/tmp/1gb_ext4.img bs=1024 count=1048576

# 格式化为 ext4
mkfs -t ext4 /tmp/1gb_ext4.img

# 挂载并填充内容
mkdir ~/mnt
sudo mount -t ext4 /tmp/1gb_ext4.img ~/mnt
# 将需要的内容复制到 ~/mnt 目录
# ...
sudo umount ~/mnt

# 上传到 Cypress（可选优化）
yt --proxy [集群地址] create --type file \
    --attributes '{replication_factor=10;primary_medium=ssd_blobs;account=sys;}' \
    --path //tmp/1gb_ext4.img

# 上传文件内容
yt --proxy [集群地址] write-file //tmp/1gb_ext4.img < /tmp/1gb_ext4.img

# 设置文件系统类型属性
yt --proxy [集群地址] set //tmp/1gb_ext4.img/@filesystem ext4
```

#### 2. 创建 squashfs 文件系统镜像

```bash
# 安装必要工具
sudo apt install squashfs-tools

# 准备源目录
mkdir ~/mnt
# 填充 ~/mnt 目录内容
# ...

# 创建 squashfs 镜像
mksquashfs ~/mnt /tmp/1gb_squashfs.img

# 上传到 Cypress
yt --proxy [集群地址] write-file //tmp/1gb_squashfs.img < /tmp/1gb_squashfs.img
yt --proxy [集群地址] set //tmp/1gb_squashfs.img/@filesystem squashfs
```

### 配置文件

创建配置文件 `config.yson`：

```yson
cluster_connection = {
    # 从 //sys/@cluster_connection 获取集群连接配置
    # ...
};

file_exports = {
    1gb_ext4 = {
        path = "//tmp/1gb_ext4.img";
    };

    # 可以添加更多导出
    # another_fs = {
    #     path = "//tmp/another_file.img";
    # };
};

nbd_server = {
    # NBD 服务器配置
    # ...
};

thread_count = 4;  # 线程数，默认为 2
```

### 编译和运行

#### 编译

```bash
ya make yt/yt/tools/cypress_nbd_server/ -r
```

#### 运行服务器

```bash
./yt/yt/tools/cypress_nbd_server/cypress_nbd_server --config config.yson 2>/tmp/err.txt &
```

### 客户端使用

#### 1. 安装 NBD 客户端

```bash
sudo apt-get install nbd-client
```

#### 2. 连接 NBD 设备

```bash
# 连接到服务器上导出的文件
sudo nbd-client localhost -N 1gb_ext4 /dev/nbd0
```

#### 3. 挂载文件系统

```bash
# 创建挂载点
mkdir ~/mnt

# 只读模式挂载（推荐）
sudo mount -t ext4 -o ro /dev/nbd0 ~/mnt

# 或者对于 squashfs
sudo mount -t squashfs -o ro /dev/nbd0 ~/mnt
```

#### 4. 使用文件系统

```bash
# 浏览内容
ls ~/mnt
cat ~/mnt/some_file.txt

# 注意：只读模式下不能修改
```

#### 5. 清理和断开

```bash
# 卸载文件系统
sudo umount ~/mnt

# 断开 NBD 连接
sudo nbd-client -d /dev/nbd0

# 停止服务器
killall cypress_nbd_server
```

## 实现原理

### 核心架构

1. **NBD 服务器**：实现标准 NBD 协议，处理客户端请求
2. **Cypress 客户端**：连接到 YTsaurus 集群读取文件数据
3. **块设备抽象**：将文件抽象为块设备接口
4. **缓存层**：提高读取性能

### 数据流程

```
NBD客户端 -> NBD协议 -> Cypress NBD Server -> YTsaurus API -> Cypress 存储
```

### 关键组件

- `TCypressFileBlockDeviceConfig` - 文件块设备配置
- `TConfig` - 服务器主配置
- `NBD Server` - NBD 协议实现
- `Image Reader` - 镜像文件读取器

## 性能优化

### 服务端优化

- 调整 `thread_count` 参数以匹配 CPU 核心数
- 使用 SSD 存储后端提高 I/O 性能
- 合理设置缓存大小

### 客户端优化

```bash
# 使用更大的块大小
sudo nbd-client -b 4096 localhost -N 1gb_ext4 /dev/nbd0

# 启用本地缓存（需要支持）
# 具体参数取决于内核版本和配置
```

## 注意事项

### 安全性

- 确保网络连接的安全性
- 使用只读模式避免意外修改
- 定期备份镜像文件

### 性能考虑

- 网络延迟会影响 I/O 性能
- 大文件读取建议使用本地缓存
- 多并发访问需要合理规划

### 限制

- 文件大小受 NBD 协议限制（通常为 2TB）
- 只支持只读访问
- 需要稳定的网络连接

## 故障排除

### 常见问题

1. **连接失败**
   - 检查网络连接
   - 验证配置文件格式
   - 确认服务器正在运行

2. **挂载失败**
   - 检查文件系统类型
   - 验证镜像文件完整性
   - 查看内核日志

3. **性能问题**
   - 检查网络带宽
   - 调整线程数
   - 监控服务器资源使用

### 调试命令

```bash
# 查看服务器日志
tail -f /tmp/err.txt

# 检查 NBD 连接状态
sudo nbd-client -c /dev/nbd0

# 查看内核日志
dmesg | grep nbd
```

## 高级用法

### 多镜像导出

```yson
file_exports = {
    os_image = {
        path = "//tmp/os.img";
    };
    data_image = {
        path = "//tmp/data.img";
    };
    app_image = {
        path = "//tmp/app.img";
    };
};
```

### 负载均衡

可以运行多个服务器实例，使用不同的端口或主机，客户端可以选择最佳连接。

## 依赖项

- **yt/yt/server/lib/nbd** - NBD 协议实现库
- **yt/yt/ytlib/api** - YTsaurus API 客户端
- **yt/yt/ytlib/chunk_client** - 数据块客户端
- **yt/yt/ytlib/file_client** - 文件客户端
- **yt/yt/core/concurrency** - 并发库
- **yt/yt/core/ytree** - YSON 处理库

## 相关协议

- **NBD Protocol** - Network Block Device 协议
- **Cypress API** - YTsaurus 文件系统 API
- **YSON** - YTsaurus 数据序列化格式