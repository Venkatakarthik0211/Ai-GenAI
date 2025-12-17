"""
Document processing utilities for AWS documentation
"""

import json
from typing import List, Dict, Any, Union

from ..client.mcp_client import MCPClient
from .data_converter import convert_to_dict


class DocumentProcessor:
    """Handles processing of AWS documentation and recommendations"""
    
    def __init__(self, client: MCPClient):
        self.client = client
    
    async def search_and_process_documents(
        self, 
        search_phrase: str, 
        max_documents: int = 5,
        max_recommendations_per_doc: int = 2
    ) -> Dict[str, Any]:
        """
        Search for documents and process them with their recommendations
        
        Args:
            search_phrase: The search query
            max_documents: Maximum number of documents to process
            max_recommendations_per_doc: Maximum recommendations per document
            
        Returns:
            Dictionary containing search results and processed content
        """
        output_data = {}
        
        # Step 1: Search for documentation
        print("🔍 Searching documentation...")
        search_result = await self.client.call_tool(
            "search_documentation",
            arguments={"search_phrase": search_phrase},
            timeout=100,
        )
        
        if search_result.error:
            print(f"❌ Search failed: {search_result.error}")
            return {"error": search_result.error}
        
        search_results = self._normalize_search_results(search_result.data)
        output_data["search_results"] = convert_to_dict(search_results)
        
        print(f"✅ Found {len(search_results)} search results")
        
        # Step 2: Process documents
        doc_content = await self._process_documents(
            search_results[:max_documents],
            max_recommendations_per_doc
        )
        
        output_data["doc_content"] = doc_content
        
        return output_data
    
    def _normalize_search_results(self, search_results: Any) -> List[Dict[str, Any]]:
        """Normalize search results to a consistent format"""
        if isinstance(search_results, dict):
            search_results = search_results.get('results', [])
        elif isinstance(search_results, str):
            try:
                search_results = json.loads(search_results)
                if isinstance(search_results, dict):
                    search_results = search_results.get('results', [])
            except json.JSONDecodeError:
                search_results = []
        
        if not isinstance(search_results, list):
            search_results = []
            
        return search_results
    
    async def _process_documents(
        self, 
        search_results: List[Dict[str, Any]], 
        max_recommendations_per_doc: int
    ) -> List[Dict[str, Any]]:
        """Process documents and their recommendations"""
        doc_content = []
        
        for idx, result in enumerate(search_results):
            print(f"📄 Processing document {idx + 1}/{len(search_results)}...")
            
            url = self._extract_url_from_result(result)
            if not url:
                continue
            
            # Read main document content
            main_content = await self._read_document_content(url)
            if main_content:
                doc_content.append({
                    "type": "main_content",
                    "source": url,
                    "content": main_content
                })
            
            # Process recommendations for this document
            recommendations = await self._process_document_recommendations(
                url, max_recommendations_per_doc
            )
            doc_content.extend(recommendations)
        
        return doc_content
    
    def _extract_url_from_result(self, result: Union[Dict[str, Any], str]) -> str:
        """Extract URL from search result"""
        if isinstance(result, dict):
            return result.get('url') or result.get('topic')
        elif isinstance(result, str):
            return result
        return None
    
    async def _read_document_content(self, url: str) -> Any:
        """Read content from a document URL"""
        print(f"  📖 Reading content from: {url}")
        content_result = await self.client.call_tool(
            "read_documentation",
            arguments={"url": url},
            timeout=100,
        )
        
        if content_result.error:
            print(f"  ❌ Failed to read content: {content_result.error}")
            return None
            
        return content_result.data
    
    async def _process_document_recommendations(
        self, 
        url: str, 
        max_recommendations: int
    ) -> List[Dict[str, Any]]:
        """Process recommendations for a document"""
        print(f"  💡 Getting recommendations for: {url}")
        recommendations_result = await self.client.call_tool(
            "recommend",
            arguments={"context": url},
            timeout=100
        )
        
        if recommendations_result.error:
            print(f"  ❌ Failed to get recommendations: {recommendations_result.error}")
            return []
        
        recommendations = self._normalize_recommendations(recommendations_result.data)
        
        # Process each recommendation
        processed_recommendations = []
        for rec_idx, rec in enumerate(recommendations[:max_recommendations]):
            print(f"    🔗 Processing recommendation {rec_idx + 1}/{min(len(recommendations), max_recommendations)}...")
            
            rec_url = self._extract_url_from_result(rec)
            if not rec_url:
                continue
                
            rec_content = await self._read_document_content(rec_url)
            if rec_content:
                processed_recommendations.append({
                    "type": "recommendation",
                    "source": rec_url,
                    "parent": url,
                    "content": rec_content
                })
        
        return processed_recommendations
    
    def _normalize_recommendations(self, rec_results: Any) -> List[Dict[str, Any]]:
        """Normalize recommendations to a consistent format"""
        if isinstance(rec_results, dict):
            rec_results = rec_results.get('recommendations', [])
        elif isinstance(rec_results, str):
            try:
                rec_results = json.loads(rec_results)
                if isinstance(rec_results, dict):
                    rec_results = rec_results.get('recommendations', [])
            except json.JSONDecodeError:
                rec_results = []
        
        if not isinstance(rec_results, list):
            rec_results = []
            
        return rec_results
    
    def get_processing_summary(self, doc_content: List[Dict[str, Any]]) -> Dict[str, int]:
        """Get summary statistics of processed documents"""
        main_docs = len([d for d in doc_content if d['type'] == 'main_content'])
        recommendations = len([d for d in doc_content if d['type'] == 'recommendation'])
        
        return {
            "main_documents": main_docs,
            "recommendations": recommendations,
            "total_items": len(doc_content)
        }