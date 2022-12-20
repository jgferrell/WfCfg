@echo off
REM --- %RemoteInstaller% = full path to the server-shared installer
set RemoteInstaller=%~2%~1

REM --- %LocalPythonDir% = target installation directory
set LocalPythonDir=%~3

REM --- %TempDir% = local temporary directory for storing the installer
set TempDir=%~4

REM --- %TempInstaller% = full path to local copy of installer (in %TempDir%)
set TempInstaller=%~4\%~1

REM --- %Python% = full path to Python executable (in %LocalPythonDir%)
set Python=%~3\python.exe

REM --- Remove Python if it's currently installed
if exist "%Python%" (
   if not exist "%TempInstaller%" (
      echo Copying installer to temp directory.
      copy "%RemoteInstaller%" "%TempDir%"
   )
   echo Running installer from temp directory.
   call "%TempInstaller%" /quiet /uninstall
   if not exist "%Python%" (
      rmdir /q /s "%LocalPythonDir%"
      echo Python now is now uninstalled.      
   ) else (
      echo ERROR: Python was not successfully uninstalled.
   )
) else (
   echo Python is not currently installed to "%LocalPythonDir%".
)
