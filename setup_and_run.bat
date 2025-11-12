@echo off
echo ========================================
echo Beverage Sales Forecasting Dashboard
echo Setup and Launch Script
echo ========================================
echo.

REM Check if virtual environment exists
if not exist "venv\" (
    echo Creating virtual environment...
    python -m venv venv
    echo.
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate
echo.

REM Install/Update requirements
echo Installing dependencies...
pip install -r requirements.txt
echo.

REM Launch the app
echo ========================================
echo Launching Streamlit Dashboard...
echo ========================================
echo.
echo The dashboard will open in your browser automatically.
echo Press Ctrl+C to stop the server.
echo.

streamlit run app.py

pause

