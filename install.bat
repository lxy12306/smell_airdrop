@echo off
setlocal EnableDelayedExpansion
chcp 65001 >nul

:: --- 配置 ---
set "SCRIPT_DIR=%~dp0"
set "APP_NAME=Airdrop"
:: 安装目标目录
set "INSTALL_ROOT=%LOCALAPPDATA%\Airdrop"
:: 快捷方式目录
set "BIN_DIR=%USERPROFILE%\Scripts"
set "SHORTCUT_PATH=%BIN_DIR%\ad.bat"

:: 源目录
set "SRC_PYTHON=%SCRIPT_DIR%python_windows"
set "SRC_CLIENT=%SCRIPT_DIR%client"
set "SRC_SERVER=%SCRIPT_DIR%server"
set "SRC_OSS=%SCRIPT_DIR%oss"
set "SRC_WRAPPER=%SCRIPT_DIR%wrappers\ad.bat"
set "SRC_REQ=%SCRIPT_DIR%requirements.txt"

:: 目标目录
set "DST_PYTHON=%INSTALL_ROOT%\python_windows"
set "DST_CLIENT=%INSTALL_ROOT%\client"
set "DST_SERVER=%INSTALL_ROOT%\server"
set "DST_OSS=%INSTALL_ROOT%\oss"
set "DST_PYTHON_EXE=%DST_PYTHON%\python.exe"
set "DST_CLIENT_SCRIPT=%DST_CLIENT%\client.py"

:: 检查参数
if "%1"=="uninstall" goto :uninstall
if "%1"=="pack" goto :pack_python

:install
echo [INFO] Installing %APP_NAME%...

:: 0. 检查系统架构
if /i "%PROCESSOR_ARCHITECTURE%"=="ARM64" (
    echo [ERROR] ARM architecture is not currently supported on Windows.
    exit /b 1
)

:: 1. 检查内嵌 Python 源
set "SRC_PYTHON_ARCHIVE=%SCRIPT_DIR%python_windows_x86.tar.gz"

if not exist "%SRC_PYTHON%\python.exe" (
    if exist "%SRC_PYTHON_ARCHIVE%" (
        echo [INFO] Extracting python_windows_x86.tar.gz...
        :: Remove trailing backslash from SCRIPT_DIR for tar command consistency
        set "TAR_DIR=%SCRIPT_DIR:~0,-1%"
        tar -xzf "%SRC_PYTHON_ARCHIVE%" -C "!TAR_DIR!"
        set "CLEANUP_PYTHON=1"
    )
)

if not exist "%SRC_PYTHON%\python.exe" (
    echo [ERROR] Embedded Python not found at: "%SRC_PYTHON%"
    echo Please ensure you have the full installation package ^(python_windows folder or python_windows_x86.tar.gz^).
    exit /b 1
)

:: 2. 复制文件到安装目录
echo [INFO] Copying files to %INSTALL_ROOT%...
if not exist "%INSTALL_ROOT%" mkdir "%INSTALL_ROOT%"

:: 复制 Python 环境
echo   - Copying Python environment...
xcopy "%SRC_PYTHON%\*" "%DST_PYTHON%\" /E /I /Y /Q >nul
if errorlevel 1 (
    echo [ERROR] Failed to copy Python environment.
    exit /b 1
)

:: 复制客户端代码
echo   - Copying Client code...
xcopy "%SRC_CLIENT%\*" "%DST_CLIENT%\" /E /I /Y /Q >nul

:: 复制服务端代码
echo   - Copying Server code...
xcopy "%SRC_SERVER%\*" "%DST_SERVER%\" /E /I /Y /Q >nul

:: 复制 OSS 工具代码 (覆盖 OSS 目录，但排除 .env)
echo   - Copying OSS tools...
xcopy "%SRC_OSS%\*" "%DST_OSS%\" /E /I /Y /Q >nul
if exist "%DST_OSS%\.env" (
    del "%DST_OSS%\.env"
)


:: 3. 安装依赖 (如果 requirements.txt 存在)
if exist "%SRC_REQ%" (
    echo [INFO] Installing dependencies...
    copy /Y "%SRC_REQ%" "%INSTALL_ROOT%\" >nul
    "%DST_PYTHON_EXE%" -m pip install -r "%INSTALL_ROOT%\requirements.txt" --no-warn-script-location >nul 2>&1
)

:: 4. 创建快捷方式
if not exist "%BIN_DIR%" mkdir "%BIN_DIR%"
echo [INFO] Installing wrapper script...
copy /Y "%SRC_WRAPPER%" "%SHORTCUT_PATH%" >nul
echo [SUCCESS] Shortcut created at: "%SHORTCUT_PATH%"

:: 5. 更新环境 (PATH 和 别名)
call :update_env install

:: 6. 清理临时解压的文件
if defined CLEANUP_PYTHON (
    echo [INFO] Cleaning up extracted Python environment...
    if exist "%SRC_PYTHON%" rmdir /S /Q "%SRC_PYTHON%"
)

echo.
echo [DONE] Installation complete!
echo You may need to restart your terminal to use the 'ad' command.
goto :eof

:uninstall
echo [INFO] Uninstalling %APP_NAME%...

:: 1. 删除快捷方式
if exist "%SHORTCUT_PATH%" (
    del "%SHORTCUT_PATH%"
    echo [SUCCESS] Removed shortcut: "%SHORTCUT_PATH%"
)

:: 2. 删除安装文件
if exist "%INSTALL_ROOT%" (
    echo [INFO] Removing installation files...
    rmdir /S /Q "%INSTALL_ROOT%"
    echo [SUCCESS] Removed directory: "%INSTALL_ROOT%"
)

:: 3. 清理环境 (PATH 和 别名)
call :update_env uninstall

echo.
echo [DONE] Uninstallation complete.
goto :eof

:: --- 打包/更新 Python 环境 ---
:pack_python
echo [INFO] Updating Python Package (Pack Mode)...

:: 0. 检查系统架构
if /i "%PROCESSOR_ARCHITECTURE%"=="ARM64" (
    echo [ERROR] ARM architecture is not currently supported on Windows.
    exit /b 1
)

:: 1. 检查内嵌 Python 源
set "SRC_PYTHON_ARCHIVE=%SCRIPT_DIR%python_windows_x86.tar.gz"

:: 2. 解压 (如果目录不存在)
if not exist "%SRC_PYTHON%\python.exe" (
    if exist "%SRC_PYTHON_ARCHIVE%" (
        echo [INFO] Extracting archive...
        tar -xzf "%SRC_PYTHON_ARCHIVE%"
        set "CLEANUP_PYTHON=1"
    ) else (
        echo [ERROR] No python source or archive found "%SRC_PYTHON%" or "%SRC_PYTHON_ARCHIVE%".
        exit /b 1
    )
)

:: 3. 安装依赖
echo [INFO] Installing requirements to embedded Python...
"%SRC_PYTHON%\python.exe" -m pip install -r "%SRC_REQ%"
if errorlevel 1 (
    echo [ERROR] Pip install failed.
    exit /b 1
)

:: 4. 清理垃圾文件
echo [INFO] Cleaning __pycache__...
for /d /r "%SRC_PYTHON%" %%d in (__pycache__) do @if exist "%%d" rd /s /q "%%d"
for /r "%SRC_PYTHON%" %%f in (*.pyc) do @del "%%f"

:: 4. 重新打包
echo [INFO] Creating archive %SRC_PYTHON_ARCHIVE%...
if exist "%SRC_PYTHON_ARCHIVE%" (
    echo [INFO] Backing up old archive...
    move /Y "%SRC_PYTHON_ARCHIVE%" "%SRC_PYTHON_ARCHIVE%.bak" >nul
)

:: 注意: tar 在 Windows 上对路径比较敏感，确保在当前目录下操作
tar -czf "python_windows_x86.tar.gz" python_windows

echo [SUCCESS] Updated %SRC_PYTHON_ARCHIVE%
echo Size:
for %%I in ("%SRC_PYTHON_ARCHIVE%") do echo %%~zI bytes

:: 5. 清理 (如果此脚本解压了它)
if defined CLEANUP_PYTHON (
    echo [INFO] Cleaning up extracted Python environment...
    if exist "%SRC_PYTHON%" rmdir /S /Q "%SRC_PYTHON%"
)

goto :eof

:: --- 子程序: 更新环境变量和别名 ---
:update_env
set "ACTION=%1"
set "PS_SCRIPT=%TEMP%\airdrop_env_manager.ps1"
echo [INFO] Updating PATH and Aliases (%ACTION%)...

if exist "%PS_SCRIPT%" del "%PS_SCRIPT%"

:: 生成 PowerShell 脚本 (使用逐行写入以避免 Batch 块解析错误)
echo param($targetDir, $shortcutPath, $action) >> "%PS_SCRIPT%"
echo $targetDir = $targetDir.TrimEnd('\') >> "%PS_SCRIPT%"
echo $scope = 'User' >> "%PS_SCRIPT%"
echo. >> "%PS_SCRIPT%"
echo # --- 1. Manage PATH --- >> "%PS_SCRIPT%"
echo $oldPath = [Environment]::GetEnvironmentVariable('PATH', $scope) >> "%PS_SCRIPT%"
echo if ($oldPath -eq $null) { $oldPath = "" } >> "%PS_SCRIPT%"
echo $parts = $oldPath -split ';' ^| Where-Object { $_.Trim() -ne "" } >> "%PS_SCRIPT%"
echo. >> "%PS_SCRIPT%"
echo if ($action -eq 'install') { >> "%PS_SCRIPT%"
echo     $exists = $parts ^| Where-Object { $_.TrimEnd('\') -eq $targetDir } >> "%PS_SCRIPT%"
echo     if (-not $exists) { >> "%PS_SCRIPT%"
echo         $newPath = "$oldPath;$targetDir" >> "%PS_SCRIPT%"
echo         if ($oldPath -eq "") { $newPath = $targetDir } >> "%PS_SCRIPT%"
echo         [Environment]::SetEnvironmentVariable('PATH', $newPath, $scope) >> "%PS_SCRIPT%"
echo         Write-Host "[SUCCESS] Added $targetDir to PATH." >> "%PS_SCRIPT%"
echo     } else { >> "%PS_SCRIPT%"
echo         Write-Host "[INFO] $targetDir is already in PATH." >> "%PS_SCRIPT%"
echo     } >> "%PS_SCRIPT%"
echo } elseif ($action -eq 'uninstall') { >> "%PS_SCRIPT%"
echo     $newParts = $parts ^| Where-Object { $_.TrimEnd('\') -ne $targetDir } >> "%PS_SCRIPT%"
echo     $newPath = $newParts -join ';' >> "%PS_SCRIPT%"
echo     if ($newPath -ne $oldPath) { >> "%PS_SCRIPT%"
echo         [Environment]::SetEnvironmentVariable('PATH', $newPath, $scope) >> "%PS_SCRIPT%"
echo         Write-Host "[SUCCESS] Removed $targetDir from PATH." >> "%PS_SCRIPT%"
echo     } else { >> "%PS_SCRIPT%"
echo         Write-Host "[INFO] PATH is clean." >> "%PS_SCRIPT%"
echo     } >> "%PS_SCRIPT%"
echo } >> "%PS_SCRIPT%"
echo. >> "%PS_SCRIPT%"
echo # --- 2. Manage PowerShell Alias in Profile --- >> "%PS_SCRIPT%"
echo $profilePath = $PROFILE >> "%PS_SCRIPT%"
echo # 注意: 在 cmd 中调用 powershell 时 $PROFILE 可能指向 Documents\WindowsPowerShell\... >> "%PS_SCRIPT%"
echo if (-not (Test-Path $profilePath) -and $action -eq 'install') { >> "%PS_SCRIPT%"
echo     try { New-Item -Path $profilePath -ItemType File -Force ^| Out-Null } catch {} >> "%PS_SCRIPT%"
echo } >> "%PS_SCRIPT%"
echo. >> "%PS_SCRIPT%"
echo if (Test-Path $profilePath) { >> "%PS_SCRIPT%"
echo     $content = Get-Content $profilePath >> "%PS_SCRIPT%"
echo     # 清理旧别名 (Clean) >> "%PS_SCRIPT%"
echo     $newContent = $content ^| Where-Object { $_ -notmatch 'Set-Alias.*["'']ad["'']' } >> "%PS_SCRIPT%"
echo     $newContent ^| Set-Content $profilePath >> "%PS_SCRIPT%"
echo     Write-Host "[INFO] Cleaned old 'ad' aliases from Profile." >> "%PS_SCRIPT%"
echo. >> "%PS_SCRIPT%"
echo     if ($action -eq 'install') { >> "%PS_SCRIPT%"
echo         # 设置新别名 (Set) >> "%PS_SCRIPT%"
echo         # 使用单引号包裹 PowerShell 命令中的双引号 >> "%PS_SCRIPT%"
echo         Add-Content $profilePath "Set-Alias -Name ad -Value ""$shortcutPath""" >> "%PS_SCRIPT%"
echo         Write-Host "[SUCCESS] Added 'ad' alias to PowerShell Profile." >> "%PS_SCRIPT%"
echo     } >> "%PS_SCRIPT%"
echo } >> "%PS_SCRIPT%"

:: 执行 PowerShell 脚本
powershell -NoProfile -ExecutionPolicy Bypass -File "%PS_SCRIPT%" -targetDir "%BIN_DIR%" -shortcutPath "%SHORTCUT_PATH%" -action "%ACTION%"

:: 清理临时脚本
if exist "%PS_SCRIPT%" del "%PS_SCRIPT%"
exit /b
