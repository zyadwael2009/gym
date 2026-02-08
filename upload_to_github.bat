@echo off
echo ============================================
echo   GYM BACKEND - GITHUB UPLOAD HELPER
echo ============================================
echo.
echo This script will help you upload to GitHub.
echo.
echo BEFORE RUNNING THIS:
echo 1. Create a new repository on GitHub
echo 2. Copy the repository URL
echo.
set /p REPO_URL="Enter your GitHub repository URL (e.g., https://github.com/username/repo.git): "
echo.
echo Adding remote...
git remote add origin %REPO_URL%
echo.
echo Setting main branch...
git branch -M main
echo.
echo Pushing to GitHub...
git push -u origin main
echo.
echo ============================================
echo   DONE! Check your GitHub repository.
echo ============================================
pause

