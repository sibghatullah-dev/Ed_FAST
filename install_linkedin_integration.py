#!/usr/bin/env python3
"""
LinkedIn Integration Installation Script for EdFast Platform
This script helps install and configure the LinkedIn scraping functionality.
"""

import os
import sys
import subprocess
import platform
from pathlib import Path

def print_header():
    """Print installation header."""
    print("=" * 60)
    print("LinkedIn Integration Installation for EdFast Platform")
    print("=" * 60)
    print()

def check_python_version():
    """Check if Python version is compatible."""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("❌ Python 3.8 or higher is required")
        print(f"Current version: {version.major}.{version.minor}.{version.micro}")
        return False
    print(f"✅ Python version: {version.major}.{version.minor}.{version.micro}")
    return True

def install_requirements():
    """Install required packages."""
    print("\n📦 Installing required packages...")
    
    requirements_files = [
        "requirements.txt",
        "flask_api/requirements.txt"
    ]
    
    for req_file in requirements_files:
        if os.path.exists(req_file):
            print(f"Installing from {req_file}...")
            try:
                subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", req_file])
                print(f"✅ Successfully installed packages from {req_file}")
            except subprocess.CalledProcessError as e:
                print(f"❌ Failed to install packages from {req_file}: {e}")
                return False
        else:
            print(f"⚠️ Requirements file not found: {req_file}")
    
    return True

def check_chrome_driver():
    """Check if Chrome WebDriver is available."""
    print("\n🌐 Checking Chrome WebDriver...")
    
    try:
        result = subprocess.run(["chromedriver", "--version"], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print(f"✅ Chrome WebDriver found: {result.stdout.strip()}")
            return True
    except (subprocess.TimeoutExpired, FileNotFoundError):
        pass
    
    print("❌ Chrome WebDriver not found")
    print("\nTo install Chrome WebDriver:")
    
    system = platform.system().lower()
    if system == "windows":
        print("1. Download from: https://chromedriver.chromium.org/")
        print("2. Extract chromedriver.exe to a folder in your PATH")
        print("3. Or use: pip install webdriver-manager")
    elif system == "darwin":  # macOS
        print("1. Run: brew install chromedriver")
        print("2. Or use: pip install webdriver-manager")
    elif system == "linux":
        print("1. Run: sudo apt-get install chromium-chromedriver")
        print("2. Or use: pip install webdriver-manager")
    
    return False

def create_directories():
    """Create necessary directories."""
    print("\n📁 Creating directories...")
    
    directories = [
        "linkedin",
        "chrome_user_data",
        "downloaded_images",
        "flask_api/uploads/linkedin"
    ]
    
    for directory in directories:
        try:
            os.makedirs(directory, exist_ok=True)
            print(f"✅ Created directory: {directory}")
        except Exception as e:
            print(f"❌ Failed to create directory {directory}: {e}")
            return False
    
    return True

def test_imports():
    """Test if key packages can be imported."""
    print("\n🧪 Testing package imports...")
    
    packages = [
        ("jobspy", "python-jobspy"),
        ("selenium", "selenium"),
        ("pandas", "pandas"),
        ("requests", "requests"),
        ("google.auth", "google-auth"),
        ("pyperclip", "pyperclip")
    ]
    
    failed_imports = []
    
    for package, pip_name in packages:
        try:
            __import__(package)
            print(f"✅ {package}")
        except ImportError:
            print(f"❌ {package} (install with: pip install {pip_name})")
            failed_imports.append(pip_name)
    
    if failed_imports:
        print(f"\n⚠️ Some packages failed to import. Install them with:")
        print(f"pip install {' '.join(failed_imports)}")
        return False
    
    return True

def create_sample_config():
    """Create sample configuration files."""
    print("\n⚙️ Creating sample configuration...")
    
    # Create sample .env file
    env_content = """# LinkedIn Integration Configuration
# Copy this to .env and update with your values

# Google Drive Integration (Optional)
GOOGLE_DRIVE_FOLDER_ID=your_folder_id_here
GOOGLE_CREDENTIALS_PATH=credentials.json

# Chrome WebDriver Settings
CHROME_HEADLESS=false
CHROME_USER_DATA_DIR=chrome_user_data

# LinkedIn Scraping Settings
LINKEDIN_MAX_JOBS_PER_SEARCH=100
LINKEDIN_MAX_POSTS_PER_SCRAPE=200
LINKEDIN_REQUEST_DELAY=2
"""
    
    try:
        with open(".env.sample", "w") as f:
            f.write(env_content)
        print("✅ Created .env.sample")
    except Exception as e:
        print(f"❌ Failed to create .env.sample: {e}")
    
    # Create sample credentials template
    creds_content = """{
  "type": "service_account",
  "project_id": "your-project-id",
  "private_key_id": "your-private-key-id",
  "private_key": "-----BEGIN PRIVATE KEY-----\\nYOUR_PRIVATE_KEY\\n-----END PRIVATE KEY-----\\n",
  "client_email": "your-service-account@your-project.iam.gserviceaccount.com",
  "client_id": "your-client-id",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/your-service-account%40your-project.iam.gserviceaccount.com"
}
"""
    
    try:
        with open("credentials.json.sample", "w") as f:
            f.write(creds_content)
        print("✅ Created credentials.json.sample")
    except Exception as e:
        print(f"❌ Failed to create credentials.json.sample: {e}")

def print_next_steps():
    """Print next steps for the user."""
    print("\n" + "=" * 60)
    print("🎉 LinkedIn Integration Installation Complete!")
    print("=" * 60)
    print()
    print("Next Steps:")
    print("1. Copy .env.sample to .env and configure your settings")
    print("2. If using Google Drive integration:")
    print("   - Create a Google Cloud Project")
    print("   - Enable Google Drive API")
    print("   - Create service account credentials")
    print("   - Copy credentials.json.sample to credentials.json and update")
    print("3. Start the Flask API server:")
    print("   cd flask_api && python app.py")
    print("4. Start the frontend development server:")
    print("   cd edfast-frontend && npm run dev")
    print("5. Visit http://localhost:3000/linkedin to use the LinkedIn features")
    print()
    print("Documentation: See LINKEDIN_INTEGRATION_GUIDE.md for detailed usage")
    print("Support: Check the troubleshooting section in the guide")

def main():
    """Main installation function."""
    print_header()
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Install requirements
    if not install_requirements():
        print("\n❌ Installation failed during package installation")
        sys.exit(1)
    
    # Check Chrome WebDriver
    chrome_available = check_chrome_driver()
    
    # Create directories
    if not create_directories():
        print("\n❌ Installation failed during directory creation")
        sys.exit(1)
    
    # Test imports
    if not test_imports():
        print("\n⚠️ Some packages failed to import. Please install them manually.")
    
    # Create sample configuration
    create_sample_config()
    
    # Print next steps
    print_next_steps()
    
    if not chrome_available:
        print("\n⚠️ Note: Chrome WebDriver is not installed. Post scraping will not work.")
        print("Please install Chrome WebDriver to use all features.")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⏹️ Installation interrupted by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error during installation: {e}")
        sys.exit(1)
