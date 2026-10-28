@echo off
rem Chạy tự động mỗi ngày (mở cửa sổ ẩn). Có thể copy file này vào Startup:
rem   %APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup
start "" /min powershell -NoProfile -WindowStyle Hidden -ExecutionPolicy Bypass -File "%~dp0run_daily_loop.ps1"
