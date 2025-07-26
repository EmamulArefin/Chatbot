@echo off
REM Quick Deploy Script for Windows
echo 🚀 Preparing Bangla PDF QA for Streamlit Cloud deployment...

REM Check if git is initialized
if not exist ".git" (
    echo Initializing git repository...
    git init
    git branch -M main
)

REM Add all files
echo Adding files to git...
git add .

REM Commit changes
echo Committing changes...
git commit -m "Deploy: Bangla PDF QA ready for Streamlit Cloud"

echo ✅ Project is ready for deployment!
echo.
echo Next steps:
echo 1. Push to GitHub: git remote add origin YOUR_GITHUB_REPO_URL
echo 2. Push code: git push -u origin main
echo 3. Go to https://share.streamlit.io
echo 4. Connect your GitHub repo
echo 5. Set main file: app_deploy.py
echo 6. Add your OpenAI API key in secrets
echo.
echo 🎉 Your app will be live at: https://your-app-name.streamlit.app
pause
