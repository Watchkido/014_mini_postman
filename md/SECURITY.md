# Security Policy für Mini Postman

## 🔒 Sicherheitsrichtlinien

### 1. Umgebungsvariablen & Secrets
- **NIEMALS** `.env` Dateien in Git committen
- Verwende `.env.example` als Template
- Rotiere API-Keys regelmäßig (mindestens alle 90 Tage)
- Verwende starke, zufällige Passwörter (min. 32 Zeichen)

### 2. API-Schlüssel Management
```bash
# Gute Praxis - Umgebungsvariablen verwenden
export OPENAI_API_KEY="sk-..."
python m005_gesundheitschecker.py --url https://api.example.com

# SCHLECHT - Hardcoded in Code
api_key = "sk-1234567890..."  # NIEMALS so machen!
```

### 3. Netzwerk-Sicherheit
- Verwende HTTPS für alle externen API-Aufrufe
- Validiere SSL-Zertifikate (kein `verify=False`)
- Implementiere Rate Limiting (Standard: 60 Requests/Minute)
- Timeout für alle HTTP-Requests (Standard: 10s)

### 4. Input-Validierung
- Sanitize alle User-Inputs vor API-Aufrufen
- Verwende Whitelisting für erlaubte URLs
- Blockiere interne IP-Bereiche (127.0.0.1, 192.168.x.x, 10.x.x.x)

### 5. Logging & Monitoring
- Logge NIEMALS API-Keys oder Passwörter
- Anonymisiere sensible Daten in Logs
- Überwache ungewöhnliche API-Nutzung
- Alarmiere bei Fehlschlägen

### 6. Container-Sicherheit
```dockerfile
# Verwende Non-Root User
USER minipostman

# Minimale Base-Images
FROM python:3.11-slim

# Keine unnötigen Packages
RUN apt-get remove --purge -y gcc && rm -rf /var/lib/apt/lists/*
```

### 7. Abhängigkeiten
- Halte alle Dependencies aktuell
- Verwende `pip-audit` für Vulnerability-Scans
- Pinne Major-Versionen in requirements.txt

## ⚠️ Bekannte Sicherheitsrisiken

### 1. LibreTranslate Integration
**Risiko**: Unverschlüsselte Übertragung sensibler Daten
**Mitigation**: 
- Verwende HTTPS für LibreTranslate
- Implementiere lokale Instanz für sensible Daten
- Logge keine übersetzten Inhalte

### 2. Streamlit Session State
**Risiko**: Session-Daten im Browser-Speicher
**Mitigation**:
- Keine API-Keys in Session State
- Automatisches Logout nach Inaktivität
- Sichere Cookie-Einstellungen

### 3. Log-Dateien
**Risiko**: Sensible Daten in Logs
**Mitigation**:
- Regex-basierte Filterung von API-Keys
- Rotation und Verschlüsselung von Log-Dateien
- Restricted File Permissions (600)

## 🚨 Incident Response

### Bei kompromittierten API-Keys:
1. **Sofort** betroffene Keys deaktivieren
2. Neue Keys generieren und rotieren
3. Logs auf unautorisierten Zugriff prüfen
4. Affected Services neu deployen
5. Post-Incident Review durchführen

### Bei Datenlecks:
1. Betroffene Systeme isolieren
2. Umfang des Lecks bewerten
3. Betroffene Nutzer/Kunden informieren
4. Regulatory Compliance prüfen (DSGVO, etc.)
5. Sicherheitsmaßnahmen verstärken

## 🔧 Security Tools

### Empfohlene Tools:
```bash
# Dependency Vulnerability Scanning
pip install pip-audit
pip-audit

# Secrets Detection
pip install detect-secrets
detect-secrets scan

# Code Quality & Security
pip install bandit
bandit -r .

# Environment Validation
python env_config.py
```

### Pre-Commit Hooks:
```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/Yelp/detect-secrets
    rev: v1.4.0
    hooks:
      - id: detect-secrets
  - repo: https://github.com/PyCQA/bandit
    rev: 1.7.5
    hooks:
      - id: bandit
```

## 📋 Security Checklist

### Vor Produktions-Deployment:
- [ ] Alle API-Keys in Umgebungsvariablen
- [ ] `.env` ist in `.gitignore`
- [ ] SSL/TLS für alle externen Verbindungen
- [ ] Rate Limiting implementiert
- [ ] Input-Validierung aktiviert
- [ ] Logging ohne sensible Daten
- [ ] Dependency Scan durchgeführt
- [ ] Container läuft als Non-Root
- [ ] Firewall-Regeln konfiguriert
- [ ] Monitoring & Alerting aktiv

### Regelmäßige Security Reviews:
- [ ] Monatlich: Dependency Updates
- [ ] Quartalsweise: API-Key Rotation
- [ ] Halbjährlich: Security Audit
- [ ] Jährlich: Penetration Testing

## 📞 Kontakt bei Sicherheitsproblemen

**Security Contact**: security@minipostman.dev
**PGP Key**: [Hier einfügen]
**Response Time**: 24 Stunden für kritische Issues

---
**Letzte Aktualisierung**: 6. Oktober 2025
**Version**: 1.0