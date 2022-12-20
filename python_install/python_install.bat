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

REM --- Install Python if it's not already installed
if not exist "%Python%" (
   if not exist "%TempInstaller%" (
      echo Copying installer to temp directory.
      copy "%RemoteInstaller%" "%TempDir%"
   )
   echo Running installer from temp directory.
   call "%TempInstaller%" /quiet InstallAllUsers=1 TargetDir="%LocalPythonDir%" Shortcuts=0 Include_doc=0 Include_tcltk=0 LongPathsEnabled=1
   if exist "%Python%" (
      echo Python now installed to "%LocalPythonDir%".
   ) else (
      echo ERROR: Python was not successfully installed.
      goto exit
   )
) else (
   echo Python already installed to "%LocalPythonDir%".
)

REM --- Create "usr" directory (for custom scripts) if it's not already there
set UsrDir=%LocalPythonDir%\usr
if not exist "%UsrDir%" (
   echo Making `usr` directory for local scripts.
   mkdir "%UsrDir%"
)

REM --- upgrade Pip to latest version
echo Updating Pip to latest version.
"%Python%" -m pip install --upgrade pip

:exit
