@echo off
setlocal
cd /d "%~dp0"
where gh >nul 2>&1
if errorlevel 1 (echo ERROR: GitHub CLI not installed. Use PUBLISH_EXISTING_REPO_WINDOWS.bat after creating the repo in your browser. & exit /b 1)
where git >nul 2>&1
if errorlevel 1 (echo ERROR: Git for Windows not installed. & exit /b 1)
python tools\verify_release.py
if errorlevel 1 exit /b 1
gh auth status
if errorlevel 1 (echo ERROR: Log into GitHub CLI yourself with: gh auth login & exit /b 1)
if not exist .git git init
(git config user.name >nul 2>&1) || (echo ERROR: configure git identity. & exit /b 1)
git add .
git commit -m "SC03216 reproducibility stage 1" || echo NOTE: no changes
git branch -M main
gh repo create Ting-YiLin/finreason-task3-sc03216-repro --public --source . --remote origin --push
if errorlevel 1 (echo ERROR: repository creation/push failed, inspect output. & exit /b 1)
echo PUBLISHED. Check public files and no leaks.
endlocal
