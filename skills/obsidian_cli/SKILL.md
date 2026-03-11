---
title: Obsidian CLI (Root)
description: Main entry point for the Obsidian CLI. Handles syntax rules and routes to sub-skills for specific domains (Files, Search, Tasks, System, Developer).
version: 1.0.0
requirements: Obsidian App running, Obsidian 1.12+ installer
---

# Obsidian CLI

Control the running Obsidian application from the terminal.

## Global Syntax
*   **Command:** `obsidian <command> [params] [flags]`
*   **Targeting Vaults:** `vault=<name>` must be the **first** parameter if switching vaults.
*   **Targeting Files:**
    *   `file=<name>`: Fuzzy match (WikiLink style).
    *   `path=<path>`: Exact path from root.
*   **Quoting:** `content="Text with spaces"`.
*   **Copying:** Add `--copy` to any command to copy output to clipboard.

## Sub-Skill Routing

| Requirement | Sub-Skill |
| :--- | :--- |
| **Manage Content:** Create, read, edit, move, delete, properties/YAML, templates, bookmarks. | `skills/files.md` |
| **Find Info:** Search text, find tags, view backlinks/outlinks, outline, random notes. | `skills/search.md` |
| **Planning:** Manage tasks, checkboxes, daily notes, unique notes (Zettelkasten). | `skills/tasks.md` |
| **Configuration:** Plugins, themes, workspaces, Sync, Publish, vaults, hotkeys. | `skills/system.md` |
| **Coding/Debug:** Execute JavaScript (`eval`), take screenshots, inspect DOM/CSS, database bases. | `skills/developer.md` |

## Quick Reference (Top Commands)
*   **Open Daily Note:** `obsidian daily`
*   **Quick Search:** `obsidian search query="<text>"`
*   **Read Active File:** `obsidian read`
*   **Eval JS:** `obsidian eval code="<js>"`
*   **Reload App:** `obsidian reload`
