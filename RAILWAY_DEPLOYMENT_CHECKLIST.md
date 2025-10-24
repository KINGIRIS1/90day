# Railway Deployment Checklist

Use this checklist to ensure smooth deployment to Railway.

## Pre-Deployment Checklist

### Code Preparation
- [ ] All code committed to Git repository
- [ ] Repository pushed to GitHub/GitLab/Bitbucket
- [ ] No sensitive data in code (API keys, passwords)
- [ ] `.env` files are in `.gitignore`

### Configuration Files Verified
- [ ] `/app/backend/nixpacks.toml` exists with correct pip commands
- [ ] `/app/backend/railway.json` exists
- [ ] `/app/backend/Procfile` exists
- [ ] `/app/frontend/nixpacks.toml` exists
- [ ] `/app/frontend/railway.json` exists
- [ ] `/app/frontend/Procfile` exists
- [ ] `/app/backend/requirements.txt` is complete
- [ ] `/app/frontend/package.json` includes "serve" package

### API Keys Ready
- [ ] MongoDB connection string (Railway MongoDB or Atlas)
- [ ] JWT_SECRET_KEY generated (random 32+ character string)
- [ ] OpenAI API key (or Emergent LLM Key ready)

## Railway Setup Checklist

### Project Creation
- [ ] Railway account created at https://railway.app
- [ ] New project created in Railway dashboard
- [ ] GitHub repository connected to Railway (if using GitHub deployment)

### MongoDB Service
- [ ] MongoDB service added to project (+ New → Database → Add MongoDB)
- [ ] MongoDB connection string copied from service variables
- [ ] Database name added to connection string (e.g., `/document_scanner`)

### Backend Service Setup
- [ ] New service created (+ New → GitHub Repo or Empty Service)
- [ ] Root Directory set to `backend` (Settings → Root Directory)
- [ ] Builder set to "Nixpacks"
- [ ] All environment variables added:
  - [ ] `MONGO_URL` = (MongoDB connection string)
  - [ ] `JWT_SECRET_KEY` = (random secret key)
  - [ ] `OPENAI_API_KEY` = (your API key)
  - [ ] `MAX_CONCURRENT` = 10
  - [ ] `MAX_CONCURRENT_SCANS` = 5
  - [ ] `UVICORN_TIMEOUT` = 300
- [ ] Service deployed successfully
- [ ] Backend URL copied (e.g., `https://xxx.up.railway.app`)

### Frontend Service Setup
- [ ] New service created (+ New → GitHub Repo or Empty Service)
- [ ] Root Directory set to `frontend` (Settings → Root Directory)
- [ ] Builder set to "Nixpacks"
- [ ] Environment variable added:
  - [ ] `REACT_APP_BACKEND_URL` = (backend URL from above)
- [ ] Service deployed successfully
- [ ] Frontend URL copied (e.g., `https://xxx.up.railway.app`)

## Post-Deployment Checklist

### Admin Setup
- [ ] Visited `https://backend-url.up.railway.app/api/setup-admin`
- [ ] Confirmed admin user created (JSON response)
- [ ] Admin credentials noted: `admin` / `Thommit@19`

### Basic Testing
- [ ] Frontend loads successfully at frontend URL
- [ ] Login page appears without errors
- [ ] Logged in with admin credentials
- [ ] Dashboard/main app loads

### Feature Testing
- [ ] Single image upload works
- [ ] Image scanning completes (OCR result appears)
- [ ] Document naming with short codes works
- [ ] PDF export (single) works
- [ ] Batch upload works (multiple images)
- [ ] Smart grouping works (multi-page documents)
- [ ] Scan history displays correctly
- [ ] Folder scanning works (ZIP upload)
- [ ] Rules management UI works (Quy Tắc tab)

### Performance Testing
- [ ] Upload speed acceptable
- [ ] Scanning completes within reasonable time (3-5s per image)
- [ ] No timeout errors (502/504)
- [ ] Multiple concurrent scans work

### Security Checklist
- [ ] Admin password changed from default
- [ ] CORS settings reviewed in `backend/server.py`
- [ ] Only frontend domain allowed in CORS origins (production)
- [ ] All API calls use HTTPS
- [ ] No sensitive data exposed in frontend

## Monitoring Setup (Optional but Recommended)

- [ ] Railway service metrics reviewed (CPU, Memory, Network)
- [ ] Logs checked for errors or warnings
- [ ] Alerts set up for service downtime
- [ ] Database size monitored
- [ ] Backup strategy implemented for MongoDB

## Production Readiness Checklist

### Code Quality
- [ ] All backend tests pass
- [ ] All frontend tests pass
- [ ] No console errors in browser
- [ ] No Python warnings in backend logs

### Configuration
- [ ] Environment variables double-checked
- [ ] All URLs use HTTPS
- [ ] CORS configured for production domain only
- [ ] Rate limiting considered (if needed)

### Documentation
- [ ] Deployment guide reviewed
- [ ] User credentials documented securely
- [ ] Admin panel usage documented
- [ ] Troubleshooting guide available

### Scaling Preparation
- [ ] Railway plan sufficient for expected load (30+ users)
- [ ] Resource limits configured (RAM, CPU)
- [ ] MAX_CONCURRENT values tuned for performance
- [ ] Database connection pool configured

## Troubleshooting Quick Reference

### Build Fails
- [ ] Check Root Directory is correct (`backend` or `frontend`)
- [ ] Verify all config files exist (nixpacks.toml, railway.json)
- [ ] Review build logs for specific errors
- [ ] Ensure requirements.txt/package.json are complete

### Backend Won't Start
- [ ] Check MONGO_URL is correct and accessible
- [ ] Verify all required environment variables are set
- [ ] Check backend logs for Python errors
- [ ] Ensure PORT variable is available (Railway sets this)

### Frontend Can't Connect
- [ ] Verify REACT_APP_BACKEND_URL is correct
- [ ] Ensure backend URL has `https://` and no trailing `/`
- [ ] Check CORS settings in backend allow frontend domain
- [ ] Test backend endpoints directly with curl/Postman

### Database Connection Issues
- [ ] Verify MongoDB service is running on Railway
- [ ] Check connection string format
- [ ] Ensure database name is in connection string
- [ ] Test connection from Railway backend service

### Performance Issues
- [ ] Increase UVICORN_TIMEOUT if seeing 502/504 errors
- [ ] Increase MAX_CONCURRENT and MAX_CONCURRENT_SCANS
- [ ] Check Railway service metrics for resource bottlenecks
- [ ] Consider upgrading Railway plan for more resources
- [ ] Verify OpenAI API key has sufficient quota

## Deployment Complete! 🎉

Once all checkboxes are marked, your application is successfully deployed to Railway!

### What's Next?
1. Share frontend URL with users
2. Monitor usage and logs
3. Set up regular database backups
4. Plan for scaling as user base grows
5. Keep dependencies updated
6. Monitor costs and optimize resources

### Need Help?
- See: `/app/RAILWAY_DEPLOYMENT_GUIDE.md` for detailed instructions
- See: `/app/RAILWAY_QUICK_START.md` for quick reference
- See: `/app/RAILWAY_FIX_SUMMARY.md` for technical details
- Railway Support: https://help.railway.app

---

**Deployment Date**: _______________
**Backend URL**: _______________
**Frontend URL**: _______________
**Admin Credentials**: admin / (new password after change)
**Railway Project**: _______________
