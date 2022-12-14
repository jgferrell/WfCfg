@echo off
REM --- "%Python%" = path to local python.exe file
set Python=C:\Program Files\Python311\python.exe
REM --- "%Workflows%" = path to local Sirsi Workflows client launcher
set Workflows=C:\Program Files (x86)\Sirsi\JWF\wf.bat

REM --- "%WfCfg%" = path to wfcfg.py
set WfCfg=%~dp0wfcfg.py
REM --- %LogFile% = path to WfCfg log file
set LogFile=%windir%\temp\wfcfg.log

echo ++++++++++++++++ >> %LogFile% 2>&1
echo ++ wfcfg.bat +++ >> %LogFile% 2>&1
echo ++++++++++++++++ >> %LogFile% 2>&1
echo %DATE% %TIME% >> %LogFile% 2>&1

REM --- don't try to run WfCfg unless both Workflows and Python are installed
if not exist "%Workflows%" goto NoWorkflows
if not exist "%Python%" goto NoPython

:WfCfg
REM --- use Python to run WfCfg; pass all CLI arguments to WfCfg
echo wfcfg.bat: Executing "%WfCfg%" %* >> %LogFile% 2>&1
"%Python%" "%WfCfg%" %*  >> %LogFile% 2>&1
goto exit

:NoWorkflows
echo wfcfg.bat: Workflows not installed at %Workflows% >> %LogFile% 2>&1
goto exit

:NoPython
echo wfcfg.bat:Python not installed at %Python% >> %LogFile% 2>&1
goto exit

:exit
echo wfcfg.bat: Exiting. >> %LogFile% 2>&1
