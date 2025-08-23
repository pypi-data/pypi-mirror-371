"""
Token management and authentication for Polaris CLI
"""

import json
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, Optional

from polaris_cli.utils.exceptions import (AuthenticationError,
                                          ConfigurationError, PolarisError)


class TokenManager:
    """Manages API tokens and authentication profiles."""
    
    def __init__(self):
        self.config_dir = Path.home() / ".polaris"
        self.config_file = self.config_dir / "config.json"
        self.ensure_config_dir()
    
    def ensure_config_dir(self) -> None:
        """Ensure the configuration directory exists."""
        self.config_dir.mkdir(exist_ok=True, mode=0o700)
    
    def load_config(self) -> Dict[str, Any]:
        """Load configuration from file."""
        if not self.config_file.exists():
            return {"profiles": {}, "default_profile": None}
        
        try:
            with open(self.config_file, "r") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError) as e:
            raise ConfigurationError(f"Failed to load configuration: {e}")
    
    def save_config(self, config: Dict[str, Any]) -> None:
        """Save configuration to file."""
        try:
            with open(self.config_file, "w") as f:
                json.dump(config, f, indent=2)
            os.chmod(self.config_file, 0o600)  # Restrict access
        except IOError as e:
            raise ConfigurationError(f"Failed to save configuration: {e}")
    
    def validate_polaris_token(self, token: str) -> bool:
        """Validate Polaris token format."""
        if not token:
            return False
        
        # Basic validation - tokens should start with pk_ and be at least 40 chars
        return token.startswith("pk_") and len(token) >= 40
    
    def validate_jwt_token(self, jwt_token: str) -> bool:
        """Validate JWT token by making API call."""
        if not jwt_token:
            return False
        
        try:
            from polaris_cli.utils.api_client import get_api_client
            api_client = get_api_client()
            result = api_client.validate_token(jwt_token)
            return result.get("valid", False)
        except Exception:
            return False
    
    def add_profile(self, name: str, polaris_token: str, jwt_token: Optional[str] = None, 
                   jwt_expires: Optional[str] = None, user_info: Optional[Dict[str, Any]] = None) -> None:
        """Add a new authentication profile."""
        if not self.validate_polaris_token(polaris_token):
            raise AuthenticationError("Invalid Polaris token format")
        
        config = self.load_config()
        config["profiles"][name] = {
            "polaris_token": polaris_token,
            "jwt_token": jwt_token,
            "jwt_expires": jwt_expires,
            "user_info": user_info or {},
            "created_at": datetime.now().isoformat(),
            "last_used": None,
        }
        
        # Set as default if it's the first profile
        if not config["default_profile"]:
            config["default_profile"] = name
        
        self.save_config(config)
    
    def remove_profile(self, name: str) -> None:
        """Remove an authentication profile."""
        config = self.load_config()
        
        if name not in config["profiles"]:
            raise ConfigurationError(f"Profile '{name}' not found")
        
        del config["profiles"][name]
        
        # Update default if we removed it
        if config["default_profile"] == name:
            remaining_profiles = list(config["profiles"].keys())
            config["default_profile"] = remaining_profiles[0] if remaining_profiles else None
        
        self.save_config(config)
    
    def set_default_profile(self, name: str) -> None:
        """Set the default authentication profile."""
        config = self.load_config()
        
        if name not in config["profiles"]:
            raise ConfigurationError(f"Profile '{name}' not found")
        
        config["default_profile"] = name
        self.save_config(config)
    
    def get_profile(self, name: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Get a specific profile or the default one."""
        config = self.load_config()
        
        if name is None:
            name = config.get("default_profile")
        
        if name is None:
            return None
        
        profile = config["profiles"].get(name)
        if profile:
            # Update last used timestamp
            profile["last_used"] = datetime.now().isoformat()
            config["profiles"][name] = profile
            self.save_config(config)
        
        return profile
    
    def get_current_jwt_token(self, profile: Optional[str] = None) -> Optional[str]:
        """Get the JWT token for the current or specified profile."""
        profile_data = self.get_profile(profile)
        if not profile_data:
            return None
        
        jwt_token = profile_data.get("jwt_token")
        jwt_expires = profile_data.get("jwt_expires")
        
        # Check if JWT token is expired
        if jwt_token and jwt_expires:
            try:
                expire_time = datetime.fromisoformat(jwt_expires.replace("Z", "+00:00"))
                if datetime.now().replace(tzinfo=expire_time.tzinfo) >= expire_time:
                    # Token is expired, try to refresh it
                    return self._refresh_jwt_token(profile_data.get("name", "default"))
            except (ValueError, TypeError):
                pass
        
        return jwt_token
    
    def get_current_polaris_token(self, profile: Optional[str] = None) -> Optional[str]:
        """Get the Polaris token for the current or specified profile."""
        profile_data = self.get_profile(profile)
        return profile_data.get("polaris_token") if profile_data else None
    
    def _refresh_jwt_token(self, profile_name: str) -> Optional[str]:
        """Refresh JWT token for a profile."""
        try:
            profile_data = self.get_profile(profile_name)
            if not profile_data:
                return None
            
            current_jwt = profile_data.get("jwt_token")
            if not current_jwt:
                return None
            
            from polaris_cli.utils.api_client import get_api_client
            api_client = get_api_client()
            
            # Try to refresh the token
            response = api_client.refresh_token(current_jwt)
            new_jwt = response.get("access_token")
            expires_in_hours = response.get("expires_in_hours", 24)
            
            if new_jwt:
                # Calculate expiration time
                expire_time = datetime.now() + timedelta(hours=expires_in_hours)
                
                # Update the profile
                config = self.load_config()
                if profile_name in config["profiles"]:
                    config["profiles"][profile_name]["jwt_token"] = new_jwt
                    config["profiles"][profile_name]["jwt_expires"] = expire_time.isoformat()
                    self.save_config(config)
                
                return new_jwt
                
        except Exception:
            return None
        
        return None
    
    def list_profiles(self) -> Dict[str, Dict[str, Any]]:
        """List all authentication profiles."""
        config = self.load_config()
        profiles = config.get("profiles", {})
        default_profile = config.get("default_profile")
        
        # Add default flag to each profile
        for name, profile in profiles.items():
            profile["is_default"] = (name == default_profile)
            profile["name"] = name
        
        return profiles
    
    def is_authenticated(self, profile: Optional[str] = None) -> bool:
        """Check if there's a valid JWT authentication token."""
        jwt_token = self.get_current_jwt_token(profile)
        return jwt_token is not None and self.validate_jwt_token(jwt_token)
    
    def login_with_token(self, polaris_token: str, profile_name: str = "default") -> None:
        """Login with a Polaris token and get JWT from API."""
        if not self.validate_polaris_token(polaris_token):
            raise AuthenticationError("Invalid Polaris token format")
        
        try:
            from polaris_cli.utils.api_client import get_api_client
            api_client = get_api_client()
            
            # Login with Polaris token to get JWT
            response = api_client.login_with_token(polaris_token)
            jwt_token = response.get("access_token")
            expires_in_hours = response.get("expires_in_hours", 24)
            user_info = response.get("user_info", {})
            
            if not jwt_token:
                raise AuthenticationError("Failed to obtain JWT token from API")
            
            # Calculate expiration time
            expire_time = datetime.now() + timedelta(hours=expires_in_hours)
            
            # Add the profile with both tokens
            self.add_profile(
                profile_name,
                polaris_token,
                jwt_token,
                expire_time.isoformat(),
                user_info
            )
            
        except PolarisError as e:
            raise AuthenticationError(f"Login failed: {str(e)}")
        except Exception as e:
            raise AuthenticationError(f"Login failed: {str(e)}")
    
    def logout(self, profile_name: Optional[str] = None) -> None:
        """Logout by removing the profile."""
        if profile_name is None:
            config = self.load_config()
            profile_name = config.get("default_profile")
        
        if profile_name:
            self.remove_profile(profile_name)
    
    def get_auth_status(self) -> Dict[str, Any]:
        """Get authentication status information."""
        config = self.load_config()
        default_profile = config.get("default_profile")
        
        if not default_profile:
            return {
                "authenticated": False,
                "profile": None,
                "profiles_count": len(config.get("profiles", {})),
            }
        
        profile = config["profiles"].get(default_profile, {})
        polaris_token = profile.get("polaris_token", "")
        jwt_token = self.get_current_jwt_token(default_profile)
        user_info = profile.get("user_info", {})
        
        return {
            "authenticated": self.is_authenticated(default_profile),
            "profile": default_profile,
            "profiles_count": len(config.get("profiles", {})),
            "created_at": profile.get("created_at"),
            "last_used": profile.get("last_used"),
            "token_prefix": f"{polaris_token[:10]}..." if polaris_token else None,
            "user_email": user_info.get("email"),
            "user_role": user_info.get("role"),
            "jwt_valid": jwt_token is not None,
        }
    
    def get_authenticated_api_client(self, profile: Optional[str] = None):
        """Get an API client with authentication set up."""
        from polaris_cli.utils.api_client import get_api_client
        
        api_client = get_api_client()
        jwt_token = self.get_current_jwt_token(profile)
        
        if jwt_token:
            api_client.set_auth_token(jwt_token)
        
        return api_client
