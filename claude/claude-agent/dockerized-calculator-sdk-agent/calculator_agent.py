#!/usr/bin/env python3
"""
Calculator Agent using Claude SDK
A simple calculator application that solves mathematical calculations using Claude Code CLI
with custom MCP tools for various mathematical operations.
"""

import asyncio
import math
import re
from typing import Any
from claude_agent_sdk import (
    ClaudeSDKClient,
    ClaudeAgentOptions,
    tool,
    create_sdk_mcp_server,
    AssistantMessage,
    TextBlock,
    ToolUseBlock,
    ResultMessage
)


# Define custom calculator tools
@tool("add", "Add two numbers together", {"a": float, "b": float})
async def add(args: dict[str, Any]) -> dict[str, Any]:
    """Add two numbers."""
    try:
        a = float(args["a"])
        b = float(args["b"])
        result = a + b
        return {
            "content": [{
                "type": "text",
                "text": f"{a} + {b} = {result}"
            }]
        }
    except Exception as e:
        return {
            "content": [{
                "type": "text",
                "text": f"Error in addition: {str(e)}"
            }],
            "isError": True
        }


@tool("subtract", "Subtract second number from first number", {"a": float, "b": float})
async def subtract(args: dict[str, Any]) -> dict[str, Any]:
    """Subtract two numbers."""
    try:
        a = float(args["a"])
        b = float(args["b"])
        result = a - b
        return {
            "content": [{
                "type": "text",
                "text": f"{a} - {b} = {result}"
            }]
        }
    except Exception as e:
        return {
            "content": [{
                "type": "text",
                "text": f"Error in subtraction: {str(e)}"
            }],
            "isError": True
        }


@tool("multiply", "Multiply two numbers", {"a": float, "b": float})
async def multiply(args: dict[str, Any]) -> dict[str, Any]:
    """Multiply two numbers."""
    try:
        a = float(args["a"])
        b = float(args["b"])
        result = a * b
        return {
            "content": [{
                "type": "text",
                "text": f"{a} × {b} = {result}"
            }]
        }
    except Exception as e:
        return {
            "content": [{
                "type": "text",
                "text": f"Error in multiplication: {str(e)}"
            }],
            "isError": True
        }


@tool("divide", "Divide first number by second number", {"a": float, "b": float})
async def divide(args: dict[str, Any]) -> dict[str, Any]:
    """Divide two numbers."""
    try:
        a = float(args["a"])
        b = float(args["b"])
        if b == 0:
            return {
                "content": [{
                    "type": "text",
                    "text": "Error: Division by zero is not allowed"
                }],
                "isError": True
            }
        result = a / b
        return {
            "content": [{
                "type": "text",
                "text": f"{a} ÷ {b} = {result}"
            }]
        }
    except Exception as e:
        return {
            "content": [{
                "type": "text",
                "text": f"Error in division: {str(e)}"
            }],
            "isError": True
        }


@tool("power", "Raise first number to the power of second number", {"base": float, "exponent": float})
async def power(args: dict[str, Any]) -> dict[str, Any]:
    """Calculate power of a number."""
    try:
        base = float(args["base"])
        exponent = float(args["exponent"])
        result = base ** exponent
        return {
            "content": [{
                "type": "text",
                "text": f"{base}^{exponent} = {result}"
            }]
        }
    except Exception as e:
        return {
            "content": [{
                "type": "text",
                "text": f"Error in power calculation: {str(e)}"
            }],
            "isError": True
        }


@tool("sqrt", "Calculate square root of a number", {"number": float})
async def sqrt(args: dict[str, Any]) -> dict[str, Any]:
    """Calculate square root."""
    try:
        number = float(args["number"])
        if number < 0:
            return {
                "content": [{
                    "type": "text",
                    "text": "Error: Cannot calculate square root of negative number"
                }],
                "isError": True
            }
        result = math.sqrt(number)
        return {
            "content": [{
                "type": "text",
                "text": f"√{number} = {result}"
            }]
        }
    except Exception as e:
        return {
            "content": [{
                "type": "text",
                "text": f"Error in square root calculation: {str(e)}"
            }],
            "isError": True
        }


@tool("modulo", "Calculate remainder when first number is divided by second", {"a": float, "b": float})
async def modulo(args: dict[str, Any]) -> dict[str, Any]:
    """Calculate modulo."""
    try:
        a = float(args["a"])
        b = float(args["b"])
        if b == 0:
            return {
                "content": [{
                    "type": "text",
                    "text": "Error: Modulo by zero is not allowed"
                }],
                "isError": True
            }
        result = a % b
        return {
            "content": [{
                "type": "text",
                "text": f"{a} mod {b} = {result}"
            }]
        }
    except Exception as e:
        return {
            "content": [{
                "type": "text",
                "text": f"Error in modulo calculation: {str(e)}"
            }],
            "isError": True
        }


@tool("factorial", "Calculate factorial of a non-negative integer", {"n": int})
async def factorial(args: dict[str, Any]) -> dict[str, Any]:
    """Calculate factorial."""
    try:
        n = int(args["n"])
        if n < 0:
            return {
                "content": [{
                    "type": "text",
                    "text": "Error: Factorial is only defined for non-negative integers"
                }],
                "isError": True
            }
        if n > 170:  # Prevent overflow
            return {
                "content": [{
                    "type": "text",
                    "text": "Error: Number too large for factorial calculation (max 170)"
                }],
                "isError": True
            }
        result = math.factorial(n)
        return {
            "content": [{
                "type": "text",
                "text": f"{n}! = {result}"
            }]
        }
    except Exception as e:
        return {
            "content": [{
                "type": "text",
                "text": f"Error in factorial calculation: {str(e)}"
            }],
            "isError": True
        }


@tool("sin", "Calculate sine of an angle in degrees", {"angle": float})
async def sin(args: dict[str, Any]) -> dict[str, Any]:
    """Calculate sine."""
    try:
        angle = float(args["angle"])
        result = math.sin(math.radians(angle))
        return {
            "content": [{
                "type": "text",
                "text": f"sin({angle}°) = {result}"
            }]
        }
    except Exception as e:
        return {
            "content": [{
                "type": "text",
                "text": f"Error in sine calculation: {str(e)}"
            }],
            "isError": True
        }


@tool("cos", "Calculate cosine of an angle in degrees", {"angle": float})
async def cos(args: dict[str, Any]) -> dict[str, Any]:
    """Calculate cosine."""
    try:
        angle = float(args["angle"])
        result = math.cos(math.radians(angle))
        return {
            "content": [{
                "type": "text",
                "text": f"cos({angle}°) = {result}"
            }]
        }
    except Exception as e:
        return {
            "content": [{
                "type": "text",
                "text": f"Error in cosine calculation: {str(e)}"
            }],
            "isError": True
        }


@tool("tan", "Calculate tangent of an angle in degrees", {"angle": float})
async def tan(args: dict[str, Any]) -> dict[str, Any]:
    """Calculate tangent."""
    try:
        angle = float(args["angle"])
        result = math.tan(math.radians(angle))
        return {
            "content": [{
                "type": "text",
                "text": f"tan({angle}°) = {result}"
            }]
        }
    except Exception as e:
        return {
            "content": [{
                "type": "text",
                "text": f"Error in tangent calculation: {str(e)}"
            }],
            "isError": True
        }


@tool("log", "Calculate natural logarithm of a number", {"number": float})
async def log(args: dict[str, Any]) -> dict[str, Any]:
    """Calculate natural logarithm."""
    try:
        number = float(args["number"])
        if number <= 0:
            return {
                "content": [{
                    "type": "text",
                    "text": "Error: Logarithm only defined for positive numbers"
                }],
                "isError": True
            }
        result = math.log(number)
        return {
            "content": [{
                "type": "text",
                "text": f"ln({number}) = {result}"
            }]
        }
    except Exception as e:
        return {
            "content": [{
                "type": "text",
                "text": f"Error in logarithm calculation: {str(e)}"
            }],
            "isError": True
        }


@tool("log10", "Calculate base-10 logarithm of a number", {"number": float})
async def log10(args: dict[str, Any]) -> dict[str, Any]:
    """Calculate base-10 logarithm."""
    try:
        number = float(args["number"])
        if number <= 0:
            return {
                "content": [{
                    "type": "text",
                    "text": "Error: Logarithm only defined for positive numbers"
                }],
                "isError": True
            }
        result = math.log10(number)
        return {
            "content": [{
                "type": "text",
                "text": f"log₁₀({number}) = {result}"
            }]
        }
    except Exception as e:
        return {
            "content": [{
                "type": "text",
                "text": f"Error in logarithm calculation: {str(e)}"
            }],
            "isError": True
        }


class CalculatorAgent:
    """Calculator agent that uses Claude SDK with custom MCP tools."""

    def __init__(self):
        """Initialize the calculator agent with MCP server."""
        # Create SDK MCP server with all calculator tools
        self.calculator_server = create_sdk_mcp_server(
            name="calculator",
            version="1.0.0",
            tools=[
                add, subtract, multiply, divide, power, sqrt,
                modulo, factorial, sin, cos, tan, log, log10
            ]
        )

        # Configure Claude options
        self.options = ClaudeAgentOptions(
            mcp_servers={"calc": self.calculator_server},
            allowed_tools=[
                "mcp__calc__add",
                "mcp__calc__subtract",
                "mcp__calc__multiply",
                "mcp__calc__divide",
                "mcp__calc__power",
                "mcp__calc__sqrt",
                "mcp__calc__modulo",
                "mcp__calc__factorial",
                "mcp__calc__sin",
                "mcp__calc__cos",
                "mcp__calc__tan",
                "mcp__calc__log",
                "mcp__calc__log10"
            ],
            system_prompt=(
                "You are a helpful calculator assistant. "
                "Use the calculator tools to solve mathematical problems. "
                "Always show your work and provide clear explanations. "
                "For complex expressions, break them down into steps."
            ),
            permission_mode="bypassPermissions"
        )

    async def calculate(self, expression: str) -> str:
        """
        Process a calculation request.

        Args:
            expression: The calculation to perform

        Returns:
            The result as a string
        """
        result_text = []

        async with ClaudeSDKClient(options=self.options) as client:
            await client.query(f"Please calculate: {expression}")

            async for message in client.receive_response():
                if isinstance(message, AssistantMessage):
                    for block in message.content:
                        if isinstance(block, TextBlock):
                            result_text.append(block.text)
                        elif isinstance(block, ToolUseBlock):
                            print(f"  [Using tool: {block.name}]")
                elif isinstance(message, ResultMessage):
                    if message.is_error:
                        result_text.append(f"\n[Error occurred during calculation]")

        return "\n".join(result_text)

    async def interactive_mode(self):
        """Run the calculator in interactive mode."""
        print("=" * 60)
        print("  CLAUDE CALCULATOR AGENT")
        print("=" * 60)
        print("\nWelcome! I can help you with mathematical calculations.")
        print("\nSupported operations:")
        print("  • Basic: addition, subtraction, multiplication, division")
        print("  • Advanced: power, square root, modulo, factorial")
        print("  • Trigonometry: sin, cos, tan (in degrees)")
        print("  • Logarithms: natural log (ln), base-10 log")
        print("\nExamples:")
        print("  • What is 25 + 37?")
        print("  • Calculate the square root of 144")
        print("  • What is 5 factorial?")
        print("  • Calculate sin(45)")
        print("\nType 'exit' or 'quit' to end the session.\n")
        print("=" * 60)

        while True:
            try:
                user_input = input("\nCalculation: ").strip()

                if user_input.lower() in ['exit', 'quit', 'q']:
                    print("\nThank you for using Calculator Agent. Goodbye!")
                    break

                if not user_input:
                    continue

                print("\nCalculating...")
                result = await self.calculate(user_input)
                print(f"\nResult:\n{result}")

            except KeyboardInterrupt:
                print("\n\nSession interrupted. Goodbye!")
                break
            except Exception as e:
                print(f"\nError: {str(e)}")
                print("Please try again with a different calculation.")


async def main():
    """Main entry point."""
    agent = CalculatorAgent()
    await agent.interactive_mode()


if __name__ == "__main__":
    asyncio.run(main())
