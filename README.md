# Campus Customs — Homework 4

Campus Customs is a Yale-inspired customer storefront built with React, Vite, TypeScript, FastAPI, SQLite, and a PydanticAI shop assistant. The site supports product browsing, catalogue-backed price and inventory answers, clickable product results from chat, account registration/login, persistent chat history for logged-in customers, and product/page context.

## Before running

The local data pack is intentionally excluded from GitHub. Make sure these local files exist:

```text
data/
├── campus_customs.db
└── products/
    └── product image files referenced by the database
```

The database and product images are not included in the public repository. Place them in the paths above after cloning. Do not commit the data pack ZIP, database, or images.

## Backend setup

From the project root, create and activate a virtual environment, then install the Python dependencies:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Copy `.env.example` to `.env` and put the real `PORTKEY_API_KEY` in the local file if you want to use the configured PydanticAI model. The key is optional for local demonstrations: without it, the backend uses its deterministic SQLite-backed fallback. `PORTKEY_MODEL` defaults to `gpt-5.6-luna`.

Start FastAPI from the `backend` folder:

```powershell
cd backend
uvicorn main:app --reload --port 8000
```

The API is available at `http://localhost:8000`. The backend serves product images at `/media` and requires the local SQLite database at `data/campus_customs.db`.

## Frontend setup

In a second terminal, install the frontend dependencies and start Vite:

```powershell
cd frontend
npm install
npm run dev
```

Open the URL shown by Vite, normally `http://localhost:5173`. The Vite proxy forwards `/api` and `/media` requests to the FastAPI server on port 8000.

## Useful checks

```powershell
# From backend, verify the API is responding
Invoke-RestMethod http://localhost:8000/api/health

# From frontend, create a production build
npm run build
```

The completed evidence report is at `output/app_check.html`. Open it directly in a browser; its screenshots use relative paths and do not require the application to be running.

## Repository safety

`.gitignore` excludes `.env`, the local database, product images, the local data-pack ZIP, virtual environments, dependencies, caches, and build output. Commit `.env.example` only; it contains placeholders and no working credentials. The public repository should contain the application source, documentation, prompt log, and `output/` evidence files, but not the local data pack or secrets.
