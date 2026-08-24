import os
from typing import List, Dict, Any
import chromadb
from chromadb.utils import embedding_functions
from sentence_transformers import CrossEncoder

class EnterpriseDataFabricRAG:
    def __init__(self, collection_name: str = "aramco_audit_logs"):
        self.chroma_client = chromadb.PersistentClient(path="./enterprise_vector_db")
        self.embedding_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name="all-MiniLM-L6-v2"
        )
        self.collection = self.chroma_client.get_or_create_collection(
            name=collection_name, 
            embedding_function=self.embedding_fn
        )
        self.reranker = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2")

    def ingest_unstructured_document(self, doc_id: str, text: str, sap_metadata: Dict[str, Any]):
        chunks = [text[i:i+500] for i in range(0, len(text), 400)]
        ids = [f"{doc_id}_chunk_{idx}" for idx in range(len(chunks))]
        metadatas = [sap_metadata for _ in range(len(chunks))]
        
        self.collection.add(
            documents=chunks,
            ids=ids,
            metadatas=metadatas
        )
        print(f"📦 Successfully indexed {len(chunks)} chunks for {doc_id} into Data Fabric.")

    def contextual_semantic_search(self, user_query: str, region_filter: str = None, top_k: int = 5) -> List[Dict[str, Any]]:
        where_clause = {"region": region_filter} if region_filter else None
        
        results = self.collection.query(
            query_texts=[user_query],
            n_results=top_k * 2,
            where=where_clause
        )
        
        if not results or not results['documents'] or not results['documents'][0]:
            return []
            
        fetched_chunks = results['documents'][0]
        fetched_metadata = results['metadatas'][0]
        
        pairs = [[user_query, chunk] for chunk in fetched_chunks]
        scores = self.reranker.predict(pairs)
        
        reranked_results = []
        for idx, score in enumerate(scores):
            reranked_results.append({
                "text": fetched_chunks[idx],
                "sap_metadata": fetched_metadata[idx],
                "confidence_score": float(round(score, 4))
            })
            
        return sorted(reranked_results, key=lambda x: x["confidence_score"], reverse=True)[:top_k]
