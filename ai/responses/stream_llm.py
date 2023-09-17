"""
Credits:
- https://gist.github.com/ninely/88485b2e265d852d3feb8bd115065b1a
- https://github.com/hwchase17/langchain/discussions/1706
"""
import enum
import functools
from typing import Any, Awaitable, Callable, Dict, Optional, Union

from fastapi.responses import StreamingResponse
from langchain.chains.base import Chain
from langchain.chains.conversational_retrieval.base import BaseConversationalRetrievalChain
from starlette.background import BackgroundTask
from starlette.types import Send

from ai.callback.stream_callback import AsyncRetrievalQAStreamingCallback

@enum.unique
class SignatureStatus(enum.IntEnum):
    CONTINUE = 0
    CONSIDER = 1
    STOP = 2


class SignatureHandler:
    def __init__(self):
        self.token_checking = ""
        self.is_stop = False
        self.start_marker = ".\n\n"
        self.end_marker = ",\n"

    def get_signature_status(self) -> int:
        token_checking = self.token_checking.strip(" ").lower()
        if len(token_checking) < 30:
            if token_checking.endswith(self.end_marker):
                return SignatureStatus.STOP.value
            if token_checking.startswith(self.start_marker):
                return SignatureStatus.CONSIDER.value
        return SignatureStatus.CONTINUE.value

class BaseLangchainStreamingResponse(StreamingResponse):
    """Base StreamingResponse class wrapper for langchain chains."""

    def __init__(
        self,
        chain_executor: Callable[[Send], Awaitable[Any]],
        background: Optional[BackgroundTask] = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(content=iter(()), background=background, **kwargs)

        self.chain_executor = chain_executor

    async def stream_response(self, send: Send) -> None:
        await send(
            {
                "type": "http.response.start",
                "status": self.status_code,
                "headers": self.raw_headers,
            }
        )

        async def send_token(token: Union[str, bytes], signature_handler: SignatureHandler):
            if isinstance(token, bytes):
                await send({"type": "http.response.body", "body": token, "more_body": True})
            else:
                if signature_handler.is_stop:
                    return

                if signature_handler.get_signature_status() == SignatureStatus.STOP.value:
                    signature_handler.is_stop = True
                    await send({"type": "http.response.body", "body": ".", "more_body": True})
                else:
                    signature_handler.token_checking += token
                    if signature_handler.get_signature_status() in (
                        SignatureStatus.CONSIDER.value,
                        SignatureStatus.STOP.value,
                    ):
                        await send({"type": "http.response.body", "body": "", "more_body": True})
                    else:
                        token = signature_handler.token_checking.encode(self.charset)
                        signature_handler.token_checking = ""
                        await send({"type": "http.response.body", "body": token, "more_body": True})

        try:
            send_token_partial = functools.partial(send_token, signature_handler=SignatureHandler())
            outputs = await self.chain_executor(send_token_partial)
            if self.background is not None:
                self.background.kwargs["outputs"] = outputs
        except Exception as e:
            if self.background is not None:
                self.background.kwargs["outputs"] = str(e)
            await send(
                {
                    "type": "http.response.body",
                    "body": "".encode(self.charset),
                    "more_body": False,
                }
            )
            return

        await send({"type": "http.response.body", "body": b"", "more_body": False})

    @staticmethod
    def _create_chain_executor(chain: Chain, inputs: Union[Dict[str, Any], Any]) -> Callable[[Send], Awaitable[Any]]:
        raise NotImplementedError

    @classmethod
    def from_chain(
        cls,
        chain: Chain,
        inputs: Union[Dict[str, Any], Any],
        background: Optional[BackgroundTask] = None,
        **kwargs: Any,
    ) -> "BaseLangchainStreamingResponse":
        chain_executor = cls._create_chain_executor(chain, inputs)

        return cls(
            chain_executor=chain_executor,
            background=background,
            **kwargs,
        )
    
class ConversationalRetrievalStreamingResponse(BaseLangchainStreamingResponse):
    """BaseLangchainStreamingResponse class wrapper for ConversationalRetrievalStreamingResponse instances."""

    @staticmethod
    def _create_chain_executor(
        chain: BaseConversationalRetrievalChain, inputs: Union[Dict[str, Any], Any]
    ) -> Callable[[Send], Awaitable[Any]]:
        async def wrapper(send: Send):
            result = await chain.acall(inputs=inputs, callbacks=[AsyncRetrievalQAStreamingCallback(send=send)])

            return result

        return wrapper
