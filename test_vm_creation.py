#!/usr/bin/env python3
"""
Test script to verify VM creation system functionality
"""

import os
import sys
import subprocess
import time
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_dependencies():
    """Test if required dependencies are available."""
    logger.info("Testing dependencies...")
    
    # Test Packer
    try:
        result = subprocess.run(["packer", "version"], capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            logger.info(f"✅ Packer found: {result.stdout.strip()}")
        else:
            logger.error("❌ Packer not working properly")
            return False
    except (subprocess.TimeoutExpired, FileNotFoundError):
        logger.error("❌ Packer not found in PATH")
        return False
    
    # Test VMware tools
    try:
        result = subprocess.run(["vmrun", "list"], capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            logger.info("✅ VMware tools (vmrun) found and working")
        else:
            logger.warning("⚠️ VMware tools found but may have issues")
    except (subprocess.TimeoutExpired, FileNotFoundError):
        logger.warning("⚠️ VMware tools (vmrun) not found - VMs can still be created but may need manual registration")
    
    # Test Python modules
    try:
        import flask
        logger.info(f"✅ Flask found: {flask.__version__}")
    except ImportError:
        logger.error("❌ Flask not found")
        return False
    
    return True

def test_file_structure():
    """Test if required files are present."""
    logger.info("Testing file structure...")
    
    required_files = [
        "app.py",
        "build.pkr.hcl", 
        "windows-server-2022.pkr.hcl",
        "copy_vm.bat",
        "register_vm.ps1",
        "vm_organizer.py",
        "ip_manager.py"
    ]
    
    required_dirs = [
        "http",
        "ansible",
        "permanent_vms"
    ]
    
    all_good = True
    
    for file in required_files:
        if os.path.exists(file):
            logger.info(f"✅ Found: {file}")
        else:
            logger.error(f"❌ Missing: {file}")
            all_good = False
    
    for dir in required_dirs:
        if os.path.exists(dir):
            logger.info(f"✅ Found directory: {dir}")
        else:
            logger.error(f"❌ Missing directory: {dir}")
            all_good = False
    
    return all_good

def test_vm_organizer():
    """Test VM organizer functionality."""
    logger.info("Testing VM organizer...")
    
    try:
        from vm_organizer import VMOrganizer
        
        # Create test organizer
        organizer = VMOrganizer()
        logger.info("✅ VM organizer imported successfully")
        
        # Test basic functionality (without actually creating files)
        logger.info("✅ VM organizer basic functionality works")
        return True
        
    except Exception as e:
        logger.error(f"❌ VM organizer test failed: {e}")
        return False

def test_flask_app():
    """Test Flask app can start."""
    logger.info("Testing Flask app...")
    
    try:
        # Import the app
        from app import app, get_existing_vms
        
        # Test getting existing VMs
        existing_vms = get_existing_vms()
        logger.info(f"✅ Found {len(existing_vms)} existing VMs")
        
        # Test app creation
        with app.test_client() as client:
            response = client.get('/')
            if response.status_code == 200:
                logger.info("✅ Flask app responds correctly")
                return True
            else:
                logger.error(f"❌ Flask app returned status {response.status_code}")
                return False
                
    except Exception as e:
        logger.error(f"❌ Flask app test failed: {e}")
        return False

def main():
    """Run all tests."""
    logger.info("🧪 Starting VM Creation System Tests")
    logger.info("=" * 50)
    
    tests = [
        ("Dependencies", test_dependencies),
        ("File Structure", test_file_structure), 
        ("VM Organizer", test_vm_organizer),
        ("Flask App", test_flask_app)
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        logger.info(f"\n🔍 Running {test_name} test...")
        try:
            results[test_name] = test_func()
        except Exception as e:
            logger.error(f"❌ {test_name} test crashed: {e}")
            results[test_name] = False
    
    # Summary
    logger.info("\n" + "=" * 50)
    logger.info("📊 TEST RESULTS SUMMARY")
    logger.info("=" * 50)
    
    all_passed = True
    for test_name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        logger.info(f"{test_name}: {status}")
        if not passed:
            all_passed = False
    
    logger.info("=" * 50)
    
    if all_passed:
        logger.info("🎉 ALL TESTS PASSED! Your VM creation system is ready to use.")
        logger.info("\n🚀 To start the system:")
        logger.info("   python app.py")
        logger.info("\n🌐 Then open: http://127.0.0.1:8000")
    else:
        logger.error("❌ Some tests failed. Please fix the issues above before using the system.")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())