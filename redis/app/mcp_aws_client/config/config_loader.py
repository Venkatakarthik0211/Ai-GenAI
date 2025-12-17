"""
Configuration loading utilities for AWS Use Case Documentation
"""

import yaml
from typing import Dict, Any, List, Optional
from pathlib import Path
import os
from datetime import datetime


def load_config(config_path: str = "usecase_config.yaml") -> Dict[str, Any]:
    """Load use case configuration from YAML file"""
    try:
        config_file = Path(config_path)
        if config_file.exists():
            with open(config_file, 'r') as f:
                config = yaml.safe_load(f)
                # Validate and enhance config
                return _validate_and_enhance_config(config)
        else:
            print(f"⚠️ Config file {config_path} not found, using defaults")
            return _get_default_usecase_config()
    except Exception as e:
        print(f"⚠️ Error loading config: {e}, using defaults")
        return _get_default_usecase_config()


def _get_default_usecase_config() -> Dict[str, Any]:
    """Get default use case configuration"""
    return {
        # Main use case configuration
        "user_query": "Build a scalable web application with database and caching",
        
        # AI Enhancement settings
        "use_bedrock": True,
        "auto_refine": True,
        "include_best_practices": True,
        "include_cost_analysis": True,
        "include_security": True,
        
        # Processing settings
        "max_documents": 10,
        "max_recommendations_per_doc": 3,
        "enable_vectors": True,
        "similarity_threshold": 0.3,
        
        # MCP Server settings
        "mcp_url": os.getenv('MCP_SERVER_URL', 'http://localhost:5000'),
        
        # Output settings
        "output_format": "comprehensive",  # comprehensive, summary, minimal
        "include_raw_docs": False,
        "include_metadata": True,
        
        # Filtering settings
        "preferred_services": [],  # Empty means no preference
        "exclude_services": [],
        "focus_areas": [],  # e.g., ["security", "cost", "performance"]
        
        # Advanced settings
        "deduplicate_results": True,
        "merge_similar_recommendations": True,
        "generate_architecture_diagram": False,
        "include_implementation_steps": True
    }


def _validate_and_enhance_config(config: Dict[str, Any]) -> Dict[str, Any]:
    """Validate and enhance configuration with defaults"""
    default_config = _get_default_usecase_config()
    
    # Merge with defaults
    enhanced_config = {**default_config, **config}
    
    # Validate required fields
    if not enhanced_config.get("user_query"):
        print("⚠️ No user_query provided in config, using default")
        enhanced_config["user_query"] = default_config["user_query"]
    
    # Validate numeric fields
    numeric_fields = {
        "max_documents": (1, 50),
        "max_recommendations_per_doc": (1, 10),
        "similarity_threshold": (0.1, 1.0)
    }
    
    for field, (min_val, max_val) in numeric_fields.items():
        value = enhanced_config.get(field)
        if not isinstance(value, (int, float)) or not (min_val <= value <= max_val):
            print(f"⚠️ Invalid {field}: {value}, using default: {default_config[field]}")
            enhanced_config[field] = default_config[field]
    
    # Validate boolean fields
    boolean_fields = [
        "use_bedrock", "auto_refine", "include_best_practices", 
        "include_cost_analysis", "include_security", "enable_vectors",
        "include_raw_docs", "include_metadata", "deduplicate_results",
        "merge_similar_recommendations", "generate_architecture_diagram",
        "include_implementation_steps"
    ]
    
    for field in boolean_fields:
        if not isinstance(enhanced_config.get(field), bool):
            enhanced_config[field] = default_config[field]
    
    # Validate list fields
    list_fields = ["preferred_services", "exclude_services", "focus_areas"]
    for field in list_fields:
        if not isinstance(enhanced_config.get(field), list):
            enhanced_config[field] = default_config[field]
    
    # Validate output format
    valid_formats = ["comprehensive", "summary", "minimal"]
    if enhanced_config.get("output_format") not in valid_formats:
        enhanced_config["output_format"] = default_config["output_format"]
    
    return enhanced_config


def save_config(config: Dict[str, Any], config_path: str = "usecase_config.yaml") -> bool:
    """Save use case configuration to YAML file"""
    try:
        # Add metadata
        config_with_metadata = {
            **config,
            "_metadata": {
                "created_at": datetime.now().isoformat(),
                "config_version": "2.0",
                "config_type": "usecase"
            }
        }
        
        with open(config_path, 'w') as f:
            yaml.safe_dump(config_with_metadata, f, default_flow_style=False, indent=2)
        print(f"✅ Configuration saved to {config_path}")
        return True
    except Exception as e:
        print(f"❌ Error saving config: {e}")
        return False


def load_batch_config(batch_config_path: str = "batch_usecases.yaml") -> Dict[str, Any]:
    """Load batch use case configuration"""
    try:
        config_file = Path(batch_config_path)
        if config_file.exists():
            with open(config_file, 'r') as f:
                batch_config = yaml.safe_load(f)
                return _validate_batch_config(batch_config)
        else:
            print(f"⚠️ Batch config file {batch_config_path} not found, creating example")
            example_config = _get_example_batch_config()
            save_batch_config(example_config, batch_config_path)
            return example_config
    except Exception as e:
        print(f"⚠️ Error loading batch config: {e}, using example")
        return _get_example_batch_config()


def _validate_batch_config(batch_config: Dict[str, Any]) -> Dict[str, Any]:
    """Validate batch configuration"""
    if not isinstance(batch_config.get("use_cases"), list):
        print("⚠️ Invalid batch config: use_cases must be a list")
        return _get_example_batch_config()
    
    # Validate each use case
    validated_cases = []
    for i, use_case in enumerate(batch_config["use_cases"]):
        if not isinstance(use_case, dict) or not use_case.get("query"):
            print(f"⚠️ Skipping invalid use case {i+1}: missing query")
            continue
        
        # Merge with default settings
        default_case = {
            "auto_refine": True,
            "include_best_practices": True,
            "include_cost_analysis": False,
            "include_security": False,
            "max_documents": 10,
            "max_recommendations_per_doc": 3
        }
        validated_case = {**default_case, **use_case}
        validated_cases.append(validated_case)
    
    batch_config["use_cases"] = validated_cases
    
    # Add global settings if not present
    if "global_settings" not in batch_config:
        batch_config["global_settings"] = {
            "use_bedrock": True,
            "enable_vectors": True,
            "output_format": "comprehensive"
        }
    
    return batch_config


def _get_example_batch_config() -> Dict[str, Any]:
    """Get example batch configuration"""
    return {
        "global_settings": {
            "use_bedrock": True,
            "enable_vectors": True,
            "output_format": "comprehensive",
            "mcp_url": "http://localhost:5000"
        },
        "use_cases": [
            {
                "name": "Scalable Web Application",
                "query": "Build a scalable web application with auto-scaling, load balancing, and RDS database",
                "include_best_practices": True,
                "include_cost_analysis": True,
                "include_security": True,
                "focus_areas": ["scalability", "reliability"]
            },
            {
                "name": "Serverless Data Pipeline",
                "query": "Create a serverless data processing pipeline with Lambda, S3, and DynamoDB",
                "include_best_practices": True,
                "include_cost_analysis": True,
                "focus_areas": ["performance", "cost"]
            },
            {
                "name": "Secure Multi-tier App",
                "query": "Set up a secure multi-tier application with VPC, security groups, and encryption",
                "include_best_practices": True,
                "include_security": True,
                "focus_areas": ["security", "compliance"]
            },
            {
                "name": "Cost-Optimized Startup",
                "query": "Design a cost-optimized architecture for a startup with monitoring and alerts",
                "include_best_practices": True,
                "include_cost_analysis": True,
                "focus_areas": ["cost", "monitoring"]
            },
            {
                "name": "Real-time Analytics",
                "query": "Build a real-time analytics dashboard with Kinesis, Lambda, and QuickSight",
                "include_best_practices": True,
                "include_cost_analysis": False,
                "focus_areas": ["performance", "real-time"]
            }
        ]
    }


def save_batch_config(batch_config: Dict[str, Any], batch_config_path: str = "batch_usecases.yaml") -> bool:
    """Save batch use case configuration"""
    try:
        # Add metadata
        batch_config_with_metadata = {
            **batch_config,
            "_metadata": {
                "created_at": datetime.now().isoformat(),
                "config_version": "2.0",
                "config_type": "batch_usecases",
                "total_use_cases": len(batch_config.get("use_cases", []))
            }
        }
        
        with open(batch_config_path, 'w') as f:
            yaml.safe_dump(batch_config_with_metadata, f, default_flow_style=False, indent=2)
        print(f"✅ Batch configuration saved to {batch_config_path}")
        return True
    except Exception as e:
        print(f"❌ Error saving batch config: {e}")
        return False


def get_config_template(config_type: str = "usecase") -> Dict[str, Any]:
    """Get configuration template for different types"""
    if config_type == "usecase":
        return _get_default_usecase_config()
    elif config_type == "batch":
        return _get_example_batch_config()
    else:
        raise ValueError(f"Unknown config type: {config_type}")


def create_config_from_template(config_type: str = "usecase", output_path: Optional[str] = None) -> str:
    """Create configuration file from template"""
    template = get_config_template(config_type)
    
    if output_path is None:
        if config_type == "usecase":
            output_path = "usecase_config.yaml"
        elif config_type == "batch":
            output_path = "batch_usecases.yaml"
    
    if config_type == "usecase":
        success = save_config(template, output_path)
    elif config_type == "batch":
        success = save_batch_config(template, output_path)
    
    if success:
        return output_path
    else:
        raise Exception(f"Failed to create config file: {output_path}")


def update_config_field(config_path: str, field_path: str, value: Any) -> bool:
    """Update a specific field in configuration file"""
    try:
        config = load_config(config_path)
        
        # Handle nested field paths (e.g., "global_settings.use_bedrock")
        keys = field_path.split('.')
        current = config
        
        # Navigate to the parent of the target field
        for key in keys[:-1]:
            if key not in current:
                current[key] = {}
            current = current[key]
        
        # Set the value
        current[keys[-1]] = value
        
        return save_config(config, config_path)
    except Exception as e:
        print(f"❌ Error updating config field {field_path}: {e}")
        return False


def validate_config_compatibility(config: Dict[str, Any]) -> List[str]:
    """Validate configuration compatibility and return warnings"""
    warnings = []
    
    # Check for conflicting settings
    if config.get("use_bedrock") and not config.get("auto_refine"):
        warnings.append("Bedrock is enabled but auto_refine is disabled - consider enabling auto_refine for better results")
    
    if config.get("include_cost_analysis") and not config.get("include_best_practices"):
        warnings.append("Cost analysis is enabled but best practices are disabled - best practices include cost optimization")
    
    if config.get("max_documents", 0) > 20 and not config.get("deduplicate_results"):
        warnings.append("High document count without deduplication may result in redundant information")
    
    if config.get("similarity_threshold", 0) < 0.2:
        warnings.append("Very low similarity threshold may include irrelevant results")
    
    # Check for resource-intensive settings
    if (config.get("max_documents", 0) > 30 and 
        config.get("include_best_practices") and 
        config.get("include_cost_analysis") and 
        config.get("include_security")):
        warnings.append("High document count with all enhancements enabled may take significant time to process")
    
    return warnings


# Backward compatibility
def _get_default_config() -> Dict[str, Any]:
    """Backward compatibility function"""
    return {
        "service": "AWS",
        "posture": "security", 
        "sub_posture": "IAM",
        # Map to new usecase format
        "user_query": "Provide AWS IAM security best practices"
    }