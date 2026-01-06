import os
import pickle
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
from typing import List, Dict, Any

class DocumentRetriever:
    def __init__(self, index_path: str = None, 
                 doc_path: str = None,
                 model_name: str = 'all-MiniLM-L6-v2'):
        
        self.model = SentenceTransformer(model_name)
        
        # Determine paths - try multiple locations for flexibility
        possible_index_paths = [
            "embeddings/faiss_index.bin",
            "../embeddings/faiss_index.bin",
            "./embeddings/faiss_index.bin",
            os.path.join(os.path.dirname(__file__), "..", "embeddings", "faiss_index.bin")
        ]
        
        possible_doc_paths = [
            "embeddings/faiss_index.pkl",
            "../embeddings/faiss_index.pkl",
            "./embeddings/faiss_index.pkl",
            os.path.join(os.path.dirname(__file__), "..", "embeddings", "faiss_index.pkl")
        ]
        
        if index_path is None:
            # Try relative paths from different starting points
            index_path = next((p for p in possible_index_paths if os.path.exists(p)), possible_index_paths[0])
        
        if doc_path is None:
            doc_path = next((p for p in possible_doc_paths if os.path.exists(p)), possible_doc_paths[0])
        
        # Load FAISS index
        if os.path.exists(index_path):
            self.index = faiss.read_index(index_path)
        else:
            raise FileNotFoundError(f"FAISS index not found at {index_path}. Tried: {possible_index_paths}")
        
        # Load documents metadata
        if os.path.exists(doc_path):
            with open(doc_path, 'rb') as f:
                self.documents = pickle.load(f)
        else:
            raise FileNotFoundError(f"Documents metadata not found at {doc_path}. Tried: {possible_doc_paths}")
    
    def retrieve(self, query: str, k: int = 3) -> List[Dict[str, Any]]:
        """Retrieve top-k most relevant documents for the query."""
        # Encode query
        query_embedding = self.model.encode([query])
        
        # Normalize for cosine similarity
        faiss.normalize_L2(query_embedding)
        
        # Search
        scores, indices = self.index.search(query_embedding.astype('float32'), k)
        
        # Get relevant documents
        results = []
        for score, idx in zip(scores[0], indices[0]):
            if idx < len(self.documents):
                doc = self.documents[idx].copy()
                doc['score'] = float(score)
                results.append(doc)
        
        return results

    def get_context(self, query: str, k: int = 3) -> str:
        """Get formatted context from retrieved documents."""
        results = self.retrieve(query, k)
        
        if not results:
            return "No relevant information found."
        
        context_parts = []
        for i, doc in enumerate(results, 1):
            source_name = os.path.basename(doc['source'])
            context_parts.append(f"[Document {i} from {source_name}]:\n{doc['content']}")
        
        return "\n\n".join(context_parts)