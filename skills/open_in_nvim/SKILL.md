---
name: open_in_nvim
description: Opens files in Neovim using Kitty terminal in a new OS window and navigates to specific line and column
---

# Open in Neovim Skill

You help users open files in Neovim using Kitty terminal in a new OS window and navigate to specific line and column positions.

## When to Use

- User asks to open a file in nvim
- User wants to jump to a specific line or column in a file
- User provides a file path with line/column coordinates

## Workflow

### Step 1: Extract Parameters

Identify the following from the user's request:
- **FILENAME**: The file path to open (will be converted to absolute path)
- **LINE**: The line number to jump to (default: 1 if not specified)
- **COLUMN**: The column number to jump to (default: 1 if not specified)

Examples:
- "open main.rs at line 99" → FILENAME=main.rs, LINE=99, COLUMN=1
- "nvim main.rs line 99 column 50" → FILENAME=main.rs, LINE=99, COLUMN=50
- "open /path/to/file.py" → FILENAME=/path/to/file.py, LINE=1, COLUMN=1

### Step 2: Construct the Kitty Command

Use the following command format:

```bash
kitty @ launch --type os-window nvim "+normal! <LINE>G<COLUMN>|" <ABSOLUTE_PATH>
```

Where:
- `<LINE>` is the line number (1-indexed)
- `<COLUMN>` is the column number (1-indexed)
- `<ABSOLUTE_PATH>` is the full absolute path to the file (from Step 2)

The command uses:
- `kitty @ launch --type os-window` to open a new OS window (not a kitty pane)
- `nvim` as the command to run in the new window
- `+normal! <LINE>G<COLUMN>|` to navigate to the line and column
  - `G` jumps to the specified line
  - `|` moves to the specified column

### Step 3: Execute the Command

Run the command using the bash tool.

## Examples

**Example 1: Line only**

User request: "open main.rs at line 99"

Command:
```bash
kitty @ launch --type os-window nvim "+normal! 99G1|" /home/uneeb/.config/opencode/main.rs
```

**Example 2: Line and column**

User request: "nvim main.rs line 99 column 50"

Command:
```bash
kitty @ launch --type os-window nvim "+normal! 99G50|" /home/uneeb/.config/opencode/main.rs
```

**Example 3: Full path with line and column**

User request: "open /home/user/project/src/lib.rs at line 250 column 15"

Command (already absolute):
```bash
kitty @ launch --type os-window nvim "+normal! 250G15|" /home/user/project/src/lib.rs
```

**Example 4: Just open file (no line/column)**

User request: "open README.md"

Command:
```bash
kitty @ launch --type os-window nvim "+normal! 1G1|" /home/uneeb/.config/opencode/README.md
```

## Notes

- The `kitty @ launch --type os-window` command opens a new OS window (not a kitty pane)
- This requires Kitty to be running and have the remote control feature enabled
- Line and column numbers are 1-indexed
- If only line is specified, column defaults to 1
- If neither line nor column is specified, both default to 1
