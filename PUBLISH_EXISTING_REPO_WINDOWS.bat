@echo off
setlocal
cd /d "%~dp0"
where git >nul 2>&1
if errorlevel 1 (
  echo ERROR: Install Git for Windows first: https://git-scm.com/download/win
  exit /b 1
)
python tools\verify_release.py
if errorlevel 1 exit /b 1
if not exist .git git init
(git config user.name >nul 2>&1) || (echo ERROR: configure git user.name and user.email first & exit /b 1)
git add .
git commit -m "SC03216 reproducibility stage 1" || echo NOTE: no new changes, continuing
if exist .git\config (
  git remote get-url origin >nul 2>&1
  if errorlevel 1 git remote add origin https://github.com/Ting-YiLin/finreason-task3-sc03216-repro.git
)
git branch -M main
git push -u origin main
if errorlevel 1 (
  echo ERROR: push failed. Create the empty PUBLIC repository on github.com/new and authenticate git first.
  exit /b 1
)
echo PUBLISHED. VERIFY PUBLIC ACCESS in a signed-out browser and review excluded files.
endlocal
