import os
import json
from dotenv import load_dotenv, set_key
from pathlib import Path
from .version import __version__  # Import version from central location

class Config:
    def __init__(self):
        self.VERSION = __version__  # Use imported version
        self.CYAN = "\033[96m"
        self.YELLOW = "\033[93m"
        self.BOLD = "\033[1m"
        self.RESET = "\033[0m"
        self.RED = "\033[31m"
        self.GREEN = "\033[32m"
        self.SMALL_FONT = "\033[0;2m"  # Smaller font (dim)

        # Project config files
        self.project_root = Path(__file__).parent.parent
        self.mcp_settings_file = self.project_root / "cli_FSD" / "config_files" / "mcp_settings.json"

        # User config files
        self.config_dir = os.path.expanduser("~/.config/cli-FSD")
        self.config_file = os.path.join(self.config_dir, "config.json")
        self.preferences_file = os.path.join(self.config_dir, "preferences.json")
        
        # Create config directory if it doesn't exist
        os.makedirs(self.config_dir, exist_ok=True)

        self.current_model = os.getenv("DEFAULT_MODEL", "gpt-4o")
        self.api_key = os.getenv("OPENAI_API_KEY")
        self.server_port = int(os.getenv("SERVER_PORT", 5000))
        
        # Sequential Thinking settings
        self.sequential_thinking_enabled = False
        self.sequential_thinking_llm_choice = False
        
        # Load preferences
        self.load_preferences()
        self.load_mcp_settings()

        # Models dictionary with latest text-only models
        self.models = {
            # GPT-4o Models
            "gpt-4o": "gpt-4o",
            "gpt-4o-mini": "gpt-4o-mini",
            "gpt-4.1": "gpt-4.1",
            "gpt-4.1-mini": "gpt-4.1-mini",
            "gpt-4.1-nano": "gpt-4.1-nano",

            # Reasoning Models
            "o1": "o1",
            "o1-mini": "o1-mini",
            "o1-preview": "o1-preview",
            "o3": "o3",
            "o4-mini": "o4-mini",
            
            # Legacy GPT-4 Models
            "gpt-4-turbo": "gpt-4-turbo",
            "gpt-4": "gpt-4",
            "gpt-4-0613": "gpt-4-0613",
            
            # Claude Models
            "claude-3-opus": "claude-3-opus-20240229",
            "claude-3-sonnet": "claude-3-sonnet-20240229",
            "claude-3-haiku": "claude-3-haiku-20240307",
            "claude-3.5-sonnet": "claude-3-5-sonnet-latest",
            "claude-3-7-sonnet": "claude-3-7-sonnet-latest"
                  }
        
    def load_preferences(self):
        """Load preferences from file or set defaults"""
        try:
            if os.path.exists(self.preferences_file):
                with open(self.preferences_file, 'r') as f:
                    prefs = json.load(f)
                    self.session_model = prefs.get('model')
                    self.safe_mode = prefs.get('safe_mode', False)
                    self.autopilot_mode = prefs.get('autopilot_mode', False)
                    self.use_claude = prefs.get('use_claude', False)
                    self.use_ollama = prefs.get('use_ollama', False)
                    self.use_groq = prefs.get('use_groq', False)
                    self.scriptreviewer_on = prefs.get('scriptreviewer_on', False)
                    self.last_ollama_model = prefs.get('last_ollama_model', 'llama3.1:8b')
                    self.ollama_endpoint = prefs.get('ollama_endpoint', 'http://localhost:11434')
                    
                    # Load sequential thinking preferences
                    self.sequential_thinking_enabled = prefs.get('sequential_thinking_enabled', False)
                    self.sequential_thinking_llm_choice = prefs.get('sequential_thinking_llm_choice', False)
                    
                    # Load formatting preferences
                    self.enhanced_formatting = prefs.get('enhanced_formatting', True)  # Default to enhanced
            else:
                self.session_model = None
                self.safe_mode = False
                self.autopilot_mode = False
                self.use_claude = False
                self.use_ollama = False
                self.use_groq = False
                self.scriptreviewer_on = False
                self.last_ollama_model = 'llama3.1:8b'  # Default Ollama model
                self.ollama_endpoint = 'http://localhost:11434'  # Default endpoint
                self.enhanced_formatting = True  # Default to enhanced formatting
        except Exception as e:
            print(f"Error loading preferences: {e}")
            # Use defaults if loading fails
            self.session_model = None
            self.safe_mode = False
            self.autopilot_mode = False
            self.use_claude = False
            self.use_ollama = False
            self.use_groq = False
            self.scriptreviewer_on = False
        
        # These don't persist between sessions
        self.llm_suggestions = None
        self.last_response = None

    def save_preferences(self):
        """Save current preferences to file"""
        try:
            prefs = {
                'model': self.session_model,
                'safe_mode': self.safe_mode,
                'autopilot_mode': self.autopilot_mode,
                'use_claude': self.use_claude,
                'use_ollama': self.use_ollama,
                'use_groq': self.use_groq,
                'scriptreviewer_on': self.scriptreviewer_on,
                'last_ollama_model': self.last_ollama_model,
                'ollama_endpoint': self.ollama_endpoint,
                'sequential_thinking_enabled': self.sequential_thinking_enabled,
                'sequential_thinking_llm_choice': self.sequential_thinking_llm_choice,
                'enhanced_formatting': self.enhanced_formatting
            }
            with open(self.preferences_file, 'w') as f:
                json.dump(prefs, f, indent=2)
        except Exception as e:
            print(f"Error saving preferences: {e}")

    def load_mcp_settings(self):
        """Load MCP server settings from project config"""
        try:
            if self.mcp_settings_file.exists():
                with open(self.mcp_settings_file) as f:
                    self.mcp_settings = json.load(f)
            else:
                print(f"{self.RED}Warning: MCP settings file not found at {self.mcp_settings_file}{self.RESET}")
                self.mcp_settings = {"mcpServers": {}}
        except Exception as e:
            print(f"{self.RED}Error loading MCP settings: {e}{self.RESET}")
            self.mcp_settings = {"mcpServers": {}}

def initialize_config(args):
    config = Config()
    
    # Handle default flag first
    if args.default:
        config.session_model = None
        config.use_ollama = False
        config.use_claude = False
        config.use_groq = False
        config.autopilot_mode = False
        config.scriptreviewer_on = False
        config.safe_mode = False
    else:
        # Update config with command line args
        if args.safe:
            config.safe_mode = args.safe
        if args.autopilot:
            config.autopilot_mode = args.autopilot
        if args.claude:
            config.session_model = "claude"
            config.use_claude = True
            config.use_ollama = False
            config.use_groq = False
        if args.ollama:
            config.session_model = "ollama"
            config.use_ollama = True
            config.use_claude = False
            config.use_groq = False
            config.current_model = config.last_ollama_model
        if args.groq:
            config.session_model = "groq"
            config.use_groq = True
            config.use_claude = False
            config.use_ollama = False
        if args.assistantsAPI:
            config.scriptreviewer_on = True
    
    # Save any changes from command line args
    config.save_preferences()
    
    return config
