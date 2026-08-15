# NammaTN – AI Civic Connect

## Slide 1: NammaTN – AI Civic Connect
- AI-powered civic issue reporting for citizens
- Built as a student prototype for Tamil Nadu civic workflows

## Slide 2: Problem
- Citizens struggle to report local civic issues clearly and quickly
- Public problems are often described in informal Tamil/Tanglish/English
- Local authorities need a simple and structured complaint pipeline

## Slide 3: Solution
- NammaTN converts natural-language complaints into structured reports
- Citizens can submit issues with district, area, and optional proof photo
- Authorities can manage and update complaint status

## Slide 4: System architecture
- React frontend for citizen and admin interactions
- Flask backend for validation and complaint operations
- MongoDB for storing users and complaints
- Gemini AI for classification and severity estimation

## Slide 5: Key features
- Citizen registration and login
- AI complaint analysis
- Complaint tracking by ID
- Optional photo upload or camera capture
- Admin dashboard and status updates

## Slide 6: Technology stack
- React + Vite
- Python + Flask
- MongoDB
- Google Gemini API
- Pytest

## Slide 7: AI functionality
- Interprets Tamil, Tanglish, and English messages
- Detects the issue category and severity
- Keeps a deterministic local fallback if the AI service is unavailable

## Slide 8: Testing and red/green run
- Automated backend tests cover normal flows and invalid inputs
- Red run demonstrates a deliberate failure and restoration
- Green run confirms the fix and final passing result

## Slide 9: AI change loop
- Requirement and prompt
- Inspection and implementation
- Test execution and failure diagnosis
- Fix and final validation

## Slide 10: Live demo / conclusion
- Citizen reports issue
- AI classifies it
- Complaint is created and tracked
- Admin reviews and updates status
- Final status is visible to the citizen

This presentation is intentionally concise and suitable for an internship assessment.
