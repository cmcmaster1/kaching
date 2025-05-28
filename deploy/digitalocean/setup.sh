#!/bin/bash
# KaChing DigitalOcean Deployment Script
# Automated setup for Ubuntu 22.04 LTS droplet

set -e  # Exit on any error

echo "🚀 KaChing DigitalOcean Deployment Starting..."
echo "================================================"

# Configuration
KACHING_USER="kaching"
KACHING_HOME="/opt/kaching"
PYTHON_VERSION="3.12"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if running as root
if [[ $EUID -ne 0 ]]; then
   log_error "This script must be run as root (use sudo)"
   exit 1
fi

log_info "Starting KaChing deployment on DigitalOcean droplet..."

# Update system
log_info "Updating system packages..."
apt update && apt upgrade -y

# Install essential packages
log_info "Installing essential packages..."
apt install -y \
    curl \
    wget \
    git \
    htop \
    nano \
    vim \
    unzip \
    software-properties-common \
    apt-transport-https \
    ca-certificates \
    gnupg \
    lsb-release \
    build-essential \
    python3-dev \
    python3-pip \
    python3-venv \
    nodejs \
    npm \
    nginx \
    certbot \
    python3-certbot-nginx \
    fail2ban \
    ufw

# Install Python 3.12 if not available
log_info "Setting up Python 3.12..."
if ! command -v python3.12 &> /dev/null; then
    add-apt-repository ppa:deadsnakes/ppa -y
    apt update
    apt install -y python3.12 python3.12-venv python3.12-dev
fi

# Install uv (Python package manager)
log_info "Installing uv package manager..."
curl -LsSf https://astral.sh/uv/install.sh | sh
export PATH="$HOME/.cargo/bin:$PATH"

# Create kaching user
log_info "Creating kaching user..."
if ! id "$KACHING_USER" &>/dev/null; then
    useradd -m -s /bin/bash "$KACHING_USER"
    usermod -aG sudo "$KACHING_USER"
    log_success "Created user: $KACHING_USER"
else
    log_warning "User $KACHING_USER already exists"
fi

# Create application directory
log_info "Setting up application directory..."
mkdir -p "$KACHING_HOME"
chown -R "$KACHING_USER:$KACHING_USER" "$KACHING_HOME"

# Install Ollama for local LLM
log_info "Installing Ollama..."
curl -fsSL https://ollama.ai/install.sh | sh
systemctl enable ollama
systemctl start ollama

# Wait for Ollama to start
sleep 5

# Pull the default model
log_info "Pulling Phi-3 Mini model..."
sudo -u "$KACHING_USER" ollama pull phi3:mini

# Setup firewall
log_info "Configuring firewall..."
ufw --force reset
ufw default deny incoming
ufw default allow outgoing
ufw allow ssh
ufw allow 80/tcp
ufw allow 443/tcp
ufw allow 11434/tcp  # Ollama
ufw --force enable

# Configure fail2ban
log_info "Configuring fail2ban..."
systemctl enable fail2ban
systemctl start fail2ban

# Setup nginx
log_info "Configuring nginx..."
systemctl enable nginx
systemctl start nginx

# Create nginx config for KaChing monitoring
cat > /etc/nginx/sites-available/kaching-monitor << 'EOF'
server {
    listen 80;
    server_name _;
    
    location /health {
        access_log off;
        return 200 "healthy\n";
        add_header Content-Type text/plain;
    }
    
    location /status {
        auth_basic "KaChing Status";
        auth_basic_user_file /etc/nginx/.htpasswd;
        
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
    
    location / {
        return 404;
    }
}
EOF

# Enable the site
ln -sf /etc/nginx/sites-available/kaching-monitor /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default
nginx -t && systemctl reload nginx

# Create monitoring password
log_info "Setting up monitoring authentication..."
echo "admin:$(openssl passwd -apr1 'kaching-monitor-2024')" > /etc/nginx/.htpasswd

# Setup log rotation
log_info "Configuring log rotation..."
cat > /etc/logrotate.d/kaching << 'EOF'
/opt/kaching/workspace/logs/*.log {
    daily
    missingok
    rotate 30
    compress
    delaycompress
    notifempty
    create 644 kaching kaching
    postrotate
        systemctl reload kaching-orchestrator || true
    endscript
}
EOF

# Create systemd service
log_info "Creating systemd service..."
cat > /etc/systemd/system/kaching-orchestrator.service << EOF
[Unit]
Description=KaChing Autonomous Affiliate Content System
After=network.target ollama.service
Wants=ollama.service

[Service]
Type=simple
User=$KACHING_USER
Group=$KACHING_USER
WorkingDirectory=$KACHING_HOME
Environment=PATH=/home/$KACHING_USER/.cargo/bin:/usr/local/bin:/usr/bin:/bin
Environment=PYTHONPATH=$KACHING_HOME
ExecStart=/home/$KACHING_USER/.cargo/bin/uv run python -m kaching.orchestrator
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal
SyslogIdentifier=kaching

# Resource limits
LimitNOFILE=65536
MemoryMax=2G
CPUQuota=80%

[Install]
WantedBy=multi-user.target
EOF

# Create health check service
cat > /etc/systemd/system/kaching-health.service << EOF
[Unit]
Description=KaChing Health Check Service
After=network.target

[Service]
Type=simple
User=$KACHING_USER
Group=$KACHING_USER
WorkingDirectory=$KACHING_HOME
Environment=PATH=/home/$KACHING_USER/.cargo/bin:/usr/local/bin:/usr/bin:/bin
ExecStart=/home/$KACHING_USER/.cargo/bin/uv run python -m kaching.tools.health_monitor
Restart=always
RestartSec=30
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF

# Enable services
systemctl daemon-reload
systemctl enable kaching-orchestrator
systemctl enable kaching-health

# Create deployment script for user
cat > "$KACHING_HOME/deploy.sh" << 'EOF'
#!/bin/bash
# KaChing Application Deployment Script
# Run this as the kaching user to deploy/update the application

set -e

REPO_URL="https://github.com/cmcmaster1/kaching.git"
KACHING_HOME="/opt/kaching"

cd "$KACHING_HOME"

echo "🔄 Deploying KaChing application..."

# Clone or update repository
if [ -d ".git" ]; then
    echo "📥 Updating existing repository..."
    git pull origin main
else
    echo "📥 Cloning repository..."
    git clone "$REPO_URL" .
fi

# Install dependencies
echo "📦 Installing dependencies..."
uv sync

# Copy configuration
if [ ! -f ".env" ]; then
    echo "⚙️ Creating environment configuration..."
    cp kaching/templates/digitalocean.json .kaching-config.json
    cp env.example .env
    echo "❗ Please edit .env file with your configuration"
fi

# Create workspace directories
echo "📁 Setting up workspace..."
mkdir -p workspace/{config,content,logs,schedule,secrets}

# Set permissions
chmod 755 workspace
chmod 700 workspace/secrets

# Create initial schedule
echo "📅 Creating initial schedule..."
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
        },
        {
            "name": "monthly_strategy_review",
            "schedule": "0 11 1 * *",
            "description": "Monthly strategy review on 1st of each month at 11 AM"
        }
    ]
}
SCHEDULE_EOF

echo "✅ Deployment complete!"
echo ""
echo "Next steps:"
echo "1. Edit .env file with your API keys and configuration"
echo "2. Test the system: uv run examples/end_to_end_demo.py"
echo "3. Start the service: sudo systemctl start kaching-orchestrator"
echo "4. Check status: sudo systemctl status kaching-orchestrator"
echo "5. View logs: sudo journalctl -u kaching-orchestrator -f"
EOF

chmod +x "$KACHING_HOME/deploy.sh"
chown "$KACHING_USER:$KACHING_USER" "$KACHING_HOME/deploy.sh"

# Create monitoring script
cat > "$KACHING_HOME/monitor.sh" << 'EOF'
#!/bin/bash
# KaChing Monitoring Script

echo "🔍 KaChing System Status"
echo "======================="

# Service status
echo "📊 Service Status:"
systemctl is-active kaching-orchestrator && echo "✅ Orchestrator: Running" || echo "❌ Orchestrator: Stopped"
systemctl is-active kaching-health && echo "✅ Health Monitor: Running" || echo "❌ Health Monitor: Stopped"
systemctl is-active ollama && echo "✅ Ollama: Running" || echo "❌ Ollama: Stopped"
systemctl is-active nginx && echo "✅ Nginx: Running" || echo "❌ Nginx: Stopped"

echo ""

# Resource usage
echo "💻 Resource Usage:"
echo "CPU: $(top -bn1 | grep "Cpu(s)" | awk '{print $2}' | cut -d'%' -f1)%"
echo "Memory: $(free -h | awk '/^Mem:/ {print $3 "/" $2}')"
echo "Disk: $(df -h / | awk 'NR==2 {print $3 "/" $2 " (" $5 " used)"}')"

echo ""

# Recent logs
echo "📝 Recent Activity:"
journalctl -u kaching-orchestrator --since "1 hour ago" --no-pager -n 5

echo ""
echo "🔗 Monitoring URLs:"
echo "Health Check: http://$(curl -s ifconfig.me)/health"
echo "Status Dashboard: http://$(curl -s ifconfig.me)/status (admin/kaching-monitor-2024)"
EOF

chmod +x "$KACHING_HOME/monitor.sh"
chown "$KACHING_USER:$KACHING_USER" "$KACHING_HOME/monitor.sh"

# Create backup script
cat > "$KACHING_HOME/backup.sh" << 'EOF'
#!/bin/bash
# KaChing Backup Script

BACKUP_DIR="/opt/kaching/backups"
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="kaching_backup_$DATE.tar.gz"

mkdir -p "$BACKUP_DIR"

echo "📦 Creating backup: $BACKUP_FILE"

tar -czf "$BACKUP_DIR/$BACKUP_FILE" \
    --exclude='workspace/logs' \
    --exclude='.git' \
    --exclude='__pycache__' \
    --exclude='.venv' \
    workspace/ \
    .env \
    .kaching-config.json

# Keep only last 7 backups
cd "$BACKUP_DIR"
ls -t kaching_backup_*.tar.gz | tail -n +8 | xargs -r rm

echo "✅ Backup complete: $BACKUP_DIR/$BACKUP_FILE"
echo "📊 Available backups:"
ls -lh kaching_backup_*.tar.gz
EOF

chmod +x "$KACHING_HOME/backup.sh"
chown "$KACHING_USER:$KACHING_USER" "$KACHING_HOME/backup.sh"

# Setup cron for backups
log_info "Setting up automated backups..."
(crontab -u "$KACHING_USER" -l 2>/dev/null; echo "0 2 * * * /opt/kaching/backup.sh >> /opt/kaching/workspace/logs/backup.log 2>&1") | crontab -u "$KACHING_USER" -

# Final setup
log_info "Final setup steps..."

# Create welcome message
cat > /etc/motd << 'EOF'

🚀 KaChing Autonomous Affiliate Content System
==============================================

📁 Application: /opt/kaching
👤 User: kaching
🔧 Commands:
   - Deploy/Update: sudo -u kaching /opt/kaching/deploy.sh
   - Monitor: sudo -u kaching /opt/kaching/monitor.sh
   - Backup: sudo -u kaching /opt/kaching/backup.sh
   - Logs: sudo journalctl -u kaching-orchestrator -f

🌐 Monitoring:
   - Health: http://YOUR_IP/health
   - Status: http://YOUR_IP/status (admin/kaching-monitor-2024)

📚 Documentation: /opt/kaching/docs/

EOF

log_success "DigitalOcean deployment setup complete!"
echo ""
echo "🎉 Next Steps:"
echo "1. Switch to kaching user: sudo -u kaching -i"
echo "2. Deploy application: /opt/kaching/deploy.sh"
echo "3. Configure environment: nano /opt/kaching/.env"
echo "4. Start services: sudo systemctl start kaching-orchestrator kaching-health"
echo "5. Monitor: /opt/kaching/monitor.sh"
echo ""
echo "🔗 Access monitoring at: http://$(curl -s ifconfig.me)/health"
echo "📊 Status dashboard: http://$(curl -s ifconfig.me)/status"
echo ""
echo "🔐 Default monitoring credentials:"
echo "   Username: admin"
echo "   Password: kaching-monitor-2024"
echo ""
log_warning "Remember to:"
log_warning "- Change monitoring password"
log_warning "- Configure your .env file"
log_warning "- Set up SSL certificates with certbot"
log_warning "- Configure your domain DNS"