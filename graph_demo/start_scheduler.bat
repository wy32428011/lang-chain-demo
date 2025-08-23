@echo off
chcp 65001 >nul
echo 正在启动股票分析定时任务...

REM 设置虚拟环境Python路径
set VENV_PYTHON=f:\langchian\demo\.venv\Scripts\python.exe

REM 检查Python是否安装
%VENV_PYTHON% --version >nul 2>&1
if errorlevel 1 (
    echo 错误: 未找到虚拟环境Python，请先激活虚拟环境
    pause
    exit /b 1
)

REM 检查schedule库是否安装
echo 检查schedule库...
%VENV_PYTHON% -c "import schedule" >nul 2>&1
if errorlevel 1 (
    echo schedule库未安装，正在安装...
    %VENV_PYTHON% -m pip install schedule
    if errorlevel 1 (
        echo 安装schedule库失败
        pause
        exit /b 1
    )
    echo schedule库安装成功
)

REM 检查akshare库是否安装
echo 检查akshare库...
%VENV_PYTHON% -c "import akshare" >nul 2>&1
if errorlevel 1 (
    echo akshare库未安装，正在安装...
    %VENV_PYTHON% -m pip install akshare
    if errorlevel 1 (
        echo 安装akshare库失败
        pause
        exit /b 1
    )
    echo akshare库安装成功
)

echo 启动定时任务...
cd /d "%~dp0"
%VENV_PYTHON% schedule_task.py

pause