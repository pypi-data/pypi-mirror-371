#!/usr/bin/env python3
"""
Setup script for the LangGraph Code Generation System
Automates installation, dependency management, and initial configuration.
"""

import os
import sys
import subprocess
import platform
from pathlib import Path

def print_header():
    """Print setup header."""
    print("=" * 60)
    print("🚀 LangGraph Code Generation System Setup")
    print("=" * 60)

def check_python_version():
    """Check if Python version is compatible."""
    print("🔍 Checking Python version...")
    
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required!")
        print(f"   Current version: {sys.version}")
        sys.exit(1)
    
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor} detected")
    return True

def check_virtual_environment():
    """Check if running in a virtual environment."""
    print("🔍 Checking virtual environment...")
    
    in_venv = hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix)
    
    if in_venv:
        print("✅ Running in virtual environment")
        return True
    else:
        print("⚠️  Not running in virtual environment")
        print("   It's recommended to use a virtual environment")
        response = input("   Continue anyway? (y/N): ").lower().strip()
        return response in ['y', 'yes']

def create_virtual_environment():
    """Create a virtual environment if requested."""
    print("🔍 Virtual environment setup...")
    
    response = input("   Create a new virtual environment? (Y/n): ").lower().strip()
    if response in ['', 'y', 'yes']:
        venv_name = input("   Virtual environment name (default: venv): ").strip() or "venv"
        
        try:
            subprocess.run([sys.executable, "-m", "venv", venv_name], check=True)
            print(f"✅ Virtual environment '{venv_name}' created successfully")
            
            if platform.system() == "Windows":
                activate_script = f"{venv_name}\\Scripts\\activate"
                print(f"   To activate: {activate_script}")
            else:
                activate_script = f"source {venv_name}/bin/activate"
                print(f"   To activate: {activate_script}")
            
            return venv_name
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to create virtual environment: {e}")
            return None
    else:
        print("   Skipping virtual environment creation")
        return None

def install_dependencies():
    """Install required dependencies."""
    print("📦 Installing dependencies...")
    
    try:
        # Upgrade pip first
        subprocess.run([sys.executable, "-m", "pip", "install", "--upgrade", "pip"], check=True)
        print("✅ Pip upgraded")
        
        # Install requirements
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], check=True)
        print("✅ Dependencies installed successfully")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        return False
    except FileNotFoundError:
        print("❌ requirements.txt not found!")
        return False

def create_env_file():
    """Create .env file from template."""
    print("🔧 Setting up environment variables...")
    
    env_template = Path("env_template.txt")
    env_file = Path(".env")
    
    if env_file.exists():
        response = input("   .env file already exists. Overwrite? (y/N): ").lower().strip()
        if response not in ['y', 'yes']:
            print("   Skipping .env file creation")
            return True
    
    if env_template.exists():
        try:
            with open(env_template, 'r') as f:
                template_content = f.read()
            
            with open(env_file, 'w') as f:
                f.write(template_content)
            
            print("✅ .env file created from template")
            print("   ⚠️  Remember to add your actual API keys!")
            return True
            
        except Exception as e:
            print(f"❌ Failed to create .env file: {e}")
            return False
    else:
        print("⚠️  env_template.txt not found, creating basic .env file")
        try:
            basic_env = """# LangGraph Code Generation System Environment Variables
# Add your actual API keys here

# Required: Your Google Gemini API key
GEMINI_API_KEY=your_gemini_api_key_here

# Optional: Specify Gemini model (default: gemini-pro)
MODEL=gemini-pro

# Optional: Additional configuration
DEBUG=false
LOG_LEVEL=INFO
"""
            with open(env_file, 'w') as f:
                f.write(basic_env)
            
            print("✅ Basic .env file created")
            print("   ⚠️  Remember to add your actual API keys!")
            return True
            
        except Exception as e:
            print(f"❌ Failed to create .env file: {e}")
            return False

def create_sample_component_file():
    """Create a sample component descriptions file."""
    print("📝 Creating sample component file...")
    
    component_file = Path("component_descriptions.txt")
    
    if component_file.exists():
        response = input("   component_descriptions.txt already exists. Overwrite? (y/N): ").lower().strip()
        if response not in ['y', 'yes']:
            print("   Skipping component file creation")
            return True
    
    try:
        sample_components = """## Component: homepage-hero-section
- description: A hero section for the homepage with a brief introduction to the healthcare application, a large inviting headline, and a primary call to action button like 'Book an Appointment' and a secondary 'Learn More' button. Incorporate the black, orange, and white color theme.

## Component: global-navbar
- description: A responsive navigation bar for easy access to all pages: Homepage, About Us, Services, Appointment Booking, Patient Login, Doctor Login, Contact Us. Use the black, orange, and white color theme.

## Component: global-footer
- description: A footer for the webpage with contact details (placeholder), copyright information, and placeholder icons for social media links. Ensure it's responsive and uses the black, orange, and white color theme.

## Component: homepage-feature-display
- description: A section for the homepage displaying key features of the healthcare application in a visually appealing box format. Each box should have an icon placeholder, a title, and a brief description. Ensure it's responsive and uses the black, orange, and white color theme.
"""
        
        with open(component_file, 'w') as f:
            f.write(sample_components)
        
        print("✅ Sample component_descriptions.txt created")
        print("   📝 Edit this file to customize your components")
        return True
        
    except Exception as e:
        print(f"❌ Failed to create component file: {e}")
        return False

def test_imports():
    """Test if all required packages can be imported."""
    print("🧪 Testing imports...")
    
    required_packages = [
        'langgraph',
        'langchain_core',
        'langchain_google_genai',
        'beautifulsoup4',
        'dotenv'
    ]
    
    failed_imports = []
    
    for package in required_packages:
        try:
            if package == 'beautifulsoup4':
                import bs4
            elif package == 'dotenv':
                import dotenv
            else:
                __import__(package)
            print(f"   ✅ {package}")
        except ImportError:
            print(f"   ❌ {package}")
            failed_imports.append(package)
    
    if failed_imports:
        print(f"❌ Failed to import: {', '.join(failed_imports)}")
        return False
    else:
        print("✅ All imports successful")
        return True

def run_basic_test():
    """Run a basic functionality test."""
    print("🧪 Running basic functionality test...")
    
    try:
        # Test component parsing
        from main import parse_component_file, Component
        
        # Create a test component file
        test_content = """## Component: test-component
- description: A simple test component for validation purposes."""
        
        with open("test_components.txt", "w") as f:
            f.write(test_content)
        
        # Test parsing
        components = parse_component_file("test_components.txt")
        
        if components and len(components) == 1:
            print("   ✅ Component parsing test passed")
            
            # Clean up test file
            os.remove("test_components.txt")
            return True
        else:
            print("   ❌ Component parsing test failed")
            return False
            
    except Exception as e:
        print(f"   ❌ Functionality test failed: {e}")
        return False

def print_next_steps():
    """Print next steps for the user."""
    print("\n" + "=" * 60)
    print("🎉 Setup Complete!")
    print("=" * 60)
    
    print("\n📋 Next Steps:")
    print("1. Add your Gemini API key to the .env file")
    print("2. Customize component_descriptions.txt with your components")
    print("3. Run the system: python main.py")
    print("4. View results in the dist/ folder")
    
    print("\n🔑 Getting Gemini API Key:")
    print("   • Visit: https://makersuite.google.com/app/apikey")
    print("   • Create a new API key")
    print("   • Add it to your .env file")
    
    print("\n📚 Documentation:")
    print("   • README.md - Complete usage guide")
    print("   • main.py - Code comments and examples")
    
    print("\n🚀 Ready to generate some code!")

def main():
    """Main setup function."""
    print_header()
    
    # Check prerequisites
    if not check_python_version():
        return
    
    if not check_virtual_environment():
        return
    
    # Create virtual environment if requested
    venv_name = create_virtual_environment()
    
    # Install dependencies
    if not install_dependencies():
        print("❌ Setup failed at dependency installation")
        return
    
    # Create configuration files
    if not create_env_file():
        print("❌ Setup failed at environment file creation")
        return
    
    if not create_sample_component_file():
        print("❌ Setup failed at component file creation")
        return
    
    # Test functionality
    if not test_imports():
        print("❌ Setup failed at import testing")
        return
    
    if not run_basic_test():
        print("❌ Setup failed at functionality testing")
        return
    
    # Success
    print_next_steps()

if __name__ == "__main__":
    main()
