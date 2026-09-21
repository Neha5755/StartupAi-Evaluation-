# StartupReady AI EVALUATION Platform

Full-stack implementation of the 15-step startup evaluation from the supplied brief.

## Run locally

Requires Python 3.10+. No third-party packages or Node.js are needed.

Terminal 1:

```powershell
cd backend
python app.py
```

Open http://localhost:3001. This single Python server serves both the frontend and backend API.

The API runs on port 3001 and saves completed work automatically in `backend/data/assessment.json`.

The backend is implemented in Python using the standard library (`http.server`, `json`, and `pathlib`), so it is suitable for a Python full-stack internship assignment without dependency setup.

## Deploy on Render

The included `render.yaml` deploys the complete app as one Python web service. Push the repository to GitHub, then in Render select **New > Blueprint**, connect the repository, and deploy. Render reads `render.yaml` automatically. The deployed site is available at the supplied `onrender.com` URL.

Important: assessment data is saved in a local JSON file. This is suitable for a demo, but Render's filesystem is not persistent across deploys/restarts. For production, replace it with PostgreSQL or another database.

## Included

- 15 guided evaluation stages with all brief subject areas
- progress, autosave, Save & Resume, skip, context help and uploads
- local AI-style feedback and "Improve with AI" writing action
- live score, category scorecard, risk flags, recommendations, SWOT and downloadable report
