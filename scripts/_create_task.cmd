@echo off
set TASKNAME=PowerlandMonitor
set PS1=C:\Users\camil.sahnoune\competitive-intel\publish\scripts\run_monitor.ps1
schtasks /Create /TN "%TASKNAME%" /TR "powershell.exe -NoProfile -ExecutionPolicy Bypass -File \"%PS1%\"" /SC WEEKLY /D MON /ST 06:00 /F
echo exit=%errorlevel%
