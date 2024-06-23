@echo off
cd /d "C:\Users\USERNAME\Path-to-Folder\web"
start "" "http://localhost:80"
"C:\Users\USERNAME\AppData\Local\Programs\Python\Python312\python.exe" fetch_metrics.py
pause
