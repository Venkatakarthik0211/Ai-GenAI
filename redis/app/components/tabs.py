"""
Tab components for the main dashboard with AWS Titan vector capabilities for use cases
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
from typing import Dict, Any, Optional, List

from services.redis_service import RedisVectorService
from components.display import UsecaseDocumentDisplay


class UsecaseTabManager:
    """Manage different tabs in the dashboard with AWS Titan vector features for use cases"""

    def __init__(self, redis_service: RedisVectorService):
        self.redis_service = redis_service
        self.display = UsecaseDocumentDisplay()

    def render_current_usecase_tab(self):
        """Render current use case documentation tab"""
        st.header("🎯 Current Use Case Documentation")

        # Show embedding service status
        self._show_embedding_status()

        # Check if current data exists in session state
        current_data = st.session_state.get('current_usecase_data')

        if current_data is not None:
            self.display.display_usecase_documentation_data(current_data)
        else:
            # Try to get the most recent data from Redis
            try:
                latest_data = self.redis_service.get_latest_usecase_data()
                if latest_data:
                    st.info("📋 Displaying most recent use case from Redis")
                    self.display.display_usecase_documentation_data(latest_data)
                else:
                    st.info("💡 No use case documentation available. Use the sidebar to generate documentation for your AWS use case.")
                    
                    # Show some example use cases
                    st.markdown("### 🌟 Example Use Cases")
                    examples = [
                        "🌐 Build a scalable web application with auto-scaling, load balancing, and database",
                        "📊 Create a data analytics pipeline with real-time processing and visualization",
                        "🔒 Set up a secure multi-tier application with proper access controls",
                        "💰 Design a cost-optimized architecture for a startup application",
                        "🚀 Build a serverless microservices architecture with API Gateway"
                    ]
                    
                    for example in examples:
                        st.markdown(f"• {example}")
                        
            except Exception as e:
                st.error(f"Error retrieving data from Redis: {str(e)}")

    def _show_embedding_status(self):
        """Show embedding service status"""
        embedding_info = self.redis_service.get_embedding_status()
        
        if embedding_info.get('available', False):
            method = embedding_info.get('method', 'unknown')
            if method == 'titan':
                st.success(f"🤖 AWS Titan Embeddings Active (Dimension: {embedding_info.get('embedding_dim', 'N/A')})")
            elif method == 'tfidf':
                st.warning(f"📊 TF-IDF Fallback Active (Dimension: {embedding_info.get('embedding_dim', 'N/A')})")
            else:
                st.info(f"🔧 Embedding Method: {method}")
        else:
            error = embedding_info.get('initialization_error', 'Unknown error')
            st.error(f"❌ Embedding Service Unavailable: {error}")
            
            # Show troubleshooting tips
            with st.expander("🔧 Troubleshooting Tips"):
                st.markdown("""
                **For AWS Titan Embeddings:**
                - Ensure AWS credentials are configured
                - Check AWS Bedrock access permissions
                - Verify AWS region is supported for Bedrock
                - Enable Bedrock access in your AWS account
                
                **For TF-IDF Fallback:**
                - Install scikit-learn: `pip install scikit-learn`
                """)

    def render_semantic_search_tab(self):
        """Render semantic search tab for use cases with AWS Titan support"""
        st.header("🔍 Search Use Case Documentation")
        
        # Show embedding service info
        embedding_info = self.redis_service.get_embedding_status()
        
        col1, col2 = st.columns([3, 1])
        with col1:
            if embedding_info.get('method') == 'titan':
                st.success("🤖 AWS Titan Semantic Search Active")
            elif embedding_info.get('method') == 'tfidf':
                st.warning("📊 TF-IDF Text Search Active")
            else:
                st.error("❌ Enhanced Text Search Only")
        
        with col2:
            if st.button("🔄 Refresh Status"):
                st.rerun()
        
        # Handle example query from session state
        example_query = st.session_state.get('example_query', '')
        if example_query:
            del st.session_state['example_query']
        
        # Search interface
        col1, col2 = st.columns([3, 1])
        
        with col1:
            search_query = st.text_input(
                "Search Query",
                value=example_query,
                placeholder="Search through existing use case documentation...",
                help="Use natural language to find relevant use cases and documentation"
            )
        
        with col2:
            st.write("")  # Spacing
            st.write("")  # Spacing
            search_button = st.button("🔍 Search", type="primary")
        
        # Advanced filters
        with st.expander("🔧 Advanced Filters"):
            col1, col2, col3 = st.columns(3)
            
            with col1:
                usecase_filter = st.selectbox(
                    "Use Case Filter",
                    ["All"] + self._get_available_usecases()
                )
            
            with col2:
                service_filter = st.multiselect(
                    "AWS Services",
                    self._get_available_services(),
                    help="Filter by AWS services mentioned in use cases"
                )
            
            with col3:
                col3a, col3b = st.columns(2)
                with col3a:
                    top_k = st.slider("Max Results", 1, 20, 10)
                with col3b:
                    min_similarity = st.slider("Min Similarity", 0.1, 1.0, 0.2, 0.1)
        
        # Handle search
        if search_button and search_query:
            with st.spinner("🔍 Searching use case documentation..."):
                try:
                    results = self.redis_service.semantic_search_usecases(
                        query=search_query,
                        top_k=top_k,
                        usecase_filter=usecase_filter if usecase_filter != "All" else None,
                        min_similarity=min_similarity
                    )
                    
                    if results:
                        # Show search method used
                        if results and 'match_type' in results[0]:
                            match_type = results[0]['match_type']
                            if 'semantic_titan' in match_type:
                                st.success("🤖 Results from AWS Titan semantic search")
                            elif 'semantic_tfidf' in match_type:
                                st.info("📊 Results from TF-IDF semantic search")
                            elif 'text_fallback' in match_type:
                                st.warning("📝 Results from enhanced text search")
                        
                        self.display.display_semantic_search_results(results, search_query)
                        
                        # Handle similar document requests
                        if st.session_state.get('find_similar_to'):
                            doc_id = st.session_state['find_similar_to']
                            st.markdown("---")
                            with st.spinner("Finding similar documents..."):
                                similar_docs = self.redis_service.get_similar_usecase_documents(doc_id, 5)
                                self.display.display_similar_documents(similar_docs, doc_id)
                            # Clear the session state
                            del st.session_state['find_similar_to']
                    else:
                        st.info("🔍 No results found. Try a different query or check if use case documentation is available.")
                        
                        # Suggest alternatives
                        st.markdown("### 💡 Suggestions:")
                        st.markdown("- Try broader search terms")
                        st.markdown("- Check spelling and try synonyms")
                        st.markdown("- Generate more use case documentation first")
                        
                except Exception as e:
                    st.error(f"Error performing search: {str(e)}")
                    st.exception(e)  # Show full traceback in development
        
        elif search_button and not search_query:
            st.warning("Please enter a search query.")
        
        # Show some example queries
        if not search_query:
            st.markdown("### 💡 Example Search Queries")
            examples = [
                "How to build a scalable web application?",
                "Serverless architecture best practices",
                "Cost optimization for startups",
                "Data analytics pipeline setup",
                "Multi-tier security implementation",
                "Auto-scaling configuration",
                "Database backup and recovery",
                "Content delivery network setup"
            ]
            
            cols = st.columns(2)
            for i, example in enumerate(examples):
                with cols[i % 2]:
                    if st.button(f"🔍 {example}", key=f"example_{i}", use_container_width=True):
                        st.session_state['example_query'] = example
                        st.rerun()

    def _get_available_usecases(self) -> List[str]:
        """Get list of available use case types from stored data"""
        try:
            vector_stats = self.redis_service.get_usecase_statistics()
            usecases = list(vector_stats.get('usecase_queries_distribution', {}).keys())
            return [u for u in usecases if u != 'Unknown'][:10]  # Limit to 10 most common
        except Exception as e:
            st.error(f"Error getting use cases: {e}")
            return []

    def _get_available_services(self) -> List[str]:
        """Get list of available AWS services from stored data"""
        try:
            vector_stats = self.redis_service.get_usecase_statistics()
            services = list(vector_stats.get('key_services_distribution', {}).keys())
            return [s for s in services if s != 'Unknown']
        except Exception as e:
            # Return common AWS services as fallback
            return ['EC2', 'S3', 'RDS', 'Lambda', 'CloudFront', 'ELB', 'VPC', 'IAM', 'CloudWatch', 'Auto Scaling']

    def render_analytics_tab(self):
        """Render analytics tab with AWS Titan vector analytics"""
        st.header("📊 Use Case Analytics Dashboard")

        try:
            analytics_data = self.redis_service.get_usecase_analytics_data()
            vector_stats = analytics_data.get('vector_stats', {})

            if not analytics_data or analytics_data.get('total_queries', 0) == 0:
                st.info("📋 No use case queries found. Generate some use case documentation to see analytics.")
                return

            # Embedding service status
            embedding_info = vector_stats.get('embedding_service', {})
            if embedding_info:
                col1, col2, col3 = st.columns(3)
                with col1:
                    method = embedding_info.get('method', 'unknown')
                    if method == 'titan':
                        st.success(f"🤖 AWS Titan Active")
                    elif method == 'tfidf':
                        st.warning(f"📊 TF-IDF Active")
                    else:
                        st.error(f"❌ No Embeddings")
                
                with col2:
                    if embedding_info.get('available', False):
                        st.success("✅ Service Available")
                    else:
                        st.error("❌ Service Unavailable")
                
                with col3:
                    dim = embedding_info.get('embedding_dim', 'N/A')
                    st.info(f"📐 Dimension: {dim}")

            # Main metrics
            st.subheader("📈 Key Metrics")
            col1, col2, col3, col4 = st.columns(4)

            with col1:
                st.metric("🎯 Total Use Cases", analytics_data.get('total_queries', 0))
            with col2:
                st.metric("📚 Total Documents", analytics_data.get('total_docs', 0))
            with col3:
                st.metric("🧠 Vector Embeddings", vector_stats.get('total_vectors', 0))
            with col4:
                st.metric("🤖 Bedrock Enhanced", analytics_data.get('bedrock_enhanced', 0))

            # Enhancement statistics
            col5, col6, col7, col8 = st.columns(4)
            
            with col5:
                st.metric("✨ Query Refined", analytics_data.get('query_refined', 0))
            with col6:
                st.metric("📄 New Documents", analytics_data.get('total_new_docs', 0))
            with col7:
                st.metric("🔄 Duplicates Skipped", analytics_data.get('total_duplicates', 0))
            with col8:
                unique_docs = vector_stats.get('unique_documents', 0)
                st.metric("🎯 Unique Documents", unique_docs)

            # Vector statistics
            if vector_stats and vector_stats.get('total_vectors', 0) > 0:
                st.subheader("🧠 Vector Analytics")
                
                # Embedding methods distribution
                embedding_methods = vector_stats.get('embedding_methods_used', {})
                if embedding_methods:
                    st.markdown("#### 🔧 Embedding Methods Used")
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        fig_methods = px.pie(
                            values=list(embedding_methods.values()),
                            names=list(embedding_methods.keys()),
                            title="Embedding Methods Distribution"
                        )
                        st.plotly_chart(fig_methods, use_container_width=True)
                    
                    with col2:
                        # Embedding dimensions used
                        embedding_dims = vector_stats.get('embedding_dimensions_used', {})
                        if embedding_dims:
                            fig_dims = px.bar(
                                x=list(embedding_dims.keys()),
                                y=list(embedding_dims.values()),
                                title="Embedding Dimensions Used",
                                labels={'x': 'Dimensions', 'y': 'Count'}
                            )
                            st.plotly_chart(fig_dims, use_container_width=True)
                
                col1, col2 = st.columns(2)
                
                with col1:
                    # Use case queries distribution
                    usecase_data = analytics_data.get('usecase_queries', {})
                    if usecase_data:
                        # Limit to top 10 for better visualization
                        top_usecases = dict(sorted(usecase_data.items(), key=lambda x: x[1], reverse=True)[:10])
                        fig_usecases = px.pie(
                            values=list(top_usecases.values()),
                            names=[name[:30] + "..." if len(name) > 30 else name for name in top_usecases.keys()],
                            title="Top Use Case Queries"
                        )
                        fig_usecases.update_traces(textposition='inside', textinfo='percent+label')
                        st.plotly_chart(fig_usecases, use_container_width=True)
                
                with col2:
                    # Key services distribution
                    services_data = analytics_data.get('key_services', {})
                    if services_data:
                        # Limit to top 10 services
                        top_services = dict(sorted(services_data.items(), key=lambda x: x[1], reverse=True)[:10])
                        fig_services = px.bar(
                            x=list(top_services.values()),
                            y=list(top_services.keys()),
                            orientation='h',
                            title="Most Referenced AWS Services",
                            labels={'x': 'References', 'y': 'AWS Service'}
                        )
                        fig_services.update_layout(height=400)
                        st.plotly_chart(fig_services, use_container_width=True)

                # Document types distribution
                col3, col4 = st.columns(2)
                
                with col3:
                    types_data = vector_stats.get('types_distribution', {})
                    if types_data:
                        fig_types = px.bar(
                            x=list(types_data.keys()),
                            y=list(types_data.values()),
                            title="Document Types Distribution",
                            labels={'x': 'Document Type', 'y': 'Count'}
                        )
                        st.plotly_chart(fig_types, use_container_width=True)
                
                with col4:
                    # Enhancement status pie chart
                    enhancement_data = {
                        'Bedrock Enhanced': analytics_data.get('bedrock_enhanced', 0),
                        'Query Refined': analytics_data.get('query_refined', 0),
                        'Standard': analytics_data.get('total_queries', 0) - analytics_data.get('bedrock_enhanced', 0)
                    }
                    enhancement_data = {k: v for k, v in enhancement_data.items() if v > 0}
                    
                    if enhancement_data:
                        fig_enhancement = px.pie(
                            values=list(enhancement_data.values()),
                            names=list(enhancement_data.keys()),
                            title="AI Enhancement Status"
                        )
                        st.plotly_chart(fig_enhancement, use_container_width=True)

            # Recent use cases timeline
            st.subheader("🕒 Recent Use Case Queries")
            recent_queries = analytics_data.get('recent_queries', [])
            if recent_queries:
                # Create a more detailed dataframe
                queries_data = []
                for query in recent_queries[:10]:  # Show last 10
                    queries_data.append({
                        'Timestamp': query.get('timestamp', 'N/A'),
                        'Original Query': query.get('original_query', 'N/A')[:50] + '...' if len(query.get('original_query', '')) > 50 else query.get('original_query', 'N/A'),
                        'Key Services': ', '.join(query.get('key_services', [])[:3]),
                        'Total Docs': query.get('total_docs', 0),
                        'New Docs': query.get('new_documents', 0),
                        'Duplicates': query.get('duplicate_documents', 0),
                        'Bedrock Enhanced': '✅' if query.get('enhanced_by_bedrock', False) else '❌',
                        'Query Refined': '✅' if query.get('query_refined', False) else '❌',
                        'Embedding Method': query.get('embedding_method', 'unknown')
                    })
                
                queries_df = pd.DataFrame(queries_data)
                st.dataframe(queries_df, use_container_width=True)

        except Exception as e:
            st.error(f"Error loading analytics data: {str(e)}")
            st.exception(e)

    def render_stored_usecases_tab(self):
        """Render stored use cases tab"""
        st.header("📚 Stored Use Case Documentation")

        try:
            recent_queries = self.redis_service.get_recent_usecase_queries()

            if recent_queries:
                st.subheader("📋 Available Use Case Documentation")

                for i, query in enumerate(recent_queries):
                    if not isinstance(query, dict):
                        continue

                    timestamp = query.get('timestamp', '')
                    if not timestamp:
                        continue

                    try:
                        formatted_time = datetime.fromisoformat(timestamp).strftime("%Y-%m-%d %H:%M:%S")
                    except ValueError:
                        formatted_time = timestamp

                    # Create an expandable card for each use case
                    with st.expander(f"🎯 Use Case {i+1}: {formatted_time}", expanded=False):
                        col1, col2 = st.columns([2, 1])
                        
                        with col1:
                            original_query = query.get('original_query', 'N/A')
                            st.markdown(f"**Original Query:** {original_query}")
                            
                            refined_query = query.get('refined_query', 'N/A')
                            if refined_query != original_query:
                                st.markdown(f"**Refined Query:** {refined_query}")
                            
                            usecase_summary = query.get('usecase_summary', '')
                            if usecase_summary:
                                summary_preview = usecase_summary[:150] + "..." if len(usecase_summary) > 150 else usecase_summary
                                st.markdown(f"**Summary:** {summary_preview}")
                            
                            key_services = query.get('key_services', [])
                            if key_services:
                                st.markdown(f"**Key Services:** {', '.join(key_services[:5])}")
                            
                            # Show embedding method used
                            embedding_method = query.get('embedding_method', 'unknown')
                            if embedding_method == 'titan':
                                st.success("🤖 AWS Titan Embeddings")
                            elif embedding_method == 'tfidf':
                                st.warning("📊 TF-IDF Embeddings")
                            else:
                                st.info(f"🔧 Method: {embedding_method}")
                        
                        with col2:
                            # Metrics
                            total_docs = query.get('total_docs', 0)
                            new_docs = query.get('new_documents', 0)
                            duplicates = query.get('duplicate_documents', 0)
                            
                            st.metric("📄 Total Docs", total_docs)
                            st.metric("📄 New Docs", new_docs)
                            st.metric("🔄 Duplicates", duplicates)
                            
                            # Enhancement status
                            if query.get('enhanced_by_bedrock', False):
                                st.success("🤖 Bedrock Enhanced")
                            if query.get('query_refined', False):
                                st.success("✨ Query Refined")
                            
                            # Embedding dimensions
                            embedding_dims = query.get('embedding_dimensions', 1024)
                            st.info(f"📐 Dims: {embedding_dims}")
                        
                        # Action button
                        if st.button("📖 View Full Documentation", key=f"view_{i}"):
                            data_key = f"aws_usecase_docs:data:{timestamp}"
                            data = self.redis_service.get_usecase_data(data_key)
                            if data:
                                st.session_state['current_usecase_data'] = data
                                st.success("✅ Use case loaded! Check the 'Current Use Case' tab.")
                                st.rerun()
                            else:
                                st.error("❌ Failed to load use case data from Redis.")
            else:
                st.info("📋 No stored use case documentation found.")
                st.markdown("### 💡 Get Started")
                st.markdown("Use the sidebar to generate documentation for your AWS use cases!")

        except Exception as e:
            st.error(f"Error loading stored use cases: {str(e)}")

    def render_system_status_tab(self):
        """Render system status tab with AWS Titan vector information"""
        st.header("⚙️ System Status")

        try:
            # Test connection first
            connection_status, connection_msg = self.redis_service.test_connection()
            
            if connection_status:
                st.success(f"✅ {connection_msg}")
            else:
                st.error(f"❌ {connection_msg}")
                return

            system_info = self.redis_service.get_system_info()
            vector_stats = self.redis_service.get_usecase_statistics()
            embedding_info = self.redis_service.get_embedding_status()

            if not system_info or system_info.get('error'):
                error_msg = system_info.get('error', 'Unknown error') if system_info else 'Failed to get system info'
                st.error(f"Error getting system info: {error_msg}")
                return

            # Embedding Service Status
            st.subheader("🤖 AWS Titan Embedding Service Status")
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                method = embedding_info.get('method', 'none')
                if method == 'titan':
                    st.success("🤖 AWS Titan")
                elif method == 'tfidf':
                    st.warning("📊 TF-IDF")
                else:
                    st.error("❌ None")
            
            with col2:
                if embedding_info.get('available', False):
                    st.success("✅ Available")
                else:
                    st.error("❌ Unavailable")
            
            with col3:
                dim = embedding_info.get('embedding_dim', 'N/A')
                st.metric("📐 Dimensions", dim)
            
            with col4:
                if embedding_info.get('initialized', False):
                    st.success("✅ Initialized")
                else:
                    st.error("❌ Not Initialized")

            # Show detailed embedding info
            if embedding_info.get('model_info'):
                model_info = embedding_info['model_info']
                
                with st.expander("🔧 Embedding Service Details"):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.markdown("**AWS Titan Status:**")
                        st.write(f"• Titan Available: {'✅' if model_info.get('titan_available') else '❌'}")
                        st.write(f"• Bedrock Client: {'✅' if model_info.get('bedrock_client_loaded') else '❌'}")
                        st.write(f"• AWS Region: {model_info.get('aws_region', 'N/A')}")
                        st.write(f"• Model ID: {model_info.get('model_id', 'N/A')}")
                    
                    with col2:
                        st.markdown("**Fallback Options:**")
                        st.write(f"• TF-IDF Available: {'✅' if model_info.get('tfidf_available') else '❌'}")
                        st.write(f"• TF-IDF Loaded: {'✅' if model_info.get('tfidf_loaded') else '❌'}")
                        st.write(f"• Current Method: {model_info.get('current_method', 'N/A')}")

            # Show initialization error if any
            if embedding_info.get('initialization_error'):
                st.error(f"🚨 Initialization Error: {embedding_info['initialization_error']}")

            # System metrics
            st.subheader("📊 Redis System Metrics")
            col1, col2, col3, col4 = st.columns(4)

            with col1:
                st.metric("Total Keys", system_info.get('total_keys', 0))
            with col2:
                st.metric("Use Case Keys", system_info.get('usecase_keys', 0))
            with col3:
                st.metric("Vector Keys", system_info.get('vector_keys', 0))
            with col4:
                st.metric("Used Memory", system_info.get('used_memory', 'N/A'))

            # Vector system info
            if vector_stats and not vector_stats.get('error'):
                st.subheader("🧠 Vector System Status")
                
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric("Total Vectors", vector_stats.get('total_vectors', 0))
                with col2:
                    st.metric("Unique Documents", vector_stats.get('unique_documents', 0))
                with col3:
                    duplicates = vector_stats.get('potential_duplicates', 0)
                    st.metric("Potential Duplicates", duplicates)
                with col4:
                    st.metric("Vector Dimension", vector_stats.get('vector_dimension', 0))

                # Enhancement statistics
                col5, col6, col7, col8 = st.columns(4)
                
                with col5:
                    st.metric("🤖 Bedrock Enhanced", vector_stats.get('bedrock_enhanced_count', 0))
                with col6:
                    st.metric("✨ Query Refined", vector_stats.get('query_refined_count', 0))
                with col7:
                    embedding_methods = vector_stats.get('embedding_methods_used', {})
                    titan_count = embedding_methods.get('titan', 0)
                    st.metric("🤖 Titan Vectors", titan_count)
                with col8:
                    tfidf_count = embedding_methods.get('tfidf', 0)
                    st.metric("📊 TF-IDF Vectors", tfidf_count)

            # System information table
            st.subheader("📋 Redis Server Information")
            info_data = {
                'Redis Version': system_info.get('redis_version', 'N/A'),
                'Uptime (days)': system_info.get('uptime_days', 0),
                'Total Commands': system_info.get('total_commands', 0),
                'Connected Clients': system_info.get('connected_clients', 0),
                'Keyspace Hits': system_info.get('keyspace_hits', 0),
                'Keyspace Misses': system_info.get('keyspace_misses', 0),
                'Service Type': system_info.get('service_type', 'N/A')
            }

            info_df = pd.DataFrame([info_data])
            st.dataframe(info_df, use_container_width=True)

            # Data management section
            st.subheader("🗑️ Data Management")
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                if st.button("🔄 Remove Duplicates", type="secondary"):
                    with st.spinner("Removing duplicates..."):
                        result = self.redis_service.remove_duplicates()
                        duplicates_removed = result.get('duplicates_removed', 0)
                        unique_docs = result.get('unique_documents', 0)
                        
                        if duplicates_removed > 0:
                            st.success(f"✅ Removed {duplicates_removed} duplicates!")
                            st.info(f"📊 {unique_docs} unique documents remain")
                        else:
                            st.info("No duplicates found")
            
            with col2:
                if st.button("🧠 Clear Vector Data Only", type="secondary"):
                    cleared = self.redis_service.clear_all_vectors()
                    st.success(f"✅ Cleared {cleared} vector keys")
            
            with col3:
                if st.button("🗑️ Clear All Use Case Data", type="secondary"):
                    cleared = self.redis_service.clear_all_usecase_data()
                    st.success(f"✅ Cleared {cleared} total keys")
                    # Clear session state
                    if 'current_usecase_data' in st.session_state:
                        del st.session_state['current_usecase_data']
            
            with col4:
                if st.button("🔄 Test Connection", type="secondary"):
                    status, msg = self.redis_service.test_connection()
                    if status:
                        st.success(f"✅ {msg}")
                    else:
                        st.error(f"❌ {msg}")

            # Performance tips
            st.subheader("💡 Performance Tips & Recommendations")
            
            recommendations = []
            
            if not embedding_info.get('available', False):
                recommendations.append("🚨 **Critical**: Embedding service is not available. Vector search capabilities are disabled.")
                if embedding_info.get('method') == 'none':
                    recommendations.append("🔧 **Action**: Configure AWS credentials and enable Bedrock access for optimal performance.")
            
            if embedding_info.get('method') == 'tfidf':
                recommendations.append("⚠️ **Warning**: Using TF-IDF fallback. Consider configuring AWS Titan for better semantic search.")
            
            if vector_stats.get('potential_duplicates', 0) > 0:
                recommendations.append(f"🔄 **Maintenance**: Found {vector_stats.get('potential_duplicates', 0)} potential duplicate documents. Consider running duplicate removal.")
            
            if vector_stats.get('total_vectors', 0) > 1000:
                recommendations.append("📊 **Performance**: Large number of vectors detected. Consider periodic cleanup for optimal performance.")
            
            if vector_stats.get('total_vectors', 0) == 0:
                recommendations.append("💡 **Getting Started**: No vectors found. Generate some use case documentation to enable vector search.")
            
            # Show recommendations
            for rec in recommendations:
                if "Critical" in rec or "🚨" in rec:
                    st.error(rec)
                elif "Warning" in rec or "⚠️" in rec:
                    st.warning(rec)
                else:
                    st.info(rec)
            
            if not recommendations:
                st.success("✅ System is running optimally!")

        except Exception as e:
            st.error(f"Error getting system info: {str(e)}")
            st.exception(e)


# Backward compatibility - alias for the old class name
TabManager = UsecaseTabManager