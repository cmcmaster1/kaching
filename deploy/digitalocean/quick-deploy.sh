#!/bin/bash
# KaChing Quick Deploy Script (No GitHub Required)
# Run this after manually uploading files to /opt/kaching

set -e

KACHING_HOME="/opt/kaching"
KACHING_USER="kaching"

echo "🚀 KaChing Quick Deployment (Local Files)"
echo "========================================"

# Ensure we're in the right directory
cd "$KACHING_HOME"

# Set ownership
chown -R "$KACHING_USER:$KACHING_USER" "$KACHING_HOME"

# Install dependencies
echo "📦 Installing dependencies..."
sudo -u "$KACHING_USER" /home/$KACHING_USER/.cargo/bin/uv sync

# Copy configuration
if [ ! -f ".env" ]; then
    echo "⚙️ Creating environment configuration..."
    sudo -u "$KACHING_USER" cp kaching/templates/digitalocean.json .kaching-config.json
    sudo -u "$KACHING_USER" cp env.example .env
    echo "❗ Please edit .env file with your configuration"
fi

# Create workspace directories
echo "📁 Setting up workspace..."
sudo -u "$KACHING_USER" mkdir -p workspace/{config,content,logs,schedule,secrets}

# Set permissions
chmod 755 workspace
chmod 700 workspace/secrets

# Create initial schedule
echo "📅 Creating initial schedule..."
sudo -u "$KACHING_USER" cat > workspace/schedule/schedule.json << 'EOF'
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
        },
        {
            "name": "monthly_strategy_review",
            "schedule": "0 11 1 * *",
            "description": "Monthly strategy review on 1st of each month at 11 AM"
        }
    ]
}
EOF

echo "✅ Quick deployment complete!"
echo ""
echo "Next steps:"
echo "1. Edit .env file: nano .env"
echo "2. Test the system: sudo -u kaching uv run examples/end_to_end_demo.py"
echo "3. Start services: sudo systemctl start kaching-orchestrator kaching-health"
echo "4. Check status: sudo systemctl status kaching-orchestrator"
echo "5. View logs: sudo journalctl -u kaching-orchestrator -f" 