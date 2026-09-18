# StartupReady AI Platform

Full-stack implementation of the 15-step startup evaluation from the supplied brief.

## Run

Requires Python 3.10+. No third-party packages or Node.js are needed.

Terminal 1:
```powershell
cd backend
python app.py
```

Terminal 2:
```powershell
cd frontend
python server.py
```

Open http://localhost:5173.

The API runs on port 3001 and saves completed work automatically in `backend/data/assessment.json`.

The backend is implemented in Python using the standard library (`http.server`, `json`, and `pathlib`), so it is suitable for a Python full-stack internship assignment without dependency setup.

## Included

- 15 guided evaluation stages with all brief subject areas
- progress, autosave, Save & Resume, skip, context help and uploads
- local AI-style feedback and "Improve with AI" writing action
- live score, category scorecard, risk flags, recommendations, SWOT and downloadable report
