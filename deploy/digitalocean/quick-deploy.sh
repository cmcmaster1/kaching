#!/bin/bash
# Quick deployment script for KaChing on DigitalOcean
# Handles private GitHub repository authentication

# Check if stdin is a terminal (interactive) or pipe
if [[ ! -t 0 ]]; then
    echo "❌ This script requires interactive input and cannot be piped from curl."
    echo ""
    echo "💡 Please run it this way instead:"
    echo "wget https://raw.githubusercontent.com/cmcmaster1/kaching/main/deploy/digitalocean/quick-deploy.sh"
    echo "chmod +x quick-deploy.sh"
    echo "./quick-deploy.sh --yes"
    echo ""
    echo "Or for system setup only:"
    echo "curl -fsSL https://raw.githubusercontent.com/cmcmaster1/kaching/main/deploy/digitalocean/setup.sh | sudo bash"
    exit 1
fi

# Check for --yes flag to skip confirmation
SKIP_CONFIRM=false
if [[ "$1" == "--yes" || "$1" == "-y" ]]; then
    SKIP_CONFIRM=true
fi

echo "🚀 KaChing Quick Deployment"
echo "=========================="

# Check if running as root
if [[ $EUID -eq 0 ]]; then
   echo "❌ Don't run this as root. Run as regular user with sudo access."
   exit 1
fi

echo "📋 Pre-deployment checklist:"
echo "✅ DigitalOcean droplet created (Ubuntu 22.04 LTS)"
echo "✅ SSH access to droplet"
echo "✅ GitHub private repository: https://github.com/cmcmaster1/kaching"
echo ""

if [[ "$SKIP_CONFIRM" == "false" ]]; then
    echo "Continue with deployment? (y/N)"
    read -r confirm
    if [[ ! $confirm =~ ^[Yy]$ ]]; then
        echo "Deployment cancelled."
        exit 0
    fi
else
    echo "🚀 Auto-confirming deployment (--yes flag detected)"
fi

echo ""
echo "🚀 Starting system setup..."

# Download and run main setup script FIRST
curl -fsSL https://raw.githubusercontent.com/cmcmaster1/kaching/main/deploy/digitalocean/setup.sh | sudo bash

echo ""
echo "✅ System setup complete!"
echo ""

echo "🔐 GitHub Authentication Setup"
echo "Choose your preferred method:"
echo "1) Personal Access Token (Recommended)"
echo "2) SSH Key"
echo ""
echo "Enter choice (1-2):"
read -r auth_method

if [[ $auth_method == "1" ]]; then
    echo ""
    echo "📝 Personal Access Token Setup:"
    echo "1. Go to: https://github.com/settings/tokens"
    echo "2. Generate new token (classic)"
    echo "3. Select 'repo' scope"
    echo "4. Copy the token"
    echo ""
    echo "Have you created your token? (y/N)"
    read -r token_ready
    if [[ ! $token_ready =~ ^[Yy]$ ]]; then
        echo "Please create your token first, then run this script again."
        exit 0
    fi
    
    echo "GitHub Username:"
    read -r GITHUB_USER
    echo "Personal Access Token:"
    read -rs GITHUB_TOKEN
    echo ""
    
    # Test authentication
    echo "🔍 Testing GitHub authentication..."
    if curl -s -H "Authorization: token $GITHUB_TOKEN" https://api.github.com/repos/cmcmaster1/kaching >/dev/null; then
        echo "✅ GitHub authentication successful"
    else
        echo "❌ GitHub authentication failed. Please check your credentials."
        exit 1
    fi
    
elif [[ $auth_method == "2" ]]; then
    echo ""
    echo "🔑 SSH Key Setup:"
    echo "We'll generate an SSH key and you'll need to add it to GitHub."
    echo ""
    
    # Generate SSH key if it doesn't exist
    if [[ ! -f ~/.ssh/id_ed25519 ]]; then
        echo "Generating SSH key..."
        ssh-keygen -t ed25519 -C "kaching-deployment" -f ~/.ssh/id_ed25519 -N ""
    fi
    
    echo "📋 Copy this SSH public key to GitHub:"
    echo "https://github.com/settings/ssh/new"
    echo ""
    cat ~/.ssh/id_ed25519.pub
    echo ""
    echo "Have you added the SSH key to GitHub? (y/N)"
    read -r ssh_ready
    if [[ ! $ssh_ready =~ ^[Yy]$ ]]; then
        echo "Please add the SSH key to GitHub first, then run this script again."
        exit 0
    fi
    
    # Test SSH connection
    echo "🔍 Testing SSH connection to GitHub..."
    if ssh -T git@github.com 2>&1 | grep -q "successfully authenticated"; then
        echo "✅ SSH authentication successful"
    else
        echo "❌ SSH authentication failed. Please check your SSH key setup."
        exit 1
    fi
else
    echo "Invalid choice. Exiting."
    exit 1
fi

echo ""
echo "🔧 Now configuring application..."

# Switch to kaching user and deploy
sudo -u kaching bash << DEPLOY_EOF
cd /opt/kaching

# Set up git credentials based on chosen method
if [[ "$auth_method" == "1" ]]; then
    git clone "https://${GITHUB_USER}:${GITHUB_TOKEN}@github.com/cmcmaster1/kaching.git" .
elif [[ "$auth_method" == "2" ]]; then
    git clone "git@github.com:cmcmaster1/kaching.git" .
fi

# Install dependencies
echo "📦 Installing dependencies..."
uv sync

# Copy configuration templates
echo "⚙️ Setting up configuration..."
cp kaching/templates/digitalocean.json .kaching-config.json
cp env.example .env

# Create workspace directories
mkdir -p workspace/{config,content,logs,schedule,secrets}
chmod 755 workspace
chmod 700 workspace/secrets

# Create initial schedule
cat > workspace/schedule/schedule.json << 'SCHEDULE_EOF'
{
    "enabled": true,
    "tasks": [
        {
            "name": "daily_content_generation",
            "schedule": "0 9 * * 1,3,5",
            "description": "Generate content Monday, Wednesday, Friday at 9 AM"
        },
        {
            "name": "weekly_performance_review",
            "schedule": "0 10 * * 1",
            "description": "Weekly performance analysis every Monday at 10 AM"
        }
    ]
}
SCHEDULE_EOF

echo "✅ Application deployment complete!"
DEPLOY_EOF

echo ""
echo "🎉 KaChing deployment successful!"
echo ""
echo "📝 Next steps:"
echo "1. Configure your .env file: sudo -u kaching nano /opt/kaching/.env"
echo "2. Test the system: sudo -u kaching uv run examples/end_to_end_demo.py"
echo "3. Start services: sudo systemctl start kaching-orchestrator kaching-health"
echo "4. Monitor: /opt/kaching/monitor.sh"
echo ""
echo "🌐 Monitoring URLs:"
echo "Health: http://$(curl -s ifconfig.me)/health"
echo "Status: http://$(curl -s ifconfig.me)/status (admin/kaching-monitor-2024)"
echo ""
echo "🔐 Remember to:"
echo "- Configure your .env file with API keys"
echo "- Set up SSL certificates with certbot"
echo "- Configure your domain DNS" 