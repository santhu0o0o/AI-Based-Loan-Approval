# LoanWise AI — Loan Approval Prediction System

A machine-learning web application that estimates whether a home-loan application is **likely to be approved or rejected**, and explains why in plain English.

It is built so that someone with no technical or financial background can use it. It never shows a stack trace, and wrong or nonsense input never produces a confident wrong answer.

> **Disclaimer:** this is an academic demonstration trained on 614 historical applications. It is not a lending decision and must not be presented as one. See [docs/MODEL_CARD.md](docs/MODEL_CARD.md).

| Home | Form validation | Result |
|---|---|---|
| ![Home](docs/screenshots/home-desktop.png) | ![Validation](docs/screenshots/check-errors-desktop.png) | ![Result](docs/screenshots/result-approved-desktop.png) |

---

## Quick start

**macOS / Linux**
```bash
./run.sh
```

**Windows**
```bat
run.bat
```

On the first run the script:
1. creates a virtual environment in `.venv`;
2. installs the Python dependencies;
3. trains the model if `artifacts/models/loan_model.pkl` is missing;
4. builds the frontend if `frontend/dist` is missing (this needs Node.js 18+);
5. starts the server and opens your browser.

Every later run just starts the app. On macOS, port 5000 is usually taken by AirPlay Receiver, so the script falls back to **http://127.0.0.1:8000** automatically.

| Command | What it does |
|---|---|
| `./run.sh` | Set up if needed, then start the app |
| `./run.sh --retrain` | Retrain the model, then start |
| `./run.sh --test` | Run the test suite |
| `LOANWISE_PORT=8080 ./run.sh` | Use a specific port |

**Requirements:** Python 3.10+. Node.js 18+ is only needed if you change the frontend, because a pre-built copy ships in `frontend/dist`.

---

## Tech stack

| Layer | Technology |
|---|---|
| Frontend | React 19, React Router, Framer Motion, Lucide icons, hand-drawn SVG illustrations, esbuild |
| Backend | Python 3.10+, Flask 3, gunicorn (production) |
| Machine learning | scikit-learn, pandas, NumPy, joblib, matplotlib (EDA charts) |
| Storage | SQLite (prediction history) |
| Tooling | ruff, mypy (strict), unittest/pytest, Docker, Makefile |

---

## How it works

```
Browser (React)
   │  Layer 1: real-time validation in the form
   ▼
POST /api/predict  (Flask)
   │  Layer 2: server-side validation   (loanwise/domain/validation.py)
   │  Layer 3: sanitiser → model format  (loanwise/domain/sanitizer.py)
   ▼
ML pipeline (Logistic Regression)    → probability of approval
   ▼
Guardrails (loanwise/domain/guardrails.py)
   │  Common-sense lending rules that override the model on clearly wrong
   │  answers, e.g. monthly payment above 65% of income → rejected
   ▼
Plain-English verdict + reasons + estimated EMI → saved to SQLite → shown to the user
```

**Input handling.** Harmless formatting is accepted and normalised: `"₹ 45,000"`, `"25 lakh"`, `"20 years"`, `" YES "`. Anything that is actually invalid gets a specific, friendly message on the right field, and all errors are reported together.

**Model.** Logistic Regression, Decision Tree and Random Forest are compared with 5-fold cross-validation. The winner is picked by cross-validation accuracy, never by test-set score. A training-time check guarantees that more income never lowers the approval chance and that a bigger loan never raises it.

| Model | CV accuracy | Test accuracy | F1 |
|---|---|---|---|
| **Logistic Regression** (chosen) | 0.798 ± 0.046 | 0.854 | 0.903 |
| Random Forest | 0.796 ± 0.044 | 0.854 | 0.903 |
| Decision Tree | 0.784 ± 0.046 | 0.854 | 0.903 |

For reference, a model that always says "approved" would score 0.69. Credit history is by far the strongest factor.

More detail is in [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md), [docs/API.md](docs/API.md) and [docs/MODEL_CARD.md](docs/MODEL_CARD.md).

---

## Project structure

```
LoanWiseAI/
├── src/loanwise/              Python package
│   ├── config.py              Settings from LOANWISE_* environment variables
│   ├── logging_config.py
│   ├── api/                   Flask app factory, routes, errors, user messages, SPA serving
│   ├── domain/                Pure business logic: schemas, validation, sanitiser, guardrails
│   ├── services/              Prediction flow, model registry, samples
│   ├── storage/               SQLite history repository
│   └── ml/                    Features, data, pipelines, evaluation, EDA, training
├── frontend/                  React app (src/) and pre-built bundle (dist/)
├── tests/
│   ├── unit/                  Validation, sanitiser, guardrails, features, config, CORS, services
│   └── integration/           Full HTTP API and history
├── scripts/                   train_model.py, run_server.py
├── data/raw/                  loan.csv (labelled), test.csv (unlabelled; used for demo samples)
├── artifacts/
│   ├── models/                loan_model.pkl, model_info.json
│   └── reports/eda/           EDA charts
├── docs/                      ARCHITECTURE.md, API.md, MODEL_CARD.md, screenshots/
├── run.sh, run.bat            One-command launchers
├── wsgi.py                    Production entry point (gunicorn wsgi:app)
├── pyproject.toml             Package metadata, ruff and mypy config
├── requirements.txt           Runtime dependencies
├── requirements-dev.txt       Development dependencies
├── Makefile                   install / train / test / lint / typecheck / run / serve
└── Dockerfile                 Multi-stage build: Node builds the UI, Python serves it
```

---

## Development

```bash
make install-dev       # dependencies + dev tools (ruff, mypy, pytest)
make train             # retrain the model → artifacts/
make test              # 90 tests
make lint typecheck    # ruff + mypy --strict
make run               # dev server
make serve             # gunicorn
```

**Frontend** (in `frontend/`):

```bash
npm install
npm run dev       # live-reload UI on :5173, proxies /api to :5000
npm run build     # writes frontend/dist, which Flask serves
```

**Docker**

```bash
docker build -t loanwise-ai .
docker run -p 5000:5000 loanwise-ai
```

All settings are optional environment variables; see [.env.example](.env.example).

---

## Deploy for free (Render)

The repo includes a [`render.yaml`](render.yaml) blueprint, so deploying is one click once the code is on GitHub:

1. Push this folder to a GitHub repository (private or public).
2. Go to [dashboard.render.com](https://dashboard.render.com), choose **New → Blueprint**, and pick the repository.
3. Render reads `render.yaml` and creates a free web service called `loanwise-ai`. It installs the requirements, starts `gunicorn wsgi:app` and checks `/api/health`.
4. After about 3–5 minutes the app is live at `https://loanwise-ai.onrender.com` (or a similar URL).

Every later `git push` redeploys automatically.

**Free-plan behaviour:**
- **Sleep:** the app sleeps after 15 minutes without visitors, and the first visit afterwards takes about a minute. Open the link a couple of minutes before a demo.
- **History resets:** the disk is temporary, so prediction history clears whenever the app restarts, sleeps or redeploys. Predictions are not affected.
- **No Node.js needed:** the pre-built `frontend/dist` is committed, so Render does not need to build the frontend.

You can also run the `Dockerfile` on any container host (Render, Koyeb, Fly.io, a VPS).

---

## Known limitations

- **Small dataset.** 614 rows from a single public dataset. The accuracy numbers are indicative only.
- **Protected attributes.** The model uses Gender and Marital Status, as the original project specification required. In a real lending product this would raise fair-lending and regulatory concerns, and these features should be removed and the model audited for bias before any production use.
- **Approximate EMI.** The guardrails estimate EMI at 9% annual interest; real rates vary.
- **Single-instance storage.** SQLite history suits a demo. Use a managed database for multi-instance deployments.
