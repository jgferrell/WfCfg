@echo off
REM --- %PythonInstaller% = the name (without path) of Python installer
set PythonInstaller=python-3.11.0-amd64.exe

REM --- %TargetPythonDir% = directory to which we install Python
set TargetPythonDir=%ProgramFiles%\Python311

REM --- %TempDir% = temporary directory to which we copy install file
set TempDir=%windir%\temp

REM --- %InstallerDir% = the filepath of the directory containing this 
REM     file and %PythonInstaller% --- NOTE: INCLUDES TRAILING SLASH
set InstallerDir=%~dp0

if "%1" == "install" (
   echo Attempting to install Python.
   call "%~dp0python_install.bat" "%PythonInstaller%" "%InstallerDir%" "%TargetPythonDir%" "%TempDir%"
) else (
   if "%1" == "uninstall" (
      echo Attempting to uninstall Python.
      call "%~dp0python_uninstall.bat" "%PythonInstaller%" "%InstallerDir%" "%TargetPythonDir%" "%TempDir%"
   ) else (
      echo Error: run `python.bat install` or `python.bat uninstall`.
   )
)
