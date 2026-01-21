# Airdrop 安装指南

## 快速安装

### Windows

#### 默认安装
```cmd
.\install.bat
```
这将创建 `ad` 快捷命令。

#### 自定义快捷方式名称
```cmd
.\install.bat <快捷方式名称>
```

**示例：**
```cmd
.\install.bat ad1       # 创建 ad1 快捷命令
.\install.bat myair     # 创建 myair 快捷命令
```

### Linux / macOS

#### 默认安装
```bash
chmod +x install.sh
./install.sh
```
这将创建 `ad` 快捷命令。

#### 自定义快捷方式名称
```bash
./install.sh <快捷方式名称>
```

**示例：**
```bash
./install.sh ad1        # 创建 ad1 快捷命令
./install.sh myair      # 创建 myair 快捷命令
```

## 处理快捷方式冲突

如果安装时发现快捷方式已存在，安装脚本会提示你选择：

- **[O]verwrite** - 覆盖现有的快捷方式
- **[R]ename** - 输入一个新的名称
- **[C]ancel** - 取消安装

**示例交互：**
```
[WARNING] Shortcut 'ad' already exists at: /home/user/.local/bin/ad
Do you want to: [O]verwrite / [R]ename / [C]ancel? R
Enter a new shortcut name: ad1
```

## 卸载

### Windows
```cmd
# 卸载默认的 'ad' 快捷方式
.\install.bat uninstall

# 卸载指定的快捷方式
.\install.bat uninstall ad1
```

### Linux / macOS
```bash
# 卸载默认的 'ad' 快捷方式
./install.sh uninstall

# 卸载指定的快捷方式
./install.sh uninstall ad1
```

## 安装后使用

安装完成后，重启终端（或运行 `source ~/.bashrc`），然后就可以使用你的快捷命令了：

```bash
# 如果使用默认的 'ad'
ad --help
ad setup http://localhost:8888

# 如果使用自定义的 'ad1'
ad1 --help
ad1 setup http://localhost:8888
```

## 常见问题

### Q: 为什么需要自定义快捷方式名称？

**A:** 如果你的系统中已经有 `ad` 命令（例如 Active Directory 工具），使用自定义名称可以避免命令冲突。

### Q: 可以同时安装多个快捷方式吗？

**A:** 可以！你可以多次运行安装脚本，每次使用不同的名称：
```bash
./install.sh ad1
./install.sh ad2
./install.sh myair
```

### Q: 安装后命令无法使用怎么办？

**A:** 
1. 重启终端或运行 `source ~/.bashrc` (Linux/macOS)
2. 在 Windows 上，可能需要重启 PowerShell
3. 确认 PATH 环境变量已正确配置

### Q: 如何查看已安装的快捷方式？

**A:** 
- **Windows:** 查看 `%USERPROFILE%\Scripts\` 目录
- **Linux/macOS:** 查看 `~/.local/bin/` 目录

```bash
# Linux/macOS
ls -la ~/.local/bin/ad*

# Windows PowerShell
Get-ChildItem "$env:USERPROFILE\Scripts\ad*"
```
