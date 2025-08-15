[# MCP Server Tutorial

## Introduction
In this guide, you’ll learn how to set up and run an MCP (Model Context Protocol) server with your own tools.
The two example tools here are:
- `add_numbers` → adds two numbers together
- `summarize_url` → fetches a webpage, cleans the text, and summarizes it using an AI API call

Once your server is working, you can swap in any tools you like.

---

## Prerequisites
- Python 3.10+
- Git installed
- [FastMCP](https://pypi.org/project/fastmcp/)
- [Requests](https://pypi.org/project/requests/)
- [BeautifulSoup4](https://pypi.org/project/beautifulsoup4/)
- [Readability-lxml](https://pypi.org/project/readability-lxml/)
- `openai` Python package and an OpenAI API key (model: `gpt-4o`)
- (Optional) [cloudflared](https://developers.cloudflare.com/cloudflare-one/connections/connect-apps/install-and-setup/installation/) for tunneling

---

## Step 1: Clone the Repository
```bash
git clone https://github.com/<your-username>/<your-repo>.git
cd <your-repo>
```

---

## Step 2: Create a Virtual Environment and Install Dependencies
```bash
python -m venv .venv
# macOS/Linux:
source .venv/bin/activate
# Windows (PowerShell):
# .\.venv\Scripts\Activate.ps1

pip install -r requirements.txt
```

**requirements.txt**
```
fastmcp
requests
beautifulsoup4
readability-lxml
openai
lxml
```

---

## Step 3: Configure the Server
Set your OpenAI API key via environment variable (recommended):

```bash
# macOS/Linux
export OPENAI_API_KEY="sk-..."
# Windows (PowerShell)
setx OPENAI_API_KEY "sk-..."
```

In `add_server.py`, ensure:
```python
MODEL = "gpt-4o"
HOST = "127.0.0.1"
PORT = 8000
TRANSPORT = "http"  # or "stdio"
```

When `TRANSPORT="http"`, your server listens on:
```
http://127.0.0.1:8000
```

---

## Step 4: Run the Server
```bash
python add_server.py
```
![MCP server running in terminal](bd10f9cc5f43970b6e0ce998c7ef3709.png/server-running.png)
---

## Step 5: Debug with MCP Inspector (No Tunneling Needed)
Use the official Inspector to test tools locally.

```bash
npx @modelcontextprotocol/inspector
```

**Connect settings:**
- **Transport Type:** `Streamable HTTP`
- **URL:** `http://127.0.0.1:8000/mcp/`

> Connect **only while your Python server is running**.

You’ll see your tools (`add_numbers`, `summarize_url`) and can run them with custom inputs.

---

## Step 6: Put the Server Online with Cloudflared (Optional)
If you want to share your local server:

```bash
cloudflared tunnel --url http://127.0.0.1:8000
```

Cloudflared prints a public URL like:
```
https://<random>.trycloudflare.com
```

**Important:** When using this URL in clients, **append `/mcp/`**:
```
https://<random>.trycloudflare.com/mcp/
```

Keep **both** the Python server **and** cloudflared running while testing.

---

## Step 7: Add the Server to OpenAI Chat
1. Open OpenAI Chat (Models page) → MCP settings
2. **Add MCP Server**
3. Enter:
   - **URL:** your Cloudflare URL **with `/mcp/` appended**
   - **Label:** `my_mcp_tools` (must match your server’s `FastMCP(name="my_mcp_tools")`)
4. Connect while the server and tunnel are running

### Auto tool use from chat
Once connected, the model can propose calling your tools based on your prompt and will ask for confirmation before running.

Example prompt:
> Summarize https://en.wikipedia.org/wiki/Cefnllys_Castle and focus on the scenery.

---

## Step 8: Tool Descriptions
- **add_numbers(x, y)** → returns `{"result": x + y}`
- **summarize_url(url, focus="", words=200)** → fetches, cleans, and summarizes a page; optional focus string and desired word count

---

## Step 9: Full Source — `add_server.py`
```python
# add_server.py
import os
import textwrap
import requests
from bs4 import BeautifulSoup
from readability import Document
from openai import OpenAI
from fastmcp import FastMCP

MODEL = "gpt-4o"
HOST = "127.0.0.1"
PORT = 8000
TRANSPORT = "http"

# IMPORTANT: use env var, do NOT hardcode keys in code
API_KEY = os.getenv("OPENAI_API_KEY")

mcp = FastMCP(name="my_mcp_tools")  # must match the label in your client

@mcp.tool(description="Add two numbers together")
def add_numbers(x: float, y: float) -> dict:
    return {"result": x + y}

@mcp.tool(description="Summarize a URL in ~N words (default 200)")
def summarize_url(url: str, focus: str = "", words: int = 200) -> dict:
    try:
        r = requests.get(url, timeout=10, headers={"User-Agent": "MCP-URL-Bot/1.0"})
        r.raise_for_status()
        html = Document(r.text).summary(html_partial=True) or r.text
        soup = BeautifulSoup(html, "lxml")
        for tag in soup(["script", "style", "noscript"]):
            tag.decompose()
        text = "\\n".join(ln.strip() for ln in soup.get_text("\\n").splitlines() if ln.strip())
    except Exception as e:
        return {"ok": False, "error": f"fetch_failed: {e}"}

    # keep prompt size reasonable
    text = text[:12000]
    focus_line = f"\\nFocus: {focus.strip()}\\n" if focus else ""
    prompt = textwrap.dedent(f"""
        Summarize the page in ~{words} words. Be accurate; do not invent facts.
        Use bullet points if helpful.{focus_line}
        --- PAGE START ---
        {text}
        --- PAGE END ---
    """).strip()

    try:
        client = OpenAI(api_key=API_KEY)
        resp = client.responses.create(model=MODEL, input=prompt)
        return {"ok": True, "summary": (resp.output_text or "").strip()}
    except Exception as e:
        return {"ok": False, "error": f"llm_failed: {e}"}

if __name__ == "__main__":
    if TRANSPORT == "http":
        mcp.run(transport="http", host=HOST, port=PORT)
    else:
        mcp.run(transport="stdio")
```

---

## Step 10: Troubleshooting
- **Inspector can’t connect** → check Transport Type, URL (`/mcp/`), and that the server is running.
- **Tunnel issues** → start the Python server **before** `cloudflared`.
- **`fetch_failed`** → verify the URL and your network.
- **`llm_failed`** → ensure `OPENAI_API_KEY` is set and `MODEL` is valid.
- **Chat not connecting** → confirm tunnel URL ends with `/mcp/` and label matches `my_mcp_tools`.

---

## Final Notes
This tutorial gets **your own MCP server and tools running**. The key is a reliable **server backbone** and a clear **debugging process** (Inspector + tunneling).
From here, customize freely: add, remove, or modify tools to fit your use case.
](https://github.com/realkidpyro/mcp-tutorial/tree/main/pictures)
