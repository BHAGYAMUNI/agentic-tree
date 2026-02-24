# 🎯 COPY-PASTE COMMANDS FOR DEPLOYMENT

Just copy and paste these commands in order!

---

## PART 1: GitHub Setup (10 minutes)

### Step 1: Clone Your Repository
```bash
cd Desktop
git clone https://github.com/YOUR-USERNAME/agentic-tree.git
cd agentic-tree
```

### Step 2: Add Your Code to Git
```bash
git add .
git commit -m "Initial commit: Tree AI application"
git push origin main
```

**Done! Your code is on GitHub ✅**

---

## PART 2: Test Locally with Docker (10 minutes)

### Step 1: Start Docker
```bash
# From project root
docker-compose up -d --build
```

Wait 30 seconds for containers to start...

### Step 2: Check Status
```bash
docker-compose ps
```

Should show all containers running ✅

### Step 3: Seed Database
```bash
docker-compose exec backend python seed.py
```

### Step 4: Test in Browser
```
Frontend: http://localhost:5173
Backend API Docs: http://localhost:8000/docs

Login with:
Email: demo@example.com
Password: demo123
```

### Step 5: Stop when done
```bash
docker-compose down
```

**Done! Local testing complete ✅**

---

## PART 3: Deploy Backend to Heroku (15 minutes)

### Step 1: Install Heroku CLI
Download from: https://devcenter.heroku.com/articles/heroku-cli

### Step 2: Login to Heroku
```bash
heroku login
```

### Step 3: Create Backend App
```bash
heroku create tree-ai-backend-YOURNAME
```

Replace YOURNAME with something unique like your firstname or student ID

### Step 4: Add PostgreSQL Database
```bash
heroku addons:create heroku-postgresql:hobby-dev -a tree-ai-backend-YOURNAME
```

### Step 5: Set Environment Variables
```bash
heroku config:set JWT_SECRET=change-this-to-random-string -a tree-ai-backend-YOURNAME
heroku config:set ENVIRONMENT=production -a tree-ai-backend-YOURNAME
```

### Step 6: Add Heroku Remote
```bash
heroku git:remote -a tree-ai-backend-YOURNAME
```

### Step 7: Deploy Backend
```bash
git push heroku main
```

Wait for deployment to complete...

### Step 8: Run Migrations and Seed Data
```bash
heroku run alembic upgrade head -a tree-ai-backend-YOURNAME
heroku run python seed.py -a tree-ai-backend-YOURNAME
```

### Step 9: Test Backend
Open in browser:
```
https://tree-ai-backend-YOURNAME.herokuapp.com/docs
```

You should see API documentation ✅

**Done! Backend deployed ✅**

Save these URLs:
- Backend: `https://tree-ai-backend-YOURNAME.herokuapp.com`
- API Docs: `https://tree-ai-backend-YOURNAME.herokuapp.com/docs`

---

## PART 4: Deploy Frontend to Heroku (15 minutes)

### Step 1: Create Frontend App
```bash
heroku create tree-ai-frontend-YOURNAME
```

Use same YOURNAME as backend

### Step 2: Set Backend URL
```bash
heroku config:set VITE_API_URL=https://tree-ai-backend-YOURNAME.herokuapp.com -a tree-ai-frontend-YOURNAME
```

### Step 3: Create Procfile for Frontend
```bash
cd frontend
echo "web: npm run build && npm run preview" > Procfile
cd ..
```

### Step 4: Add Heroku Remote for Frontend
```bash
cd frontend
heroku git:remote -a tree-ai-frontend-YOURNAME
cd ..
```

### Step 5: Deploy Frontend
```bash
cd frontend
git push heroku main
cd ..
```

Wait for deployment to complete...

### Step 6: Test Frontend
Open in browser:
```
https://tree-ai-frontend-YOURNAME.herokuapp.com
```

Login with:
```
Email: demo@example.com
Password: demo123
```

**Done! Frontend deployed ✅**

Save this URL:
- Frontend: `https://tree-ai-frontend-YOURNAME.herokuapp.com`

---

## PART 5: Final Git Push

### Push Deployment Files to GitHub
```bash
git add .
git commit -m "Add deployment guides and configuration"
git push origin main
```

---

## PART 6: Recording Demo Video

### Using Built-in Screen Recorder

**Windows:**
1. Press Windows + Shift + S
2. Select "Video" at bottom
3. Select area to record
4. Click "Start"
5. Do your demo
6. Click stop

**macOS:**
1. Press Command + Shift + 5
2. Select "Record Screen"
3. Click to record

**Linux:**
Install OBS Studio:
```bash
sudo apt install obs-studio
```

---

## 📝 SUBMISSION TEMPLATE

Copy this and fill in:

```
TREE AI - PROJECT SUBMISSION

GitHub Repository:
https://github.com/YOUR-USERNAME/agentic-tree

Frontend URL:
https://tree-ai-frontend-YOURNAME.herokuapp.com

Backend URL:
https://tree-ai-backend-YOURNAME.herokuapp.com

API Documentation:
https://tree-ai-backend-YOURNAME.herokuapp.com/docs

Demo Video:
[YouTube link will be here after you upload]

Test Account:
Email: demo@example.com
Password: demo123
```

---

## 🔍 VERIFICATION CHECKLIST

After everything is deployed, verify:

```bash
# 1. Check GitHub
✅ https://github.com/YOUR-USERNAME/agentic-tree (public)
✅ README.md exists
✅ docker-compose.yml exists
✅ Dockerfiles exist
✅ All code is there

# 2. Check Frontend
✅ https://tree-ai-frontend-YOURNAME.herokuapp.com loads
✅ Can login
✅ Can create tree
✅ Can insert nodes

# 3. Check Backend
✅ https://tree-ai-backend-YOURNAME.herokuapp.com/docs shows API
✅ Can make API requests in Swagger

# 4. Check Database
✅ Test user exists (demo@example.com)
✅ Can perform tree operations
```

---

## 📊 QUICK REFERENCE

| Item | Your Value |
|------|-----------|
| GitHub Username | _________________ |
| Unique Name (YOURNAME) | _________________ |
| Backend App Name | tree-ai-backend-YOURNAME |
| Frontend App Name | tree-ai-frontend-YOURNAME |
| Frontend URL | https://tree-ai-frontend-YOURNAME.herokuapp.com |
| Backend URL | https://tree-ai-backend-YOURNAME.herokuapp.com |
| Demo Video URL | _________________ |

---

## ✅ YOU'RE DONE!

When everything above is complete:

1. ✅ Code is on GitHub
2. ✅ Frontend is deployed and live
3. ✅ Backend is deployed and live
4. ✅ Database is seeded
5. ✅ Demo video is recorded
6. ✅ README is complete

**Submit your professor:**
- GitHub repo link
- Frontend URL
- Backend URL
- Demo video link

🎉 **Congratulations! You're ready to submit!** 🎉
