"""
Sidebar components for the Streamlit app with vector capabilities for use cases
"""

import streamlit as st
import os
from typing import Dict, Any, Tuple

from services.redis_service import RedisVectorService
from services.mcp_service import MCPService


class UsecaseSidebarControls:
    """Handle sidebar controls and configuration with vector features for use cases"""

    def __init__(self, redis_service: RedisVectorService):
        self.redis_service = redis_service

    def render_usecase_input_section(self) -> Dict[str, Any]:
        """Render use case input section and return config"""
        st.sidebar.subheader("🎯 Use Case Query")

        # Main use case query input
        user_query = st.sidebar.text_area(
            "Describe your AWS use case:",
            placeholder="e.g., I want to build a scalable web application with database, caching, and CDN...",
            help="Describe what you want to build or achieve with AWS services",
            height=100
        )

        # MCP Server configuration
        mcp_url = st.sidebar.text_input(
            "MCP Server URL",
            value=os.getenv('MCP_SERVER_URL', 'http://localhost:5000'),
            placeholder="http://mcp-server:5000"
        )

        return {
            "user_query": user_query,
            "mcp_url": mcp_url
        }

    def render_ai_enhancement_section(self) -> Dict[str, Any]:
        """Render AI enhancement configuration section"""
        st.sidebar.subheader("🤖 AI Enhancement")
        
        # Bedrock enhancement
        use_bedrock = st.sidebar.checkbox(
            "Use Bedrock for Query Enhancement",
            value=True,
            help="Use AWS Bedrock to refine your query and generate comprehensive documentation"
        )
        
        # Query refinement options
        with st.sidebar.expander("🔧 Enhancement Options"):
            auto_refine = st.sidebar.checkbox(
                "Auto-refine Query",
                value=True,
                help="Automatically improve the query for better results"
            )
            
            include_best_practices = st.sidebar.checkbox(
                "Include Best Practices",
                value=True,
                help="Include AWS best practices in the documentation"
            )
            
            include_cost_analysis = st.sidebar.checkbox(
                "Include Cost Considerations",
                value=True,
                help="Include cost optimization recommendations"
            )
            
            include_security = st.sidebar.checkbox(
                "Include Security Recommendations",
                value=True,
                help="Include security best practices and considerations"
            )

        return {
            "use_bedrock": use_bedrock,
            "auto_refine": auto_refine,
            "include_best_practices": include_best_practices,
            "include_cost_analysis": include_cost_analysis,
            "include_security": include_security
        }

    def render_vector_search_section(self) -> Dict[str, Any]:
        """Render vector search configuration section"""
        st.sidebar.subheader("🧠 Vector Search")
        
        enable_vectors = st.sidebar.checkbox(
            "Enable Vector Embeddings",
            value=True,
            help="Create semantic embeddings for better search capabilities"
        )
        
        with st.sidebar.expander("⚙️ Vector Settings"):
            similarity_threshold = st.slider(
                "Similarity Threshold",
                min_value=0.1,
                max_value=1.0,
                value=0.3,
                step=0.1,
                help="Minimum similarity score for search results"
            )
            
            max_results = st.slider(
                "Max Results",
                min_value=5,
                max_value=50,
                value=20,
                help="Maximum number of documents to retrieve"
            )

        return {
            "enable_vectors": enable_vectors,
            "similarity_threshold": similarity_threshold,
            "max_results": max_results
        }

    def render_semantic_search_section(self) -> Dict[str, Any]:
        """Render semantic search section for existing use cases"""
        st.sidebar.subheader("🔍 Search Existing Use Cases")
        
        search_query = st.sidebar.text_area(
            "Search Query",
            placeholder="Search through existing use case documentation...",
            help="Use natural language to search through stored use cases",
            height=80
        )
        
        # Search filters
        with st.sidebar.expander("🔧 Search Filters"):
            filter_usecase = st.selectbox(
                "Filter by Use Case Type",
                ["All"] + self._get_available_usecases(),
                help="Filter results by use case type"
            )
            
            filter_services = st.multiselect(
                "Filter by AWS Services",
                self._get_available_services(),
                help="Filter results by AWS services mentioned"
            )
            
            top_k = st.slider(
                "Number of Results",
                min_value=1,
                max_value=20,
                value=5,
                help="Maximum number of results to return"
            )
            
            min_similarity = st.slider(
                "Minimum Similarity",
                min_value=0.1,
                max_value=1.0,
                value=0.2,
                step=0.1,
                help="Minimum similarity score to include in results"
            )
        
        search_clicked = st.sidebar.button("🔍 Search Use Cases", type="secondary")
        
        return {
            "query": search_query,
            "usecase_filter": filter_usecase if filter_usecase != "All" else None,
            "services_filter": filter_services if filter_services else None,
            "top_k": top_k,
            "min_similarity": min_similarity,
            "search_clicked": search_clicked
        }

    def _get_available_usecases(self) -> list:
        """Get list of available use case types from stored data"""
        try:
            vector_stats = self.redis_service.get_usecase_statistics()
            usecases = list(vector_stats.get('usecase_queries_distribution', {}).keys())
            return [u for u in usecases if u != 'Unknown'][:10]  # Limit to 10 most common
        except:
            return []

    def _get_available_services(self) -> list:
        """Get list of available AWS services from stored data"""
        try:
            vector_stats = self.redis_service.get_usecase_statistics()
            services = list(vector_stats.get('key_services_distribution', {}).keys())
            return [s for s in services if s != 'Unknown']
        except:
            return ['EC2', 'S3', 'RDS', 'Lambda', 'CloudFront', 'ELB', 'VPC', 'IAM', 'CloudWatch', 'Auto Scaling']

    def render_action_buttons(self, usecase_config: Dict[str, Any], ai_config: Dict[str, Any], vector_config: Dict[str, Any]) -> Tuple[bool, bool, bool]:
        """Render action buttons and return their states"""
        st.sidebar.markdown("---")
        st.sidebar.subheader("🚀 Actions")
        
        # Main action button
        generate_clicked = st.sidebar.button(
            "🎯 Generate Use Case Documentation", 
            type="primary",
            help="Generate comprehensive documentation for your use case"
        )
        
        # Secondary actions
        col1, col2 = st.sidebar.columns(2)
        with col1:
            clear_clicked = st.sidebar.button(
                "🗑️ Clear Data",
                help="Clear all stored use case data"
            )
        
        with col2:
            dedupe_clicked = st.sidebar.button(
                "🔄 Remove Duplicates",
                help="Remove duplicate documents from storage"
            )

        if generate_clicked:
            self._handle_generate_usecase_documentation(usecase_config, ai_config, vector_config)

        if clear_clicked:
            self._handle_clear_data()
            
        if dedupe_clicked:
            self._handle_remove_duplicates()

        return generate_clicked, clear_clicked, dedupe_clicked

    def _handle_generate_usecase_documentation(self, usecase_config: Dict[str, Any], ai_config: Dict[str, Any], vector_config: Dict[str, Any]):
        """Handle use case documentation generation with vector support"""
        user_query = usecase_config.get("user_query", "").strip()
        
        if not user_query:
            st.sidebar.error("❌ Please enter a use case query first!")
            return
        
        with st.spinner("Generating use case documentation..."):
            try:
                # Show different messages based on enhancements
                if ai_config.get("use_bedrock", False):
                    st.sidebar.info("🤖 Using Bedrock to enhance and analyze your use case...")
                
                if vector_config.get("enable_vectors", False):
                    st.sidebar.info("🧠 Creating vector embeddings for semantic search...")

                # Prepare the full configuration
                full_config = {
                    **usecase_config,
                    **ai_config,
                    **vector_config
                }

                mcp_service = MCPService(
                    mcp_url=usecase_config["mcp_url"],
                    use_bedrock=ai_config.get("use_bedrock", False)
                )
                
                # Generate use case documentation
                usecase_data = mcp_service.generate_usecase_documentation_sync(full_config)

                if "error" not in usecase_data:
                    # Store in Redis with vectors if enabled
                    data_key = self.redis_service.store_usecase_data(usecase_data)
                    st.sidebar.success("✅ Use case documentation generated and stored!")

                    # Show additional info about enhancements
                    metadata = usecase_data.get('metadata', {})
                    if metadata.get('enhanced_by_bedrock'):
                        st.sidebar.info("🤖 Enhanced with Bedrock AI analysis")
                    
                    if metadata.get('query_refined'):
                        st.sidebar.info("✨ Query was automatically refined")

                    # Show statistics
                    raw_docs = len(usecase_data.get('raw_documentation', []))
                    if raw_docs > 0:
                        st.sidebar.info(f"📚 Found {raw_docs} supporting documents")

                    # Store in session state
                    st.session_state['current_usecase_data'] = usecase_data
                else:
                    st.sidebar.error(f"❌ Error: {usecase_data['error']}")

            except Exception as e:
                st.sidebar.error(f"❌ Error generating documentation: {str(e)}")

    def _handle_clear_data(self):
        """Handle data clearing including vectors"""
        cleared_count = self.redis_service.clear_all_usecase_data()
        if cleared_count > 0:
            st.sidebar.success(f"✅ Cleared {cleared_count} data keys!")
            # Clear session state
            if 'current_usecase_data' in st.session_state:
                del st.session_state['current_usecase_data']
        else:
            st.sidebar.info("No data to clear")

    def _handle_remove_duplicates(self):
        """Handle duplicate removal"""
        with st.spinner("Removing duplicate documents..."):
            try:
                result = self.redis_service.remove_duplicates()
                duplicates_removed = result.get('duplicates_removed', 0)
                unique_docs = result.get('unique_documents', 0)
                
                if duplicates_removed > 0:
                    st.sidebar.success(f"✅ Removed {duplicates_removed} duplicates!")
                    st.sidebar.info(f"📊 {unique_docs} unique documents remain")
                else:
                    st.sidebar.info("No duplicates found")
            except Exception as e:
                st.sidebar.error(f"❌ Error removing duplicates: {str(e)}")

    def render_connection_status(self, usecase_config: Dict[str, Any], ai_config: Dict[str, Any]):
        """Render connection status section"""
        st.sidebar.subheader("🔌 Connection Status")

        # Redis status
        redis_connected, redis_message = self.redis_service.test_connection()
        if redis_connected:
            st.sidebar.success(f"✅ Redis: {redis_message}")
        else:
            st.sidebar.error(f"❌ Redis: {redis_message}")

        # Vector model status
        if hasattr(self.redis_service, 'embedding_model') and self.redis_service.embedding_model:
            st.sidebar.success("✅ Vector embeddings: Ready")
        else:
            st.sidebar.warning("⚠️ Vector embeddings: Not available")

        # MCP status (optional test)
        if st.sidebar.button("🧪 Test MCP Connection"):
            try:
                mcp_service = MCPService(
                    mcp_url=usecase_config["mcp_url"],
                    use_bedrock=ai_config.get("use_bedrock", False)
                )
                mcp_status = mcp_service.test_connection_sync()

                if mcp_status["status"] == "success":
                    st.sidebar.success("✅ MCP server is healthy")
                    if mcp_status.get("bedrock_enabled"):
                        st.sidebar.success("✅ Bedrock enhancement enabled")
                    else:
                        st.sidebar.info("ℹ️ Bedrock enhancement disabled")
                else:
                    st.sidebar.error(f"❌ MCP error: {mcp_status.get('error', 'Unknown')}")
            except Exception as e:
                st.sidebar.error(f"❌ MCP connection error: {str(e)}")

    def render_statistics_section(self):
        """Render statistics section"""
        st.sidebar.subheader("📊 Statistics")
        
        try:
            stats = self.redis_service.get_usecase_statistics()
            
            # Basic stats
            col1, col2 = st.sidebar.columns(2)
            with col1:
                st.metric("📄 Total Docs", stats.get('total_vectors', 0))
            with col2:
                st.metric("🔄 Unique", stats.get('unique_documents', 0))
            
            # Enhanced stats
            bedrock_count = stats.get('bedrock_enhanced_count', 0)
            refined_count = stats.get('query_refined_count', 0)
            
            if bedrock_count > 0:
                st.sidebar.info(f"🤖 {bedrock_count} Bedrock-enhanced")
            if refined_count > 0:
                st.sidebar.info(f"✨ {refined_count} queries refined")
            
            # Show top services if available
            services_dist = stats.get('key_services_distribution', {})
            if services_dist:
                top_service = max(services_dist.items(), key=lambda x: x[1])
                st.sidebar.info(f"🔧 Top service: {top_service[0]}")
                
        except Exception as e:
            st.sidebar.error(f"Error loading stats: {str(e)}")

    def render_recent_queries_section(self):
        """Render recent queries section"""
        st.sidebar.subheader("📝 Recent Queries")
        
        try:
            recent_queries = self.redis_service.get_recent_usecase_queries()
            
            if recent_queries:
                # Show last 3 queries
                for i, query in enumerate(recent_queries[:3]):
                    with st.sidebar.expander(f"Query {i+1}", expanded=False):
                        original_query = query.get('original_query', 'N/A')
                        if len(original_query) > 50:
                            original_query = original_query[:50] + "..."
                        
                        st.write(f"**Query:** {original_query}")
                        
                        services = query.get('key_services', [])
                        if services:
                            st.write(f"**Services:** {', '.join(services[:2])}")
                        
                        if query.get('enhanced_by_bedrock'):
                            st.write("🤖 Bedrock Enhanced")
                        
                        if query.get('query_refined'):
                            st.write("✨ Query Refined")
            else:
                st.sidebar.info("No recent queries")
                
        except Exception as e:
            st.sidebar.error(f"Error loading recent queries: {str(e)}")


# Backward compatibility - alias for the old class name
SidebarControls = UsecaseSidebarControls