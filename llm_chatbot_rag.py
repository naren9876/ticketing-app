"""
LLM Chatbot with RAG (Retrieval-Augmented Generation)
Module 17: Generative AI & LLMOps
Covers: LLM integration, RAG, vector database, prompt engineering, LLM monitoring
"""

import numpy as np
import pandas as pd
from typing import List, Dict, Any, Tuple
from datetime import datetime
import logging
import json
from abc import ABC, abstractmethod
import hashlib

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ==================== Vector Database (ChromaDB-like) ====================

class SimpleVectorStore:
    """
    Simple in-memory vector store for RAG
    In production: Use ChromaDB, Pinecone, or Weaviate
    """
    
    def __init__(self):
        self.documents = []
        self.embeddings = []
        self.metadata = []
    
    def add_document(self, text: str, embedding: np.ndarray, metadata: Dict[str, Any]):
        """Add document with embedding"""
        self.documents.append(text)
        self.embeddings.append(embedding)
        self.metadata.append(metadata)
        logger.info(f"Added document: {metadata.get('title', 'Unknown')}")
    
    def search(self, query_embedding: np.ndarray, top_k: int = 3) -> List[Tuple[str, float, Dict]]:
        """
        Search for similar documents
        
        Returns: List of (document, similarity_score, metadata)
        """
        if not self.embeddings:
            return []
        
        # Calculate similarity scores (cosine similarity)
        similarities = []
        for embedding in self.embeddings:
            # Normalize vectors
            norm_query = query_embedding / (np.linalg.norm(query_embedding) + 1e-8)
            norm_embedding = embedding / (np.linalg.norm(embedding) + 1e-8)
            
            # Cosine similarity
            similarity = np.dot(norm_query, norm_embedding)
            similarities.append(similarity)
        
        # Get top K
        top_indices = np.argsort(similarities)[-top_k:][::-1]
        
        results = [
            (self.documents[i], similarities[i], self.metadata[i])
            for i in top_indices
        ]
        
        return results


# ==================== Embedding Generator ====================

class EmbeddingGenerator:
    """
    Generate embeddings for text
    In production: Use OpenAI, Sentence Transformers, etc.
    """
    
    def __init__(self, embedding_dim: int = 128):
        self.embedding_dim = embedding_dim
    
    def embed(self, text: str) -> np.ndarray:
        """
        Generate embedding for text
        Mock implementation - in production use real embeddings
        """
        # Hash-based deterministic embedding (for demo)
        hash_object = hashlib.md5(text.encode())
        hash_int = int(hash_object.hexdigest(), 16)
        np.random.seed(hash_int % (2**31))
        
        embedding = np.random.randn(self.embedding_dim).astype(np.float32)
        embedding = embedding / (np.linalg.norm(embedding) + 1e-8)
        
        return embedding
    
    def embed_batch(self, texts: List[str]) -> List[np.ndarray]:
        """Generate embeddings for multiple texts"""
        return [self.embed(text) for text in texts]


# ==================== LLM Interface ====================

class LLMInterface(ABC):
    """Abstract interface for LLM"""
    
    @abstractmethod
    def generate(self, prompt: str, **kwargs) -> str:
        pass


class MockLLM(LLMInterface):
    """
    Mock LLM for demonstration
    In production: Use OpenAI, Anthropic, local LLMs, etc.
    """
    
    def __init__(self, model_name: str = "gpt-3.5-turbo"):
        self.model_name = model_name
        self.call_count = 0
        self.total_tokens = 0
    
    def generate(
        self,
        prompt: str,
        max_tokens: int = 500,
        temperature: float = 0.7,
        **kwargs
    ) -> str:
        """
        Generate response from LLM
        
        Args:
            prompt: Input prompt
            max_tokens: Maximum tokens in response
            temperature: Sampling temperature
            
        Returns:
            Generated response
        """
        self.call_count += 1
        
        # Mock response generation
        responses = {
            "hello": "Hello! Welcome to Movie Ticketing Support. How can I help you today?",
            "price": "Movie tickets are typically priced between $10-$15 depending on the movie and time.",
            "refund": "We offer full refunds for cancellations made at least 24 hours before showtime.",
            "booking": "To book tickets, go to our website or app, select a movie, choose your seats, and complete payment.",
            "premium": "Premium membership includes discounts, early booking access, and exclusive content.",
            "default": "I understand your question about {query}. Let me help you with that."
        }
        
        # Simple keyword matching for mock responses
        query_lower = prompt.lower()
        for keyword, response in responses.items():
            if keyword in query_lower:
                self.total_tokens += len(response.split())
                return response
        
        # Default response
        self.total_tokens += 50
        return responses["default"].format(query=prompt[:50])


# ==================== RAG Chatbot ====================

class RAGChatbot:
    """
    RAG (Retrieval-Augmented Generation) Chatbot
    Combines vector search with LLM generation
    """
    
    def __init__(self, llm: LLMInterface, vector_store: SimpleVectorStore):
        self.llm = llm
        self.vector_store = vector_store
        self.embedding_generator = EmbeddingGenerator()
        self.conversation_history = []
        self.metrics = {
            'total_queries': 0,
            'successful_responses': 0,
            'avg_latency_ms': 0,
            'total_tokens_used': 0
        }
    
    def initialize_knowledge_base(self):
        """Initialize knowledge base with FAQ documents"""
        logger.info("Initializing knowledge base...")
        
        faq_documents = [
            {
                "title": "How to Book Tickets",
                "content": """To book movie tickets:
                1. Visit our website or mobile app
                2. Select your preferred movie
                3. Choose the date and time
                4. Select your seats
                5. Add snacks (optional)
                6. Complete payment
                Tickets are confirmed via email and SMS.""",
                "category": "booking"
            },
            {
                "title": "Cancellation and Refunds",
                "content": """Refund Policy:
                - Full refund: Cancellation 24+ hours before showtime
                - 50% refund: Cancellation 6-24 hours before showtime
                - No refund: Cancellation less than 6 hours before showtime
                Refunds are processed within 5-7 business days.""",
                "category": "policy"
            },
            {
                "title": "Premium Membership",
                "content": """Premium Membership Benefits:
                - $5 discount per ticket
                - Early booking (30 days in advance)
                - Exclusive movie previews
                - Free snacks once per month
                - VIP customer support
                
                Cost: $9.99/month or $99.99/year""",
                "category": "membership"
            },
            {
                "title": "Technical Support",
                "content": """Common Issues:
                - App crashes: Clear cache and reinstall
                - Payment issues: Try a different payment method
                - Seat selection: Refresh page and try again
                - Email not received: Check spam folder
                
                Contact support: support@ticketing.com""",
                "category": "support"
            },
            {
                "title": "Pricing and Discounts",
                "content": """Ticket Pricing:
                - Standard: $12
                - Peak hours (evening/weekend): $15
                - Matinee (before 5 PM): $9
                
                Discounts:
                - Students: 20% off
                - Seniors: 25% off
                - Group booking (10+): 15% off""",
                "category": "pricing"
            }
        ]
        
        # Add documents to vector store
        for doc in faq_documents:
            embedding = self.embedding_generator.embed(doc['content'])
            self.vector_store.add_document(
                text=doc['content'],
                embedding=embedding,
                metadata={
                    'title': doc['title'],
                    'category': doc['category']
                }
            )
        
        logger.info(f"Loaded {len(faq_documents)} documents")
    
    def retrieve_context(self, query: str, top_k: int = 3) -> List[str]:
        """
        Retrieve relevant context from knowledge base
        
        Args:
            query: User query
            top_k: Number of top results
            
        Returns:
            List of relevant documents
        """
        # Generate query embedding
        query_embedding = self.embedding_generator.embed(query)
        
        # Search vector store
        results = self.vector_store.search(query_embedding, top_k=top_k)
        
        contexts = []
        for doc, similarity, metadata in results:
            logger.info(f"Retrieved: {metadata['title']} (similarity: {similarity:.3f})")
            contexts.append(f"[{metadata['title']}]\n{doc}")
        
        return contexts
    
    def generate_response(
        self,
        query: str,
        context: List[str],
        system_prompt: str = None
    ) -> str:
        """
        Generate response using LLM with context
        
        Args:
            query: User query
            context: Retrieved context documents
            system_prompt: System prompt for LLM
            
        Returns:
            Generated response
        """
        if system_prompt is None:
            system_prompt = """You are a helpful customer support chatbot for a movie ticketing platform.
            Use the provided context to answer questions accurately and helpfully.
            If the context doesn't contain the answer, say you'll connect them with support team.
            Be concise and friendly."""
        
        # Build prompt
        context_str = "\n\n".join(context)
        full_prompt = f"""{system_prompt}

Context:
{context_str}

Customer Query: {query}

Response:"""
        
        # Generate response
        response = self.llm.generate(
            prompt=full_prompt,
            max_tokens=300,
            temperature=0.7
        )
        
        return response.strip()
    
    def chat(self, query: str, retrieve_context: bool = True) -> Dict[str, Any]:
        """
        Process user query and generate response
        
        Args:
            query: User query
            retrieve_context: Whether to use RAG
            
        Returns:
            Response and metadata
        """
        import time
        start_time = time.time()
        
        self.metrics['total_queries'] += 1
        
        logger.info(f"Processing query: {query}")
        
        try:
            # Retrieve context
            contexts = self.retrieve_context(query) if retrieve_context else []
            
            # Generate response
            response = self.generate_response(query, contexts)
            
            # Update metrics
            latency = (time.time() - start_time) * 1000
            self.metrics['successful_responses'] += 1
            self.metrics['avg_latency_ms'] = (
                (self.metrics['avg_latency_ms'] + latency) / 2
            )
            self.metrics['total_tokens_used'] += len(response.split())
            
            # Store in history
            self.conversation_history.append({
                'timestamp': datetime.now(),
                'query': query,
                'response': response,
                'contexts_used': len(contexts),
                'latency_ms': latency
            })
            
            return {
                'query': query,
                'response': response,
                'contexts': contexts,
                'confidence': 0.85 if contexts else 0.6,
                'latency_ms': latency,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error generating response: {str(e)}")
            return {
                'query': query,
                'response': f"Sorry, I encountered an error: {str(e)}",
                'error': True
            }
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get chatbot performance metrics"""
        success_rate = (
            self.metrics['successful_responses'] / max(self.metrics['total_queries'], 1) * 100
        )
        
        return {
            **self.metrics,
            'success_rate_percent': success_rate,
            'conversation_turns': len(self.conversation_history)
        }
    
    def monitor_model_quality(self) -> Dict[str, Any]:
        """
        Monitor chatbot quality metrics
        
        Returns:
            Quality assessment
        """
        if not self.conversation_history:
            return {'status': 'No conversations yet'}
        
        # Calculate average response time
        latencies = [c['latency_ms'] for c in self.conversation_history]
        avg_latency = np.mean(latencies)
        
        # Check for degradation
        if avg_latency > 1000:  # > 1 second
            logger.warning(f"High latency detected: {avg_latency:.0f}ms")
        
        return {
            'avg_response_time_ms': float(avg_latency),
            'min_response_time_ms': float(np.min(latencies)),
            'max_response_time_ms': float(np.max(latencies)),
            'total_conversations': len(self.conversation_history),
            'quality_status': 'HEALTHY' if avg_latency < 500 else 'DEGRADED'
        }


# ==================== Example Usage ====================

if __name__ == "__main__":
    logger.info("Initializing RAG Chatbot...")
    
    # Initialize components
    llm = MockLLM(model_name="gpt-3.5-turbo")
    vector_store = SimpleVectorStore()
    chatbot = RAGChatbot(llm, vector_store)
    
    # Initialize knowledge base
    chatbot.initialize_knowledge_base()
    
    # Example conversations
    queries = [
        "How do I book movie tickets?",
        "What's your refund policy?",
        "Tell me about premium membership",
        "I'm having technical issues",
        "How much do tickets cost?"
    ]
    
    print("\n" + "="*80)
    print("MOVIE TICKETING CHATBOT - DEMONSTRATION")
    print("="*80 + "\n")
    
    for query in queries:
        result = chatbot.chat(query, retrieve_context=True)
        
        print(f"Customer: {result['query']}")
        print(f"Bot: {result['response']}")
        print(f"Latency: {result['latency_ms']:.0f}ms")
        print()
    
    # Print metrics
    print("="*80)
    print("CHATBOT METRICS")
    print("="*80)
    
    metrics = chatbot.get_metrics()
    for key, value in metrics.items():
        if isinstance(value, float):
            print(f"{key}: {value:.2f}")
        else:
            print(f"{key}: {value}")
    
    # Print quality assessment
    print("\n" + "="*80)
    print("QUALITY ASSESSMENT")
    print("="*80)
    
    quality = chatbot.monitor_model_quality()
    for key, value in quality.items():
        if isinstance(value, float):
            print(f"{key}: {value:.2f}")
        else:
            print(f"{key}: {value}")
