@echo off
REM --- %PythonInstaller% = the name (without path) of Python installer
set PythonInstaller=python-3.11.0-amd64.exe

REM --- %LocalPythonDir% = directory to which we install Python
set LocalPythonDir=%ProgramFiles%\Python311

REM --- %TempDir% = temporary directory to which we copy install file
set TempDir=%windir%\temp

REM --- %PythonFilepath% = the complete path to Python installer, assuming
REM        that is in the same directory as the Python BAT files
set PythonFilepath=%~dp0%PythonInstaller%

if "%1" == "install" (
   echo Attempting to install Python.
   call "%~dp0python_install.bat" "%PythonInstaller%" "%PythonFilePath%" "%LocalPythonDir%" "%TempDir%"
) else (
   if "%1" == "uninstall" (
      echo Attempting to uninstall Python.
      call "%~dp0python_uninstall.bat" "%PythonInstaller%" "%PythonFilePath%" "%LocalPythonDir%" "%TempDir%"
   ) else (
      echo Error: run `python.bat install` or `python.bat uninstall`.
   )
)
