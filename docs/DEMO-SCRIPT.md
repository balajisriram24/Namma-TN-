# 5-Minute Demo Script

## 0:00–2:00 — Problem, approach, and solution

Speaker notes:
- “NammaTN solves a common civic problem: citizens often report issues in informal language, and the complaint gets lost in translation.”
- “This project turns everyday messages into structured civic complaints.”
- “The app accepts Tamil, Tanglish, and English input and identifies the issue type and severity with AI help.”
- “The system then stores the complaint, returns a complaint ID, and lets the authority update its status.”
- “The architecture is simple: frontend, backend, MongoDB, and AI classification.”

Actions:
- Show the landing citizen page.
- Explain the problem and the AI role briefly.
- Point to the complaint types and the optional proof upload area.

## 2:00–5:00 — Live demo

Speaker notes:
- “I will register as a citizen and log in.”
- “Then I will describe a civic issue in plain language: ‘Water is not supplied to our area for 3 days.’”
- “The AI identifies the issue type and suggested severity.”
- “I will enter the district and area, and optionally attach a proof photo.”
- “The app creates a complaint and returns a complaint ID.”
- “I will save that ID and show the citizen tracking panel.”
- “Now I will switch to the admin view and log in as the authority.”
- “The admin sees the complaint in the dashboard and can view the proof image if uploaded.”
- “The status is updated from Submitted to In Progress and then to Resolved.”
- “The citizen can see the final status on their tracking page.”

Actions:
1. Register a sample citizen account.
2. Log in.
3. Submit a complaint with natural-language text.
4. Show the complaint ID.
5. Open the tracking panel and search by complaint ID.
6. Log in as admin.
7. Open the complaint dashboard.
8. Update the status to In Progress.
9. Update the status to Resolved.
10. Return to the citizen view and show the final status.

Important note:
- Only demonstrate features that are actually implemented in the current repository.
