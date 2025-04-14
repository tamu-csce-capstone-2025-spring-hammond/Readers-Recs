# Reader's Recs
Enhancing Book Discovery & Interaction with ML-Driven Recommendations

# Table of Contents
- [Reader's Recs](#readers-recs)
- [Table of Contents](#table-of-contents)
- [Dev Setup](#dev-setup)
  - [Making a Local Development Branch](#making-a-local-development-branch)
  - [Dependencies](#dependencies)
    - [Python](#python)
    - [JavaScript](#javascript)
- [Running Locally](#running-locally)
  - [Backend](#backend)
    - [Database API Connection](#database-api-connection)
    - [ML Model](#ml-model)
   - [ML Model](#ml-model)
   - [Database Calls](#database-calls)
  - [Frontend](#frontend)
  - [Entering the Virtual Environment](#entering-the-virtual-environment)
- [Testing](#testing)
  - [Running the Linter](#running-the-linter)
- [Deploying](#deploying)
- [Troubleshooting](#troubleshooting)

# Dev Setup
## Making a Local Development Branch
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
### Database API Connection
```
cd backend
python -m main
```
### ML Model
```
cd backend
python .\book-rec-model.py
```
### Database Calls
```
python -m backend.main
```

## Frontend
```
cd frontend
npm start
```

## Entering the virtual environment
Run the following from the project directory.
```
source backend/book_recommender_env/bin/activate
```

# Testing
## Running the Linter
Run the following to analyze the code for programming errors, bugs, stylistic errors and suspicious constructs.
```
flake8 .
black .
```

# Deploying
Deployment will occur during sprint releases from the `main` branch, and is done through vercel.
```
npm install -g vercel
vercel login
vercel
```
Any environment variables can be added to the Vercel through `vercel env add <VARIABLE_NAME> <VALUE>`.

# Troubleshooting
In the case of issues with nested React environments competing, run the following commands within `frontend`.
```
Remove-Item -Recurse -Force .\node_modules
Remove-Item .\package-lock.json
npm cache clean --force
npm install
```
If this does not resolve the issue, try running these commands once again in the root folder.