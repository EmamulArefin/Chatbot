# Quick Deploy Script for Streamlit Cloud
# Run this script to prepare your project for Streamlit Cloud deployment

echo "🚀 Preparing Bangla PDF QA for Streamlit Cloud deployment..."

# Check if git is initialized
if [ ! -d ".git" ]; then
    echo "Initializing git repository..."
    git init
    git branch -M main
fi

# Add all files
echo "Adding files to git..."
git add .

# Commit changes
echo "Committing changes..."
git commit -m "Deploy: Bangla PDF QA ready for Streamlit Cloud"

echo "✅ Project is ready for deployment!"
echo ""
echo "Next steps:"
echo "1. Push to GitHub: git remote add origin YOUR_GITHUB_REPO_URL"
echo "2. Push code: git push -u origin main"
echo "3. Go to https://share.streamlit.io"
echo "4. Connect your GitHub repo"
echo "5. Set main file: app_deploy.py"
echo "6. Add your OpenAI API key in secrets"
echo ""
echo "🎉 Your app will be live at: https://your-app-name.streamlit.app"
