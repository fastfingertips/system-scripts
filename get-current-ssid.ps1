# Get current Wi-Fi network SSID
$interfaces = netsh wlan show interfaces
$ssidLine = $interfaces | Select-String "SSID" | Where-Object { $_ -notmatch "BSSID" }
if ($ssidLine) {
    $ssid = ($ssidLine -split ":")[1].Trim()
    Write-Output $ssid
}
