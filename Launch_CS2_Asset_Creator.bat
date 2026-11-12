@echo off
title CS2 Asset Creator 2.0
cd /d "%~dp0"
py -3 CS2_Asset_Creator.py
if errorlevel 1 (echo Install Python 3.10+ with Tcl/Tk. & pause)
