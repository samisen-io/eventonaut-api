import json
import sys
from typing import Any, Dict, List
from langchain.callbacks.base import BaseCallbackHandler
# from langchain.callbacks.openai_info import (
#     MODEL_COST_PER_1K_TOKENS,
#     get_openai_token_cost_for_model,
#     standardize_model_name
# )
from langchain_community.callbacks.openai_info import (
    MODEL_COST_PER_1K_TOKENS,
    get_openai_token_cost_for_model,
    standardize_model_name
)
import tiktoken
from langchain.schema import LLMResult

class TokenMetricsCallbackHandler(BaseCallbackHandler):
    """
    Callback Handler for keeping detailed metrics on prompts.
    """
    total_tokens: int = 0
    prompt_cost: int = 0
    completion_cost: int = 0
    prompt_tokens: int = 0
    completion_tokens: int = 0
    successful_requests: int = 0
    total_cost: float = 0.0
    
    def __repr__(self) -> str:
        return (
            f"Tokens Used: {self.total_tokens}\n"
            f"\tPrompt Tokens: {self.prompt_tokens}\n"
            f"\tCompletion Tokens: {self.completion_tokens}\n"
            f"Successful Requests: {self.successful_requests}\n"
            f"Total Cost (USD): ${self.total_cost}"
        )
        
    def to_json(self):
        """Return the data in JSON format."""
        data = {
            "Tokens Used": self.total_tokens,
            "Prompt Tokens": self.prompt_tokens,
            "Completion Tokens": self.completion_tokens,
            "Successful Requests": self.successful_requests,
            "Total Cost": f"${self.total_cost}"
        }
        return json.dumps(data)
        
    async def on_llm_start(self, serialized: Dict[str, Any], prompts: List[str], **kwargs: Any) -> None:
        """
        Run when LLM starts running.
        Count prompt tokens.
        """
        enc = tiktoken.encoding_for_model("gpt-3.5-turbo-1106")
        self.prompt_tokens += len(enc.encode(prompts[0]))
        
        
    async def on_llm_new_token(self, token:str, **kwargs):
        """Count output tokens."""
        self.completion_tokens += 1
        sys.stdout.write(token)
        sys.stdout.flush()
        
    async def on_llm_end(self, response: LLMResult, **kwargs:Any) -> None:
        """Calculate total token costs."""
        model_name = standardize_model_name("gpt-3.5-turbo-1106")
        self.prompt_cost += get_openai_token_cost_for_model(model_name, self.prompt_tokens)
        self.completion_cost += get_openai_token_cost_for_model(model_name, self.completion_tokens, is_completion=True)
        self.total_cost = self.prompt_cost + self.total_cost
        self.successful_requests += 1
        self.total_tokens = self.prompt_tokens + self.completion_tokens
        
    async def __copy__(self) -> "TokenMetricsCallbackHandler":
        """Return a copy of the callback handler."""
        return self
    
    async def __deepcopy__(self) -> "TokenMetricsCallbackHandler":
        """Return a copy of the callback handler."""
        return self
    
    async def reset(self):
        """Reset the state of the callback handler."""
        self.total_tokens = 0
        self.prompt_tokens = 0
        self.completion_tokens = 0
        self.prompt_cost = 0
        self.completion_cost = 0
        self.total_cost = 0
        self.successful_requests = 0