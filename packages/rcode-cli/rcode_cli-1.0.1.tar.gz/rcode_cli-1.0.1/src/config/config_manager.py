"""
R-Code Configuration Manager
===========================

Manages R-Code configuration including models, MCP servers, and user rules.
Automatically creates and maintains .rcode configuration directory.
"""

import os
import json
from pathlib import Path
from typing import Dict, Any, List, Optional
import shutil


class RCodeConfigManager:
    """Manages R-Code configuration files and settings"""
    
    def __init__(self, config_dir: str = ".rcode"):
        """
        Initialize configuration manager
        
        Args:
            config_dir: Configuration directory name (default: .rcode)
        """
        self.config_dir = Path.cwd() / config_dir
        self.config_file = self.config_dir / "config.json"
        self.mcp_servers_file = self.config_dir / "mcp-servers.json"
        self.rules_file = self.config_dir / "rules.md"
        
        # Ensure configuration directory exists
        self.setup_config_directory()
    
    def setup_config_directory(self):
        """Create .rcode directory and default configuration files"""
        # Create .rcode directory
        self.config_dir.mkdir(exist_ok=True)
        
        # Automatically add .rcode/ to .gitignore for security
        self._ensure_gitignore_protection()
        
        # Create default config.json if it doesn't exist
        if not self.config_file.exists():
            self._create_default_config()
        
        # Create default mcp-servers.json if it doesn't exist
        if not self.mcp_servers_file.exists():
            self._create_default_mcp_config()
        
        # Create default rules.md if it doesn't exist
        if not self.rules_file.exists():
            self._create_default_rules()
    
    def _create_default_config(self):
        """Create default configuration file"""
        default_config = {
            "version": "1.0.0",
            "models": {
                "primary": "claude",
                "fallback": "openai",
                "available": {
                    "claude": {
                        "name": "anthropic:claude-3-5-sonnet-20241022",
                        "temperature": 0.1,
                        "max_tokens": 4000,
                        "api_key_env": "ANTHROPIC_API_KEY",
                        "enabled": True
                    },
                    "openai": {
                        "name": "openai:gpt-4-turbo-preview",
                        "temperature": 0.1,  
                        "max_tokens": 4000,
                        "api_key_env": "OPENAI_API_KEY",
                        "enabled": True
                    },
                    "gemini": {
                        "name": "google:gemini-1.5-pro",
                        "temperature": 0.1,
                        "max_tokens": 4000,
                        "api_key_env": "GOOGLE_API_KEY",
                        "enabled": False
                    }
                }
            },
            "tools": {
                "web_search": {
                    "enabled": True,
                    "api_key_env": "TAVILY_API_KEY"
                },
                "file_operations": {
                    "enabled": True,
                    "live_coding": True,
                    "vscode_integration": True
                },
                "terminal_operations": {
                    "enabled": True,
                    "human_approval_required": True,
                    "auto_approve_safe_commands": False,
                    "allowed_directories": ["."],
                    "restricted_directories": [],
                    "safe_commands": [
                        "ls", "dir", "pwd", "whoami", "echo", "cat", "head", "tail",
                        "grep", "find", "which", "where", "type", "help", "--help",
                        "git status", "git log", "git diff", "git branch", "npm list",
                        "pip list", "python --version", "node --version", "npm --version"
                    ],
                    "dangerous_commands": [
                        "rm", "del", "rmdir", "rd", "format", "fdisk", "dd",
                        "shutdown", "reboot", "halt", "poweroff", "kill", "killall",
                        "sudo", "su", "chmod", "chown", "passwd", "useradd", "userdel",
                        "curl", "wget", "ssh", "scp", "rsync", "mount", "umount"
                    ]
                }
            },
            "ui": {
                "theme": "rcode",
                "colors": {
                    "primary": "rgb(255,106,0)",
                    "secondary": "rgb(255,215,0)",
                    "success": "green",
                    "error": "red",
                    "warning": "yellow"
                },
                "streaming": {
                    "enabled": True,
                    "chunk_size": 1,
                    "delay": 0.01
                }
            },
            "advanced": {
                "memory": {
                    "persistent": True,
                    "max_messages": 100
                },
                "logging": {
                    "enabled": True,
                    "level": "INFO",
                    "file": ".rcode/logs/rcode.log"
                }
            }
        }
        
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(default_config, f, indent=2)
    
    def _create_default_mcp_config(self):
        """Create empty MCP servers configuration using Cline schema"""
        default_mcp_config = {
            "mcpServers": {}
        }
        
        with open(self.mcp_servers_file, 'w', encoding='utf-8') as f:
            json.dump(default_mcp_config, f, indent=2)
    
    def _create_default_rules(self):
        """Create default rules file"""
        default_rules = """# R-Code Custom Rules

*Generated by R-Code AI Assistant*

## Custom Instructions

Add your custom instructions and rules here. The AI will read and follow these rules during conversations.

### Code Style Preferences
- Use meaningful variable names
- Add comments for complex logic
- Follow PEP 8 for Python code
- Use TypeScript for JavaScript projects

### Project Preferences
- Create tests for new functions
- Add documentation for public APIs
- Use git for version control
- Follow semantic versioning

### AI Behavior
- Be concise but thorough in explanations
- Always show code examples when helpful
- Ask clarifying questions when requirements are unclear
- Prioritize security and best practices

### File Operations
- Always backup important files before major changes
- Use descriptive commit messages
- Organize code into logical modules
- Keep configuration files readable

## Custom Tools and Workflows

Document any custom workflows or tool preferences here.

## MCP Server Instructions

If you've added custom MCP servers, document their usage here.

---

*Edit this file to customize R-Code behavior to your preferences*
"""
        
        with open(self.rules_file, 'w', encoding='utf-8') as f:
            f.write(default_rules)
    
    def _ensure_gitignore_protection(self):
        """
        Automatically add .rcode/ directory to .gitignore for security.
        
        This prevents users from accidentally exposing sensitive configuration
        data (API keys, credentials, etc.) on GitHub or other version control.
        """
        gitignore_path = Path.cwd() / ".gitignore"
        rcode_entry = f"{self.config_dir.name}/"
        
        try:
            # Read existing .gitignore or create empty content
            if gitignore_path.exists():
                with open(gitignore_path, 'r', encoding='utf-8') as f:
                    gitignore_content = f.read()
            else:
                gitignore_content = ""
            
            # Check if .rcode/ is already protected
            lines = gitignore_content.splitlines()
            
            # Look for exact match or pattern that would cover .rcode/
            rcode_protected = any(
                line.strip() in [rcode_entry, rcode_entry.rstrip('/'), f"/{rcode_entry}", f"/{rcode_entry.rstrip('/')}"]
                for line in lines
                if line.strip() and not line.strip().startswith('#')
            )
            
            if not rcode_protected:
                # Add .rcode/ protection with security notice
                protection_block = f"""
# ====================
# R-Code Configuration Protection
# ====================
# SECURITY: Protect .rcode/ directory from version control
# Contains sensitive data: API keys, credentials, personal settings
{rcode_entry}
!{rcode_entry}config.json.example
!{rcode_entry}rules.md.example
!{rcode_entry}mcp-servers.json.example
"""
                
                # Add to gitignore
                if gitignore_content and not gitignore_content.endswith('\n'):
                    gitignore_content += '\n'
                
                gitignore_content += protection_block
                
                # Write updated .gitignore
                with open(gitignore_path, 'w', encoding='utf-8') as f:
                    f.write(gitignore_content)
                
                print(f"🔒 Automatically added {rcode_entry} to .gitignore for security")
            
        except Exception as e:
            # Don't fail if we can't update .gitignore, but warn the user
            print(f"⚠️  Could not update .gitignore: {e}")
            print(f"🔒 SECURITY WARNING: Please manually add '{rcode_entry}' to your .gitignore file")
            print("   This prevents accidental exposure of API keys and credentials on GitHub")
    
    def load_config(self) -> Dict[str, Any]:
        """Load configuration from config.json"""
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"⚠️  Error loading config: {e}")
            return {}
    
    def save_config(self, config: Dict[str, Any]):
        """Save configuration to config.json"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2)
        except Exception as e:
            print(f"❌ Error saving config: {e}")
    
    def load_mcp_servers(self) -> Dict[str, Any]:
        """Load MCP servers configuration"""
        try:
            with open(self.mcp_servers_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"⚠️  Error loading MCP servers: {e}")
            return {"servers": {}}
    
    def save_mcp_servers(self, mcp_config: Dict[str, Any]):
        """Save MCP servers configuration"""
        try:
            with open(self.mcp_servers_file, 'w', encoding='utf-8') as f:
                json.dump(mcp_config, f, indent=2)
        except Exception as e:
            print(f"❌ Error saving MCP servers: {e}")
    
    def load_rules(self) -> str:
        """Load custom rules from rules.md"""
        try:
            with open(self.rules_file, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            print(f"⚠️  Error loading rules: {e}")
            return ""
    
    def save_rules(self, rules: str):
        """Save custom rules to rules.md"""
        try:
            with open(self.rules_file, 'w', encoding='utf-8') as f:
                f.write(rules)
        except Exception as e:
            print(f"❌ Error saving rules: {e}")
    
    def get_enabled_models(self) -> Dict[str, Any]:
        """Get list of enabled models with their configurations"""
        config = self.load_config()
        models = config.get("models", {}).get("available", {})
        
        enabled_models = {}
        for model_key, model_config in models.items():
            if model_config.get("enabled", False):
                # Check if API key is available
                api_key_env = model_config.get("api_key_env")
                if api_key_env and os.getenv(api_key_env):
                    enabled_models[model_key] = model_config
        
        return enabled_models
    
    def get_enabled_mcp_servers(self) -> Dict[str, Any]:
        """Get list of enabled MCP servers using Cline schema"""
        mcp_config = self.load_mcp_servers()
        servers = mcp_config.get("mcpServers", {})
        
        # All servers in Cline schema are enabled by default
        return servers
    
    def add_mcp_server(self, key: str, name: str, transport: str, enabled: bool = True, **kwargs):
        """Add a new MCP server configuration"""
        mcp_config = self.load_mcp_servers()
        
        server_config = {
            "name": name,
            "transport": transport,
            "enabled": enabled,
            **kwargs
        }
        
        mcp_config["servers"][key] = server_config
        self.save_mcp_servers(mcp_config)
    
    def update_model_config(self, model_key: str, **updates):
        """Update configuration for a specific model"""
        config = self.load_config()
        
        if model_key in config.get("models", {}).get("available", {}):
            config["models"]["available"][model_key].update(updates)
            self.save_config(config)
        else:
            print(f"⚠️  Model '{model_key}' not found in configuration")
    
    def get_config_info(self) -> Dict[str, Any]:
        """Get overview of current configuration"""
        config = self.load_config()
        mcp_config = self.load_mcp_servers()
        
        enabled_models = list(self.get_enabled_models().keys())
        enabled_servers = list(self.get_enabled_mcp_servers().keys())
        
        return {
            "config_dir": str(self.config_dir),
            "config_version": config.get("version", "unknown"),
            "primary_model": config.get("models", {}).get("primary", "none"),
            "enabled_models": enabled_models,
            "enabled_mcp_servers": enabled_servers,
            "tools_enabled": config.get("tools", {}),
            "ui_theme": config.get("ui", {}).get("theme", "default")
        }


# Global configuration manager instance
config_manager = RCodeConfigManager()
