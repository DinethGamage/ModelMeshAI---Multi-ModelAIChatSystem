"""
RAG (Retrieval-Augmented Generation) pipeline for document-based Q&A.
Handles PDF processing, embedding, storage, and retrieval.
"""

import os
from typing import List, Dict, Any, Optional
from pathlib import Path

import chromadb
from chromadb.config import Settings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma

from app.config import config
from app.models import model_manager


class RAGPipeline:
    """Complete RAG pipeline for document processing and retrieval."""
    
    def __init__(self, session_id: str):
        """
        Initialize RAG pipeline for a specific session.
        
        Args:
            session_id: Unique session identifier for isolating documents
        """
        self.session_id = session_id
        self.collection_name = f"session_{session_id}"
        
        # Initialize embeddings
        self.embeddings = HuggingFaceEmbeddings(
            model_name=config.EMBEDDING_MODEL,
            model_kwargs={'device': 'cpu'},
            encode_kwargs={'normalize_embeddings': True}
        )
        
        # Initialize text splitter
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=config.CHUNK_SIZE,
            chunk_overlap=config.CHUNK_OVERLAP,
            length_function=len,
            separators=["\n\n", "\n", " ", ""]
        )
        
        # Vector store will be initialized when needed
        self.vector_store: Optional[Chroma] = None
    
    def _get_vectorstore_path(self) -> str:
        """Get the path for this session's vector store."""
        path = os.path.join(config.VECTOR_STORE_PATH, self.collection_name)
        os.makedirs(path, exist_ok=True)
        return path
    
    def extract_text_from_pdf(self, pdf_path: str) -> List[str]:
        """
        Extract text from a PDF file.
        
        Args:
            pdf_path: Path to the PDF file
            
        Returns:
            List of text chunks
        """
        loader = PyPDFLoader(pdf_path)
        documents = loader.load()
        
        # Split documents into chunks
        chunks = self.text_splitter.split_documents(documents)
        
        # Extract text content
        text_chunks = [chunk.page_content for chunk in chunks]
        
        return text_chunks
    
    def store_document(self, pdf_path: str) -> int:
        """
        Process and store a PDF document in the vector store.
        
        Args:
            pdf_path: Path to the PDF file
            
        Returns:
            Number of chunks stored
        """
        # Extract and chunk text
        text_chunks = self.extract_text_from_pdf(pdf_path)
        
        if not text_chunks:
            raise ValueError("No text extracted from PDF")
        
        # Create or update vector store
        persist_directory = self._get_vectorstore_path()
        
        self.vector_store = Chroma.from_texts(
            texts=text_chunks,
            embedding=self.embeddings,
            persist_directory=persist_directory,
            collection_name=self.collection_name
        )
        
        return len(text_chunks)
    
    def retrieve_context(self, query: str, top_k: Optional[int] = None) -> List[str]:
        """
        Retrieve relevant context for a query.
        
        Args:
            query: User query
            top_k: Number of chunks to retrieve (defaults to config value)
            
        Returns:
            List of relevant text chunks
        """
        if not self.vector_store:
            # Try to load existing vector store
            persist_directory = self._get_vectorstore_path()
            
            if not os.path.exists(persist_directory):
                return []
            
            try:
                self.vector_store = Chroma(
                    persist_directory=persist_directory,
                    embedding_function=self.embeddings,
                    collection_name=self.collection_name
                )
            except Exception:
                return []
        
        # Perform similarity search
        k = top_k or config.TOP_K_RETRIEVAL
        results = self.vector_store.similarity_search(query, k=k)
        
        # Extract text content
        contexts = [doc.page_content for doc in results]
        
        return contexts
    
    def generate_answer(self, query: str, contexts: List[str]) -> str:
        """
        Generate an answer using retrieved contexts.
        
        Args:
            query: User query
            contexts: Retrieved context chunks
            
        Returns:
            Generated answer
        """
        if not contexts:
            return "I don't have any document context to answer this question. Please upload a PDF document first."
        
        # Construct prompt with context
        context_text = "\n\n".join([f"Context {i+1}:\n{ctx}" for i, ctx in enumerate(contexts)])
        
        prompt = f"""You are a helpful assistant answering questions based on provided document context.

CONTEXT FROM DOCUMENT:
{context_text}

USER QUESTION:
{query}

INSTRUCTIONS:
- Answer the question using ONLY the information from the context above
- If the context doesn't contain enough information to fully answer, say so
- Be specific and cite relevant parts of the context
- Do not make up or infer information not present in the context

ANSWER:"""
        
        # Generate answer using document model
        model = model_manager.get_model("document")
        response = model.invoke(prompt)
        
        return response.content
    
    def query(self, query: str) -> Dict[str, Any]:
        """
        Complete RAG query: retrieve context and generate answer.
        
        Args:
            query: User query
            
        Returns:
            Dictionary with answer, contexts, and metadata
        """
        # Retrieve relevant contexts
        contexts = self.retrieve_context(query)
        
        # Generate answer
        answer = self.generate_answer(query, contexts)
        
        return {
            "answer": answer,
            "contexts": contexts,
            "num_contexts": len(contexts),
        }


class RAGManager:
    """Manages RAG pipelines for multiple sessions."""
    
    def __init__(self):
        """Initialize the RAG manager."""
        self._pipelines: Dict[str, RAGPipeline] = {}
    
    def get_pipeline(self, session_id: str) -> RAGPipeline:
        """
        Get or create a RAG pipeline for a session.
        
        Args:
            session_id: Session identifier
            
        Returns:
            RAG pipeline instance
        """
        if session_id not in self._pipelines:
            self._pipelines[session_id] = RAGPipeline(session_id)
        
        return self._pipelines[session_id]
    
    def remove_pipeline(self, session_id: str) -> None:
        """
        Remove a RAG pipeline and clean up resources.
        
        Args:
            session_id: Session identifier
        """
        if session_id in self._pipelines:
            del self._pipelines[session_id]


# Global RAG manager instance
rag_manager = RAGManager()
