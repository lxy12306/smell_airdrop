#!/usr/bin/env python3
"""
Airdrop 文件传输系统安装程序
支持 Windows 和 Linux 平台自动安装和配置
"""

import os
import sys
import platform
import subprocess
import shutil
import json
from pathlib import Path
from typing import Optional, List, Tuple

if platform.system().lower() == 'windows':
    import winreg  # Windows注册表访问


class SetupError(Exception):
    """安装错误"""
    pass


class AirdropSetup:
    """Airdrop 安装管理器"""
    
    def __init__(self):
        self.platform = platform.system().lower()
        self.script_dir = Path(__file__).parent.resolve()
        self.python_exe: str = ""
        self.install_dir: Optional[Path] = None

        # 验证平台支持
        if self.platform not in ['windows', 'linux']:
            raise SetupError(f"当前仅支持 Windows 和 Linux 平台，检测到平台: {self.platform}")

        print(f"🚀 Airdrop 安装程序")
        print(f"📍 脚本目录: {self.script_dir}")
        print(f"💻 平台: {self.platform.title()}")
        print(f"🐍 Python: 内嵌独立环境")
        print("-" * 50)
        
        # 仅在 Linux 平台解压 python_linux.tar.gz
        if self.platform == 'linux':
            tar_file = self.script_dir / 'python_linux.tar.gz'
            if tar_file.exists():
                print(f"📦 检测到压缩文件 {tar_file}，正在解压...")
                try:
                    subprocess.run(['tar', '-xzf', str(tar_file), '-C', str(self.script_dir)], check=True)
                    print("✅ 解压完成")
                except subprocess.CalledProcessError as e:
                    raise SetupError(f"❌ 解压失败: {e}")
            else:
                print(f"❌ 未找到压缩文件 {tar_file}")
    
    def detect_python(self) -> Tuple[str, str]:
        """检测可用的Python解释器"""
        print("🔍 检测 Python 环境...")

        if self.platform == 'linux':
            
            embedded_python = self.script_dir / 'python_linux' / 'bin' / 'python3'
            if embedded_python.exists():
                try:
                    result = subprocess.run(
                        [str(embedded_python), '--version'],
                        stdout=subprocess.PIPE,  # 替换 capture_output
                        stderr=subprocess.PIPE,  # 替换 capture_output
                        universal_newlines=True,  # 替换 text 参数
                        timeout=10,
                        encoding='utf-8',
                        errors='ignore'
                    )
                    if result.returncode == 0:
                        version = result.stdout.strip()
                        print(f"✅ 找到内嵌 Python: {embedded_python} -> {version}")
                        print(f"🎯 使用内嵌 Python 环境 (独立运行)")
                        return str(embedded_python), str(embedded_python)
                    else:
                        raise SetupError(f"❌ 内嵌 Python 无法正常运行: {result.stderr}")
                except Exception as e:
                    raise SetupError(f"❌ 内嵌 Python 检测失败: {e}")
            else:
                raise SetupError(f"❌ 未找到内嵌 Python 环境: {embedded_python}\n请确保 python_linux 目录存在且包含完整的 Python 环境")

        # Windows 平台只使用内嵌 Python
        if self.platform == 'windows':
            embedded_python = self.script_dir / 'python_windows' / 'python.exe'
            if embedded_python.exists():
                try:
                    result = subprocess.run(
                        [str(embedded_python), '--version'],
                        stdout=subprocess.PIPE,  # 替换 capture_output
                        stderr=subprocess.PIPE,  # 替换 capture_output
                        universal_newlines=True,  # 替换 text 参数
                        timeout=10,
                        encoding='utf-8',
                        errors='ignore'
                    )
                    if result.returncode == 0:
                        version = result.stdout.strip()
                        print(f"✅ 找到内嵌 Python: {embedded_python} -> {version}")
                        print(f"🎯 使用内嵌 Python 环境 (独立运行)")
                        return str(embedded_python), str(embedded_python)
                    else:
                        raise SetupError(f"❌ 内嵌 Python 无法正常运行: {result.stderr}")
                except Exception as e:
                    raise SetupError(f"❌ 内嵌 Python 检测失败: {e}")
            else:
                raise SetupError(f"❌ 未找到内嵌 Python 环境: {embedded_python}\n请确保 python_windows 目录存在且包含完整的 Python 环境")
        
        # 非 Windows 平台的处理保持原样 (如果以后支持其他平台)
        raise SetupError("❌ 当前仅支持 Windows 和 Linux 平台的内嵌 Python 环境")
    
    def check_dependencies(self) -> List[str]:
        """检查并返回缺失的依赖包"""
        print("📦 检查依赖包...")
        
        required_packages = ['flask', 'werkzeug', 'requests', 'click']
        
        # Windows 平台使用内嵌 Python，始终安装所有依赖包确保环境完整
        if self.platform in ['windows', 'linux']:
            print("🔧 使用内嵌 Python 环境，将确保所有依赖包完整安装")
            return required_packages
        
        # 其他平台的处理 (目前不支持)
        missing_packages = []
        for package in required_packages:
            try:
                result = subprocess.run(
                    [self.python_exe, '-c', f'import {package}'],
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                if result.returncode == 0:
                    print(f"✅ {package} 已安装")
                else:
                    print(f"❌ {package} 未安装")
                    missing_packages.append(package)
            except Exception as e:
                print(f"❌ {package} 检查失败: {e}")
                missing_packages.append(package)
        
        return missing_packages
    
    def install_dependencies(self, packages: List[str]) -> bool:
        """安装缺失的依赖包"""
        if not packages:
            return True
        
        print(f"📥 安装依赖包: {', '.join(packages)}")
        
        # 尝试使用requirements.txt
        requirements_file = self.script_dir / 'requirements.txt'
        if requirements_file.exists():
            try:
                result = subprocess.run(
                    [self.python_exe, '-m', 'pip', 'install', '-r', str(requirements_file)],
                    stdout=subprocess.PIPE,  # 替换 capture_output
                    stderr=subprocess.PIPE,  # 替换 capture_output
                    check=True,
                    universal_newlines=True,  # 替换 text 参数
                    timeout=300,
                    encoding='utf-8',
                    errors='ignore'
                )
                print("✅ 依赖包安装成功")
                return True
            except subprocess.CalledProcessError as e:
                print(f"❌ 使用 requirements.txt 安装失败: {e.stderr}")
        
        # 逐个安装包
        for package in packages:
            try:
                print(f"📥 正在安装 {package}...")
                result = subprocess.run(
                    [self.python_exe, '-m', 'pip', 'install', package],
                    stdout=subprocess.PIPE,  # 替换 capture_output
                    stderr=subprocess.PIPE,  # 替换 capture_output
                    check=True,
                    universal_newlines=True,  # 替换 text 参数
                    timeout=120,
                    encoding='utf-8',
                    errors='ignore'
                )
                print(f"✅ {package} 安装成功")
            except subprocess.CalledProcessError as e:
                print(f"❌ {package} 安装失败: {e.stderr}")
                return False
            except subprocess.TimeoutExpired:
                print(f"❌ {package} 安装超时")
                return False
        
        return True
    
    def choose_install_directory(self) -> Path:
        """选择安装目录"""
        print("\n📁 选择安装目录:")
        
        # 推荐的安装位置
        if self.platform == 'windows':
            candidates = [
                Path.home() / 'AppData' / 'Local' / 'Airdrop',
                Path('C:/Program Files/Airdrop'),
                Path('C:/Airdrop'),
                Path.home() / 'Airdrop'
            ]
        elif self.platform == 'linux':
            candidates = [
                Path.home() / '.local' / 'share' / 'Airdrop',
                Path('/opt/Airdrop'),
                Path('/usr/local/share/Airdrop'),
                Path.home() / 'Airdrop'
            ]
        
        print("推荐安装位置:")
        for i, path in enumerate(candidates, 1):
            accessible = self._check_directory_writable(path)
            status = "✅ 可写" if accessible else "❌ 需要管理员权限"
            print(f"  {i}. {path} ({status})")
        
        print(f"  {len(candidates) + 1}. 自定义路径")
        
        while True:
            try:
                choice = input(f"\n请选择安装位置 (1-{len(candidates) + 1}) [1]: ").strip()
                if not choice:
                    choice = "1"
                
                choice_num = int(choice)
                
                if 1 <= choice_num <= len(candidates):
                    install_dir = candidates[choice_num - 1]
                    if self._check_directory_writable(install_dir):
                        return install_dir
                    else:
                        print(f"❌ 无法写入目录: {install_dir}")
                        print("请选择其他位置或以管理员身份运行")
                        continue
                
                elif choice_num == len(candidates) + 1:
                    custom_path = input("请输入自定义路径: ").strip()
                    if custom_path:
                        install_dir = Path(custom_path)
                        if self._check_directory_writable(install_dir):
                            return install_dir
                        else:
                            print(f"❌ 无法写入目录: {install_dir}")
                            continue
                
                else:
                    print("❌ 无效选择")
                    
            except ValueError:
                print("❌ 请输入数字")
            except KeyboardInterrupt:
                print("\n❌ 安装取消")
                sys.exit(1)
    
    def _check_directory_writable(self, path: Path) -> bool:
        """检查目录是否可写"""
        try:
            # 创建目录（如果不存在）
            path.mkdir(parents=True, exist_ok=True)
            
            # 测试写入权限
            test_file = path / '.write_test'
            test_file.write_text('test')
            test_file.unlink()
            
            return True
        except (PermissionError, OSError):
            return False
    
    def copy_files(self, install_dir: Path) -> bool:
        """复制程序文件到安装目录"""
        print(f"📂 复制文件到: {install_dir}")
        
        try:
            # 创建安装目录结构
            install_dir.mkdir(parents=True, exist_ok=True)
            (install_dir / 'server').mkdir(exist_ok=True)
            (install_dir / 'client').mkdir(exist_ok=True)
            
            # 复制文件
            files_to_copy = [
                ('server/server.py', 'server/server.py'),
                ('client/client.py', 'client/client.py'),
                ('requirements.txt', 'requirements.txt'),
                ('README.md', 'README.md'),
                ('airdrop.sh', 'airdrop.sh'),
            ]
            
            for src, dst in files_to_copy:
                src_path = self.script_dir / src
                dst_path = install_dir / dst
                
                if src_path.exists():
                    shutil.copy2(src_path, dst_path)
                    print(f"✅ 复制: {src} -> {dst}")
                else:
                    print(f"⚠️  跳过: {src} (文件不存在)")
            
            # 修改 airdrop.sh 以支持内嵌 Python
            airdrop_sh_path = install_dir / 'airdrop.sh'
            if self.platform == 'linux':
                airdrop_sh_path.chmod(0o755)  # 确保脚本可执行

            return True

        except Exception as e:
            print(f"❌ 复制文件失败: {e}")
            return False
    
    def create_launcher_script(self, install_dir: Path) -> bool:
        """创建启动脚本"""
        if self.platform == 'linux':
            print("📦 复制内嵌 Python 环境...")
            python_linux_src = self.script_dir / 'python_linux'
            python_linux_dst = install_dir / 'python_linux'

            if python_linux_src.exists():
                try:
                    if python_linux_dst.exists():
                        shutil.rmtree(python_linux_dst)
                    shutil.copytree(python_linux_src, python_linux_dst)
                    print(f"✅ 复制内嵌 Python: python_linux -> {python_linux_dst}")
                except Exception as e:
                    print(f"❌ 复制内嵌 Python 失败: {e}")
                    return False
            else:
                print(f"⚠️  未找到内嵌 Python 目录: {python_linux_src}")
                return False

            print("📝 Linux 平台无需额外启动脚本，使用 airdrop.sh 即可")
            return True

        # Windows 平台复制内嵌 Python
        if self.platform == 'windows':
            python_windows_src = self.script_dir / 'python_windows'
            if python_windows_src.exists():
                python_windows_dst = install_dir / 'python_windows'
                print(f"📦 复制内嵌 Python 环境...")

                # 使用 shutil.copytree 复制整个目录
                if python_windows_dst.exists():
                    shutil.rmtree(python_windows_dst)
                shutil.copytree(python_windows_src, python_windows_dst)
                print(f"✅ 复制内嵌 Python: python_windows -> {python_windows_dst}")

                # 更新 python_exe 路径为内嵌版本
                self.python_exe = str(python_windows_dst / 'python.exe')
                print(f"🐍 使用内嵌 Python: {self.python_exe}")
            else:
                print(f"⚠️  未找到内嵌 Python 目录: {python_windows_src}")
            
            return True
    
    def add_to_path(self, install_dir: Path) -> bool:
        """将安装目录添加到系统PATH"""
        if self.platform == 'linux':
            print("🔧 配置系统PATH和别名...")
            bashrc_path = Path.home() / '.bashrc'
            path_entry = f'export PATH="$PATH:{install_dir}"'
            alias_entry = f'alias ad="{install_dir}/airdrop.sh"'

            try:
                if bashrc_path.exists():
                    content = bashrc_path.read_text(encoding='utf-8')
                    updated_content = []
                    alias_found = False

                    for line in content.splitlines():
                        if line.strip().startswith('alias ad='):
                            alias_found = True
                            updated_content.append(alias_entry)
                        else:
                            updated_content.append(line)

                    if not alias_found:
                        updated_content.append(f'# Airdrop Alias\n{alias_entry}')

                    if path_entry not in content:
                        updated_content.append(f'# Airdrop PATH\n{path_entry}')

                    bashrc_path.write_text('\n'.join(updated_content), encoding='utf-8')
                    print(f"✅ 已更新 .bashrc，设置 PATH 和别名")
                else:
                    with bashrc_path.open('w', encoding='utf-8') as f:
                        f.write(f'# Airdrop PATH\n{path_entry}\n# Airdrop Alias\n{alias_entry}\n')
                    print(f"✅ 创建 .bashrc 并添加 PATH 和别名: {install_dir}")

                print("⚡ 请运行以下命令以立即生效:")
                print(f"source {bashrc_path}")
                return True

            except Exception as e:
                print(f"❌ 配置 PATH 和别名失败: {e}")
                print("请手动将以下内容添加到 .bashrc:")
                print(f"  {path_entry}")
                print(f"  {alias_entry}")
                return False

        print("🔧 配置系统PATH...")
        
        try:
            # 读取当前用户PATH
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, 'Environment', 0, winreg.KEY_ALL_ACCESS) as key:
                try:
                    current_path, _ = winreg.QueryValueEx(key, 'PATH')
                except FileNotFoundError:
                    current_path = ''
                
                # 检查是否已经在PATH中
                install_dir_str = str(install_dir)
                path_entries = [p.strip() for p in current_path.split(';') if p.strip()]
                
                if install_dir_str not in path_entries:
                    # 添加到PATH
                    new_path = ';'.join(path_entries + [install_dir_str])
                    winreg.SetValueEx(key, 'PATH', 0, winreg.REG_EXPAND_SZ, new_path)
                    print(f"✅ 已将 {install_dir} 添加到用户PATH")
                    return True
                else:
                    print(f"✅ {install_dir} 已在PATH中")
                    return True
                    
        except Exception as e:
            print(f"❌ 配置PATH失败: {e}")
            print("请手动将以下路径添加到系统PATH:")
            print(f"  {install_dir}")
            return False
    
    def create_config(self, install_dir: Path) -> bool:
        """创建初始配置"""
        print("⚙️  创建初始配置...")
        
        try:
            config_file = Path.home() / '.airdrop_config.json'
            if not config_file.exists():
                config = {
                    'servers': {},
                    'default_server': None,
                    'install_dir': str(install_dir)
                }
                
                with open(config_file, 'w', encoding='utf-8') as f:
                    json.dump(config, f, indent=2, ensure_ascii=False)
                
                print(f"✅ 创建配置文件: {config_file}")
            else:
                print(f"✅ 配置文件已存在: {config_file}")
            
            return True
            
        except Exception as e:
            print(f"❌ 创建配置失败: {e}")
            return False
    
    def setup_powershell_alias(self, install_dir: Path) -> bool:
        """配置PowerShell别名"""
        print("⚡ 配置 PowerShell 别名...")
        
        try:
            # 使用PowerShell $PROFILE 变量获取正确的配置文件路径
            print("🔍 获取 PowerShell 配置文件路径...")
            result = subprocess.run(
                ['powershell', '-Command', '$PROFILE'],
                capture_output=True,
                text=True,
                timeout=10,
                encoding='utf-8',
                errors='ignore'
            )
            
            if result.returncode != 0:
                print(f"❌ 无法获取 PowerShell 配置文件路径: {result.stderr}")
                return False
            
            profile_path = Path(result.stdout.strip())
            print(f"📍 PowerShell 配置文件路径: {profile_path}")
            
            # 如果配置文件不存在，创建它
            if not profile_path.exists():
                print("📝 创建 PowerShell 配置文件...")
                creation_result = subprocess.run(
                    ['powershell', '-Command', f'New-Item -Type File -Path "{profile_path}" -Force'],
                    capture_output=True,
                    text=True,
                    timeout=10,
                    encoding='utf-8',
                    errors='ignore'
                )
                
                if creation_result.returncode != 0:
                    print(f"❌ 创建配置文件失败: {creation_result.stderr}")
                    # 尝试手动创建
                    try:
                        profile_path.parent.mkdir(parents=True, exist_ok=True)
                        profile_path.write_text("# PowerShell 配置文件\n", encoding='utf-8')
                        print(f"✅ 手动创建配置文件: {profile_path}")
                    except Exception as e:
                        print(f"❌ 手动创建配置文件失败: {e}")
                        return False
                else:
                    print(f"✅ 配置文件创建成功: {profile_path}")
            
            # 别名命令 - 清除旧别名并设置新的指向 airdrop.bat
            alias_command = f'Set-Alias -Name ad -Value "{install_dir}\\airdrop.bat"'
            
            # 读取现有内容
            try:
                content = profile_path.read_text(encoding='utf-8')
            except Exception:
                content = "# PowerShell 配置文件\n"
            
            # 检查是否已经存在别名
            if 'Set-Alias -Name ad' not in content:
                # 添加清除旧别名和设置新别名的命令
                content += f"\n{alias_command}\n"
                profile_path.write_text(content, encoding='utf-8')
                print(f"✅ PowerShell 别名已添加到: {profile_path}")
            else:
                # 如果已存在，替换旧的别名设置
                lines = content.split('\n')
                new_lines = []
                skip_next = False
                
                for i, line in enumerate(lines):
                    if skip_next:
                        skip_next = False
                        continue
                        
                    if 'Set-Alias -Name ad' in line:
                        # 替换旧的别名设置
                        new_lines.append(alias_command)
                        # 如果下一行也是相关的注释，跳过
                        if i > 0 and lines[i-1].strip().startswith('# Airdrop'):
                            new_lines = new_lines[:-4] + [alias_command]
                    else:
                        new_lines.append(line)
                
                content = '\n'.join(new_lines)
                profile_path.write_text(content, encoding='utf-8')
                print(f"✅ PowerShell 别名已更新: {profile_path}")
            
            # 尝试为当前会话设置别名
            print("⚡ 显示当前会话别名设置命令...")
            print(f"请在安装完成后手动运行以下命令来设置当前会话别名:")
            print(f'if (Get-Alias -Name ad -ErrorAction SilentlyContinue) {{ Remove-Item Alias:ad }}')
            print(f'Set-Alias -Name ad -Value "{install_dir}\\airdrop.bat"')
            print()
            
            return True
                        
        except Exception as e:
            print(f"❌ PowerShell 别名配置失败: {e}")
            return False
    
    def test_installation(self, install_dir: Path) -> bool:
        """测试安装结果"""
        print("🧪 测试安装结果...")
        
        try:
            # 测试 airdrop.bat 命令，设置正确的编码
            result = subprocess.run(
                [str(install_dir / 'airdrop.bat'), 'help'],
                capture_output=True,
                text=True,
                timeout=30,
                encoding='utf-8',
                errors='ignore'  # 忽略编码错误
            )
            
            if result.returncode == 0:
                print("✅ airdrop.bat 命令测试成功")
                return True
            else:
                print(f"❌ airdrop.bat 命令测试失败: {result.stderr}")
                
                # 如果使用内嵌 Python，也测试直接调用 Python
                if (install_dir / 'python_windows' / 'python.exe').exists():
                    print("🔍 测试内嵌 Python...")
                    python_test = subprocess.run(
                        [str(install_dir / 'python_windows' / 'python.exe'), '--version'],
                        capture_output=True,
                        text=True,
                        timeout=10,
                        encoding='utf-8',
                        errors='ignore'
                    )
                    if python_test.returncode == 0:
                        print(f"✅ 内嵌 Python 正常: {python_test.stdout.strip()}")
                    else:
                        print(f"❌ 内嵌 Python 异常: {python_test.stderr}")
                
                return False
                
        except Exception as e:
            print(f"❌ 测试失败: {e}")
            return False
    
    def show_post_install_info(self, install_dir: Path):
        """显示安装后信息"""
        print("\n" + "=" * 50)
        print("🎉 安装完成!")
        print("=" * 50)
        print(f"📍 安装目录: {install_dir}")

        if self.platform == 'linux':
            print(f"🐍 Python 环境: 内嵌 Python (自包含)")
            print(f"📁 Python 路径: {install_dir / 'python_linux' / 'bin' / 'python3'}")
            print(f"⚙️  使用方法: {install_dir}/airdrop.sh")
        else:
            print(f"🐍 Python 环境: 内嵌 Python")
            print(f"📁 Python 路径: {install_dir / 'python_windows' / 'python.exe'}")
        
        print(f"⚙️  配置文件: {Path.home() / '.airdrop_config.json'}")
        print()
        print("📋 使用方法:")
        print("1. 启动服务器:")
        print(f"   {install_dir}\\airdrop.bat server C:\\temp\\files")
        print()
        print("2. 配置客户端:")
        print("   ad setup myserver http://localhost:8888 --default")
        print()
        print("3. 使用客户端:")
        print("   ad upload file.txt test/1/")
        print("   ad download test/1/file.txt ./")
        print("   ad list")
        print()
        print("💡 提示:")
        if self.platform == 'linux':
            print("- 使用内嵌 Python 环境，无需系统 Python 依赖")
        else:
            print("- 使用内嵌 Python 环境，无需系统 Python 依赖")
        print("- PowerShell 配置文件已自动更新，新的PowerShell会话将自动具有 'ad' 别名")
        print("- 当前会话请先清除旧别名: if (Get-Alias -Name ad -ErrorAction SilentlyContinue) { Remove-Item Alias:ad }")
        print("- 然后设置新别名: Set-Alias -Name ad -Value \"" + str(install_dir) + "\\airdrop.bat\"")
        print("- 在命令提示符中需要重新打开以使用 'ad' 命令")
        print("- 查看完整文档: README.md")
        print("- 快捷命令帮助: SHORTCUTS.md")
        print()
        
        print("🚀 立即设置当前会话别名:")
        print(f'if (Get-Alias -Name ad -ErrorAction SilentlyContinue) {{ Remove-Item Alias:ad }}')
        print(f'Set-Alias -Name ad -Value "{install_dir}\\airdrop.bat"')
        print()
    
    def install(self):
        """执行完整安装流程"""
        try:
            # 1. 检测Python
            python_cmd, python_exe = self.detect_python()
            self.python_exe = python_exe
            
            # 2. 检查依赖
            missing_deps = self.check_dependencies()
            if missing_deps:
                if not self.install_dependencies(missing_deps):
                    raise SetupError("依赖包安装失败")
            
            # 3. 选择安装目录
            self.install_dir = self.choose_install_directory()
            
            # 4. 复制文件
            if not self.copy_files(self.install_dir):
                raise SetupError("文件复制失败")
            
            # 5. 创建启动脚本
            if not self.create_launcher_script(self.install_dir):
                raise SetupError("创建启动脚本失败")
            
            # 6. 添加到PATH
            self.add_to_path(self.install_dir)
            
            # 7. 配置PowerShell别名
            if self.platform == 'windows':
                self.setup_powershell_alias(self.install_dir)
            
            # 8. 创建配置
            if not self.create_config(self.install_dir):
                raise SetupError("创建配置失败")
            
            # 9. 测试安装
            if not self.test_installation(self.install_dir):
                print("⚠️  安装完成但测试失败，请检查配置")
            
            # 10. 显示后续信息
            self.show_post_install_info(self.install_dir)
            
            # 如果是 Linux 平台，删除 python_linux 目录
            if self.platform == 'linux':
                python_linux_dir = self.script_dir / 'python_linux'
                if python_linux_dir.exists():
                    try:
                        shutil.rmtree(python_linux_dir)
                        print(f"✅ 已删除内嵌 Python 目录: {python_linux_dir}")
                    except Exception as e:
                        print(f"⚠️ 无法删除内嵌 Python 目录: {e}")
            
        except KeyboardInterrupt:
            print("\n❌ 安装被用户取消")
            sys.exit(1)
        except SetupError as e:
            print(f"\n❌ 安装失败: {e}")
            sys.exit(1)
        except Exception as e:
            print(f"\n❌ 安装出现未知错误: {e}")
            sys.exit(1)


def main():
    """主程序入口"""
    print("Airdrop 文件传输系统 - 安装程序 (内嵌 Python 版本)")
    print("Version: 1.0.0")
    print("Platform: Windows 和 Linux")
    print("Python: 内嵌独立环境")
    print()
    
    # 检查内嵌 Python 是否存在
    script_dir = Path(__file__).parent.resolve()
    embedded_python_windows = script_dir / 'python_windows' / 'python.exe'
    embedded_python_linux = script_dir / 'python_linux' / 'bin' / 'python3'
    
    if not embedded_python_windows.exists() and not embedded_python_linux.exists():
        print("❌ 错误: 未找到内嵌 Python 环境")
        print(f"📍 期望路径: {embedded_python_windows} 或 {embedded_python_linux}")
        print("💡 请确保 python_windows 或 python_linux 目录存在且包含完整的 Python 环境")
        print()
        input("按任意键退出...")
        sys.exit(1)
    
    if embedded_python_windows.exists():
        print(f"✅ 找到内嵌 Python: {embedded_python_windows}")
    if embedded_python_linux.exists():
        print(f"✅ 找到内嵌 Python: {embedded_python_linux}")
    print()
    
    # 开始安装
    setup = AirdropSetup()
    setup.install()


if __name__ == '__main__':
    main()
