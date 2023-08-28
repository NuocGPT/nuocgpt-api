import logging
import os
import backoff

from typing import List, Text

import openai

from langchain.document_loaders import PyPDFium2Loader
from langchain.text_splitter import TokenTextSplitter
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores import Chroma

from llama_index import download_loader

from core.constants import IngestDataConstants

@backoff.on_exception(backoff.expo, openai.error.RateLimitError)
def openai_embedding_with_backoff():
    return OpenAIEmbeddings(chunk_size=IngestDataConstants.CHUNK_OVERLAP)

class DataIngestor:
    """Ingest data with different format to create vectorstore"""
    def __init__(self, lang: str = ""):
        self.lang = lang
        self.vectorstore_folder_path = f"vectorstores/{self.lang}"

    def create_vectorstore(self) -> Text:
        vectorstore_path = ""
        try:
            vectorstore_path = os.path.join(IngestDataConstants.ROOT_PATH, f"{self.vectorstore_folder_path}/")
            if not os.path.exists(vectorstore_path):
                os.makedirs(vectorstore_path)
        except Exception as e:
            logging.exception(e)
        finally:
            return vectorstore_path
        
    def _save_vectorstore(self, raw_documents: List, vectorstore_path: Text):
        text_splitter = TokenTextSplitter(
            model_name="gpt-3.5-turbo",
            chunk_size=IngestDataConstants.CHUNK_SIZE,
            chunk_overlap=IngestDataConstants.CHUNK_OVERLAP,
        )

        splitted_documents = text_splitter.split_documents(raw_documents)
        embeddings = openai_embedding_with_backoff()

        vectorstore = Chroma(persist_directory=vectorstore_path, embedding_function=embeddings)
        vectorstore.add_documents(splitted_documents)
        vectorstore.persist()
        
    def ingest_pdf(self, pdf_path: Text):
        vectorstore_path = self.create_vectorstore()

        loader = PyPDFium2Loader(pdf_path)
        raw_documents = loader.load()

        num_of_pages = 0
        text_length = 0
        if len(raw_documents) > 0:
            num_of_pages = raw_documents[-1].metadata["page"] + 1
            for doc in raw_documents:
                text_length += len(doc.page_content)

        self._save_vectorstore(raw_documents, vectorstore_path)

        return {"num_of_pages": num_of_pages, "text_length": text_length}
    
    def ingest_json(self, json_path: list):
        vectorstore_path = self.create_vectorstore()

        JSONReader = download_loader("JSONReader")
        loader = JSONReader()
        documents = loader.load_data(json_path)
        raw_documents = [d.to_langchain_format() for d in documents]

        self._save_vectorstore(raw_documents, vectorstore_path)
