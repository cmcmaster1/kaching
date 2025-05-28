#!/bin/bash
# WordPress-Only Setup for KaChing on DigitalOcean
# Optimized for web hosting while KaChing agents run locally

set -e  # Exit on any error

echo "🌐 KaChing WordPress Hosting Setup"
echo "=================================="

# Configuration
WORDPRESS_USER="wordpress"
WORDPRESS_HOME="/var/www/comfortlife.tech"
DOMAIN="comfortlife.tech"

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

log_info "Setting up WordPress hosting for comfortlife.tech..."

# Update system
log_info "Updating system packages..."
apt update && apt upgrade -y

# Install LAMP stack + extras
log_info "Installing LAMP stack and utilities..."
apt install -y \
    apache2 \
    mysql-server \
    php8.1 \
    php8.1-mysql \
    php8.1-curl \
    php8.1-gd \
    php8.1-xml \
    php8.1-mbstring \
    php8.1-zip \
    php8.1-intl \
    php8.1-bcmath \
    libapache2-mod-php8.1 \
    curl \
    wget \
    unzip \
    certbot \
    python3-certbot-apache \
    fail2ban \
    ufw \
    htop \
    nano

# Configure firewall
log_info "Configuring firewall..."
ufw --force reset
ufw default deny incoming
ufw default allow outgoing
ufw allow ssh
ufw allow 80/tcp
ufw allow 443/tcp
ufw --force enable

# Configure fail2ban
log_info "Configuring fail2ban..."
systemctl enable fail2ban
systemctl start fail2ban

# Secure MySQL installation
log_info "Securing MySQL..."
mysql -e "ALTER USER 'root'@'localhost' IDENTIFIED WITH mysql_native_password BY 'secure_root_password_2024';"
mysql -e "DELETE FROM mysql.user WHERE User='';"
mysql -e "DELETE FROM mysql.user WHERE User='root' AND Host NOT IN ('localhost', '127.0.0.1', '::1');"
mysql -e "DROP DATABASE IF EXISTS test;"
mysql -e "DELETE FROM mysql.db WHERE Db='test' OR Db='test\\_%';"
mysql -e "FLUSH PRIVILEGES;"

# Create WordPress database
log_info "Creating WordPress database..."
WP_DB_PASSWORD=$(openssl rand -base64 32)
mysql -u root -psecure_root_password_2024 << EOF
CREATE DATABASE wordpress_comfortlife;
CREATE USER 'wp_user'@'localhost' IDENTIFIED BY '$WP_DB_PASSWORD';
GRANT ALL PRIVILEGES ON wordpress_comfortlife.* TO 'wp_user'@'localhost';
FLUSH PRIVILEGES;
EOF

# Download and install WordPress
log_info "Installing WordPress..."
cd /tmp
wget https://wordpress.org/latest.tar.gz
tar xzf latest.tar.gz

# Create document root
mkdir -p "$WORDPRESS_HOME"
cp -R wordpress/* "$WORDPRESS_HOME/"
chown -R www-data:www-data "$WORDPRESS_HOME"
chmod -R 755 "$WORDPRESS_HOME"

# Configure WordPress
log_info "Configuring WordPress..."
cd "$WORDPRESS_HOME"
cp wp-config-sample.php wp-config.php

# Generate WordPress salts
SALTS=$(curl -s https://api.wordpress.org/secret-key/1.1/salt/)

# Update wp-config.php
sed -i "s/database_name_here/wordpress_comfortlife/" wp-config.php
sed -i "s/username_here/wp_user/" wp-config.php
sed -i "s/password_here/$WP_DB_PASSWORD/" wp-config.php
sed -i "s/localhost/localhost/" wp-config.php

# Add salts
sed -i "/put your unique phrase here/d" wp-config.php
echo "$SALTS" >> wp-config.php

# Configure Apache
log_info "Configuring Apache..."
cat > /etc/apache2/sites-available/comfortlife.tech.conf << EOF
<VirtualHost *:80>
    ServerName comfortlife.tech
    ServerAlias www.comfortlife.tech
    DocumentRoot $WORDPRESS_HOME
    
    <Directory $WORDPRESS_HOME>
        AllowOverride All
        Require all granted
    </Directory>
    
    ErrorLog \${APACHE_LOG_DIR}/comfortlife_error.log
    CustomLog \${APACHE_LOG_DIR}/comfortlife_access.log combined
</VirtualHost>
EOF

# Enable site and modules
a2ensite comfortlife.tech.conf
a2enmod rewrite
a2dissite 000-default
systemctl reload apache2

# Create WordPress API user setup script
log_info "Creating WordPress API setup script..."
cat > /root/setup-wp-api.sh << 'EOF'
#!/bin/bash
# WordPress API Setup for KaChing Integration

echo "🔧 WordPress API Setup for KaChing"
echo "=================================="

echo "After WordPress installation is complete:"
echo "1. Go to: http://comfortlife.tech/wp-admin"
echo "2. Complete WordPress setup wizard"
echo "3. Install these plugins:"
echo "   - Application Passwords (for API access)"
echo "   - Yoast SEO (for SEO optimization)"
echo "   - WP REST API (if not built-in)"
echo ""
echo "4. Create API user:"
echo "   - Users → Add New"
echo "   - Username: kaching-api"
echo "   - Role: Editor"
echo "   - Generate Application Password"
echo ""
echo "5. Configure your local KaChing .env:"
echo "   WORDPRESS_URL=https://comfortlife.tech"
echo "   WORDPRESS_USERNAME=kaching-api"
echo "   WORDPRESS_PASSWORD=your_app_password"
echo ""
echo "6. Test API access from your local machine:"
echo "   curl -u kaching-api:app_password https://comfortlife.tech/wp-json/wp/v2/posts"
EOF

chmod +x /root/setup-wp-api.sh

# Create monitoring script
cat > /root/monitor-wordpress.sh << 'EOF'
#!/bin/bash
# WordPress Monitoring Script

echo "🌐 WordPress Hosting Status"
echo "=========================="

# Service status
echo "📊 Service Status:"
systemctl is-active apache2 && echo "✅ Apache: Running" || echo "❌ Apache: Stopped"
systemctl is-active mysql && echo "✅ MySQL: Running" || echo "❌ MySQL: Stopped"
systemctl is-active fail2ban && echo "✅ Fail2ban: Running" || echo "❌ Fail2ban: Stopped"

echo ""

# Resource usage
echo "💻 Resource Usage:"
echo "CPU: $(top -bn1 | grep "Cpu(s)" | awk '{print $2}' | cut -d'%' -f1)%"
echo "Memory: $(free -h | awk '/^Mem:/ {print $3 "/" $2}')"
echo "Disk: $(df -h / | awk 'NR==2 {print $3 "/" $2 " (" $5 " used)"}')"

echo ""

# WordPress status
echo "🌐 WordPress Status:"
if curl -s -o /dev/null -w "%{http_code}" http://comfortlife.tech | grep -q "200\|301\|302"; then
    echo "✅ Website: Accessible"
else
    echo "❌ Website: Not accessible"
fi

echo ""
echo "🔗 Access URLs:"
echo "Website: http://$(curl -s ifconfig.me)"
echo "WordPress Admin: http://$(curl -s ifconfig.me)/wp-admin"
echo "API Endpoint: http://$(curl -s ifconfig.me)/wp-json/wp/v2"
EOF

chmod +x /root/monitor-wordpress.sh

# Save database credentials
cat > /root/wordpress-credentials.txt << EOF
WordPress Database Credentials:
==============================
Database: wordpress_comfortlife
Username: wp_user
Password: $WP_DB_PASSWORD

MySQL Root Password: secure_root_password_2024

WordPress Directory: $WORDPRESS_HOME
Domain: $DOMAIN
EOF

chmod 600 /root/wordpress-credentials.txt

log_success "WordPress hosting setup complete!"
echo ""
echo "🎉 Next Steps:"
echo "1. Point your domain DNS to this server IP: $(curl -s ifconfig.me)"
echo "2. Complete WordPress setup: http://comfortlife.tech"
echo "3. Run API setup: /root/setup-wp-api.sh"
echo "4. Install SSL: certbot --apache -d comfortlife.tech -d www.comfortlife.tech"
echo "5. Monitor: /root/monitor-wordpress.sh"
echo ""
echo "📁 Important files:"
echo "- Database credentials: /root/wordpress-credentials.txt"
echo "- WordPress directory: $WORDPRESS_HOME"
echo "- Apache config: /etc/apache2/sites-available/comfortlife.tech.conf"
echo ""
log_warning "Remember to:"
log_warning "- Configure your domain DNS"
log_warning "- Complete WordPress installation wizard"
log_warning "- Set up SSL certificates"
log_warning "- Create WordPress API user for KaChing" 