@echo off
chcp 65001 >nul 2>&1

set SCRIPT_DIR=%~dp0

if not exist "%SCRIPT_DIR%python_windows\python.exe" (
    echo 错误: 未找到内嵌 Python 环境
    echo 期望路径: %SCRIPT_DIR%python_windows\python.exe
    echo 请重新安装 Airdrop
    pause
    exit /b 1
)

set PYTHON_WINDOWS=%SCRIPT_DIR%python_windows\python.exe
set SERVER_SCRIPT=%SCRIPT_DIR%server\server.py
set CLIENT_SCRIPT=%SCRIPT_DIR%client\client.py

set DEFAULT_ROOT=%TEMP%\airdrop_storage
set DEFAULT_HOST=0.0.0.0
set DEFAULT_PORT=8888

if "%1"=="" goto :help
if "%1"=="help" goto :help
if "%1"=="--help" goto :help
if "%1"=="-h" goto :help
if "%1"=="server" goto :server
if "%1"=="client" goto :client

echo 未知命令: %1
echo 使用 'airdrop.bat help' 查看帮助
exit /b 1

:help
echo.
echo "Airdrop 轻量级文件传输系统"
echo.
echo "用法:"
echo "  airdrop.bat server [选项] 根目录        启动文件传输服务器"
echo "  airdrop.bat client [命令] [选项]       运行客户端操作"
echo.
echo "服务器选项:"
echo "  --host HOST     绑定主机地址 (默认: 0.0.0.0 - 所有网卡)"
echo "  --port PORT     绑定端口号 (默认: 8888)"
echo "  --max-size MB   最大文件大小限制 (默认: 500MB)"
echo "  --debug         启用详细调试输出"
echo.
echo "客户端命令:"
echo "  setup URL                配置默认服务器地址"
echo "  servers                  显示当前服务器配置"
echo "  info                     查看服务器状态信息"
echo "  put 本地文件 远程路径      上传文件到服务器"
echo "  get 远程文件 本地路径      从服务器下载文件"
echo "  list [远程目录]           列出远程目录内容"
echo "  delete 远程文件           删除远程文件"
echo.
echo "常用示例:"
echo "  启动服务器:"
echo "    airdrop.bat server C:\temp\files"
echo "    airdrop.bat server --port 9999 C:\temp\files"
echo.
echo "  配置客户端:"
echo "    airdrop.bat client setup http://localhost:8888"
echo "    airdrop.bat client servers"
echo.
echo "  文件操作:"
echo "    airdrop.bat client put image.jpg photos/"
echo "    airdrop.bat client get photos/image.jpg downloaded.jpg"
echo "    airdrop.bat client list photos"
echo "    airdrop.bat client delete photos/old_image.jpg"
echo.
goto :eof

:server
shift
if "%1"=="" (
    echo 错误: 请指定根目录
    echo 用法: airdrop.bat server [选项] 根目录
    exit /b 1
)
echo 启动 Airdrop 服务器...
"%PYTHON_WINDOWS%" "%SERVER_SCRIPT%" %1 %2 %3 %4 %5 %6 %7 %8 %9
goto :eof

:client
shift
"%PYTHON_WINDOWS%" "%CLIENT_SCRIPT%" %1 %2 %3 %4 %5 %6 %7 %8 %9
goto :eof
