@echo off
title WLAN Profile Export Tool
setlocal enabledelayedexpansion

REM Export destination
set "EXPORT_DIR=%UserProfile%\Desktop\WLAN-Profiles"

REM Create export directory
if not exist "%EXPORT_DIR%" (
    mkdir "%EXPORT_DIR%"
    echo [INFO] Created directory: %EXPORT_DIR%
)

cls
echo.
echo  WLAN PROFILE EXPORT
echo  =======================
echo.
echo  Destination: %EXPORT_DIR%
echo.

echo.
echo  EXPORT PROCESS
echo  ==============
echo.

REM Export profiles with passwords
echo  Exporting Wi-Fi profiles with passwords...
netsh wlan export profile key=clear folder="%EXPORT_DIR%" 2>nul

if %errorLevel% == 0 (
    echo  [OK] Profiles exported with passwords
) else (
    echo  [ERROR] Export failed
    goto :error
)

echo.
echo  EXPORT COMPLETE
echo  ===============
echo.
echo  Files saved to: %EXPORT_DIR%
echo  Opening folder...
start "" "%EXPORT_DIR%"

echo.
echo  Exported Files:
for /f "tokens=*" %%f in ('dir "%EXPORT_DIR%\Wi-Fi-*.xml" /b 2^>nul') do (
    echo    - %%f
)
echo.
goto :end

:error
echo.
echo  ERROR
echo  =====
echo.
echo  [ERROR] Export failed
echo  TIP: Check permissions and try again
echo.
pause
exit /b 1

:end
echo.
echo  [SUCCESS] Export completed successfully!
echo  Check the opened folder for your files.
echo.
pause
exit /b 0
