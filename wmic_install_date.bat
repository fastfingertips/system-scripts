@echo off
ver | find "Windows" > nul
if %ERRORLEVEL% NEQ 0 (
    echo This script can only be run on Windows.
    pause
    exit /b
)

for /f "tokens=2 delims==" %%I in ('wmic os get InstallDate /value') do set install_date=%%I

echo Original Install Date: %install_date%

pause
