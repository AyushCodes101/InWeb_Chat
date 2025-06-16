import numpy as np
import faiss
import json
import os
import tiktoken
from openai import OpenAI
import httpx
from typing import List, Dict
import pickle

class FAISSIndexer:
    def __init__(self, model_name="gpt-4"):
        self.model_name = model_name
        self.tokenizer = tiktoken.encoding_for_model(model_name)
        self.data_dir = "data"
        self.index_file = os.path.join(self.data_dir, "faiss_index.pkl")
        self.metadata_file = os.path.join(self.data_dir, "metadata.pkl")
        
        # Create data directory if it doesn't exist
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)
            
        # Configure custom HTTP client
        http_client = httpx.Client()
        
        # Initialize OpenAI client with custom HTTP client
        self.client = OpenAI(
            api_key=os.getenv("OPENAI_API_KEY"),
            http_client=http_client
        )
        
        # Initialize storage for text chunks and their metadata
        self.chunks: List[str] = []
        self.metadata: List[Dict] = []
        
    def create_embeddings(self, text: str) -> np.ndarray:
        """Create embeddings for text using OpenAI's API."""
        try:
            response = self.client.embeddings.create(
                input=text,
                model="text-embedding-ada-002"
            )
            return np.array(response.data[0].embedding, dtype=np.float32)
        except Exception as e:
            print(f"Error creating embedding: {str(e)}")
            return np.zeros(1536, dtype=np.float32)  # Default embedding dimension

    def chunk_text(self, text: str, max_tokens: int = 500) -> List[str]:
        """Split text into chunks that don't exceed max_tokens."""
        tokens = self.tokenizer.encode(text)
        chunks = []
        current_chunk = []
        current_length = 0
        
        for token in tokens:
            current_chunk.append(token)
            current_length += 1
            
            if current_length >= max_tokens:
                chunks.append(self.tokenizer.decode(current_chunk))
                current_chunk = []
                current_length = 0
                
        if current_chunk:
            chunks.append(self.tokenizer.decode(current_chunk))
            
        return chunks

    def build_index(self, scraped_data: List[Dict]):
        """Build FAISS index from scraped data if not already built."""
        if os.path.exists(self.index_file) and os.path.exists(self.metadata_file):
            print("Index already exists. Skipping indexing.")
            return self.load_index()

        print("Building FAISS index...")
        embeddings_list = []

        for page in scraped_data:
            # Combine title, meta description, and content
            full_text = f"{page['title']} {page['meta_description']} {page['content']}"
            
            # Split text into chunks
            text_chunks = self.chunk_text(full_text)
            
            for chunk in text_chunks:
                # Create embedding for chunk
                embedding = self.create_embeddings(chunk)
                embeddings_list.append(embedding)
                
                # Store chunk and metadata
                self.chunks.append(chunk)
                self.metadata.append({
                    'url': page['url'],
                    'title': page['title']
                })

        # Create and populate FAISS index
        embeddings_array = np.array(embeddings_list)
        dimension = embeddings_array.shape[1]
        index = faiss.IndexFlatL2(dimension)
        index.add(embeddings_array)

        # Save index and metadata
        self.save_index(index)
        return index

    def save_index(self, index):
        """Save FAISS index and metadata to disk."""
        with open(self.index_file, 'wb') as f:
            pickle.dump(index, f)
        
        with open(self.metadata_file, 'wb') as f:
            pickle.dump({
                'chunks': self.chunks,
                'metadata': self.metadata
            }, f)

    def load_index(self):
        """Load FAISS index and metadata from disk."""
        with open(self.index_file, 'rb') as f:
            index = pickle.load(f)
            
        with open(self.metadata_file, 'rb') as f:
            data = pickle.load(f)
            self.chunks = data['chunks']
            self.metadata = data['metadata']
            
        return index

    def search(self, query: str, k: int = 5):
        """Search for similar content using the query."""
        # Create query embedding
        query_embedding = self.create_embeddings(query)
        
        # Load index
        index = self.load_index()
        
        # Search index
        D, I = index.search(query_embedding.reshape(1, -1), k)
        
        results = []
        for idx in I[0]:
            if idx < len(self.chunks):
                results.append({
                    'chunk': self.chunks[idx],
                    'metadata': self.metadata[idx]
                })
                
        return results 