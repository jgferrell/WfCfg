@echo off
set PythonInstaller=%~1
set PythonFilepath=%~2
set LocalPythonDir=%~3
set TempDir=%~4
set Python=%LocalPythonDir%\python.exe

REM --- Install Python if it's not already installed
if not exist "%Python%" (
   set TempInstaller=%TempDir%\%PythonInstaller%
   if not exist "%TempInstaller%" (
      echo Copying installer to temp directory.
      copy "%PythonFilepath%" "%TempDir%"
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
