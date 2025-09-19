@echo off 
SETLOCAL EnableDelayedExpansion 
ECHO. 
ECHO ========================================================== 
ECHO      ENVIRONMENT 'review_crawler_env' ACTIVATED SUCCESSFULLY 
ECHO ========================================================== 
ECHO. 
ECHO [+] Installing/updating required packages... 
ECHO -------------------------------------------------------------------- 
CALL python -m pip install -r "C:\python-scraping-apps\TEST\ReviewCrawlerScrapy\requirements.txt" 
IF 0 neq 0 (ECHO  Failed to install packages. & pause & exit /b) 
ECHO -------------------------------------------------------------------- 
ECHO. 
ECHO [+] Starting Scrapyd server in a new background window... 
START "Scrapyd Server" scrapyd 
ECHO [i] Waiting 5 seconds for Scrapyd server to initialize... 
timeout /t 5 /nobreak >nul 
IF NOT EXIST "C:\python-scraping-apps\TEST\ReviewCrawlerScrapy\review_crawler\.deployed" ( 
    ECHO [+] Deploying 'review_crawler' project for the first time... 
    cd /D "C:\python-scraping-apps\TEST\ReviewCrawlerScrapy\" 
    CALL scrapyd-deploy 
    IF 0 equ 0 ( ECHO [i] Deployment successful. Creating flag file. & ECHO deployed > "C:\python-scraping-apps\TEST\ReviewCrawlerScrapy\review_crawler\.deployed" ) ELSE ( ECHO  Deployment failed. ) 
) ELSE ( 
    ECHO [i] Project already deployed. Skipping deployment. 
) 
ECHO. 
ECHO ========================================================== 
ECHO      SETUP COMPLETE STARTING THE FASTAPI UI... 
ECHO ========================================================== 
ECHO. 
ECHO [i] Opening the application in your default browser at http://127.0.0.1:8000 
timeout /t 2 /nobreak >nul 
START "" "http://127.0.0.1:8000" 
CALL uvicorn UI_fastapi.app.main:app --host 0.0.0.0 --port 8000 
