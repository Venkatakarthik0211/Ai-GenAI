"""
Data conversion utilities for AWS Use Case Documentation
"""

import json
from typing import Dict, Any, Union, List, Optional
from datetime import datetime
import hashlib
import re


def convert_to_dict(data: Any) -> Dict[str, Any]:
    """Convert data to dictionary format"""
    if isinstance(data, dict):
        return data
    elif isinstance(data, list):
        return {"results": data}
    elif isinstance(data, str):
        try:
            return json.loads(data)
        except json.JSONDecodeError:
            return {"content": data}
    else:
        return {"data": data}


def safe_json_loads(data: str, default: Any = None) -> Any:
    """Safely load JSON data with fallback"""
    try:
        return json.loads(data)
    except (json.JSONDecodeError, TypeError):
        return default


def format_usecase_output_data(
    usecase_data: Dict[str, Any], 
    config: Dict[str, Any]
) -> Dict[str, Any]:
    """Format final use case output data structure"""
    
    # Extract key information from usecase_data
    original_query = usecase_data.get("original_query", config.get("user_query", ""))
    refined_query = usecase_data.get("refined_query", original_query)
    doc_content = usecase_data.get("doc_content", [])
    search_results = usecase_data.get("search_results", {})
    
    # Calculate statistics
    main_documents = [d for d in doc_content if d.get('type') == 'main_content']
    recommendations = [d for d in doc_content if d.get('type') == 'recommendation']
    
    # Extract key services from documents
    key_services = extract_key_services(doc_content)
    
    # Generate use case summary
    usecase_summary = generate_usecase_summary(usecase_data, config)
    
    # Format the comprehensive output
    formatted_output = {
        "metadata": {
            "original_query": original_query,
            "refined_query": refined_query if refined_query != original_query else None,
            "query_refined": refined_query != original_query,
            "enhanced_by_bedrock": usecase_data.get("enhanced_by_bedrock", False),
            "processing_timestamp": datetime.now().isoformat(),
            "config_used": {
                "use_bedrock": config.get("use_bedrock", False),
                "auto_refine": config.get("auto_refine", False),
                "include_best_practices": config.get("include_best_practices", True),
                "include_cost_analysis": config.get("include_cost_analysis", False),
                "include_security": config.get("include_security", False),
                "max_documents": config.get("max_documents", 10),
                "similarity_threshold": config.get("similarity_threshold", 0.3)
            },
            "statistics": {
                "total_documents": len(doc_content),
                "main_documents": len(main_documents),
                "recommendations": len(recommendations),
                "new_documents": usecase_data.get("new_documents", 0),
                "duplicate_documents": usecase_data.get("duplicate_documents", 0),
                "key_services": key_services,
                "processing_time_seconds": usecase_data.get("processing_time", 0)
            }
        },
        
        "usecase_summary": usecase_summary,
        
        "architecture_overview": generate_architecture_overview(doc_content, key_services),
        
        "documentation": {
            "main_content": format_main_documents(main_documents),
            "recommendations": format_recommendations(recommendations),
            "best_practices": extract_best_practices(doc_content) if config.get("include_best_practices") else [],
            "cost_considerations": extract_cost_considerations(doc_content) if config.get("include_cost_analysis") else [],
            "security_recommendations": extract_security_recommendations(doc_content) if config.get("include_security") else []
        },
        
        "implementation_guide": generate_implementation_guide(doc_content, config) if config.get("include_implementation_steps", True) else None,
        
        "search_results": convert_to_dict(search_results) if config.get("include_raw_docs", False) else None,
        
        "raw_documents": doc_content if config.get("include_raw_docs", False) else None
    }
    
    # Remove None values based on output format
    output_format = config.get("output_format", "comprehensive")
    if output_format == "summary":
        formatted_output = create_summary_output(formatted_output)
    elif output_format == "minimal":
        formatted_output = create_minimal_output(formatted_output)
    
    return formatted_output


def extract_key_services(doc_content: List[Dict[str, Any]]) -> List[str]:
    """Extract key AWS services mentioned in documents"""
    aws_services = set()
    
    # Common AWS service patterns
    service_patterns = [
        r'\bEC2\b', r'\bS3\b', r'\bRDS\b', r'\bLambda\b', r'\bVPC\b',
        r'\bCloudFront\b', r'\bRoute 53\b', r'\bELB\b', r'\bALB\b', r'\bNLB\b',
        r'\bAutoScaling\b', r'\bCloudWatch\b', r'\bIAM\b', r'\bKMS\b',
        r'\bDynamoDB\b', r'\bRedshift\b', r'\bKinesis\b', r'\bSNS\b', r'\bSQS\b',
        r'\bAPI Gateway\b', r'\bCloudFormation\b', r'\bECS\b', r'\bEKS\b',
        r'\bElastiCache\b', r'\bOpenSearch\b', r'\bQuickSight\b'
    ]
    
    for doc in doc_content:
        content = doc.get('content', '') + ' ' + doc.get('title', '')
        for pattern in service_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            aws_services.update([match.upper() for match in matches])
    
    return sorted(list(aws_services))


def generate_usecase_summary(usecase_data: Dict[str, Any], config: Dict[str, Any]) -> Dict[str, Any]:
    """Generate a comprehensive use case summary"""
    return {
        "description": usecase_data.get("usecase_description", ""),
        "key_objectives": usecase_data.get("key_objectives", []),
        "target_architecture": usecase_data.get("target_architecture", ""),
        "estimated_complexity": usecase_data.get("complexity_assessment", "Medium"),
        "estimated_cost_range": usecase_data.get("cost_estimate", "Variable"),
        "implementation_timeline": usecase_data.get("timeline_estimate", "2-4 weeks"),
        "prerequisites": usecase_data.get("prerequisites", []),
        "key_considerations": usecase_data.get("key_considerations", [])
    }


def generate_architecture_overview(doc_content: List[Dict[str, Any]], key_services: List[str]) -> Dict[str, Any]:
    """Generate architecture overview from documents"""
    architecture_components = []
    data_flow = []
    security_layers = []
    
    for doc in doc_content:
        content = doc.get('content', '')
        
        # Extract architecture components
        if any(keyword in content.lower() for keyword in ['architecture', 'component', 'tier', 'layer']):
            architecture_components.append({
                "component": doc.get('title', 'Component'),
                "description": content[:200] + "..." if len(content) > 200 else content,
                "services": [svc for svc in key_services if svc.lower() in content.lower()]
            })
        
        # Extract data flow information
        if any(keyword in content.lower() for keyword in ['flow', 'pipeline', 'process', 'workflow']):
            data_flow.append({
                "step": doc.get('title', 'Process Step'),
                "description": content[:150] + "..." if len(content) > 150 else content
            })
        
        # Extract security layers
        if any(keyword in content.lower() for keyword in ['security', 'encryption', 'access', 'authentication']):
            security_layers.append({
                "layer": doc.get('title', 'Security Layer'),
                "description": content[:150] + "..." if len(content) > 150 else content
            })
    
    return {
        "key_services": key_services,
        "architecture_components": architecture_components[:5],  # Limit to top 5
        "data_flow": data_flow[:3],  # Limit to top 3
        "security_layers": security_layers[:3]  # Limit to top 3
    }


def format_main_documents(main_documents: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Format main documents for output"""
    formatted_docs = []
    
    for doc in main_documents:
        formatted_doc = {
            "title": doc.get('title', 'Untitled'),
            "content": doc.get('content', ''),
            "source": doc.get('source', 'Unknown'),
            "relevance_score": doc.get('similarity', 0.0),
            "key_points": extract_key_points(doc.get('content', '')),
            "related_services": extract_services_from_text(doc.get('content', ''))
        }
        formatted_docs.append(formatted_doc)
    
    return formatted_docs


def format_recommendations(recommendations: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Format recommendations for output"""
    formatted_recs = []
    
    for rec in recommendations:
        formatted_rec = {
            "title": rec.get('title', 'Recommendation'),
            "description": rec.get('content', ''),
            "priority": rec.get('priority', 'Medium'),
            "category": rec.get('category', 'General'),
            "implementation_effort": rec.get('effort', 'Medium'),
            "related_services": extract_services_from_text(rec.get('content', ''))
        }
        formatted_recs.append(formatted_rec)
    
    return formatted_recs


def extract_best_practices(doc_content: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Extract best practices from documents"""
    best_practices = []
    
    for doc in doc_content:
        content = doc.get('content', '').lower()
        if any(keyword in content for keyword in ['best practice', 'recommendation', 'should', 'must']):
            best_practices.append({
                "practice": doc.get('title', 'Best Practice'),
                "description": doc.get('content', '')[:300] + "..." if len(doc.get('content', '')) > 300 else doc.get('content', ''),
                "category": categorize_best_practice(doc.get('content', '')),
                "importance": "High" if any(word in content for word in ['critical', 'essential', 'must']) else "Medium"
            })
    
    return best_practices[:10]  # Limit to top 10


def extract_cost_considerations(doc_content: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Extract cost-related information from documents"""
    cost_items = []
    
    for doc in doc_content:
        content = doc.get('content', '').lower()
        if any(keyword in content for keyword in ['cost', 'pricing', 'billing', 'optimize', 'savings']):
            cost_items.append({
                "consideration": doc.get('title', 'Cost Consideration'),
                "description": doc.get('content', '')[:250] + "..." if len(doc.get('content', '')) > 250 else doc.get('content', ''),
                "impact": assess_cost_impact(doc.get('content', '')),
                "optimization_potential": "High" if 'optimize' in content or 'savings' in content else "Medium"
            })
    
    return cost_items[:8]  # Limit to top 8


def extract_security_recommendations(doc_content: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Extract security recommendations from documents"""
    security_items = []
    
    for doc in doc_content:
        content = doc.get('content', '').lower()
        if any(keyword in content for keyword in ['security', 'encryption', 'access', 'authentication', 'authorization', 'compliance']):
            security_items.append({
                "recommendation": doc.get('title', 'Security Recommendation'),
                "description": doc.get('content', '')[:250] + "..." if len(doc.get('content', '')) > 250 else doc.get('content', ''),
                "security_domain": categorize_security_domain(doc.get('content', '')),
                "priority": "High" if any(word in content for word in ['critical', 'vulnerable', 'risk']) else "Medium"
            })
    
    return security_items[:8]  # Limit to top 8


def generate_implementation_guide(doc_content: List[Dict[str, Any]], config: Dict[str, Any]) -> Dict[str, Any]:
    """Generate implementation guide from documents"""
    steps = []
    prerequisites = []
    considerations = []
    
    for doc in doc_content:
        content = doc.get('content', '').lower()
        
        if any(keyword in content for keyword in ['step', 'implement', 'setup', 'configure']):
            steps.append({
                "step": len(steps) + 1,
                "title": doc.get('title', f'Step {len(steps) + 1}'),
                "description": doc.get('content', '')[:200] + "..." if len(doc.get('content', '')) > 200 else doc.get('content', ''),
                "estimated_time": "30-60 minutes"  # Default estimate
            })
        
        if any(keyword in content for keyword in ['prerequisite', 'requirement', 'before']):
            prerequisites.append(doc.get('title', 'Prerequisite'))
        
        if any(keyword in content for keyword in ['consider', 'important', 'note']):
            considerations.append(doc.get('content', '')[:150] + "..." if len(doc.get('content', '')) > 150 else doc.get('content', ''))
    
    return {
        "prerequisites": prerequisites[:5],
        "implementation_steps": steps[:10],
        "key_considerations": considerations[:5],
        "estimated_total_time": f"{len(steps) * 45} minutes"
    }


def extract_key_points(content: str) -> List[str]:
    """Extract key points from content"""
    # Simple extraction based on sentence structure
    sentences = content.split('.')
    key_points = []
    
    for sentence in sentences:
        sentence = sentence.strip()
        if (len(sentence) > 20 and 
            any(keyword in sentence.lower() for keyword in ['important', 'key', 'essential', 'critical', 'must', 'should'])):
            key_points.append(sentence + '.')
    
    return key_points[:3]  # Limit to top 3


def extract_services_from_text(content: str) -> List[str]:
    """Extract AWS services mentioned in text"""
    services = []
    service_patterns = [
        r'\bEC2\b', r'\bS3\b', r'\bRDS\b', r'\bLambda\b', r'\bVPC\b',
        r'\bCloudFront\b', r'\bELB\b', r'\bAutoScaling\b', r'\bCloudWatch\b'
    ]
    
    for pattern in service_patterns:
        matches = re.findall(pattern, content, re.IGNORECASE)
        services.extend([match.upper() for match in matches])
    
    return list(set(services))


def categorize_best_practice(content: str) -> str:
    """Categorize best practice by content"""
    content_lower = content.lower()
    
    if any(keyword in content_lower for keyword in ['security', 'encryption', 'access']):
        return "Security"
    elif any(keyword in content_lower for keyword in ['performance', 'optimize', 'scale']):
        return "Performance"
    elif any(keyword in content_lower for keyword in ['cost', 'billing', 'savings']):
        return "Cost Optimization"
    elif any(keyword in content_lower for keyword in ['monitor', 'alert', 'log']):
        return "Monitoring"
    else:
        return "General"


def assess_cost_impact(content: str) -> str:
    """Assess cost impact from content"""
    content_lower = content.lower()
    
    if any(keyword in content_lower for keyword in ['expensive', 'high cost', 'significant']):
        return "High"
    elif any(keyword in content_lower for keyword in ['savings', 'optimize', 'reduce']):
        return "Savings Opportunity"
    else:
        return "Medium"


def categorize_security_domain(content: str) -> str:
    """Categorize security recommendation by domain"""
    content_lower = content.lower()
    
    if any(keyword in content_lower for keyword in ['encryption', 'kms', 'ssl', 'tls']):
        return "Data Protection"
    elif any(keyword in content_lower for keyword in ['iam', 'access', 'permission', 'role']):
        return "Identity & Access"
    elif any(keyword in content_lower for keyword in ['network', 'vpc', 'security group', 'nacl']):
        return "Network Security"
    elif any(keyword in content_lower for keyword in ['compliance', 'audit', 'governance']):
        return "Compliance"
    else:
        return "General Security"


def create_summary_output(full_output: Dict[str, Any]) -> Dict[str, Any]:
    """Create summary version of output"""
    return {
        "metadata": full_output["metadata"],
        "usecase_summary": full_output["usecase_summary"],
        "key_services": full_output["architecture_overview"]["key_services"],
        "main_recommendations": full_output["documentation"]["recommendations"][:3],
        "implementation_steps": full_output.get("implementation_guide", {}).get("implementation_steps", [])[:5]
    }


def create_minimal_output(full_output: Dict[str, Any]) -> Dict[str, Any]:
    """Create minimal version of output"""
    return {
        "query": full_output["metadata"]["original_query"],
        "key_services": full_output["architecture_overview"]["key_services"],
        "summary": full_output["usecase_summary"]["description"],
        "top_recommendations": [rec["title"] for rec in full_output["documentation"]["recommendations"][:3]]
    }


# Backward compatibility
def format_output_data(
    search_results: Any, 
    doc_content: list, 
    config: Dict[str, Any]
) -> Dict[str, Any]:
    """Backward compatibility function - converts old format to new"""
    
    # Convert old format to new usecase format
    usecase_data = {
        "original_query": f"Provide {config.get('service', 'AWS')} {config.get('posture', 'security')} best practices for {config.get('sub_posture', 'IAM')}",
        "doc_content": doc_content,
        "search_results": search_results,
        "enhanced_by_bedrock": False,
        "new_documents": len([d for d in doc_content if d.get('type') == 'main_content']),
        "duplicate_documents": 0
    }
    
    # Convert config to new format
    new_config = {
        "user_query": usecase_data["original_query"],
        "use_bedrock": False,
        "include_best_practices": True,
        "include_cost_analysis": False,
        "include_security": config.get('posture') == 'security',
        "output_format": "comprehensive"
    }
    
    return format_usecase_output_data(usecase_data, new_config)