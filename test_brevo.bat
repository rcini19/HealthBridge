@echo off
REM Quick test script for Brevo email configuration
REM This will activate your virtual environment and run the test

echo.
echo ========================================
echo   BREVO EMAIL CONFIGURATION TEST
echo ========================================
echo.

REM Check if virtual environment exists
if not exist "env\Scripts\activate.bat" (
    echo ERROR: Virtual environment not found!
    echo Please run setup.bat first to create the virtual environment.
    pause
    exit /b 1
)

echo Activating virtual environment...
call env\Scripts\activate.bat

echo.
echo Running Brevo email test...
echo.

python test_brevo_email.py

echo.
echo ========================================
echo   TEST COMPLETE
echo ========================================
echo.

deactivate
pause
