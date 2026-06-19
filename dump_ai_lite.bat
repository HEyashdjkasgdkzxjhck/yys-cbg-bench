@echo off
chcp 65001 >nul 2>&1
set PYTHONIOENCODING=utf-8
set "PATH=%LOCALAPPDATA%\Programs\Python\Python312;%LOCALAPPDATA%\Programs\Python\Python312\Scripts;%PATH%"
cd /d "%~dp0code"

if "%~1"=="" (
    echo.
    set /p "URL=paste url: "
) else (
    set "URL=%~1"
)

echo.
python cbg_bench.py --dump-raw --dump-ai --lite -u "%URL%"
echo.
echo Done. Files:
echo   output\raw_cbg.json
echo   output\equip_desc.json
echo   output\ai_profile.json
echo.
pause
