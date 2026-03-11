---
title: Obsidian CLI - Files & Content
description: Commands for creating, reading, editing, and organizing files, including properties (YAML) and templates.
---

# Files & Content Operations

## Basic File Operations
*   **List:** `obsidian files` (Flags: `folder=<path>`, `ext=<ext>`, `total`)
*   **Folders:** `obsidian folders` (Flags: `folder=<parent>`, `total`)
*   **Info:** `obsidian file` or `obsidian folder path=<path>`
*   **Open:** `obsidian open file=<name>` (Flag: `newtab`)
*   **Create:** `obsidian create`
    *   Params: `name=<name>`, `path=<path>`, `content=<text>`, `template=<name>`
    *   Flags: `overwrite`, `open`, `newtab`
*   **Read:** `obsidian read file=<name>`
*   **Edit Content:**
    *   `obsidian append content=<text>` (Flag: `inline`)
    *   `obsidian prepend content=<text>` (Flag: `inline`)
*   **Organize:**
    *   `obsidian move file=<name> to=<path>`
    *   `obsidian rename file=<name> name=<new_name>`
    *   `obsidian delete file=<name>` (Flag: `permanent`)

## Properties (YAML Frontmatter)
*   **List:** `obsidian properties file=<name>`
*   **Read Value:** `obsidian property:read name=<prop_name> file=<name>`
*   **Set Value:** `obsidian property:set name=<prop> value=<val> file=<name>`
    *   Type: `type=text|list|number|checkbox|date|datetime`
*   **Remove:** `obsidian property:remove name=<prop> file=<name>`
*   **Aliases:** `obsidian aliases` (Flags: `file=<name>`, `total`)

## Templates & Bookmarks
*   **Insert Template:** `obsidian template:insert name=<template>`
*   **Read Template:** `obsidian template:read name=<template>` (Flag: `resolve`)
*   **List Templates:** `obsidian templates total`
*   **Bookmarks:** `obsidian bookmarks` (Flags: `total`, `verbose`)
*   **Add Bookmark:** `obsidian bookmark file=<path> title=<title>`

## Other
*   **Word Count:** `obsidian wordcount file=<name>` (Flags: `words`, `characters`)
*   **History/Diff:** `obsidian diff file=<name> from=<ver> to=<ver>`
