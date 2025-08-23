"""
Anansi Compute Client - Core implementation
"""

import json
import pickle
import base64
import requests
from typing import Dict, Any, Optional, Callable, List
import time


class AnansiConfig:
    """Global configuration for Anansi client"""
    endpoint: Optional[str] = None
    api_key: Optional[str] = None
    timeout: int = 300  # 5 minutes default


def configure(endpoint: str, api_key: str, timeout: int = 300) -> None:
    """Configure Anansi client with endpoint and API key
    
    Args:
        endpoint: API endpoint URL (e.g., "https://api.rewsr.com")
        api_key: Your Anansi API key
        timeout: Request timeout in seconds (default: 300)
    """
    AnansiConfig.endpoint = endpoint.rstrip('/')
    AnansiConfig.api_key = api_key
    AnansiConfig.timeout = timeout


def _check_config() -> None:
    """Verify that client is configured"""
    if not AnansiConfig.endpoint or not AnansiConfig.api_key:
        raise ValueError(
            "Anansi not configured. Call anansi.configure(endpoint='...', api_key='...') first"
        )


def _serialize_function(fn: Callable) -> str:
    """Serialize a Python function for remote execution"""
    try:
        # Try to serialize the function
        serialized = pickle.dumps(fn)
        return base64.b64encode(serialized).decode('utf-8')
    except Exception as e:
        raise ValueError(f"Function cannot be serialized: {e}")


def compute(
    fn: Any,
    args: tuple = (),
    kwargs: Optional[Dict[str, Any]] = None,
    policy: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """Execute a computation with secure orchestration
    
    Args:
        fn: Function to execute (callable) or function name (str)
        args: Positional arguments for the function
        kwargs: Keyword arguments for the function
        policy: Security and routing policy
        
    Returns:
        Dict containing result, run_id, cloud, compute details
        
    Example:
        result = anansi.compute(
            fn=lambda x, y: [a + b for a, b in zip(x, y)],
            args=([1, 2, 3], [10, 20, 30]),
            policy={"min_trust": "GPU_CC", "allowed_clouds": ["azure"]}
        )
    """
    _check_config()
    
    if kwargs is None:
        kwargs = {}
    
    if policy is None:
        policy = {"min_trust": "CPU_TEE"}
    
    # Prepare payload
    payload = {
        "args": list(args),
        "kwargs": kwargs,
        "policy": policy
    }
    
    # Handle function serialization
    if callable(fn):
        payload["fn_type"] = "python"
        payload["fn_data"] = _serialize_function(fn)
    elif isinstance(fn, str):
        payload["fn_type"] = "builtin"
        payload["fn"] = fn
    else:
        raise ValueError("fn must be a callable function or string function name")
    
    # Make request
    headers = {
        "Authorization": f"Bearer {AnansiConfig.api_key}",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.post(
            f"{AnansiConfig.endpoint}/compute",
            json=payload,
            headers=headers,
            timeout=AnansiConfig.timeout
        )
        response.raise_for_status()
        return response.json()
        
    except requests.exceptions.RequestException as e:
        raise RuntimeError(f"Anansi compute request failed: {e}")


def run_spark(
    spark_session: Any,
    code: Callable,
    policy: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """Execute Spark code with secure orchestration
    
    Args:
        spark_session: Current Spark session (will be recreated in secure environment)
        code: Function that takes a SparkSession and returns results
        policy: Security and routing policy
        
    Returns:
        Dict containing result, run_id, cloud, compute details
        
    Example:
        result = anansi.run_spark(
            spark,
            lambda s: s.range(100).filter(lambda x: x % 2 == 0).count(),
            policy={"min_trust": "CPU_TEE", "data_residency": "US"}
        )
    """
    _check_config()
    
    if policy is None:
        policy = {"min_trust": "CPU_TEE"}
    
    # Serialize the Spark code
    try:
        spark_code_b64 = _serialize_function(code)
    except Exception as e:
        raise ValueError(f"Spark code cannot be serialized: {e}")
    
    payload = {
        "fn_type": "spark",
        "spark_code": spark_code_b64,
        "policy": policy
    }
    
    headers = {
        "Authorization": f"Bearer {AnansiConfig.api_key}",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.post(
            f"{AnansiConfig.endpoint}/compute",
            json=payload,
            headers=headers,
            timeout=AnansiConfig.timeout
        )
        response.raise_for_status()
        return response.json()
        
    except requests.exceptions.RequestException as e:
        raise RuntimeError(f"Anansi Spark request failed: {e}")


def health_check() -> Dict[str, Any]:
    """Check if Anansi service is healthy
    
    Returns:
        Dict with health status and service info
    """
    _check_config()
    
    try:
        response = requests.get(
            f"{AnansiConfig.endpoint}/healthz",
            timeout=30
        )
        response.raise_for_status()
        return response.json()
        
    except requests.exceptions.RequestException as e:
        return {"healthy": False, "error": str(e)}


def get_proof(run_id: str) -> Optional[Dict[str, Any]]:
    """Get cryptographic proof for a computation
    
    Args:
        run_id: The run ID returned from compute()
        
    Returns:
        Proof bundle or None if not found
    """
    _check_config()
    
    headers = {
        "Authorization": f"Bearer {AnansiConfig.api_key}"
    }
    
    try:
        response = requests.get(
            f"{AnansiConfig.endpoint}/proofs/{run_id}.json",
            headers=headers,
            timeout=30
        )
        if response.status_code == 404:
            return None
        response.raise_for_status()
        return response.json()
        
    except requests.exceptions.RequestException:
        return None