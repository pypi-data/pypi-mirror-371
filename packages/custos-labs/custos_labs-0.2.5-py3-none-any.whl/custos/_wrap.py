# custos/_wrap.py
from __future__ import annotations
import inspect
from typing import Any, Callable, Optional

from .bootstrap import custos_bootstrap
from .client import AutoLoggingGuardian
from .config import CustosConfig
from .exceptions import AlignmentViolation

def _ensure_client() -> AutoLoggingGuardian:
    # Prefer singleton from env; fall back to local client so heartbeats still work.
    g = custos_bootstrap()
    return g if g is not None else AutoLoggingGuardian(CustosConfig())

def _prompt_from(args, kwargs) -> str:
    # Common shapes: prompt="...", or messages=[{role,content},...], else best effort.
    if args and isinstance(args[0], str): 
        return args[0]
    p = kwargs.get("prompt")
    if isinstance(p, str):
        return p
    msgs = kwargs.get("messages")
    if isinstance(msgs, list):
        try:
            return "\n".join(f"{m.get('role','user')}: {m.get('content','')}" for m in msgs if isinstance(m, dict))
        except Exception:
            pass
    return str(p or args or kwargs)

def _resp_from(out: Any) -> str:
    # String, dict (OpenAI-like, Hugging Face), or object with .text/.content — otherwise str(out).
    if isinstance(out, str):
        return out
    if isinstance(out, dict):
        # OpenAI chat
        try:
            return out["choices"][0]["message"]["content"]
        except Exception:
            pass
        for k in ("text", "content", "generated_text", "summary_text", "reply", "output", "response"):
            v = out.get(k)
            if isinstance(v, str):
                return v
    for attr in ("text", "content"):
        if hasattr(out, attr) and isinstance(getattr(out, attr), str):
            return getattr(out, attr)
    return str(out)

class _WrapperFactory:
    """
    guardian(...options) -> wrapper you can apply to any callable:
      safe = guardian()(model_fn)
      safe = guardian(on_violation="replace", fallback="(redacted)")(obj, method="generate")
    """
    def __init__(self, *, on_violation: str = "raise", fallback: str = "I can’t help with that."):
        self.client = _ensure_client()
        self.on_violation = on_violation
        self.fallback = fallback

    def __call__(self, target: Any, *, method: Optional[str] = None) -> Callable[..., Any]:
        fn = getattr(target, method) if method else target
        if not callable(fn):
            raise TypeError("guardian(...) expects a callable or pass method='name'")

        if inspect.iscoroutinefunction(fn):
            async def wrapped(*a, **k):
                prompt = _prompt_from(a, k)
                out = await fn(*a, **k)
                resp = _resp_from(out)
                try:
                    self.client.evaluate(prompt, resp)
                    return out
                except AlignmentViolation:
                    if self.on_violation == "replace": return self.fallback
                    if self.on_violation == "return_none": return None
                    raise
            return wrapped

        def wrapped(*a, **k):
            prompt = _prompt_from(a, k)
            out = fn(*a, **k)
            resp = _resp_from(out)
            try:
                self.client.evaluate(prompt, resp)
                return out
            except AlignmentViolation:
                if self.on_violation == "replace": return self.fallback
                if self.on_violation == "return_none": return None
                raise
        return wrapped

def guardian(*, on_violation: str = "raise", fallback: str = "I can’t help with that.") -> _WrapperFactory:
    """
    Public API:
      from custos import guardian
      custos.set_api_key("...")  # or env
      safe = guardian()(model_fn)
    """
    # Ensure heartbeats start as soon as a wrapper is created
    _ensure_client().start_heartbeats()
    return _WrapperFactory(on_violation=on_violation, fallback=fallback)
