---
title: Obsidian CLI - Tasks & Planning
description: Commands for task management, daily notes, and unique note creation.
---

# Tasks & Daily Notes

## Daily Notes
*   **Open:** `obsidian daily` (Param: `paneType=tab|split|window`)
*   **Read:** `obsidian daily:read`
*   **Modify:**
    *   `obsidian daily:append content=<text>`
    *   `obsidian daily:prepend content=<text>`
    *   Flags: `inline` (no newline), `open` (view after adding).
*   **Path:** `obsidian daily:path`

## Task Management
*   **List Tasks:** `obsidian tasks`
    *   Filters: `file=<name>`, `path=<path>`, `status="<char>"`
    *   Flags: `done` (completed), `todo` (incomplete), `daily` (from daily note), `active` (active file).
    *   Output: `verbose` (includes line numbers), `total` (count only).
*   **Update/Show Task:** `obsidian task`
    *   Targeting: `ref="<path>:<line>"` OR `file=<name> line=<n>`
    *   Actions:
        *   `status="<char>"` (Set specific status)
        *   `toggle` (Flip status)
        *   `done` / `todo` (Mark specific state)

## Unique Notes (Zettelkasten)
*   **Create:** `obsidian unique`
    *   Params: `name=<text>`, `content=<text>`
    *   Flags: `open`
