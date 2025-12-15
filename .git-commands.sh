#!/bin/bash

# Source Tree - Git Setup Commands
# Run these commands to create and push to GitHub

echo "Creating Git repository..."

# Initialize git (if not already done)
git init

# Add all files
git add .

# Create initial commit
git commit -m "Initial commit: Source Tree knowledge network visualization"

echo ""
echo "✓ Local repository created"
echo ""
echo "Next steps:"
echo "1. Create a new GitHub repository at: https://github.com/new"
echo "2. Name it: sourcetree"
echo "3. Keep it public (or private if you prefer)"
echo "4. Do NOT initialize with README (we already have one)"
echo ""
echo "Then run these commands:"
echo ""
echo "  git remote add origin https://github.com/YOUR_USERNAME/sourcetree.git"
echo "  git branch -M main"
echo "  git push -u origin main"
echo ""
echo "After pushing, follow DEPLOY_RAILWAY.md for deployment instructions"
