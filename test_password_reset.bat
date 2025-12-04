@echo off
echo ========================================
echo Password Reset Email Test
echo ========================================
echo.

REM Activate virtual environment
if exist "env\Scripts\activate.bat" (
    call env\Scripts\activate.bat
)

python test_password_reset.py

echo.
pause
