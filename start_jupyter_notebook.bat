@echo off
pushd %~dp0
setlocal

echo ...Activating virtual environment
call "%~dp0venv\Scripts\activate.bat"
IF %ERRORLEVEL% NEQ 0 GOTO END
echo.

IF NOT EXIST "%~dp0venv\Scripts\jupyter-notebook.exe" (
    echo ...Installing Jupyter
    pip install jupyter
    IF %ERRORLEVEL% NEQ 0 GOTO END
)
echo ...Starting Jupyter Notebook
"%~dp0venv\Scripts\jupyter.exe" notebook
IF %ERRORLEVEL% NEQ 0 GOTO END
echo.

echo ...Deactivating virtual environment
call "%~dp0venv\Scripts\deactivate.bat"
IF %ERRORLEVEL% NEQ 0 GOTO END

:END
echo.
IF %ERRORLEVEL% NEQ 0 (
	echo [101;93mERROR DETECTED. Errorlevel: %ERRORLEVEL%[0m
    pause
) ELSE (
	echo [104mDone![0m
)

popd 
endlocal