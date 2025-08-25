# custos/__init__.py
from __future__ import annotations

__version__ = "0.2.5"

# Public exceptions/utilities
from .exceptions import AlignmentViolation
from .ethics import EthicsRegistry
from .training import FeedbackTrainer
from .guardian import CustosGuardian  

# Config + raw client access
from .config import CustosConfig
from .client import AutoLoggingGuardian
from .bootstrap import custos_bootstrap

# Simple config shims (as before)
_cfg = CustosConfig()

def set_api_key(raw_key: str) -> None:
    _cfg.api_key = raw_key

def set_backend_url(url: str) -> None:
    _cfg.backend_url = url.rstrip("/")

def guardian_client() -> AutoLoggingGuardian:
    """
    Raw client (advanced): direct access to post heartbeats/response beats.
    """
    g = custos_bootstrap()
    if g is not None:
        return g
    return AutoLoggingGuardian(_cfg)

# 🟢 NOTE: The ONE-LINER wrapper users will import.
# Usage:
#   from custos import guardian
#   safe = guardian()(model_fn)
from ._wrap import guardian  # <- this is the simple wrapper factory

__all__ = [
    "AlignmentViolation",
    "EthicsRegistry",
    "FeedbackTrainer",
    "CustosGuardian",
    "CustosConfig",
    "AutoLoggingGuardian",
    "set_api_key",
    "set_backend_url",
    "guardian",         
    "guardian_client",   
]
