@echo off
set PYTHONIOENCODING=utf-8
set "PATH=%LOCALAPPDATA%ProgramsPythonPython312;%LOCALAPPDATA%ProgramsPythonPython312Scripts;%PATH%"
cd /d "%~dp0"
start "" pythonw gui.py
