# 🌾 Singaji Setu AGENT - AI-Powered Farmer Interview System

Complete Flask backend + React frontend application for processing farmer interview surveys from audio recordings with real-time transcription and AI analysis.

## 🚀 Features

✅ **Real-time Live Recording** - Browser-based audio recording with live transcription  
✅ **File Upload Support** - Upload existing audio files (WAV, FLAC, MP3)  
✅ **Google Cloud Speech-to-Text** - Accurate Hindi & English transcription  
✅ **Gemini AI Analysis** - Intelligent survey data extraction  
✅ **WebSocket Streaming** - Real-time audio processing  
✅ **Export Options** - Download transcript, JSON, and audio files  
✅ **Progress Tracking** - Visual step-by-step workflow  

## 📁 Project Structure

```
Singaji-Setu-Agent/
├── backend/                    # Flask API Server
│   ├── app.py                 # Main Flask application
│   ├── config/                # Configuration files
│   ├── services/              # Transcription & AI services
│   ├── utils/                 # Utility functions
│   └── requirements.txt       # Python dependencies
│
├── frontend/                  # React Application
│   ├── public/                # Static files
│   ├── src/
│   │   ├── components/        # Reusable components
│   │   ├── pages/             # Page components
│   │   ├── services/          # API service
│   │   └── styles/            # CSS files
│   └── package.json           # Node dependencies
│
└── docs/                      # Documentation
```

## 🛠️ Installation

### Prerequisites
- Python 3.8+
- Node.js 16+
- Google Cloud Account with Speech-to-Text API
- Google AI Studio API Key (Gemini)

### Backend Setup

1. **Clone repository:**
   ```bash
   git clone <repository-url>
   cd Singaji-Setu-Agent/backend
   ```

2. **Create virtual environment:**
   ```bash
   python -m venv venv
   venv\Scripts\activate  # Windows
   # source venv/bin/activate  # Linux/Mac
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Setup environment variables:**
   ```bash
   copy .env.example .env
   ```
   
   Edit `.env` file:
   ```env
   GOOGLE_APPLICATION_CREDENTIALS=service-account-key.json
   GEMINI_API_KEY=your_gemini_api_key
   GCS_BUCKET_NAME=your_bucket_name
   GCP_PROJECT_ID=your_project_id
   GCP_REGION=asia-south1
   ```

5. **Add Google Cloud credentials:**
   - Download service account key from Google Cloud Console
   - Save as `service-account-key.json` in backend folder

### Frontend Setup

1. **Navigate to frontend:**
   ```bash
   cd ../frontend
   ```

2. **Install dependencies:**
   ```bash
   npm install
   ```

3. **Create environment file:**
   ```bash
   echo REACT_APP_API_URL=http://localhost:5000 > .env
   ```

## 🎯 Running the Application

### Start Backend Server
```bash
cd backend
python app.py
```
Backend runs on: `http://localhost:5000`

### Start Frontend Development Server
```bash
cd frontend
npm start
```
Frontend runs on: `http://localhost:3000`

## 📱 Usage

1. **Open Application:** Navigate to `http://localhost:3000`

2. **Choose Workflow:**
   - **Live Recording:** Record audio directly in browser
   - **Upload File:** Upload existing audio file

3. **Process Audio:**
   - Record or upload audio
   - Real-time transcription (for live recording)
   - Click "Start Transcription" (for uploaded files)

4. **Review & Edit:**
   - Review generated transcript
   - Edit if needed

5. **Generate Analysis:**
   - Click "Generate Survey Data"
   - AI analyzes and creates structured JSON

6. **Download Results:**
   - Download transcript (.txt)
   - Download survey data (.json)
   - Download audio (.wav)

## 🔧 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/health` | Health check |
| POST | `/api/reset` | Reset session |
| POST | `/api/process` | Upload + transcribe + analyze |
| POST | `/api/transcribe` | Transcribe audio |
| POST | `/api/analyze` | Analyze with AI |
| GET | `/api/download/<type>` | Download files |

## 🌐 WebSocket Events

| Event | Direction | Description |
|-------|-----------|-------------|
| `connect` | Client → Server | Client connects |
| `start_stream` | Client → Server | Start live recording |
| `audio_data` | Client → Server | Send audio chunks |
| `transcript_update` | Server → Client | Live transcript updates |
| `stop_stream` | Client → Server | Stop recording |
| `analysis_complete` | Server → Client | Analysis results |

## 🚀 Deployment

### Railway (Recommended)
```bash
# Backend
cd backend
railway init
railway up

# Frontend
cd frontend
npm run build
# Deploy to Netlify/Vercel
```

### Heroku
```bash
# Backend
echo "web: python app.py" > Procfile
git init
git add .
git commit -m "Initial commit"
heroku create your-app-name
git push heroku main

# Frontend
npm run build
# Deploy build folder to hosting service
```

## 💰 Cost Estimation

**Google Cloud Services:**
- Speech-to-Text: First 60 min/month FREE, then $0.024/min
- Cloud Storage: $0.020/GB/month
- Gemini API: 60 requests/min FREE tier

**Hosting:**
- Railway: FREE tier available
- Netlify: FREE for frontend
- Total: $0-10/month for small usage

## 🔐 Security

- Environment variables for sensitive data
- CORS configured for production
- Session-based state management
- Secure file upload handling
- HTTPS required for microphone access

## 🐛 Troubleshooting

### Common Issues

**Microphone not working:**
- Check browser permissions
- Use Chrome/Edge for best support
- Ensure HTTPS in production

**Socket disconnections:**
- Check internet connection
- Verify backend is running
- Check browser console for errors

**Transcription not working:**
- Verify Google Cloud credentials
- Check API quotas
- Ensure proper audio format

## 📚 Documentation

- [Setup Guide](SETUP_GUIDE.md)
- [Live Recording Setup](LIVE_SETUP.md)
- [Quick Reference](QUICK_REFERENCE.md)

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 📞 Support

For support and questions:
- Create an issue on GitHub
- Check documentation files
- Review troubleshooting section

---

**Made with ❤️ for farmers | AI-Powered Interview Processing**