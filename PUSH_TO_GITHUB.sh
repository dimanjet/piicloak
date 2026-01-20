#!/bin/bash
# PIICloak - GitHub Push Script
# Replace YOUR_GITHUB_USERNAME with your actual GitHub username

# Set your GitHub username here:
GITHUB_USERNAME="YOUR_GITHUB_USERNAME"

# Verify we're in the right directory
if [ ! -f "setup.py" ] || [ ! -d ".git" ]; then
    echo "❌ Error: Please run this script from /var/www/dmitry/piicloak"
    exit 1
fi

# Add remote origin
echo "🔗 Adding GitHub remote..."
git remote add origin "https://github.com/${GITHUB_USERNAME}/piicloak.git"

# Verify remote was added
git remote -v

# Push to GitHub
echo ""
echo "🚀 Pushing to GitHub..."
echo "You may be prompted for your GitHub credentials."
echo ""
git push -u origin main

echo ""
echo "✅ Done! Your project is now on GitHub:"
echo "   https://github.com/${GITHUB_USERNAME}/piicloak"
echo ""
echo "🎯 Next steps:"
echo "   1. Visit your repo on GitHub"
echo "   2. Add topics: pii, data-privacy, presidio, flask, anonymization"
echo "   3. Star your own repo ⭐"
echo "   4. Share on social media!"
