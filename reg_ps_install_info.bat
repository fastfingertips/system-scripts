@echo off
setlocal enabledelayedexpansion

:: Query registry for Windows installation info
for /f "tokens=2*" %%a in ('reg query "HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion" /v ProductName 2^>nul') do set "ProductName=%%b"
for /f "tokens=2*" %%a in ('reg query "HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion" /v DisplayVersion 2^>nul') do set "ReleaseID=%%b"
for /f "tokens=2*" %%a in ('reg query "HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion" /v CurrentBuild 2^>nul') do set "CurrentBuild=%%b"
for /f "tokens=2*" %%a in ('reg query "HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion" /v InstallDate 2^>nul') do set "InstallDate=%%b"

:: Convert install date from Unix timestamp to readable date
if defined InstallDate (
    :: Use PowerShell to calculate the actual date since CMD can't do date arithmetic
    for /f "delims=" %%a in ('powershell -command "[datetime]::ParseExact('01/01/1970', 'dd/MM/yyyy', $null).AddSeconds(%InstallDate%).ToString('dd/MM/yyyy HH:mm:ss')"') do set "formatted_date=%%a"
) else (
    set "formatted_date=Not Available"
)

:: Display results
echo Windows Installation Information:
echo Product Name: %ProductName%
echo Release ID: %ReleaseID%
echo Current Build: %CurrentBuild%
echo Install Date: %formatted_date%

pause
endlocal
