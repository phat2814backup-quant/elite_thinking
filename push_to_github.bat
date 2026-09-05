@echo off
chcp 65001 >nul
title Push Elite Thinking to GitHub

echo ========================================================
echo   HE THONG TU DUY TINH HOA (ELITE THINKING)
echo   Day ma nguon len GitHub de Deploy Streamlit Cloud
echo ========================================================
echo.

set REPO_URL=https://github.com/phat2814backup-quant/elite_thinking.git

:: Kiem tra Git
git --version >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo [LOI] Khong tim thay Git tren he thong!
    echo Vui long cai dat Git tai https://git-scm.com/
    pause
    exit /b 1
)

:: Kiem tra thu muc .git
if not exist ".git" (
    echo [+] Khoi tao Git repository...
    git init
    git branch -M main
)

:: Cau hinh khong escape ten file UTF-8
git config core.quotepath false

:: Kiem tra remote origin
git remote get-url origin >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo [+] Them remote origin: %REPO_URL%
    git remote add origin %REPO_URL%
) else (
    echo [*] Cap nhat remote origin: %REPO_URL%
    git remote set-url origin %REPO_URL%
)

:: Dam bao khong commit file nhay cam (.env, secrets.toml)
echo [*] Kiem tra trang thai tep tin...
git status --short

echo.
echo [+] Dang them tep vao Git...
git add .

echo.
set /p COMMIT_MSG="Nhap thong diep commit (Bam Enter de dung mac dinh): "
if "%COMMIT_MSG%"=="" (
    set COMMIT_MSG=Deploy Elite Thinking v2 with Supabase persistence
)

git commit -m "%COMMIT_MSG%"

echo.
echo [+] Dang day ma nguon len GitHub (branch: main)...
git push -u origin main

if %ERRORLEVEL% equ 0 (
    echo.
    echo ========================================================
    echo  [THANH CONG] Da day code len GitHub thanh cong!
    echo  URL Repo: https://github.com/phat2814backup-quant/elite_thinking
    echo.
    echo  Bay gio ban co the vao https://share.streamlit.io/
    echo  de Deploy ung dung:
    echo    - Repository: phat2814backup-quant/elite_thinking
    echo    - Branch: main
    echo    - Main file path: app.py
    echo ========================================================
) else (
    echo.
    echo [!] Co loi xay ra trong qua trinh push.
    echo Vui long kiem tra lai ket noi hoac quyen truy cap GitHub.
)

echo.
pause
