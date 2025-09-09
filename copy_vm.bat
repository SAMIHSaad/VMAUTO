@echo off
setlocal enabledelayedexpansion

REM Simple helper to copy/register a built VM to permanent_vms and open it in VMware Workstation
REM Usage: copy_vm.bat "<source_vm_output_dir>" "<destination_vm_name>"

if "%~1"=="" goto :usage
if "%~2"=="" goto :usage

set "SRC=%~1"
set "DEST=%~dp0permanent_vms\%~2"

REM Call the PowerShell script to move/copy, register, and open the VM
powershell -ExecutionPolicy Bypass -File "%~dp0register_permanent_vm.ps1" -sourceDirectory "%SRC%" -destinationDirectory "%DEST%" -OpenAfterRegister
exit /b %ERRORLEVEL%

:usage
echo Usage: %~n0 "source_vm_output_dir" "destination_vm_name"
echo Example: %~n0 "%~dp0output-ubuntu-automated" "ubuntu-automated"
exit /b 1