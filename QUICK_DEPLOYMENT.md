# Quick Deployment Guide - Deploy Anywhere Without CORS Issues

This guide shows you how to deploy CyberSentinel on **any server** without hardcoded IPs or CORS errors.

## 🚀 One-Command Deployment

```bash
git clone https://github.com/sujalthakur-03/CyberSentinel-SyslogServer.git
cd CyberSentinel-SyslogServer
chmod +x deploy.sh
./deploy.sh
```

That's it! The script will:
- Auto-detect your server IP
- Configure CORS to accept all origins
- Set up frontend to connect to your API
- Create all necessary `.env` files

## 📋 What Changed for Portable Deployment

### 1. **Dynamic CORS Configuration**

The API now accepts requests from **any origin** by default:

```bash
# In services/api/src/config.py
api_cors_origins: str = "*"  # Allow all origins by default
```

This means **no more CORS errors** when deploying on different servers!

### 2. **Environment Templates**

We've added template files that you can copy and customize:

- `.env.template` - Main configuration
- `services/api/.env.template` - API-specific settings
- `frontend/cybersentinel-ui/.env.template` - Frontend settings

### 3. **Automated Deploy Script**

The `deploy.sh` script automatically:
- Detects your server IP
- Creates `.env` files with correct values
- Configures frontend API URL
- Ready to run with `docker-compose up -d`

## 🔧 Manual Configuration (If Needed)

### For Your New Server

1. **Get your server IP:**
   ```bash
   hostname -I | awk '{print $1}'
   ```

2. **Update frontend .env:**
   ```bash
   cd frontend/cybersentinel-ui
   nano .env
   ```

   Change:
   ```
   REACT_APP_API_URL=http://YOUR_SERVER_IP:8000
   ```

3. **Update API CORS (optional):**
   ```bash
   cd services/api
   nano .env
   ```

   For production with specific origins:
   ```
   API_CORS_ORIGINS=http://YOUR_IP:3000,http://YOUR_IP:8000
   ```

   Or keep it open (development/internal):
   ```
   API_CORS_ORIGINS=*
   ```

4. **Start services:**
   ```bash
   cd /path/to/CyberSentinel-SyslogServer
   docker-compose up -d
   ```

5. **For frontend (if using npm):**
   ```bash
   cd frontend/cybersentinel-ui
   npm install
   npm start
   ```

## 🌐 Access Your Dashboard

After deployment:
- **Dashboard:** `http://YOUR_SERVER_IP:3000`
- **API:** `http://YOUR_SERVER_IP:8000`
- **API Docs:** `http://YOUR_SERVER_IP:8000/docs`

Default credentials: `admin` / `admin`

## ✅ Verification Steps

```bash
# 1. Check Docker services
docker-compose ps

# 2. Test API health
curl http://localhost:8000/health

# 3. Check CORS configuration
curl http://localhost:8000/system/info

# 4. View logs
docker-compose logs -f api
```

## 🔒 Security Notes

### For Development/Internal Networks
```bash
API_CORS_ORIGINS=*  # Accept all origins
```
This is fine for:
- Local development
- Internal corporate networks
- Testing environments

### For Production/Internet-Facing
```bash
API_CORS_ORIGINS=http://your-domain.com,https://your-domain.com
```
Specify exact allowed origins.

## 🐛 Troubleshooting

### CORS Error Still Showing?

1. **Check API CORS config:**
   ```bash
   docker-compose logs api | grep -i cors
   ```

2. **Verify frontend .env:**
   ```bash
   cat frontend/cybersentinel-ui/.env
   ```
   Make sure `REACT_APP_API_URL` matches your server.

3. **Restart services:**
   ```bash
   docker-compose restart api
   ```

4. **Clear browser cache** or use incognito mode

### Cannot Access Dashboard?

1. **Check if frontend is running:**
   ```bash
   # For Docker
   docker-compose ps

   # For npm
   ps aux | grep react-scripts
   ```

2. **Check firewall:**
   ```bash
   sudo ufw allow 3000/tcp
   sudo ufw allow 8000/tcp
   sudo ufw allow 514/udp
   ```

3. **Verify frontend .env has correct IP:**
   ```bash
   cat frontend/cybersentinel-ui/.env
   ```

### API Connection Refused?

1. **Check API is running:**
   ```bash
   curl http://localhost:8000/health
   ```

2. **Check logs:**
   ```bash
   docker-compose logs api
   ```

3. **Verify frontend can reach API:**
   ```bash
   # From the server
   curl http://YOUR_SERVER_IP:8000/health
   ```

## 🎯 Common Deployment Scenarios

### Scenario 1: Local Development
```bash
REACT_APP_API_URL=http://localhost:8000
API_CORS_ORIGINS=*
```

### Scenario 2: Remote Server (Single Machine)
```bash
# Run deploy.sh or manually:
REACT_APP_API_URL=http://192.168.1.100:8000
API_CORS_ORIGINS=*
```

### Scenario 3: Different Servers for Frontend/Backend
```bash
# Frontend Server
REACT_APP_API_URL=http://backend-server-ip:8000

# Backend Server
API_CORS_ORIGINS=http://frontend-server-ip:3000
```

### Scenario 4: Using Domain Names
```bash
REACT_APP_API_URL=https://api.yourdomain.com
API_CORS_ORIGINS=https://dashboard.yourdomain.com
```

## 📝 Quick Reference

| File | Purpose |
|------|---------|
| `.env.template` | Main config template |
| `deploy.sh` | Automated deployment script |
| `services/api/.env` | API configuration |
| `frontend/cybersentinel-ui/.env` | Frontend configuration |
| `services/api/src/config.py` | CORS settings |

## 🎉 You're Done!

Your CyberSentinel is now deployed and accessible from any server without hardcoded IPs or CORS issues!

**Next Steps:**
1. Change default passwords in `.env`
2. Configure syslog sources to send logs to your server
3. Set up alerts and notifications
4. Explore the dashboard at `http://YOUR_SERVER_IP:3000`

---

**Need help?** Check the main [DEPLOYMENT.md](DEPLOYMENT.md) for advanced configurations.
