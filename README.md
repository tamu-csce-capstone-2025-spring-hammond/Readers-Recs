# Reader's Recs
Enhancing Book Discovery & Interaction with ML-Driven Recommendations

# Table of Contents
- [Dev Setup](#dev-setup)
  - [Making a Development Branch](#making-a-dev-branch)
  - [Dependencies](#dependencies)
    - [Python](#python)
    - [JavaScript](#javascript)
- [Running Locally](#running-locally)
  - [Backend](#backend)
  - [Frontend](#frontend)
- [Deploying](#deploying)

# Dev Setup
## Making a dev branch
Do not work directly on `main` or `development`, instead make a `<feature>-dev` or `<name>-dev` branch with
```
git fetch origin
git checkout development
git pull origin development
```
Then run either `git checkout -b <feature>-dev` or `git checkout -b <name>-dev`.

Pull requests should first go through `development`, then they will be merged to `main` all together.

## Dependencies
To run both the frontend and backend of the application, your system will need to have Python, Node.js, and npm installed.

### Python
```
cd .github/workflows
pip install -r requirements.txt
```

### JavaScript
```
cd frontend
npm install react react-router-dom
```

# Running Locally
## Backend
```
cd backend
python .\book-rec-model.py
```

## Frontend
```
cd frontend
npm start
```

# Deploying
Deployment will occur during sprint releases from the `main` branch, and is done through vercel.
```
npm install -g vercel
vercel login
vercel
```
Any environment variables can be added to the Vercel through `vercel env add <VARIABLE_NAME> <VALUE>`.
