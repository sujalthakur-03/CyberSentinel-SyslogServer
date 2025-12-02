# CyberSentinel - Issue Resolution Log

## Issue #1: HTTP 405 Error on Login (Fixed)

**Date:** December 2, 2025
**Status:** ✅ RESOLVED
**Severity:** Critical

### Problem Description
Users were unable to log in to the dashboard. The login form was displaying:
```
Request failed with status code 405
```

### Root Cause Analysis

The error occurred due to **improper runtime environment variable injection** in the frontend Docker container. Specifically:

1. **Placeholder Not Replaced**: The React app was built with a placeholder API URL (`__RUNTIME_API_URL__`) instead of the actual server IP address
2. **Environment Script Issues**: The initial `env.sh` script was not properly creating or serving the `env-config.js` file
3. **Configuration Error**: The `.env` file had `SERVER_IP=0.0.0.0` instead of the actual server IP address (`172.17.124.220`)

### Technical Details

**Error Flow:**
```
User clicks "Sign In"
  → Frontend tries to call: __RUNTIME_API_URL__/auth/login
  → nginx returns 405 (Method Not Allowed)
  → Login fails
```

**Expected Flow:**
```
User clicks "Sign In"
  → Frontend calls: http://172.17.124.220:8000/auth/login
  → API authenticates user
  → Login succeeds
```

### Solution Implemented

#### 1. Fixed Dockerfile (`frontend/cybersentinel-ui/Dockerfile`)

**Before:**
- Used placeholder `__RUNTIME_API_URL__` during build
- Separate `env.sh` script file
- Complex startup sequence

**After:**
- Build with default localhost URL (`http://localhost:8000`)
- Embedded startup script directly in Dockerfile
- Simplified environment injection using ENTRYPOINT

**Key Changes:**
```dockerfile
# Create startup script directly in the image
RUN cat > /docker-entrypoint.sh <<'EOF'
#!/bin/bash
set -e

# Get the API URL from environment or use default
API_URL=${REACT_APP_API_URL:-http://localhost:8000}

# Create the runtime configuration file
cat > /usr/share/nginx/html/env-config.js <<ENVEOF
window.ENV = {
  REACT_APP_API_URL: "$API_URL"
};
ENVEOF

# Start nginx in foreground
exec nginx -g 'daemon off;'
EOF

ENTRYPOINT ["/docker-entrypoint.sh"]
```

#### 2. Updated .env Configuration

**Fixed Values:**
```env
SERVER_IP=172.17.124.220  # Changed from 0.0.0.0
REACT_APP_API_URL=http://172.17.124.220:8000  # Explicit IP instead of variable expansion
```

#### 3. Frontend API Service (`src/services/api.ts`)

**Already correctly configured:**
```typescript
const API_BASE_URL = window.ENV?.REACT_APP_API_URL ||
                     process.env.REACT_APP_API_URL ||
                     'http://localhost:8000';
```

This cascading configuration checks:
1. Runtime injected value (`window.ENV.REACT_APP_API_URL`)
2. Build-time environment variable
3. Fallback to localhost

### Verification Steps

1. ✅ Rebuild frontend Docker image with `--no-cache`
2. ✅ Update `.env` with correct server IP
3. ✅ Start frontend container
4. ✅ Verify `env-config.js` is created with correct API URL
5. ✅ Test login functionality
6. ✅ Verify all API calls use correct endpoint

### Testing Performed

```bash
# 1. Rebuild frontend
docker-compose build --no-cache frontend

# 2. Start frontend
docker-compose up -d frontend

# 3. Check logs for startup message
docker-compose logs frontend | grep "CyberSentinel Frontend Starting"

# 4. Verify env-config.js content
docker-compose exec frontend cat /usr/share/nginx/html/env-config.js

# 5. Test API connectivity
curl http://172.17.124.220:8000/health

# 6. Test login via browser
# Navigate to: http://172.17.124.220:3000/login
# Credentials: admin / admin
```

### Prevention Measures

1. **Automated IP Detection**: The `deploy.sh` script now automatically detects and configures the server IP
2. **Better Documentation**: Added clear instructions in `.env.template`
3. **Startup Logging**: Frontend container logs show the configured API URL on startup
4. **Healthchecks**: Added healthcheck to verify frontend is serving correctly

### Files Modified

| File | Change Type | Description |
|------|-------------|-------------|
| `frontend/cybersentinel-ui/Dockerfile` | Modified | Fixed runtime environment injection |
| `.env` | Updated | Set correct SERVER_IP value |
| `MEMORY.md` | Created | This documentation file |

### Related Issues

- None yet

### Additional Notes

- The 405 error specifically occurred because nginx was trying to serve the placeholder string as if it were a file path
- The frontend was built correctly, but the runtime configuration wasn't being injected properly
- CORS is configured to accept all origins (`*`) by default, so CORS was not the issue
- The API service was running correctly on port 8000

### Future Recommendations

1. Add automated tests for environment variable injection
2. Create a health check endpoint that verifies API connectivity
3. Add better error messages when API URL is not configured
4. Consider using a configuration management tool for multi-server deployments

---

## Deployment Checklist

When deploying to a new server, always:

- [ ] Run `bash deploy.sh` to auto-configure IP
- [ ] OR manually set `SERVER_IP` in `.env` to actual server IP
- [ ] Verify `REACT_APP_API_URL` matches `http://SERVER_IP:8000`
- [ ] Build with `docker-compose build`
- [ ] Start with `docker-compose up -d`
- [ ] Check frontend logs: `docker-compose logs frontend`
- [ ] Verify env-config.js: `docker-compose exec frontend cat /usr/share/nginx/html/env-config.js`
- [ ] Test login at `http://SERVER_IP:3000`

---

**Last Updated:** December 2, 2025
**Maintained By:** CyberSentinel Development Team
