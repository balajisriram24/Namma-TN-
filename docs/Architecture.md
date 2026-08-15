# Architecture

## 1. Overview

NammaTN – AI Civic Connect is a full-stack civic-reporting prototype for Tamil Nadu. Citizens describe a civic issue in Tamil, Tanglish, or English, and the system uses a lightweight classification flow to detect the issue category and severity before storing a complaint record in MongoDB.

The project is split into a React frontend and a Flask backend. The frontend handles user interaction, complaint entry, tracking, and administrative review. The backend exposes REST endpoints, validates requests, authenticates users, and persists complaint and user documents in MongoDB.

## 2. System architecture

The architecture follows a simple three-tier flow:

1. Frontend web app in React + Vite
2. Flask REST API for auth, AI analysis, complaint management, and admin actions
3. MongoDB for complaint and user persistence

A Gemini-based AI call is used for classification when a valid API key is present. If the live API is unavailable or no key is configured, the application falls back to a deterministic local classification function, so the prototype still works in a demo environment.

## 3. Frontend

The browser app is implemented in [frontend/src/App.jsx](../frontend/src/App.jsx) and styled by [frontend/src/styles.css](../frontend/src/styles.css).

Responsibilities:
- citizen registration and login
- AI complaint description flow
- district, area, and duration capture
- optional complaint proof image upload or camera capture
- complaint submission and tracking
- admin dashboard with complaint list and status actions

The frontend uses the Vite dev server and calls the Flask backend through the API wrapper in [frontend/src/api.js](../frontend/src/api.js).

## 4. Backend

The Flask application is initialized in [backend/app/__init__.py](../backend/app/__init__.py) and uses the API blueprint in [backend/app/routes.py](../backend/app/routes.py).

Responsibilities:
- user registration and login
- JWT-based authentication
- AI analysis endpoint
- complaint creation and retrieval
- admin-only complaint listing and updates
- MongoDB initialization and index setup

## 5. MongoDB

MongoDB is configured with environment variables in [backend/app/config.py](../backend/app/config.py).

The database layer is in [backend/app/db.py](../backend/app/db.py). It:
- creates the Mongo client
- initializes indexes for complaint_id, status, category, user_id, and email
- maintains the complaints and users collections
- seeds an admin user from environment variables when the values are present

## 6. Gemini AI

Gemini integration is handled in [backend/app/ai.py](../backend/app/ai.py).

Flow:
- the user sends a text message
- the backend calls the Gemini model with a prompt for category and severity detection
- the response is validated as JSON
- if the API fails or no API key is configured, a local fallback classifier is used

This fallback keeps the project runnable and demo-friendly.

## 7. Authentication

JWT-based auth is implemented in [backend/app/auth.py](../backend/app/auth.py).

The system supports:
- citizen token creation for registration and login
- token verification for protected endpoints
- admin-only authorization for status and dashboard actions

The main endpoints are protected with decorators rather than ad hoc checks.

## 8. Admin/Citizen roles

The application separates roles by user records in MongoDB.

Citizen role:
- register/login
- create complaint
- view their own complaints
- track complaint status

Admin role:
- login with admin credentials
- access the full complaint list
- view complaint details and image proof
- update submission status from Submitted to In Progress and Resolved

## 9. REST API layer

The backend routes are grouped under the /api prefix.

Key endpoints:
- /api/ai/analyze
- /api/complaints
- /api/complaints/my
- /api/complaints/<complaint_id>
- /api/auth/register
- /api/auth/login
- /api/auth/me
- /api/health

These are defined in [backend/app/routes.py](../backend/app/routes.py).

## 10. Data flow

Citizen flow:
1. User registers or logs in.
2. User enters complaint in Tamil/Tanglish/English.
3. Backend AI classifies the complaint and returns category and severity.
4. User supplies district, area, and optional duration.
5. Optional photo is accepted as a data URL if it is valid image content.
6. Complaint is created and stored in MongoDB.
7. Complaint ID is returned to the citizen.
8. Citizen can track the complaint by ID.

Admin flow:
1. Admin logs in.
2. Admin opens the dashboard.
3. Admin views all complaints and proof images when present.
4. Admin advances status values in the complaint lifecycle.

## 11. Complaint lifecycle

The application supports the following lifecycle:

Submitted -> In Progress -> Resolved

The status values are validated in the backend and enforced for admin-triggered updates.

## 12. Technology choices

- React + Vite: fast frontend development and simple browser UI
- Flask: lightweight Python API without unnecessary complexity
- PyMongo: native MongoDB access for Python
- MongoDB: flexible document storage for complaint and user records
- Gemini API: classification and issue understanding from multilingual civic messages
- JWT: lightweight authentication suitable for the prototype
- Pytest: simple backend test runner for API validation

## 13. Why these choices were selected

- The project prioritizes quick iteration for an assessment prototype.
- The stack is easy to run locally on a student environment.
- MongoDB fits a document-based complaint system well.
- Flask and React are small enough to explain clearly in a short demo.
- Gemini adds AI value without requiring a heavy ML pipeline.

## 14. Security boundaries

- Authentication is enforced on protected routes.
- Admin-only routes are restricted using a decorator.
- User passwords are hashed before storage.
- The app reads sensitive values from environment variables rather than hardcoded values.
- Proof uploads are validated to ensure they are image data URLs and not arbitrary file content.

## 15. Error and fallback behavior

The system handles failure in two important ways:

1. If MongoDB is not available, the app logs a warning and keeps startup possible for local testing.
2. If Gemini is unavailable or a key is missing, a local deterministic classifier is used instead.

This gives the app a useful fallback path while preserving the full end-to-end civic complaint workflow.
