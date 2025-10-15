# 🚀 Heroku Deployment Checklist

## ✅ Pre-Deployment Verification

### Required Files (All Present ✓)
- [x] `Procfile` - Heroku process configuration
- [x] `runtime.txt` - Python version specification (3.11.5)
- [x] `requirements.txt` - Python dependencies with gunicorn & psycopg2-binary
- [x] `.gitignore` - Excludes venv/, .env, *.db files
- [x] `.env.example` - Template for environment variables
- [x] `config.py` - Production/Development configurations
- [x] `manage.py` - Application entry point
- [x] `migrations/` - Database migration files

### Configuration Verification ✓

#### `Procfile` Contents:
```
web: gunicorn manage:app
```
✅ Uses `gunicorn` for production server  
✅ Points to correct app instance

#### `runtime.txt` Contents:
```
python-3.11.5
```
✅ Specifies supported Python version

#### `config.py` Features:
✅ Production and Development configs  
✅ Reads `DATABASE_URL` from environment  
✅ Converts Heroku's `postgres://` to `postgresql://`  
✅ Reads `SECRET_KEY` from environment  
✅ SQLite fallback for local dev  

#### `requirements.txt` Essentials:
✅ `gunicorn==21.2.0` - WSGI server  
✅ `psycopg2-binary==2.9.9` - PostgreSQL adapter  
✅ `Flask==3.0.0` - Framework  
✅ `Flask-SQLAlchemy==3.1.1` - Database ORM  
✅ `Flask-Migrate==4.0.5` - Database migrations  

---

## 📋 Deployment Steps

### 1. Initialize Git Repository (if not done)
```powershell
git init
git add .
git commit -m "Initial commit for Meeting Notes App"
```

### 2. Login to Heroku
```powershell
heroku login
```

### 3. Create Heroku App
```powershell
# Replace 'your-app-name' with your desired name
heroku create your-app-name
```

**Expected Output:**
- App URL: `https://your-app-name.herokuapp.com/`
- Git remote added: `heroku`

### 4. Add PostgreSQL Database
```powershell
heroku addons:create heroku-postgresql:essential-0
```

**Note:** `essential-0` is the free tier (as of October 2025)

**Verify database added:**
```powershell
heroku config
```
You should see `DATABASE_URL` variable.

### 5. Set Environment Variables
```powershell
# Set production environment
heroku config:set FLASK_ENV=production

# Set a strong secret key (generate one!)
heroku config:set SECRET_KEY=$(python -c "import secrets; print(secrets.token_hex(32))")
```

**Verify configuration:**
```powershell
heroku config
```

### 6. Deploy Application
```powershell
git push heroku main
```

**What happens:**
- Heroku detects Python app from `runtime.txt`
- Installs dependencies from `requirements.txt`
- Runs `Procfile` command to start `gunicorn`

### 7. Run Database Migrations
```powershell
heroku run flask db upgrade
```

**Expected Output:**
```
Running migrations...
INFO  [alembic.runtime.migration] Context impl PostgresImpl.
INFO  [alembic.runtime.migration] Will assume transactional DDL.
INFO  [alembic.runtime.migration] Running upgrade -> b8f10d110240
```

### 8. Open Your App
```powershell
heroku open
```

Your browser will open: `https://your-app-name.herokuapp.com/`

---

## 🔍 Post-Deployment Verification

### Check App Status
```powershell
heroku ps
```
Expected: `web.1: up`

### View Logs (Real-time)
```powershell
heroku logs --tail
```

### Check Database Connection
```powershell
heroku run python -c "from app import create_app, db; app = create_app('production'); app.app_context().push(); print('Tables:', db.engine.table_names())"
```

### Access Heroku PostgreSQL
```powershell
heroku pg:info
```

---

## 🛠️ Common Commands

### Restart Dynos
```powershell
heroku restart
```

### Run Flask Shell on Heroku
```powershell
heroku run flask shell
```

### Run Migrations
```powershell
# Create new migration
heroku run flask db migrate -m "description"

# Apply migrations
heroku run flask db upgrade

# Rollback migration
heroku run flask db downgrade
```

### Reset Database (⚠️ DESTROYS DATA)
```powershell
heroku pg:reset DATABASE_URL --confirm your-app-name
heroku run flask db upgrade
```

### View Environment Variables
```powershell
heroku config
```

### Set Additional Config
```powershell
heroku config:set KEY=VALUE
```

---

## 🐛 Troubleshooting

### Issue: App Crashes on Startup
**Check logs:**
```powershell
heroku logs --tail
```

**Common causes:**
- Missing environment variables
- Database connection issues
- Import errors in code

### Issue: Database Connection Failed
**Verify DATABASE_URL:**
```powershell
heroku config:get DATABASE_URL
```

**Check if it starts with `postgresql://` (not `postgres://`)**  
→ Our `config.py` handles this conversion automatically ✓

### Issue: Migrations Not Applied
**Run manually:**
```powershell
heroku run flask db upgrade
```

**Check migration history:**
```powershell
heroku run flask db current
```

### Issue: Static Files Not Loading
**Check Procfile has correct command:**
```
web: gunicorn manage:app
```

**Flask serves static files automatically in production mode** ✓

---

## 🔒 Security Best Practices

### ✅ Completed:
- [x] SECRET_KEY from environment variable
- [x] DATABASE_URL from environment variable
- [x] `.env` file in `.gitignore`
- [x] No hardcoded credentials in code
- [x] Debug mode OFF in production

### Before Going Live:
- [ ] Generate strong SECRET_KEY
- [ ] Enable HTTPS only (Heroku does this by default)
- [ ] Set up user authentication properly
- [ ] Implement rate limiting (consider Flask-Limiter)
- [ ] Add CSRF protection (Flask-WTF)
- [ ] Sanitize user inputs (bleach library already included ✓)

---

## 📊 Monitoring

### View App Metrics
```powershell
heroku logs --tail
```

### PostgreSQL Database Size
```powershell
heroku pg:info
```

### Dyno Usage
```powershell
heroku ps
```

---

## 🎯 Quick Deploy Workflow

After making changes locally:

```powershell
# 1. Test locally
python manage.py runserver

# 2. Commit changes
git add .
git commit -m "Your commit message"

# 3. Push to Heroku
git push heroku main

# 4. Run migrations if needed
heroku run flask db upgrade

# 5. Restart if necessary
heroku restart

# 6. Check logs
heroku logs --tail
```

---

## ✨ Your App is Ready for Heroku!

All configuration files are properly set up:
- ✅ Database migrations configured
- ✅ Production settings ready
- ✅ Environment variables templated
- ✅ Gunicorn configured
- ✅ PostgreSQL support included

**Just follow the deployment steps above and you're live! 🚀**
