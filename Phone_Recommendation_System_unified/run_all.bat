
@echo off
echo Starting modules...
start cmd /k "cd /d %~dp0\phonefinder && python app.py"
start cmd /k "cd /d %~dp0\salesprediction && python app.py"
start cmd /k "cd /d %~dp0\buyandsell && python app.py"
start cmd /k "cd /d %~dp0\comparephone && python app.py"
start cmd /k "cd /d %~dp0\upcomingphone && python app.py"
start cmd /k "cd /d %~dp0\reviews && python app.py"
echo All modules started.
pause
