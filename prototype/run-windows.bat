@echo off
REM ============================================================
REM  WindWings 3D prototype - chay tren Windows
REM  Chi can bam dup file nay. Lan dau se tu cai thu vien.
REM ============================================================
chcp 65001 >nul
cd /d "%~dp0"

where node >nul 2>nul
if errorlevel 1 (
  echo.
  echo [!] Chua cai Node.js.
  echo     Tai ban LTS tai: https://nodejs.org/  roi chay lai file nay.
  echo.
  pause
  exit /b 1
)

if not exist "node_modules" (
  echo [1/2] Dang cai thu vien ^(lan dau, co the mat 1-2 phut^)...
  call npm install
  if errorlevel 1 (
    echo.
    echo [!] npm install loi. Kiem tra ket noi mang roi thu lai.
    pause
    exit /b 1
  )
)

echo.
echo [2/2] Dang mo game... trinh duyet se tu bat.
echo      De tat: dong cua so nay hoac bam Ctrl+C.
echo.
call npm run dev -- --open

pause
