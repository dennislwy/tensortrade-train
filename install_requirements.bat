@echo off
pushd %~dp0
setlocal

echo [1m...Activating virtual environment[0m
call venv\Scripts\activate.bat
IF %ERRORLEVEL% NEQ 0 GOTO END
echo.

echo [1m...Installing 'requirements.ray.no-gpu.txt'[0m
pip install -r requirements.ray.no-gpu.txt
IF %ERRORLEVEL% NEQ 0 GOTO END 
echo.

echo [1m...Deactivating virtual environment[0m
call venv\Scripts\deactivate.bat
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
