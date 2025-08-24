"""
simpleVibe - A simple Python library that interfaces with Llama LLM

This package provides a simple interface to Llama LLM models. It can operate in two modes:
- Remote mode: Uses an API to communicate with a remote Llama LLM server (default)
- Local mode: Runs inference locally using transformers (requires extra dependencies)

To use local inference, install with: pip install simplevibe[local]
For remote inference, just use: pip install simplevibe
"""

__version__ = '0.1.2'

import importlib.util
import sys

# Allow users to control backend preference via environment variable
import os

# Check if all necessary local dependencies are available
def _check_local_deps():
    try:
        import transformers
        import torch
        import accelerate
        import bitsandbytes
        return True
    except ImportError:
        return False

# Allow users to force a specific backend
FORCE_BACKEND = os.environ.get('SIMPLEVIBE_BACKEND', '').lower()
HAS_LOCAL_DEPS = _check_local_deps()

# Always import llama3 from api for direct access
from .api import llama3

# Determine which backend to use
if FORCE_BACKEND == 'remote':
    # User explicitly requested remote backend
    _backend = 'remote'
elif FORCE_BACKEND == 'local':
    # User explicitly requested local backend
    if HAS_LOCAL_DEPS:
        try:
            from .vibe_source import ManifestVibes
            _backend = 'local'
        except ImportError:
            # Fallback if local is forced but has issues
            _backend = 'remote'
            print("WARNING: Local backend was requested but couldn't be initialized. Falling back to remote.")
    else:
        _backend = 'remote'
        print("WARNING: Local backend was requested but dependencies are missing. Falling back to remote.")
else:
    # Auto-detect based on dependencies (default behavior)
    if HAS_LOCAL_DEPS:
        try:
            from .vibe_source import ManifestVibes
            _backend = 'local'
        except ImportError:
            # Fallback to remote if any issues with local dependencies
            _backend = 'remote'
    else:
        _backend = 'remote'

def create_client(**kwargs):
    """
    Creates a client to interact with Llama LLM.
    
    Returns either a ManifestVibes instance (local) or a function to call the API (remote)
    depending on installed dependencies and user preference.
    
    If local dependencies are installed but there's an issue initializing the local model,
    falls back to remote mode automatically.
    
    You can force a specific backend by:
    1. Setting the SIMPLEVIBE_BACKEND environment variable to 'local' or 'remote'
    2. Using the set_backend('local'|'remote') function before calling create_client()
    """
    # Re-check environment variable in case it was changed after module import
    force_backend = os.environ.get('SIMPLEVIBE_BACKEND', '').lower()
    
    # Determine which backend to use right now
    use_local = False
    
    if force_backend == 'local':
        # User wants local, try to use it if possible
        use_local = HAS_LOCAL_DEPS
    elif force_backend == 'remote':
        # User wants remote, don't use local even if available
        use_local = False
    else:
        # Default behavior based on what was detected at import time
        use_local = _backend == 'local'
    
    if use_local:
        try:
            return ManifestVibes(**kwargs)
        except Exception as e:
            import warnings
            warnings.warn(f"Failed to initialize local model: {str(e)}. Falling back to remote API.")
            # Fall back to remote API
            def api_client(**call_kwargs):
                return llama3(**call_kwargs)
            return api_client
    else:
        # Return a function that will forward all arguments to llama3
        def api_client(**call_kwargs):
            return llama3(**call_kwargs)
        return api_client

def get_backend_type():
    """
    Returns the current backend type: 'local' or 'remote'
    
    Users can override the backend selection by setting the SIMPLEVIBE_BACKEND
    environment variable to 'local' or 'remote'.
    """
    return _backend

def set_backend(backend_type):
    """
    Set the preferred backend type for this session.
    
    This is an alternative to using the SIMPLEVIBE_BACKEND environment variable.
    Note that this will only affect future calls to create_client().
    
    Args:
        backend_type (str): Either 'local' or 'remote'
        
    Returns:
        bool: True if backend was set successfully, False otherwise
    """
    global FORCE_BACKEND
    
    if backend_type.lower() not in ['local', 'remote']:
        print(f"Invalid backend type: {backend_type}. Must be 'local' or 'remote'.")
        return False
    
    FORCE_BACKEND = backend_type.lower()
    os.environ['SIMPLEVIBE_BACKEND'] = FORCE_BACKEND
    
    print(f"Backend preference set to: {FORCE_BACKEND}")
    print("Note: This will take effect on the next call to create_client()")
    return True

# Ensure direct access to raw API function
__all__ = ['create_client', 'get_backend_type', 'set_backend', 'llama3']
