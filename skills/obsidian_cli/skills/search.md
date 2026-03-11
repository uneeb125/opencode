---
title: Obsidian CLI - Search & Graph
description: Commands for finding text, exploring tags, and navigating the link graph.
---

# Search & Navigation

## Search
*   **Find Files:** `obsidian search query="<text>"`
    *   Params: `path=<folder>`, `limit=<n>`, `format=text|json`
    *   Flags: `total`, `case`
*   **Grep Context:** `obsidian search:context query="<text>"` (Shows line numbers/content)
*   **Open UI:** `obsidian search:open query="<text>"`

## Tags
*   **List All:** `obsidian tags` (Flags: `sort=count`, `total`, `counts`)
*   **Specific File:** `obsidian tags file=<name>`
*   **Tag Info:** `obsidian tag name=<tag>` (Flags: `total`, `verbose`)

## Graph Connections
*   **Backlinks:** `obsidian backlinks file=<name>` (Flags: `counts`, `total`)
*   **Outgoing Links:** `obsidian links file=<name>`
*   **Unresolved:** `obsidian unresolved` (Flags: `total`, `counts`, `verbose`)
*   **Orphans:** `obsidian orphans` (No incoming links)
*   **Deadends:** `obsidian deadends` (No outgoing links)

## Structure
*   **Outline:** `obsidian outline file=<name>` (Headings tree)
*   **Random Note:** `obsidian random` or `obsidian random:read` (Param: `folder=<path>`)
