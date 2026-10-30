@echo off
cd /d "%~dp0\.."
call run.bat --vfs data\nested.json --script scripts\startup_full.txt
