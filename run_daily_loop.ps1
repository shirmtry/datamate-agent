# run_daily_loop.ps1 — Tự chạy 1 lần/ngày (không cần Task Scheduler / quyền admin).
# Chạy: powershell -NoProfile -ExecutionPolicy Bypass -File run_daily_loop.ps1
$root = "C:\Users\dinht\Downloads\train"
$marker = Join-Path $root "logs_daily\last_run.txt"
New-Item -ItemType Directory -Force (Join-Path $root "logs_daily") | Out-Null

while ($true) {
    $today = (Get-Date).ToString("yyyy-MM-dd")
    $last = if (Test-Path $marker) { (Get-Content $marker -Raw).Trim() } else { "" }
    $hour = (Get-Date).Hour

    if ($last -ne $today -and $hour -ge 7) {
        Write-Host "[$(Get-Date -Format 'HH:mm')] chạy gen_daily cho $today"
        & powershell -NoProfile -ExecutionPolicy Bypass -File (Join-Path $root "run_daily.ps1")
        $today | Out-File -Encoding ascii $marker
    }
    Start-Sleep -Seconds 1800
}
