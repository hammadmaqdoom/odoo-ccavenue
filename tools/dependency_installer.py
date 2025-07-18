import subprocess
import sys
import logging
import importlib

_logger = logging.getLogger(__name__)

class DependencyInstaller:
    """Utility class to handle Python package installation"""
    
    REQUIRED_PACKAGES = {
        'pycryptodome': {
            'import_name': 'Crypto',
            'test_import': 'from Crypto.Cipher import AES',
            'description': 'Encryption library for secure payments'
        },
        'requests': {
            'import_name': 'requests',
            'test_import': 'import requests',
            'description': 'HTTP library for API communications'
        }
    }

    @classmethod
    def check_package(cls, package_name, import_name):
        """Check if a package is installed and importable"""
        try:
            importlib.import_module(import_name)
            return True
        except ImportError:
            return False

    @classmethod
    def install_package(cls, package_name, user_install=True):
        """Install a Python package using pip"""
        cmd = [sys.executable, '-m', 'pip', 'install', package_name]
        if user_install:
            cmd.append('--user')
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            _logger.info(f"Successfully installed {package_name}")
            return True, result.stdout
        except subprocess.CalledProcessError as e:
            _logger.error(f"Failed to install {package_name}: {e.stderr}")
            return False, e.stderr
        except Exception as e:
            _logger.error(f"Unexpected error installing {package_name}: {e}")
            return False, str(e)

    @classmethod
    def install_all_dependencies(cls):
        """Install all required dependencies"""
        results = {}
        
        for package_name, info in cls.REQUIRED_PACKAGES.items():
            if cls.check_package(package_name, info['import_name']):
                _logger.info(f"{package_name} is already installed")
                results[package_name] = {'status': 'already_installed', 'message': 'Already installed'}
                continue
            
            _logger.info(f"Installing {package_name}...")
            success, message = cls.install_package(package_name)
            
            if success:
                # Verify installation
                if cls.check_package(package_name, info['import_name']):
                    results[package_name] = {'status': 'success', 'message': message}
                else:
                    results[package_name] = {'status': 'verification_failed', 'message': 'Installation succeeded but import failed'}
            else:
                results[package_name] = {'status': 'failed', 'message': message}
        
        return results

    @classmethod
    def get_installation_status(cls):
        """Get current installation status of all dependencies"""
        status = {}
        for package_name, info in cls.REQUIRED_PACKAGES.items():
            status[package_name] = {
                'installed': cls.check_package(package_name, info['import_name']),
                'description': info['description']
            }
        return status