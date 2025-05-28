# WordPress Setup Guide for KaChing

This guide walks you through setting up WordPress hosting and configuration for the KaChing autonomous affiliate content system.

## 🎯 Overview

The KaChing Publishing Agent requires a WordPress site with REST API access to automatically publish content with affiliate links and SEO optimization.

## 📋 Requirements

- Domain name (.com recommended for SEO)
- WordPress hosting with REST API support
- SSL certificate (HTTPS)
- WordPress application password for API access

## 🚀 Quick Setup Options

### Option 1: Managed WordPress Hosting (Recommended)

**Best for**: Beginners, hands-off management

**Recommended Providers:**
- **WP Engine** (AU $35/month) - Premium managed hosting
- **SiteGround** (AU $15/month) - Good balance of features/price
- **Kinsta** (AU $45/month) - High-performance hosting

**Pros:**
- Automatic updates and security
- Built-in caching and CDN
- WordPress-optimized servers
- Expert support

### Option 2: Shared Hosting

**Best for**: Budget-conscious, basic needs

**Recommended Providers:**
- **Namecheap** (AU $8/month) - Budget-friendly
- **Bluehost** (AU $12/month) - WordPress recommended
- **HostGator** (AU $10/month) - Reliable shared hosting

**Pros:**
- Very affordable
- Easy WordPress installation
- Good for starting out

### Option 3: VPS/Cloud Hosting

**Best for**: Technical users, scalability

**Recommended Providers:**
- **DigitalOcean** (AU $8/month) - Developer-friendly
- **Vultr** (AU $6/month) - High performance
- **Linode** (AU $7/month) - Reliable cloud hosting

**Pros:**
- Full control over server
- Highly scalable
- Cost-effective for multiple sites

## 🛠️ Step-by-Step Setup

### Step 1: Domain Registration

1. **Choose a domain name**
   ```
   Examples for arthritis niche:
   - arthritis-kitchen-helper.com
   - easy-grip-tools.com
   - joint-friendly-cooking.com
   ```

2. **Register domain** (AU $15-20/year)
   - Use Namecheap, GoDaddy, or your hosting provider
   - Enable domain privacy protection
   - Set up auto-renewal

### Step 2: WordPress Hosting Setup

#### For Managed Hosting (SiteGround Example):

1. **Sign up for hosting**
   - Choose "StartUp" plan (AU $15/month)
   - Select your domain during signup
   - Choose data center closest to Australia

2. **Install WordPress**
   - Use one-click WordPress installation
   - Choose strong admin credentials
   - Note down login details

3. **Configure basic settings**
   - Set timezone to Australia
   - Configure permalinks to "Post name"
   - Install SSL certificate (usually automatic)

#### For VPS Hosting (DigitalOcean Example):

1. **Create droplet**
   ```bash
   # Choose Ubuntu 22.04 LTS
   # Select $8/month plan (1GB RAM)
   # Add SSH key for security
   ```

2. **Install WordPress stack**
   ```bash
   # Connect via SSH
   ssh root@your-server-ip
   
   # Install LAMP stack
   apt update && apt upgrade -y
   apt install apache2 mysql-server php php-mysql php-curl php-gd php-mbstring php-xml php-zip -y
   
   # Download and configure WordPress
   cd /var/www/html
   wget https://wordpress.org/latest.tar.gz
   tar xzf latest.tar.gz
   mv wordpress/* .
   rm -rf wordpress latest.tar.gz
   
   # Set permissions
   chown -R www-data:www-data /var/www/html
   chmod -R 755 /var/www/html
   ```

3. **Configure database**
   ```bash
   mysql -u root -p
   CREATE DATABASE kaching_wp;
   CREATE USER 'kaching_user'@'localhost' IDENTIFIED BY 'strong_password';
   GRANT ALL PRIVILEGES ON kaching_wp.* TO 'kaching_user'@'localhost';
   FLUSH PRIVILEGES;
   EXIT;
   ```

### Step 3: WordPress Configuration

1. **Complete WordPress installation**
   - Visit your domain in browser
   - Follow WordPress setup wizard
   - Use database credentials from Step 2

2. **Install essential plugins**
   ```
   Required plugins:
   - Yoast SEO (for meta data management)
   - WP REST API Authentication (for secure API access)
   - Classic Editor (for better content control)
   
   Recommended plugins:
   - UpdraftPlus (backups)
   - Wordfence Security (security)
   - WP Rocket (caching)
   ```

3. **Choose SEO-friendly theme**
   ```
   Recommended themes:
   - Astra (free, fast, SEO-optimized)
   - GeneratePress (lightweight, customizable)
   - Neve (modern, affiliate-friendly)
   ```

### Step 4: REST API Configuration

1. **Enable REST API** (usually enabled by default)
   - Go to Settings > Permalinks
   - Ensure "Post name" is selected
   - Save changes

2. **Create application password**
   ```
   WordPress Admin > Users > Your Profile
   Scroll to "Application Passwords"
   Name: "KaChing Publishing Agent"
   Click "Add New Application Password"
   Copy the generated password (save securely!)
   ```

3. **Test REST API access**
   ```bash
   # Test basic API access
   curl https://yourdomain.com/wp-json/wp/v2/posts
   
   # Test authenticated access
   curl -u "username:application_password" \
        https://yourdomain.com/wp-json/wp/v2/posts
   ```

### Step 5: KaChing Integration

1. **Update environment variables**
   ```bash
   # Add to your .env file
   WORDPRESS_URL=https://yourdomain.com
   WORDPRESS_USERNAME=your_admin_username
   WORDPRESS_PASSWORD=your_application_password
   ```

2. **Test publishing agent**
   ```bash
   # Run publishing agent demo
   uv run examples/publishing_agent_demo.py
   ```

3. **Configure categories and tags**
   ```
   Create categories in WordPress:
   - Reviews
   - Guides
   - Comparisons
   - Tips
   
   Common tags:
   - arthritis
   - kitchen-tools
   - ergonomic
   - cooking
   - accessibility
   ```

## 🔧 Advanced Configuration

### SSL Certificate Setup

For VPS hosting, install Let's Encrypt:
```bash
apt install certbot python3-certbot-apache -y
certbot --apache -d yourdomain.com -d www.yourdomain.com
```

### Performance Optimization

1. **Enable caching**
   - Install WP Rocket or W3 Total Cache
   - Configure browser caching
   - Enable GZIP compression

2. **CDN setup**
   - Sign up for Cloudflare (free tier)
   - Update nameservers
   - Configure caching rules

3. **Image optimization**
   - Install Smush or ShortPixel
   - Enable WebP format
   - Set up lazy loading

### Security Hardening

1. **Basic security measures**
   ```bash
   # Hide wp-admin from unauthorized access
   # Add to .htaccess:
   <Files wp-login.php>
   order deny,allow
   deny from all
   allow from YOUR_IP_ADDRESS
   </Files>
   ```

2. **Install security plugin**
   - Wordfence Security (recommended)
   - Configure firewall rules
   - Enable two-factor authentication

## 📊 Budget Breakdown

| Item | Cost (AU$/month) | Annual Cost |
|------|------------------|-------------|
| Domain | $1.25 | $15 |
| Shared Hosting | $12 | $144 |
| SSL Certificate | $0 (free) | $0 |
| **Total Basic** | **$13.25** | **$159** |
| | | |
| Managed Hosting | $35 | $420 |
| Premium Plugins | $10 | $120 |
| **Total Premium** | **$46.25** | **$555** |

## 🧪 Testing Checklist

Before going live:

- [ ] WordPress admin access working
- [ ] REST API responding correctly
- [ ] Application password authentication working
- [ ] SSL certificate installed and working
- [ ] Basic SEO plugin configured
- [ ] Test post creation via API
- [ ] Affiliate link insertion working
- [ ] Meta data management functional

## 🚨 Troubleshooting

### Common Issues

1. **REST API not accessible**
   ```
   Solution: Check permalinks, ensure mod_rewrite enabled
   ```

2. **Authentication failing**
   ```
   Solution: Verify application password, check username
   ```

3. **SSL certificate issues**
   ```
   Solution: Force HTTPS in WordPress settings
   ```

4. **Plugin conflicts**
   ```
   Solution: Deactivate plugins one by one to identify conflicts
   ```

## 📞 Support Resources

- **WordPress.org Documentation**: https://wordpress.org/support/
- **REST API Handbook**: https://developer.wordpress.org/rest-api/
- **Hosting Provider Support**: Contact your hosting provider
- **KaChing Issues**: Check project GitHub issues

## 🎯 Next Steps

After WordPress setup:

1. **Test publishing workflow**
   ```bash
   uv run examples/publishing_agent_demo.py
   ```

2. **Configure affiliate programs**
   - Amazon Associates
   - Kitchen tool manufacturer programs
   - Health/wellness networks

3. **Set up analytics**
   - Google Analytics
   - Google Search Console
   - Affiliate tracking

4. **Deploy production system**
   - Set up automated scheduling
   - Configure monitoring alerts
   - Test full end-to-end workflow

---

*This guide is part of the KaChing autonomous affiliate content system. For more information, see the main project documentation.* 