@echo off
echo ========================================
echo Testing Dashboard Fix
echo ========================================
echo.
echo Step 1: Stopping any running backend...
taskkill /F /IM python.exe 2>nul
timeout /t 2 /nobreak >nul

echo.
echo Step 2: Starting backend...
start "Gym Backend" python app.py
timeout /t 5 /nobreak >nul

echo.
echo Step 3: Testing API...
python final_test.py

echo.
echo ========================================
echo Test Complete - Check results above
echo ========================================
pause
