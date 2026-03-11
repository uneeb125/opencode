---
title: Obsidian CLI - System & Config
description: Manage vaults, workspaces, plugins, themes, sync, and publishing.
---

# System Configuration

## Vaults & Workspace
*   **Vault Info:** `obsidian vault`
*   **List Vaults:** `obsidian vaults`
*   **Switch Vault:** `obsidian vault:open name=<name>`
*   **Workspaces:** `obsidian workspaces` (List saved layouts)
*   **Manage Layouts:**
    *   `obsidian workspace:save name=<name>`
    *   `obsidian workspace:load name=<name>`
    *   `obsidian workspace:delete name=<name>`
*   **Tabs:** `obsidian tabs` (List open tabs)
*   **Open Tab:** `obsidian tab:open file=<path>`

## Plugins & Themes
*   **List Plugins:** `obsidian plugins` (Flag: `filter=core|community`)
*   **Plugin Actions:**
    *   `obsidian plugin id=<id>` (Get Info)
    *   `obsidian plugin:enable` / `disable` / `reload` `id=<id>`
    *   `obsidian plugin:install` / `uninstall` `id=<id>`
*   **Themes:** `obsidian themes` or `obsidian theme name=<name>`
*   **Manage Themes:**
    *   `obsidian theme:set name=<name>`
    *   `obsidian theme:install name=<name>`
*   **Snippets:** `obsidian snippets` (Manage CSS snippets via `snippet:enable/disable`)

## Services
*   **Sync:**
    *   `obsidian sync` (`on`/`off`)
    *   `obsidian sync:status`
    *   `obsidian sync:history file=<name>`
    *   `obsidian sync:restore version=<n> file=<name>`
*   **Publish:**
    *   `obsidian publish:status`
    *   `obsidian publish:add file=<name>`
    *   `obsidian publish:remove file=<name>`
    *   `obsidian publish:site`

## Other
*   **Web Viewer:** `obsidian web url=<url>`
*   **Hotkeys:** `obsidian hotkeys` or `obsidian hotkey id=<command_id>`
*   **Commands:** `obsidian commands` (List IDs) or `obsidian command id=<id>` (Run ID)
