#!/usr/bin/env python3
"""
Main Streamlit application for AWS Use Case Documentation Dashboard with Vector Search
"""

import streamlit as st
import sys
import os

# Add the app directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.redis_service import RedisVectorService  # Import from redis_service.py
from components.sidebar import UsecaseSidebarControls
from components.tabs import UsecaseTabManager
from components.display import UsecaseDocumentDisplay
from utils.helpers import SessionManager, UIHelpers


def main():
    """Main application function"""
    try:
        # Page configuration
        st.set_page_config(
            page_title="AWS Use Case Documentation Dashboard with AI",
            page_icon="🎯",
            layout="wide",
            initial_sidebar_state="expanded"
        )
        
        # Initialize session
        SessionManager.initialize_session()
        
        # App header with enhanced branding
        st.title("🎯 AWS Use Case Documentation & AI Assistant")
        st.markdown("""
        **Intelligent AWS Use Case Analysis** - Describe your AWS use case and get comprehensive documentation 
        with architecture recommendations, best practices, and cost considerations powered by AI and vector search.
        """)
        
        # Initialize vector-enhanced Redis service
        try:
            redis_service = RedisVectorService()
            redis_connected, redis_message = redis_service.test_connection()
            
            if redis_connected:
                UIHelpers.show_success_message(f"✅ Connected to Redis: {redis_message}")
                
                # Check vector capabilities
                if hasattr(redis_service, 'embedding_model') and redis_service.embedding_model:
                    UIHelpers.show_success_message("🧠 Vector embeddings ready for semantic search")
                else:
                    st.warning("⚠️ Vector embeddings not available - semantic search will be limited")
                    
            else:
                UIHelpers.show_error_message(f"❌ Redis connection failed: {redis_message}")
                st.info("💡 Please check your Redis configuration and try again.")
                return
                
        except Exception as e:
            UIHelpers.show_error_message(f"Failed to initialize Redis vector service: {str(e)}")
            st.info("💡 Make sure Redis is running and the vector service dependencies are installed.")
            
            # Show the specific error for debugging
            with st.expander("🐛 Error Details"):
                st.code(f"Error: {str(e)}\nType: {type(e).__name__}")
            return
        
        # Initialize components
        try:
            sidebar = UsecaseSidebarControls(redis_service)
            tab_manager = UsecaseTabManager(redis_service)
            display = UsecaseDocumentDisplay()
        except Exception as e:
            UIHelpers.show_error_message(f"Failed to initialize components: {str(e)}")
            
            # Show component initialization errors
            with st.expander("🐛 Component Error Details"):
                st.code(f"Error: {str(e)}\nType: {type(e).__name__}")
            return
        
        # Sidebar controls
        st.sidebar.header("🎯 Use Case Assistant")
        
        # Configuration sections
        try:
            # Use case input section
            usecase_config = sidebar.render_usecase_input_section()
            
            # AI enhancement configuration
            ai_config = sidebar.render_ai_enhancement_section()
            
            # Vector search configuration
            vector_config = sidebar.render_vector_search_section()
            
            # Semantic search section for existing use cases
            search_config = {}
            if hasattr(sidebar, 'render_semantic_search_section'):
                try:
                    search_config = sidebar.render_semantic_search_section()
                except Exception as e:
                    st.sidebar.error(f"Error in semantic search section: {str(e)}")
            
            # Action buttons
            generate_clicked, clear_clicked, dedupe_clicked = sidebar.render_action_buttons(
                usecase_config, ai_config, vector_config
            )
            
            # Connection status
            sidebar.render_connection_status(usecase_config, ai_config)
            
            # Statistics section
            try:
                sidebar.render_statistics_section()
            except Exception as e:
                st.sidebar.error(f"Error loading statistics: {str(e)}")
            
            # Recent queries section
            try:
                sidebar.render_recent_queries_section()
            except Exception as e:
                st.sidebar.error(f"Error loading recent queries: {str(e)}")
                
        except Exception as e:
            st.sidebar.error(f"Error in sidebar: {str(e)}")
        
        # Handle semantic search from sidebar
        if search_config.get('search_clicked') and search_config.get('query'):
            st.session_state['perform_search'] = search_config
            st.session_state['active_tab'] = 'semantic_search'
        
        # Main content tabs with enhanced functionality
        try:
            # Dynamic tab selection based on user action
            default_tab = 0
            if st.session_state.get('active_tab') == 'semantic_search':
                default_tab = 1
            
            tab1, tab2, tab3, tab4, tab5 = st.tabs([
                "🎯 Current Use Case", 
                "🔍 Search Use Cases",
                "📊 Analytics", 
                "📚 Stored Use Cases", 
                "⚙️ System Status"
            ])
            
            with tab1:
                try:
                    tab_manager.render_current_usecase_tab()
                except Exception as e:
                    st.error(f"Error in Current Use Case tab: {str(e)}")
            
            with tab2:
                try:
                    # Check if the tab manager has the semantic search method
                    if hasattr(tab_manager, 'render_semantic_search_tab'):
                        tab_manager.render_semantic_search_tab()
                    else:
                        # Fallback semantic search interface for use cases
                        st.header("🔍 Search Use Case Documentation")
                        
                        search_query = st.text_input(
                            "Search Query",
                            placeholder="Search through existing use case documentation...",
                            help="Use natural language to find relevant use cases and documentation"
                        )
                        
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            top_k = st.slider("Max Results", 1, 20, 10)
                        with col2:
                            usecase_filter = st.selectbox("Use Case Filter", ["All", "Web Application", "Data Analytics", "Serverless", "Security"])
                        with col3:
                            min_similarity = st.slider("Min Similarity", 0.1, 1.0, 0.2, 0.1)
                        
                        if st.button("🔍 Search", type="primary") and search_query:
                            with st.spinner("Searching use case documentation..."):
                                try:
                                    results = redis_service.semantic_search_usecases(
                                        query=search_query,
                                        top_k=top_k,
                                        usecase_filter=usecase_filter if usecase_filter != "All" else None,
                                        min_similarity=min_similarity
                                    )
                                    
                                    if results:
                                        st.success(f"Found {len(results)} relevant use cases!")
                                        
                                        for i, result in enumerate(results):
                                            similarity = result.get('similarity', 0)
                                            metadata = result.get('metadata', {})
                                            
                                            with st.expander(f"Use Case {i+1} - Similarity: {similarity:.3f}", expanded=False):
                                                col_a, col_b = st.columns([2, 1])
                                                
                                                with col_a:
                                                    if metadata.get('original_query'):
                                                        st.markdown(f"**Original Query:** {metadata['original_query']}")
                                                    if metadata.get('usecase_summary'):
                                                        summary = metadata['usecase_summary'][:150] + "..." if len(metadata['usecase_summary']) > 150 else metadata['usecase_summary']
                                                        st.markdown(f"**Summary:** {summary}")
                                                    if metadata.get('key_services'):
                                                        services = ', '.join(metadata['key_services'][:3])
                                                        st.markdown(f"**Key Services:** {services}")
                                                
                                                with col_b:
                                                    st.metric("Similarity", f"{similarity:.3f}")
                                                    if metadata.get('enhanced_by_bedrock'):
                                                        st.success("🤖 AI Enhanced")
                                                
                                                content_preview = metadata.get('content_preview', '')
                                                if content_preview:
                                                    st.markdown("**Content Preview:**")
                                                    st.markdown(content_preview)
                                    else:
                                        st.info("No results found. Try a different query or generate some use case documentation first.")
                                        
                                except Exception as e:
                                    st.error(f"Error performing search: {str(e)}")
                    
                    # Handle search from sidebar
                    if st.session_state.get('perform_search'):
                        search_data = st.session_state['perform_search']
                        
                        with st.spinner("🔍 Performing semantic search..."):
                            try:
                                results = redis_service.semantic_search_usecases(
                                    query=search_data['query'],
                                    top_k=search_data.get('top_k', 10),
                                    usecase_filter=search_data.get('usecase_filter'),
                                    min_similarity=search_data.get('min_similarity', 0.2)
                                )
                                
                                if results:
                                    st.success(f"Found {len(results)} relevant use cases!")
                                    if hasattr(display, 'display_semantic_search_results'):
                                        display.display_semantic_search_results(results, search_data['query'])
                                    else:
                                        # Fallback display
                                        for i, result in enumerate(results):
                                            st.json(result)
                                else:
                                    st.info("No results found. Try a different query or generate some use case documentation first.")
                                    
                            except Exception as e:
                                st.error(f"Error performing search: {str(e)}")
                        
                        # Clear the search request
                        if 'perform_search' in st.session_state:
                            del st.session_state['perform_search']
                        if 'active_tab' in st.session_state:
                            del st.session_state['active_tab']
                            
                except Exception as e:
                    st.error(f"Error in Semantic Search tab: {str(e)}")
            
            with tab3:
                try:
                    tab_manager.render_analytics_tab()
                except Exception as e:
                    st.error(f"Error in Analytics tab: {str(e)}")
            
            with tab4:
                try:
                    tab_manager.render_stored_usecases_tab()
                except Exception as e:
                    st.error(f"Error in Stored Use Cases tab: {str(e)}")
            
            with tab5:
                try:
                    tab_manager.render_system_status_tab()
                except Exception as e:
                    st.error(f"Error in System Status tab: {str(e)}")
                    
        except Exception as e:
            st.error(f"Error rendering tabs: {str(e)}")
        
        # Show quick start guide if no data exists
        try:
            recent_queries = redis_service.get_recent_usecase_queries()
            if not recent_queries:
                st.markdown("---")
                st.subheader("🚀 Quick Start Guide")
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.markdown("""
                    ### 1️⃣ Describe Your Use Case
                    Use the sidebar to describe what you want to build with AWS services.
                    """)
                
                with col2:
                    st.markdown("""
                    ### 2️⃣ AI Enhancement
                    Enable Bedrock AI to get comprehensive documentation with best practices.
                    """)
                
                with col3:
                    st.markdown("""
                    ### 3️⃣ Explore & Search
                    Browse generated documentation and search through existing use cases.
                    """)
                
                # Example use cases
                st.markdown("### 🌟 Example Use Cases to Try")
                examples = [
                    "Build a scalable web application with auto-scaling, load balancing, and RDS database",
                    "Create a serverless data processing pipeline with Lambda, S3, and DynamoDB",
                    "Set up a secure multi-tier application with VPC, security groups, and encryption",
                    "Design a cost-optimized architecture for a startup with monitoring and alerts",
                    "Build a real-time analytics dashboard with Kinesis, Lambda, and QuickSight"
                ]
                
                for i, example in enumerate(examples, 1):
                    st.markdown(f"**{i}.** {example}")
                    
        except Exception as e:
            st.error(f"Error showing quick start guide: {str(e)}")
        
        # Footer with system information
        try:
            st.markdown("---")
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                system_info = redis_service.get_system_info()
                if system_info and not system_info.get('error'):
                    st.caption(f"📊 Total Keys: {system_info.get('total_keys', 0)}")
            
            with col2:
                vector_stats = redis_service.get_usecase_statistics()
                if vector_stats and not vector_stats.get('error'):
                    st.caption(f"🎯 Use Cases: {vector_stats.get('total_queries', 0)}")
            
            with col3:
                if vector_stats and not vector_stats.get('error'):
                    st.caption(f"🧠 Vector Embeddings: {vector_stats.get('total_vectors', 0)}")
            
            with col4:
                if hasattr(redis_service, 'embedding_model') and redis_service.embedding_model:
                    st.caption("✅ AI Search Ready")
                else:
                    st.caption("⚠️ Limited Search Mode")
                    
        except Exception as e:
            st.caption(f"Status unavailable: {str(e)}")
            
    except Exception as e:
        st.error(f"Critical application error: {str(e)}")
        st.error("Please refresh the page or contact support.")
        
        # Debug information in expander
        with st.expander("🐛 Debug Information"):
            st.code(f"""
Error Details:
- Error: {str(e)}
- Type: {type(e).__name__}
- Python Path: {sys.path}
- Working Directory: {os.getcwd()}
            """)


if __name__ == "__main__":
    main()