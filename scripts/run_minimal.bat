@echo off
cd /d "%~dp0\.."
call run.bat --vfs data\minimal.json --script scripts\stage3.txt
