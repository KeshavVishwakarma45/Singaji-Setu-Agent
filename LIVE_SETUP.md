# 🎙️ Live Real-Time Transcription Setup

## Features
✅ **Real-time transcription** - Jaise baat ho rahi hai waise text dikhega
✅ **2-person conversation** - Interviewer aur farmer dono ki baat transcribe hogi
✅ **Live streaming** - WebSocket se continuous audio streaming
✅ **Automatic AI analysis** - Recording stop karne par automatic Gemini analysis
✅ **GCP Storage** - Audio files automatically save hongi

## Installation Steps

### 1. Backend Setup
```bash
cd flask_react_version/backend

# Install new dependencies
pip install eventlet

# Or install all
pip install -r requirements.txt
```

### 2. Frontend Setup
```bash
cd flask_react_version/frontend

# Install socket.io-client
npm install socket.io-client

# Or install all
npm install
```

### 3. Start Backend
```bash
cd flask_react_version/backend
python app.py
```

### 4. Start Frontend
```bash
cd flask_react_version/frontend
npm start
```

## How to Use

1. **Open browser** - Go to `http://localhost:3000`

2. **Select "Live Recording"** - First page pe "Live Recording" option choose karo

3. **Start Recording** - "🎤 Start Live Recording" button click karo
   - Browser microphone permission maangega - Allow karo
   - Recording start hone ke baad real-time transcription dikhega

4. **Have Conversation** - 2 log baat karo (interviewer + farmer)
   - Jaise baat hogi waise text screen pe dikhega
   - Gray text = interim (temporary)
   - Black text = final (confirmed)

5. **Stop & Analyze** - Jab interview complete ho:
   - "⏹️ Stop & Analyze" button click karo
   - Automatic Gemini AI analysis hoga
   - Results page pe redirect hoga with full transcript + JSON

## Technical Details

### WebSocket Events
- `connect` - Client connects to server
- `start_stream` - Start live transcription
- `audio_data` - Send audio chunks (every 1 second)
- `transcript_update` - Receive live transcript updates
- `stop_stream` - Stop recording and analyze
- `analysis_complete` - Get final results

### Audio Format
- **Encoding**: WEBM with Opus codec
- **Sample Rate**: 48000 Hz
- **Chunk Size**: 1 second intervals
- **Language**: Hindi (hi-IN) with automatic punctuation

### Google Cloud Services Used
1. **Speech-to-Text Streaming API** - Real-time transcription
2. **Gemini AI** - Interview analysis
3. **Cloud Storage** - Audio file storage (optional)

## Troubleshooting

### Microphone not working
- Check browser permissions
- Use Chrome/Edge (best support)
- HTTPS required for production

### Transcription not showing
- Check backend console for errors
- Verify Google Cloud credentials
- Check internet connection

### WebSocket connection failed
- Ensure backend is running on port 5000
- Check CORS settings
- Verify eventlet is installed

## Cost Optimization

**Google Speech-to-Text Streaming**:
- First 60 minutes/month: FREE
- After that: $0.024 per minute
- For 100 interviews (30 min each) = 50 hours = $72/month

**Gemini API**:
- Free tier: 60 requests/minute
- Sufficient for most use cases

## Next Steps

1. Add speaker diarization (identify who is speaking)
2. Add pause/resume functionality
3. Add audio quality indicator
4. Add background noise reduction
5. Add multi-language support

## Support

For issues, check:
- Backend console logs
- Browser console (F12)
- Network tab for WebSocket connection
