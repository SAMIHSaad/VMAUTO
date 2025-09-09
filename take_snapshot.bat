@echo off
REM Takes a snapshot of a VM.
REM Called by the guest OS on shutdown via VMware Tools.

SETLOCAL

REM --- CONFIGURATION ---
REM The base directory where all your VMs are stored (e.g., C:\Users\user\Documents\Virtual Machines)
SET BASE_VM_DIR=%~dp0

REM Log file for debugging snapshot issues.
SET LOG_FILE=%~dp0\snapshot_log.txt

REM --- SCRIPT LOGIC ---

IF "{%1}" == "{}" (
    echo [%date% %time%] ERROR: No VM name provided. >> "%LOG_FILE%"
    EXIT /B 1
)

SET VM_NAME=%1
SET SNAPSHOT_NAME=Shutdown-Snapshot-%date:~10,4%%date:~4,2%%date:~7,2%-%time:~0,2%%time:~3,2%%time:~6,2%
SET VM_OUTPUT_DIR="%BASE_VM_DIR%%VM_NAME%_Output"
SET VMX_PATH="%VM_OUTPUT_DIR%\vm_files\%VM_NAME%.vmx"

echo. >> "%LOG_FILE%"
echo [%date% %time%] ----- New Snapshot Request ----- >> "%LOG_FILE%"
echo [%date% %time%] VM Name: %VM_NAME% >> "%LOG_FILE%"
echo [%date% %time%] VMX Path: %VMX_PATH% >> "%LOG_FILE%"
echo [%date% %time%] Snapshot Name: %SNAPSHOT_NAME% >> "%LOG_FILE%"

IF NOT EXIST %VMX_PATH% (
    echo [%date% %time%] ERROR: VMX file not found at %VMX_PATH%. Snapshot failed. >> "%LOG_FILE%"
    EXIT /B 1
)

REM Find vmrun.exe - searches common locations
SET VMRUN_PATH=
IF EXIST "%PROGRAMFILES(X86)%\VMware\VMware Workstation\vmrun.exe" SET VMRUN_PATH="%PROGRAMFILES(X86)%\VMware\VMware Workstation\vmrun.exe"
IF EXIST "%PROGRAMFILES%\VMware\VMware Workstation\vmrun.exe" SET VMRUN_PATH="%PROGRAMFILES%\VMware\VMware Workstation\vmrun.exe"

IF NOT DEFINED VMRUN_PATH (
    echo [%date% %time%] ERROR: vmrun.exe not found. Please add it to your system's PATH or edit this script. >> "%LOG_FILE%"
    EXIT /B 1
)

echo [%date% %time%] Found vmrun at: %VMRUN_PATH% >> "%LOG_FILE%"
echo [%date% %time%] Executing snapshot command... >> "%LOG_FILE%"

%VMRUN_PATH% -T ws snapshot %VMX_PATH% %SNAPSHOT_NAME% >> "%LOG_FILE%" 2>>&1

IF %ERRORLEVEL% == 0 (
    echo [%date% %time%] Snapshot completed successfully. >> "%LOG_FILE%"
) ELSE (
    echo [%date% %time%] ERROR: Snapshot command failed with error code %ERRORLEVEL%. Check log for details. >> "%LOG_FILE%"
)

ENDLOCAL
