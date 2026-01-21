# Airdrop 文件传输系统

一个轻量级的文件传输服务，支持文件上传下载，类似OSS服务。

## 功能特性

- ✅ 文件上传下载
- ✅ 目录浏览
- ✅ 文件删除
- ✅ 路径安全检查
- ✅ 文件哈希校验
- ✅ 跨平台支持 (Windows/Linux/macOS)
- ✅ RESTful API
- ✅ 命令行客户端
- ✅ 阿里云 OSS 命令行工具
- ✅ 内置 Python 环境隔离
- ✅ 快捷命令安装
- ✅ 开发打包工具

## 安装说明

### Windows

#### 默认安装（使用 'ad' 快捷方式）
双击运行 `install.bat` 脚本，或者在终端中执行：
```cmd
.\install.bat
```

#### 自定义快捷方式名称
如果 `ad` 命令已被占用，可以指定自定义的快捷方式名称：
```cmd
.\install.bat ad1
```
这将创建 `ad1.bat` 快捷方式，避免与现有命令冲突。

安装脚本会自动：
1. 检测快捷方式是否已存在
2. 如果存在，提供选项：覆盖(O) / 重命名(R) / 取消(C)
3. 安装 Python 环境和依赖
4. 创建自定义快捷命令
5. 自动配置环境变量（PATH）
6. 配置 PowerShell 别名

### Linux / macOS

#### 默认安装（使用 'ad' 快捷方式）
```bash
chmod +x install.sh
./install.sh
```

#### 自定义快捷方式名称
```bash
./install.sh ad1
```
或者
```bash
./install.sh install ad1
```

安装脚本会自动：
1. 检测快捷方式是否已存在
2. 如果存在，提供选项：覆盖(O) / 重命名(R) / 取消(C)
3. 安装 Python 环境
4. 创建自定义快捷命令
5. 更新 shell 配置文件 (`.bashrc`, `.zshrc` 等)

> **注意**: 安装完成后，可能需要重启终端或运行 `source ~/.bashrc` 才能生效。

### 卸载

#### Windows
```cmd
# 卸载默认的 'ad' 快捷方式
.\install.bat uninstall

# 卸载自定义快捷方式（如 'ad1'）
.\install.bat uninstall ad1
```

#### Linux / macOS
```bash
# 卸载默认的 'ad' 快捷方式
./install.sh uninstall

# 卸载自定义快捷方式（如 'ad1'）
./install.sh uninstall ad1
```

## 快速开始

### 1. 启动服务器

**Linux/macOS:**
```bash
# 使用默认配置
ad server /path/to/storage
```

**Windows:**
```cmd
# 使用默认配置
ad server C:\path\to\storage
```

### 2. 使用客户端

安装完成后，可以使用你指定的快捷命令（默认为 `ad`）：

```bash
# 以下示例使用默认的 'ad' 命令
# 如果你安装时使用了自定义名称（如 'ad1'），请将 'ad' 替换为 'ad1'

# 1. 配置默认服务器
ad setup http://localhost:8888

# 2. 文件传输
ad put file.txt test/
ad get test/file.txt
ad list

# 3. OSS 操作
ad oss config --id <AccessKeyId> --secret <AccessKeySecret>
ad oss put local_file.txt
ad oss list

# 4. Python 脚本
ad python script.py
```

## 客户端使用详解

### 配置管理
```bash
# 配置默认服务器
ad setup http://192.168.1.100:8888

# 修改服务器地址
ad setup http://backup.example.com:8888

# 查看当前服务器配置
ad servers

# 获取服务器信息
ad info
```

### 文件上传
```bash
# 上传文件到指定路径
ad put file.txt test/1/
ad put image.jpg photos/2024/
ad put --overwrite file.txt test/1/  # 覆盖已存在文件
```

### 文件下载
```bash
# 下载文件
ad get test/1/file.txt ./local_file.txt
ad get photos/2024/image.jpg ./downloads/
ad get --overwrite test/1/file.txt ./local_file.txt  # 覆盖本地文件
```

### 文件浏览
```bash
# 列出根目录
ad list

# 列出指定目录
ad list test/
ad list photos/2024/
```

### 文件删除
```bash
# 删除文件
ad delete test/1/file.txt

# 删除空目录
ad delete test/empty_dir/
```

## OSS 命令行工具 (ad oss)

Airdrop 提供了阿里云 OSS 的便捷操作工具。

### 配置 OSS
```bash
# 配置 AccessKey (自动保存到本地 .env)
ad oss config --id LTAIxxx --secret xxxxxx

# 配置 Bucket 和 Endpoint (可选)
ad oss config --bucket my-bucket --endpoint http://oss-cn-hangzhou.aliyuncs.com
```

### OSS 文件操作
```bash
# 上传文件
ad oss put file.txt
ad oss put file.txt oss_path/file.txt

# 下载文件
ad oss get oss_path/file.txt
ad oss get oss_path/file.txt ./local_file.txt

# 列出文件
ad oss list
ad oss list prefix/

# 删除文件
ad oss delete oss_path/file.txt

# 检查文件存在
ad oss exists oss_path/file.txt
```

## Python 环境使用 (ad python)

Airdrop 内置了一个独立的 Python 环境。您可以使用 `ad python` 命令来使用它，而无需污染系统的 Python 环境。

```bash
# 1. 进入交互式 Python Shell
ad python

# 2. 运行 Python 脚本
ad python my_script.py

# 3. 安装额外的包 (仅影响 Airdrop 环境)
ad python -m pip install pandas
```

## 打包与维护 (Pack Mode)

脚本现在支持自动打包功能（更新依赖、清理缓存、重新压缩）。

**Windows:**
```cmd
.\install.bat pack
```

**Linux / macOS:**
```bash
./install.sh pack
```

此命令会自动：
1. 解压现有的 Python 压缩包（如果目录不存在）
2. 安装 `requirements.txt` 中的依赖
3. 清理 `__pycache__` 和 `.pyc` 文件
4. 重新打包为 `.tar.gz` 或 `.tar.xz`
5. 清理临时解压的目录

> **注意**: Linux 下默认使用 `xz` 进行高压缩率打包 (`-9e -T0`)。所有 `pack` 操作都会在完成后自动清理临时解压的 python 目录。

## API 文档

### 服务器信息
```
GET /api/info
```

### 文件上传
```
POST /api/upload
Content-Type: multipart/form-data

参数:
- file: 文件内容
- path: 目标路径
- overwrite: 是否覆盖 (true/false)
```

### 文件下载
```
GET /api/download/<path:file_path>
```

### 文件列表
```
GET /api/list
GET /api/list/<path:dir_path>
```

### 文件删除
```
DELETE /api/delete/<path:file_path>
```

## 故障排除

### 1. 端口被占用
```bash
# 查看端口占用
netstat -tulpn | grep :8888

# 使用其他端口
ad server --port 9999 /path/to/storage
```

### 2. 权限问题
```bash
# 确保目录有写权限
chmod 755 /path/to/storage

# 检查文件权限
ls -la /path/to/storage
```

### 3. 网络连接问题
```bash
# 测试服务器连接
curl http://localhost:8888/api/info

# 检查防火墙设置
sudo ufw status
```

## 项目结构
```
smell_airdrop/
├── server/
│   └── server.py          # 服务器端
├── client/
│   └── client.py          # 客户端
├── oss/
│   └── oss_cli.py         # OSS 命令行工具
├── wrappers/
│   ├── ad                 # Linux 命令封装
│   └── ad.bat             # Windows 命令封装
├── install.bat            # Windows 安装脚本
├── install.sh             # Linux/macOS 安装脚本
├── requirements.txt       # Python 依赖
└── README.md              # 文档
```

## License

MIT License
