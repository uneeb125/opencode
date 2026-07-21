# Browser Agent Configuration

## User Information
- Full Name: Uneeb Kamal
- Username: uneeb125
- Email: uneebkamal125@gmail.com

Always use `uv` for Python environment management and execution.

## Python Environment Setup
- Use `uv venv` to create virtual environments
- Use `uv pip install` to install packages
- Use `uv run` or `uv python` to execute Python scripts and commands

## Execution Commands
- Run scripts: `uv run script.py`
- Run Python commands: `uv run python -c "command"`
- Install packages: `uv pip install package_name"
- Create venv: `uv venv .venv`

## Web Search Tool Selection

Two search MCP tools are available. Choose based on the trade-offs below:

### Primary: `exa_web_search_exa` / `exa_web_fetch_exa`
- **Speed**: <1s per query (instant)
- **Reliability**: 100% success rate across tests
- **Result diversity**: 3 results from distinct sources per query
- **Metadata**: Title, URL, published date, author, rich highlights
- **Content**: Structured highlights/snippets (sufficient for most queries)
- **Use for**: General web search, news, technical docs, blog posts, competitive analysis

### Secondary: `kindly-web-search_web_search` / `kindly-web-search_get_content`
- **Speed**: 6-34s per query (very slow — Chromium pool crashes, retries, Reddit blocks)
- **Failures observed**: Reddit blocks headless Chromium, pool crashes with `'NoneType' object has no attribute 'send'`, 30s pool timeouts
- **Content**: Full article text extraction via headless Chromium
- **Use ONLY for**: arXiv papers (structured abstract/metadata), StackExchange (Q&A with votes), GitHub Issues (parsed comments), Wikipedia (infobox extraction)
- **Never use** when `exa_web_search_exa` gives reasonable results — Exa is 10-30x faster and more reliable

### Rule of thumb
1. Always try Exa first for any search
2. Only fall back to kindly-web-search if you need specialized extraction (arXiv, StackExchange, GitHub Issues, Wikipedia) and Exa's highlights are insufficient