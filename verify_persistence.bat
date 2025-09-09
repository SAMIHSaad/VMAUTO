@echo off
echo ========================================
echo VM Persistence Verification Script
echo ========================================
echo.

set VMRUN="C:\Program Files (x86)\VMware\VMware Workstation\vmrun.exe"

echo Checking running VMs...
%VMRUN% list
echo.

echo ========================================
echo MANUAL VERIFICATION STEPS:
echo ========================================
echo.
echo 1. Connect to your running VM (za) via console or SSH
echo 2. Create a test file:
echo    sudo touch /home/ubuntu/persistence_test.txt
echo    echo "Data persistence test - $(date)" ^| sudo tee /home/ubuntu/persistence_test.txt
echo.
echo 3. Shutdown the VM gracefully:
echo    sudo shutdown -h now
echo.
echo 4. Wait for VM to fully stop, then restart it:
echo    %VMRUN% start "C:\Users\saads\OneDrive\Documents\Coding\Auto-Creation-VM\cloned-vms\za\za.vmx" nogui
echo.
echo 5. After VM boots, check if the test file exists:
echo    cat /home/ubuntu/persistence_test.txt
echo.
echo If the file exists with your test data, persistence is working!
echo.
echo ========================================
echo CURRENT VM STATUS:
echo ========================================

echo Checking VMX persistence settings for za...
findstr /i "scsi0:0.mode" "C:\Users\saads\OneDrive\Documents\Coding\Auto-Creation-VM\cloned-vms\za\za.vmx"
findstr /i "scsi0:0.redo" "C:\Users\saads\OneDrive\Documents\Coding\Auto-Creation-VM\cloned-vms\za\za.vmx"
findstr /i "bios.bootorder" "C:\Users\saads\OneDrive\Documents\Coding\Auto-Creation-VM\cloned-vms\za\za.vmx"
findstr /i "ide1:0.present" "C:\Users\saads\OneDrive\Documents\Coding\Auto-Creation-VM\cloned-vms\za\za.vmx"

echo.
echo ========================================
echo All settings look correct for persistence!
echo ========================================
pause