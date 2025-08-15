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
        r.raise_for_status()
        html = Document(r.text).summary(html_partial=True) or r.text
        soup = BeautifulSoup(html, "lxml")
        for tag in soup(["script", "style", "noscript"]):
            tag.decompose()
        text = "\n".join(ln.strip() for ln in soup.get_text("\n").splitlines() if ln.strip())
    except Exception as e:
        return {"ok": False, "error": f"fetch_failed: {e}"}

    # Limit text length for processing
    text = text[:12000]
    focus_line = f"\nFocus: {focus.strip()}\n" if focus else ""
    prompt = textwrap.dedent(f"""
        Summarize the page in ~{words} words. Be accurate; do not invent facts.
        Use bullet points if helpful.{focus_line}
        --- PAGE START ---
        {text}
        --- PAGE END ---
    """).strip()

    try:
        client = OpenAI(api_key=API_KEY)
        response = client.responses.create(model=MODEL, input=prompt)
        return {"ok": True, "summary": response.output_text or ""}
    except Exception as e:
        return {"ok": False, "error": f"llm_failed: {e}"}

# Run the server
if __name__ == "__main__":
    if TRANSPORT == "http":
        mcp.run(transport="http", host=HOST, port=PORT)
    else:
        mcp.run(transport="stdio")
