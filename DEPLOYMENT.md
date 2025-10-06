# Deployment Guide - Mini Postman

## 🚀 Übersicht

Dieser Guide führt Sie durch verschiedene Deployment-Optionen für Mini Postman.

## 📋 Voraussetzungen

### System Requirements
- **Python**: 3.8+
- **RAM**: Minimum 2GB, empfohlen 4GB+
- **Disk**: Minimum 1GB freier Speicher
- **Ports**: 8501 (Streamlit), 5000 (LibreTranslate), 5432 (PostgreSQL), 6379 (Redis)

### Dependencies Check
```bash
python --version  # >= 3.8
pip --version
git --version
docker --version  # Optional für Container-Deployment
```

## 🛠️ Lokales Development Setup

### 1. Repository klonen & Environment einrichten
```bash
git clone <repository-url>
cd 014_mini_postman

# Virtual Environment erstellen
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate

# Dependencies installieren
pip install -r requirements.txt
```

### 2. Environment-Konfiguration
```bash
# .env erstellen
cp .env.example .env

# .env editieren (siehe Abschnitt "Environment Variables")
notepad .env  # Windows
vim .env      # Linux/Mac
```

### 3. Lokaler Start
```bash
# Health Check Tool testen
python m005_gesundheitschecker.py https://jsonplaceholder.typicode.com/posts

# Streamlit GUI starten
streamlit run api_mini_postman_gui.py

# Browser öffnet automatisch: http://localhost:8501
```

## 🐳 Docker Deployment

### 1. Single Container (Mini Postman only)
```bash
# Image bauen
docker build -t mini-postman .

# Container starten
docker run -p 8501:8501 --env-file .env mini-postman

# Oder mit Environment-Variablen
docker run -p 8501:8501 \
  -e LIBRETRANSLATE_API_KEY=your-key \
  -e DEBUG=false \
  mini-postman
```

### 2. Full Stack mit Docker Compose
```bash
# Alle Services starten
docker-compose up -d

# Logs ansehen
docker-compose logs -f mini-postman

# Services stoppen
docker-compose down

# Volumes löschen (Achtung: Datenverlust!)
docker-compose down -v
```

### Container-Management
```bash
# Container Status
docker-compose ps

# In Container einsteigen
docker-compose exec mini-postman bash

# Services einzeln neustarten
docker-compose restart mini-postman
docker-compose restart libretranslate
```

## ☁️ Cloud Deployment

### 1. Heroku Deployment
```bash
# Heroku CLI installieren & einloggen
heroku login

# App erstellen
heroku create mini-postman-app

# Environment-Variablen setzen
heroku config:set LIBRETRANSLATE_API_KEY=your-key
heroku config:set OPENAI_API_KEY=your-key
heroku config:set DEBUG=false

# PostgreSQL Add-on (optional)
heroku addons:create heroku-postgresql:hobby-dev

# Deploy
git push heroku main

# App öffnen
heroku open

# Logs ansehen
heroku logs --tail
```

**Heroku-spezifische Dateien:**
```bash
# Procfile erstellen
echo "web: streamlit run api_mini_postman_gui.py --server.port \$PORT --server.address 0.0.0.0" > Procfile

# runtime.txt (Python-Version)
echo "python-3.11.0" > runtime.txt
```

### 2. AWS EC2 Deployment
```bash
# EC2 Instance erstellen (Ubuntu 20.04 LTS)
# Security Group: Ports 22 (SSH), 8501 (Streamlit), 80 (HTTP), 443 (HTTPS)

# SSH in Instance
ssh -i your-key.pem ubuntu@your-ec2-ip

# System Updates
sudo apt update && sudo apt upgrade -y

# Python & Git installieren
sudo apt install python3 python3-pip python3-venv git nginx -y

# Projekt klonen
git clone <repository-url>
cd 014_mini_postman

# Environment einrichten
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# .env konfigurieren
cp .env.example .env
nano .env

# Systemd Service erstellen
sudo nano /etc/systemd/system/mini-postman.service
```

**Systemd Service File:**
```ini
[Unit]
Description=Mini Postman Streamlit App
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/014_mini_postman
Environment=PATH=/home/ubuntu/014_mini_postman/venv/bin
ExecStart=/home/ubuntu/014_mini_postman/venv/bin/python -m streamlit run api_mini_postman_gui.py --server.port 8501 --server.address 0.0.0.0
Restart=always

[Install]
WantedBy=multi-user.target
```

```bash
# Service aktivieren & starten
sudo systemctl daemon-reload
sudo systemctl enable mini-postman
sudo systemctl start mini-postman

# Status prüfen
sudo systemctl status mini-postman

# Nginx Reverse Proxy konfigurieren
sudo nano /etc/nginx/sites-available/mini-postman
```

**Nginx Konfiguration:**
```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:8501;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

```bash
# Nginx aktivieren
sudo ln -s /etc/nginx/sites-available/mini-postman /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx

# SSL mit Let's Encrypt (optional)
sudo apt install certbot python3-certbot-nginx -y
sudo certbot --nginx -d your-domain.com
```

### 3. Azure Container Instances
```bash
# Azure CLI installieren & einloggen
az login

# Resource Group erstellen
az group create --name mini-postman-rg --location eastus

# Container Registry (optional)
az acr create --resource-group mini-postman-rg --name minipostmanregistry --sku Basic

# Container Image bauen & pushen
az acr build --registry minipostmanregistry --image mini-postman:latest .

# Container Instance erstellen
az container create \
  --resource-group mini-postman-rg \
  --name mini-postman-instance \
  --image minipostmanregistry.azurecr.io/mini-postman:latest \
  --ports 8501 \
  --environment-variables \
    LIBRETRANSLATE_API_KEY=your-key \
    DEBUG=false \
  --cpu 1 \
  --memory 2

# Public IP abrufen
az container show --resource-group mini-postman-rg --name mini-postman-instance --query ipAddress.ip
```

## 🔧 Production Konfiguration

### 1. Environment Variables
```bash
# .env für Production
DEBUG=false
MAX_REQUESTS_PER_MINUTE=100
PERFORMANCE_WARNING_MS=1000
PERFORMANCE_ERROR_MS=3000

# API Keys (verschlüsselt speichern!)
LIBRETRANSLATE_API_KEY=your-encrypted-key
OPENAI_API_KEY=your-encrypted-key

# Database (falls verwendet)
DATABASE_URL=postgresql://user:pass@localhost:5432/minipostman

# Monitoring
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=alerts@yourdomain.com
SMTP_PASSWORD=your-app-password

# Slack Integration
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/...
```

### 2. Security Hardening
```bash
# Firewall konfigurieren (Ubuntu)
sudo ufw enable
sudo ufw allow 22/tcp      # SSH
sudo ufw allow 80/tcp      # HTTP
sudo ufw allow 443/tcp     # HTTPS
sudo ufw deny 8501/tcp     # Streamlit nur über Nginx

# SSL/TLS erzwingen
# Nginx config erweitern:
# return 301 https://$server_name$request_uri;  # HTTP -> HTTPS redirect

# API Rate Limiting (in nginx)
http {
    limit_req_zone $binary_remote_addr zone=api:10m rate=10r/s;
    
    server {
        location /api/ {
            limit_req zone=api burst=20 nodelay;
        }
    }
}

# Log Rotation
sudo nano /etc/logrotate.d/mini-postman
```

**Log Rotation Config:**
```
/home/ubuntu/014_mini_postman/*.log {
    daily
    rotate 30
    compress
    delaycompress
    missingok
    notifempty
    postrotate
        systemctl reload mini-postman
    endscript
}
```

### 3. Monitoring Setup
```bash
# Health Check Cronjob
crontab -e

# Alle 5 Minuten Health Check
*/5 * * * * cd /home/ubuntu/014_mini_postman && /home/ubuntu/014_mini_postman/venv/bin/python m005_gesundheitschecker.py https://your-domain.com >> /var/log/mini-postman-health.log 2>&1

# Log Monitoring mit journalctl
journalctl -u mini-postman -f

# Performance Monitoring
sudo apt install htop iotop nethogs -y
htop  # CPU/RAM Monitoring
```

## 📊 Performance Tuning

### 1. Streamlit Optimierung
```python
# config.toml erstellen
mkdir -p ~/.streamlit

cat > ~/.streamlit/config.toml << EOF
[server]
port = 8501
headless = true
enableCORS = false
enableXsrfProtection = false

[browser]
gatherUsageStats = false

[theme]
primaryColor = "#FF6B6B"
backgroundColor = "#FFFFFF"
secondaryBackgroundColor = "#F0F2F6"
textColor = "#262730"
EOF
```

### 2. Python Performance
```python
# requirements.txt für Production
streamlit==1.28.1
requests==2.31.0
psutil==5.9.6
python-dotenv==1.0.0
aiohttp==3.8.6          # Async HTTP
uvloop==0.17.0          # Faster event loop (Linux/Mac)
orjson==3.9.9           # Faster JSON
```

### 3. Database Optimierung (falls PostgreSQL verwendet)
```sql
-- PostgreSQL Tuning
-- /etc/postgresql/14/main/postgresql.conf

shared_buffers = 256MB          # 25% of RAM
effective_cache_size = 1GB      # 75% of RAM
maintenance_work_mem = 64MB
work_mem = 4MB
max_connections = 100
```

## 🔄 CI/CD Pipeline

### GitHub Actions Workflow
```yaml
# .github/workflows/deploy.yml
name: Deploy Mini Postman

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
        pip install pytest pytest-cov
    
    - name: Run tests
      run: |
        pytest tests/ --cov=./ --cov-report=xml
    
    - name: Upload coverage
      uses: codecov/codecov-action@v3

  deploy:
    needs: test
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Deploy to Heroku
      uses: akhileshns/heroku-deploy@v3.12.12
      with:
        heroku_api_key: ${{secrets.HEROKU_API_KEY}}
        heroku_app_name: "mini-postman-app"
        heroku_email: "your-email@example.com"
        
    - name: Deploy to AWS EC2
      run: |
        echo "${{ secrets.EC2_SSH_KEY }}" > private_key.pem
        chmod 600 private_key.pem
        ssh -i private_key.pem -o StrictHostKeyChecking=no ubuntu@${{ secrets.EC2_HOST }} '
          cd 014_mini_postman &&
          git pull origin main &&
          source venv/bin/activate &&
          pip install -r requirements.txt &&
          sudo systemctl restart mini-postman
        '
```

## 🆘 Troubleshooting

### Häufige Probleme

**1. Port bereits in Verwendung**
```bash
# Port 8501 prüfen
netstat -tulpn | grep 8501
lsof -i :8501

# Prozess beenden
kill -9 <PID>

# Streamlit auf anderem Port starten
streamlit run api_mini_postman_gui.py --server.port 8502
```

**2. Unicode-Encoding Probleme**
```bash
# Environment-Variablen setzen
export PYTHONIOENCODING=utf-8
export LC_ALL=en_US.UTF-8

# Windows
set PYTHONIOENCODING=utf-8
```

**3. Permission Denied Fehler**
```bash
# Dateiberechtigungen prüfen
ls -la

# Ausführungsberechtigung setzen
chmod +x m005_gesundheitschecker.py

# Ownership ändern
sudo chown -R $USER:$USER /path/to/project
```

**4. SSL Certificate Fehler**
```python
# In Python-Code (nur für Development!)
import ssl
ssl._create_default_https_context = ssl._create_unverified_context

# Besser: CA-Bundle aktualisieren
pip install --upgrade certifi
```

**5. Memory Issues**
```bash
# Memory Usage prüfen
free -h
htop

# Swap erstellen (falls nötig)
sudo fallocate -l 2G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
```

### Logs & Debugging
```bash
# Streamlit Logs
streamlit run app.py --logger.level debug

# System Logs
journalctl -u mini-postman -n 50

# Container Logs
docker logs mini-postman-container -f

# Python Debugging
python -m pdb m005_gesundheitschecker.py <url>
```

---

**Für weitere Hilfe siehe README.md oder erstellen Sie ein GitHub Issue.**

**Letzte Aktualisierung**: 6. Oktober 2025