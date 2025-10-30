# 🚀 Quick Setup Guide - Flask + React Version

## ⚡ 5-Minute Setup

### Step 1: Backend Setup (2 minutes)

```bash
# Navigate to backend
cd flask_react_version/backend

# Create virtual environment
python -m venv venv
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy .env file
copy .env.example .env

# Edit .env with your credentials
notepad .env
```

**Required in .env:**
```env
GOOGLE_APPLICATION_CREDENTIALS=../../service-account-key.json
GEMINI_API_KEY=your_gemini_api_key_here
GCS_BUCKET_NAME=your_bucket_name
GCP_PROJECT_ID=your_project_id
GCP_REGION=asia-south1
```

### Step 2: Frontend Setup (2 minutes)

```bash
# Open new terminal
cd flask_react_version/frontend

# Install dependencies
npm install
```

### Step 3: Run Application (1 minute)

**Terminal 1 - Backend:**
```bash
cd backend
python app.py
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm start
```

**Open browser:** `http://localhost:3000`

---

## 🎯 Testing Checklist

- [ ] Backend running on port 5000
- [ ] Frontend running on port 3000
- [ ] Can select workflow (Live/Upload)
- [ ] Can upload audio file
- [ ] Transcription works
- [ ] AI analysis works
- [ ] Can download files

---

## 🔧 Common Issues & Fixes

### Issue 1: "Module not found"
```bash
# Backend
pip install -r requirements.txt

# Frontend
npm install
```

### Issue 2: "Port already in use"
```bash
# Kill process on port 5000 (Windows)
netstat -ano | findstr :5000
taskkill /PID <PID> /F

# Or change port in app.py
socketio.run(app, port=5001)
```

### Issue 3: "CORS error"
Already fixed in `app.py`:
```python
CORS(app, supports_credentials=True)
```

### Issue 4: "Google credentials not found"
```bash
# Check path in .env
GOOGLE_APPLICATION_CREDENTIALS=../../service-account-key.json

# Or use absolute path
GOOGLE_APPLICATION_CREDENTIALS=C:/path/to/service-account-key.json
```

---

## 📦 Production Build

### Backend
```bash
cd backend
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

### Frontend
```bash
cd frontend
npm run build
# Deploy 'build' folder to hosting service
```

---

## 🎨 Customization

### Change Colors
Edit `frontend/src/styles/App.css`:
```css
/* Primary color */
#2E7D32 → Your color

/* Gradient */
linear-gradient(135deg, #2E7D32 0%, #43A047 100%)
```

### Change Port
**Backend:** Edit `app.py`
```python
socketio.run(app, port=5001)
```

**Frontend:** Edit `package.json`
```json
"proxy": "http://localhost:5001"
```

---

## 📊 File Size Limits

- **Max upload:** 500MB (configurable in `app.py`)
- **Recommended:** < 100MB for faster processing

---

## 🔐 Security Checklist

- [ ] `.env` file in `.gitignore`
- [ ] Service account key not committed
- [ ] CORS properly configured
- [ ] File upload validation enabled
- [ ] Session management secure

---

## 🚀 Deployment Options

### Backend
1. **Heroku** (Free tier available)
2. **AWS EC2** (Full control)
3. **Google Cloud Run** (Serverless)
4. **DigitalOcean** (Simple VPS)

### Frontend
1. **Vercel** (Recommended, free)
2. **Netlify** (Free tier)
3. **AWS S3 + CloudFront**
4. **Firebase Hosting**

---

## 📱 Mobile Support

✅ Responsive design
✅ Touch-friendly buttons
✅ Mobile audio recording
✅ Works on iOS/Android browsers

---

## 🎯 Next Steps

1. ✅ Setup complete
2. 🧪 Test all features
3. 🎨 Customize UI (optional)
4. 🚀 Deploy to production
5. 📊 Monitor usage

---

## 💡 Tips

- Use Chrome/Edge for best compatibility
- Keep backend running while using app
- Check browser console for errors
- Monitor backend logs for issues

---

## 📞 Need Help?

1. Check README.md for detailed docs
2. Review troubleshooting section
3. Check backend logs: `python app.py`
4. Check frontend console: F12 in browser

---

**Happy Coding! 🌾**
