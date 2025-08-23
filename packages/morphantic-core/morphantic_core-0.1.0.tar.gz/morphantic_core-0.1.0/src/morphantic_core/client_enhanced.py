"""
Morphantic Core Client SDK - Enhanced with Authentication
"""

import requests
import json
import time
from typing import Dict, Any, Optional, List, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from enum import Enum

class AuthType(Enum):
    JWT = "jwt"
    API_KEY = "api_key"

@dataclass
class UserCredentials:
    email: str
    password: str

@dataclass
class UserSignupData:
    email: str
    password: str
    first_name: str
    last_name: str

@dataclass
class OptimizationConfig:
    pop_size: int = 60
    max_generations: int = 45
    n_islands: int = 4
    seed: Optional[int] = None

@dataclass
class ObjectiveSpec:
    name: str
    weight: float
    baseline: float
    target: float
    direction: str = "max"  # "max" or "min"

@dataclass
class OptimizationRequest:
    callback_url: str
    dimension: int
    bounds: Tuple[float, float] = (-5.0, 5.0)
    objectives: Optional[List[ObjectiveSpec]] = None
    config: Optional[OptimizationConfig] = None
    modules: Optional[List[str]] = None
    domain: Optional[str] = None

class MorphanticAuthenticatedClient:
    """Enhanced Morphantic client with full authentication support"""
    
    def __init__(self, base_url: str = "https://testserver.morphantic.com"):
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        self.auth_type = None
        self.access_token = None
        self.refresh_token = None
        self.api_key = None
        self.token_expiry = None
        
    def signup(self, signup_data: UserSignupData) -> Dict[str, Any]:
        """Create a new user account"""
        response = self.session.post(
            f"{self.base_url}/v1/auth/signup",
            json=asdict(signup_data)
        )
        response.raise_for_status()
        return response.json()
    
    def login(self, credentials: UserCredentials) -> Dict[str, Any]:
        """Login with email and password"""
        response = self.session.post(
            f"{self.base_url}/v1/auth/login",
            json=asdict(credentials)
        )
        response.raise_for_status()
        data = response.json()
        
        self.auth_type = AuthType.JWT
        self.access_token = data["access_token"]
        self.refresh_token = data["refresh_token"]
        self.token_expiry = datetime.now() + timedelta(seconds=data.get("expires_in", 1800))
        
        self.session.headers.update({
            "Authorization": f"Bearer {self.access_token}"
        })
        
        return data
    
    def refresh_access_token(self) -> Dict[str, Any]:
        """Refresh the access token using refresh token"""
        if not self.refresh_token:
            raise ValueError("No refresh token available")
        
        response = self.session.post(
            f"{self.base_url}/v1/auth/refresh",
            json={"refresh_token": self.refresh_token}
        )
        response.raise_for_status()
        data = response.json()
        
        self.access_token = data["access_token"]
        self.token_expiry = datetime.now() + timedelta(seconds=data.get("expires_in", 1800))
        
        self.session.headers.update({
            "Authorization": f"Bearer {self.access_token}"
        })
        
        return data
    
    def _ensure_authenticated(self):
        """Ensure the client is authenticated and tokens are valid"""
        if self.auth_type == AuthType.JWT:
            if self.token_expiry and datetime.now() >= self.token_expiry - timedelta(seconds=60):
                self.refresh_access_token()
        elif self.auth_type == AuthType.API_KEY:
            pass
        else:
            raise ValueError("Client is not authenticated. Please login or use an API key.")
    
    def get_profile(self) -> Dict[str, Any]:
        """Get current user profile"""
        self._ensure_authenticated()
        response = self.session.get(f"{self.base_url}/v1/auth/me")
        response.raise_for_status()
        return response.json()
    
    def update_profile(self, first_name: Optional[str] = None, last_name: Optional[str] = None) -> Dict[str, Any]:
        """Update user profile"""
        self._ensure_authenticated()
        data = {}
        if first_name:
            data["first_name"] = first_name
        if last_name:
            data["last_name"] = last_name
        
        response = self.session.put(
            f"{self.base_url}/v1/auth/me",
            json=data
        )
        response.raise_for_status()
        return response.json()
    
    def change_password(self, current_password: str, new_password: str) -> Dict[str, Any]:
        """Change user password"""
        self._ensure_authenticated()
        response = self.session.post(
            f"{self.base_url}/v1/auth/change-password",
            json={
                "current_password": current_password,
                "new_password": new_password
            }
        )
        response.raise_for_status()
        return response.json()
    
    def create_api_key(
        self,
        name: Optional[str] = None,
        expires_days: Optional[int] = 30,
        permissions: Optional[List[str]] = None,
        rate_limit: int = 100
    ) -> Dict[str, Any]:
        """Create a new API key"""
        self._ensure_authenticated()
        
        data = {
            "name": name,
            "expires_days": expires_days,
            "permissions": permissions or ["optimize", "read_results"],
            "rate_limit": rate_limit
        }
        
        response = self.session.post(
            f"{self.base_url}/v1/api-keys",
            json=data
        )
        response.raise_for_status()
        return response.json()
    
    def list_api_keys(self) -> List[Dict[str, Any]]:
        """List all API keys for the authenticated user"""
        self._ensure_authenticated()
        response = self.session.get(f"{self.base_url}/v1/api-keys")
        response.raise_for_status()
        return response.json()
    
    def revoke_api_key(self, key_id: str) -> Dict[str, Any]:
        """Revoke a specific API key"""
        self._ensure_authenticated()
        response = self.session.delete(f"{self.base_url}/v1/api-keys/{key_id}")
        response.raise_for_status()
        return response.json()
    
    def use_api_key(self, api_key: str):
        """Configure client to use API key authentication"""
        self.auth_type = AuthType.API_KEY
        self.api_key = api_key
        self.session.headers.update({
            "X-API-Key": api_key
        })
        # Remove JWT auth header if present
        if "Authorization" in self.session.headers:
            del self.session.headers["Authorization"]
    
    def get_usage_stats(self) -> Dict[str, Any]:
        """Get usage statistics"""
        self._ensure_authenticated()
        response = self.session.get(f"{self.base_url}/v1/usage/stats")
        response.raise_for_status()
        return response.json()
    
    def start_optimization(self, request: OptimizationRequest) -> Dict[str, Any]:
        """Start an optimization job"""
        self._ensure_authenticated()
        
        # Convert objectives to dict format
        objectives = None
        if request.objectives:
            objectives = [
                {
                    "name": obj.name,
                    "weight": obj.weight,
                    "baseline": obj.baseline,
                    "target": obj.target,
                    "direction": obj.direction
                }
                for obj in request.objectives
            ]
        
        payload = {
            "callback_url": request.callback_url,
            "dimension": request.dimension,
            "bounds": request.bounds,
            "objectives": objectives,
            "domain": request.domain,
            "modules": request.modules
        }
        
        if request.config:
            payload["config"] = asdict(request.config)
        
        response = self.session.post(
            f"{self.base_url}/v1/optimize",
            json=payload
        )
        response.raise_for_status()
        return response.json()
    
    def get_job_results(self, job_id: str) -> Dict[str, Any]:
        """Get results for a specific job"""
        self._ensure_authenticated()
        response = self.session.get(f"{self.base_url}/v1/results/{job_id}")
        response.raise_for_status()
        return response.json()
    
    def list_jobs(self, limit: int = 10, offset: int = 0) -> Dict[str, Any]:
        """List optimization jobs"""
        self._ensure_authenticated()
        response = self.session.get(
            f"{self.base_url}/v1/jobs",
            params={"limit": limit, "offset": offset}
        )
        response.raise_for_status()
        return response.json()
    
    def wait_for_job(self, job_id: str, poll_interval: int = 5, timeout: int = 3600) -> Dict[str, Any]:
        """Wait for a job to complete"""
        start_time = time.time()
        
        while True:
            if time.time() - start_time > timeout:
                raise TimeoutError(f"Job {job_id} did not complete within {timeout} seconds")
            
            result = self.get_job_results(job_id)
            if result["status"] in ["completed", "failed"]:
                return result
            
            time.sleep(poll_interval)
    
    def run_optimization(self, request: OptimizationRequest, wait: bool = True) -> Dict[str, Any]:
        """Run optimization and optionally wait for completion"""
        job = self.start_optimization(request)
        
        if wait:
            return self.wait_for_job(job["job_id"])
        return job


class QuickStart:
    """Convenience functions for quick usage"""
    
    @staticmethod
    def signup_and_login(base_url: str, signup_data: UserSignupData) -> MorphanticAuthenticatedClient:
        """Sign up a new user and login"""
        client = MorphanticAuthenticatedClient(base_url)
        client.signup(signup_data)
        client.login(UserCredentials(signup_data.email, signup_data.password))
        return client
    
    @staticmethod
    def login_and_create_api_key(base_url: str, credentials: UserCredentials) -> str:
        """Login and create an API key"""
        client = MorphanticAuthenticatedClient(base_url)
        client.login(credentials)
        response = client.create_api_key(name="Auto-generated key")
        return response["api_key"]
    
    @staticmethod
    def create_client_with_api_key(base_url: str, api_key: str) -> MorphanticAuthenticatedClient:
        """Create a client configured with API key"""
        client = MorphanticAuthenticatedClient(base_url)
        client.use_api_key(api_key)
        return client


