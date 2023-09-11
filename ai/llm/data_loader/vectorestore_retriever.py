import asyncio
from functools import partial
from typing import List, Any, Dict, ClassVar, Collection

from langchain.callbacks.manager import AsyncCallbackManagerForRetrieverRun, CallbackManagerForRetrieverRun
from langchain.schema import Document, BaseRetriever
from langchain.vectorstores import VectorStore
from pydantic import root_validator, Field


class CustomVectorStoreRetriever(BaseRetriever):
    """Retriever class for VectorStore."""

    vectorstore: VectorStore
    """VectorStore to use for retrieval."""
    search_type: str = "similarity"
    """Type of search to perform. Defaults to "similarity"."""
    search_kwargs: dict = Field(default_factory=dict)
    """Keyword arguments to pass to the search function."""
    allowed_search_types: ClassVar[Collection[str]] = (
        "similarity",
        "similarity_score_threshold",
        "mmr",
    )

    class Config:
        """Configuration for this pydantic object."""

        arbitrary_types_allowed = True

    @root_validator()
    def validate_search_type(cls, values: Dict) -> Dict:
        """Validate search type."""
        search_type = values["search_type"]
        if search_type not in cls.allowed_search_types:
            raise ValueError(
                f"search_type of {search_type} not allowed. Valid values are: " f"{cls.allowed_search_types}"
            )
        if search_type == "similarity_score_threshold":
            score_threshold = values["search_kwargs"].get("score_threshold")
            if (score_threshold is None) or (not isinstance(score_threshold, float)):
                raise ValueError("`score_threshold` is not specified with a float value(0~1) " "in `search_kwargs`.")
        return values

    def _get_relevant_documents(self, query: str, *, run_manager: CallbackManagerForRetrieverRun) -> List:
        if self.search_type == "similarity":
            docs_with_scores = self.vectorstore.similarity_search_with_score(query, **self.search_kwargs)
        elif self.search_type == "similarity_score_threshold":
            docs_with_scores = self.vectorstore.similarity_search_with_relevance_scores(query, **self.search_kwargs)

        elif self.search_type == "mmr":
            embedding = self.vectorstore._embedding_function.embed_query(query)
            docs_with_scores = self.vectorstore.max_marginal_relevance_search_with_score_by_vector(
                embedding, **self.search_kwargs
            )
        else:
            raise ValueError(f"search_type of {self.search_type} not allowed.")

        return docs_with_scores