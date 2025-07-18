import subprocess
import sys
import logging
from odoo import api, SUPERUSER_ID

_logger = logging.getLogger(__name__)

def install_python_package(package_name, import_name=None):
    """Install a Python package using pip"""
    if import_name is None:
        import_name = package_name
    
    try:
        # Try to import the package first
        __import__(import_name)
        _logger.info(f"Package {package_name} is already installed")
        return True
    except ImportError:
        _logger.info(f"Installing {package_name}...")
        try:
            # Install the package
            subprocess.check_call([
                sys.executable, '-m', 'pip', 'install', package_name, '--user'
            ])
            _logger.info(f"Successfully installed {package_name}")
            return True
        except subprocess.CalledProcessError as e:
            _logger.error(f"Failed to install {package_name}: {e}")
            return False
        except Exception as e:
            _logger.error(f"Unexpected error installing {package_name}: {e}")
            return False

def pre_init_hook(cr):
    """Pre-installation hook to install Python dependencies"""
    _logger.info("CCAvenue Payment Gateway: Installing Python dependencies...")
    
    # Install required packages
    dependencies = [
        ('pycryptodome', 'Crypto'),
        ('requests', 'requests')
    ]
    
    failed_packages = []
    for package, import_name in dependencies:
        if not install_python_package(package, import_name):
            failed_packages.append(package)
    
    if failed_packages:
        error_msg = f"Failed to install required packages: {', '.join(failed_packages)}"
        _logger.error(error_msg)
        raise Exception(error_msg)
    
    _logger.info("All Python dependencies installed successfully")

def post_init_hook(cr, registry):
    """Post-installation hook"""
    _logger.info("CCAvenue Payment Gateway: Module installed successfully")
    
    # Verify imports work
    try:
        from Crypto.Cipher import AES
        from Crypto.Util.Padding import pad, unpad
        import requests
        _logger.info("All dependencies verified successfully")
    except ImportError as e:
        _logger.error(f"Import verification failed: {e}")