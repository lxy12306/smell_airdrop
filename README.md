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
- ✅ 快捷命令安装

## 安装说明

### Windows
双击运行 `install.bat` 脚本，或者在终端中执行：
```cmd
.\install.bat
```
该脚本会自动：
1. 安装 Python 环境和依赖
2. 创建 `ad` 命令
3. 自动配置环境变量（PATH）
4. 配置 PowerShell 别名

### Linux / macOS
```bash
chmod +x install.sh
./install.sh
```
该脚本会自动：
1. 安装 Python 环境
2. 创建 `ad` 命令
3. 更新 shell 配置文件 (`.bashrc`, `.zshrc` 等)

> **注意**: 安装完成后，可能需要重启终端才能生效。

## 快速开始

### 1. 启动服务器

**Linux/macOS:**
```bash
# 使用默认配置
./airdrop.sh server /path/to/storage
```

**Windows:**
```cmd
# 使用默认配置
airdrop.bat server C:\path\to\storage
```

### 2. 使用客户端 (ad)

安装完成后，可以直接使用 `ad` 命令：

```bash
# 1. 配置默认服务器
ad setup http://localhost:8888

# 2. 查看配置
ad servers

# 3. 文件传输
ad put file.txt test/
ad get test/file.txt
ad list
```

## 客户端使用

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

## 使用示例

### 场景1: 文件传输到远程服务器

```bash
# 1. 启动服务器 (在远程Linux服务器上)
./airdrop.sh server --host 0.0.0.0 --port 8888 /home/user/files

# 2. 配置客户端 (在本地机器上)
ad setup remote http://remote-server:8888 --default

# 3. 上传文件
ad upload document.pdf work/documents/
ad upload photos/*.jpg photos/vacation/

# 4. 查看文件
ad list work/documents/
ad list photos/vacation/
```

### 场景2: 团队文件共享

```bash
# 服务器管理员启动服务
./airdrop.sh server /shared/team-files

# 团队成员配置客户端
ad setup team http://team-server:8888 --default

# 上传项目文件
ad upload project.zip projects/v1.0/
ad upload design.psd assets/designs/

# 下载其他人的文件
ad download projects/v1.0/project.zip ./
ad list assets/designs/
```

### 场景3: 备份文件

```bash
# 配置备份服务器
ad setup backup http://backup-server:8888

# 批量备份
ad upload important.doc backup/daily/$(date +%Y%m%d)/
ad upload database.sql backup/db/$(date +%Y%m%d)/

# 查看备份
ad list backup/daily/ --server backup
```

## 配置文件

客户端配置文件位于: `~/.airdrop_config.json`

```json
{
  "servers": {
    "myserver": {
      "url": "http://localhost:8888"
    },
    "backup": {
      "url": "http://backup.example.com:8888"
    }
  },
  "default_server": "myserver"
}
```

## 安全说明

1. **路径安全**: 所有文件操作都限制在指定的根目录内
2. **文件名安全**: 自动清理不安全的文件名字符
3. **大小限制**: 可配置最大文件上传大小
4. **网络访问**: 建议在可信网络环境中使用，或配置适当的防火墙规则

## 系统要求

- Python 3.7+
- Flask 2.0+
- Requests 2.25+

## 故障排除

### 1. 端口被占用
```bash
# 查看端口占用
netstat -tulpn | grep :8888

# 使用其他端口
./airdrop.sh server --port 9999 /path/to/storage
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

### 4. 客户端配置问题
```bash
# 重新配置服务器
ad setup myserver http://correct-url:8888 --default

# 检查配置文件
cat ~/.airdrop_config.json
```

## 开发

### 项目结构
```
smell_airdrop/
├── server/
│   └── server.py          # 服务器端
├── client/
│   └── client.py          # 客户端
├── airdrop.sh             # Linux/macOS 启动脚本
├── airdrop.bat            # Windows 启动脚本
├── requirements.txt       # Python 依赖
└── README.md             # 文档
```

### 扩展开发

如需扩展功能，可以修改：
- `server/server.py`: 添加新的API端点
- `client/client.py`: 添加新的客户端命令
- API支持认证、权限控制等高级功能

### 打包说明

Linux 环境下生成 Python 运行环境包 (`python_linux_x86.tar.xz`) 的命令：

```bash
# 进入包含 python/ 目录的路径
XZ_OPT="-9e -T0" tar -cJf python_linux_x86.tar.xz python/
```

## License

MIT License
