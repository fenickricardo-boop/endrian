@echo off
setlocal
cd /d "%~dp0"
where python >nul 2>&1
if errorlevel 1 (
  echo Python no esta disponible en PATH.
  echo Instala Python y las dependencias indicadas en README_LOCAL_QA.md.
  pause
  exit /b 1
)
python start_lab_qa.py
if errorlevel 1 pause
endlocal
