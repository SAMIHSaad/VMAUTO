#!/usr/bin/env python3
"""
Setup Script for VM Automation System
Initializes the system and checks dependencies.
"""

import os
import sys
import subprocess
from pathlib import Path

def check_python():
    """Check Python version."""
    print("🐍 Checking Python...")
    version = sys.version_info
    if version.major >= 3 and version.minor >= 7:
        print(f"   ✅ Python {version.major}.{version.minor}.{version.micro} (OK)")
        return True
    else:
        print(f"   ❌ Python {version.major}.{version.minor}.{version.micro} (Need 3.7+)")
        return False

def check_dependencies():
    """Check system dependencies."""
    print("\n🔧 Checking dependencies...")
    
    dependencies = {
        'packer': 'packer version',
        'flask': 'python -c "import flask; print(flask.__version__)"',
    }
    
    results = {}
    
    for dep, cmd in dependencies.items():
        try:
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            if result.returncode == 0:
                print(f"   ✅ {dep} (Available)")
                results[dep] = True
            else:
                print(f"   ❌ {dep} (Not found)")
                results[dep] = False
        except Exception:
            print(f"   ❌ {dep} (Error checking)")
            results[dep] = False
    
    return results

def install_python_packages():
    """Install required Python packages."""
    print("\n📦 Installing Python packages...")
    
    packages = ['flask', 'pathlib']
    
    for package in packages:
        try:
            print(f"   Installing {package}...")
            result = subprocess.run([sys.executable, '-m', 'pip', 'install', package], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                print(f"   ✅ {package} installed")
            else:
                print(f"   ⚠️  {package} installation warning: {result.stderr}")
        except Exception as e:
            print(f"   ❌ Error installing {package}: {e}")

def create_sample_config():
    """Create sample configuration files if they don't exist."""
    print("\n⚙️  Checking configuration...")
    
    base_dir = Path.cwd()
    
    # Check if ips.txt exists
    ips_file = base_dir / 'ips.txt'
    if not ips_file.exists():
        print("   Creating sample ips.txt...")
        sample_ips = """# Available IP addresses for VMs
# Add one IP per line
192.168.1.100
192.168.1.101
192.168.1.102
192.168.1.103
192.168.1.104
"""
        with open(ips_file, 'w') as f:
            f.write(sample_ips)
        print("   ✅ Created ips.txt with sample IPs")
    else:
        print("   ✅ ips.txt exists")

def check_vmware():
    """Check VMware installation."""
    print("\n🖥️  Checking VMware...")
    
    # Common VMware paths
    vmware_paths = [
        r"C:\Program Files (x86)\VMware\VMware Workstation\vmrun.exe",
        r"C:\Program Files\VMware\VMware Workstation\vmrun.exe",
        r"C:\Program Files (x86)\VMware\VMware Player\vmrun.exe",
        r"C:\Program Files\VMware\VMware Player\vmrun.exe"
    ]
    
    vmware_found = False
    for path in vmware_paths:
        if Path(path).exists():
            print(f"   ✅ VMware found at: {path}")
            vmware_found = True
            break
    
    if not vmware_found:
        print("   ⚠️  VMware not found in standard locations")
        print("   💡 Please install VMware Workstation or Player")
    
    return vmware_found

def check_packer():
    """Check Packer installation."""
    print("\n📦 Checking Packer...")
    
    try:
        result = subprocess.run(['packer', 'version'], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"   ✅ Packer found: {result.stdout.strip()}")
            return True
        else:
            print("   ❌ Packer not found")
            return False
    except FileNotFoundError:
        print("   ❌ Packer not found")
        return False

def show_next_steps(vmware_ok, packer_ok):
    """Show next steps to user."""
    print("\n" + "="*60)
    print("SETUP COMPLETE!")
    print("="*60)
    
    if vmware_ok and packer_ok:
        print("\n🎉 System is ready to use!")
        print("\nNext steps:")
        print("1. Start the web interface: python app.py")
        print("2. Open http://127.0.0.1:8000 in your browser")
        print("3. Create your first VM!")
        print("\nOr use command line:")
        print('   python vm_manager.py create "MyFirstVM"')
    else:
        print("\n⚠️  Additional setup required:")
        
        if not packer_ok:
            print("\n📦 Install Packer:")
            print("   1. Download from: https://www.packer.io/downloads")
            print("   2. Add to PATH environment variable")
        
        if not vmware_ok:
            print("\n🖥️  Install VMware:")
            print("   1. Download VMware Workstation or Player")
            print("   2. Install with default settings")
    
    print("\n📚 Documentation:")
    print("   - Read VM_AUTOMATION_GUIDE.md for detailed instructions")
    print("   - Run: python system_status.py to check system status")
    print("   - Run: python vm_manager.py --help for command help")

def main():
    """Main setup function."""
    print("🚀 VM Automation System Setup")
    print("="*60)
    
    # Check Python
    if not check_python():
        print("\n❌ Python version too old. Please upgrade to Python 3.7+")
        return 1
    
    # Install Python packages
    install_python_packages()
    
    # Check dependencies
    deps = check_dependencies()
    
    # Create sample config
    create_sample_config()
    
    # Check VMware and Packer
    vmware_ok = check_vmware()
    packer_ok = check_packer()
    
    # Show next steps
    show_next_steps(vmware_ok, packer_ok)
    
    return 0

if __name__ == "__main__":
    sys.exit(main())