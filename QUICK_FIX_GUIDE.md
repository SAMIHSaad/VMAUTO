# Quick Fix Guide - VM Data Loss Issue

## 🚨 Problem
VMs lose all data after power off or restart.

## ✅ Solution Applied
**Your VMs have been automatically fixed!**

## 🔍 Check Status
```bash
python fix_vm_persistence.py --check all
```

## 🔧 If You Still Have Issues

### Fix All VMs
```bash
python fix_vm_persistence.py --fix all
```

### Fix Specific VM
```bash
python fix_vm_persistence.py --fix vm_name
```

### Test VM Persistence
```bash
python fix_vm_persistence.py --test vm_name
```

## 📁 Safe VM Operations

Use these scripts (created automatically in each VM folder):
- `Start_VM.bat` - Start VM
- `Stop_VM_WithSnapshot.bat` - Stop with safety snapshot
- `Restart_VM_WithSnapshot.bat` - Restart with safety snapshot

## ✅ Current Status

All your VMs are now configured with:
- ✅ Persistent disk mode
- ✅ Correct boot order (hard disk first)
- ✅ CD-ROM devices detached
- ✅ Automatic snapshots enabled
- ✅ Safety scripts created

## 🧪 Manual Test

1. Start your VM
2. Create test file: `echo "test data" > /tmp/test.txt`
3. Shutdown: `sudo shutdown -h now`
4. Start VM again
5. Check file: `cat /tmp/test.txt`

If the file exists, persistence is working! 🎉

## 📞 Need Help?

Run the diagnostic tool:
```bash
python fix_vm_persistence.py --check vm_name
```

This will show you exactly what's configured and any remaining issues.