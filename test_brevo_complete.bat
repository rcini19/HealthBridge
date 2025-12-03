@echo off
echo ========================================
echo HealthBridge Brevo Email Test
echo ========================================
echo.
echo This will test your Brevo email configuration
echo for expiry notifications and password reset.
echo.

REM Activate virtual environment
if exist "env\Scripts\activate.bat" (
    echo Activating virtual environment...
    call env\Scripts\activate.bat
) else (
    echo Warning: Virtual environment not found
    echo Running with system Python...
)

echo.
echo Running Brevo test suite...
echo.

python test_brevo_complete.py

echo.
echo ========================================
echo Test complete!
echo ========================================
pause
