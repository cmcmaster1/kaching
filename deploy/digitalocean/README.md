# KaChing DigitalOcean Deployment Guide

Complete guide for deploying KaChing on DigitalOcean with automated setup scripts.

## 🚀 Quick Start

### 1. Create DigitalOcean Droplet

**Recommended Specs:**
- **OS**: Ubuntu 22.04 LTS
- **Size**: Basic Droplet, 2 GB RAM / 1 vCPU ($18/month)
- **Storage**: 50 GB SSD
- **Region**: Choose closest to your target audience

**Optional Upgrades:**
- 4 GB RAM / 2 vCPU ($36/month) for better performance
- Enable monitoring and backups

### 2. Initial Server Setup

```bash
# SSH into your droplet
ssh root@YOUR_DROPLET_IP

# Download the deployment script
wget https://raw.githubusercontent.com/cmcmaster1/kaching/main/deploy/digitalocean/quick-deploy.sh
chmod +x quick-deploy.sh

# Run the deployment
./quick-deploy.sh --yes

# Alternative: Download and run setup script directly
curl -fsSL https://raw.githubusercontent.com/cmcmaster1/kaching/main/deploy/digitalocean/setup.sh | bash
```

### 3. Deploy Application

```bash
# Switch to kaching user
sudo -u kaching -i

# Deploy the application
/opt/kaching/deploy.sh

# Configure environment
nano /opt/kaching/.env
```

### 4. Configure Environment

Edit `/opt/kaching/.env` with your settings:

```bash
# Core Settings
KACHING_NICHE="accessibility and comfort technology"
WORDPRESS_URL=https://comfortlife.tech

# API Keys
BRAVE_API_KEY="your_brave_api_key"
AMAZON_ASSOCIATE_ID="your_amazon_id"

# WordPress
WORDPRESS_USERNAME="your_wp_username"
WORDPRESS_PASSWORD="your_wp_app_password"
```

### 5. Start Services

```bash
# Start KaChing services
sudo systemctl start kaching-orchestrator
sudo systemctl start kaching-health

# Check status
sudo systemctl status kaching-orchestrator
sudo systemctl status kaching-health

# View logs
sudo journalctl -u kaching-orchestrator -f
```

## 📊 Monitoring & Management

### Health Monitoring

```bash
# System status
/opt/kaching/monitor.sh

# Web health check
curl http://YOUR_IP/health

# Status dashboard (requires auth)
# Username: admin
# Password: kaching-monitor-2024
curl -u admin:kaching-monitor-2024 http://YOUR_IP/status
```

### Log Management

```bash
# View orchestrator logs
sudo journalctl -u kaching-orchestrator -f

# View health monitor logs
sudo journalctl -u kaching-health -f

# Application logs
tail -f /opt/kaching/workspace/logs/kaching.log
```

### Backup & Recovery

```bash
# Manual backup
/opt/kaching/backup.sh

# Automated backups run daily at 2 AM
# View backup logs
tail -f /opt/kaching/workspace/logs/backup.log

# Restore from backup
cd /opt/kaching
tar -xzf backups/kaching_backup_YYYYMMDD_HHMMSS.tar.gz
```

## 🔧 Configuration Details

### System Services

- **kaching-orchestrator**: Main application service
- **kaching-health**: Health monitoring service
- **ollama**: Local LLM service
- **nginx**: Web server for monitoring
- **fail2ban**: Security service

### File Structure

```
/opt/kaching/
├── kaching/                 # Application code
├── workspace/               # Working directory
│   ├── config/             # Configuration files
│   ├── content/            # Generated content
│   ├── logs/               # Application logs
│   ├── schedule/           # Task scheduling
│   └── secrets/            # Secure credentials
├── deploy.sh               # Deployment script
├── monitor.sh              # Monitoring script
├── backup.sh               # Backup script
└── .env                    # Environment configuration
```

### Firewall Configuration

- **SSH (22)**: Secure shell access
- **HTTP (80)**: Web monitoring
- **HTTPS (443)**: Secure web (for SSL)
- **Ollama (11434)**: Local LLM API

## 🔒 Security Features

### Automatic Security

- **UFW Firewall**: Configured with minimal open ports
- **Fail2ban**: Protects against brute force attacks
- **User Isolation**: Application runs as dedicated user
- **Resource Limits**: Prevents resource exhaustion

### Manual Security Steps

```bash
# Change monitoring password
sudo htpasswd /etc/nginx/.htpasswd admin

# Setup SSL certificate (after domain configuration)
sudo certbot --nginx -d comfortlife.tech

# Update system packages
sudo apt update && sudo apt upgrade -y

# Review security logs
sudo journalctl -u fail2ban -f
```

## 🌐 Domain Configuration

### DNS Setup

Point your domain to the droplet IP:

```
A     @              YOUR_DROPLET_IP
A     www            YOUR_DROPLET_IP
CNAME *              comfortlife.tech
```

### SSL Certificate

```bash
# Install SSL certificate
sudo certbot --nginx -d comfortlife.tech -d www.comfortlife.tech

# Auto-renewal is configured automatically
sudo certbot renew --dry-run
```

## 📈 Performance Optimization

### Resource Monitoring

```bash
# Check resource usage
htop

# Monitor disk usage
df -h

# Check memory usage
free -h

# Monitor network
iftop
```

### Scaling Options

**Vertical Scaling (Resize Droplet):**
- Upgrade to 4 GB RAM / 2 vCPU for better performance
- Add more storage if needed

**Horizontal Scaling:**
- Deploy multiple droplets for different niches
- Use load balancer for high availability

## 🚨 Troubleshooting

### Common Issues

**Service Won't Start:**
```bash
# Check service status
sudo systemctl status kaching-orchestrator

# View detailed logs
sudo journalctl -u kaching-orchestrator -n 50

# Check configuration
/opt/kaching/monitor.sh
```

**High Resource Usage:**
```bash
# Check processes
top -u kaching

# Restart services
sudo systemctl restart kaching-orchestrator

# Check disk space
df -h
```

**Network Issues:**
```bash
# Check firewall
sudo ufw status

# Test Ollama
curl http://localhost:11434/api/version

# Test health endpoint
curl http://localhost/health
```

### Recovery Procedures

**Complete System Recovery:**
```bash
# Stop services
sudo systemctl stop kaching-orchestrator kaching-health

# Restore from backup
cd /opt/kaching
tar -xzf backups/kaching_backup_LATEST.tar.gz

# Restart services
sudo systemctl start kaching-orchestrator kaching-health
```

## 💰 Cost Optimization

### Monthly Costs

- **Basic Droplet**: $18/month (2 GB RAM)
- **Premium Droplet**: $36/month (4 GB RAM)
- **Backups**: $1.80/month (10% of droplet cost)
- **Monitoring**: Free
- **Load Balancer**: $12/month (if needed)

### Cost Saving Tips

1. **Start Small**: Begin with basic droplet, upgrade as needed
2. **Use Snapshots**: Create snapshots before major changes
3. **Monitor Usage**: Use built-in monitoring to optimize resources
4. **Scheduled Scaling**: Scale down during low-traffic periods

## 📞 Support

### Getting Help

1. **Check Logs**: Always start with log analysis
2. **Monitor Dashboard**: Use web monitoring interface
3. **System Status**: Run `/opt/kaching/monitor.sh`
4. **Documentation**: Review `/opt/kaching/docs/`

### Useful Commands

```bash
# Quick system check
/opt/kaching/monitor.sh

# Restart everything
sudo systemctl restart kaching-orchestrator kaching-health ollama nginx

# Update application
sudo -u kaching /opt/kaching/deploy.sh

# Emergency stop
sudo systemctl stop kaching-orchestrator kaching-health
```

---

## 🎯 Next Steps After Deployment

1. **Configure WordPress**: Set up comfortlife.tech with WordPress
2. **Apply for Affiliates**: Amazon Associates and other programs
3. **Test Content Generation**: Run end-to-end workflow
4. **Monitor Performance**: Watch logs and metrics
5. **Scale as Needed**: Upgrade resources based on usage

Your KaChing system is now ready for autonomous operation! 🚀 