@echo off
pushd %~dp0
setlocal

set python_path=%ProgramFiles%\Python37\python.exe

IF NOT EXIST "%python_path%" (
    echo [101;93mPython 3.7 not found![0m
    goto END
)

"%python_path%" -V
echo [1m...Creating virtual environment at '%~dp0venv'[0m
"%python_path%" -m venv "%~dp0venv"
IF %ERRORLEVEL% NEQ 0 GOTO END

echo [1m...Activating virtual environment[0m
call "%~dp0venv\Scripts\activate.bat"
IF %ERRORLEVEL% NEQ 0 GOTO END

echo [1m...Upgrading 'pip'[0m
"%~dp0venv\Scripts\python.exe" -m pip install --upgrade pip
IF %ERRORLEVEL% NEQ 0 GOTO END

echo [1m...Deactivating virtual environment[0m
call "%~dp0venv\Scripts\deactivate.bat"
IF %ERRORLEVEL% NEQ 0 GOTO END

:END
echo.
IF %ERRORLEVEL% NEQ 0 (
	echo [101;93mERROR DETECTED. Errorlevel: %ERRORLEVEL%[0m
) ELSE (
	echo [104mDone![0m
)

popd 
endlocal

pause