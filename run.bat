echo off
echo Installing dependencies...
pip install -r requirements.txt

echo Setting up environment...
if not exist ".env" (
    echo Creating .env file from template...
    copy .env .env.example
)

echo Creating database...
mysql -u root -e "CREATE DATABASE IF NOT EXISTS sales_manager;"

echo Initializing database tables...
python init_db.py

echo.
echo ========================================
echo  IMPORTANT: Edit .env and change API_KEY
echo ========================================
echo.

echo Starting Sales Manager Agent...
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
pause
