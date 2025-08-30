# WLAN Password Viewer
# Displays saved Wi-Fi profiles and their passwords in a table format

Write-Host "WLAN PASSWORD VIEWER" -ForegroundColor Green
Write-Host "===================" -ForegroundColor Green
Write-Host ""

# Get all Wi-Fi profiles and extract passwords
try {
    $results = (netsh wlan show profiles) | Select-String "\:(.+)$" | ForEach-Object {
        $profileName = $_.Matches.Groups[1].Value.Trim()
        
        # Get profile details with password
        $profileDetails = netsh wlan show profile name="$profileName" key=clear
        $passwordLine = $profileDetails | Select-String "Key Content\W+\:(.+)$"
        
        if ($passwordLine) {
            $password = $passwordLine.Matches.Groups[1].Value.Trim()
        } else {
            $password = "No password / Open network"
        }
        
        [PSCustomObject]@{
            "Profile Name" = $profileName
            "Password" = $password
        }
    }
    
    if ($results) {
        $results | Format-Table -AutoSize
        Write-Host "Found $($results.Count) Wi-Fi profiles" -ForegroundColor Green
    } else {
        Write-Host "No Wi-Fi profiles found" -ForegroundColor Yellow
    }
} catch {
    Write-Host "ERROR: Failed to retrieve Wi-Fi profiles" -ForegroundColor Red
    Write-Host "Details: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host ""
Write-Host "Press any key to exit..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
