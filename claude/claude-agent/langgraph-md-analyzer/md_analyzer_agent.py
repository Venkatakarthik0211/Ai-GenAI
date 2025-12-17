#!/usr/bin/env python3
"""
LangGraph Markdown Analyzer with Claude SDK Agent
A LangGraph workflow with a single node that uses Claude SDK to analyze markdown files.
"""

import asyncio
import os
from typing import TypedDict, Annotated, Optional
from langgraph.graph import StateGraph, END
from langgraph.graph.state import CompiledStateGraph
from claude_agent_sdk import (
    ClaudeSDKClient,
    ClaudeAgentOptions,
    AssistantMessage,
    TextBlock,
    ResultMessage
)


# Define the state for our graph
class AnalyzerState(TypedDict):
    """State for the markdown analyzer workflow."""
    file_path: str
    file_content: Optional[str]
    summary: Optional[str]
    analysis: Optional[str]
    error: Optional[str]
    status: str


class ClaudeSDKAnalyzerNode:
    """LangGraph node that uses Claude SDK to analyze markdown files."""

    def __init__(self):
        """Initialize the Claude SDK analyzer node."""
        self.options = ClaudeAgentOptions(
            allowed_tools=["Read", "Write", "Glob", "Grep"],
            system_prompt=(
                "You are an expert markdown file analyzer. "
                "When given a file path, read the file and provide:\n"
                "1. A concise summary (2-3 sentences)\n"
                "2. Key topics and themes\n"
                "3. Document structure analysis\n"
                "4. Any notable patterns or issues\n"
                "Be clear, structured, and thorough in your analysis."
            ),
            permission_mode="bypassPermissions"
        )

    async def analyze_markdown(self, state: AnalyzerState) -> AnalyzerState:
        """
        Analyze a markdown file using Claude SDK.

        Args:
            state: Current workflow state with file_path

        Returns:
            Updated state with analysis results
        """
        file_path = state["file_path"]

        print(f"\n{'='*60}")
        print(f"  ANALYZING: {file_path}")
        print(f"{'='*60}\n")

        try:
            # Check if file exists
            if not os.path.exists(file_path):
                state["error"] = f"File not found: {file_path}"
                state["status"] = "error"
                return state

            # Use Claude SDK to analyze the file
            analysis_results = []

            async with ClaudeSDKClient(options=self.options) as client:
                prompt = f"""Please analyze the markdown file at: {file_path}

Read the file and provide:
1. A concise summary (2-3 sentences)
2. Key topics and main themes
3. Document structure (headings, sections)
4. Any notable patterns, issues, or recommendations

Format your response clearly with these sections."""

                await client.query(prompt)

                print("🔍 Claude is analyzing the file...")

                async for message in client.receive_response():
                    if isinstance(message, AssistantMessage):
                        for block in message.content:
                            if isinstance(block, TextBlock):
                                analysis_results.append(block.text)
                    elif isinstance(message, ResultMessage):
                        if message.is_error:
                            state["error"] = "Error occurred during analysis"
                            state["status"] = "error"
                            return state

            # Combine all analysis results
            full_analysis = "\n".join(analysis_results)

            # Extract summary (first paragraph typically)
            lines = full_analysis.split("\n")
            summary_lines = []
            for line in lines[:10]:  # Look in first 10 lines
                if line.strip() and not line.startswith("#"):
                    summary_lines.append(line.strip())
                if len(summary_lines) >= 3:
                    break

            state["analysis"] = full_analysis
            state["summary"] = " ".join(summary_lines) if summary_lines else full_analysis[:200]
            state["status"] = "completed"

            print("\n✅ Analysis completed successfully!")

        except Exception as e:
            state["error"] = str(e)
            state["status"] = "error"
            print(f"\n❌ Error: {str(e)}")

        return state


class MarkdownAnalyzerGraph:
    """LangGraph workflow for analyzing markdown files."""

    def __init__(self):
        """Initialize the LangGraph workflow."""
        self.analyzer_node = ClaudeSDKAnalyzerNode()
        self.graph: Optional[CompiledStateGraph] = None
        self._build_graph()

    def _build_graph(self):
        """Build the LangGraph workflow."""
        # Create the graph
        workflow = StateGraph(AnalyzerState)

        # Add the single analyzer node
        workflow.add_node("analyze", self.analyzer_node.analyze_markdown)

        # Set entry point
        workflow.set_entry_point("analyze")

        # Set finish point
        workflow.add_edge("analyze", END)

        # Compile the graph
        self.graph = workflow.compile()

        print("📊 LangGraph workflow built successfully!")
        print("   Nodes: [analyze]")
        print("   Flow: START -> analyze -> END\n")

    async def analyze_file(self, file_path: str) -> AnalyzerState:
        """
        Analyze a markdown file through the workflow.

        Args:
            file_path: Path to the markdown file

        Returns:
            Final state with analysis results
        """
        if not self.graph:
            raise RuntimeError("Graph not initialized")

        # Initialize state
        initial_state: AnalyzerState = {
            "file_path": file_path,
            "file_content": None,
            "summary": None,
            "analysis": None,
            "error": None,
            "status": "pending"
        }

        # Run the workflow
        final_state = await self.graph.ainvoke(initial_state)

        return final_state

    def visualize_graph(self, output_path: str = "graph_visualization.png"):
        """
        Generate a visual representation of the LangGraph workflow.

        Args:
            output_path: Path to save the visualization
        """
        try:
            if not self.graph:
                print("❌ Graph not initialized")
                return

            # Generate graph visualization using Mermaid PNG
            graph_image = self.graph.get_graph().draw_mermaid_png()

            # Save to file
            with open(output_path, "wb") as f:
                f.write(graph_image)

            print(f"✅ Graph visualization saved to: {output_path}")

            # Also generate ASCII representation for terminal
            print("\n📊 Workflow Structure:")
            print("=" * 50)
            print("   START")
            print("     ↓")
            print("   [analyze: Claude SDK Agent]")
            print("     ↓")
            print("   END")
            print("=" * 50)

        except Exception as e:
            print(f"⚠️  Could not generate visualization: {str(e)}")
            # Fallback to simple ASCII diagram
            print("\n📊 Workflow Structure (ASCII):")
            print("=" * 50)
            print("   START → [analyze] → END")
            print("=" * 50)


class InteractiveAnalyzer:
    """Interactive interface for the markdown analyzer."""

    def __init__(self):
        """Initialize the interactive analyzer."""
        self.graph = MarkdownAnalyzerGraph()

    async def run_interactive(self):
        """Run the analyzer in interactive mode."""
        print("=" * 70)
        print("  LANGGRAPH MARKDOWN ANALYZER - Claude SDK Agent")
        print("=" * 70)
        print("\n📄 This tool analyzes markdown files using a LangGraph workflow")
        print("   with Claude SDK as the analysis node.\n")
        print("Features:")
        print("  • Reads and analyzes markdown files")
        print("  • Provides summaries and key insights")
        print("  • Analyzes document structure")
        print("  • Identifies themes and patterns\n")
        print("Commands:")
        print("  • Enter a file path to analyze")
        print("  • Type 'visualize' to see the workflow graph")
        print("  • Type 'exit' or 'quit' to end session\n")
        print("=" * 70)

        while True:
            try:
                user_input = input("\n📁 File path (or command): ").strip()

                if user_input.lower() in ['exit', 'quit', 'q']:
                    print("\n👋 Thank you for using Markdown Analyzer. Goodbye!")
                    break

                if user_input.lower() == 'visualize':
                    print("\n📊 Generating workflow visualization...")
                    self.graph.visualize_graph("logs/workflow_graph.png")
                    continue

                if not user_input:
                    continue

                # Analyze the file
                result = await self.graph.analyze_file(user_input)

                # Display results
                print("\n" + "=" * 70)
                print("  ANALYSIS RESULTS")
                print("=" * 70)

                if result["status"] == "error":
                    print(f"\n❌ Error: {result['error']}")
                else:
                    print(f"\n📊 Summary:")
                    print(f"   {result['summary']}\n")
                    print(f"📝 Full Analysis:")
                    print("-" * 70)
                    print(result['analysis'])
                    print("-" * 70)

                # Ask if user wants to save the analysis
                save = input("\n💾 Save analysis to file? (y/n): ").strip().lower()
                if save == 'y':
                    output_file = f"logs/analysis_{os.path.basename(user_input)}.txt"
                    with open(output_file, 'w') as f:
                        f.write(f"File: {user_input}\n")
                        f.write(f"Status: {result['status']}\n")
                        f.write(f"\nSummary:\n{result['summary']}\n")
                        f.write(f"\nFull Analysis:\n{result['analysis']}\n")
                    print(f"✅ Analysis saved to: {output_file}")

            except KeyboardInterrupt:
                print("\n\n👋 Session interrupted. Goodbye!")
                break
            except Exception as e:
                print(f"\n❌ Error: {str(e)}")
                print("Please try again with a valid file path.")


async def main():
    """Main entry point."""
    analyzer = InteractiveAnalyzer()

    # Generate workflow visualization at startup
    print("\n📊 Generating workflow visualization...")
    analyzer.graph.visualize_graph("logs/workflow_graph.png")

    # Run interactive mode
    await analyzer.run_interactive()


if __name__ == "__main__":
    asyncio.run(main())
