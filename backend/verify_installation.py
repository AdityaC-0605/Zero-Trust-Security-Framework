#!/usr/bin/env python3
"""
Installation Verification Script
Checks if all required Python packages are installed
"""

import sys

def check_package(package_name, import_name=None):
    """Check if a package is installed"""
    if import_name is None:
        import_name = package_name
    
    try:
        __import__(import_name)
        print(f"✓ {package_name} is installed")
        return True
    except ImportError:
        print(f"✗ {package_name} is NOT installed")
        return False

def main():
    print("=" * 50)
    print("Python Package Installation Verification")
    print("=" * 50)
    print()
    
    packages = [
        ("Flask", "flask"),
        ("Flask-CORS", "flask_cors"),
        ("Firebase Admin", "firebase_admin"),
        ("PyJWT", "jwt"),
        ("Python-dotenv", "dotenv"),
        ("PyOTP", "pyotp"),
        ("Cryptography", "cryptography"),
        ("Gunicorn", "gunicorn"),
        ("Pytest", "pytest"),
        ("PyTorch", "torch"),
        ("Scikit-learn", "sklearn"),
        ("NumPy", "numpy"),
        ("Pandas", "pandas"),
        ("TensorFlow", "tensorflow"),
        ("Flask-SocketIO", "flask_socketio"),
        ("Redis", "redis"),
        ("Celery", "celery"),
        ("Web3", "web3"),
        ("IPFS HTTP Client", "ipfshttpclient"),
        ("Anthropic", "anthropic"),
        ("GeoIP2", "geoip2"),
        ("Requests", "requests"),
        ("NLTK", "nltk"),
        ("spaCy", "spacy"),
        ("Geopy", "geopy"),
    ]
    
    installed = 0
    missing = 0
    
    for package_name, import_name in packages:
        if check_package(package_name, import_name):
            installed += 1
        else:
            missing += 1
    
    print()
    print("=" * 50)
    print(f"Summary: {installed} installed, {missing} missing")
    print("=" * 50)
    
    if missing > 0:
        print()
        print("To install missing packages, run:")
        print("  pip install -r requirements.txt")
        return 1
    else:
        print()
        print("All packages are installed! ✓")
        return 0

if __name__ == "__main__":
    sys.exit(main())
