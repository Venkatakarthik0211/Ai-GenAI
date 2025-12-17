# redis_service.py - Complete AWS Titan Embeddings Integration
import redis
import json
import os
import numpy as np
from datetime import datetime
from typing import Dict, Any, List, Optional, Tuple
import pickle
import hashlib
import boto3
from botocore.exceptions import ClientError, NoCredentialsError
import streamlit as st

# Make scikit-learn optional for fallback
try:
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity as sklearn_cosine_similarity
    HAS_SKLEARN = True
    print("✅ Scikit-learn dependencies loaded successfully")
except ImportError as e:
    HAS_SKLEARN = False
    TfidfVectorizer = None
    sklearn_cosine_similarity = None
    print(f"❌ Scikit-learn dependencies not available: {e}")


class AWSEmbeddingService:
    """AWS Titan Embeddings service with fallback options"""
    
    _instance = None
    _initialized = False
    
    def __new__(cls, method: str = "auto"):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self, method: str = "auto"):
        # Only initialize once
        if self._initialized:
            return
            
        self.method = "none"
        self.bedrock_client = None
        self.tfidf_vectorizer = None
        self.embedding_dim = None
        self.initialization_error = None
        self.model_id = "amazon.titan-embed-text-v2:0"
        
        print(f"🔄 [AWS] Initializing embedding service with method: {method}")
        
        if method == "auto":
            self._init_auto()
        elif method == "titan":
            success = self._init_titan()
            if not success:
                print("⚠️ Titan failed, trying TF-IDF...")
                self._init_tfidf()
        elif method == "tfidf":
            success = self._init_tfidf()
            if not success:
                print("⚠️ TF-IDF failed, trying Titan...")
                self._init_titan()
        else:
            print(f"Unknown method: {method}, falling back to auto")
            self._init_auto()
        
        self._initialized = True
        print(f"🎯 [AWS] Final embedding method: {self.method}")
    
    def _init_auto(self):
        """Try methods in order of preference"""
        print("🔄 [AWS] Auto-initializing embedding service...")
        
        # Try AWS Titan first (best option)
        if self._init_titan():
            print("✅ [AWS] Auto-init: Titan selected")
            return
        
        # Try TF-IDF as fallback
        if self._init_tfidf():
            print("✅ [AWS] Auto-init: TF-IDF selected")
            return
        
        print("❌ [AWS] Auto-init: No embedding methods available")
    
    def _init_titan(self) -> bool:
        """Initialize AWS Titan Embeddings"""
        try:
            print("🔄 [AWS] Initializing AWS Bedrock client...")
            
            # Try to initialize Bedrock client
            self.bedrock_client = boto3.client(
                'bedrock-runtime',
                region_name=os.getenv('AWS_REGION', 'us-east-1')
            )
            
            # Test the connection with a simple embedding
            print("🔄 [AWS] Testing Titan embeddings...")
            test_response = self._create_titan_embedding("test connection")
            
            if test_response is not None:
                self.method = "titan"
                self.embedding_dim = 1024  # Titan v2 default dimension
                print("✅ [AWS] AWS Titan Embeddings initialized successfully")
                return True
            else:
                raise Exception("Test embedding failed")
                
        except NoCredentialsError:
            self.initialization_error = "AWS credentials not found. Please configure AWS credentials."
            print(f"❌ [AWS] {self.initialization_error}")
            self.bedrock_client = None
            return False
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == 'UnauthorizedOperation':
                self.initialization_error = "AWS Bedrock access denied. Please check IAM permissions."
            elif error_code == 'AccessDeniedException':
                self.initialization_error = "Access denied to Bedrock. Please enable Bedrock access in your AWS account."
            else:
                self.initialization_error = f"AWS Bedrock error: {error_code}"
            print(f"❌ [AWS] {self.initialization_error}")
            self.bedrock_client = None
            return False
        except Exception as e:
            self.initialization_error = f"Failed to initialize AWS Titan: {str(e)}"
            print(f"❌ [AWS] {self.initialization_error}")
            self.bedrock_client = None
            return False
    
    def _init_tfidf(self) -> bool:
        """Initialize TF-IDF vectorizer as fallback"""
        if not HAS_SKLEARN:
            self.initialization_error = "TF-IDF not available (scikit-learn not installed)"
            return False
        
        try:
            print("🔄 [AWS] Initializing TF-IDF vectorizer as fallback...")
            self.tfidf_vectorizer = TfidfVectorizer(
                max_features=1000,
                stop_words='english',
                ngram_range=(1, 2),
                min_df=1,
                max_df=0.95,
                sublinear_tf=True
            )
            
            self.method = "tfidf"
            self.embedding_dim = 1000
            print("✅ [AWS] TF-IDF vectorizer initialized successfully")
            return True
            
        except Exception as e:
            self.initialization_error = f"Failed to initialize TF-IDF: {str(e)}"
            print(f"❌ [AWS] {self.initialization_error}")
            self.tfidf_vectorizer = None
            return False
    
    def create_embedding(self, text: str, dimensions: int = 1024) -> Optional[np.ndarray]:
        """Create embedding using the available method"""
        if not text or not text.strip():
            return None
        
        try:
            if self.method == "titan":
                return self._create_titan_embedding(text, dimensions)
            elif self.method == "tfidf":
                return self._create_tfidf_embedding(text)
            else:
                return None
        except Exception as e:
            print(f"Error creating embedding: {e}")
            return None
    
    def _create_titan_embedding(self, text: str, dimensions: int = 1024) -> Optional[np.ndarray]:
        """Create embedding using AWS Titan"""
        try:
            if not self.bedrock_client:
                return None
            
            # Prepare the request body
            body = {
                "inputText": text,
                "dimensions": dimensions,  # 256, 512, or 1024
                "normalize": True
            }
            
            # Call Bedrock
            response = self.bedrock_client.invoke_model(
                modelId=self.model_id,
                body=json.dumps(body),
                contentType='application/json',
                accept='application/json'
            )
            
            # Parse response
            response_body = json.loads(response['body'].read())
            embedding = response_body.get('embedding')
            
            if embedding:
                return np.array(embedding, dtype=np.float32)
            else:
                print("❌ No embedding in Titan response")
                return None
                
        except ClientError as e:
            print(f"AWS Bedrock error: {e}")
            return None
        except Exception as e:
            print(f"Error creating Titan embedding: {e}")
            return None
    
    def _create_tfidf_embedding(self, text: str) -> Optional[np.ndarray]:
        """Create embedding using TF-IDF"""
        try:
            if not self.tfidf_vectorizer:
                return None
                
            if hasattr(self.tfidf_vectorizer, 'vocabulary_'):
                vector = self.tfidf_vectorizer.transform([text])
                return vector.toarray().flatten()
            else:
                return None
                
        except Exception as e:
            print(f"Error creating TF-IDF embedding: {e}")
            return None
    
    def fit_tfidf_corpus(self, texts: List[str]):
        """Fit TF-IDF vectorizer on a corpus of texts"""
        if self.method == "tfidf" and self.tfidf_vectorizer and texts:
            try:
                print(f"🔄 [AWS] Fitting TF-IDF on {len(texts)} documents...")
                self.tfidf_vectorizer.fit(texts)
                print(f"✅ [AWS] TF-IDF fitted on {len(texts)} documents")
            except Exception as e:
                print(f"Error fitting TF-IDF corpus: {e}")
    
    def is_available(self) -> bool:
        """Check if embedding service is available"""
        return self.method in ["titan", "tfidf"] and (
            (self.method == "titan" and self.bedrock_client is not None) or
            (self.method == "tfidf" and self.tfidf_vectorizer is not None)
        )
    
    def get_info(self) -> Dict[str, Any]:
        """Get information about the embedding service"""
        return {
            "method": self.method,
            "available": self.is_available(),
            "embedding_dim": self.embedding_dim,
            "initialization_error": self.initialization_error,
            "initialized": self._initialized,
            "model_info": {
                "titan_available": self.bedrock_client is not None,
                "tfidf_available": HAS_SKLEARN,
                "current_method": self.method,
                "model_id": self.model_id if self.method == "titan" else None,
                "bedrock_client_loaded": self.bedrock_client is not None,
                "tfidf_loaded": self.tfidf_vectorizer is not None,
                "aws_region": os.getenv('AWS_REGION', 'us-east-1')
            }
        }


@st.cache_resource
def get_redis_service(embedding_method: str = "auto", embedding_dimensions: int = 1024) -> 'RedisVectorService':
    """Cached Redis service to prevent multiple initializations"""
    print(f"🏭 [CACHE] Creating new RedisVectorService instance")
    return RedisVectorService(embedding_method, embedding_dimensions)


class RedisVectorService:
    """Handle all Redis operations for AWS documentation data with AWS Titan embeddings"""

    def __init__(self, embedding_method: str = "auto", embedding_dimensions: int = 1024):
        print(f"🚀 [SERVICE] Initializing RedisVectorService with embedding_method: {embedding_method}")
        
        self.redis_client = self._init_redis()
        self.key_prefix = "aws_usecase_docs"
        self.vector_prefix = "aws_usecase_vectors"
        self.embedding_dimensions = embedding_dimensions
        
        # Use AWS embedding service
        self.embedding_service = AWSEmbeddingService(embedding_method)
        self.vector_dim = self.embedding_service.embedding_dim or embedding_dimensions
        
        # Print final status
        embedding_info = self.embedding_service.get_info()
        print(f"🎯 [SERVICE] Embedding service status:")
        print(f"   Method: {embedding_info['method']}")
        print(f"   Available: {embedding_info['available']}")
        print(f"   Initialized: {embedding_info['initialized']}")
        print(f"   Dimension: {self.vector_dim}")
        if embedding_info.get('initialization_error'):
            print(f"   Error: {embedding_info['initialization_error']}")

    def _init_redis(self) -> redis.Redis:
        """Initialize Redis connection"""
        return redis.Redis(
            host=os.getenv('REDIS_HOST', 'localhost'),
            port=int(os.getenv('REDIS_PORT', 6379)),
            password=os.getenv('REDIS_PASSWORD', 'Localdev@123'),
            decode_responses=False
        )

    def test_connection(self) -> tuple[bool, str]:
        """Test Redis connection and embedding service"""
        try:
            self.redis_client.ping()
            embedding_info = self.embedding_service.get_info()
            
            status_msg = f"Redis: ✅ Connected | Embedding: {embedding_info['method']}"
            if embedding_info['available']:
                status_msg += " ✅ Available"
                if embedding_info['method'] == 'titan':
                    status_msg += f" (Region: {embedding_info['model_info']['aws_region']})"
            else:
                status_msg += " ❌ Not Available"
                if embedding_info.get('initialization_error'):
                    status_msg += f" ({embedding_info['initialization_error']})"
            
            return True, status_msg
        except redis.ConnectionError:
            return False, "Redis connection failed"
        except redis.AuthenticationError:
            return False, "Redis authentication failed"
        except Exception as e:
            return False, f"Error: {str(e)}"

    def get_embedding_status(self) -> Dict[str, Any]:
        """Get detailed embedding service status"""
        return self.embedding_service.get_info()

    def _create_embedding(self, text: str) -> Optional[np.ndarray]:
        """Create embedding for text using AWS service"""
        if not self.embedding_service.is_available() or not text.strip():
            return None

        try:
            return self.embedding_service.create_embedding(text, self.embedding_dimensions)
        except Exception as e:
            print(f"Error creating embedding: {e}")
            return None

    def _fallback_text_search(self, query: str, top_k: int = 5,
                            usecase_filter: Optional[str] = None) -> List[Dict[str, Any]]:
        """Enhanced fallback text-based search with better scoring"""
        print("Using enhanced fallback text-based search...")
        
        # Get all vector metadata
        index_key = f"{self.vector_prefix}:index"
        vector_ids = self.redis_client.smembers(index_key)
        
        if not vector_ids:
            return []
        
        results = []
        query_lower = query.lower()
        query_words = set(query_lower.split())
        
        for vector_id in vector_ids:
            vector_id = vector_id.decode('utf-8') if isinstance(vector_id, bytes) else vector_id
            metadata_key = f"{self.vector_prefix}:meta:{vector_id}"
            metadata_data = self.redis_client.get(metadata_key)
            
            if metadata_data:
                try:
                    metadata = json.loads(metadata_data.decode('utf-8') if isinstance(metadata_data, bytes) else metadata_data)
                    
                    # Apply usecase filter
                    if usecase_filter and usecase_filter != "All":
                        original_query = metadata.get('original_query', '').lower()
                        refined_query = metadata.get('refined_query', '').lower()
                        if usecase_filter.lower() not in original_query and usecase_filter.lower() not in refined_query:
                            continue
                    
                    # Enhanced text similarity calculation
                    content_preview = metadata.get('content_preview', '').lower()
                    source = metadata.get('source', '').lower()
                    doc_type = metadata.get('type', '').lower()
                    usecase_summary = metadata.get('usecase_summary', '').lower()
                    key_services = ' '.join(metadata.get('key_services', [])).lower()
                    
                    # Combine all searchable text
                    searchable_text = f"{content_preview} {source} {doc_type} {usecase_summary} {key_services}"
                    searchable_words = set(searchable_text.split())
                    
                    # Calculate multiple similarity metrics
                    similarity = 0.0
                    
                    # 1. Word overlap similarity (Jaccard)
                    if query_words and searchable_words:
                        intersection = query_words.intersection(searchable_words)
                        union = query_words.union(searchable_words)
                        jaccard_sim = len(intersection) / len(union) if union else 0.0
                        similarity += jaccard_sim * 0.4
                    
                    # 2. Substring matching
                    if query_lower in searchable_text:
                        similarity += 0.3
                    
                    # 3. Exact matches in important fields
                    if query_lower in source or query_lower in doc_type:
                        similarity += 0.2
                    
                    # 4. Service matching bonus
                    if any(word in key_services for word in query_words):
                        similarity += 0.1
                    
                    if similarity > 0.1:  # Minimum threshold
                        results.append({
                            'vector_id': vector_id,
                            'similarity': min(similarity, 1.0),  # Cap at 1.0
                            'metadata': metadata,
                            'match_type': 'text_fallback'
                        })
                            
                except Exception as e:
                    print(f"Error in fallback search for {vector_id}: {e}")
                    continue
        
        # Sort by similarity and return top_k
        results.sort(key=lambda x: x['similarity'], reverse=True)
        return results[:top_k]

    def _generate_content_hash(self, content: str, source: str = "", doc_type: str = "") -> str:
        """Generate a unique hash for document content to detect duplicates"""
        unique_string = f"{content.strip()}{source.strip()}{doc_type.strip()}"
        return hashlib.sha256(unique_string.encode()).hexdigest()

    def _document_exists(self, content_hash: str) -> Optional[str]:
        """Check if a document with this content hash already exists"""
        hash_key = f"{self.key_prefix}:hash:{content_hash}"
        redis_text = redis.Redis(
            host=os.getenv('REDIS_HOST', 'localhost'),
            port=int(os.getenv('REDIS_PORT', 6379)),
            password=os.getenv('REDIS_PASSWORD', 'Localdev@123'),
            decode_responses=True
        )
        existing_vector_id = redis_text.get(hash_key)
        return existing_vector_id

    def _store_document_hash(self, content_hash: str, vector_id: str):
        """Store the mapping between content hash and vector ID"""
        hash_key = f"{self.key_prefix}:hash:{content_hash}"
        redis_text = redis.Redis(
            host=os.getenv('REDIS_HOST', 'localhost'),
            port=int(os.getenv('REDIS_PORT', 6379)),
            password=os.getenv('REDIS_PASSWORD', 'Localdev@123'),
            decode_responses=True
        )
        redis_text.set(hash_key, vector_id)

    def _store_vector(self, vector_id: str, embedding: np.ndarray, metadata: Dict[str, Any]):
        """Store vector with metadata"""
        vector_key = f"{self.vector_prefix}:vec:{vector_id}"
        metadata_key = f"{self.vector_prefix}:meta:{vector_id}"

        # Store vector as binary data
        self.redis_client.set(vector_key, pickle.dumps(embedding))

        # Store metadata as JSON
        self.redis_client.set(metadata_key, json.dumps(metadata))

        # Add to vector index
        index_key = f"{self.vector_prefix}:index"
        self.redis_client.sadd(index_key, vector_id)

    def _prepare_tfidf_corpus(self, documents: List[Dict[str, Any]]):
        """Prepare TF-IDF corpus if using TF-IDF method"""
        if self.embedding_service.method == "tfidf" and documents:
            texts = []
            for doc in documents:
                content = str(doc.get('content', ''))
                if content.strip():
                    texts.append(content)
            
            if texts:
                self.embedding_service.fit_tfidf_corpus(texts)

    def store_usecase_data(self, data: Dict[str, Any]) -> str:
        """Store usecase documentation data with AWS Titan embeddings"""
        timestamp = datetime.now().isoformat()

        # Store main data
        redis_text = redis.Redis(
            host=os.getenv('REDIS_HOST', 'localhost'),
            port=int(os.getenv('REDIS_PORT', 6379)),
            password=os.getenv('REDIS_PASSWORD', 'Localdev@123'),
            decode_responses=True
        )

        main_key = f"{self.key_prefix}:data:{timestamp}"
        redis_text.set(main_key, json.dumps(data))

        # Extract usecase information
        original_query = data.get('original_query', '')
        refined_query = data.get('refined_query', '')
        enhanced_documentation = data.get('enhanced_documentation', {})
        
        # Store usecase metadata
        usecase_metadata = {
            'original_query': original_query,
            'refined_query': refined_query,
            'usecase_summary': enhanced_documentation.get('usecase_summary', ''),
            'key_services': enhanced_documentation.get('key_services', []),
            'implementation_steps': enhanced_documentation.get('implementation_steps', []),
            'best_practices': enhanced_documentation.get('best_practices', []),
            'key_recommendations': enhanced_documentation.get('key_recommendations', []),
            'cost_considerations': enhanced_documentation.get('cost_considerations', ''),
            'security_considerations': enhanced_documentation.get('security_considerations', ''),
            'query_refined': data.get('metadata', {}).get('query_refined', False),
            'enhanced_by_bedrock': data.get('metadata', {}).get('enhanced_by_bedrock', False),
            'total_documents_found': data.get('metadata', {}).get('total_documents_found', 0),
            'processing_timestamp': data.get('metadata', {}).get('processing_timestamp', timestamp),
            'created_at': timestamp,
            'embedding_method': self.embedding_service.method,
            'embedding_dimensions': self.embedding_dimensions
        }
        
        metadata_key = f"{self.key_prefix}:usecase_metadata:{timestamp}"
        redis_text.hset(metadata_key, mapping={k: json.dumps(v) if isinstance(v, (list, dict)) else str(v) for k, v in usecase_metadata.items()})

        # Store search results
        search_results = data.get('search_results', {})
        if search_results:
            search_key = f"{self.key_prefix}:search:{timestamp}"
            redis_text.set(search_key, json.dumps(search_results))

        # Process raw documentation and create vectors
        raw_documentation = data.get('raw_documentation', [])
        
        # Prepare TF-IDF corpus if needed
        self._prepare_tfidf_corpus(raw_documentation)
        
        vector_ids = []
        duplicate_count = 0
        new_document_count = 0

        for i, doc in enumerate(raw_documentation):
            content_text = str(doc.get('content', ''))
            source = doc.get('source', '')
            doc_type = doc.get('type', '')
            
            if not content_text.strip():
                continue

            # Generate content hash for deduplication
            content_hash = self._generate_content_hash(content_text, source, doc_type)
            
            # Check if document already exists
            existing_vector_id = self._document_exists(content_hash)
            
            if existing_vector_id:
                vector_ids.append(existing_vector_id)
                duplicate_count += 1
                print(f"Duplicate document found: {source} - {doc_type[:50]}...")
                continue

            # Document is new, proceed with storage
            doc_key = f"{self.key_prefix}:doc:{timestamp}:{i}"

            # Store document data
            doc_data = {
                'type': doc_type,
                'source': source,
                'parent': doc.get('parent', ''),
                'content': json.dumps(content_text),
                'content_hash': content_hash,
                'original_query': original_query,
                'refined_query': refined_query,
                'usecase_context': enhanced_documentation.get('usecase_summary', ''),
                'embedding_method': self.embedding_service.method,
                'embedding_dimensions': self.embedding_dimensions,
                'created_at': timestamp
            }
            redis_text.hset(doc_key, mapping=doc_data)

            # Create and store vectors (if embedding service is available)
            if self.embedding_service.is_available():
                # Combine content with usecase context for better embeddings
                embedding_text = f"{content_text} {enhanced_documentation.get('usecase_summary', '')}"
                embedding = self._create_embedding(embedding_text)
                
                if embedding is not None:
                    vector_id = f"{timestamp}:{i}"
                    vector_metadata = {
                        'doc_key': doc_key,
                        'timestamp': timestamp,
                        'doc_index': i,
                        'type': doc_type,
                        'source': source,
                        'parent': doc.get('parent', ''),
                        'content_preview': content_text[:200],
                        'content_hash': content_hash,
                        'original_query': original_query,
                        'refined_query': refined_query,
                        'usecase_summary': enhanced_documentation.get('usecase_summary', ''),
                        'key_services': enhanced_documentation.get('key_services', []),
                        'key_recommendations': enhanced_documentation.get('key_recommendations', []),
                        'query_refined': usecase_metadata.get('query_refined', False),
                        'enhanced_by_bedrock': usecase_metadata.get('enhanced_by_bedrock', False),
                        'embedding_method': self.embedding_service.method,
                        'embedding_dimensions': self.embedding_dimensions,
                        'created_at': timestamp
                    }

                    try:
                        self._store_vector(vector_id, embedding, vector_metadata)
                        self._store_document_hash(content_hash, vector_id)
                        vector_ids.append(vector_id)
                        new_document_count += 1
                    except Exception as e:
                        print(f"Error storing vector for doc {i}: {e}")

        # Store vector mapping for this usecase entry
        if vector_ids:
            vector_mapping_key = f"{self.key_prefix}:vectors:{timestamp}"
            redis_text.set(vector_mapping_key, json.dumps(vector_ids))

        # Update usecase metadata with deduplication stats
        usecase_metadata.update({
            'new_documents': new_document_count,
            'duplicate_documents': duplicate_count,
            'total_processed': len(raw_documentation),
            'vector_ids_count': len(vector_ids)
        })

        # Add to recent usecase queries list
        self._add_to_recent_usecase_queries(timestamp, usecase_metadata, redis_text)

        print(f"Usecase storage complete: {new_document_count} new documents, {duplicate_count} duplicates skipped")
        print(f"Embedding method used: {self.embedding_service.method}")
        return main_key

    def _add_to_recent_usecase_queries(self, timestamp: str, usecase_metadata: Dict[str, Any], redis_client):
        """Add usecase query to recent queries list"""
        recent_key = f"{self.key_prefix}:recent_usecases"
        query_info = {
            'timestamp': timestamp,
            'original_query': usecase_metadata.get('original_query', ''),
            'refined_query': usecase_metadata.get('refined_query', ''),
            'usecase_summary': usecase_metadata.get('usecase_summary', '')[:100] + '...' if len(usecase_metadata.get('usecase_summary', '')) > 100 else usecase_metadata.get('usecase_summary', ''),
            'key_services': usecase_metadata.get('key_services', [])[:3],
            'total_docs': usecase_metadata.get('total_documents_found', 0),
            'new_documents': usecase_metadata.get('new_documents', 0),
            'duplicate_documents': usecase_metadata.get('duplicate_documents', 0),
            'total_processed': usecase_metadata.get('total_processed', 0),
            'query_refined': usecase_metadata.get('query_refined', False),
            'enhanced_by_bedrock': usecase_metadata.get('enhanced_by_bedrock', False),
            'embedding_method': usecase_metadata.get('embedding_method', 'none'),
            'embedding_dimensions': usecase_metadata.get('embedding_dimensions', 1024)
        }
        redis_client.lpush(recent_key, json.dumps(query_info))
        redis_client.ltrim(recent_key, 0, 9)

    def semantic_search_usecases(self, query: str, top_k: int = 5,
                                usecase_filter: Optional[str] = None,
                                min_similarity: float = 0.1) -> List[Dict[str, Any]]:
        """Perform semantic search using AWS Titan embeddings"""
        
        # If no embedding service available, use fallback text search
        if not self.embedding_service.is_available():
            print("Warning: No embedding service available, using enhanced text search")
            return self._fallback_text_search(query, top_k, usecase_filter)

        # Create query embedding
        query_embedding = self._create_embedding(query)
        if query_embedding is None:
            print("Warning: Could not create embedding for query, using fallback text search")
            return self._fallback_text_search(query, top_k, usecase_filter)

        # Get all vectors
        index_key = f"{self.vector_prefix}:index"
        vector_ids = self.redis_client.smembers(index_key)

        if not vector_ids:
            print("Warning: No vectors found in database")
            return []

        similarities = []
        seen_hashes = set()

        for vector_id in vector_ids:
            vector_id = vector_id.decode('utf-8') if isinstance(vector_id, bytes) else vector_id

            vector_key = f"{self.vector_prefix}:vec:{vector_id}"
            metadata_key = f"{self.vector_prefix}:meta:{vector_id}"

            vector_data = self.redis_client.get(vector_key)
            metadata_data = self.redis_client.get(metadata_key)

            if vector_data and metadata_data:
                try:
                    stored_embedding = pickle.loads(vector_data)
                    metadata = json.loads(metadata_data.decode('utf-8') if isinstance(metadata_data, bytes) else metadata_data)

                    content_hash = metadata.get('content_hash', '')
                    if content_hash in seen_hashes:
                        continue
                    seen_hashes.add(content_hash)

                    # Apply usecase filter
                    if usecase_filter and usecase_filter != "All":
                        original_query = metadata.get('original_query', '').lower()
                        refined_query = metadata.get('refined_query', '').lower()
                        usecase_summary = metadata.get('usecase_summary', '').lower()
                        
                        if (usecase_filter.lower() not in original_query and 
                            usecase_filter.lower() not in refined_query and 
                            usecase_filter.lower() not in usecase_summary):
                            continue

                    similarity = self._calculate_similarity(query_embedding, stored_embedding)

                    if similarity >= min_similarity:
                        similarities.append({
                            'vector_id': vector_id,
                            'similarity': similarity,
                            'metadata': metadata,
                            'match_type': f'semantic_{self.embedding_service.method}'
                        })

                except Exception as e:
                    print(f"Error processing vector {vector_id}: {e}")
                    continue

        similarities.sort(key=lambda x: x['similarity'], reverse=True)
        return similarities[:top_k]

    def _calculate_similarity(self, vec1: np.ndarray, vec2: np.ndarray) -> float:
        """Calculate similarity between two vectors (method-agnostic)"""
        try:
            if self.embedding_service.method == "tfidf":
                # For TF-IDF, use sklearn's cosine similarity
                if HAS_SKLEARN:
                    similarity = sklearn_cosine_similarity([vec1], [vec2])[0][0]
                    return float(similarity)
            
            # For Titan or fallback, use cosine similarity
            dot_product = np.dot(vec1, vec2)
            norm_a = np.linalg.norm(vec1)
            norm_b = np.linalg.norm(vec2)

            if norm_a == 0 or norm_b == 0:
                return 0.0

            return float(dot_product / (norm_a * norm_b))
        except Exception:
            return 0.0

    def get_similar_usecase_documents(self, doc_id: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """Find documents similar to a given usecase document"""
        vector_key = f"{self.vector_prefix}:vec:{doc_id}"
        vector_data = self.redis_client.get(vector_key)

        if not vector_data:
            return []

        try:
            doc_embedding = pickle.loads(vector_data)
        except Exception:
            return []

        # Get all other vectors
        index_key = f"{self.vector_prefix}:index"
        vector_ids = self.redis_client.smembers(index_key)

        similarities = []
        seen_hashes = set()

        for vector_id in vector_ids:
            vector_id = vector_id.decode('utf-8') if isinstance(vector_id, bytes) else vector_id

            if vector_id == doc_id:
                continue

            other_vector_key = f"{self.vector_prefix}:vec:{vector_id}"
            metadata_key = f"{self.vector_prefix}:meta:{vector_id}"

            other_vector_data = self.redis_client.get(other_vector_key)
            metadata_data = self.redis_client.get(metadata_key)

            if other_vector_data and metadata_data:
                try:
                    other_embedding = pickle.loads(other_vector_data)
                    metadata = json.loads(metadata_data.decode('utf-8') if isinstance(metadata_data, bytes) else metadata_data)

                    content_hash = metadata.get('content_hash', '')
                    if content_hash in seen_hashes:
                        continue
                    seen_hashes.add(content_hash)

                    similarity = self._calculate_similarity(doc_embedding, other_embedding)

                    similarities.append({
                        'vector_id': vector_id,
                        'similarity': similarity,
                        'metadata': metadata
                    })

                except Exception as e:
                    print(f"Error processing vector {vector_id}: {e}")
                    continue

        similarities.sort(key=lambda x: x['similarity'], reverse=True)
        return similarities[:top_k]

    def get_usecase_data(self, key: str) -> Dict[str, Any]:
        """Retrieve usecase documentation data from Redis"""
        redis_text = redis.Redis(
            host=os.getenv('REDIS_HOST', 'localhost'),
            port=int(os.getenv('REDIS_PORT', 6379)),
            password=os.getenv('REDIS_PASSWORD', 'Localdev@123'),
            decode_responses=True
        )

        data_str = redis_text.get(key)
        if data_str:
            return json.loads(data_str)
        return {}

    def get_recent_usecase_queries(self) -> List[Dict[str, Any]]:
        """Get recent usecase documentation queries"""
        redis_text = redis.Redis(
            host=os.getenv('REDIS_HOST', 'localhost'),
            port=int(os.getenv('REDIS_PORT', 6379)),
            password=os.getenv('REDIS_PASSWORD', 'Localdev@123'),
            decode_responses=True
        )

        recent_key = f"{self.key_prefix}:recent_usecases"
        recent_data = redis_text.lrange(recent_key, 0, -1)
        return [json.loads(item) for item in recent_data]

    def get_latest_usecase_data(self) -> Optional[Dict[str, Any]]:
        """Get the most recent usecase data"""
        recent_queries = self.get_recent_usecase_queries()
        if recent_queries:
            latest_query = recent_queries[0]
            timestamp = latest_query['timestamp']
            data_key = f"{self.key_prefix}:data:{timestamp}"
            return self.get_usecase_data(data_key)
        return None

    def get_usecase_statistics(self) -> Dict[str, Any]:
        """Get usecase vector database statistics"""
        try:
            index_key = f"{self.vector_prefix}:index"
            total_vectors = self.redis_client.scard(index_key)

            vector_ids = self.redis_client.smembers(index_key)

            original_queries = {}
            key_services = {}
            types = {}
            embedding_methods = {}
            embedding_dimensions = {}
            unique_hashes = set()
            bedrock_enhanced = 0
            query_refined = 0

            for vector_id in vector_ids:
                vector_id = vector_id.decode('utf-8') if isinstance(vector_id, bytes) else vector_id
                metadata_key = f"{self.vector_prefix}:meta:{vector_id}"
                metadata_data = self.redis_client.get(metadata_key)

                if metadata_data:
                    try:
                        metadata = json.loads(metadata_data.decode('utf-8') if isinstance(metadata_data, bytes) else metadata_data)

                        original_query = metadata.get('original_query', 'Unknown')[:50]
                        doc_type = metadata.get('type', 'Unknown')
                        content_hash = metadata.get('content_hash', '')
                        services = metadata.get('key_services', [])
                        embedding_method = metadata.get('embedding_method', 'unknown')
                        embedding_dim = metadata.get('embedding_dimensions', 1024)

                        original_queries[original_query] = original_queries.get(original_query, 0) + 1
                        types[doc_type] = types.get(doc_type, 0) + 1
                        embedding_methods[embedding_method] = embedding_methods.get(embedding_method, 0) + 1
                        embedding_dimensions[str(embedding_dim)] = embedding_dimensions.get(str(embedding_dim), 0) + 1
                        
                        for service in services:
                            key_services[service] = key_services.get(service, 0) + 1
                        
                        if content_hash:
                            unique_hashes.add(content_hash)
                            
                        if metadata.get('enhanced_by_bedrock', False):
                            bedrock_enhanced += 1
                            
                        if metadata.get('query_refined', False):
                            query_refined += 1

                    except Exception:
                        continue

            embedding_info = self.embedding_service.get_info()

            return {
                'total_vectors': total_vectors,
                'unique_documents': len(unique_hashes),
                'potential_duplicates': total_vectors - len(unique_hashes),
                'bedrock_enhanced_count': bedrock_enhanced,
                'query_refined_count': query_refined,
                'vector_dimension': self.vector_dim,
                'embedding_service': embedding_info,
                'embedding_methods_used': embedding_methods,
                'embedding_dimensions_used': embedding_dimensions,
                'usecase_queries_distribution': original_queries,
                'key_services_distribution': key_services,
                'types_distribution': types
            }

        except Exception as e:
            return {'error': str(e)}

    def get_usecase_analytics_data(self) -> Dict[str, Any]:
        """Get analytics data for usecase dashboard"""
        recent_queries = self.get_recent_usecase_queries()
        vector_stats = self.get_usecase_statistics()

        if not recent_queries:
            return {
                'total_queries': 0,
                'total_docs': 0,
                'total_new_docs': 0,
                'total_duplicates': 0,
                'bedrock_enhanced': 0,
                'query_refined': 0,
                'usecase_queries': {},
                'key_services': {},
                'embedding_methods': {},
                'embedding_dimensions': {},
                'recent_queries': [],
                'vector_stats': vector_stats
            }

        # Calculate statistics
        total_docs = sum(q.get('total_docs', 0) for q in recent_queries)
        total_new_docs = sum(q.get('new_documents', 0) for q in recent_queries)
        total_duplicates = sum(q.get('duplicate_documents', 0) for q in recent_queries)
        bedrock_enhanced = sum(1 for q in recent_queries if q.get('enhanced_by_bedrock', False))
        query_refined = sum(1 for q in recent_queries if q.get('query_refined', False))

        # Usecase query distribution
        usecase_queries = {}
        for q in recent_queries:
            original_query = q.get('original_query', 'Unknown')[:50]
            usecase_queries[original_query] = usecase_queries.get(original_query, 0) + 1

        # Key services distribution
        key_services = {}
        for q in recent_queries:
            services = q.get('key_services', [])
            for service in services:
                key_services[service] = key_services.get(service, 0) + 1

        # Embedding methods distribution
        embedding_methods = {}
        for q in recent_queries:
            method = q.get('embedding_method', 'unknown')
            embedding_methods[method] = embedding_methods.get(method, 0) + 1

        # Embedding dimensions distribution
        embedding_dimensions = {}
        for q in recent_queries:
            dim = str(q.get('embedding_dimensions', 1024))
            embedding_dimensions[dim] = embedding_dimensions.get(dim, 0) + 1

        return {
            'total_queries': len(recent_queries),
            'total_docs': total_docs,
            'total_new_docs': total_new_docs,
            'total_duplicates': total_duplicates,
            'bedrock_enhanced': bedrock_enhanced,
            'query_refined': query_refined,
            'usecase_queries': usecase_queries,
            'key_services': key_services,
            'embedding_methods': embedding_methods,
            'embedding_dimensions': embedding_dimensions,
            'recent_queries': recent_queries,
            'vector_stats': vector_stats
        }

    def remove_duplicates(self) -> Dict[str, int]:
        """Remove duplicate documents from the database"""
        index_key = f"{self.vector_prefix}:index"
        vector_ids = self.redis_client.smembers(index_key)
        
        seen_hashes = {}
        duplicates_removed = 0
        total_processed = 0
        
        for vector_id in vector_ids:
            vector_id = vector_id.decode('utf-8') if isinstance(vector_id, bytes) else vector_id
            total_processed += 1
            
            metadata_key = f"{self.vector_prefix}:meta:{vector_id}"
            metadata_data = self.redis_client.get(metadata_key)
            
            if metadata_data:
                try:
                    metadata = json.loads(metadata_data.decode('utf-8') if isinstance(metadata_data, bytes) else metadata_data)
                    content_hash = metadata.get('content_hash', '')
                    
                    if content_hash:
                        if content_hash in seen_hashes:
                            self._remove_vector(vector_id)
                            duplicates_removed += 1
                        else:
                            seen_hashes[content_hash] = vector_id
                            
                except Exception as e:
                    print(f"Error processing vector {vector_id} for deduplication: {e}")
        
        return {
            'total_processed': total_processed,
            'duplicates_removed': duplicates_removed,
            'unique_documents': len(seen_hashes)
        }

    def _remove_vector(self, vector_id: str):
        """Remove a vector and its associated data"""
        vector_key = f"{self.vector_prefix}:vec:{vector_id}"
        metadata_key = f"{self.vector_prefix}:meta:{vector_id}"
        index_key = f"{self.vector_prefix}:index"
        
        self.redis_client.delete(vector_key)
        self.redis_client.delete(metadata_key)
        self.redis_client.srem(index_key, vector_id)

    def clear_all_vectors(self) -> int:
        """Clear all vector data"""
        vector_keys = self.redis_client.keys(f"{self.vector_prefix}:*")
        hash_keys = self.redis_client.keys(f"{self.key_prefix}:hash:*")
        all_keys = vector_keys + hash_keys
        if all_keys:
            return self.redis_client.delete(*all_keys)
        return 0

    def clear_all_usecase_data(self) -> int:
        """Clear all usecase-related keys including vectors"""
        usecase_keys = self.redis_client.keys(f"{self.key_prefix}:*")
        vector_keys = self.redis_client.keys(f"{self.vector_prefix}:*")

        all_keys = usecase_keys + vector_keys
        if all_keys:
            return self.redis_client.delete(*all_keys)
        return 0

    def get_system_info(self) -> Dict[str, Any]:
        """Get Redis system information including embedding service info"""
        try:
            info = self.redis_client.info()
            usecase_keys_count = len(self.redis_client.keys(f"{self.key_prefix}:*"))
            vector_keys_count = len(self.redis_client.keys(f"{self.vector_prefix}:*"))
            embedding_info = self.embedding_service.get_info()

            return {
                'total_keys': self.redis_client.dbsize(),
                'usecase_keys': usecase_keys_count,
                'vector_keys': vector_keys_count,
                'used_memory': info.get('used_memory_human', 'N/A'),
                'connected_clients': info.get('connected_clients', 0),
                'redis_version': info.get('redis_version', 'N/A'),
                'uptime_days': info.get('uptime_in_days', 0),
                'total_commands': info.get('total_commands_processed', 0),
                'keyspace_hits': info.get('keyspace_hits', 0),
                'keyspace_misses': info.get('keyspace_misses', 0),
                'embedding_service': embedding_info,
                'service_type': 'aws_titan_usecase_documentation_service'
            }
        except Exception as e:
            return {'error': str(e)}

    # Backward compatibility methods
    def store_aws_data(self, data: Dict[str, Any]) -> str:
        """Backward compatibility method"""
        return self.store_usecase_data(data)
    
    def semantic_search(self, query: str, top_k: int = 5, **kwargs) -> List[Dict[str, Any]]:
        """Backward compatibility method"""
        usecase_filter = kwargs.get('service_filter') or kwargs.get('usecase_filter')
        return self.semantic_search_usecases(query, top_k, usecase_filter)
    
    def get_recent_queries(self) -> List[Dict[str, Any]]:
        """Backward compatibility method"""
        return self.get_recent_usecase_queries()
    
    def get_analytics_data(self) -> Dict[str, Any]:
        """Backward compatibility method"""
        return self.get_usecase_analytics_data()


# Backward compatibility
RedisService = RedisVectorService