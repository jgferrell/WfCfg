@echo off

REM enabledelayedexpansion: for random numbers
setlocal enabledelayedexpansion

REM --- "%Python%" = path to local python.exe file
set Python=C:\Program Files\Python311\python.exe
REM --- "%Workflows%" = path to local Sirsi Workflows client launcher
set Workflows=C:\Program Files (x86)\Sirsi\JWF\wf.bat

REM --- "%WfCfg%" = path to wfcfg.py
set WfCfg=%~dp0wfcfg.py
REM --- %LogFile% = path to WfCfg log file
set LogFile=%windir%\temp\wfcfg.log

REM --- don't try to run WfCfg unless both Workflows and Python are installed
if not exist "%Workflows%" goto NoWorkflows
if not exist "%Python%" goto NoPython

REM --- WfCfg system lock: enforce sequential execution of wfcfg.bat
REM - "%LockDir%" = where we're storing lock files WfCfg
set LockDir=%temp%
set LockFile=%LockDir%\wfcfg.lock
REM - Lock loop; wait until system is available
echo [%TIME%] Checking for lock files. >> %LogFile% 2>&1
:LockLoop
REM - pause for a random number of seconds
set MinSeconds=0
set MaxSeconds=30
set MaxSeconds=30
set /a RandTime=!RANDOM! * (1 + %MaxSeconds%) / 32768 + %MinSeconds%
echo [%TIME%] Waiting for %RandTime% seconds. >> %LogFile% 2>&1
timeout /t %RandTime%
if exist %LockFile% goto LockLoop
copy /y nul "%LockFile%"
echo [%TIME%] Establishing lock (%RandTime%): %LockFile% >> %LogFile% 2>&1

:WfCfg
echo ++++++++++++++++ >> %LogFile% 2>&1
echo ++ wfcfg.bat +++ >> %LogFile% 2>&1
echo ++++++++++++++++ >> %LogFile% 2>&1
echo %DATE% %TIME% >> %LogFile% 2>&1
REM --- use Python to run WfCfg; pass all CLI arguments to WfCfg
echo [%TIME%] wfcfg.bat: Executing "%WfCfg%" %* >> %LogFile% 2>&1
"%Python%" "%WfCfg%" %*  >> %LogFile% 2>&1
goto exit

:NoWorkflows
echo [%TIME%] wfcfg.bat: Workflows not installed at %Workflows% >> %LogFile% 2>&1
goto exit

:NoPython
echo [%TIME%] wfcfg.bat:Python not installed at %Python% >> %LogFile% 2>&1
goto exit

:exit
echo [%TIME%] Releasing lock: %LockFile% >> %LogFile% 2>&1
del /f /q "%LockFile%"
echo [%TIME%] wfcfg.bat: Exiting. >> %LogFile% 2>&1
