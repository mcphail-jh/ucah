@echo off
setlocal

REM Define the name of your virtual environment
set VENV_NAME=my_venv

REM Define the name of your requirements file
set REQUIREMENTS_FILE=requirements.txt

REM Check if Python is installed and accessible
where python >nul 2>&1
if %errorlevel% neq 0 (
    echo Python is not found in your PATH. Please install Python or add it to your PATH.
    goto :eof
)

REM Create the virtual environment if it doesn't exist
if not exist %VENV_NAME% (
    echo Creating virtual environment "%VENV_NAME%"...
    python -m venv %VENV_NAME%
    if %errorlevel% neq 0 (
        echo Failed to create virtual environment.
        goto :eof
    )
) else (
    echo Virtual environment "%VENV_NAME%" already exists.
)

REM Activate the virtual environment
echo Activating virtual environment "%VENV_NAME%"...
call %VENV_NAME%\Scripts\activate.bat
if %errorlevel% neq 0 (
    echo Failed to activate virtual environment.
    goto :eof
)

REM Check if requirements.txt exists
if not exist %REQUIREMENTS_FILE% (
    echo "%REQUIREMENTS_FILE%" not found. Skipping dependency installation.
    goto :deactivate_venv
)

REM Install dependencies from requirements.txt
echo Installing dependencies from "%REQUIREMENTS_FILE%"...
pip install -r %REQUIREMENTS_FILE%
if %errorlevel% neq 0 (
    echo Failed to install dependencies.
    goto :deactivate_venv
)

echo Virtual environment setup and dependencies installed successfully.

:deactivate_venv
REM Deactivate the virtual environment
echo Deactivating virtual environment...
call deactivate.bat

endlocal