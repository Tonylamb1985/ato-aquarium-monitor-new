#!/bin/bash
#
# ATO Aquarium Monitor - GitHub Deployment Script
# Author: Tony Lamb (tonylamb1985)
# 
# This script automatically uploads your ATO project to GitHub
#

set -e  # Exit on any error

# Configuration
GITHUB_USERNAME="tonylamb1985"
REPO_NAME="ato-aquarium-monitor"
REPO_URL="https://github.com/${GITHUB_USERNAME}/${REPO_NAME}.git"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo ""
echo "=================================================="
echo "  🐠 ATO Aquarium Monitor - GitHub Deploy"
echo "=================================================="
echo ""
echo "GitHub Username: ${GITHUB_USERNAME}"
echo "Repository: ${REPO_NAME}"
echo ""

# Check if we're in the right directory
if [ ! -f "ato_monitor.py" ]; then
    echo -e "${RED}❌ Error: ato_monitor.py not found!${NC}"
    echo "Please run this script from the ato-aquarium-monitor directory"
    exit 1
fi

# Check if git is installed
if ! command -v git &> /dev/null; then
    echo -e "${RED}❌ Error: git is not installed!${NC}"
    echo "Install git first:"
    echo "  sudo apt install git"
    exit 1
fi

echo -e "${BLUE}Checking repository status...${NC}"

# Check if already a git repository
if [ -d ".git" ]; then
    echo -e "${YELLOW}⚠️  Git repository already exists${NC}"
    read -p "Do you want to reset and start fresh? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        rm -rf .git
        echo -e "${GREEN}✅ Removed existing git repository${NC}"
    fi
fi

# Initialize git repository if needed
if [ ! -d ".git" ]; then
    echo -e "${BLUE}Initializing git repository...${NC}"
    git init
    git branch -M main
    echo -e "${GREEN}✅ Git repository initialized${NC}"
fi

# Configure git user (if not already configured globally)
if [ -z "$(git config user.name)" ]; then
    echo ""
    echo -e "${YELLOW}Git user not configured. Please enter your details:${NC}"
    read -p "Your name: " GIT_NAME
    read -p "Your email: " GIT_EMAIL
    git config user.name "$GIT_NAME"
    git config user.email "$GIT_EMAIL"
    echo -e "${GREEN}✅ Git user configured${NC}"
fi

# Check for GitHub authentication
echo ""
echo -e "${YELLOW}⚠️  GitHub Authentication Required${NC}"
echo ""
echo "You'll need to authenticate with GitHub. Choose your method:"
echo ""
echo "1. Personal Access Token (Recommended)"
echo "2. SSH Key"
echo "3. I'll do it manually later"
echo ""
read -p "Choose option (1/2/3): " AUTH_CHOICE

if [ "$AUTH_CHOICE" == "1" ]; then
    echo ""
    echo -e "${BLUE}Creating Personal Access Token:${NC}"
    echo "1. Go to: https://github.com/settings/tokens/new"
    echo "2. Note: 'ATO Aquarium Monitor'"
    echo "3. Expiration: 90 days (or your preference)"
    echo "4. Scopes: Check 'repo' (full control of private repositories)"
    echo "5. Click 'Generate token'"
    echo "6. COPY THE TOKEN (you'll only see it once!)"
    echo ""
    read -p "Press Enter when you have your token ready..."
    echo ""
    read -sp "Paste your GitHub token: " GITHUB_TOKEN
    echo ""
    
    # Configure git to use token
    REPO_URL="https://${GITHUB_TOKEN}@github.com/${GITHUB_USERNAME}/${REPO_NAME}.git"
    echo -e "${GREEN}✅ Token configured${NC}"
    
elif [ "$AUTH_CHOICE" == "2" ]; then
    echo ""
    echo -e "${BLUE}Using SSH authentication${NC}"
    REPO_URL="git@github.com:${GITHUB_USERNAME}/${REPO_NAME}.git"
    
    # Check if SSH key exists
    if [ ! -f "$HOME/.ssh/id_rsa.pub" ] && [ ! -f "$HOME/.ssh/id_ed25519.pub" ]; then
        echo -e "${YELLOW}No SSH key found. Generate one:${NC}"
        echo "  ssh-keygen -t ed25519 -C 'your_email@example.com'"
        echo "  cat ~/.ssh/id_ed25519.pub"
        echo "Then add to GitHub: https://github.com/settings/ssh/new"
        echo ""
        read -p "Press Enter when SSH key is added to GitHub..."
    fi
else
    echo -e "${YELLOW}You can add remote manually later with:${NC}"
    echo "  git remote add origin ${REPO_URL}"
fi

# Stage all files
echo ""
echo -e "${BLUE}Staging files...${NC}"
git add .

# Show what will be committed
echo ""
echo -e "${BLUE}Files to be committed:${NC}"
git status --short

# Create commit
echo ""
echo -e "${BLUE}Creating initial commit...${NC}"
git commit -m "Initial commit - v1.0.0 🐠

- Complete ATO monitoring system
- Temperature sensor with calibration
- Auto-calibration from refills
- Seasonal tracking
- 6-tab Home Assistant dashboard
- Comprehensive documentation
- Safety features and alerts

Ready for community use!"

echo -e "${GREEN}✅ Commit created${NC}"

# Check if repository exists on GitHub
echo ""
echo -e "${BLUE}Checking if GitHub repository exists...${NC}"

# Try to check if repo exists (will fail if it doesn't, that's OK)
if git ls-remote "$REPO_URL" &>/dev/null; then
    echo -e "${YELLOW}⚠️  Repository already exists on GitHub${NC}"
    read -p "Do you want to force push? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        FORCE_PUSH=true
    else
        echo -e "${RED}Aborted. Remove remote repository first or use force push.${NC}"
        exit 1
    fi
else
    echo -e "${YELLOW}Repository doesn't exist yet on GitHub${NC}"
    echo ""
    echo "Please create it now:"
    echo "1. Go to: https://github.com/new"
    echo "2. Repository name: ${REPO_NAME}"
    echo "3. Description: Enterprise-grade Auto Top-Off monitoring for aquariums"
    echo "4. Public or Private (your choice)"
    echo "5. ❌ Do NOT initialize with README (we have one)"
    echo "6. Click 'Create repository'"
    echo ""
    read -p "Press Enter when repository is created on GitHub..."
fi

# Add remote if not already added
if ! git remote | grep -q origin; then
    echo -e "${BLUE}Adding remote origin...${NC}"
    git remote add origin "$REPO_URL"
    echo -e "${GREEN}✅ Remote added${NC}"
fi

# Push to GitHub
echo ""
echo -e "${BLUE}Pushing to GitHub...${NC}"

if [ "$FORCE_PUSH" == "true" ]; then
    git push -u origin main --force
else
    git push -u origin main
fi

if [ $? -eq 0 ]; then
    echo ""
    echo -e "${GREEN}=================================================="
    echo "  ✅ SUCCESS! Repository uploaded to GitHub!"
    echo "==================================================${NC}"
    echo ""
    echo "🌐 View your repository at:"
    echo "   https://github.com/${GITHUB_USERNAME}/${REPO_NAME}"
    echo ""
    echo "🎯 Next steps:"
    echo "   1. Add topics/tags to your repository"
    echo "   2. Upload photos to images/ folder"
    echo "   3. Create your first release (v1.0.0)"
    echo "   4. Share on Reddit, forums, social media!"
    echo ""
    echo "📸 Add topics on GitHub:"
    echo "   raspberry-pi, home-assistant, aquarium, ato,"
    echo "   mqtt, python, automation, monitoring, iot"
    echo ""
    echo "🌟 Don't forget to star your own repository!"
    echo ""
else
    echo ""
    echo -e "${RED}=================================================="
    echo "  ❌ Error pushing to GitHub"
    echo "==================================================${NC}"
    echo ""
    echo "Common issues:"
    echo "1. Authentication failed - check token or SSH key"
    echo "2. Repository doesn't exist - create it first"
    echo "3. Network issue - check internet connection"
    echo ""
    echo "Try manual push:"
    echo "  git push -u origin main"
    echo ""
    exit 1
fi

# Create first release (optional)
echo ""
read -p "Do you want to create a release tag (v1.0.0)? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    git tag -a v1.0.0 -m "Version 1.0.0 - Initial Release

🎉 First stable release of ATO Aquarium Monitor!

Features:
- Auto-calibration system
- Temperature monitoring with DS18B20
- Seasonal tracking (Spring/Summer/Autumn/Winter)
- 6-tab Home Assistant dashboard
- Pump control via relay
- Multiple safety features
- Comprehensive documentation

Tested on: Raspberry Pi 3 Model B
Compatible with: Home Assistant 2024.1+"

    git push origin v1.0.0
    
    echo ""
    echo -e "${GREEN}✅ Release tag created!${NC}"
    echo "Create the release on GitHub:"
    echo "1. Go to: https://github.com/${GITHUB_USERNAME}/${REPO_NAME}/releases/new"
    echo "2. Choose tag: v1.0.0"
    echo "3. Release title: v1.0.0 - Initial Release"
    echo "4. Add description from tag message"
    echo "5. Click 'Publish release'"
fi

echo ""
echo -e "${BLUE}=================================================="
echo "  🚀 Deployment Complete!"
echo "==================================================${NC}"
echo ""
echo "Repository: https://github.com/${GITHUB_USERNAME}/${REPO_NAME}"
echo ""
echo "Happy fishkeeping! 🐠💙"
echo ""
