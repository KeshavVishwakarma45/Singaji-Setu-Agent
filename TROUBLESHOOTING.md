# 🔧 Connection Troubleshooting Guide

## Quick Fix Steps

### 1. **Fixed API URL Mismatch** ✅
- **Issue**: Frontend was trying to connect to port 8080, backend runs on 5000
- **Fix**: Updated `frontend/src/services/api.js` to use correct port
- **Status**: RESOLVED

### 2. **Start Both Servers**
```bash
# Option A: Use the startup script
start_app.bat

# Option B: Manual startup
# Terminal 1 - Backend
cd backend
venv\Scripts\activate
python app.py

# Terminal 2 - Frontend  
cd frontend
npm start
```

### 3. **Test Connection**
```bash
# Run connection test
test_connection.bat

# Or manual test
curl http://localhost:5000/api/health
curl http://localhost:3000
```

## Common Issues & Solutions

### ❌ "Connection failed. Retrying..."

**Cause**: Backend server not running or wrong port

**Solutions**:
1. Check if backend is running: `http://localhost:5000/api/health`
2. Restart backend: `cd backend && python app.py`
3. Check virtual environment is activated
4. Verify port 5000 is not blocked by firewall

### ❌ Frontend won't load

**Cause**: Frontend server not started or dependencies missing

**Solutions**:
1. Install dependencies: `cd frontend && npm install`
2. Start frontend: `npm start`
3. Check if port 3000 is available
4. Clear browser cache

### ❌ WebSocket connection fails

**Cause**: Socket.IO connection issues

**Solutions**:
1. Ensure backend is running first
2. Check browser console for errors
3. Try different browser (Chrome recommended)
4. Disable browser extensions temporarily

### ❌ Google Cloud errors

**Cause**: Invalid credentials or API not enabled

**Solutions**:
1. Check `.env` file has correct credentials
2. Verify Google Cloud Speech-to-Text API is enabled
3. Check Gemini API key is valid
4. Ensure GCS bucket exists

## Environment Check

### Backend Requirements
- Python 3.8+
- Virtual environment activated
- All packages installed: `pip install -r requirements.txt`
- Google Cloud credentials configured
- Port 5000 available

### Frontend Requirements  
- Node.js 16+
- Dependencies installed: `npm install`
- Port 3000 available
- Modern browser with WebRTC support

## Port Configuration

| Service | Port | URL |
|---------|------|-----|
| Backend API | 5000 | http://localhost:5000 |
| Frontend | 3000 | http://localhost:3000 |
| WebSocket | 5000 | ws://localhost:5000 |

## Debug Commands

```bash
# Check if ports are in use
netstat -an | findstr :5000
netstat -an | findstr :3000

# Test backend endpoints
curl http://localhost:5000/api/health
curl -X POST http://localhost:5000/api/test

# Check backend logs
cd backend && python app.py

# Check frontend logs  
cd frontend && npm start
```

## Still Having Issues?

1. **Check browser console** for JavaScript errors
2. **Check backend terminal** for Python errors  
3. **Verify environment variables** in both `.env` files
4. **Test with simple curl commands** first
5. **Try different browser** or incognito mode

## Success Indicators

✅ Backend health check returns `{"status": "ok"}`
✅ Frontend loads at http://localhost:3000
✅ No console errors in browser
✅ WebSocket connects successfully
✅ Audio recording works in browser