@echo off
cd /d "%~dp0"
xelatex -interaction=nonstopmode -halt-on-error main.tex >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    start "" "main.pdf"
)
