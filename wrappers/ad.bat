@echo off
setlocal

:: Get the directory where this script is located (User Scripts dir)
set "BIN_DIR=%~dp0"
:: Remove trailing backslash if present
set "BIN_DIR=%BIN_DIR:~0,-1%"

:: Define Installation Root
set "INSTALL_ROOT=%LOCALAPPDATA%\Airdrop"
set "PYTHON_EXE=%INSTALL_ROOT%\python_windows\python.exe"
set "CLIENT_SCRIPT=%INSTALL_ROOT%\client\client.py"
set "SERVER_SCRIPT=%INSTALL_ROOT%\server\server.py"
set "OSS_SCRIPT=%INSTALL_ROOT%\oss\oss_cli.py"

if not exist "%PYTHON_EXE%" (
    echo [ERROR] Python not found at: %PYTHON_EXE%
    echo Please reinstall Airdrop.
    exit /b 1
)

:: Dispatcher
if "%1"=="server" goto :server
if "%1"=="python" goto :python
if "%1"=="oss" goto :oss

:: Default to Client, but print paths if no args
if "%~1"=="" (
    echo [INFO] Airdrop Root: %INSTALL_ROOT%
    echo [INFO] Python Path:  %INSTALL_ROOT%\python_windows
    echo.
)

:client
"%PYTHON_EXE%" "%CLIENT_SCRIPT%" %*
goto :EOF

:server
shift
"%PYTHON_EXE%" "%SERVER_SCRIPT%" %1 %2 %3 %4 %5 %6 %7 %8 %9
goto :EOF

:oss
shift
"%PYTHON_EXE%" "%OSS_SCRIPT%" %1 %2 %3 %4 %5 %6 %7 %8 %9
goto :EOF

:python
shift
"%PYTHON_EXE%" %1 %2 %3 %4 %5 %6 %7 %8 %9
goto :EOF
