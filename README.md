# NammaTN – AI Civic Connect
> AI-powered civic issue reporting and tracking platform for Tamil Nadu.

🌐 **Live Demo:** https://namma-tn-ewpq.onrender.com

> **Note:** NammaTN is a student-built prototype and is not an official government application.

A full-stack prototype that lets citizens report civic issues in Tamil, Tanglish, or English, then tracks those issues through an admin workflow.

> Prototype notice: this project is a student-built prototype and is not an official government application.

## Overview

NammaTN helps citizens report issues such as:
- water supply problems
- road and pothole issues
- drainage and flooding concerns
- waste dumping and sanitation complaints
- streetlight faults

The app uses AI to classify each complaint and stores it in MongoDB for citizen tracking and admin review.

## Features

- citizen registration and login
- civic issue complaint creation from natural language
- AI category and severity analysis
- district and area capture
- optional complaint proof upload via file or camera
- complaint tracking by ID
- admin dashboard with complaint status updates
- fallback local classifier if Gemini is unavailable

## Tech stack

- Frontend: React + Vite
- Backend: Python + Flask
- Database: MongoDB (with a local fallback for test environments)
- AI: Google Gemini API
- Testing: Pytest
- Auth: JWT

## Project structure

```text
NammaTN/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── ai.py
│   │   ├── auth.py
│   │   ├── config.py
│   │   ├── db.py
│   │   └── routes.py
│   ├── tests/
│   │   └── test_api.py
│   ├── .env.example
│   ├── .env
│   ├── requirements.txt
│   └── run.py
├── docs/
│   ├── AI-CHANGE-LOOP.md
│   ├── AI-TOOLS.md
│   ├── Architecture.md
│   ├── DEMO-SCRIPT.md
│   ├── Design.md
│   ├── PRESENTATION.md
│   └── UserGuide.md
├── evidence/
│   ├── RED-GREEN-RUN.md
│   ├── green-run.txt
│   └── red-run.txt
├── frontend/
│   ├── src/
│   │   ├── App.jsx
│   │   ├── api.js
│   │   ├── main.jsx
│   │   └── styles.css
│   ├── .env.example
│   ├── .gitignore
│   ├── index.html
│   ├── package.json
│   └── vite.config.js
├── .gitignore
├── e2e_test.py
├── README.md
├── test_api.py
└── requirements.txt
```

## Prerequisites

- Python 3.10+
- Node.js 20+
- MongoDB local instance or MongoDB Atlas connection
- Optional: Gemini API key for live AI classification

## Environment variables

Create a local backend/.env file with values similar to this, replacing placeholders with your own secure values:

```env
MONGO_URI=mongodb://localhost:27017
MONGO_DB=namma_tn
GEMINI_API_KEY=YOUR_GEMINI_API_KEY
FRONTEND_ORIGIN=http://localhost:5173
SECRET_KEY=change-me
JWT_ALGORITHM=HS256
JWT_EXP_SECONDS=86400
ADMIN_EMAIL=admin@namma.tn
ADMIN_PASSWORD=admin123
```

Do not commit real secrets to Git.

## MongoDB setup

### Local MongoDB
```powershell
mongod
```

Then use:
```env
MONGO_URI=mongodb://localhost:27017
MONGO_DB=namma_tn
```

### Atlas
Create a MongoDB Atlas cluster, get the connection string, and set it in backend/.env.

## Gemini setup

- create a Gemini API key in Google AI Studio
- add it to backend/.env as `GEMINI_API_KEY`
- if the key is missing or the call fails, the app falls back to a local classification algorithm

## Backend installation

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

## Backend run

```powershell
cd backend
.\.venv\Scripts\Activate.ps1
python run.py
```

Backend URL:
```text
http://127.0.0.1:5000
```

## Frontend installation

```powershell
cd frontend
npm install
```

## Frontend run

```powershell
cd frontend
npm run dev
```

Frontend URL:
```text
http://localhost:5173
```

## Health check

```text
http://127.0.0.1:5000/api/health
```

Expected JSON example:
```json
{"status":"ok","database":"connected"}
```

## Test command

```powershell
cd backend
python -m pytest -q
```

## Citizen demo flow

1. Register as a citizen.
2. Login.
3. Describe a problem in Tamil, Tanglish, or English.
4. Confirm the AI classification.
5. Add district, area, and optional duration.
6. Optionally upload a proof photo or capture one with the camera.
7. Submit the complaint and save the complaint ID.
8. Track the complaint from the citizen page.

## Admin demo flow

1. Log in with the admin account.
2. Open the Authority Dashboard.
3. Review complaint details and uploaded proof images.
4. Update complaint status from Submitted to In Progress and then Resolved.

## API endpoints

- POST /api/ai/analyze
- POST /api/complaints
- GET /api/complaints
- GET /api/complaints/my
- GET /api/complaints/<complaint_id>
- PATCH /api/complaints/<complaint_id>
- POST /api/auth/register
- POST /api/auth/login
- GET /api/auth/me
- POST /api/auth/logout
- GET /api/health

## Authentication

- JWT-based auth is used for citizen and admin flows.
- Protected routes require a Bearer token.
- Admin-only endpoints reject non-admin users with 403.

## Photo upload feature

The application includes an optional proof-image feature:
- citizens can upload file-based images
- browser camera capture is supported when the device allows it
- file type validation accepts only common image MIME types encoded as data URLs
- the photo is stored with the complaint and shown in the admin dashboard when present

## Security notes

- Never commit real secrets to Git.
- Keep API keys, MongoDB URIs, and credentials in local environment files only.
- .env files are not tracked by Git in this repo.
- The project is a prototype and should not be used as a production public service without a proper security review.

## Documentation

- [docs/Architecture.md](docs/Architecture.md)
- [docs/Design.md](docs/Design.md)
- [docs/UserGuide.md](docs/UserGuide.md)
- [docs/AI-CHANGE-LOOP.md](docs/AI-CHANGE-LOOP.md)
- [docs/AI-TOOLS.md](docs/AI-TOOLS.md)
- [docs/PRESENTATION.md](docs/PRESENTATION.md)
- [docs/DEMO-SCRIPT.md](docs/DEMO-SCRIPT.md)
- [evidence/RED-GREEN-RUN.md](evidence/RED-GREEN-RUN.md)

## Assessment evidence

- [evidence/red-run.txt](evidence/red-run.txt)
- [evidence/green-run.txt](evidence/green-run.txt)

## Notes

The current repo includes the required working app flow, assessment docs, and validation evidence. The backend also includes a MongoDB fallback used for safe local testing when no database server is running.

{
  "category": "flooding",
  "severity": "medium",
  "needs_location": true
}
```

The backend validates the model output before using it.

## 9. Reliability / fallback

The application should not depend blindly on the AI response.

If:

- Gemini API key is missing
- Gemini is unavailable
- Gemini returns malformed JSON
- Gemini returns an unsupported category

the backend falls back to deterministic keyword classification.

This makes the basic demo usable even if the external AI service is temporarily unavailable.

## 10. Assessment Red Run / Green Run

For the AI change-loop evidence, start with the working MVP.

Suggested change request:

> "Allow citizens to track complaint status through the chatbot using a complaint ID."

Then use your coding AI assistant to:

1. Inspect the existing code.
2. Implement the change.
3. Run tests.
4. Intentionally demonstrate a failing validation/test.
5. Ask the coding AI to diagnose and fix it.
6. Run the tests again.
7. Capture the final passing result.

Keep screenshots/logs of the change request, red run, fix, and green run for the assessment evidence.

## 11. Important safety / product boundary

NammaTN should **not** claim to be an official government portal.

It should also not invent:

- Official water-release schedules
- Government scheme eligibility
- Compensation decisions
- Official emergency instructions
- Government complaint resolution

For this prototype, the product is a **civic issue reporting and tracking assistant**.

## 12. Suggested demo story

1. Open NammaTN.
2. Type a Tanglish water complaint.
3. Show Gemini classification.
4. Provide Thanjavur + Thiruvaiyaru.
5. Create complaint.
6. Show generated complaint ID.
7. Open Authority Dashboard.
8. Show the new complaint.
9. Change `Submitted → In Progress`.
10. Track the complaint from the citizen screen.
11. Change it to `Resolved`.
12. Show the final status.

This gives a complete:

**Citizen → AI → REST API → MongoDB → Authority → Status tracking**

story.

## Official references

- MongoDB PyMongo documentation: urlPyMongo Driver Documentationhttps://www.mongodb.com/docs/languages/python/pymongo-driver/current/
- MongoDB Atlas / PyMongo quickstart: urlPyMongo Get Startedhttps://www.mongodb.com/docs/languages/python/pymongo-driver/current/get-started/
- Flask documentation: urlFlask Documentationhttps://flask.palletsprojects.com/
- Gemini API documentation: urlGemini API Documentationhttps://ai.google.dev/gemini-api/docs
#   N a m m a - T N - 
 
 
