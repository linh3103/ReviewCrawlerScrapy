@echo off
CLS
ECHO ====================================================================
ECHO      AUTOMATED SETUP ^& RUN SCRIPT FOR REVIEW CRAWLER (WINDOWS)
ECHO ====================================================================
ECHO This script will set up the environment, start servers, and run the app.
ECHO It prioritizes Conda if available, otherwise it will use venv.
ECHO ====================================================================
ECHO.

REM === THAY ĐỔI 1: LẤY ĐƯỜNG DẪN GỐC CỦA DỰ ÁN ===
REM %~dp0 sẽ lấy đường dẫn của thư mục chứa file setup.bat này
SET "PROJECT_ROOT=%~dp0"
ECHO [i] Project root directory identified as: %PROJECT_ROOT%
ECHO.

REM --- Bước 1: Quyết định sử dụng Conda hay venv ---
ECHO [?] Checking for Conda installation...
CALL conda --version >nul 2>nul
IF %errorlevel% equ 0 (
    ECHO [i] Conda found! Proceeding with Conda setup.
    GOTO USE_CONDA
) ELSE (
    ECHO [!] Conda not found. Falling back to Python's standard venv.
    GOTO USE_VENV
)


:USE_CONDA
REM ===================== LOGIC CHO CONDA =====================
SET ENV_NAME=review_crawler_env
ECHO.
ECHO --- Conda Setup ---
ECHO [?] Checking if Conda environment '%ENV_NAME%' exists...
CALL conda env list | findstr /B "%ENV_NAME% " >nul
IF %errorlevel% neq 0 (
    ECHO [+] Conda environment '%ENV_NAME%' not found. Creating it now...
    CALL conda create --name %ENV_NAME% python=3.10 pip -y
    IF %errorlevel% neq 0 ( ECHO !!! ERROR: Failed to create Conda environment. & GOTO FAILED )
) ELSE (
    ECHO [i] Conda environment '%ENV_NAME%' already exists.
)

ECHO [+] Installing/updating packages in '%ENV_NAME%'...
REM === THAY ĐỔI 2: SỬ DỤNG ĐƯỜNG DẪN TUYỆT ĐỐI ===
CALL conda run -n %ENV_NAME% python -m pip install -r "%PROJECT_ROOT%requirements.txt"
IF %errorlevel% neq 0 ( ECHO !!! ERROR: Failed to install packages using Conda. & GOTO FAILED )

REM --- START SCRAPYD VÀ DEPLOY ---
CALL :START_AND_DEPLOY_LOGIC "conda run -n %ENV_NAME%"

ECHO [+] Starting the Flask UI application...
CALL conda run -n %ENV_NAME% python "%PROJECT_ROOT%UI\app.py"
GOTO END


:USE_VENV
REM ===================== LOGIC CHO VENV =====================
ECHO.
ECHO --- Venv Setup ---
CALL python --version >nul 2>nul
if %errorlevel% neq 0 ( ECHO !!! ERROR: Python is not found. & GOTO FAILED )

IF NOT EXIST "%PROJECT_ROOT%venv" (
    ECHO [+] Creating virtual environment 'venv'...
    CALL python -m venv "%PROJECT_ROOT%venv"
    IF %errorlevel% neq 0 ( ECHO !!! ERROR: Failed to create virtual environment. & GOTO FAILED )
) ELSE (
    ECHO [i] Virtual environment 'venv' already exists.
)

ECHO [+] Activating venv and installing packages...
CALL "%PROJECT_ROOT%venv\Scripts\activate"
CALL python -m pip install -r "%PROJECT_ROOT%requirements.txt"
IF %errorlevel% neq 0 ( ECHO !!! ERROR: Failed to install packages using venv. & GOTO FAILED )

REM --- START SCRAPYD VÀ DEPLOY ---
CALL :START_AND_DEPLOY_LOGIC ""

ECHO [+] Starting the Flask UI application...
CALL python "%PROJECT_ROOT%UI\app.py"
GOTO END


REM ===================== HÀM CON CHO LOGIC CHUNG =====================
:START_AND_DEPLOY_LOGIC
SET "RUN_PREFIX=%~1"

ECHO.
ECHO --- Starting Servers and Deploying Project ---
ECHO [+] Starting Scrapyd server in a new window...
START "Scrapyd Server" %RUN_PREFIX% scrapyd

ECHO [i] Waiting 5 seconds for Scrapyd server to initialize...
timeout /t 5 /nobreak >nul

IF NOT EXIST "%PROJECT_ROOT%crawler\.deployed" (
    ECHO [+] Project has not been deployed. Deploying 'crawler' project now...
    
    REM === THAY ĐỔI 3: DÙNG CD /D VỚI ĐƯỜNG DẪN TUYỆT ĐỐI ===
    cd /D "%PROJECT_ROOT%crawler"
    
    CALL %RUN_PREFIX% scrapyd-deploy
    IF %errorlevel% equ 0 (
        ECHO [i] Deployment successful. Creating a flag file to skip this step next time.
        ECHO deployed > .deployed
    ) ELSE (
        ECHO !!! WARNING: Deployment failed. The crawler might not be available in Scrapyd.
    )
    
    REM === THAY ĐỔI 4: QUAY VỀ THƯ MỤC GỐC MỘT CÁCH AN TOÀN ===
    cd /D "%PROJECT_ROOT%"
) ELSE (
    ECHO [i] Project already deployed. Skipping deployment.
)
ECHO.
EXIT /B 0


:FAILED
ECHO.
ECHO !!! Setup failed. Please check the error messages above.
GOTO END


:END
ECHO.
ECHO --- Application has finished or been closed. ---
pause