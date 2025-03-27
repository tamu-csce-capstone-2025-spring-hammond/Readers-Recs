# Reader's Recs
Enhancing Book Discovery & Interaction with ML-Driven Recommendations

# Table of Contents
- [Reader's Recs](#readers-recs)
- [Table of Contents](#table-of-contents)
- [Dev Setup](#dev-setup)
  - [Making a dev branch](#making-a-dev-branch)
  - [Running the Linter](#running-the-linter)
  - [Entering the virtual environment](#entering-the-virtual-environment)
  - [Dependencies](#dependencies)
    - [Python](#python)
    - [JavaScript](#javascript)
- [Running Locally](#running-locally)
  - [Backend](#backend)
   - [ML Model](#ml-model)
   - [Database Calls](#database-calls)
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

## Running the Linter
To lint the code, run the commands below.
```
flake8 .
black .
```

## Entering the virtual environment
From the project directory, run:
```
source backend/book_recommender_env/bin/activate
```


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

# Deploying
Deployment will occur during sprint releases from the `main` branch, and is done through vercel.
```
npm install -g vercel
vercel login
vercel
```
Any environment variables can be added to the Vercel through `vercel env add <VARIABLE_NAME> <VALUE>`.
