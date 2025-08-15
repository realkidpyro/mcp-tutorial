# add_server.py

import textwrap
import requests
from bs4 import BeautifulSoup
from readability import Document
from openai import OpenAI
from fastmcp import FastMCP

# Configuration
API_KEY = "YOUR_API_KEY_HERE"
MODEL = "gpt-4o"
HOST = "127.0.0.1"
PORT = 8000
TRANSPORT = "http"

# Create the MCP server instance
mcp = FastMCP(name="my_mcp_tools")  # Must match label in the client

# Tool: Add two numbers
@mcp.tool(description="Add two numbers together")
def add_numbers(x: float, y: float) -> dict:
    return {"result": x + y}

# Tool: Summarize a URL
@mcp.tool(description="Summarize a URL in ~200 words")
def summarize_url(url: str, focus: str = "", words: int = 200) -> dict:
    try:
        r = requests.get(url, timeout=10, headers={"User-Agent": "MCP-URL-Bot/1.0"})
        r.ra
