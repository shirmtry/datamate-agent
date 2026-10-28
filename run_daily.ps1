param(
    [int]$MaxQuestions = 320
)
# Chạy 1 lượt sinh dữ liệu trong ngày (gọi bởi Task Scheduler lúc 07:30)
$ErrorActionPreference = "Continue"
$root = "C:\Users\dinht\Downloads\train"
$py = "C:\Users\dinht\AppData\Local\Python\pythoncore-3.14-64\python.exe"

$env:PYTHONIOENCODING = "utf-8"
$env:PYTHONPATH = "$root\vendor"

$logDir = Join-Path $root "logs_daily"
New-Item -ItemType Directory -Force $logDir | Out-Null
$log = Join-Path $logDir ("daily_{0}.log" -f (Get-Date -Format "yyyyMMdd_HHmm"))

Set-Location $root
"=== START $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss') ===" | Out-File -Encoding utf8 $log
& $py gen_daily.py --max-questions $MaxQuestions --retry-failed 2>&1 | Out-File -Append -Encoding utf8 $log
"=== END $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss') ===" | Out-File -Append -Encoding utf8 $log
