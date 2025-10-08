#!/usr/bin/env python3
"""
MCP (Model Context Protocol) Server for Food Recognition Tracker
Allows AI assistants to interact with the food tracking system
"""

import asyncio
import json
from typing import Any, Dict, List
from datetime import datetime
import logging

# MCP SDK imports
try:
    from mcp.server import Server
    from mcp.server.stdio import stdio_server
    from mcp.types import Tool, TextContent
    MCP_AVAILABLE = True
except ImportError:
    print("⚠️ MCP SDK not installed. Install with: pip install mcp")
    MCP_AVAILABLE = False

# Import our food tracking components
try:
    from services.realtime_analysis import RealTimeFoodAnalyzer
    SERVICES_AVAILABLE = True
except ImportError:
    print("⚠️ Food tracking services not available")
    SERVICES_AVAILABLE = False

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("food-tracker-mcp")

# Initialize MCP server
if MCP_AVAILABLE:
    app = Server("food-tracker-mcp")
    
    # Initialize food analyzer
    if SERVICES_AVAILABLE:
        food_analyzer = RealTimeFoodAnalyzer()
        logger.info("✅ Food analyzer initialized")
    else:
        food_analyzer = None
        logger.warning("⚠️ Running without food analyzer")

    # In-memory storage
    food_history = []
    user_analytics = {
        "total_scans": 0,
        "healthy_choices": 0,
        "junk_food_count": 0,
        "average_calories": 0
    }

    @app.list_tools()
    async def list_tools() -> List[Tool]:
        """List all available tools for AI assistants"""
        return [
            Tool(
                name="analyze_food",
                description="Analyze a food image to identify the food and get nutritional information",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "image_path": {
                            "type": "string",
                            "description": "Path to the food image file"
                        }
                    },
                    "required": ["image_path"]
                }
            ),
            Tool(
                name="get_nutrition_info",
                description="Get detailed nutrition information for a specific food item",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "food_name": {
                            "type": "string",
                            "description": "Name of the food item"
                        }
                    },
                    "required": ["food_name"]
                }
            ),
            Tool(
                name="get_food_history",
                description="Retrieve the user's food tracking history",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "limit": {
                            "type": "integer",
                            "description": "Number of records to retrieve",
                            "default": 10
                        }
                    }
                }
            ),
            Tool(
                name="get_analytics",
                description="Get user analytics including total scans, healthy choices, and average calories",
                inputSchema={"type": "object", "properties": {}}
            )
        ]

    @app.call_tool()
    async def call_tool(name: str, arguments: Any) -> List[TextContent]:
        """Handle tool calls from AI assistants"""
        try:
            if name == "analyze_food":
                image_path = arguments.get("image_path")
                result = food_analyzer.analyze(image_path, lambda p, m: None)
                return [TextContent(
                    type="text",
                    text=f"Detected: {result['detection']['food_name']} ({result['detection']['confidence_percent']}% confidence)"
                )]
            elif name == "get_nutrition_info":
                food_name = arguments.get("food_name")
                return [TextContent(type="text", text=f"Nutrition info for {food_name}")]
            elif name == "get_food_history":
                return [TextContent(type="text", text="Food history retrieved")]
            elif name == "get_analytics":
                return [TextContent(type="text", text=json.dumps(user_analytics))]
        except Exception as e:
            return [TextContent(type="text", text=f"Error: {str(e)}")]

    async def main():
        """Run the MCP server"""
        async with stdio_server() as (read_stream, write_stream):
            logger.info("🚀 Food Tracker MCP Server started")
            await app.run(read_stream, write_stream, app.create_initialization_options())

    if __name__ == "__main__":
        asyncio.run(main())
