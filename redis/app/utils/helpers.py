"""
Helper utilities for the AWS Use Case Documentation Streamlit app
"""

import streamlit as st
from typing import Dict, Any, Optional, List, Tuple
import re
import json
from datetime import datetime
import hashlib


class SessionManager:
    """Manage Streamlit session state for use case documentation"""
    
    @staticmethod
    def initialize_session():
        """Initialize session state variables for use case app"""
        # Current use case data
        if 'current_usecase_data' not in st.session_state:
            st.session_state['current_usecase_data'] = None
        
        # Last configuration used
        if 'last_usecase_config' not in st.session_state:
            st.session_state['last_usecase_config'] = {}
        
        # Search history
        if 'search_history' not in st.session_state:
            st.session_state['search_history'] = []
        
        # Active tab tracking
        if 'active_tab' not in st.session_state:
            st.session_state['active_tab'] = 'current_usecase'
        
        # Processing status
        if 'processing_status' not in st.session_state:
            st.session_state['processing_status'] = {}
        
        # User preferences
        if 'user_preferences' not in st.session_state:
            st.session_state['user_preferences'] = {
                'auto_refine': True,
                'use_bedrock': True,
                'include_best_practices': True,
                'default_max_docs': 10
            }
        
        # Recent queries cache
        if 'recent_queries_cache' not in st.session_state:
            st.session_state['recent_queries_cache'] = []
        
        # Vector search settings
        if 'vector_search_settings' not in st.session_state:
            st.session_state['vector_search_settings'] = {
                'similarity_threshold': 0.3,
                'max_results': 10,
                'enable_reranking': True
            }
    
    @staticmethod
    def update_current_usecase_data(data: Optional[Dict[str, Any]]):
        """Update current use case data in session"""
        st.session_state['current_usecase_data'] = data
        if data:
            # Update last successful processing timestamp
            st.session_state['processing_status']['last_success'] = datetime.now().isoformat()
    
    @staticmethod
    def get_current_usecase_data() -> Optional[Dict[str, Any]]:
        """Get current use case data from session"""
        return st.session_state.get('current_usecase_data')
    
    @staticmethod
    def clear_current_usecase_data():
        """Clear current use case data from session"""
        st.session_state['current_usecase_data'] = None
    
    @staticmethod
    def has_current_usecase_data() -> bool:
        """Check if current use case data exists and is not None"""
        current_data = st.session_state.get('current_usecase_data')
        return current_data is not None and current_data != {}
    
    @staticmethod
    def add_to_search_history(query: str, results_count: int = 0):
        """Add search query to history"""
        search_entry = {
            'query': query,
            'timestamp': datetime.now().isoformat(),
            'results_count': results_count
        }
        
        # Avoid duplicates
        history = st.session_state.get('search_history', [])
        if not any(entry['query'] == query for entry in history[-5:]):  # Check last 5
            history.append(search_entry)
            # Keep only last 20 searches
            st.session_state['search_history'] = history[-20:]
    
    @staticmethod
    def get_search_history() -> List[Dict[str, Any]]:
        """Get search history"""
        return st.session_state.get('search_history', [])
    
    @staticmethod
    def update_user_preferences(preferences: Dict[str, Any]):
        """Update user preferences"""
        current_prefs = st.session_state.get('user_preferences', {})
        current_prefs.update(preferences)
        st.session_state['user_preferences'] = current_prefs
    
    @staticmethod
    def get_user_preferences() -> Dict[str, Any]:
        """Get user preferences"""
        return st.session_state.get('user_preferences', {})
    
    @staticmethod
    def set_processing_status(status: str, message: str = ""):
        """Set processing status"""
        st.session_state['processing_status'] = {
            'status': status,
            'message': message,
            'timestamp': datetime.now().isoformat()
        }
    
    @staticmethod
    def get_processing_status() -> Dict[str, Any]:
        """Get processing status"""
        return st.session_state.get('processing_status', {})
    
    @staticmethod
    def update_recent_queries_cache(queries: List[Dict[str, Any]]):
        """Update recent queries cache"""
        st.session_state['recent_queries_cache'] = queries
    
    @staticmethod
    def get_recent_queries_cache() -> List[Dict[str, Any]]:
        """Get recent queries cache"""
        return st.session_state.get('recent_queries_cache', [])


class UsecaseConfigValidator:
    """Validate use case configuration inputs"""
    
    @staticmethod
    def validate_usecase_config(config: Dict[str, Any]) -> Tuple[bool, str]:
        """Validate use case configuration parameters"""
        if not config or not isinstance(config, dict):
            return False, "Configuration is required"
        
        # Validate user query
        user_query = config.get('user_query', '').strip()
        if not user_query:
            return False, "Use case query is required"
        
        if len(user_query) < 10:
            return False, "Use case query must be at least 10 characters long"
        
        if len(user_query) > 500:
            return False, "Use case query must be less than 500 characters"
        
        # Validate MCP URL
        mcp_url = config.get('mcp_url', '')
        if not mcp_url:
            return False, "MCP URL is required"
        
        if not (mcp_url.startswith('http://') or mcp_url.startswith('https://')):
            return False, "MCP URL must start with http:// or https://"
        
        # Validate numeric parameters
        max_docs = config.get('max_documents', 10)
        if not isinstance(max_docs, int) or max_docs < 1 or max_docs > 50:
            return False, "Max documents must be between 1 and 50"
        
        max_recs = config.get('max_recommendations_per_doc', 3)
        if not isinstance(max_recs, int) or max_recs < 1 or max_recs > 10:
            return False, "Max recommendations per document must be between 1 and 10"
        
        similarity_threshold = config.get('similarity_threshold', 0.3)
        if not isinstance(similarity_threshold, (int, float)) or not (0.1 <= similarity_threshold <= 1.0):
            return False, "Similarity threshold must be between 0.1 and 1.0"
        
        return True, "Configuration is valid"
    
    @staticmethod
    def validate_search_query(query: str) -> Tuple[bool, str]:
        """Validate search query"""
        if not query or not isinstance(query, str):
            return False, "Search query is required"
        
        query = query.strip()
        if len(query) < 3:
            return False, "Search query must be at least 3 characters long"
        
        if len(query) > 200:
            return False, "Search query must be less than 200 characters"
        
        # Check for potentially problematic characters
        if re.search(r'[<>{}[\]\\]', query):
            return False, "Search query contains invalid characters"
        
        return True, "Search query is valid"
    
    @staticmethod
    def sanitize_user_input(input_text: str) -> str:
        """Sanitize user input for safety"""
        if not isinstance(input_text, str):
            return ""
        
        # Remove potentially dangerous characters
        sanitized = re.sub(r'[<>{}[\]\\]', '', input_text)
        
        # Limit length
        sanitized = sanitized[:1000]
        
        # Strip whitespace
        return sanitized.strip()
    
    @staticmethod
    def validate_aws_services(services: List[str]) -> Tuple[bool, str]:
        """Validate AWS services list"""
        if not isinstance(services, list):
            return False, "Services must be a list"
        
        # Known AWS services for validation
        valid_services = {
            'EC2', 'S3', 'RDS', 'Lambda', 'VPC', 'CloudFront', 'Route53',
            'ELB', 'ALB', 'NLB', 'AutoScaling', 'CloudWatch', 'IAM', 'KMS',
            'DynamoDB', 'Redshift', 'Kinesis', 'SNS', 'SQS', 'API Gateway',
            'CloudFormation', 'ECS', 'EKS', 'ElastiCache', 'OpenSearch',
            'QuickSight', 'Glue', 'EMR', 'SageMaker', 'Bedrock'
        }
        
        invalid_services = [svc for svc in services if svc not in valid_services]
        if invalid_services:
            return False, f"Invalid AWS services: {', '.join(invalid_services)}"
        
        return True, "AWS services are valid"


class UIHelpers:
    """UI helper functions for use case documentation"""
    
    @staticmethod
    def show_success_message(message: str):
        """Show success message"""
        st.success(f"✅ {message}")
    
    @staticmethod
    def show_error_message(message: str):
        """Show error message"""
        st.error(f"❌ {message}")
    
    @staticmethod
    def show_info_message(message: str):
        """Show info message"""
        st.info(f"ℹ️ {message}")
    
    @staticmethod
    def show_warning_message(message: str):
        """Show warning message"""
        st.warning(f"⚠️ {message}")
    
    @staticmethod
    def show_processing_message(message: str):
        """Show processing message with spinner"""
        return st.spinner(f"🔄 {message}")
    
    @staticmethod
    def safe_get(data: Optional[Dict[str, Any]], key: str, default: Any = None) -> Any:
        """Safely get value from dictionary that might be None"""
        if data is None or not isinstance(data, dict):
            return default
        return data.get(key, default)
    
    @staticmethod
    def format_timestamp(timestamp: str) -> str:
        """Format timestamp for display"""
        try:
            dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            return dt.strftime("%Y-%m-%d %H:%M:%S")
        except (ValueError, AttributeError):
            return timestamp
    
    @staticmethod
    def truncate_text(text: str, max_length: int = 100, suffix: str = "...") -> str:
        """Truncate text to specified length"""
        if not isinstance(text, str):
            return str(text)
        
        if len(text) <= max_length:
            return text
        
        return text[:max_length - len(suffix)] + suffix
    
    @staticmethod
    def create_download_button(data: Dict[str, Any], filename: str, label: str = "Download"):
        """Create download button for data"""
        json_data = json.dumps(data, indent=2, default=str)
        
        st.download_button(
            label=f"📥 {label}",
            data=json_data,
            file_name=filename,
            mime="application/json"
        )
    
    @staticmethod
    def display_metrics_row(metrics: Dict[str, Any], columns: int = 4):
        """Display metrics in a row"""
        cols = st.columns(columns)
        
        for i, (label, value) in enumerate(metrics.items()):
            with cols[i % columns]:
                st.metric(label, value)
    
    @staticmethod
    def create_expandable_section(title: str, content: str, expanded: bool = False):
        """Create expandable section with content"""
        with st.expander(title, expanded=expanded):
            st.markdown(content)
    
    @staticmethod
    def display_key_value_pairs(data: Dict[str, Any], title: str = "Details"):
        """Display key-value pairs in a formatted way"""
        st.subheader(title)
        
        for key, value in data.items():
            if isinstance(value, (list, dict)):
                st.markdown(f"**{key}:**")
                st.json(value)
            else:
                st.markdown(f"**{key}:** {value}")
    
    @staticmethod
    def create_progress_indicator(current: int, total: int, label: str = "Progress"):
        """Create progress indicator"""
        progress = current / total if total > 0 else 0
        st.progress(progress, text=f"{label}: {current}/{total}")
    
    @staticmethod
    def display_status_badge(status: str) -> str:
        """Display status badge with appropriate emoji"""
        status_map = {
            'success': '✅',
            'error': '❌',
            'warning': '⚠️',
            'info': 'ℹ️',
            'processing': '🔄',
            'pending': '⏳',
            'completed': '✅',
            'failed': '❌'
        }
        
        emoji = status_map.get(status.lower(), '📋')
        return f"{emoji} {status.title()}"


class UsecaseAnalyzer:
    """Analyze and categorize use cases"""
    
    @staticmethod
    def categorize_usecase(query: str) -> str:
        """Categorize use case based on query content"""
        query_lower = query.lower()
        
        # Web application patterns
        if any(keyword in query_lower for keyword in ['web', 'website', 'application', 'app', 'frontend']):
            return "Web Application"
        
        # Data and analytics patterns
        elif any(keyword in query_lower for keyword in ['data', 'analytics', 'pipeline', 'etl', 'warehouse', 'lake']):
            return "Data & Analytics"
        
        # Serverless patterns
        elif any(keyword in query_lower for keyword in ['serverless', 'lambda', 'function', 'event-driven']):
            return "Serverless"
        
        # Security patterns
        elif any(keyword in query_lower for keyword in ['security', 'secure', 'encryption', 'compliance', 'audit']):
            return "Security"
        
        # Machine learning patterns
        elif any(keyword in query_lower for keyword in ['ml', 'machine learning', 'ai', 'model', 'training']):
            return "Machine Learning"
        
        # Microservices patterns
        elif any(keyword in query_lower for keyword in ['microservice', 'container', 'docker', 'kubernetes', 'api']):
            return "Microservices"
        
        # DevOps patterns
        elif any(keyword in query_lower for keyword in ['devops', 'ci/cd', 'deployment', 'automation']):
            return "DevOps"
        
        # IoT patterns
        elif any(keyword in query_lower for keyword in ['iot', 'sensor', 'device', 'telemetry']):
            return "IoT"
        
        else:
            return "General"
    
    @staticmethod
    def extract_complexity_indicators(query: str) -> str:
        """Extract complexity indicators from query"""
        query_lower = query.lower()
        
        # High complexity indicators
        high_complexity = ['enterprise', 'large scale', 'multi-region', 'high availability', 'disaster recovery']
        if any(indicator in query_lower for indicator in high_complexity):
            return "High"
        
        # Low complexity indicators
        low_complexity = ['simple', 'basic', 'small', 'prototype', 'poc', 'proof of concept']
        if any(indicator in query_lower for indicator in low_complexity):
            return "Low"
        
        return "Medium"
    
    @staticmethod
    def estimate_timeline(query: str, complexity: str) -> str:
        """Estimate implementation timeline"""
        base_times = {
            "Low": "1-2 weeks",
            "Medium": "2-4 weeks", 
            "High": "4-8 weeks"
        }
        
        query_lower = query.lower()
        
        # Adjust for specific patterns
        if any(keyword in query_lower for keyword in ['migration', 'legacy', 'enterprise']):
            return "6-12 weeks"
        elif any(keyword in query_lower for keyword in ['prototype', 'poc', 'demo']):
            return "1-2 weeks"
        
        return base_times.get(complexity, "2-4 weeks")
    
    @staticmethod
    def suggest_key_services(query: str) -> List[str]:
        """Suggest key AWS services based on query"""
        query_lower = query.lower()
        suggested_services = []
        
        # Core compute services
        if any(keyword in query_lower for keyword in ['server', 'compute', 'instance', 'vm']):
            suggested_services.append('EC2')
        
        if any(keyword in query_lower for keyword in ['serverless', 'function', 'lambda']):
            suggested_services.append('Lambda')
        
        # Storage services
        if any(keyword in query_lower for keyword in ['storage', 'file', 'object', 'backup']):
            suggested_services.append('S3')
        
        # Database services
        if any(keyword in query_lower for keyword in ['database', 'db', 'sql', 'mysql', 'postgres']):
            suggested_services.append('RDS')
        
        if any(keyword in query_lower for keyword in ['nosql', 'dynamodb', 'document']):
            suggested_services.append('DynamoDB')
        
        # Networking services
        if any(keyword in query_lower for keyword in ['network', 'vpc', 'subnet', 'security']):
            suggested_services.append('VPC')
        
        if any(keyword in query_lower for keyword in ['load balancer', 'load balancing', 'elb']):
            suggested_services.append('ELB')
        
        # Content delivery
        if any(keyword in query_lower for keyword in ['cdn', 'content delivery', 'cloudfront']):
            suggested_services.append('CloudFront')
        
        # Monitoring
        if any(keyword in query_lower for keyword in ['monitor', 'alert', 'log', 'metric']):
            suggested_services.append('CloudWatch')
        
        # Security
        if any(keyword in query_lower for keyword in ['security', 'access', 'permission', 'role']):
            suggested_services.append('IAM')
        
        return list(set(suggested_services))  # Remove duplicates


# Backward compatibility aliases
ConfigValidator = UsecaseConfigValidator