#!/bin/bash
# Quick commit script for KaChing project

echo "🚀 KaChing Quick Commit & Push"
echo "=============================="

# Check if we're in a git repo
if [ ! -d ".git" ]; then
    echo "📁 Initializing git repository..."
    git init
fi

# Add all files
echo "📦 Adding files..."
git add .

# Commit
echo "💾 Committing changes..."
git commit -m "Initial KaChing deployment - autonomous affiliate content system

✅ Multi-agent system with Smolagents framework
✅ MCP integration with 200+ tools  
✅ Research & Content agents production ready
✅ DigitalOcean deployment scripts
✅ Configuration management for accessibility niche
✅ Health monitoring and security features

Ready for production deployment on comfortlife.tech"

# Check if remote exists
if ! git remote get-url origin >/dev/null 2>&1; then
    echo "🔗 Setting up GitHub remote..."
    echo "Please create a GitHub repository and run:"
    echo "git remote add origin https://github.com/cmcmaster1/kaching.git"
    echo "git branch -M main"
    echo "git push -u origin main"
else
    echo "🚀 Pushing to GitHub..."
    git push -u origin main
fi

echo "✅ Commit complete!"
echo ""
echo "🎯 Next steps:"
echo "1. Update GitHub URLs in deploy/digitalocean/setup.sh with your username"
echo "2. Run your DigitalOcean deployment"
echo "3. Configure WordPress on comfortlife.tech" 