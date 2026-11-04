@echo off
REM ============================================================================
REM LoanWise AI - one-command launcher (Windows)
REM
REM Usage:
REM   run.bat              Set up (first run only) and start the app
REM   run.bat --retrain    Retrain the model before starting
REM   run.bat --test       Run the test suite and exit
REM
REM Environment overrides: LOANWISE_PORT (default 5000), LOANWISE_HOST (default 127.0.0.1)
REM ============================================================================
setlocal
cd /d "%~dp0"

set "VENV_DIR=.venv"
set "VPY=%VENV_DIR%\Scripts\python.exe"
set "MODEL_FILE=artifacts\models\loan_model.pkl"
set "FRONTEND_DIST=frontend\dist\index.html"

REM --- 1. Python --------------------------------------------------------------
where py >nul 2>nul
if %errorlevel%==0 (set "PYTHON=py -3") else (set "PYTHON=python")
%PYTHON% -c "import sys; sys.exit(0 if sys.version_info >= (3, 10) else 1)" >nul 2>nul
if errorlevel 1 (
  echo xx  Python 3.10+ is required. Install it from https://www.python.org/downloads/
  exit /b 1
)

REM --- 2. Virtual environment + dependencies --------------------------------
if not exist "%VPY%" (
  echo ==^> Creating virtual environment in .venv ^(first run only^)
  %PYTHON% -m venv "%VENV_DIR%" || exit /b 1
  echo ==^> Installing Python dependencies
  "%VPY%" -m pip install --quiet --upgrade pip
  "%VPY%" -m pip install --quiet setuptools wheel
  "%VPY%" -m pip install --quiet -r requirements.txt || exit /b 1
  "%VPY%" -m pip install --quiet -e . --no-deps --no-build-isolation || exit /b 1
)

REM --- 3. Tests (optional) ---------------------------------------------------
if /i "%~1"=="--test" (
  "%VPY%" -m unittest discover -s tests -t . -v
  exit /b %errorlevel%
)

REM --- 4. Model ---------------------------------------------------------------
set "TRAIN=0"
if /i "%~1"=="--retrain" set "TRAIN=1"
if not exist "%MODEL_FILE%" set "TRAIN=1"
if "%TRAIN%"=="1" (
  echo ==^> Training the model ^(about a minute^)
  "%VPY%" scripts\train_model.py || exit /b 1
)

REM --- 5. Frontend -----------------------------------------------------------
if not exist "%FRONTEND_DIST%" (
  where npm >nul 2>nul
  if errorlevel 1 (
    echo !!  frontend\dist is missing and npm is not installed. Install Node.js 18+ from https://nodejs.org
  ) else (
    echo ==^> Building the frontend ^(first run only^)
    pushd frontend
    call npm install --no-audit --no-fund && call npm run build
    popd
  )
)

REM --- 6. Run -----------------------------------------------------------------
if not defined LOANWISE_HOST set "LOANWISE_HOST=127.0.0.1"
if not defined LOANWISE_PORT set "LOANWISE_PORT=5000"
set "URL=http://%LOANWISE_HOST%:%LOANWISE_PORT%"
echo ==^> Starting LoanWise AI at %URL%  ^(press Ctrl+C to stop^)
start "" cmd /c "timeout /t 3 >nul && start %URL%"
"%VPY%" scripts\run_server.py
