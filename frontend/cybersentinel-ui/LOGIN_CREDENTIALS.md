# CyberSentinel SyslogServer - Login Credentials

## Default Users

The system comes with two pre-configured users for testing:

### Administrator Account
- **Username**: `admin`
- **Password**: `admin`
- **Permissions**: Full access (read, write, admin)

### Regular User Account
- **Username**: `user`
- **Password**: `user`
- **Permissions**: Read-only access

## Login Instructions

1. Navigate to http://localhost:3000
2. Enter one of the credentials above
3. Click "Sign In"

## Security Note

⚠️ **IMPORTANT**: These are default credentials for development/testing only.  
In production, you should:
- Change these default passwords
- Implement proper user management
- Use a real database instead of the mock user database
- Enable additional security measures (2FA, password policies, etc.)

## API Endpoints

The backend API is running on http://localhost:8000

Key endpoints:
- `POST /auth/login` - Authenticate and get access token
- `GET /health` - Health check
- `POST /logs/search` - Search logs
- `GET /logs/statistics` - Get statistics
- `GET /logs/threats` - Get threat logs
- `GET /docs` - API documentation (Swagger UI)
