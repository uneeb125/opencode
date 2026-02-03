---
name: open_tab_gquery
description: Opens Google or DuckDuckGo search in the user's default browser using xdg-open
---

# Open Tab Google/DuckDuckGo Query Skill

You help users search Google or DuckDuckGo by opening search results in their default browser via xdg-open.

## When to Use

- User asks to search Google or DuckDuckGo for something
- User wants to look up information online
- User references searching the web

## Workflow

### Step 1: Extract the Query

Identify the search query from the user's request. The query can be:
- Direct: "search for python tutorials"
- Implicit: "how do I install docker" → query = "how do I install docker"
- Follow-up: previous context provides the topic

### Step 2: URL Encode the Query

The query must be URL-encoded for the search URL. Replace spaces with `%20` and other special characters accordingly.

Example:
- "python tutorials" → "python%20tutorials"
- "docker install" → "docker%20install"

### Step 3: Choose Search Engine

Determine which search engine to use:
- Default: Google (if not specified)
- DuckDuckGo: if user explicitly mentions "duckduckgo" or "ddg"
- Google: if user explicitly mentions "google"

### Step 4: Execute xdg-open

Run the xdg-open command with the encoded query:

**For Google:**
```bash
xdg-open "https://www.google.com/search?client=firefox-b-1-d&q=<encoded_query>"
```

**For DuckDuckGo:**
```bash
xdg-open "https://duckduckgo.com/?ia=web&origin=funnel_home_website&t=h_&q=<encoded_query>"
```

Replace `<encoded_query>` with the URL-encoded search query.

## Examples

**Example 1: Google search (default)**

User request: "search for react hooks tutorial"

1. Query: "react hooks tutorial"
2. Engine: Google (default)
3. Encoded query: "react%20hooks%20tutorial"
4. Command:
```bash
xdg-open "https://www.google.com/search?client=firefox-b-1-d&q=react%20hooks%20tutorial"
```

**Example 2: DuckDuckGo search**

User request: "search duckduckgo for rust documentation"

1. Query: "rust documentation"
2. Engine: DuckDuckGo (user specified)
3. Encoded query: "rust%20documentation"
4. Command:
```bash
xdg-open "https://duckduckgo.com/?ia=web&origin=funnel_home_website&t=h_&q=rust%20documentation"
```
