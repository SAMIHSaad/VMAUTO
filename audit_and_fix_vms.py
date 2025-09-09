#!/usr/bin/env python3
"""
Audit and auto-fix VM persistence and ISO settings across existing VMs.
Also generates Start/Stop/Restart scripts that take snapshots before stop/restart.

Targets:
- Directories ending with _Output
- Directories under permanent_vms/*

Fixes:
- scsi0:0.mode = "independent-persistent"
- scsi0:0.redo = ""
- Detach ISO/CD-ROM (ide1:0, sata0:1, ide0:1) and prevent autoconnect
- Set boot order to prefer HDD
- Generate Start/Stop/Restart scripts next to the VMX so snapshot is taken before power off/restart

Usage:
  python audit_and_fix_vms.py [--dry-run]
"""
import argparse
import sys
from pathlib import Path
from typing import Tuple

BASE_DIR = Path(__file__).resolve().parent

CDROM_ADDRS = ["ide1:0", "sata0:1", "ide0:1"]


def set_or_add_vmx(lines: list[str], key: str, value: str) -> Tuple[list[str], bool]:
    """Set key="value" in VMX lines; add if missing. Returns (lines, changed)."""
    target = f'{key} = "{value}"'
    lowered = key.lower()
    changed = False
    for i, l in enumerate(lines):
        s = l.strip()
        if s.lower().startswith(lowered + " ") and "=" in s:
            if l != target:
                lines[i] = target
                changed = True
            return lines, changed
    # not found -> append
    lines.append(target)
    return lines, True


def detach_iso_devices(lines: list[str]) -> Tuple[list[str], bool]:
    changed_any = False
    for addr in CDROM_ADDRS:
        for k, v in [
            (f"{addr}.present", "FALSE"),
            (f"{addr}.startConnected", "FALSE"),
            (f"{addr}.deviceType", "cdrom-raw"),
            (f"{addr}.fileName", ""),
        ]:
            lines, ch = set_or_add_vmx(lines, k, v)
            changed_any = changed_any or ch
    return lines, changed_any


def enforce_persistence(lines: list[str]) -> Tuple[list[str], bool]:
    changed_any = False
    for k, v in [
        ("scsi0:0.mode", "independent-persistent"),
        ("scsi0:0.redo", ""),
    ]:
        lines, ch = set_or_add_vmx(lines, k, v)
        changed_any = changed_any or ch
    return lines, changed_any


def enforce_boot_order(lines: list[str]) -> Tuple[list[str], bool]:
    # Add both spellings for safety
    changed_any = False
    for k, v in [("bios.bootOrder", "hdd,cdrom"), ("bios.bootorder", "hdd,cdrom")]:
        lines, ch = set_or_add_vmx(lines, k, v)
        changed_any = changed_any or ch
    return lines, changed_any


def write_power_scripts(vmx_path: Path, dry_run: bool) -> None:
    vm_dir = vmx_path.parent
    vm_name = vmx_path.stem
    start_bat = f"""@echo off
REM Start VM (no snapshot here)
set VMX="{vmx_path}"
if not exist %VMX% (
  echo VMX not found: %VMX%
  pause
  exit /b 1
)
vmrun start %VMX% nogui
if %ERRORLEVEL% NEQ 0 (
  echo Failed to start VM
  pause
  exit /b %ERRORLEVEL%
)
echo VM started.
"""
    stop_bat = f"""@echo off
REM Stop VM after taking a snapshot
set VMX="{vmx_path}"
if not exist %VMX% (
  echo VMX not found: %VMX%
  pause
  exit /b 1
)
for /f "tokens=1-4 delims=/:. " %%a in ("%date% %time%") do set TS=%%d%%b%%c_%%e%%f%%g
set TS=%TS: =0%
set SNAP=PreStop_{vm_name}_%TS%

REM Create snapshot
vmrun snapshot %VMX% "%SNAP%"
if %ERRORLEVEL% NEQ 0 (
  echo Snapshot failed. Aborting stop to avoid data loss.
  pause
  exit /b %ERRORLEVEL%
)

REM Graceful stop first
vmrun stop %VMX% soft
if %ERRORLEVEL% NEQ 0 (
  echo Soft stop failed, forcing power off...
  vmrun stop %VMX% hard
)
echo VM stopped.
"""
    restart_bat = f"""@echo off
REM Restart VM with a snapshot before reboot
set VMX="{vmx_path}"
if not exist %VMX% (
  echo VMX not found: %VMX%
  pause
  exit /b 1
)
for /f "tokens=1-4 delims=/:. " %%a in ("%date% %time%") do set TS=%%d%%b%%c_%%e%%f%%g
set TS=%TS: =0%
set SNAP=PreRestart_{vm_name}_%TS%

REM Create snapshot
vmrun snapshot %VMX% "%SNAP%"
if %ERRORLEVEL% NEQ 0 (
  echo Snapshot failed. Aborting restart to avoid data loss.
  pause
  exit /b %ERRORLEVEL%
)

REM Try a guest OS reboot if tools are available; else stop+start
vmrun reset %VMX% soft
if %ERRORLEVEL% NEQ 0 (
  echo Soft reset failed, stopping and starting instead...
  vmrun stop %VMX% soft
  if %ERRORLEVEL% NEQ 0 vmrun stop %VMX% hard
  vmrun start %VMX% nogui
)
echo VM restarted.
"""
    mapping = {
        "Start_VM.bat": start_bat,
        "Stop_VM_WithSnapshot.bat": stop_bat,
        "Restart_VM_WithSnapshot.bat": restart_bat,
    }
    for name, content in mapping.items():
        target = vm_dir / name
        if dry_run:
            print(f"DRY: would write {target}")
        else:
            target.write_text(content)


def process_vmx(vmx_path: Path, dry_run: bool) -> Tuple[bool, bool]:
    """Process a single VMX file. Returns (changed_vmx, wrote_scripts)."""
    print(f"Processing: {vmx_path}")
    text = vmx_path.read_text(encoding="utf-8", errors="ignore")
    lines = [l.rstrip("\n\r") for l in text.splitlines()]

    changed = False
    lines, ch = enforce_persistence(lines)
    changed = changed or ch

    lines, ch = detach_iso_devices(lines)
    changed = changed or ch

    lines, ch = enforce_boot_order(lines)
    changed = changed or ch

    if changed and not dry_run:
        vmx_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
        print("  - VMX updated")
    elif changed and dry_run:
        print("  - DRY: VMX would be updated")
    else:
        print("  - VMX already compliant")

    # Always (re)write power scripts to ensure availability
    write_power_scripts(vmx_path, dry_run)
    return changed, True


def find_vmx_candidates(base: Path, extra_roots: list[Path] | None = None, deep_search: bool = True) -> list[Path]:
    candidates: list[Path] = []
    # *_Output at root
    for p in base.glob("*_Output"):
        if p.is_dir():
            candidates.extend(p.rglob("*.vmx"))
    # permanent_vms/*
    pv = base / "permanent_vms"
    if pv.is_dir():
        for sub in pv.iterdir():
            if sub.is_dir():
                candidates.extend(sub.rglob("*.vmx"))
    # any provided extra roots
    if extra_roots:
        for root in extra_roots:
            root = root.resolve()
            if root.is_file() and root.suffix.lower() == ".vmx":
                candidates.append(root)
            elif root.is_dir():
                candidates.extend(root.rglob("*.vmx"))
    # optional deep repo-wide search
    if deep_search:
        candidates.extend(base.rglob("*.vmx"))
    # de-duplicate
    dedup = []
    seen = set()
    for p in candidates:
        try:
            rp = p.resolve()
        except Exception:
            rp = p
        if rp not in seen:
            seen.add(rp)
            dedup.append(rp)
    return dedup


def main() -> int:
    parser = argparse.ArgumentParser(description="Audit and auto-fix VM persistence and ISO settings, generate power scripts.")
    parser.add_argument("--dry-run", action="store_true", help="Show actions without changing files")
    parser.add_argument("--search-roots", nargs="*", help="Additional folders or .vmx files to search")
    parser.add_argument("--no-deep", action="store_true", help="Disable repo-wide deep search")
    args = parser.parse_args()

    extra = [Path(p) for p in (args.search_roots or [])]
    vmx_files = find_vmx_candidates(BASE_DIR, extra_roots=extra, deep_search=not args.no_deep)
    if not vmx_files:
        print("No VMX files found. Provide paths with --search-roots if your VMs are elsewhere.")
        return 0

    updated = 0
    for vmx in vmx_files:
        ch, _ = process_vmx(vmx, args.dry_run)
        if ch:
            updated += 1

    print(f"\nCompleted. VMX updated: {updated}/{len(vmx_files)}")
    if args.dry_run:
        print("(dry run)")
    return 0


if __name__ == "__main__":
    sys.exit(main())