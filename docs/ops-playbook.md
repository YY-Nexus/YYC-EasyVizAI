# YYC³ EasyVizAI Operations Playbook

## 🚀 Server Setup & Deployment

### Server Environment Preparation

#### 1. System Requirements
```bash
# Ubuntu/Debian
sudo apt update && sudo apt upgrade -y
sudo apt install -y curl wget git build-essential

# CentOS/RHEL
sudo yum update -y
sudo yum groupinstall -y "Development Tools"
sudo yum install -y curl wget git
```

#### 2. Node.js LTS Installation
```bash
# Install Node.js 18 LTS
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt-get install -y nodejs

# Verify installation
node --version  # Should show v18.x.x
npm --version
```

#### 3. pnpm Installation (Alternative)
```bash
# Install pnpm globally
npm install -g pnpm

# Verify installation
pnpm --version
```

### Application Deployment

#### 1. Clone and Setup
```bash
# Clone repository
git clone https://github.com/YY-Nexus/YYC-EasyVizAI.git
cd YYC-EasyVizAI

# Install dependencies
make bootstrap

# Setup environment
cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env.local
```

#### 2. Configure Environment Variables
```bash
# Edit backend environment
nano backend/.env

# Required settings:
NODE_ENV=production
PORT=8000
OPENAI_API_KEY=your_actual_openai_key
LOG_LEVEL=info
ALLOWED_ORIGINS=https://your-domain.com

# Edit frontend environment
nano frontend/.env.local

# Required settings:
NEXT_PUBLIC_API_URL=https://your-api-domain.com
NEXT_PUBLIC_WS_URL=wss://your-api-domain.com
```

#### 3. Build Applications
```bash
# Build for production
make build

# Test production build locally
make start
```

## 🔧 Process Management

### PM2 Setup for Backend
```bash
# Install PM2 globally
npm install -g pm2

# Create PM2 ecosystem file
cat > ecosystem.config.js << EOF
module.exports = {
  apps: [{
    name: 'easyvizai-backend',
    script: 'src/server.js',
    cwd: './backend',
    instances: 1,
    exec_mode: 'fork',
    env: {
      NODE_ENV: 'production',
      PORT: 8000
    },
    log_file: './logs/combined.log',
    out_file: './logs/out.log',
    error_file: './logs/error.log',
    time: true
  }]
};
EOF

# Start with PM2
pm2 start ecosystem.config.js

# Save PM2 configuration
pm2 save
pm2 startup
```

### Nginx Configuration
```bash
# Install Nginx
sudo apt install -y nginx

# Create site configuration
sudo tee /etc/nginx/sites-available/easyvizai << EOF
server {
    listen 80;
    server_name your-domain.com;

    # Frontend (Next.js)
    location / {
        proxy_pass http://localhost:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_cache_bypass \$http_upgrade;
    }

    # Backend API
    location /api/ {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }

    # WebSocket
    location /ws {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }

    # Health check
    location /health {
        proxy_pass http://localhost:8000;
        access_log off;
    }

    # Security headers
    add_header X-Frame-Options DENY;
    add_header X-Content-Type-Options nosniff;
    add_header X-XSS-Protection "1; mode=block";
}
EOF

# Enable site
sudo ln -s /etc/nginx/sites-available/easyvizai /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

## 📊 Monitoring & Logging

### Log Management
```bash
# View application logs
make logs

# View PM2 logs
pm2 logs easyvizai-backend

# Setup log rotation
sudo tee /etc/logrotate.d/easyvizai << EOF
/home/*/YYC-EasyVizAI/backend/logs/*.log {
    daily
    missingok
    rotate 52
    compress
    delaycompress
    notifempty
    create 644 \$USER \$USER
    postrotate
        pm2 reloadLogs
    endscript
}
EOF
```

### Health Monitoring
```bash
# Create health check script
cat > scripts/health-check.sh << 'EOF'
#!/bin/bash

# Health check endpoints
BACKEND_URL="http://localhost:8000/health"
FRONTEND_URL="http://localhost:3000"

# Check backend
if curl -sf \$BACKEND_URL > /dev/null; then
    echo "✅ Backend is healthy"
else
    echo "❌ Backend is down"
    # Restart backend
    pm2 restart easyvizai-backend
fi

# Check frontend
if curl -sf \$FRONTEND_URL > /dev/null; then
    echo "✅ Frontend is healthy"
else
    echo "❌ Frontend is down"
    # Restart frontend (if using PM2)
    # pm2 restart easyvizai-frontend
fi
EOF

chmod +x scripts/health-check.sh

# Add to crontab for regular checks
(crontab -l 2>/dev/null; echo "*/5 * * * * /path/to/YYC-EasyVizAI/scripts/health-check.sh") | crontab -
```

## 🔒 Security Configuration

### Firewall Setup
```bash
# UFW (Ubuntu)
sudo ufw allow ssh
sudo ufw allow 80
sudo ufw allow 443
sudo ufw enable

# iptables (CentOS)
sudo firewall-cmd --permanent --add-service=ssh
sudo firewall-cmd --permanent --add-service=http
sudo firewall-cmd --permanent --add-service=https
sudo firewall-cmd --reload
```

### SSL Certificate (Let's Encrypt)
```bash
# Install certbot
sudo apt install -y certbot python3-certbot-nginx

# Obtain certificate
sudo certbot --nginx -d your-domain.com

# Test auto-renewal
sudo certbot renew --dry-run
```

### Environment Security
```bash
# Secure environment files
chmod 600 backend/.env frontend/.env.local

# Create dedicated user
sudo useradd -m -s /bin/bash easyvizai
sudo usermod -aG www-data easyvizai

# Set proper permissions
sudo chown -R easyvizai:easyvizai /home/easyvizai/YYC-EasyVizAI
sudo chmod -R 755 /home/easyvizai/YYC-EasyVizAI
```

## 📋 Maintenance Tasks

### Regular Updates
```bash
# Update system packages
sudo apt update && sudo apt upgrade -y

# Update Node.js packages
cd YYC-EasyVizAI
npm audit
make clean
make bootstrap
make build

# Restart services
pm2 restart all
sudo systemctl reload nginx
```

### Backup Procedures
```bash
# Create backup script
cat > scripts/backup.sh << 'EOF'
#!/bin/bash

BACKUP_DIR="/backup/easyvizai"
DATE=$(date +%Y%m%d_%H%M%S)

# Create backup directory
mkdir -p \$BACKUP_DIR

# Backup application files
tar -czf \$BACKUP_DIR/app_\$DATE.tar.gz \
    --exclude=node_modules \
    --exclude=.next \
    --exclude=logs \
    /home/*/YYC-EasyVizAI

# Backup environment files
cp backend/.env \$BACKUP_DIR/backend_env_\$DATE
cp frontend/.env.local \$BACKUP_DIR/frontend_env_\$DATE

# Cleanup old backups (keep last 7 days)
find \$BACKUP_DIR -name "*.tar.gz" -mtime +7 -delete
find \$BACKUP_DIR -name "*_env_*" -mtime +7 -delete

echo "Backup completed: \$DATE"
EOF

chmod +x scripts/backup.sh

# Schedule daily backups
(crontab -l 2>/dev/null; echo "0 2 * * * /path/to/YYC-EasyVizAI/scripts/backup.sh") | crontab -
```

## 🚨 Troubleshooting

### Common Issues

#### Backend Won't Start
```bash
# Check logs
pm2 logs easyvizai-backend

# Check port usage
sudo netstat -tlnp | grep :8000

# Restart PM2
pm2 restart easyvizai-backend

# Check environment
cat backend/.env
```

#### Frontend Build Fails
```bash
# Clear cache
rm -rf frontend/.next frontend/node_modules
cd frontend && npm install

# Check environment
cat frontend/.env.local

# Build again
cd .. && make build
```

#### WebSocket Connection Issues
```bash
# Check Nginx WebSocket configuration
sudo nginx -t

# Test WebSocket endpoint
curl -i -N -H "Connection: Upgrade" \
     -H "Upgrade: websocket" \
     -H "Sec-WebSocket-Key: test" \
     -H "Sec-WebSocket-Version: 13" \
     http://localhost:8000/ws
```

### Performance Optimization
```bash
# Enable Nginx compression
sudo tee -a /etc/nginx/nginx.conf << EOF
# Gzip compression
gzip on;
gzip_vary on;
gzip_min_length 1024;
gzip_proxied any;
gzip_comp_level 6;
gzip_types
    text/plain
    text/css
    text/xml
    text/javascript
    application/json
    application/javascript
    application/xml+rss
    application/atom+xml
    image/svg+xml;
EOF

# Restart Nginx
sudo systemctl restart nginx
```

## 📞 Support Contacts

- **Technical Issues**: Check logs and documentation
- **API Keys**: Ensure proper configuration in .env files
- **Performance**: Monitor with PM2 and system tools
- **Security**: Regular updates and security scanning

---

**YYC³ EasyVizAI Operations Team**
Last Updated: $(date +%Y-%m-%d)