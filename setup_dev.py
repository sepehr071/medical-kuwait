#!/usr/bin/env python3
"""
Development setup script for Kuwait Medical Clinic Flask Backend
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def run_command(command, description):
    """Run a command and handle errors"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e}")
        if e.stdout:
            print(f"STDOUT: {e.stdout}")
        if e.stderr:
            print(f"STDERR: {e.stderr}")
        return False

def check_prerequisites():
    """Check if required software is installed"""
    print("🔍 Checking prerequisites...")
    
    # Check Python
    try:
        python_version = subprocess.check_output([sys.executable, "--version"], text=True)
        print(f"✅ Python: {python_version.strip()}")
    except:
        print("❌ Python not found")
        return False
    
    # Check MongoDB
    try:
        mongo_version = subprocess.check_output(["mongod", "--version"], text=True, stderr=subprocess.DEVNULL)
        print("✅ MongoDB: Available")
    except:
        print("❌ MongoDB not found - please install MongoDB Community Server")
        return False
    
    # Check if MongoDB is running
    try:
        subprocess.check_output(["mongosh", "--eval", "db.runCommand('ping')"], text=True, stderr=subprocess.DEVNULL)
        print("✅ MongoDB: Running")
    except:
        print("⚠️  MongoDB: Not running - please start MongoDB service")
    
    return True

def setup_virtual_environment():
    """Set up Python virtual environment"""
    venv_path = Path("venv")
    
    if venv_path.exists():
        print("✅ Virtual environment already exists")
        return True
    
    return run_command(f"{sys.executable} -m venv venv", "Creating virtual environment")

def install_dependencies():
    """Install Python dependencies"""
    if os.name == 'nt':  # Windows
        pip_command = "venv\\Scripts\\pip"
    else:  # Unix/Linux/macOS
        pip_command = "venv/bin/pip"
    
    return run_command(f"{pip_command} install -r requirements.txt", "Installing dependencies")

def setup_environment_file():
    """Set up environment file"""
    env_file = Path(".env")
    env_example = Path(".env.example")
    
    if env_file.exists():
        print("✅ Environment file already exists")
        return True
    
    if env_example.exists():
        shutil.copy2(env_example, env_file)
        print("✅ Environment file created from template")
        print("⚠️  Please update .env file with your actual configuration values")
        return True
    else:
        print("❌ .env.example not found")
        return False

def initialize_database():
    """Initialize database with sample data"""
    if os.name == 'nt':  # Windows
        python_command = "venv\\Scripts\\python"
    else:  # Unix/Linux/macOS
        python_command = "venv/bin/python"
    
    return run_command(f"{python_command} migrations/init_db.py init", "Initializing database")

def main():
    """Main setup function"""
    print("🚀 Kuwait Medical Clinic Flask Backend Setup")
    print("=" * 50)
    
    # Check prerequisites
    if not check_prerequisites():
        print("❌ Prerequisites check failed. Please install required software.")
        sys.exit(1)
    
    # Setup steps
    steps = [
        (setup_virtual_environment, "Virtual environment setup"),
        (install_dependencies, "Dependencies installation"),
        (setup_environment_file, "Environment configuration"),
        (initialize_database, "Database initialization")
    ]
    
    failed_steps = []
    
    for step_func, step_name in steps:
        if not step_func():
            failed_steps.append(step_name)
    
    print("\n" + "=" * 50)
    if failed_steps:
        print("❌ Setup completed with errors:")
        for step in failed_steps:
            print(f"   - {step}")
        print("\nPlease resolve the errors and run the setup again.")
    else:
        print("✅ Setup completed successfully!")
        print("\n📋 Next steps:")
        print("1. Review and update .env file with your configuration")
        print("2. Start the development server:")
        if os.name == 'nt':  # Windows
            print("   venv\\Scripts\\python run.py")
        else:  # Unix/Linux/macOS
            print("   venv/bin/python run.py")
        print("3. Test the API at http://localhost:5000/api/health")
    
    print("=" * 50)

if __name__ == "__main__":
    main()