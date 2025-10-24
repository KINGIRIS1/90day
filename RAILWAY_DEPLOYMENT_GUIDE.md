# Railway Deployment Guide for Document Scanner App

This guide will help you deploy the Vietnamese Document Scanner application to Railway with proper support for concurrent users.

## Prerequisites

1. **Railway Account**: Sign up at https://railway.app
2. **GitHub Repository**: Push your code to a GitHub repository (or use Railway CLI)
3. **MongoDB Database**: You'll need a MongoDB connection string (Railway provides MongoDB addon, or use MongoDB Atlas)

## Architecture Overview

The application consists of two services:
- **Backend**: FastAPI (Python) service on port 8001
- **Frontend**: React application served via `serve` package

## Step-by-Step Deployment

### Option 1: Deploy via Railway Dashboard (Recommended)

#### Step 1: Create New Project
1. Go to https://railway.app/dashboard
2. Click "New Project"
3. Select "Deploy from GitHub repo" (or "Empty Project" if deploying manually)

#### Step 2: Add MongoDB Database
1. In your project dashboard, click "+ New"
2. Select "Database" → "Add MongoDB"
3. Railway will provision a MongoDB instance
4. Copy the connection string from the MongoDB service variables (it will look like: `mongodb://mongo:password@containers-us-west-xxx.railway.app:6379`)

#### Step 3: Deploy Backend Service

1. Click "+ New" → "GitHub Repo" (if using GitHub) or "Empty Service"
2. Select your repository
3. **Important: Configure the service root directory**
   - Go to service Settings
   - Under "Build & Deploy"
   - Set **Root Directory** to `/backend` or `backend` (without leading slash in new Railway UI)
   - Set **Builder** to "Nixpacks" (should be auto-detected)

4. **Configure Environment Variables**:
   Go to service Variables tab and add:
   ```
   MONGO_URL=mongodb://mongo:password@containers-us-west-xxx.railway.app:6379/document_scanner
   JWT_SECRET_KEY=your-super-secret-jwt-key-change-this-in-production
   OPENAI_API_KEY=your-openai-key (or use Emergent LLM Key)
   MAX_CONCURRENT=10
   MAX_CONCURRENT_SCANS=5
   UVICORN_TIMEOUT=300
   PORT=8001
   ```

   **Important Notes**:
   - Replace `MONGO_URL` with your actual MongoDB connection string from Step 2
   - Generate a strong random string for `JWT_SECRET_KEY`
   - If you have Emergent LLM Key, you can use that instead of OPENAI_API_KEY
   - The `PORT` variable will be automatically set by Railway, but backend expects 8001

5. **Verify Build Configuration**:
   - The `nixpacks.toml` file in the backend directory will be automatically detected
   - It should use Python 3.10 with pip, cairo, and pango packages
   - If build fails, check the logs for specific errors

6. **Deploy**:
   - Railway will automatically deploy after you save the configuration
   - Monitor the deployment logs
   - Once deployed, copy the public URL (e.g., `https://your-backend.up.railway.app`)

#### Step 4: Deploy Frontend Service

1. Click "+ New" → "GitHub Repo" (same repository) or "Empty Service"
2. **Important: Configure the service root directory**
   - Go to service Settings
   - Under "Build & Deploy"
   - Set **Root Directory** to `/frontend` or `frontend`
   - Set **Builder** to "Nixpacks"

3. **Configure Environment Variables**:
   Go to service Variables tab and add:
   ```
   REACT_APP_BACKEND_URL=https://your-backend.up.railway.app
   PORT=3000
   ```
   
   **Important**: Replace `https://your-backend.up.railway.app` with the actual backend URL from Step 3

4. **Deploy**:
   - Railway will automatically build and deploy
   - It will run `yarn install`, `yarn build`, and serve the build folder
   - Once deployed, you'll get a public URL (e.g., `https://your-app.up.railway.app`)

#### Step 5: Initialize Admin User

After both services are deployed:

1. Open your browser and navigate to: `https://your-backend.up.railway.app/api/setup-admin`
2. You should see a JSON response confirming admin user creation
3. Default admin credentials:
   - Username: `admin`
   - Password: `Thommit@19`

**Important**: Change the admin password after first login!

#### Step 6: Test the Application

1. Navigate to your frontend URL: `https://your-app.up.railway.app`
2. You should see the login page
3. Login with admin credentials
4. Test the scanning functionality:
   - Upload a test image
   - Verify OCR and document naming works
   - Check PDF export
   - Test batch scanning

### Option 2: Deploy via Railway CLI

#### Step 1: Install Railway CLI
```bash
npm install -g @railway/cli
railway login
```

#### Step 2: Initialize Project
```bash
railway init
railway link
```

#### Step 3: Add MongoDB
```bash
railway add --database mongodb
```

#### Step 4: Deploy Backend
```bash
cd backend
railway up
```

#### Step 5: Set Environment Variables
```bash
railway variables set MONGO_URL="your-mongodb-url"
railway variables set JWT_SECRET_KEY="your-secret-key"
railway variables set OPENAI_API_KEY="your-openai-key"
railway variables set MAX_CONCURRENT=10
railway variables set MAX_CONCURRENT_SCANS=5
railway variables set UVICORN_TIMEOUT=300
```

#### Step 6: Deploy Frontend
```bash
cd ../frontend
railway up
railway variables set REACT_APP_BACKEND_URL="your-backend-url"
```

## Troubleshooting Common Issues

### Issue 1: "pip: command not found"
**Solution**: The updated `nixpacks.toml` uses `python3 -m pip` instead of `pip` directly. Make sure you're using the latest configuration files.

### Issue 2: Build Fails with "No such file or directory"
**Solution**: Ensure the Root Directory is correctly set to `backend` or `frontend` in Railway service settings.

### Issue 3: Frontend Can't Connect to Backend
**Solution**: 
- Verify `REACT_APP_BACKEND_URL` is set correctly in frontend environment variables
- Make sure backend URL includes `https://` and doesn't have a trailing slash
- Check CORS settings in backend `server.py`

### Issue 4: MongoDB Connection Fails
**Solution**:
- Verify `MONGO_URL` format is correct
- Ensure MongoDB service is running on Railway
- Check that database name is included in the connection string

### Issue 5: Images Not Processing (502/504 Errors)
**Solution**:
- Increase `UVICORN_TIMEOUT` to 300 or higher
- Check Railway service logs for memory issues
- Consider upgrading Railway plan for more resources
- Verify OpenAI API key is valid

### Issue 6: Services Keep Restarting
**Solution**:
- Check deployment logs for errors
- Verify all required environment variables are set
- Ensure `requirements.txt` and `package.json` have all dependencies
- Check Railway service metrics for memory/CPU limits

## Scaling Configuration

For 30+ concurrent users, consider:

1. **Backend Resources**:
   - Minimum: 1GB RAM, 1 vCPU
   - Recommended: 2GB RAM, 2 vCPU
   - Set `MAX_CONCURRENT=15` and `MAX_CONCURRENT_SCANS=10`

2. **Frontend Resources**:
   - Minimum: 512MB RAM
   - Recommended: 1GB RAM

3. **MongoDB**:
   - Use Railway's Persistent Volume addon or MongoDB Atlas
   - Enable connection pooling
   - Monitor database size

4. **Railway Plan**:
   - Starter plan may be sufficient for testing
   - Developer plan ($5/month) recommended for production
   - Team plan for higher resource limits

## Monitoring and Maintenance

1. **View Logs**:
   ```bash
   railway logs --service backend
   railway logs --service frontend
   ```

2. **Monitor Metrics**:
   - Check Railway dashboard for CPU, memory, and network usage
   - Set up alerts for service downtime

3. **Database Backups**:
   - Railway doesn't automatically backup databases
   - Consider using MongoDB Atlas for automatic backups
   - Or implement manual backup scripts

4. **Update Deployment**:
   - Push changes to GitHub (if using GitHub integration)
   - Railway will automatically rebuild and redeploy
   - Or use `railway up` with CLI

## Security Recommendations

1. **Change Default Credentials**:
   - Change admin password immediately after first login
   - Rotate JWT_SECRET_KEY periodically

2. **Environment Variables**:
   - Never commit `.env` files to Git
   - Use Railway's environment variable management
   - Rotate API keys regularly

3. **CORS Configuration**:
   - Update CORS origins in `backend/server.py` to only allow your frontend domain
   - Remove wildcard origins in production

4. **HTTPS Only**:
   - Railway provides SSL certificates automatically
   - Ensure all API calls use HTTPS

## Cost Estimation

Railway pricing (as of 2024):
- **Starter**: $5/month per service
- **Developer**: $20/month (multiple services included)
- **Team**: Custom pricing

Estimated monthly cost for this application:
- Backend service: $5-10
- Frontend service: $5-10
- MongoDB: $5-15 (depending on storage)
- **Total**: ~$15-35/month

For 30 concurrent users with moderate usage, expect:
- **Developer plan** should be sufficient
- Monitor usage and upgrade if needed

## Support

If you encounter issues:
1. Check Railway documentation: https://docs.railway.app
2. Review deployment logs in Railway dashboard
3. Check this application's GitHub issues
4. Contact Railway support for platform-specific issues

## Next Steps After Deployment

1. ✅ Test all features thoroughly
2. ✅ Set up monitoring and alerts
3. ✅ Configure backups for MongoDB
4. ✅ Update CORS settings for production
5. ✅ Change default admin credentials
6. ✅ Set up custom domain (optional)
7. ✅ Implement rate limiting for API endpoints (optional)
8. ✅ Add logging/analytics (optional)

---

**Deployment Configuration Files**:
- ✅ `/backend/nixpacks.toml` - Backend build configuration (FIXED: pip issue resolved)
- ✅ `/backend/railway.json` - Backend Railway settings
- ✅ `/backend/Procfile` - Backend start command
- ✅ `/frontend/nixpacks.toml` - Frontend build configuration
- ✅ `/frontend/railway.json` - Frontend Railway settings
- ✅ `/frontend/Procfile` - Frontend start command

All configuration files are included in the repository and ready for Railway deployment.
