@echo off
REM Ensure Pyenv is activated in this session
SET PYENV="%USERPROFILE%\.pyenv"
SET PYENV_ROOT=%PYENV%
SET PATH=%PYENV_ROOT%\pyenv-win\shims;%PYENV_ROOT%\pyenv-win\bin;%PATH%

REM Set the Python version for this project
pyenv install 3.11.2
pyenv local 3.11.2
pyenv rehash

REM Launch Python (now using the local version)
python --version
