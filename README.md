# Pregnancy Calculator

Small Flask app: estimate due date and current gestational age, with optional patient save.

## Local run

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python app.py
```

Open http://127.0.0.1:5000

## Tests

```powershell
pytest -q
```

## Deploy to PythonAnywhere (free)

1. Sign up at pythonanywhere.com.
2. **Files** → upload this folder, or `git clone` from a Bash console into `/home/<user>/calc`.
3. **Consoles → Bash**:
   ```bash
   cd ~/calc
   mkvirtualenv --python=python3.11 calc-venv
   pip install -r requirements.txt
   ```
4. **Web** → *Add a new web app* → *Manual configuration* → *Python 3.11*.
5. In the web app config:
   - **Source code:** `/home/<user>/calc`
   - **Virtualenv:** `/home/<user>/.virtualenvs/calc-venv`
   - **WSGI file:** edit to:
     ```python
     import sys
     path = '/home/<user>/calc'
     if path not in sys.path:
         sys.path.insert(0, path)
     from wsgi import application
     ```
   - **Static files:** URL `/static/` → Directory `/home/<user>/calc/static/`
6. Click **Reload**.

SQLite DB file `calc.db` is created on first run next to `app.py` and persists across reloads.

## Language

Default is Hebrew (RTL). Click the language link in the header to toggle to English. Choice is stored in a cookie.
