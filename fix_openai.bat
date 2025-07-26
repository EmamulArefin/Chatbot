@echo off
REM Quick fix script for OpenAI API compatibility
echo 🔧 Fixing OpenAI API compatibility...

REM Install/upgrade to the latest OpenAI package
pip install --upgrade "openai>=1.0.0"

echo ✅ OpenAI package updated successfully!
echo 🔄 Please restart your Streamlit application.
pause
