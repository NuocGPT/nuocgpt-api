"""Callback handlers used in the app."""

from typing import Any, Dict

import langchain
from langchain.callbacks.base import AsyncCallbackHandler
from pydantic import BaseModel, Field
from starlette.types import Send

SOURCE_DOCUMENT_TEMPLATE = """
page content: {page_content}
source: {source}
"""


class AsyncStreamingResponseCallback(AsyncCallbackHandler, BaseModel):
    """Async Callback handler for FastAPI StreamingResponse."""

    send: Send = Field(...)

    @property
    def always_verbose(self) -> bool:
        """Whether to call verbose callbacks even if verbose is False."""
        return True


class AsyncLLMChainStreamingCallback(AsyncStreamingResponseCallback):
    """AsyncStreamingResponseCallback handler for LLMChain."""

    async def on_llm_new_token(self, token: str, **kwargs: Any) -> None:
        """Run on new LLM token. Only available when streaming is enabled."""
        await self.send(token)


class AsyncRetrievalQAStreamingCallback(AsyncLLMChainStreamingCallback):
    """AsyncStreamingResponseCallback handler for RetrievalQA."""

    source_document_template: str = SOURCE_DOCUMENT_TEMPLATE

    async def on_chain_end(self, outputs: Dict[str, Any], **kwargs: Any) -> None:
        """Run when chain ends running."""
        if langchain.llm_cache is not None and "answer" in outputs:
            await self.send(outputs["answer"])
        if "source_documents" in outputs:
            await self.send("\n\nSOURCE DOCUMENTS: \n")
            for document in outputs["source_documents"]:
                await self.send(
                    self.source_document_template.format(
                        page_content=document.page_content,
                        source=document.metadata["source"],
                    )
                )
