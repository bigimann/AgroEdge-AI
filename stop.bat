@echo off
REM AgroEdge AI — stop services started by start.bat
REM Closes the named console windows. If you started things manually
REM instead, just close those terminal windows directly.

taskkill /FI "WindowTitle eq AgroEdge Backend*" /T /F >nul 2>&1
taskkill /FI "WindowTitle eq AgroEdge Frontend*" /T /F >nul 2>&1

echo Stopped AgroEdge Backend and AgroEdge Frontend windows (if they were running).
