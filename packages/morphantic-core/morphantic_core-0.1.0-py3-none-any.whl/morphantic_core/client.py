import requests
import json
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from datetime import datetime

@dataclass
class OptimizationConfig:
    pop_size: int = 60
    max_generations: int = 45
    n_islands: int = 4
    seed: Optional[int] = None

@dataclass
class OptimizationRequest:
    objectives: Optional[List[Dict[str, Any]]] = None
    callback_url: str = ""
    dimension: int = 10
    bounds: tuple = (-5.0, 5.0)
    config: OptimizationConfig = None
    modules: Optional[List[str]] = None
    domain: Optional[str] = None

class MorphanticClient:
    def __init__(self, base_url: str = "https://testserver.morphantic.com", api_key: Optional[str] = None):
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key
        self.session = requests.Session()
        if api_key:
            self.session.headers.update({"X-API-Key": api_key})
    
    def create_api_key(self, user_id: str, expires_days: int = 30) -> Dict[str, Any]:
        """Create a new API key"""
        response = self.session.post(
            f"{self.base_url}/v1/auth/create-key",
            json={"user_id": user_id, "expires_days": expires_days}
        )
        response.raise_for_status()
        return response.json()
    
    def list_keys(self, user_id: str) -> Dict[str, Any]:
        """List all API keys for a user"""
        response = self.session.get(f"{self.base_url}/v1/auth/keys/{user_id}")
        response.raise_for_status()
        return response.json()
    
    def revoke_key(self) -> Dict[str, Any]:
        """Revoke the current API key"""
        response = self.session.delete(f"{self.base_url}/v1/auth/revoke-key")
        response.raise_for_status()
        return response.json()
    
    def start_optimization(self, request: OptimizationRequest) -> Dict[str, Any]:
        """Start an optimization job"""
        if request.config is None:
            request.config = OptimizationConfig()
        
        payload = {
            "objectives": request.objectives,
            "callback_url": request.callback_url,
            "dimension": request.dimension,
            "bounds": request.bounds,
            "config": {
                "pop_size": request.config.pop_size,
                "max_generations": request.config.max_generations,
                "n_islands": request.config.n_islands,
                "seed": request.config.seed
            },
            "modules": request.modules,
            "domain": request.domain
        }
        
        response = self.session.post(
            f"{self.base_url}/v1/optimize",
            json=payload
        )
        response.raise_for_status()
        return response.json()
    
    def get_results(self, job_id: str) -> Dict[str, Any]:
        """Get results for a job"""
        response = self.session.get(f"{self.base_url}/v1/results/{job_id}")
        response.raise_for_status()
        return response.json()
    
    def wait_for_completion(self, job_id: str, poll_interval: int = 5, timeout: int = 3600) -> Dict[str, Any]:
        """Wait for a job to complete"""
        import time
        start_time = time.time()
        
        while True:
            if time.time() - start_time > timeout:
                raise TimeoutError(f"Job {job_id} did not complete within {timeout} seconds")
            
            result = self.get_results(job_id)
            if result["status"] in ["completed", "failed"]:
                return result
            
            time.sleep(poll_interval)

# Convenience functions for quick usage
def create_api_key(base_url: str, user_id: str, expires_days: int = 30) -> str:
    """Quick function to create an API key"""
    client = MorphanticClient(base_url)
    response = client.create_api_key(user_id, expires_days)
    return response["api_key"]

def run_optimization(base_url: str, api_key: str, request: OptimizationRequest, wait: bool = True) -> Dict[str, Any]:
    """Quick function to run optimization"""
    client = MorphanticClient(base_url, api_key)
    job = client.start_optimization(request)
    
    if wait:
        return client.wait_for_completion(job["job_id"])
    return job
