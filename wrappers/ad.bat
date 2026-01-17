@echo off
setlocal

:: Get the directory where this script is located (User Scripts dir)
set "BIN_DIR=%~dp0"
:: Remove trailing backslash if present
set "BIN_DIR=%BIN_DIR:~0,-1%"

:: Define Installation Root relative to this script? 
:: No, because User/Scripts is usually C:\Users\xxx\Scripts
:: And App is in C:\Users\xxx\AppData\Local\Airdrop
:: They are not reliably relative.
:: So we use the standard env var %LOCALAPPDATA%

set "INSTALL_ROOT=%LOCALAPPDATA%\Airdrop"
set "PYTHON_EXE=%INSTALL_ROOT%\python_windows\python.exe"
set "CLIENT_SCRIPT=%INSTALL_ROOT%\client\client.py"
set "SERVER_SCRIPT=%INSTALL_ROOT%\server\server.py"

if not exist "%PYTHON_EXE%" (
    echo [ERROR] Python not found at: %PYTHON_EXE%
    echo Please reinstall Airdrop.
    exit /b 1
)

:: Dispatcher
if "%1"=="server" (
    :: Shift arguments to remove "server"
    shift
    :: Call Server
    :: Note: shift only affects %1..%9, but we can construct args list or just use %* if we don't mind "server" being there?
    :: No, server.py doesn't accept "server" as arg.
    :: We use a loop to reconstruct args.
    
    set "ARGS="
    :parse_args
    if "%~1"=="" goto :run_server
    set "ARGS=%ARGS% %1"
    shift
    goto :parse_args
    
    :run_server
    "%PYTHON_EXE%" "%SERVER_SCRIPT%" %ARGS%
) else (
    :: Call Client
    "%PYTHON_EXE%" "%CLIENT_SCRIPT%" %*
)
