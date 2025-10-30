# 🚀 Deployment Guide

## Quick Deploy Commands

### 1. Initialize Git Repository
```bash
cd Singaji-Setu-Agent
git init
git add .
git commit -m "Initial commit: Singaji Setu Agent v1.0"
```

### 2. Push to GitHub
```bash
# Create repository on GitHub first, then:
git remote add origin https://github.com/yourusername/singaji-setu-agent.git
git branch -M main
git push -u origin main
```

### 3. Deploy Backend (Railway)
```bash
cd backend
npm install -g @railway/cli
railway login
railway init
railway up
```

### 4. Deploy Frontend (Netlify)
```bash
cd frontend
npm run build
# Drag & drop build folder to netlify.com
```

## Environment Variables Setup

### Backend (Railway)
```bash
railway variables set GOOGLE_APPLICATION_CREDENTIALS=service-account-key.json
railway variables set GEMINI_API_KEY=your_key
railway variables set GCS_BUCKET_NAME=your_bucket
railway variables set GCP_PROJECT_ID=your_project
```

### Frontend (Netlify)
```bash
# In Netlify dashboard, add:
REACT_APP_API_URL=https://your-backend-url.railway.app
```

## Production Checklist

- [ ] Environment variables configured
- [ ] Google Cloud credentials uploaded
- [ ] CORS updated for production URLs
- [ ] HTTPS enabled
- [ ] Domain configured (optional)
- [ ] Monitoring setup (optional)

## Cost Optimization

- Use Railway free tier (500 hours/month)
- Use Netlify free tier (100GB bandwidth)
- Monitor Google Cloud usage
- Set up billing alerts

## Monitoring

### Health Check URLs
- Backend: `https://your-backend.railway.app/api/health`
- Frontend: `https://your-frontend.netlify.app`

### Logs
```bash
# Railway logs
railway logs

# Netlify logs
# Available in dashboard
```