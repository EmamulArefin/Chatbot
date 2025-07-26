# Quick fix script for OpenAI API compatibility
# Run this if you encounter OpenAI API errors

echo "🔧 Fixing OpenAI API compatibility..."

# Install/upgrade to the latest OpenAI package
pip install --upgrade openai>=1.0.0

echo "✅ OpenAI package updated successfully!"
echo "🔄 Please restart your Streamlit application."
