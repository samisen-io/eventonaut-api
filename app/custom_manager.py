
from contextlib import contextmanager
from contextvars import ContextVar
from typing import (
    Generator,
    Optional,
)

from app.custom_handler import TokenMetricsCallbackHandler

# from custom_handler import CustomCallbackHandler

openai_callback_var: ContextVar[Optional[TokenMetricsCallbackHandler]] = ContextVar(
    "openai_callback", default=None
)

@contextmanager
def custom_get_openai_callback() -> Generator[TokenMetricsCallbackHandler, None, None]:
    """Get the custom OpenAI callback handler."""
    callback = TokenMetricsCallbackHandler()
    openai_callback_var.set(callback)
    yield callback
    openai_callback_var.set(None)