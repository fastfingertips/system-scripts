@echo off
:: Check if the operating system is Windows
ver | find "Windows" > nul
if %ERRORLEVEL% NEQ 0 (
    echo This script can only be run on Windows.
    exit /b
)

:: Display the original installation date
systeminfo | find "Original Install Date"
