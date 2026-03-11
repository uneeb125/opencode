---
title: Obsidian CLI - Developer
description: Advanced tools for executing code, debugging, inspecting the DOM, and database operations.
---

# Developer Tools

## JavaScript Execution
*   **Eval:** `obsidian eval code="<javascript>"`
    *   *Example:* `obsidian eval code="app.vault.getFiles().length"`
*   **Console:** `obsidian dev:console` (Flags: `limit=<n>`, `level=error|log`, `clear`)
*   **Errors:** `obsidian dev:errors`

## Debugging & Inspection
*   **DevTools:** `obsidian devtools` (Toggle window)
*   **Screenshot:** `obsidian dev:screenshot path=<filename.png>`
*   **Mobile Mode:** `obsidian dev:mobile` (`on`/`off`)
*   **DOM Inspection:** `obsidian dev:dom selector="<css>"`
    *   Flags: `text`, `inner`, `all`, `attr=<name>`
*   **CSS Inspection:** `obsidian dev:css selector="<css>"`
*   **Chrome Protocol:** `obsidian dev:cdp method=<method> params=<json>`

## Bases (Database/Tables)
*   **List:** `obsidian bases`
*   **Views:** `obsidian base:views`
*   **Query:** `obsidian base:query file=<base_file> view=<view_name>`
    *   Format: `format=json|csv|md`
*   **Create Row:** `obsidian base:create file=<base_file> content=<text>`
