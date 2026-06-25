# Health Prediction Application

A small full-stack app that stores patient blood-test records and automatically
generates an AI-based health **Remark** for each one.
User opens browser
        ↓
app.py starts
        ↓
database.init_db()
        ↓
SQLite creates patients table if missing
        ↓
Streamlit shows patient form
        ↓
User enters patient data
        ↓
validators.py checks data validity
        ↓
predictor.py generates AI remark
        ↓
database.py stores everything
        ↓
SQLite saves record permanently
        ↓
Patient records displayed

## Tech Stack & Why

| Layer        | Choice                         | Why |
|---------------|--------------------------------|-----|
| Frontend/UI   | **Streamlit**                  | Pure Python, fast to build a clean CRUD UI, keeps the review focused on logic rather than HTML/CSS boilerplate. |
| Backend       | **Python**                     | Required by the task; also the natural fit for the ML piece. |
| Database      | **SQLite**                     | Zero setup — it's just a local file, no server/Docker needed, runs instantly on any reviewer's machine. |
| Prediction    | **Custom-trained scikit-learn model** (RandomForestClassifier) + **optional free Hugging Face Inference API** | See "How prediction works" below — guarantees a free, always-working solution while still demonstrating real external API integration. |

## How prediction works

1. A `RandomForestClassifier` is trained (`train_model.py`) on a synthetic
   dataset whose labels are derived from standard clinical reference ranges
   for glucose, haemoglobin, and cholesterol (see comments in that file).
   This is the model that is *always* used — it's free, offline, and
   instant.
2. If you optionally set `HF_API_TOKEN` in your `.env` (a free Hugging Face
   token), `predictor.py` will also call the free Hugging Face Inference API
   (zero-shot classification) to cross-check the local model's finding and
   append a confidence score to the Remark. If the token isn't set, or the
   API call fails for any reason (no internet, rate limit, etc.), the app
   silently falls back to the local model's result — the app never breaks
   because of the external API.

This design satisfies the task's requirement to "call any external AI/ML or
Health-related API" while keeping the app 100% free and runnable offline.

## Project Structure

```
health-app/
├── app.py              # Streamlit UI (CRUD)
├── database.py         # SQLite connection + CRUD functions
├── validators.py        # Input validation (email, dob, numeric ranges)
├── predictor.py         # ML prediction + optional Hugging Face API call
├── train_model.py       # Generates synthetic data & trains the local model
├── requirements.txt
├── .env.example          # Template for optional env variables (no real secrets)
└── .gitignore
```

## Setup & Run

### 1. Install dependencies
```bash
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. (Optional) configure environment
```bash
cp .env.example .env
```
Leave `HF_API_TOKEN` blank to use only the local ML model (recommended —
no signup needed). Only fill it in if you want the extra API cross-check.

### 3. Train the local ML model (one-time)
```bash
python train_model.py
```
This creates `model.pkl`, which `predictor.py` loads at runtime.

### 4. Run the app
```bash
streamlit run app.py
```
Open the URL Streamlit prints (usually `http://localhost:8501`).

That's it — no database server, no Docker, no external account required.
The first time you run the app, it automatically creates `health_app.db`
(a SQLite file) in the project folder to store your patient records
permanently between runs.

## Features Implemented

- **Create**: Add a new patient via a validated form; a Remark is generated automatically on save.
- **Read**: View all records in a searchable table.
- **Update**: Select a record by ID and edit it; the Remark is regenerated.
- **Delete**: Select a record by ID and remove it.
- **Validation**: Full name required, DOB cannot be in the future, email format checked with regex, glucose/haemoglobin/cholesterol must be numeric and within plausible physiological ranges.
- **Persistent storage**: SQLite file on disk (not in-memory), so records survive app restarts.
- **AI/ML integration**: Custom-trained classifier (always-on) + optional free external API cross-check.

## Security Notes

- No credentials are hardcoded. The only configurable value (`HF_API_TOKEN`)
  comes from an environment variable loaded via `python-dotenv`.
- `.env`, `model.pkl`, and `health_app.db` are excluded via `.gitignore` and
  were never committed.
- Only `.env.example` (with a blank placeholder) is committed, so the repo
  is safe to make public.

## Known Limitations / Possible Extensions

- The synthetic training dataset is rule-derived, so model accuracy on it
  is near-perfect by construction — a real deployment would need an actual
  labeled clinical dataset (subject to data-privacy regulations) for a more
  meaningful accuracy benchmark.
- Could swap SQLite for PostgreSQL/MySQL for a multi-user production deployment
  — the SQL in `database.py` is plain and would translate directly.
- Could add pagination for very large patient lists.
