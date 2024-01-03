"""Callback handlers used in the app."""
import logging
import os
from typing import Any, Dict, List
from uuid import UUID

import tiktoken
from langchain.callbacks.base import AsyncCallbackHandler
from langchain.schema import LLMResult

class StreamingLLMCallbackHandler(AsyncCallbackHandler):
    """Callback handler for streaming LLM responses."""

    def __init__(self):
        self.llm_encoding = tiktoken.encoding_for_model("gpt-3.5-turbo")
        self.prompt_tokens = 0
        self.completion_tokens = 0
        self.total_tokens = 0

    async def on_llm_start(self, serialized: Dict[str, Any], prompts: List[str], **kwargs: Any) -> None:
        self.prompt_tokens = len(self.llm_encoding.encode(prompts[0]))

    async def on_llm_end(self, response: LLMResult, *, run_id: UUID, parent_run_id: UUID = None, **kwargs: Any) -> None:
        output = response.dict()["generations"][0][0]["text"]
        self.completion_tokens = len(self.llm_encoding.encode(output))
        self.total_tokens = self.prompt_tokens + self.completion_tokens

        logging.info(f"Response: {output}")
        logging.info(
            f"Tokens used: {self.completion_tokens + self.prompt_tokens}"
            f"(Prompt tokens: {self.prompt_tokens}; Completion tokens: {self.completion_tokens})"
        )
