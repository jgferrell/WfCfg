@echo off
set PythonInstaller=%~1
set PythonFilepath=%~2
set LocalPythonDir=%~3
set TempDir=%~4
set Python=%LocalPythonDir%\python.exe

REM --- Remove Python if it's currently installed
if exist "%Python%" (
   set TempInstaller=%TempDir%\%PythonInstaller%
   if not exist "%TempInstaller%" (
      echo Copying installer to temp directory.
      copy "%PythonFilepath%" "%TempDir%"
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
