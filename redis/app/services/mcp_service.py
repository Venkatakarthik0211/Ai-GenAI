"""
MCP service for AWS documentation fetching with Bedrock query enhancement for use cases
"""

import asyncio
import boto3
import json
from typing import Dict, Any, List
from botocore.exceptions import ClientError

from mcp_aws_client import MCPClient, DocumentProcessor
from mcp_aws_client.processors.data_converter import format_usecase_output_data


class BedrockQueryEnhancer:
    """Use Bedrock to enhance and refine usecase queries and process documentation"""
    
    def __init__(self, region_name: str = "us-east-1"):
        try:
            self.bedrock_client = boto3.client(
                'bedrock-runtime',
                region_name=region_name
            )
            self.model_id = "us.anthropic.claude-3-5-sonnet-20241022-v2:0"
            self.available = True
        except Exception as e:
            print(f"Bedrock initialization failed: {str(e)}")
            self.bedrock_client = None
            self.available = False
    
    def refine_usecase_query(self, usecase_query: str) -> str:
        """Refine the user's usecase query using Bedrock for better documentation retrieval"""
        
        if not self.available:
            return usecase_query
        
        prompt = self._build_query_refinement_prompt(usecase_query)
        
        try:
            response = self._call_bedrock(prompt, max_tokens=150)
            refined_query = self._parse_refined_query_response(response)
            return refined_query or usecase_query
        except Exception as e:
            print(f"Bedrock query refinement failed: {str(e)}")
            return usecase_query
    
    def enhance_documentation_for_usecase(self, documentation: List[Dict[str, Any]], original_query: str) -> Dict[str, Any]:
        """Use Bedrock to process and concentrate documentation based on the usecase query"""
        
        if not self.available or not documentation:
            return {
                "enhanced_content": documentation,
                "usecase_summary": f"Documentation related to: {original_query}",
                "key_recommendations": [],
                "key_services": [],
                "implementation_steps": [],
                "best_practices": [],
                "cost_considerations": "Not specified in documentation",
                "security_considerations": "Not specified in documentation"
            }
        
        # Combine documentation content
        combined_content = self._combine_documentation_content(documentation)
        
        prompt = self._build_documentation_enhancement_prompt(combined_content, original_query)
        
        try:
            response = self._call_bedrock(prompt, max_tokens=2000)
            enhanced_result = self._parse_documentation_response(response)
            return enhanced_result
        except Exception as e:
            print(f"Bedrock documentation enhancement failed: {str(e)}")
            return {
                "enhanced_content": documentation,
                "usecase_summary": f"Documentation related to: {original_query}",
                "key_recommendations": [],
                "key_services": [],
                "implementation_steps": [],
                "best_practices": [],
                "cost_considerations": "Not specified in documentation",
                "security_considerations": "Not specified in documentation",
                "error": str(e)
            }
    
    def _build_query_refinement_prompt(self, usecase_query: str) -> str:
        """Build prompt for refining the usecase query"""
        
        return f"""You are an expert in AWS cloud services and documentation search. Your task is to refine a user's usecase query to make it more effective for finding relevant AWS documentation.

Original User Query: "{usecase_query}"

Your task: Transform this query into a more precise, technical search query that will find the most relevant AWS documentation for this use case.

Guidelines:
- Use official AWS service names and terminology
- Include relevant technical keywords that would appear in AWS documentation
- Focus on the core use case and related AWS services
- Add context that helps identify the right documentation
- Keep it focused but comprehensive
- Remove vague terms and add specific AWS-related terms

Examples:
- "secure file storage" → "AWS S3 secure file storage encryption access control IAM policies"
- "database performance" → "Amazon RDS performance optimization monitoring CloudWatch metrics"
- "serverless web app" → "AWS Lambda API Gateway serverless web application architecture"
- "cost monitoring" → "AWS Cost Explorer billing alerts CloudWatch cost optimization"

Return ONLY the refined search query, no quotes, no explanation:"""
    
    def _build_documentation_enhancement_prompt(self, documentation_content: str, original_query: str) -> str:
        """Build prompt for enhancing documentation based on usecase"""
        
        return f"""You are an AWS solutions architect expert. Analyze the following AWS documentation and create a concentrated, usecase-focused summary.

Original User Query: "{original_query}"

Documentation Content:
{documentation_content}

Your task: Create a comprehensive response that focuses specifically on the user's use case. Structure your response as JSON with the following format:

{{
    "usecase_summary": "A clear summary of how AWS services address this specific use case",
    "key_services": ["list", "of", "relevant", "aws", "services"],
    "implementation_steps": ["step 1", "step 2", "step 3"],
    "best_practices": ["practice 1", "practice 2", "practice 3"],
    "key_recommendations": ["recommendation 1", "recommendation 2"],
    "related_services": ["additional", "services", "to", "consider"],
    "common_pitfalls": ["pitfall 1", "pitfall 2"],
    "cost_considerations": "Brief cost optimization notes",
    "security_considerations": "Brief security notes"
}}

Guidelines:
- Focus specifically on the user's use case
- Extract the most relevant information from the documentation
- Provide actionable recommendations
- Keep each section concise but informative
- Ensure all recommendations are based on the provided documentation
- If information is missing for any section, use an empty array or "Not specified in documentation"

Return ONLY the JSON response:"""
    
    def _combine_documentation_content(self, documentation: List[Dict[str, Any]]) -> str:
        """Combine documentation content into a single string for processing"""
        
        combined = []
        for doc in documentation[:5]:  # Limit to first 5 docs to stay within token limits
            if isinstance(doc, dict):
                title = doc.get('title', 'Untitled')
                content = doc.get('content', doc.get('summary', ''))
                if content:
                    combined.append(f"Document: {title}\nContent: {content}\n---")
        
        return "\n".join(combined)[:15000]  # Limit content length
    
    def _call_bedrock(self, prompt: str, max_tokens: int = 1000) -> str:
        """Call Bedrock API with the prompt"""
        
        body = {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": max_tokens,
            "messages": [
                {
                    "role": "user",
                    "content": str(prompt)
                }
            ],
            "temperature": 0.1,
            "top_p": 0.9
        }
        
        body_json = json.dumps(body, ensure_ascii=True)
        
        response = self.bedrock_client.invoke_model(
            modelId=self.model_id,
            body=body_json.encode('utf-8')
        )
        
        response_body = json.loads(response['body'].read())
        return response_body['content'][0]['text']
    
    def _parse_refined_query_response(self, response: str) -> str:
        """Parse Bedrock response to extract the refined query"""
        try:
            query = response.strip().strip('"').strip("'").strip()
            
            # Remove any prefixes
            prefixes = ["query:", "search:", "output:", "result:", "refined query:"]
            for prefix in prefixes:
                if query.lower().startswith(prefix):
                    query = query[len(prefix):].strip()
            
            if query and 10 <= len(query) <= 300:
                return query
            
            return None
            
        except Exception as e:
            print(f"Error parsing refined query response: {str(e)}")
            return None
    
    def _parse_documentation_response(self, response: str) -> Dict[str, Any]:
        """Parse Bedrock response to extract enhanced documentation"""
        try:
            # Try to extract JSON from the response
            response = response.strip()
            
            # Find JSON content
            start_idx = response.find('{')
            end_idx = response.rfind('}') + 1
            
            if start_idx != -1 and end_idx != -1:
                json_content = response[start_idx:end_idx]
                parsed_response = json.loads(json_content)
                
                # Validate and ensure all required fields exist
                default_response = {
                    "usecase_summary": "Information not available",
                    "key_services": [],
                    "implementation_steps": [],
                    "best_practices": [],
                    "key_recommendations": [],
                    "related_services": [],
                    "common_pitfalls": [],
                    "cost_considerations": "Not specified in documentation",
                    "security_considerations": "Not specified in documentation"
                }
                
                # Merge with defaults to ensure all fields exist
                for key, default_value in default_response.items():
                    if key not in parsed_response:
                        parsed_response[key] = default_value
                
                return parsed_response
            else:
                # Fallback if JSON parsing fails
                return {
                    "usecase_summary": response[:500] + "..." if len(response) > 500 else response,
                    "key_recommendations": ["See documentation content for details"],
                    "key_services": [],
                    "implementation_steps": [],
                    "best_practices": [],
                    "related_services": [],
                    "common_pitfalls": [],
                    "cost_considerations": "Not specified in documentation",
                    "security_considerations": "Not specified in documentation",
                    "parsing_note": "Could not parse structured response"
                }
                
        except json.JSONDecodeError as e:
            print(f"JSON parsing error: {str(e)}")
            return {
                "usecase_summary": response[:500] + "..." if len(response) > 500 else response,
                "key_recommendations": ["See documentation content for details"],
                "key_services": [],
                "implementation_steps": [],
                "best_practices": [],
                "related_services": [],
                "common_pitfalls": [],
                "cost_considerations": "Not specified in documentation",
                "security_considerations": "Not specified in documentation",
                "error": "JSON parsing failed"
            }
        except Exception as e:
            print(f"Error parsing documentation response: {str(e)}")
            return {
                "usecase_summary": "Error processing documentation",
                "key_recommendations": [],
                "key_services": [],
                "implementation_steps": [],
                "best_practices": [],
                "related_services": [],
                "common_pitfalls": [],
                "cost_considerations": "Not specified in documentation",
                "security_considerations": "Not specified in documentation",
                "error": str(e)
            }


class MCPService:
    """Handle MCP client operations for AWS documentation with Bedrock enhancement for use cases"""
    
    def __init__(self, mcp_url: str = "http://localhost:5000", use_bedrock: bool = True):
        self.mcp_url = mcp_url
        self.use_bedrock = use_bedrock
        self.bedrock_enhancer = BedrockQueryEnhancer() if use_bedrock else None
    
    async def generate_usecase_documentation(self, usecase_config: Dict[str, Any]) -> Dict[str, Any]:
        """Generate comprehensive use case documentation"""
        try:
            usecase_query = usecase_config.get('user_query', '')
            if not usecase_query:
                return {"error": "No use case query provided"}
            
            # Use the existing fetch method
            result = await self.fetch_usecase_documentation(usecase_query)
            
            if "error" in result:
                return result
            
            # Transform the result to match expected format
            doc_content = []
            
            # Add main documents
            for doc in result.get('raw_documentation', []):
                doc_content.append({
                    'type': 'main_content',
                    'title': doc.get('title', 'AWS Documentation'),
                    'content': doc.get('content', ''),
                    'source': doc.get('source', 'AWS Documentation'),
                    'similarity': doc.get('similarity', 0.0)
                })
            
            # Add enhanced recommendations as separate documents
            enhanced_docs = result.get('enhanced_documentation', {})
            recommendations = enhanced_docs.get('key_recommendations', [])
            
            for i, rec in enumerate(recommendations):
                doc_content.append({
                    'type': 'recommendation',
                    'title': f'Recommendation {i+1}',
                    'content': rec,
                    'source': 'Bedrock AI Enhancement',
                    'priority': 'Medium'
                })
            
            # Return in expected format
            return {
                "original_query": result.get('original_query'),
                "refined_query": result.get('refined_query'),
                "doc_content": doc_content,
                "search_results": result.get('search_results', {}),
                "enhanced_by_bedrock": result.get('metadata', {}).get('enhanced_by_bedrock', False),
                "new_documents": len(doc_content),
                "duplicate_documents": 0,
                "processing_time": 0,
                "usecase_summary": enhanced_docs.get('usecase_summary', ''),
                "key_services": enhanced_docs.get('key_services', []),
                "implementation_steps": enhanced_docs.get('implementation_steps', []),
                "best_practices": enhanced_docs.get('best_practices', []),
                "cost_considerations": enhanced_docs.get('cost_considerations', ''),
                "security_considerations": enhanced_docs.get('security_considerations', ''),
                "architecture_insights": enhanced_docs.get('related_services', []),
                "metadata": result.get('metadata', {})
            }
            
        except Exception as e:
            return {"error": str(e)}
    
    def generate_usecase_documentation_sync(self, usecase_config: Dict[str, Any]) -> Dict[str, Any]:
        """Synchronous wrapper for generate_usecase_documentation"""
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            result = loop.run_until_complete(self.generate_usecase_documentation(usecase_config))
            loop.close()
            return result
        except Exception as e:
            return {"error": str(e)}
    
    async def fetch_usecase_documentation(self, usecase_query: str) -> Dict[str, Any]:
        """Fetch AWS documentation for a specific use case with Bedrock enhancement"""
        try:
            client = MCPClient(self.mcp_url)
            
            async with client:
                # Check server health
                health = await client.health_check()
                if health.get('status') != 'ok':
                    return {"error": "MCP server is not healthy"}
                
                # Initialize document processor
                processor = DocumentProcessor(client)
                
                # Step 1: Refine the usecase query using Bedrock
                refined_query = self._refine_query(usecase_query)
                print(f"🔍 Original query: {usecase_query}")
                print(f"🔍 Refined query: {refined_query}")
                
                # Step 2: Search for documentation using refined query
                output_data = await processor.search_and_process_documents(
                    search_phrase=refined_query,
                    max_documents=8,  # Get more docs for better context
                    max_recommendations_per_doc=3
                )
                
                if "error" in output_data:
                    return output_data
                
                # Step 3: Enhance documentation using Bedrock
                enhanced_docs = self._enhance_documentation(
                    output_data.get('doc_content', []), 
                    usecase_query
                )
                
                # Step 4: Prepare final response
                final_response = {
                    "original_query": usecase_query,
                    "refined_query": refined_query,
                    "enhanced_documentation": enhanced_docs,
                    "raw_documentation": output_data.get('doc_content', []),
                    "search_results": output_data.get("search_results", []),
                    "metadata": {
                        "total_documents_found": len(output_data.get('doc_content', [])),
                        "enhanced_by_bedrock": self.use_bedrock and self.bedrock_enhancer and self.bedrock_enhancer.available,
                        "query_refined": refined_query != usecase_query,
                        "processing_timestamp": output_data.get('metadata', {}).get('processing_timestamp')
                    }
                }
                
                return final_response
                
        except Exception as e:
            return {"error": str(e)}
    
    def _refine_query(self, usecase_query: str) -> str:
        """Refine the usecase query using Bedrock"""
        
        if self.use_bedrock and self.bedrock_enhancer and self.bedrock_enhancer.available:
            try:
                refined_query = self.bedrock_enhancer.refine_usecase_query(usecase_query)
                if refined_query and refined_query != usecase_query:
                    return refined_query
            except Exception as e:
                print(f"Query refinement failed, using original: {str(e)}")
        
        return usecase_query
    
    def _enhance_documentation(self, documentation: List[Dict[str, Any]], original_query: str) -> Dict[str, Any]:
        """Enhance documentation using Bedrock"""
        
        if self.use_bedrock and self.bedrock_enhancer and self.bedrock_enhancer.available:
            try:
                return self.bedrock_enhancer.enhance_documentation_for_usecase(
                    documentation, original_query
                )
            except Exception as e:
                print(f"Documentation enhancement failed: {str(e)}")
        
        # Fallback response
        return {
            "usecase_summary": f"Documentation related to: {original_query}",
            "key_recommendations": ["Review the raw documentation for detailed information"],
            "key_services": [],
            "implementation_steps": [],
            "best_practices": [],
            "related_services": [],
            "common_pitfalls": [],
            "cost_considerations": "Not specified in documentation",
            "security_considerations": "Not specified in documentation",
            "enhancement_status": "Bedrock enhancement not available"
        }
    
    def fetch_usecase_documentation_sync(self, usecase_query: str) -> Dict[str, Any]:
        """Synchronous wrapper for async fetch method"""
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            result = loop.run_until_complete(self.fetch_usecase_documentation(usecase_query))
            loop.close()
            return result
        except Exception as e:
            return {"error": str(e)}
    
    async def test_connection(self) -> Dict[str, Any]:
        """Test MCP server connection and Bedrock availability"""
        try:
            client = MCPClient(self.mcp_url)
            async with client:
                health = await client.health_check()
                tools = await client.list_tools()
                
                bedrock_status = False
                if self.use_bedrock and self.bedrock_enhancer:
                    bedrock_status = self.bedrock_enhancer.available
                
                return {
                    "status": "success",
                    "health": health,
                    "tools_available": 'result' in tools and 'tools' in tools['result'],
                    "bedrock_enabled": bedrock_status,
                    "service_type": "usecase_documentation_service"
                }
        except Exception as e:
            return {"status": "error", "error": str(e)}
    
    def test_connection_sync(self) -> Dict[str, Any]:
        """Synchronous wrapper for connection test"""
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            result = loop.run_until_complete(self.test_connection())
            loop.close()
            return result
        except Exception as e:
            return {"status": "error", "error": str(e)}


# Example usage
if __name__ == "__main__":
    # Initialize the service
    service = MCPService(use_bedrock=True)
    
    # Example usecase configuration
    example_config = {
        "user_query": "serverless image processing workflow",
        "use_bedrock": True,
        "auto_refine": True,
        "include_best_practices": True,
        "include_cost_analysis": True,
        "include_security": True,
        "max_documents": 10,
        "max_recommendations_per_doc": 3
    }
    
    print(f"Testing with config: {example_config}")
    
    result = service.generate_usecase_documentation_sync(example_config)
    
    if "error" not in result:
        print(f"✅ Success!")
        print(f"Original Query: {result.get('original_query')}")
        print(f"Refined Query: {result.get('refined_query')}")
        print(f"Documents Found: {len(result.get('doc_content', []))}")
        print(f"Enhanced Summary: {result.get('usecase_summary', 'N/A')}")
        print(f"Key Services: {', '.join(result.get('key_services', []))}")
    else:
        print(f"❌ Error: {result['error']}")