#!/bin/bash

# Trial Transcription System - Virtual Environment Setup Script
# This script creates and configures a virtual environment for the project

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to check Python version
check_python_version() {
    print_status "Checking Python version..."
    
    if ! command_exists python3; then
        print_error "Python 3 is not installed or not in PATH"
        print_error "Please install Python 3.8 or higher"
        exit 1
    fi
    
    python_version=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
    python_major=$(python3 -c "import sys; print(sys.version_info.major)")
    python_minor=$(python3 -c "import sys; print(sys.version_info.minor)")
    
    if [ "$python_major" -lt 3 ] || ([ "$python_major" -eq 3 ] && [ "$python_minor" -lt 8 ]); then
        print_error "Python 3.8 or higher is required"
        print_error "Current version: $python_version"
        exit 1
    fi
    
    print_success "Python $python_version detected"
}

# Function to create virtual environment
create_venv() {
    local venv_name=${1:-"venv"}
    
    print_status "Creating virtual environment: $venv_name"
    
    if [ -d "$venv_name" ]; then
        print_warning "Virtual environment '$venv_name' already exists"
        read -p "Do you want to recreate it? (y/N): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            print_status "Removing existing virtual environment..."
            rm -rf "$venv_name"
        else
            print_status "Using existing virtual environment"
            return 0
        fi
    fi
    
    if python3 -m venv "$venv_name"; then
        print_success "Virtual environment '$venv_name' created successfully"
    else
        print_error "Failed to create virtual environment"
        exit 1
    fi
}

# Function to activate virtual environment
activate_venv() {
    local venv_name=${1:-"venv"}
    
    print_status "Activating virtual environment..."
    
    if [ -f "$venv_name/bin/activate" ]; then
        source "$venv_name/bin/activate"
        print_success "Virtual environment activated"
        
        # Update pip
        print_status "Upgrading pip..."
        pip install --upgrade pip
        
        # Install dependencies
        if [ -f "requirements.txt" ]; then
            print_status "Installing dependencies from requirements.txt..."
            pip install -r requirements.txt
            print_success "Dependencies installed successfully"
        else
            print_warning "requirements.txt not found, skipping dependency installation"
        fi
        
        # Test imports
        print_status "Testing imports..."
        if python3 -c "import openai, dotenv, langchain, langchain_openai" 2>/dev/null; then
            print_success "All required packages imported successfully"
        else
            print_warning "Some packages failed to import"
            print_warning "You may need to install dependencies manually"
        fi
        
    else
        print_error "Virtual environment activation script not found"
        exit 1
    fi
}

# Function to create .env file
create_env_file() {
    print_status "Setting up environment variables..."
    
    if [ -f ".env" ]; then
        print_warning ".env file already exists"
        read -p "Do you want to overwrite it? (y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            print_status "Keeping existing .env file"
            return 0
        fi
    fi
    
    # Create .env file
    cat > .env << 'EOF'
# Trial Transcription System Environment Variables
# Add your actual API keys here

# Required: Your OpenAI API key
# Get one from: https://platform.openai.com/api-keys
OPENAI_API_KEY=your_openai_api_key_here

# Optional: Additional configuration
DEBUG=false
LOG_LEVEL=INFO
EOF
    
    print_success ".env file created"
    print_warning "Remember to add your actual OpenAI API key!"
}

# Function to test the system
test_system() {
    print_status "Testing the transcription system..."
    
    # Check if sample files exist
    if [ -f "sample.wav" ]; then
        print_success "Sample audio file found"
    else
        print_warning "Sample audio file not found (optional)"
    fi
    
    if [ -f "sample_transcript.txt" ]; then
        print_success "Sample transcript found"
    else
        print_warning "Sample transcript not found (optional)"
    fi
    
    # Test if main script can be imported
    if python3 -c "from transcribe_and_summarize import transcribe_with_whisper, summarize_with_nano" 2>/dev/null; then
        print_success "Main functions imported successfully"
    else
        print_warning "Could not import main functions (check dependencies)"
    fi
}

# Function to display next steps
show_next_steps() {
    local venv_name=${1:-"venv"}
    
    echo
    echo "============================================================"
    echo "🎉 Virtual Environment Setup Complete!"
    echo "============================================================"
    echo
    echo "📋 Next Steps:"
    echo "1. Activate the virtual environment:"
    echo "   source $venv_name/bin/activate"
    echo
    echo "2. Add your OpenAI API key to the .env file"
    echo "   • Visit: https://platform.openai.com/api-keys"
    echo "   • Create a new API key"
    echo "   • Edit .env file and replace 'your_openai_api_key_here'"
    echo
    echo "3. Test the system:"
    echo "   python transcribe_and_summarize.py"
    echo
    echo "4. Try your own audio files by modifying AUDIO_PATH in the script"
    echo
    echo "🎵 Ready to transcribe some audio!"
    echo
    echo "💡 Tip: You can also run 'python setup.py' for automated setup"
}

# Main function
main() {
    echo "============================================================"
    echo "🎵 Trial Transcription System - Virtual Environment Setup"
    echo "============================================================"
    echo
    
    # Check Python version
    check_python_version
    
    # Get virtual environment name
    read -p "Enter virtual environment name (default: venv): " venv_name
    venv_name=${venv_name:-"venv"}
    
    # Create virtual environment
    create_venv "$venv_name"
    
    # Create configuration files
    create_env_file
    
    # Activate and configure virtual environment
    activate_venv "$venv_name"
    
    # Test the system
    test_system
    
    # Show next steps
    show_next_steps "$venv_name"
}

# Check if script is being sourced or executed
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    # Script is being executed
    main "$@"
else
    # Script is being sourced
    print_status "Script sourced. Run 'main' to start setup."
fi
