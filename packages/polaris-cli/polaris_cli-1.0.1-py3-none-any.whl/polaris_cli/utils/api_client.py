"""
API client for Polaris CLI
Handles all HTTP requests to the Polaris API server
"""

import json
import os
from typing import Any, Dict, List, Optional, Union
from urllib.parse import urljoin

import requests

from polaris_cli.utils.exceptions import (AuthenticationError,
                                          ConfigurationError, PolarisError)


class PolarisAPIClient:
    """Client for making requests to the Polaris API."""
    
    def __init__(self, base_url: str = "https://polaris-api-server.onrender.com"):
        self.base_url = base_url.rstrip("/")
        self.session = requests.Session()
        self.session.headers.update({
            "Content-Type": "application/json",
            "User-Agent": "Polaris-CLI/1.0.0"
        })
    
    def set_auth_token(self, token: str) -> None:
        """Set the JWT token for authenticated requests."""
        if token:
            self.session.headers["Authorization"] = f"Bearer {token}"
        else:
            self.session.headers.pop("Authorization", None)
    
    def _make_request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        data: Optional[Dict[str, Any]] = None,
        timeout: int = 30
    ) -> Dict[str, Any]:
        """Make an HTTP request to the API."""
        url = urljoin(self.base_url, endpoint.lstrip("/"))
        
        try:
            response = self.session.request(
                method=method.upper(),
                url=url,
                params=params,
                json=data if data else None,
                timeout=timeout
            )
            
            # Handle different status codes
            if response.status_code == 401:
                raise AuthenticationError("Authentication failed. Please login again.")
            elif response.status_code == 403:
                raise AuthenticationError("Access denied. Insufficient permissions.")
            elif response.status_code == 404:
                raise PolarisError(f"Resource not found: {endpoint}")
            elif response.status_code >= 400:
                try:
                    error_data = response.json()
                    error_msg = error_data.get("detail", f"HTTP {response.status_code}")
                except:
                    error_msg = f"HTTP {response.status_code}: {response.text}"
                raise PolarisError(error_msg)
            
            # Parse response
            if response.headers.get("content-type", "").startswith("application/json"):
                return response.json()
            else:
                return {"data": response.text, "status_code": response.status_code}
                
        except requests.exceptions.ConnectionError:
            raise PolarisError(f"Unable to connect to Polaris API at {self.base_url}")
        except requests.exceptions.Timeout:
            raise PolarisError("Request timeout. The API server may be slow to respond.")
        except requests.exceptions.RequestException as e:
            raise PolarisError(f"Request failed: {str(e)}")
    
    def get(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Make a GET request."""
        return self._make_request("GET", endpoint, params=params)
    
    def post(self, endpoint: str, data: Optional[Dict[str, Any]] = None, json: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Make a POST request."""
        payload = json if json is not None else data
        return self._make_request("POST", endpoint, data=payload)
    
    def put(self, endpoint: str, data: Optional[Dict[str, Any]] = None, json: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Make a PUT request."""
        payload = json if json is not None else data
        return self._make_request("PUT", endpoint, data=payload)
    
    def delete(self, endpoint: str) -> Dict[str, Any]:
        """Make a DELETE request."""
        return self._make_request("DELETE", endpoint)
    
    # Authentication endpoints
    def login_with_token(self, polaris_token: str) -> Dict[str, Any]:
        """Login with a Polaris token and get JWT."""
        return self.post("/auth/token/login", {"polaris_token": polaris_token})
    
    def refresh_token(self, jwt_token: str) -> Dict[str, Any]:
        """Refresh the JWT token."""
        old_auth = self.session.headers.get("Authorization")
        self.set_auth_token(jwt_token)
        try:
            return self.post("/auth/token/refresh")
        finally:
            if old_auth:
                self.session.headers["Authorization"] = old_auth
    
    def validate_token(self, jwt_token: str) -> Dict[str, Any]:
        """Validate a JWT token."""
        old_auth = self.session.headers.get("Authorization")
        self.set_auth_token(jwt_token)
        try:
            return self.post("/auth/token/validate")
        finally:
            if old_auth:
                self.session.headers["Authorization"] = old_auth
    
    def get_user_info(self) -> Dict[str, Any]:
        """Get current user information."""
        return self.get("/auth/me")
    
    # Resource endpoints
    def list_resources(
        self,
        provider: Optional[str] = None,
        resource_type: Optional[str] = None,
        available_only: Optional[bool] = None,
        sort_by: Optional[str] = None
    ) -> Dict[str, Any]:
        """List all resources with optional filters."""
        params = {}
        if provider:
            params["provider"] = provider
        if resource_type:
            params["resource_type"] = resource_type
        if available_only is not None:
            params["available_only"] = str(available_only).lower()
        if sort_by:
            params["sort_by"] = sort_by
        
        return self.get("/resources/", params=params)
    
    def search_resources(self, query: str, resource_type: Optional[str] = None, available_only: Optional[bool] = None) -> Dict[str, Any]:
        """Search resources by query."""
        params = {"q": query}
        if resource_type:
            params["resource_type"] = resource_type
        if available_only is not None:
            params["available_only"] = str(available_only).lower()
        
        return self.get("/resources/search", params=params)
    
    def list_cpu_resources(
        self,
        min_cores: Optional[int] = None,
        architecture: Optional[str] = None,
        available_only: Optional[bool] = None
    ) -> Dict[str, Any]:
        """List CPU resources."""
        params = {}
        if min_cores:
            params["min_cores"] = min_cores
        if architecture:
            params["architecture"] = architecture
        if available_only is not None:
            params["available_only"] = str(available_only).lower()
        
        return self.get("/resources/cpu", params=params)
    
    def list_gpu_resources(
        self,
        provider: Optional[str] = None,
        min_memory: Optional[str] = None,
        model: Optional[str] = None,
        available_only: Optional[bool] = None
    ) -> Dict[str, Any]:
        """List GPU resources."""
        params = {}
        if provider:
            params["provider"] = provider
        if min_memory:
            params["min_memory"] = min_memory
        if model:
            params["model"] = model
        if available_only is not None:
            params["available_only"] = str(available_only).lower()
        
        return self.get("/resources/gpu", params=params)
    
    def get_resource_availability(self, region: Optional[str] = None) -> Dict[str, Any]:
        """Get resource availability statistics."""
        params = {}
        if region:
            params["region"] = region
        
        return self.get("/resources/availability", params=params)
    
    # Template endpoints
    def list_templates(
        self,
        category: Optional[str] = None,
        gpu_required: Optional[bool] = None,
        sort_by: Optional[str] = None
    ) -> Dict[str, Any]:
        """List all templates with optional filters."""
        params = {}
        if category:
            params["category"] = category
        if gpu_required is not None:
            params["gpu_required"] = str(gpu_required).lower()
        if sort_by:
            params["sort_by"] = sort_by
        
        return self.get("/templates/", params=params)
    
    def get_template(self, template_id: str) -> Dict[str, Any]:
        """Get template by ID."""
        return self.get(f"/templates/{template_id}")
    
    def search_templates(self, query: str, category: Optional[str] = None) -> Dict[str, Any]:
        """Search templates by query."""
        params = {"q": query}
        if category:
            params["category"] = category
        
        return self.get("/templates/search/", params=params)
    
    def list_templates_by_category(self, category: str, sort_by: Optional[str] = None) -> Dict[str, Any]:
        """Get templates by category."""
        params = {}
        if sort_by:
            params["sort_by"] = sort_by
        
        return self.get(f"/templates/category/{category}", params=params)
    
    def list_gpu_templates(self, sort_by: Optional[str] = None) -> Dict[str, Any]:
        """List GPU required templates."""
        params = {}
        if sort_by:
            params["sort_by"] = sort_by
        
        return self.get("/templates/gpu/required", params=params)
    
    def list_cpu_templates(self, sort_by: Optional[str] = None) -> Dict[str, Any]:
        """List CPU only templates."""
        params = {}
        if sort_by:
            params["sort_by"] = sort_by
        
        return self.get("/templates/cpu/only", params=params)
    
    def list_template_categories(self) -> Dict[str, Any]:
        """List all template categories."""
        return self.get("/templates/categories/list")
    
    # System endpoints
    def health_check(self) -> Dict[str, Any]:
        """Check API health."""
        return self.get("/health")
    
    def get_api_info(self) -> Dict[str, Any]:
        """Get API information."""
        return self.get("/")
    
    # SSH Key Management endpoints
    def list_ssh_keys(self) -> Dict[str, Any]:
        """List user's SSH keys."""
        return self.get("/ssh/keys/")
    
    def add_ssh_key(self, name: str, public_key: str) -> Dict[str, Any]:
        """Add a new SSH key."""
        data = {
            "name": name,
            "public_key": public_key
        }
        return self.post("/ssh/keys/", json=data)
    
    def delete_ssh_key(self, key_id: str) -> Dict[str, Any]:
        """Delete an SSH key."""
        return self.delete(f"/ssh/keys/{key_id}")
    
    def set_default_ssh_key(self, key_id: str) -> Dict[str, Any]:
        """Set an SSH key as default."""
        return self.put(f"/ssh/keys/{key_id}/default")
    
    # Instance Management endpoints
    def create_instance(self, name: str, resource_id: str, template_id: str, 
                       ssh_key_id: Optional[str] = None, disk_size: int = 100, 
                       auto_shutdown: int = 0, duration_days: int = 1) -> Dict[str, Any]:
        """Create a new instance."""
        data = {
            "name": name,
            "resource_id": resource_id,
            "template_id": template_id,
            "disk_size": disk_size,
            "auto_shutdown": auto_shutdown,
            "duration_days": duration_days
        }
        if ssh_key_id:
            data["ssh_key_id"] = ssh_key_id
        return self.post("/instances/", json=data)
    
    def list_instances(self, status: Optional[str] = None, region: Optional[str] = None,
                      limit: int = 50, offset: int = 0) -> Dict[str, Any]:
        """List user instances."""
        params = {"limit": limit, "offset": offset}
        if status:
            params["status"] = status
        if region:
            params["region"] = region
        return self.get("/instances/", params=params)
    
    def get_instance(self, instance_id: str) -> Dict[str, Any]:
        """Get instance details."""
        return self.get(f"/instances/{instance_id}")
    
    def start_instance(self, instance_id: str) -> Dict[str, Any]:
        """Start an instance."""
        return self.put(f"/instances/{instance_id}/start")
    
    def stop_instance(self, instance_id: str) -> Dict[str, Any]:
        """Stop an instance."""
        return self.put(f"/instances/{instance_id}/stop")
    
    def terminate_instance(self, instance_id: str) -> Dict[str, Any]:
        """Terminate an instance."""
        return self.delete(f"/instances/{instance_id}")
    
    def get_instance_logs(self, instance_id: str, tail: int = 100, 
                         follow: bool = False, since: Optional[str] = None) -> Dict[str, Any]:
        """Get instance logs."""
        params = {"tail": tail, "follow": follow}
        if since:
            params["since"] = since
        return self.get(f"/instances/{instance_id}/logs", params=params)
    
    def execute_command(self, instance_id: str, command: str, timeout: int = 30,
                       user: str = "root", working_dir: Optional[str] = None) -> Dict[str, Any]:
        """Execute command on instance."""
        data = {
            "command": command,
            "timeout": timeout,
            "user": user
        }
        if working_dir:
            data["working_dir"] = working_dir
        return self.post(f"/instances/{instance_id}/exec", json=data)
    
    def get_instance_status(self, instance_id: str) -> Dict[str, Any]:
        """Get detailed instance status."""
        return self.get(f"/instances/{instance_id}/status")


# Global API client instance
_api_client: Optional[PolarisAPIClient] = None


def get_api_client() -> PolarisAPIClient:
    """Get the global API client instance."""
    global _api_client
    if _api_client is None:
        _api_client = PolarisAPIClient()
    return _api_client
