#!/bin/bash
# Edit History Browser CLI
# Usage: edits-cli [id]
#   without id: lists all edits
#   with id: opens that edit in neovim

# Get current directory basename AND tmux session for session-specific history
DIRNAME=$(basename "$PWD")
SESSION_TAG=$(tmux display-message -p '#S' 2>/dev/null | tr '[:upper:]' '[:lower:]' | sed 's/[^a-z0-9]/_/g' || echo "default")
HISTORY_FILE="/tmp/opencode-edits-${DIRNAME}-${SESSION_TAG}.json"

if [ ! -f "$HISTORY_FILE" ]; then
    echo "No edit history found for this session."
    exit 1
fi

if [ $# -eq 0 ]; then
    echo "**Edit History Browser** (session: $SESSION_TAG)"
    echo ""
    # Check if jq is available
    if command -v jq &> /dev/null; then
        jq -r '.[] | "\(.[0]+1). [\(."timeLabel")] \(."filePath" | split("/") | .[-1]) (Line \(."lineNumber")\n   └─ \(."summary")")' "$HISTORY_FILE" 2>/dev/null
    else
        cat "$HISTORY_FILE"
    fi
    echo ""
    echo "Usage: edits-cli <number> to jump to an edit"
else
    IDX=$(( $1 - 1 ))
    
    # Check if jq is available
    if command -v jq &> /dev/null; then
        RECORD=$(jq ".[$IDX]" "$HISTORY_FILE" 2>/dev/null)
        if [ -z "$RECORD" ] || [ "$RECORD" = "null" ]; then
            echo "Edit ID $1 not found"
            exit 1
        fi
        
        FILE=$(echo "$RECORD" | jq -r '.filePath')
        LINE=$(echo "$RECORD" | jq -r '.lineNumber')
    else
        echo "jq is required but not installed"
        exit 1
    fi
    
    # Check if nvr (neovim-remote) is available
    if command -v nvr &> /dev/null; then
        SOCKET="/tmp/nvim-opencode-${DIRNAME}-${SESSION_TAG}.pipe"
        nvr --servername "$SOCKET" --remote +$LINE "$FILE" 2>/dev/null && echo "Opened $FILE at line $LINE" || echo "Failed to open file"
    else
        echo "nvr not found. Install neovim-remote: pip install neovim-remote"
        echo "Or open manually: $FILE:$LINE"
        exit 1
    fi
fi
