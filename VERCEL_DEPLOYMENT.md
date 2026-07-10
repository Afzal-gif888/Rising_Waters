# Vercel Deployment Guide - Rising Waters

## Overview
Rising Waters is a Flask-based flood prediction application that can be deployed on Vercel using Python serverless functions. This guide provides step-by-step instructions for deploying the project.

## Prerequisites
- GitHub account with the Rising Waters repository pushed
- Vercel account (free tier available at https://vercel.com)
- The repository must be public or Vercel must have access

## Project Structure for Vercel
```
Rising_Waters/
├── api/
│   └── index.py                 # Vercel serverless function handler
├── backend/
│   ├── __init__.py
│   ├── app.py                   # Flask application
│   ├── config/
│   ├── routes/
│   ├── services/
│   └── predict.py
├── frontend/
│   ├── static/                  # CSS, JS, images
│   └── templates/               # HTML templates
├── ml/
│   └── utils/                   # ML utilities (for reference)
├── models/
│   ├── floods.save              # Trained model artifact
│   └── transform.save           # Scaler artifact
├── src/
│   └── app.py                   # Entry point
├── tests/
├── vercel.json                  # Vercel configuration
├── .env.example                 # Environment variables template
├── requirements.txt             # Python dependencies
└── README.md

```

## Required Environment Variables

These variables must be set in the Vercel dashboard:

| Variable | Description | Example | Required |
| --- | --- | --- | --- |
| `SECRET_KEY` | Flask secret key for session management | `your-secure-random-key` | Yes |
| `DEBUG` | Debug mode (must be False in production) | `False` | Yes |
| `LOG_LEVEL` | Logging level | `INFO` | No (default: INFO) |
| `MODEL_PATH` | Path to trained model artifact | `models/floods.save` | No |
| `SCALER_PATH` | Path to feature scaler artifact | `models/transform.save` | No |

## Step-by-Step Deployment

### 1. Push Code to GitHub
Ensure all code is committed and pushed to GitHub:
```bash
git add .
git commit -m "Ready for Vercel deployment"
git push origin main
```

### 2. Import Project into Vercel
1. Go to https://vercel.com/new
2. Click "Import Project"
3. Select "Import Git Repository"
4. Enter your GitHub repository URL: `https://github.com/Afzal-gif888/Rising_Waters`
5. Click "Continue"

### 3. Configure Project Settings
1. **Project Name**: `rising-waters` (or your preferred name)
2. **Framework Preset**: Select "Other" (Vercel will auto-detect Flask)
3. **Root Directory**: Leave as default (or set to `/` if needed)
4. **Build Command**: `pip install -r requirements.txt`
5. **Output Directory**: Leave blank
6. **Install Command**: `pip install -r requirements.txt`

### 4. Add Environment Variables
In the "Environment Variables" section, add:

```
SECRET_KEY=your-secure-random-key-here
DEBUG=False
LOG_LEVEL=INFO
MODEL_PATH=models/floods.save
SCALER_PATH=models/transform.save
```

**To generate a secure SECRET_KEY:**
```python
import secrets
print(secrets.token_hex(32))
```

Or use an online generator: https://generate.security/

### 5. Deploy
1. Click the "Deploy" button
2. Wait for the build and deployment to complete
3. You'll receive a URL like: `https://rising-waters-xxx.vercel.app`

### 6. Verify Deployment
Once deployed, test these endpoints:
- **Home Page**: `https://your-app.vercel.app/`
- **Prediction Page**: `https://your-app.vercel.app/predict`
- **Health Check**: `https://your-app.vercel.app/health`

## File Descriptions

### `api/index.py`
Vercel serverless function handler. This file:
- Imports the Flask application from `src.app`
- Configures environment variables for Vercel
- Exposes the `app` object for Vercel to execute

### `vercel.json`
Vercel configuration file that specifies:
- Build command
- Development command
- Environment variables
- Serverless function routing
- Request timeout settings

### `.env.example`
Template for environment variables. Update with production values before deploying.

## Common Issues and Troubleshooting

### Issue: "Module not found" error for backend
**Solution**: Ensure `sys.path` manipulation in `api/index.py` includes the project root.

### Issue: Model artifacts not found during prediction
**Solution**: Verify that:
1. `models/floods.save` and `models/transform.save` exist in the repository
2. Environment variables `MODEL_PATH` and `SCALER_PATH` are set correctly
3. Paths are relative to project root, not absolute

### Issue: Static files (CSS, JS) not loading
**Solution**: Ensure Flask is configured with correct paths:
- `template_folder=str(BASE_DIR / "frontend" / "templates")`
- `static_folder=str(BASE_DIR / "frontend" / "static")`

### Issue: 500 errors after deployment
**Solution**:
1. Check Vercel logs: Dashboard → Your Project → Deployments → Logs
2. Ensure `DEBUG=False` is set (stack traces won't be exposed in production)
3. Verify all environment variables are set in Vercel dashboard

### Issue: Prediction returns 502 or timeout
**Solution**: 
1. Increase function timeout in `vercel.json` (currently 60 seconds)
2. Optimize model loading to cache between requests

## Redeployment

### After Making Code Changes
1. Commit and push changes to GitHub:
   ```bash
   git add .
   git commit -m "Your message"
   git push origin main
   ```

2. Option A: Automatic redeploy
   - Vercel automatically redeploys on push to main branch

3. Option B: Manual redeploy
   - Go to Vercel Dashboard
   - Select your project
   - Click "Deployments"
   - Click the three dots on the latest deployment
   - Select "Redeploy"

### After Updating Environment Variables
1. Go to Vercel Dashboard
2. Select your project
3. Go to Settings → Environment Variables
4. Update the values
5. Go to Deployments and click "Redeploy" on the latest deployment

## Production Considerations

### Security
- Always use `DEBUG=False` in production
- Generate a strong SECRET_KEY (minimum 32 characters)
- Never commit `.env` files to GitHub

### Performance
- Model artifacts are loaded once per container, not per request
- Vercel will auto-scale based on traffic
- Consider caching strategies for frequently used predictions

### Monitoring
- Use Vercel Analytics to monitor usage
- Check logs regularly for errors
- Set up alerts for failed deployments

### Cold Starts
- First request may take 5-10 seconds due to Python environment setup
- Subsequent requests are faster
- Use `/health` endpoint to keep function warm if needed

## Rollback to Previous Version

If something goes wrong:
1. Go to Vercel Dashboard
2. Select your project
3. Go to Deployments
4. Find the previous working deployment
5. Click the three dots
6. Select "Promote to Production"

## Local Testing Before Deployment

To test locally before pushing to Vercel:
```bash
# Install dependencies
pip install -r requirements.txt

# Run locally
python -m flask --app src.app run --debug

# Or use Gunicorn (production-like)
gunicorn -w 1 -b 0.0.0.0:8000 "src.app:app"
```

## Support

For Vercel-specific issues:
- Visit https://vercel.com/docs
- Check Vercel Community: https://vercel.com/support
- View deployment logs in Vercel Dashboard

For application-specific issues:
- Check GitHub Issues
- Review local logs in `logs/` directory
- Inspect Flask error handlers in `backend/app.py`

## Final Notes

- The deployed application is stateless; no data persists between requests
- Model artifacts are read-only during runtime
- Predictions are calculated on-demand for each request
- The application follows Flask best practices for WSGI deployment
