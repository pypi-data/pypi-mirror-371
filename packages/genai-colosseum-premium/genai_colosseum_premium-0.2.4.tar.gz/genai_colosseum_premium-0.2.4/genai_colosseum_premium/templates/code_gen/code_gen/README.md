# 🚀 LangGraph Code Generation System

A powerful, automated web development system that uses LangGraph and Google's Gemini AI to generate complete websites from component descriptions.

## ✨ Features

- **Automated Code Generation**: Generate HTML, CSS, and JavaScript for web components using AI
- **LangGraph Workflow**: Robust, stateful processing with error handling and retry mechanisms
- **Component-Based Architecture**: Modular design for easy maintenance and extension
- **Smart Navigation**: Automatic link generation and routing between pages
- **Responsive Design**: AI-generated components follow modern web standards
- **File Organization**: Clean output structure with separate component files and assembled website

## 🏗️ Architecture

The system uses a **4-node LangGraph workflow**:

1. **Initialize Components** → Parse component descriptions
2. **Component Router** → Determine next action (generate or assemble)
3. **Generate Component Code** → Use Gemini AI to create HTML/CSS/JS
4. **Assemble Final Website** → Combine components into complete pages

## 📁 Project Structure

```
langraph/code_gen/
├── main.py                 # Main application file
├── requirements.txt        # Python dependencies
├── README.md              # This file
├── setup.py               # Setup script
├── create_venv.sh         # Virtual environment script
├── env_template.txt       # Environment variables template
├── component_descriptions.txt  # Your component specifications
├── output/                # Generated component files
│   └── components/        # Individual HTML/CSS/JS files
└── dist/                  # Final assembled website
    ├── index.html
    ├── about-us.html
    ├── services.html
    ├── style.css
    └── script.js
```

## 🚀 Quick Start

### 1. Setup Environment

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure API Keys

Create a `.env` file:

```bash
cp env_template.txt .env
# Edit .env with your actual API keys
```

Required environment variables:
- `GEMINI_API_KEY`: Your Google Gemini API key
- `MODEL`: Gemini model name (default: gemini-pro)

### 3. Define Components

Create a `component_descriptions.txt` file with your component specifications:

```txt
## Component: homepage-hero-section
- description: A hero section with headline, description, and call-to-action buttons

## Component: global-navbar
- description: Navigation bar with links to all pages
```

### 4. Generate Website

```bash
python main.py
```

### 5. View Results

```bash
cd dist
python -m http.server 8000
# Open http://localhost:8000 in your browser
```

## 🔧 Configuration

### Component File Format

The system expects components in this format:

```txt
## Component: component-name
- description: Detailed description of what this component should do

## Component: another-component
- description: Another component description
```

### Page Structure

Pages are automatically generated based on the `PAGE_STRUCTURE` configuration in `main.py`:

```python
PAGE_STRUCTURE = {
    "index.html": ["global-navbar", "homepage-hero-section", "global-footer"],
    "about-us.html": ["global-navbar", "about-us-content", "global-footer"],
    # ... more pages
}
```

### Navigation Mapping

Automatic link generation based on text content:

```python
NAV_URL_MAP = {
    "homepage": "index.html",
    "about us": "about-us.html",
    "book appointment": "appointment-booking.html",
    # ... more mappings
}
```

## 🎨 Customization

### Color Themes

Modify the `DEFAULT_THEME` in the `Config` class:

```python
DEFAULT_THEME = {
    "primary": "#000000",      # Black
    "secondary": "#FF6B35",    # Orange
    "accent": "#FFFFFF",       # White
    "text": "#333333",         # Dark gray
    "background": "#FFFFFF"    # White
}
```

### LLM Settings

Adjust AI generation parameters:

```python
MAX_RETRIES = 3          # Retry attempts for failed generations
RETRY_DELAY = 2          # Seconds between retries
TEMPERATURE = 0.1        # AI creativity level (0.0 = focused, 1.0 = creative)
```

### Output Directories

Customize file paths:

```python
OUTPUT_DIR = Path("output")           # Component files
COMPONENTS_DIR = OUTPUT_DIR / "components"  # Individual files
DIST_DIR = Path("dist")               # Final website
```

## 📝 Component Examples

### Hero Section
```txt
## Component: homepage-hero-section
- description: A hero section for the homepage with a brief introduction to the healthcare application, a large inviting headline, and a primary call to action button like 'Book an Appointment' and a secondary 'Learn More' button. Incorporate the black, orange, and white color theme.
```

### Navigation Bar
```txt
## Component: global-navbar
- description: A responsive navigation bar for easy access to all pages: Homepage, About Us, Services, Appointment Booking, Patient Login, Doctor Login, Contact Us. Use the black, orange, and white color theme.
```

### Form Component
```txt
## Component: appointment-booking-form
- description: An online form for booking appointments. Include fields for patient details, a calendar view for selecting available appointment slots (frontend UI only, no backend integration), and a submit button.
```

## 🐛 Troubleshooting

### Common Issues

1. **API Key Error**
   ```
   Error: GEMINI_API_KEY environment variable not set
   ```
   **Solution**: Check your `.env` file and ensure the API key is correct.

2. **Component Parsing Error**
   ```
   No components found. Please check your component file.
   ```
   **Solution**: Verify your `component_descriptions.txt` format matches the expected structure.

3. **Generation Failures**
   ```
   Failed to generate code for component after 3 attempts
   ```
   **Solution**: Check your internet connection and API key validity. The system will continue with other components.

### Debug Mode

Enable detailed logging by modifying the logging level in `main.py`:

```python
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
```

## 🔄 Workflow Details

### 1. Component Parsing
- Reads `component_descriptions.txt`
- Extracts component names and descriptions
- Creates `Component` objects with metadata

### 2. Code Generation
- Iterates through each component
- Sends description to Gemini AI
- Extracts HTML, CSS, and JavaScript
- Saves individual component files

### 3. Website Assembly
- Combines all CSS into `style.css`
- Combines all JavaScript into `script.js`
- Creates HTML pages with proper structure
- Updates navigation links automatically

### 4. Output Generation
- `output/components/`: Individual component files
- `dist/`: Complete website ready for deployment

## 🚀 Advanced Usage

### Custom Prompts

Modify the AI prompts in `generate_component_code_node()`:

```python
system_prompt = """Your custom system prompt here"""
human_prompt = f"""Your custom human prompt here: {current_component.description}"""
```

### Additional Page Types

Add new pages to `PAGE_STRUCTURE`:

```python
PAGE_STRUCTURE = {
    # ... existing pages
    "new-page.html": ["global-navbar", "new-component", "global-footer"],
}
```

### Custom Navigation

Extend `NAV_URL_MAP` for additional link mappings:

```python
NAV_URL_MAP = {
    # ... existing mappings
    "custom link": "custom-page.html",
}
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is open source and available under the MIT License.

## 🆘 Support

If you encounter issues:

1. Check the troubleshooting section
2. Review the logs for error messages
3. Verify your component file format
4. Ensure all dependencies are installed
5. Check your API key configuration

---

**Happy coding! 🎉**
