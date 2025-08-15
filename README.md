# MCP Server Tutorial

## Introduction
In this guide, you’ll learn how to set up and run an MCP (Model Context Protocol) server with your own tools.  
The two example tools here are:
- `add_numbers` → Adds two numbers together
- `summarize_url` → Summarizes the content of a given webpage using an AI API call.

You can replace these with any tools you want once your server is working.

---

## Prerequisites
- Python 3.10+
- Git installed
- [FastMCP](https://pypi.org/project/fastmcp/)
- [Requests](https://pypi.org/project/requests/)
- [BeautifulSoup4](https://pypi.org/project/beautifulsoup4/)
- [Readability-lxml](https://pypi.org/project/readability-lxml/)
- OpenAI API key with access to `gpt-4o`
- (Optional) [cloudflared](https://developers.cloudflare.com/cloudflare-one/connections/connect-apps/install-and-setup/installation/) for tunneling

---

## Step 1: Clone the Repository
```bash
git clone https://github.com/<your-username>/<your-repo>.git
cd <your-repo>

---

## Step 2: Create a Virtual Environment and Install Dependencies
```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .\\.venv\\Scripts\\activate
pip install -r requirements.txt

```nginx
fastmcp
requests
beautifulsoup4
readability-lxml
opena

