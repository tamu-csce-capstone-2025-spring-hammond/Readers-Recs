# Reader’s Recs
**Enhancing Book Discovery & Interaction with ML-Driven Recommendations**

## Table of Contents
- [Reader’s Recs](#readers-recs)
- [Table of Contents](#table-of-contents)
- [Dev Setup](#dev-setup)
  - [System Requirements](#system-requirements)
  - [Making a Local Development Branch](#making-a-local-development-branch)
  - [Cloning the Repository](#cloning-the-repository)
  - [Installing Dependencies](#installing-dependencies)
  - [Setting Up the Environment File](#setting-up-the-environment-file)
  - [API Endpoint Configuration](#api-endpoint-configuration)
  - [Starting Redis](#starting-redis)
- [Running Locally](#running-locally)
  - [Backend](#backend)
  - [Frontend](#frontend)
  - [(Optional) Virtual Environment](#optional-virtual-environment)
- [Testing](#testing)
  - [Running the Linter](#running-the-linter)
  - [Running Python Backend Tests](#running-python-backend-tests)
- [Deploying](#deploying)
- [Troubleshooting](#troubleshooting)

---

# Dev Setup

## System Requirements
- **Operating Systems:** Windows 10+ or macOS 10.15+
- **Software Needed:**
  - Python 3.10 or higher
  - Node.js 18+ and npm 9+
  - Redis (required to run the ML model)

Check installed versions:
```bash
python --version
node --version
npm --version
```

## Making a Local Development Branch
Always work on a feature branch, not directly on `main` or `development`:
```bash
git fetch origin
git checkout development
git pull origin development
git checkout -b <feature>-dev
```
Pull requests should be submitted to `development` first.

## Cloning the Repository
```bash
git lfs install --skip-smudge
git clone https://github.com/tamu-csce-capstone-2025-spring-hammond/Readers-Recs.git
```

## Installing Dependencies

### Python
```bash
cd .github/workflows
pip install -r requirements.txt
```

### JavaScript (Frontend)
```bash
cd frontend
npm install react react-router-dom
```

## Setting Up the Environment File
Create a `.env` file at the root of the project with the following structure:
```env
MONGO_URI=
GOOGLE_CLIENT_ID=
GOOGLE_CLIENT_SECRET=
FRONTEND_URL=http://localhost:3000
BACKEND_URL=http://localhost:8000
```

- `MONGO_URI`: MongoDB connection string  
- `GOOGLE_CLIENT_ID`: OAuth client ID  
- `GOOGLE_CLIENT_SECRET`: OAuth secret  
- `FRONTEND_URL`: Local frontend URL  
- `BACKEND_URL`: Local backend URL  

> Contact a project administrator for credentials. Do not commit your `.env` file.

## API Endpoint Configuration
Modify `frontend/src/api.js`:
- Comment out the production backend URL.
- Uncomment the local backend URL.

Example:
```javascript
const BACKEND_URL = "http://localhost:8000";
// const BACKEND_URL = "https://readers-recs-production.up.railway.app";
```

## Starting Redis
**macOS:**
```bash
brew install redis
brew services start redis
```
**Windows:**
```bash
redis-server
```

---

# Running Locally

## Backend
Start the backend server:
```bash
cd backend
python -m main
```

## Frontend
In a new terminal window:
```bash
cd frontend
npm start
```
The app will be available at [http://localhost:3000](http://localhost:3000).

## (Optional) Virtual Environment
If using a virtual environment:
```bash
source backend/book_recommender_env/bin/activate
```

---

# Testing

## Running the Linter
```bash
flake8 .
black .
```

## Running Python Backend Tests
Generate a test coverage report:
```bash
pytest --cov=backend --cov-config=.coveragerc --cov-report=html:htmlcov tests/
```

---

# Deploying
Deployment to production is handled through [Vercel](https://vercel.com/):
```bash
npm install -g vercel
vercel login
vercel
```
Add environment variables:
```bash
vercel env add <VARIABLE_NAME> <VALUE>
```

---

# Troubleshooting
If you experience issues with dependencies:
```bash
cd frontend
Remove-Item -Recurse -Force .\node_modules
Remove-Item .\package-lock.json
npm cache clean --force
npm install
```
If problems persist, repeat the steps in the root directory.

---

# Website
[www.readersrecs.com](https://www.readersrecs.com)
