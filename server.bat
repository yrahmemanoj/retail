@echo off
echo Running EDA analysis...
python eda\run.py
if %errorlevel% neq 0 (
    echo EDA analysis failed. Exiting.
    pause
    exit /b 1
)
echo EDA analysis completed successfully!
echo Starting Python HTTP Server...
start "" http://localhost:8000/dashboard/
python -m http.server 8000