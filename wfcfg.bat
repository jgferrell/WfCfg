@echo off

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

:WfCfg
echo wfcfg.bat: %DATE% %TIME% >> %LogFile% 2>&1
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
echo [%TIME%] wfcfg.bat: Exiting. >> %LogFile% 2>&1
