# 🚀 Deployment Guide

This document provides multiple deployment options for the Bangla PDF Question Answering System.

## 📋 Pre-deployment Checklist

- [ ] OpenAI API key obtained
- [ ] Git repository pushed to GitHub
- [ ] All dependencies tested locally
- [ ] Environment variables configured

## 🌟 Option 1: Streamlit Cloud (Recommended - Free)

### Steps:
1. **Push to GitHub:**
   ```bash
   git add .
   git commit -m "Ready for deployment"
   git push origin main
   ```

2. **Deploy on Streamlit Cloud:**
   - Visit [share.streamlit.io](https://share.streamlit.io)
   - Connect your GitHub account
   - Select your repository
   - Set the main file path: `app_deploy.py`
   - Add secrets in Streamlit Cloud dashboard:
     ```
     OPENAI_API_KEY = "your_api_key_here"
     ```

3. **Advanced settings:**
   - Python version: 3.9
   - Requirements file: `requirements.txt`
   - Packages file: `packages.txt`

### ✅ Pros:
- Free hosting
- Automatic HTTPS
- Easy setup
- Auto-restart on code changes

### ❌ Cons:
- Limited resources
- Public repository required (for free tier)

## 🐳 Option 2: Docker Deployment

### Local Docker:
```bash
# Build the image
docker build -t bangla-pdf-qa .

# Run the container
docker run -p 8501:8501 -e OPENAI_API_KEY=your_key bangla-pdf-qa
```

### Docker Compose:
```bash
# Create .env file with your API key
echo "OPENAI_API_KEY=your_api_key_here" > .env

# Run with docker-compose
docker-compose up -d
```

### Deploy to Cloud with Docker:
- **Google Cloud Run**
- **AWS ECS**
- **Azure Container Instances**
- **DigitalOcean App Platform**

## 🚂 Option 3: Railway (Easy)

### Steps:
1. **Connect GitHub to Railway:**
   - Visit [railway.app](https://railway.app)
   - Connect your GitHub repository

2. **Configure environment:**
   - Add `OPENAI_API_KEY` in Railway dashboard
   - Railway will automatically detect the `railway.json` config

3. **Deploy:**
   - Railway auto-deploys on git push

### ✅ Pros:
- Very easy setup
- Good free tier
- Automatic scaling

## 🌊 Option 4: Heroku

### Steps:
1. **Install Heroku CLI**
2. **Login and create app:**
   ```bash
   heroku login
   heroku create your-app-name
   ```

3. **Add buildpacks:**
   ```bash
   heroku buildpacks:add --index 1 heroku-community/apt
   heroku buildpacks:add --index 2 heroku/python
   ```

4. **Set environment variables:**
   ```bash
   heroku config:set OPENAI_API_KEY=your_api_key_here
   ```

5. **Deploy:**
   ```bash
   git push heroku main
   ```

## ☁️ Option 5: Other Cloud Platforms

### Google Cloud Platform (Cloud Run):
```bash
# Build and deploy
gcloud builds submit --tag gcr.io/PROJECT_ID/bangla-pdf-qa
gcloud run deploy --image gcr.io/PROJECT_ID/bangla-pdf-qa --platform managed
```

### AWS (ECS/Fargate):
- Use the Dockerfile with AWS ECS
- Configure ALB for load balancing

### Azure (Container Instances):
```bash
az container create --resource-group myResourceGroup --name bangla-pdf-qa --image your-image
```

## 🔧 Configuration for Different Platforms

### Environment Variables:
```bash
OPENAI_API_KEY=your_openai_api_key
STREAMLIT_SERVER_PORT=8501
STREAMLIT_SERVER_ADDRESS=0.0.0.0
```

### Resource Requirements:
- **Memory:** 1-2 GB minimum
- **CPU:** 1 vCPU minimum
- **Storage:** 2 GB for dependencies and cache

## 🛠️ Troubleshooting

### Common Issues:

1. **Tesseract not found:**
   - Ensure `packages.txt` includes `tesseract`
   - Check system package installation

2. **Bengali language data missing:**
   - The app auto-downloads Bengali data
   - Falls back to English if Bengali unavailable

3. **Memory issues:**
   - Increase container memory
   - Use sentence-transformers with smaller models

4. **Slow startup:**
   - Normal for first run (model downloads)
   - Subsequent runs use cached models

### Performance Optimization:

1. **Reduce model size:**
   ```python
   MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"  # Smaller, faster
   ```

2. **Enable caching:**
   - Models and embeddings are cached automatically
   - PDF processing is cached per file

3. **Optimize images:**
   - Reduce PDF DPI for faster processing
   - Compress images before OCR

## 📈 Monitoring

### Health Checks:
- All deployment configs include health checks
- Monitor at: `https://your-app.com/_stcore/health`

### Logging:
- Streamlit provides built-in logging
- Check platform-specific logs for issues

## 🔐 Security

### API Key Management:
- Never commit API keys to git
- Use platform-specific secret management
- Rotate keys regularly

### HTTPS:
- Most platforms provide automatic HTTPS
- Streamlit Cloud includes HTTPS by default

## 💰 Cost Estimates

| Platform | Free Tier | Paid Plans Start |
|----------|-----------|------------------|
| Streamlit Cloud | Yes (unlimited public apps) | $20/month |
| Railway | 500 hours/month | $5/month |
| Heroku | 550 hours/month | $7/month |
| Google Cloud Run | 2M requests/month | Pay per use |
| Docker VPS | N/A | $5-20/month |

## 🎯 Recommended Deployment Strategy

1. **Development/Testing:** Streamlit Cloud (free)
2. **Production (small):** Railway or Google Cloud Run
3. **Production (large):** Docker on dedicated VPS
4. **Enterprise:** Kubernetes cluster

Choose based on your traffic, budget, and technical requirements!
