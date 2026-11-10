@echo off
title Shattered Continent - map setup
cd /d "%~dp0"
echo Shattered Continent: putting the nations on the map
echo.
set "GAME=C:\Program Files (x86)\Steam\steamapps\common\Hearts of Iron IV"
if not exist "%GAME%\history\states" (
  echo Could not find Hearts of Iron IV in the default Steam folder.
  echo In Steam: right-click Hearts of Iron IV, Manage, Browse local files, then copy the folder path from the address bar.
  set /p "GAME=Paste the path to your Hearts of Iron IV folder and press Enter: "
)
where py >/dev/null 2>nul
if %errorlevel%==0 (
  py tools\setup_map.py "%GAME%"
) else (
  python tools\setup_map.py "%GAME%"
)
if errorlevel 1 (
  echo.
  echo Something went wrong. If it says Python was not found, install Python from https://www.python.org/downloads/
  echo and tick "Add python.exe to PATH" during install, then run this again.
)
echo.
pause
