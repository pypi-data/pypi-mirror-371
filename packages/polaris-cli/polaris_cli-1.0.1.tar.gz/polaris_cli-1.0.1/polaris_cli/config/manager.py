"""
Configuration management for Polaris CLI
"""

import json
from pathlib import Path
from typing import Any, Dict, Optional

from polaris_cli.utils.exceptions import ConfigurationError


class ConfigManager:
    """Manages CLI configuration settings."""
    
    def __init__(self):
        self.config_dir = Path.home() / ".polaris"
        self.settings_file = self.config_dir / "settings.json"
        self.ensure_config_dir()
        self._defaults = self._get_default_settings()
    
    def ensure_config_dir(self) -> None:
        """Ensure the configuration directory exists."""
        self.config_dir.mkdir(exist_ok=True, mode=0o700)
    
    def _get_default_settings(self) -> Dict[str, Any]:
        """Get default configuration settings."""
        return {
            "default_region": "us-west-1",
            "output_format": "table",  # table, json, csv
            "show_prices": True,
            "currency": "usd",
            "auto_confirm": False,
            "max_results": 50,
            "timeout": 30,
            "retry_attempts": 3,
            "show_animations": True,
            "color_mode": "auto",  # auto, always, never
            "verbose": False,
            "ssh_default_user": "root",
            "ssh_timeout": 30,
            "billing_alerts": {
                "enabled": True,
                "threshold": 100.0,
            },
            "resource_preferences": {
                "preferred_gpu_provider": "nvidia",
                "preferred_cpu_provider": "amd",
                "preferred_storage_type": "nvme",
            },
            "display_preferences": {
                "table_style": "modern",
                "show_timestamps": True,
                "timezone": "local",
                "date_format": "%Y-%m-%d %H:%M:%S",
            }
        }
    
    def load_settings(self) -> Dict[str, Any]:
        """Load settings from file, falling back to defaults."""
        if not self.settings_file.exists():
            return self._defaults.copy()
        
        try:
            with open(self.settings_file, "r") as f:
                stored_settings = json.load(f)
            
            # Merge with defaults to ensure all keys exist
            settings = self._defaults.copy()
            settings.update(stored_settings)
            return settings
        
        except (json.JSONDecodeError, IOError) as e:
            raise ConfigurationError(f"Failed to load settings: {e}")
    
    def save_settings(self, settings: Dict[str, Any]) -> None:
        """Save settings to file."""
        try:
            with open(self.settings_file, "w") as f:
                json.dump(settings, f, indent=2)
        except IOError as e:
            raise ConfigurationError(f"Failed to save settings: {e}")
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get a configuration value."""
        settings = self.load_settings()
        
        # Support nested keys with dot notation
        keys = key.split(".")
        value = settings
        
        try:
            for k in keys:
                value = value[k]
            return value
        except (KeyError, TypeError):
            return default
    
    def set(self, key: str, value: Any) -> None:
        """Set a configuration value."""
        settings = self.load_settings()
        
        # Support nested keys with dot notation
        keys = key.split(".")
        current = settings
        
        # Navigate to the parent of the target key
        for k in keys[:-1]:
            if k not in current or not isinstance(current[k], dict):
                current[k] = {}
            current = current[k]
        
        # Set the value
        current[keys[-1]] = value
        
        self.save_settings(settings)
    
    def unset(self, key: str) -> bool:
        """Remove a configuration value."""
        settings = self.load_settings()
        
        keys = key.split(".")
        current = settings
        
        try:
            # Navigate to the parent
            for k in keys[:-1]:
                current = current[k]
            
            # Remove the key
            if keys[-1] in current:
                del current[keys[-1]]
                self.save_settings(settings)
                return True
            
            return False
        except (KeyError, TypeError):
            return False
    
    def reset(self) -> None:
        """Reset all settings to defaults."""
        self.save_settings(self._defaults.copy())
    
    def show_all(self) -> Dict[str, Any]:
        """Show all current settings."""
        return self.load_settings()
    
    def validate_setting(self, key: str, value: Any) -> bool:
        """Validate a setting value."""
        validators = {
            "output_format": lambda v: v in ["table", "json", "csv"],
            "currency": lambda v: v in ["usd", "eur", "gbp"],
            "color_mode": lambda v: v in ["auto", "always", "never"],
            "max_results": lambda v: isinstance(v, int) and 1 <= v <= 1000,
            "timeout": lambda v: isinstance(v, int) and 1 <= v <= 300,
            "retry_attempts": lambda v: isinstance(v, int) and 0 <= v <= 10,
            "show_animations": lambda v: isinstance(v, bool),
            "show_prices": lambda v: isinstance(v, bool),
            "auto_confirm": lambda v: isinstance(v, bool),
            "verbose": lambda v: isinstance(v, bool),
            "ssh_timeout": lambda v: isinstance(v, int) and 1 <= v <= 300,
        }
        
        validator = validators.get(key)
        if validator:
            return validator(value)
        
        # If no specific validator, allow any value
        return True
    
    def get_profile_config(self, profile: Optional[str] = None) -> Dict[str, Any]:
        """Get configuration for a specific profile."""
        settings = self.load_settings()
        
        if profile:
            profile_key = f"profiles.{profile}"
            profile_settings = self.get(profile_key, {})
            
            # Merge profile-specific settings with global settings
            merged = settings.copy()
            merged.update(profile_settings)
            return merged
        
        return settings
    
    def set_profile_config(self, profile: str, key: str, value: Any) -> None:
        """Set a configuration value for a specific profile."""
        profile_key = f"profiles.{profile}.{key}"
        self.set(profile_key, value)
