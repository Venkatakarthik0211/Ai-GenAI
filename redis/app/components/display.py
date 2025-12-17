"""
Display components for AWS documentation data with vector capabilities for use cases
"""

import streamlit as st
import json
from typing import Any, Dict, Optional, List


class UsecaseDocumentDisplay:
    """Handle display of AWS usecase documentation content with vector features"""

    @staticmethod
    def display_document_content(content: Any, title: str = "Content", similarity_score: Optional[float] = None):
        """Display document content in a nice format, prioritizing markdown rendering"""
        # Add similarity score to title if available
        title_with_score = title
        if similarity_score is not None:
            title_with_score = f"{title} (Similarity: {similarity_score:.3f})"
        
        with st.expander(f"📄 {title_with_score}", expanded=False):
            if isinstance(content, dict):
                # Check if it's a structured document with markdown content
                if 'content' in content or 'text' in content or 'markdown' in content:
                    # Extract the actual content
                    actual_content = content.get('content') or content.get('text') or content.get('markdown')
                    if isinstance(actual_content, str):
                        st.markdown(actual_content, unsafe_allow_html=False)
                    else:
                        st.json(content)
                else:
                    st.json(content)

            elif isinstance(content, list):
                for i, item in enumerate(content):
                    st.write(f"**Item {i+1}:**")
                    if isinstance(item, dict):
                        # Check if list item contains markdown content
                        if 'content' in item or 'text' in item or 'markdown' in item:
                            actual_content = item.get('content') or item.get('text') or item.get('markdown')
                            if isinstance(actual_content, str):
                                st.markdown(actual_content, unsafe_allow_html=False)
                            else:
                                st.json(item)
                        else:
                            st.json(item)
                    elif isinstance(item, str):
                        # Render string items as markdown
                        st.markdown(item, unsafe_allow_html=False)
                    else:
                        st.write(item)

                    if i < len(content) - 1:  # Don't add divider after last item
                        st.divider()

            elif isinstance(content, str):
                # First try to parse as JSON to see if it's structured data
                try:
                    parsed_content = json.loads(content)
                    # If it's a dict with content fields, extract and render as markdown
                    if isinstance(parsed_content, dict) and ('content' in parsed_content or 'text' in parsed_content or 'markdown' in parsed_content):
                        actual_content = parsed_content.get('content') or parsed_content.get('text') or parsed_content.get('markdown')
                        if isinstance(actual_content, str):
                            st.markdown(actual_content, unsafe_allow_html=False)
                        else:
                            st.json(parsed_content)
                    else:
                        st.json(parsed_content)
                except json.JSONDecodeError:
                    # It's a regular string, render as markdown
                    if len(content.strip()) > 0:
                        # For very long content, provide a scrollable container
                        if len(content) > 2000:
                            st.markdown("**Content (Scrollable):**")
                            st.markdown(
                                f"""
                                <div style="height: 400px; overflow-y: auto; border: 1px solid #ddd; padding: 10px; border-radius: 5px;">
                                {content}
                                </div>
                                """,
                                unsafe_allow_html=True
                            )
                        else:
                            st.markdown(content, unsafe_allow_html=False)
                    else:
                        st.info("Empty content")
            else:
                st.write(content)

    @staticmethod
    def display_enhanced_usecase_summary(enhanced_documentation: Dict[str, Any]):
        """Display the Bedrock-enhanced usecase summary"""
        if not enhanced_documentation:
            return
        
        st.subheader("🎯 Use Case Analysis")
        
        # Main usecase summary
        usecase_summary = enhanced_documentation.get('usecase_summary', '')
        if usecase_summary:
            st.markdown("### 📋 Summary")
            st.info(usecase_summary)
        
        # Create columns for different sections
        col1, col2 = st.columns(2)
        
        with col1:
            # Key Services
            key_services = enhanced_documentation.get('key_services', [])
            if key_services:
                st.markdown("### 🔧 Key AWS Services")
                for service in key_services:
                    st.markdown(f"• **{service}**")
            
            # Implementation Steps
            implementation_steps = enhanced_documentation.get('implementation_steps', [])
            if implementation_steps:
                st.markdown("### 📝 Implementation Steps")
                for i, step in enumerate(implementation_steps, 1):
                    st.markdown(f"{i}. {step}")
        
        with col2:
            # Best Practices
            best_practices = enhanced_documentation.get('best_practices', [])
            if best_practices:
                st.markdown("### ✅ Best Practices")
                for practice in best_practices:
                    st.markdown(f"• {practice}")
            
            # Key Recommendations
            key_recommendations = enhanced_documentation.get('key_recommendations', [])
            if key_recommendations:
                st.markdown("### 💡 Key Recommendations")
                for recommendation in key_recommendations:
                    st.markdown(f"• {recommendation}")
        
        # Additional considerations in full width
        col3, col4 = st.columns(2)
        
        with col3:
            # Cost Considerations
            cost_considerations = enhanced_documentation.get('cost_considerations', '')
            if cost_considerations and cost_considerations != "Not specified in documentation":
                st.markdown("### 💰 Cost Considerations")
                st.markdown(cost_considerations)
        
        with col4:
            # Security Considerations
            security_considerations = enhanced_documentation.get('security_considerations', '')
            if security_considerations and security_considerations != "Not specified in documentation":
                st.markdown("### 🔒 Security Considerations")
                st.markdown(security_considerations)
        
        # Related Services
        related_services = enhanced_documentation.get('related_services', [])
        if related_services:
            st.markdown("### 🔗 Related Services to Consider")
            cols = st.columns(min(len(related_services), 4))
            for i, service in enumerate(related_services):
                with cols[i % 4]:
                    st.markdown(f"• {service}")
        
        # Common Pitfalls
        common_pitfalls = enhanced_documentation.get('common_pitfalls', [])
        if common_pitfalls:
            st.markdown("### ⚠️ Common Pitfalls")
            for pitfall in common_pitfalls:
                st.warning(f"⚠️ {pitfall}")

    @staticmethod
    def display_semantic_search_results(search_results: List[Dict[str, Any]], query: str):
        """Display semantic search results with similarity scores for usecases"""
        st.subheader(f"🔍 Semantic Search Results for: '{query}'")
        
        if not search_results:
            st.info("No results found for your query.")
            return
        
        st.success(f"Found {len(search_results)} relevant documents")
        
        for i, result in enumerate(search_results):
            similarity = result.get('similarity', 0)
            metadata = result.get('metadata', {})
            vector_id = result.get('vector_id', '')
            
            # Create a nice card layout
            with st.container():
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    st.markdown(f"**Result {i+1}** - {metadata.get('type', 'Document').title()}")
                    if metadata.get('source'):
                        st.markdown(f"📄 **Source:** {metadata['source']}")
                    if metadata.get('original_query'):
                        st.markdown(f"🎯 **Original Query:** {metadata['original_query']}")
                    if metadata.get('usecase_summary'):
                        st.markdown(f"📋 **Use Case:** {metadata['usecase_summary'][:100]}...")
                    
                    # Show key services if available
                    key_services = metadata.get('key_services', [])
                    if key_services:
                        services_text = ", ".join(key_services[:3])
                        if len(key_services) > 3:
                            services_text += f" (+{len(key_services)-3} more)"
                        st.markdown(f"🔧 **Services:** {services_text}")
                
                with col2:
                    # Similarity score with color coding
                    if similarity >= 0.8:
                        st.success(f"🎯 {similarity:.3f}")
                    elif similarity >= 0.6:
                        st.warning(f"📊 {similarity:.3f}")
                    else:
                        st.info(f"📈 {similarity:.3f}")
                
                # Content preview
                content_preview = metadata.get('content_preview', '')
                if content_preview:
                    st.markdown("**Preview:**")
                    st.markdown(f"> {content_preview}...")
                
                # Action buttons
                col_a, col_b = st.columns([1, 1])
                with col_a:
                    if st.button(f"View Full Content", key=f"view_{vector_id}"):
                        # Store the document ID for detailed view
                        st.session_state[f'show_detail_{vector_id}'] = True
                
                with col_b:
                    if st.button(f"Find Similar", key=f"similar_{vector_id}"):
                        st.session_state['find_similar_to'] = vector_id
                
                # Show detailed content if requested
                if st.session_state.get(f'show_detail_{vector_id}', False):
                    try:
                        # Get full document content from metadata
                        doc_key = metadata.get('doc_key', '')
                        if doc_key:
                            st.markdown("**Full Content:**")
                            content = metadata.get('content_preview', 'Content not available')
                            st.markdown(content)
                    except Exception as e:
                        st.error(f"Error loading full content: {e}")
                
                st.divider()

    @staticmethod
    def display_similar_documents(similar_docs: List[Dict[str, Any]], source_doc_id: str):
        """Display similar usecase documents"""
        st.subheader(f"🔗 Documents Similar to {source_doc_id}")
        
        if not similar_docs:
            st.info("No similar documents found.")
            return
        
        for i, doc in enumerate(similar_docs):
            similarity = doc.get('similarity', 0)
            metadata = doc.get('metadata', {})
            
            with st.expander(f"Similar Document {i+1} (Similarity: {similarity:.3f})", expanded=False):
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    if metadata.get('source'):
                        st.markdown(f"**Source:** {metadata['source']}")
                    if metadata.get('original_query'):
                        st.markdown(f"**Original Query:** {metadata['original_query']}")
                    if metadata.get('usecase_summary'):
                        st.markdown(f"**Use Case:** {metadata['usecase_summary']}")
                    if metadata.get('type'):
                        st.markdown(f"**Type:** {metadata['type']}")
                    
                    # Show key services
                    key_services = metadata.get('key_services', [])
                    if key_services:
                        st.markdown(f"**Key Services:** {', '.join(key_services)}")
                
                with col2:
                    st.metric("Similarity", f"{similarity:.3f}")
                
                content_preview = metadata.get('content_preview', '')
                if content_preview:
                    st.markdown("**Content Preview:**")
                    st.markdown(content_preview)

    @staticmethod
    def display_usecase_metadata(data: Dict[str, Any]):
        """Display usecase query metadata with vector information"""
        if not data:
            return

        st.subheader("📋 Use Case Query Information")
        
        # Main query information
        col1, col2 = st.columns(2)
        
        with col1:
            original_query = data.get('original_query', 'N/A')
            st.markdown(f"**🎯 Original Query:** `{original_query}`")
            
            refined_query = data.get('refined_query', 'N/A')
            if refined_query != original_query:
                st.markdown(f"**🔍 Refined Query:** `{refined_query}`")
        
        with col2:
            metadata = data.get('metadata', {})
            if metadata.get('enhanced_by_bedrock'):
                st.success("🤖 **Enhanced by Bedrock AI**")
            if metadata.get('query_refined'):
                st.success("✨ **Query Refined by AI**")
        
        # Statistics
        col3, col4, col5, col6 = st.columns(4)
        
        with col3:
            total_docs = metadata.get('total_documents_found', 0)
            st.metric("📚 Total Documents", total_docs)
        
        with col4:
            raw_docs = len(data.get('raw_documentation', []))
            st.metric("📄 Raw Documents", raw_docs)
        
        with col5:
            search_results = len(data.get('search_results', []))
            st.metric("🔍 Search Results", search_results)
        
        with col6:
            processing_time = metadata.get('processing_timestamp', 'N/A')
            if processing_time != 'N/A':
                st.metric("⏱️ Processed", "✅")
            else:
                st.metric("⏱️ Processed", "❌")

    @staticmethod
    def display_search_results(search_results: Optional[Dict[str, Any]]):
        """Display search results for usecases"""
        if not search_results:
            return

        st.subheader("🔍 Search Results")

        results = search_results.get('results', [])
        if isinstance(results, list) and results:
            for i, result in enumerate(results):
                with st.expander(f"Search Result {i+1}", expanded=False):
                    if isinstance(result, dict):
                        # Check if result has readable content
                        if 'title' in result or 'description' in result or 'content' in result:
                            if 'title' in result:
                                st.markdown(f"**Title:** {result['title']}")
                            if 'description' in result:
                                st.markdown(f"**Description:** {result['description']}")
                            if 'content' in result and isinstance(result['content'], str):
                                st.markdown("**Content:**")
                                st.markdown(result['content'], unsafe_allow_html=False)

                            # Show other metadata
                            other_fields = {k: v for k, v in result.items()
                                          if k not in ['title', 'description', 'content'] and v}
                            if other_fields:
                                st.markdown("**Additional Information:**")
                                st.json(other_fields)
                        else:
                            st.json(result)
                    else:
                        st.markdown(str(result), unsafe_allow_html=False)
        else:
            st.info("No search results found")

    @staticmethod
    def display_raw_documentation_section(raw_documentation: Optional[list]):
        """Display raw documentation section for usecases"""
        if not raw_documentation:
            st.info("No raw documentation available")
            return

        st.subheader("📚 Raw Documentation")

        # Separate main documents and recommendations
        main_docs = [doc for doc in raw_documentation if doc.get('type') == 'main_content']
        recommendations = [doc for doc in raw_documentation if doc.get('type') == 'recommendation']
        other_docs = [doc for doc in raw_documentation if doc.get('type') not in ['main_content', 'recommendation']]

        # Display main documents
        if main_docs:
            st.markdown("### 📄 Main Documents")
            for i, doc in enumerate(main_docs):
                source = doc.get('source', f'Document {i+1}')
                content = doc.get('content', '')

                # Show source query if available
                source_query = doc.get('source_query')
                title_suffix = f" (Query: {source_query})" if source_query else ""

                UsecaseDocumentDisplay.display_document_content(
                    content,
                    f"Main Document: {source}{title_suffix}"
                )

        # Display recommendations
        if recommendations:
            st.markdown("### 💡 Recommendations")
            for i, doc in enumerate(recommendations):
                source = doc.get('source', f'Recommendation {i+1}')
                parent = doc.get('parent', 'Unknown')
                content = doc.get('content', '')

                # Show source query if available
                source_query = doc.get('source_query')
                title_suffix = f" (Query: {source_query})" if source_query else ""

                UsecaseDocumentDisplay.display_document_content(
                    content,
                    f"Recommendation: {source} (from {parent}){title_suffix}"
                )

        # Display other documents
        if other_docs:
            st.markdown("### 📋 Other Documents")
            for i, doc in enumerate(other_docs):
                source = doc.get('source', f'Document {i+1}')
                doc_type = doc.get('type', 'Unknown')
                content = doc.get('content', '')

                UsecaseDocumentDisplay.display_document_content(
                    content,
                    f"{doc_type.title()}: {source}"
                )

        # Show summary statistics
        total_docs = len(main_docs) + len(recommendations) + len(other_docs)
        if total_docs > 0:
            st.markdown("---")
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("📄 Main Documents", len(main_docs))
            with col2:
                st.metric("💡 Recommendations", len(recommendations))
            with col3:
                st.metric("📋 Other Documents", len(other_docs))
            with col4:
                st.metric("📊 Total Content", total_docs)

    @classmethod
    def display_usecase_documentation_data(cls, data: Optional[Dict[str, Any]]):
        """Display complete usecase documentation data"""
        # Handle None data
        if data is None:
            st.info("No usecase documentation data available.")
            return

        # Handle empty data
        if not data:
            st.info("No usecase documentation data found.")
            return

        # Check for errors
        if isinstance(data, dict) and data.get("error"):
            st.error(f"❌ Error: {data['error']}")
            return

        # Display usecase metadata first
        cls.display_usecase_metadata(data)

        # Add some spacing
        st.markdown("---")

        # Display enhanced usecase summary (main feature)
        enhanced_documentation = data.get('enhanced_documentation', {})
        if enhanced_documentation:
            cls.display_enhanced_usecase_summary(enhanced_documentation)
            st.markdown("---")

        # Display search results
        search_results = data.get('search_results', {})
        if search_results:
            cls.display_search_results(search_results)
            st.markdown("---")

        # Display raw documentation (this is the supporting content)
        raw_documentation = data.get('raw_documentation', [])
        if raw_documentation:
            with st.expander("📚 View Raw Documentation", expanded=False):
                cls.display_raw_documentation_section(raw_documentation)

    @staticmethod
    def display_usecase_analytics(analytics_data: Dict[str, Any]):
        """Display usecase analytics dashboard"""
        if not analytics_data:
            st.info("No analytics data available")
            return
        
        st.subheader("📊 Use Case Analytics Dashboard")
        
        # Main metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("🎯 Total Queries", analytics_data.get('total_queries', 0))
        with col2:
            st.metric("📚 Total Documents", analytics_data.get('total_docs', 0))
        with col3:
            st.metric("🤖 Bedrock Enhanced", analytics_data.get('bedrock_enhanced', 0))
        with col4:
            st.metric("✨ Query Refined", analytics_data.get('query_refined', 0))
        
        # Charts section
        col5, col6 = st.columns(2)
        
        with col5:
            # Use case queries distribution
            usecase_queries = analytics_data.get('usecase_queries', {})
            if usecase_queries:
                st.markdown("### 🎯 Popular Use Case Queries")
                st.bar_chart(usecase_queries)
        
        with col6:
            # Key services distribution
            key_services = analytics_data.get('key_services', {})
            if key_services:
                st.markdown("### 🔧 Most Referenced AWS Services")
                st.bar_chart(key_services)
        
        # Recent queries table
        recent_queries = analytics_data.get('recent_queries', [])
        if recent_queries:
            st.markdown("### 📝 Recent Use Case Queries")
            
            # Create a formatted table
            formatted_queries = []
            for query in recent_queries[:5]:  # Show last 5
                formatted_queries.append({
                    'Query': query.get('original_query', 'N/A')[:50] + '...' if len(query.get('original_query', '')) > 50 else query.get('original_query', 'N/A'),
                    'Services': ', '.join(query.get('key_services', [])[:2]),
                    'Docs': query.get('total_docs', 0),
                    'Enhanced': '✅' if query.get('enhanced_by_bedrock', False) else '❌',
                    'Refined': '✅' if query.get('query_refined', False) else '❌'
                })
            
            if formatted_queries:
                st.table(formatted_queries)


# Backward compatibility - alias for the old class name
DocumentDisplay = UsecaseDocumentDisplay