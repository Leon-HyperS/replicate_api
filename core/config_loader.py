"""
Configuration loader and manager
"""

import json
import yaml
from pathlib import Path
from typing import Dict, Any, List, Optional, Union
import copy


class ConfigLoader:
    """Load and manage generation configurations"""
    
    def __init__(self, config_dir: Union[str, Path] = "config/prompts"):
        """
        Initialize the config loader
        
        Args:
            config_dir: Directory containing configuration files
        """
        self.config_dir = Path(config_dir)
        self.config_dir.mkdir(parents=True, exist_ok=True)
        self._cache = {}
        self._templates = {}
        self._load_templates()
    
    def load(self, config_name: str) -> Dict[str, Any]:
        """
        Load a configuration by name
        
        Args:
            config_name: Name of the config file (without extension) or path
            
        Returns:
            Configuration dictionary
        """
        # Check cache first
        if config_name in self._cache:
            return copy.deepcopy(self._cache[config_name])
        
        # Try to find the config file
        config_path = self._find_config_file(config_name)
        
        if not config_path:
            raise FileNotFoundError(f"Configuration '{config_name}' not found")
        
        # Load the config
        config = self._load_file(config_path)
        
        # Process inheritance if specified
        if '_extends' in config:
            config = self._process_inheritance(config)
        
        # Cache and return
        self._cache[config_name] = config
        return copy.deepcopy(config)
    
    def load_all(self) -> Dict[str, Dict[str, Any]]:
        """
        Load all configurations in the config directory
        
        Returns:
            Dictionary mapping config names to configurations
        """
        configs = {}
        
        for file_path in self.config_dir.glob("*.json"):
            config_name = file_path.stem
            if not config_name.startswith("_"):  # Skip files starting with underscore
                try:
                    configs[config_name] = self.load(config_name)
                except Exception as e:
                    print(f"Warning: Failed to load {config_name}: {e}")
        
        for file_path in self.config_dir.glob("*.yaml"):
            config_name = file_path.stem
            if not config_name.startswith("_"):
                try:
                    configs[config_name] = self.load(config_name)
                except Exception as e:
                    print(f"Warning: Failed to load {config_name}: {e}")
        
        return configs
    
    def save(self, config: Dict[str, Any], name: str, format: str = "json") -> Path:
        """
        Save a configuration
        
        Args:
            config: Configuration dictionary
            name: Name for the config file
            format: File format ('json' or 'yaml')
            
        Returns:
            Path to saved file
        """
        if format == "yaml":
            file_path = self.config_dir / f"{name}.yaml"
            with open(file_path, 'w') as f:
                yaml.dump(config, f, default_flow_style=False, sort_keys=False)
        else:
            file_path = self.config_dir / f"{name}.json"
            with open(file_path, 'w') as f:
                json.dump(config, f, indent=2)
        
        # Clear cache for this config
        if name in self._cache:
            del self._cache[name]
        
        return file_path
    
    def validate(self, config: Dict[str, Any], schema: Optional[Dict[str, Any]] = None) -> bool:
        """
        Validate a configuration against a schema
        
        Args:
            config: Configuration to validate
            schema: Optional schema to validate against
            
        Returns:
            True if valid
        """
        # Basic validation - ensure required fields exist
        required_fields = ['subject', 'scene']  # Minimal requirements
        
        for field in required_fields:
            if field not in config:
                raise ValueError(f"Required field '{field}' missing from configuration")
        
        # Additional schema validation could be added here
        if schema:
            # Implement JSON schema validation
            pass
        
        return True
    
    def list_configs(self) -> List[str]:
        """
        List all available configuration names
        
        Returns:
            List of configuration names
        """
        configs = []
        
        for file_path in self.config_dir.glob("*.json"):
            if not file_path.stem.startswith("_"):
                configs.append(file_path.stem)
        
        for file_path in self.config_dir.glob("*.yaml"):
            if not file_path.stem.startswith("_"):
                configs.append(file_path.stem)
        
        return sorted(list(set(configs)))
    
    def _find_config_file(self, config_name: str) -> Optional[Path]:
        """Find a config file by name"""
        # If it's already a path, use it directly
        if Path(config_name).exists():
            return Path(config_name)
        
        # Check in config directory
        for ext in ['.json', '.yaml', '.yml']:
            config_path = self.config_dir / f"{config_name}{ext}"
            if config_path.exists():
                return config_path
        
        return None
    
    def _load_file(self, file_path: Path) -> Dict[str, Any]:
        """Load a config file based on extension"""
        with open(file_path, 'r') as f:
            if file_path.suffix in ['.yaml', '.yml']:
                return yaml.safe_load(f)
            else:
                return json.load(f)
    
    def _load_templates(self):
        """Load template configurations"""
        template_dir = self.config_dir / "_templates"
        if template_dir.exists():
            for template_path in template_dir.glob("*"):
                if template_path.is_file():
                    template_name = template_path.stem
                    self._templates[template_name] = self._load_file(template_path)
    
    def _process_inheritance(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Process configuration inheritance"""
        extends = config.pop('_extends')
        
        if isinstance(extends, str):
            extends = [extends]
        
        # Start with empty config
        merged_config = {}
        
        # Merge all parent configs
        for parent_name in extends:
            if parent_name in self._templates:
                parent_config = self._templates[parent_name]
            else:
                parent_config = self.load(parent_name)
            
            merged_config = self._deep_merge(merged_config, parent_config)
        
        # Merge current config on top
        merged_config = self._deep_merge(merged_config, config)
        
        return merged_config
    
    def _deep_merge(self, base: Dict[str, Any], update: Dict[str, Any]) -> Dict[str, Any]:
        """Deep merge two dictionaries"""
        result = copy.deepcopy(base)
        
        for key, value in update.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._deep_merge(result[key], value)
            else:
                result[key] = copy.deepcopy(value)
        
        return result