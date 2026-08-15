# Design Document

## 1. User roles

### Citizen
A citizen can:
- create a new account
- log in securely
- describe a civic issue in Tamil, Tanglish, or English
- submit a district and area
- optionally attach one photo as proof
- receive a complaint ID
- track status for their own complaints

### Admin
An administrator can:
- log in with the seeded admin account
- view the wider complaint list
- inspect complaint details and uploaded proof image
- update complaint status

## 2. Citizen flow

Citizen flow:

Register
→ Login
→ Describe civic problem
→ AI classification
→ Enter district and area
→ Optional photo upload
→ Submit complaint
→ Receive complaint ID
→ Track complaint status

This flow is implemented in the frontend citizen experience and backend complaint routes.

## 3. Admin flow

Admin flow:

Login
→ Dashboard
→ View complaints
→ Review complaint details and proof photo
→ Update status

The admin dashboard supports status changes from Submitted to In Progress and then to Resolved.

## 4. Complaint data model

The complaint document includes the following fields as they actually exist in the backend:

- complaint_id
- user_id
- message
- category
- severity
- district
- area
- duration
- proof_image
- status
- created_at
- updated_at

The complaint_id is generated using a prefix based on category and a timestamped UUID suffix.

## 5. Status lifecycle

The implemented lifecycle is:

Submitted
→ In Progress
→ Resolved

Status changes are validated on the backend before being saved.

## 6. API design

The application exposes the following endpoints:

### AI analysis
- POST /api/ai/analyze

Purpose:
- send a message and retrieve a category and severity

### Complaint creation
- POST /api/complaints

Purpose:
- create a complaint using authenticated citizen session

### Complaint retrieval
- GET /api/complaints/<complaint_id>
- GET /api/complaints/my
- GET /api/complaints

Purpose:
- get one complaint, the user's own complaints, or the admin list

### Complaint status update
- PATCH /api/complaints/<complaint_id>

Purpose:
- update complaint status by admin

### Authentication
- POST /api/auth/register
- POST /api/auth/login
- GET /api/auth/me
- POST /api/auth/logout

## 7. Authentication and authorization

Authentication uses JWT tokens.

- Citizens register and log in to receive a token.
- Protected endpoints require a Bearer token header.
- The admin dashboard is guarded by an admin role check.
- Citizens can only read their own complaint list.
- Admins can read the full complaint list and modify status.

## 8. Validation

The backend validates:
- complaint message length
- required fields such as district and area
- valid category names
- valid severity levels
- valid image data URL for proof_image
- valid JWT token on protected requests
- valid status transitions

## 9. Error handling

The backend returns clear JSON errors for:
- invalid auth
- missing required fields
- invalid category or severity
- invalid image file input
- invalid complaint ID or not-found result
- forbidden admin access
- malformed requests

The frontend surfaces those errors in the UI and shows them to the user without crashing the app.

## 10. Security considerations

- Passwords are hashed before save.
- Tokens are validated server-side.
- Admin route protections are enforced.
- Secrets are expected to be stored in environment variables, not committed to source control.
- Image proof is restricted to accepted image content types encoded as data URLs.

The project is a prototype and should not be treated as a production civic platform.
