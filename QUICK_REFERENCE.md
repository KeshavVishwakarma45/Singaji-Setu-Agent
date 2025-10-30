# ⚡ Quick Reference Card

## 🚀 Start Commands

```bash
# Backend
cd backend
venv\Scripts\activate
python app.py

# Frontend
cd frontend
npm start
```

## 🌐 URLs

- Frontend: http://localhost:3000
- Backend API: http://localhost:5000
- Health Check: http://localhost:5000/api/health

## 📡 API Endpoints

```
POST   /api/init                    # Initialize session
POST   /api/upload                  # Upload audio
POST   /api/transcribe              # Transcribe audio
POST   /api/analyze                 # AI analysis
GET    /api/session/<id>            # Get session data
GET    /api/download/<id>/<type>    # Download files
```

## 📁 File Structure

```
backend/
  app.py              # Main Flask app
  services/           # Business logic
  config/             # Configuration
  utils/              # Utilities

frontend/
  src/
    pages/            # Page components
    components/       # Reusable components
    services/         # API calls
    styles/           # CSS
```

## 🔧 Common Commands

```bash
# Install dependencies
pip install -r requirements.txt    # Backend
npm install                        # Frontend

# Run tests
pytest                             # Backend
npm test                           # Frontend

# Build for production
gunicorn app:app                   # Backend
npm run build                      # Frontend

# Clean install
rm -rf venv && python -m venv venv # Backend
rm -rf node_modules && npm install # Frontend
```

## 🐛 Debug Commands

```bash
# Check ports
netstat -ano | findstr :5000
netstat -ano | findstr :3000

# Kill process
taskkill /PID <PID> /F

# View logs
python app.py                      # Backend logs
npm start                          # Frontend logs
```

## 🔐 Environment Variables

```env
# Backend (.env)
GOOGLE_APPLICATION_CREDENTIALS=path/to/key.json
GEMINI_API_KEY=your_key
GCS_BUCKET_NAME=bucket_name
GCP_PROJECT_ID=project_id
GCP_REGION=asia-south1

# Frontend (.env)
REACT_APP_API_URL=http://localhost:5000
```

## 📦 Dependencies

### Backend
- Flask 3.0+
- Flask-CORS
- Flask-SocketIO
- google-cloud-speech
- langchain-google-genai

### Frontend
- React 18+
- axios
- react-router-dom

## 🎨 Customization Points

```
Colors:        frontend/src/styles/App.css
API URL:       frontend/src/services/api.js
Backend Port:  backend/app.py (line 285)
Schema:        backend/app.py (get_default_schema)
```

## 🚀 Deployment

### Backend (Heroku)
```bash
heroku create app-name
git push heroku main
heroku config:set KEY=value
```

### Frontend (Vercel)
```bash
npm run build
vercel deploy
```

## 📊 Performance Tips

- Use production build for frontend
- Enable gzip compression
- Use CDN for static files
- Optimize audio file size
- Cache API responses

## 🔒 Security Checklist

- [ ] .env in .gitignore
- [ ] CORS configured
- [ ] File size limits set
- [ ] Input validation enabled
- [ ] HTTPS in production

## 📱 Browser Support

✅ Chrome 90+
✅ Firefox 88+
✅ Safari 14+
✅ Edge 90+
⚠️ IE not supported

## 🎯 Testing URLs

```
Workflow:      http://localhost:3000/
Upload:        http://localhost:3000/input
Transcribe:    http://localhost:3000/transcribe
Analyze:       http://localhost:3000/analyze
Results:       http://localhost:3000/results
```

## 💡 Quick Fixes

**Backend not starting?**
- Check .env file
- Verify Python version (3.8+)
- Install dependencies

**Frontend not loading?**
- Check Node version (16+)
- Clear npm cache
- Delete node_modules

**API not connecting?**
- Check backend is running
- Verify CORS settings
- Check proxy in package.json

**Upload failing?**
- Check file format (WAV/FLAC)
- Verify file size < 500MB
- Check GCS credentials

## 📞 Support

- README.md - Full documentation
- SETUP_GUIDE.md - Setup instructions
- COMPARISON.md - Feature comparison
- GitHub Issues - Report bugs

---

**Keep this card handy! 📌**
