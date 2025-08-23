import os
import re
import sys
import json
from typing import List, TypedDict, Dict, Optional
from pathlib import Path
from dataclasses import dataclass
from langgraph.graph import StateGraph, END
from dotenv import load_dotenv
import time
from bs4 import BeautifulSoup
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.output_parsers import StrOutputParser
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# --- 1. Data Models ---

@dataclass
class Component:
    """Represents a single component with its metadata and generated code."""
    name: str
    description: str
    html: str = ""
    css: str = ""
    js: str = ""
    filename_base: str = ""
    
    def __post_init__(self):
        if not self.filename_base:
            self.filename_base = self.name.replace(' ', '-').lower()

@dataclass
class GenerationResult:
    """Result of code generation for a component."""
    success: bool
    component: Optional[Component] = None
    error_message: str = ""
    retry_count: int = 0

class GraphState(TypedDict):
    """State for the LangGraph workflow."""
    components: List[Component]
    generated_components: List[Component]
    processed_count: int
    errors: List[str]
    current_component: Optional[Component]

# --- 2. Configuration and Constants ---

class Config:
    """Configuration constants for the code generation system."""
    
    # File paths
    OUTPUT_DIR = Path("output")
    COMPONENTS_DIR = OUTPUT_DIR / "components"
    DIST_DIR = Path("dist")
    
    # LLM settings
    MAX_RETRIES = 3
    RETRY_DELAY = 2
    TEMPERATURE = 0.1
    
    # Color themes
    DEFAULT_THEME = {
        "primary": "#000000",      # Black
        "secondary": "#FF6B35",    # Orange
        "accent": "#FFFFFF",       # White
        "text": "#333333",         # Dark gray
        "background": "#FFFFFF"    # White
    }
    
    # Page structure mapping
    PAGE_STRUCTURE = {
        "index.html": ["global-navbar", "homepage-hero-section", "homepage-feature-display", "global-footer"],
        "about-us.html": ["global-navbar", "about-us-page-content", "global-footer"],
        "services.html": ["global-navbar", "services-page-content", "global-footer"],
        "appointment-booking.html": ["global-navbar", "appointment-booking-form", "global-footer"],
        "patient-login.html": ["global-navbar", "patient-login-ui", "global-footer"],
        "doctor-login.html": ["global-navbar", "doctor-login-ui", "global-footer"],
        "contact-us.html": ["global-navbar", "contact-us-page-content", "global-footer"],
    }
    
    # Navigation URL mapping
    NAV_URL_MAP = {
        "homepage": "index.html",
        "about us": "about-us.html",
        "services": "services.html",
        "appointment booking": "appointment-booking.html",
        "patient login": "patient-login.html",
        "doctor login": "doctor-login.html",
        "contact us": "contact-us.html",
        "book appointment": "appointment-booking.html",
        "schedule your visit today": "appointment-booking.html",
        "login": "patient-login.html",
    }

# --- 3. Utility Functions ---

def ensure_directories():
    """Create necessary directories if they don't exist."""
    Config.OUTPUT_DIR.mkdir(exist_ok=True)
    Config.COMPONENTS_DIR.mkdir(exist_ok=True)
    Config.DIST_DIR.mkdir(exist_ok=True)

def clean_filename(name: str) -> str:
    """Clean component name for use as filename."""
    return re.sub(r'[^a-zA-Z0-9\-_]', '-', name.lower()).strip('-')

def parse_component_file(filepath: str) -> List[Component]:
    """Parse the component descriptions file and return a list of Component objects."""
    components = []
    current_component = None
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                
                if line.startswith('## Component:'):
                    if current_component:
                        components.append(current_component)
                    
                    # Extract component name
                    name = line.split(':', 1)[1].strip().replace('**', '').strip()
                    current_component = Component(name=name, description="")
                    
                elif line.startswith('- description:') and current_component:
                    # Extract description
                    description = line.split(':', 1)[1].strip()
                    current_component.description = description
                    
                elif line and not line.startswith('#') and current_component and current_component.description:
                    # Append additional description lines
                    current_component.description += " " + line
        
        # Add the last component
        if current_component:
            components.append(current_component)
            
        logger.info(f"Successfully parsed {len(components)} components from {filepath}")
        return components
        
    except FileNotFoundError:
        logger.error(f"Component file '{filepath}' not found")
        return []
    except Exception as e:
        logger.error(f"Error parsing component file: {e}")
        return []

def extract_code_from_llm_output(llm_output: str) -> tuple[str, str, str]:
    """Extract HTML, CSS, and JS from LLM output."""
    html_match = re.search(r'```html\s*(.*?)\s*```', llm_output, re.DOTALL)
    
    if not html_match:
        raise ValueError("Could not find HTML code block in LLM output")
    
    combined_code = html_match.group(1).strip()
    
    # Extract CSS
    css_match = re.search(r'<style>(.*?)</style>', combined_code, re.DOTALL)
    css = css_match.group(1).strip() if css_match else ""
    
    # Extract JS
    js_match = re.search(r'<script>(.*?)</script>', combined_code, re.DOTALL)
    js = js_match.group(1).strip() if js_match else ""
    
    # Extract HTML (remove style and script tags)
    html = re.sub(r'<style>.*?</style>', '', combined_code, flags=re.DOTALL)
    html = re.sub(r'<script>.*?</script>', '', html, flags=re.DOTALL).strip()
    
    return html, css, js

def save_component_files(component: Component):
    """Save individual component files to the components directory."""
    try:
        # Save HTML
        html_file = Config.COMPONENTS_DIR / f"{component.filename_base}.html"
        with open(html_file, 'w', encoding='utf-8') as f:
            f.write(component.html)
        
        # Save CSS
        css_file = Config.COMPONENTS_DIR / f"{component.filename_base}.css"
        with open(css_file, 'w', encoding='utf-8') as f:
            f.write(component.css)
        
        # Save JS
        js_file = Config.COMPONENTS_DIR / f"{component.filename_base}.js"
        with open(js_file, 'w', encoding='utf-8') as f:
            f.write(component.js)
            
        logger.info(f"Saved component files: {component.filename_base}")
        
    except Exception as e:
        logger.error(f"Error saving component files for {component.name}: {e}")
        raise

# --- 4. LangGraph Nodes ---

def initialize_components_node(state: GraphState) -> GraphState:
    """Initialize the graph state with component descriptions."""
    components = state.get("components", [])
    
    if not components:
        raise ValueError("No components provided in initial state")
    
    logger.info(f"Initialized graph with {len(components)} components")
    
    return {
        "components": components,
        "generated_components": [],
        "processed_count": 0,
        "errors": [],
        "current_component": None
    }

def component_router_node(state: GraphState) -> Dict[str, str]:
    """Route to next node based on processing status."""
    processed_count = state["processed_count"]
    total_components = len(state["components"])
    
    if processed_count < total_components:
        logger.info(f"Routing to generate component {processed_count + 1}/{total_components}")
        return {"next_node": "generate_component_code"}
    else:
        logger.info("All components processed, routing to assembly")
        return {"next_node": "assemble_final_website"}

def generate_component_code_node(state: GraphState) -> GraphState:
    """Generate code for the next component using the LLM."""
    components = state["components"]
    generated_components = state["generated_components"]
    processed_count = state["processed_count"]
    
    if processed_count >= len(components):
        return state
    
    current_component = components[processed_count]
    logger.info(f"Generating code for component: {current_component.name}")
    
    # Check API key
    google_api_key = os.getenv("GEMINI_API_KEY")
    if not google_api_key:
        error_msg = "GEMINI_API_KEY environment variable not set"
        logger.error(error_msg)
        return {
            **state,
            "errors": state["errors"] + [error_msg],
            "processed_count": processed_count + 1
        }
    
    # Initialize LLM
    model_name = os.getenv("MODEL", "gemini-pro").split('/')[-1]
    llm = ChatGoogleGenerativeAI(
        model=model_name,
        google_api_key=google_api_key,
        temperature=Config.TEMPERATURE
    )
    
    # Create prompt
    system_prompt = """You are an expert web developer specializing in clean, semantic HTML, modern CSS, and vanilla JavaScript.

Your task is to generate self-contained web components that are:
- Responsive and mobile-friendly
- Accessible (proper ARIA labels, semantic HTML)
- Modern and clean in design
- Well-structured and maintainable

Use the specified color theme if provided (black, orange, white).
Generate complete, valid code that can be immediately used."""

    human_prompt = f"""Generate HTML, CSS, and JavaScript for this component:

Component Name: {current_component.name}
Description: {current_component.description}

Requirements:
- Generate self-contained HTML with embedded CSS and JavaScript
- Use semantic HTML5 elements
- Make it responsive
- Include proper accessibility features
- Use modern CSS (flexbox/grid, CSS variables)
- Write clean, vanilla JavaScript

Output Format:
```html
<div class="component-container">
    <style>
        /* CSS styles here */
    </style>
    
    <!-- HTML content here -->
    
    <script>
        // JavaScript functionality here
    </script>
</div>
```

Ensure all code is valid and complete."""

    prompt = ChatPromptTemplate.from_messages([
        SystemMessage(content=system_prompt),
        HumanMessage(content=human_prompt)
    ])
    
    # Generate code with retry mechanism
    for attempt in range(Config.MAX_RETRIES):
        try:
            logger.info(f"Attempt {attempt + 1}/{Config.MAX_RETRIES} for {current_component.name}")
            
            response = llm.invoke(prompt.format_messages())
            html, css, js = extract_code_from_llm_output(response.content)
            
            # Update component with generated code
            current_component.html = html
            current_component.css = css
            current_component.js = js
            
            # Save individual files
            save_component_files(current_component)
            
            # Update state
            new_generated_components = generated_components + [current_component]
            
            logger.info(f"Successfully generated code for {current_component.name}")
            
            return {
                **state,
                "generated_components": new_generated_components,
                "processed_count": processed_count + 1,
                "current_component": current_component
            }
            
        except Exception as e:
            logger.warning(f"Attempt {attempt + 1} failed for {current_component.name}: {e}")
            if attempt < Config.MAX_RETRIES - 1:
                time.sleep(Config.RETRY_DELAY)
            else:
                error_msg = f"Failed to generate code for {current_component.name} after {Config.MAX_RETRIES} attempts"
                logger.error(error_msg)
                return {
                    **state,
                    "errors": state["errors"] + [error_msg],
                    "processed_count": processed_count + 1
                }
    
    return state

def assemble_final_website_node(state: GraphState) -> GraphState:
    """Assemble the final website from generated components."""
    logger.info("Starting final website assembly")
    
    generated_components = state["generated_components"]
    
    # Create component lookup map
    component_map = {comp.filename_base: comp for comp in generated_components}
    
    # Combine all CSS and JS
    combined_css = "\n\n/* Component: {} */\n{}".format(
        "\n/* Component: */\n".join([f"{comp.name}" for comp in generated_components]),
        "\n\n".join([comp.css for comp in generated_components])
    )
    
    combined_js = "\n\n// Component: {}\n{}".format(
        "\n// Component: ".join([f"{comp.name}" for comp in generated_components]),
        "\n\n".join([comp.js for comp in generated_components])
    )
    
    # Save global CSS and JS
    with open(Config.DIST_DIR / "style.css", 'w', encoding='utf-8') as f:
        f.write(combined_css)
    
    with open(Config.DIST_DIR / "script.js", 'w', encoding='utf-8') as f:
        f.write(combined_js)
    
    # Generate HTML pages
    for page_filename, component_names in Config.PAGE_STRUCTURE.items():
        page_components = []
        
        for comp_name in component_names:
            component = component_map.get(comp_name)
            if component:
                page_components.append(component.html)
            else:
                logger.warning(f"Component '{comp_name}' not found for page '{page_filename}'")
        
        if page_components:
            # Combine components
            page_body = "\n".join(page_components)
            
            # Update navigation links
            soup = BeautifulSoup(page_body, 'html.parser')
            update_navigation_links(soup)
            
            # Generate full page HTML
            full_page = generate_page_html(page_filename, str(soup))
            
            # Save page
            page_path = Config.DIST_DIR / page_filename
            with open(page_path, 'w', encoding='utf-8') as f:
                f.write(full_page)
            
            logger.info(f"Generated page: {page_filename}")
    
    logger.info("Website assembly complete")
    return state

def update_navigation_links(soup: BeautifulSoup):
    """Update navigation links in the HTML."""
    # Update anchor tags
    for a_tag in soup.find_all('a', href=True):
        link_text = a_tag.get_text(strip=True).lower()
        if link_text in Config.NAV_URL_MAP:
            a_tag['href'] = Config.NAV_URL_MAP[link_text]
    
    # Update button navigation
    for button in soup.find_all('button'):
        button_text = button.get_text(strip=True).lower()
        if button_text in Config.NAV_URL_MAP:
            button['onclick'] = f"window.location.href='{Config.NAV_URL_MAP[button_text]}';"

def generate_page_html(page_filename: str, body_content: str) -> str:
    """Generate complete HTML page with proper structure."""
    page_title = page_filename.replace('.html', '').replace('-', ' ').title()
    
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="description" content="{page_title} - Healthcare Application">
    <title>{page_title} - Healthcare App</title>
    <link rel="stylesheet" href="style.css">
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
</head>
<body>
{body_content}
    <script src="script.js"></script>
</body>
</html>"""

# --- 5. Build and Run LangGraph ---

def build_graph() -> StateGraph:
    """Build the LangGraph workflow."""
    builder = StateGraph(GraphState)
    
    # Add nodes
    builder.add_node("initialize_components", initialize_components_node)
    builder.add_node("component_router", component_router_node)
    builder.add_node("generate_component_code", generate_component_code_node)
    builder.add_node("assemble_final_website", assemble_final_website_node)
    
    # Set entry point
    builder.set_entry_point("initialize_components")
    
    # Add edges
    builder.add_edge("initialize_components", "component_router")
    builder.add_edge("generate_component_code", "component_router")
    builder.add_edge("assemble_final_website", END)
    
    # Add conditional edges
    builder.add_conditional_edges(
        "component_router",
        lambda state: state["next_node"],
        {
            "generate_component_code": "generate_component_code",
            "assemble_final_website": "assemble_final_website"
        }
    )
    
    return builder.compile()

def main():
    """Main execution function."""
    # Load environment variables
    load_dotenv()
    
    # Ensure directories exist
    ensure_directories()
    
    # Parse component file
    component_file = "component_descriptions.txt"
    components = parse_component_file(component_file)
    
    if not components:
        logger.error("No components found. Please check your component file.")
        return
    
    # Build and run graph
    app = build_graph()
    
    initial_state = {
        "components": components,
        "generated_components": [],
        "processed_count": 0,
        "errors": [],
        "current_component": None
    }
    
    logger.info("Starting LangGraph code generation process...")
    
    try:
        # Stream the execution
        for step in app.stream(initial_state):
            if isinstance(step, dict) and all(value == {} for value in step.values()):
                continue
            logger.info(f"Step: {step}")
        
        logger.info("Code generation process completed successfully!")
        
        # Display results
        display_results()
        
    except Exception as e:
        logger.error(f"Error during code generation: {e}")
        sys.exit(1)

def display_results():
    """Display the results of the code generation process."""
    print("\n" + "="*60)
    print("🎉 CODE GENERATION COMPLETE!")
    print("="*60)
    
    # Check dist directory
    if Config.DIST_DIR.exists():
        print(f"\n📁 Your website is ready in: {Config.DIST_DIR.absolute()}")
        print("\n🌐 TO VIEW YOUR WEBSITE:")
        print("1. Open terminal and navigate to the dist folder:")
        print(f"   cd {Config.DIST_DIR.absolute()}")
        print("2. Start a local server:")
        print("   python -m http.server 8000")
        print("3. Open your browser and go to: http://localhost:8000")
        
        print("\n📄 Generated Pages:")
        for page_file in Config.DIST_DIR.glob("*.html"):
            print(f"   • {page_file.name}")
            
        print("\n🎨 Generated Assets:")
        print(f"   • style.css - Combined CSS")
        print(f"   • script.js - Combined JavaScript")
        
    else:
        print("❌ Website assembly failed - dist directory not created")
    
    # Check components directory
    if Config.COMPONENTS_DIR.exists():
        print(f"\n🔧 Individual component files saved in: {Config.COMPONENTS_DIR.absolute()}")
        component_files = list(Config.COMPONENTS_DIR.glob("*"))
        print(f"   Total files: {len(component_files)}")
    
    print("\n" + "="*60)

if __name__ == "__main__":
    main()
