@echo off
chcp 65001 >nul
title Export Project Context for AI Agent

echo ========================================================
echo   HE THONG TU DUY TINH HOA (ELITE THINKING FAMILY V2)
echo   Xuat toan bo cau truc, app, CSDL va tien do vao .md
echo   (Khong chua thong tin mat khau/API key nhay cam)
echo ========================================================
echo.

:: 1. Uu tien dung Python trong virtualenv neu co
if exist ".venv\Scripts\python.exe" (
    set "PYTHON_EXE=.venv\Scripts\python.exe"
    goto RUN_SCRIPT
)

if exist "venv\Scripts\python.exe" (
    set "PYTHON_EXE=venv\Scripts\python.exe"
    goto RUN_SCRIPT
)

:: 2. Neu khong co venv, dung python he thong
python --version >nul 2>&1
if %ERRORLEVEL% equ 0 (
    set "PYTHON_EXE=python"
    goto RUN_SCRIPT
)

echo [LOI] Khong tim thay Python tren he thong hoac .venv!
echo Vui long cai dat Python 3.10+ hoac khoi tao .venv.
echo.
pause
exit /b 1

:RUN_SCRIPT
echo [*] Dang thuc thi: %PYTHON_EXE% export_project_context.py
echo.
%PYTHON_EXE% export_project_context.py

if %ERRORLEVEL% neq 0 goto FAILED

echo.
echo ========================================================
echo  [THANH CONG] Da cap nhat file: PROJECT_CONTEXT.md
echo.
echo  Khi lam viec voi bat ky AI Agent nao:
echo  Gemini, Claude, ChatGPT, Cursor, Windsurf, Antigravity...
echo  Ban chi can yeu cau Agent:
echo.
echo  "Hay doc file PROJECT_CONTEXT.md de nam toan bo boi canh"
echo  "du an, vi tri app, co so du lieu va tien do cong viec."
echo ========================================================
goto DONE

:FAILED
echo.
echo [!] Co loi xay ra trong qua trinh xuat du lieu.

:DONE
echo.
pause
