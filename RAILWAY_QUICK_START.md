# Railway Deployment - Quick Start

## Fixed: "pip: command not found" Error ✅

The error has been resolved by updating the `nixpacks.toml` configuration to use `python3 -m pip` instead of `pip` directly.

## Updated Files

The following files have been updated and are ready for deployment:

1. **`/app/backend/nixpacks.toml`** - Fixed pip installation command
2. **`/app/backend/railway.json`** - Updated start command
3. **`/app/backend/Procfile`** - Updated to use python3 module syntax
4. **`/app/frontend/nixpacks.toml`** - Frontend build configuration
5. **`/app/frontend/railway.json`** - Frontend deployment settings
6. **`/app/frontend/Procfile`** - Frontend start command

## Quick Deployment Steps

### 1. Push Code to GitHub (if not already done)
```bash
git add .
git commit -m "Railway deployment configuration"
git push origin main
```

### 2. Create Railway Project
- Go to https://railway.app
- Click "New Project" → "Deploy from GitHub repo"
- Select your repository

### 3. Deploy Backend
1. **Add Service**: Click "+ New" → Select your repo
2. **Set Root Directory**: Settings → Root Directory = `backend`
3. **Add MongoDB**: "+ New" → "Database" → "Add MongoDB"
4. **Set Environment Variables**:
   ```
   MONGO_URL=<copy from MongoDB service>
   JWT_SECRET_KEY=your-random-secret-key-here
   OPENAI_API_KEY=your-key-or-emergent-llm-key
   MAX_CONCURRENT=10
   MAX_CONCURRENT_SCANS=5
   ```
5. **Deploy**: Railway will automatically build and deploy
6. **Copy Backend URL**: e.g., `https://your-backend.up.railway.app`

### 4. Deploy Frontend
1. **Add Service**: Click "+ New" → Select same repo
2. **Set Root Directory**: Settings → Root Directory = `frontend`
3. **Set Environment Variable**:
   ```
   REACT_APP_BACKEND_URL=<your-backend-url-from-step-3>
   ```
4. **Deploy**: Railway will automatically build and deploy
5. **Copy Frontend URL**: e.g., `https://your-app.up.railway.app`

### 5. Initialize Admin User
- Visit: `https://your-backend.up.railway.app/api/setup-admin`
- Login credentials: `admin` / `Thommit@19`
- ⚠️ Change password after first login!

### 6. Test Application
- Visit your frontend URL
- Login with admin credentials
- Upload a test document image
- Verify scanning, OCR, and PDF export work

## What's Different from Previous Instructions?

### Backend Changes:
- ✅ Uses `python3 -m pip install` instead of `pip install` (fixes the error)
- ✅ Uses `python3 -m uvicorn` instead of `uvicorn` directly
- ✅ Explicitly includes `pip` in nixPkgs
- ✅ Upgrades pip before installing requirements

### Root Directory Configuration:
- ✅ Backend service: Root Directory = `backend`
- ✅ Frontend service: Root Directory = `frontend`
- ✅ This tells Railway which folder to build from

## Troubleshooting

### Build Still Fails?
1. Check Railway build logs for specific errors
2. Verify Root Directory is set correctly (without leading `/`)
3. Ensure all required files exist in backend/frontend folders
4. Try manual rebuild: Settings → "Redeploy"

### MongoDB Connection Issues?
1. Verify MONGO_URL is copied correctly from MongoDB service
2. Add database name to connection string: `/document_scanner`
3. Check MongoDB service is running

### Frontend Can't Connect to Backend?
1. Verify REACT_APP_BACKEND_URL has correct backend URL
2. Ensure URL starts with `https://` and has no trailing slash
3. Check backend CORS settings allow frontend domain

## Environment Variables Summary

### Backend Required Variables:
```env
MONGO_URL=mongodb://user:pass@host:port/document_scanner
JWT_SECRET_KEY=generate-random-string-here
OPENAI_API_KEY=sk-... (or Emergent LLM Key)
MAX_CONCURRENT=10
MAX_CONCURRENT_SCANS=5
UVICORN_TIMEOUT=300
```

### Frontend Required Variable:
```env
REACT_APP_BACKEND_URL=https://your-backend.up.railway.app
```

## Next Steps

1. ✅ Deploy successfully
2. ✅ Test all features
3. ✅ Change admin password
4. ✅ Add more users via admin panel
5. ✅ Monitor usage and logs
6. ⚠️ Update CORS in production for security

## Cost Estimate

For 30 concurrent users:
- Backend: ~$5-10/month
- Frontend: ~$5-10/month
- MongoDB: ~$5-15/month
- **Total**: $15-35/month

## Need Help?

See detailed guide: `/app/RAILWAY_DEPLOYMENT_GUIDE.md`
