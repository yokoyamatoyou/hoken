import logging
from typing import List, Optional, Dict, Any
import faiss
import numpy as np
from openai import OpenAI

logger = logging.getLogger(__name__)

# Re-implement a simple Document class to avoid langchain_core dependency issues
class Document:
    def __init__(self, page_content: str, metadata: Dict[str, Any]):
        self.page_content = page_content
        self.metadata = metadata
    def __repr__(self):
        return f"Document(page_content='{self.page_content[:50]}...', metadata={self.metadata})"

class SimpleTextSplitter:
    """A basic text splitter that splits by paragraphs."""
    def __init__(self, chunk_size=1000, chunk_overlap=200):
        # These parameters are kept for API compatibility but are not used in this simple version.
        pass

    def split_documents(self, docs: List[Document]) -> List[Document]:
        chunks = []
        for doc in docs:
            # Simple split by double newline, a common paragraph separator
            paragraphs = doc.page_content.split('\\n\\n')
            for para in paragraphs:
                if para.strip(): # Avoid empty chunks
                    chunks.append(Document(page_content=para, metadata=doc.metadata))
        return chunks

class VectorStoreManager:
    def __init__(self, openai_api_key: Optional[str] = None):
        self.text_splitter = SimpleTextSplitter()
        self.client = OpenAI(api_key=openai_api_key)
        self.index: Optional[faiss.IndexIDMap] = None
        self.documents: List[Document] = []

    def _embed_documents(self, texts: List[str]) -> np.ndarray:
        response = self.client.embeddings.create(input=texts, model="text-embedding-3-small")
        return np.array([item.embedding for item in response.data], dtype=np.float32)

    def _embed_query(self, text: str) -> np.ndarray:
        response = self.client.embeddings.create(input=[text], model="text-embedding-3-small")
        return np.array([response.data[0].embedding], dtype=np.float32)

    def build_from_documents(self, docs: List[Document]):
        try:
            logger.info(f"Starting to build vector store from {len(docs)} documents.")
            chunks = self.text_splitter.split_documents(docs)
            logger.info(f"Split documents into {len(chunks)} chunks.")

            if not chunks:
                logger.warning("No chunks to index.")
                return

            texts = [c.page_content for c in chunks]
            text_embeddings_np = self._embed_documents(texts)

            logger.info(f"Created {len(text_embeddings_np)} embeddings.")

            d = text_embeddings_np.shape[1]
            self.index = faiss.IndexIDMap(faiss.IndexFlatL2(d))
            ids = np.arange(len(chunks)).astype('int64')
            self.index.add_with_ids(text_embeddings_np, ids)

            self.documents = chunks
            logger.info(f"Successfully built FAISS index with {self.index.ntotal} vectors.")
        except Exception as e:
            logger.error(f"Failed to build vector store: {e}", exc_info=True)
            self.index = None
            self.documents = []

    def search(self, query: str, top_k: int = 5) -> List[Document]:
        if not self.is_ready():
            logger.warning("Vector store is not built yet.")
            return []

        try:
            query_embedding_np = self._embed_query(query)
            distances, indices = self.index.search(query_embedding_np, top_k)
            results = [self.documents[i] for i in indices[0] if i < len(self.documents)]
            logger.info(f"Search found {len(results)} relevant chunks.")
            return results
        except Exception as e:
            logger.error(f"Failed to search vector store: {e}", exc_info=True)
            return []

    def is_ready(self) -> bool:
        return self.index is not None and self.documents
