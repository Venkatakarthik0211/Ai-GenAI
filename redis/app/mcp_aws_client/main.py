#!/usr/bin/env python3
"""
Main entry point for MCP AWS Use Case Client
"""

import asyncio
import json
import argparse
from pathlib import Path

from .client.mcp_client import MCPClient
from .config.config_loader import load_config
from .processors.usecase_processor import UsecaseProcessor
from .processors.data_converter import format_usecase_output_data
from .utils.testing import test_connection, run_diagnostic_tests


async def main():
    """Main function"""
    parser = argparse.ArgumentParser(description="AWS MCP Use Case Client")
    parser.add_argument("--test", action="store_true", help="Run connection tests")
    parser.add_argument("--diagnostic", action="store_true", help="Run diagnostic tests")
    parser.add_argument("--config", default="usecase_config.yaml", help="Use case config file path")
    parser.add_argument("--url", default="http://localhost:5000", help="Server URL")
    parser.add_argument("--output", default="aws_usecase_output.json", help="Output file")
    parser.add_argument("--max-docs", type=int, default=10, help="Maximum documents to process")
    parser.add_argument("--max-recs", type=int, default=3, help="Maximum recommendations per document")
    parser.add_argument("--use-bedrock", action="store_true", help="Enable Bedrock AI enhancement")
    parser.add_argument("--auto-refine", action="store_true", help="Auto-refine use case query")
    parser.add_argument("--include-best-practices", action="store_true", default=True, help="Include best practices")
    parser.add_argument("--include-cost-analysis", action="store_true", help="Include cost considerations")
    parser.add_argument("--include-security", action="store_true", help="Include security recommendations")
    
    # Use case input options
    parser.add_argument("--query", help="Use case query (overrides config)")
    parser.add_argument("--interactive", action="store_true", help="Interactive mode for use case input")
    
    args = parser.parse_args()
    
    if args.test:
        success = await test_connection(args.url)
        return 0 if success else 1
    
    if args.diagnostic:
        results = await run_diagnostic_tests(args.url)
        print(f"\n📊 Diagnostic Results:")
        print(json.dumps(results, indent=2))
        return 0 if results["connection"] else 1
    
    # Interactive mode for use case input
    if args.interactive:
        print("🎯 AWS Use Case Documentation Generator")
        print("=" * 50)
        user_query = input("Describe your AWS use case: ")
        if not user_query.strip():
            print("❌ No use case provided, exiting...")
            return 1
        args.query = user_query
    
    # Load configuration
    config = load_config(args.config)
    
    # Override with command line query if provided
    if args.query:
        config["user_query"] = args.query
    
    # Validate use case query
    if not config.get("user_query"):
        print("❌ No use case query provided. Use --query, --interactive, or specify in config file.")
        return 1
    
    print(f"📋 Use Case Config: {config}")
    
    # Initialize client and processor
    client = MCPClient(args.url)
    
    async with client:
        # Check server health first
        health = await client.health_check()
        print(f"🏥 Server health: {health}")
        
        if health.get('status') != 'ok':
            print("❌ Server is not healthy, exiting...")
            return 1
        
        # Check Bedrock availability if requested
        if args.use_bedrock:
            bedrock_status = await client.check_bedrock_status()
            if not bedrock_status.get('available', False):
                print("⚠️ Bedrock not available, continuing without AI enhancement...")
                args.use_bedrock = False
            else:
                print("🤖 Bedrock AI enhancement enabled")
        
        # Initialize use case processor
        processor = UsecaseProcessor(
            client,
            use_bedrock=args.use_bedrock,
            auto_refine=args.auto_refine
        )
        
        # Prepare use case configuration
        usecase_config = {
            "user_query": config.get("user_query"),
            "use_bedrock": args.use_bedrock,
            "auto_refine": args.auto_refine,
            "include_best_practices": args.include_best_practices,
            "include_cost_analysis": args.include_cost_analysis,
            "include_security": args.include_security,
            "max_documents": args.max_docs,
            "max_recommendations_per_doc": args.max_recs
        }
        
        print(f"🎯 Processing use case: {config.get('user_query')}")
        
        # Process use case
        try:
            output_data = await processor.generate_usecase_documentation(usecase_config)
            
            if "error" in output_data:
                print(f"❌ Processing failed: {output_data['error']}")
                return 1
            
            # Format final output
            formatted_output = format_usecase_output_data(
                output_data,
                usecase_config
            )
            
            # Print comprehensive summary
            summary = processor.get_usecase_processing_summary(output_data)
            print(f"\n📊 Use Case Processing Summary:")
            print(f"  🎯 Original Query: {summary.get('original_query', 'N/A')}")
            
            if summary.get('query_refined'):
                print(f"  ✨ Refined Query: {summary.get('refined_query', 'N/A')}")
            
            if summary.get('enhanced_by_bedrock'):
                print(f"  🤖 Bedrock Enhanced: Yes")
            
            print(f"  📚 Documents Found: {summary.get('total_documents', 0)}")
            print(f"  📄 New Documents: {summary.get('new_documents', 0)}")
            print(f"  🔄 Duplicates Skipped: {summary.get('duplicate_documents', 0)}")
            print(f"  💡 Recommendations: {summary.get('total_recommendations', 0)}")
            print(f"  🔧 Key Services: {', '.join(summary.get('key_services', [])[:5])}")
            
            if summary.get('usecase_summary'):
                print(f"  📋 Use Case Summary: {summary['usecase_summary'][:100]}...")
            
            # Architecture insights
            if summary.get('architecture_insights'):
                print(f"  🏗️ Architecture Insights: {len(summary['architecture_insights'])} components")
            
            # Cost considerations
            if summary.get('cost_considerations'):
                print(f"  💰 Cost Considerations: {len(summary['cost_considerations'])} items")
            
            # Security recommendations
            if summary.get('security_recommendations'):
                print(f"  🔒 Security Recommendations: {len(summary['security_recommendations'])} items")
            
            # Save results
            output_file = Path(args.output)
            with open(output_file, 'w') as f:
                json.dump(formatted_output, f, indent=2, default=str)
            print(f"  💾 Results saved to: {output_file}")
            
            # Save metadata separately for debugging
            metadata_file = output_file.with_suffix('.metadata.json')
            with open(metadata_file, 'w') as f:
                json.dump(summary, f, indent=2, default=str)
            print(f"  📋 Metadata saved to: {metadata_file}")
            
            return 0
            
        except Exception as e:
            print(f"❌ Processing error: {str(e)}")
            import traceback
            traceback.print_exc()
            return 1


async def run_batch_usecases():
    """Run multiple use cases from a batch file"""
    parser = argparse.ArgumentParser(description="AWS MCP Batch Use Case Client")
    parser.add_argument("--batch-file", required=True, help="JSON file with multiple use cases")
    parser.add_argument("--url", default="http://localhost:5000", help="Server URL")
    parser.add_argument("--output-dir", default="batch_output", help="Output directory")
    parser.add_argument("--use-bedrock", action="store_true", help="Enable Bedrock AI enhancement")
    
    args = parser.parse_args()
    
    # Load batch file
    try:
        with open(args.batch_file, 'r') as f:
            batch_data = json.load(f)
    except Exception as e:
        print(f"❌ Error loading batch file: {str(e)}")
        return 1
    
    # Create output directory
    output_dir = Path(args.output_dir)
    output_dir.mkdir(exist_ok=True)
    
    # Initialize client
    client = MCPClient(args.url)
    
    async with client:
        # Check server health
        health = await client.health_check()
        if health.get('status') != 'ok':
            print("❌ Server is not healthy, exiting...")
            return 1
        
        processor = UsecaseProcessor(client, use_bedrock=args.use_bedrock)
        
        results = []
        
        for i, usecase in enumerate(batch_data.get('use_cases', []), 1):
            print(f"\n🎯 Processing use case {i}/{len(batch_data['use_cases'])}")
            print(f"Query: {usecase.get('query', 'N/A')}")
            
            try:
                usecase_config = {
                    "user_query": usecase.get('query'),
                    "use_bedrock": args.use_bedrock,
                    "auto_refine": usecase.get('auto_refine', True),
                    "include_best_practices": usecase.get('include_best_practices', True),
                    "include_cost_analysis": usecase.get('include_cost_analysis', False),
                    "include_security": usecase.get('include_security', False),
                    "max_documents": usecase.get('max_documents', 10),
                    "max_recommendations_per_doc": usecase.get('max_recommendations_per_doc', 3)
                }
                
                output_data = await processor.generate_usecase_documentation(usecase_config)
                
                if "error" not in output_data:
                    # Format and save individual result
                    formatted_output = format_usecase_output_data(output_data, usecase_config)
                    
                    output_file = output_dir / f"usecase_{i:03d}.json"
                    with open(output_file, 'w') as f:
                        json.dump(formatted_output, f, indent=2, default=str)
                    
                    summary = processor.get_usecase_processing_summary(output_data)
                    results.append({
                        "usecase_id": i,
                        "query": usecase.get('query'),
                        "status": "success",
                        "summary": summary,
                        "output_file": str(output_file)
                    })
                    
                    print(f"✅ Success: {summary.get('total_documents', 0)} docs, {summary.get('total_recommendations', 0)} recs")
                else:
                    results.append({
                        "usecase_id": i,
                        "query": usecase.get('query'),
                        "status": "error",
                        "error": output_data['error']
                    })
                    print(f"❌ Error: {output_data['error']}")
                    
            except Exception as e:
                results.append({
                    "usecase_id": i,
                    "query": usecase.get('query'),
                    "status": "error",
                    "error": str(e)
                })
                print(f"❌ Exception: {str(e)}")
        
        # Save batch results summary
        batch_summary = {
            "total_usecases": len(batch_data['use_cases']),
            "successful": len([r for r in results if r['status'] == 'success']),
            "failed": len([r for r in results if r['status'] == 'error']),
            "results": results
        }
        
        summary_file = output_dir / "batch_summary.json"
        with open(summary_file, 'w') as f:
            json.dump(batch_summary, f, indent=2, default=str)
        
        print(f"\n📊 Batch Processing Complete:")
        print(f"  ✅ Successful: {batch_summary['successful']}")
        print(f"  ❌ Failed: {batch_summary['failed']}")
        print(f"  📁 Output directory: {output_dir}")
        print(f"  📋 Summary file: {summary_file}")
        
        return 0 if batch_summary['failed'] == 0 else 1


if __name__ == "__main__":
    import sys
    
    # Check if running in batch mode
    if len(sys.argv) > 1 and '--batch-file' in sys.argv:
        exit_code = asyncio.run(run_batch_usecases())
    else:
        exit_code = asyncio.run(main())
    
    exit(exit_code)