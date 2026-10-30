@echo off
cd /d "%~dp0\.."
call run.bat --vfs data\simple.json --script scripts\stage3.txt
