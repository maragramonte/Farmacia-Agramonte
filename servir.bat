@echo off
REM Doble clic aqui para abrir la web de la farmacia en este ordenador.
cd /d "%~dp0"
py servir.py 2>nul || python servir.py
pause
