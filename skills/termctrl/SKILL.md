---
name: termctrl
description: Control, inspect, test, and capture real terminal applications for agents and TUI review. Use when the user needs to launch terminal apps, interact with TUI programs, capture terminal screenshots, record terminal sessions, send input to running terminals, or automate terminal-based workflows. Triggers include "run a terminal app", "capture terminal output", "screenshot a TUI", "send input to terminal", "record terminal session", "interact with TUI", or any task requiring programmatic terminal interaction.
---

# Terminal Control with termctrl

Control, inspect, test, and capture real terminal applications using `termctrl`.

## Core Concepts

- **One-off operations**: `termctrl show` and `termctrl save` launch a process, capture, then terminate it.
- **Named sessions**: `termctrl start` keeps a persistent session for multiple interactions.
- **OpenTUI apps**: Programs using OpenTUI (like OpenCode) require `--host opentui` flag.

## Quick Start

```bash
# One-off: run and capture visible screen
termctrl show -- my-terminal-app

# Save as PNG
termctrl save --format png --out captures/app.png -- my-terminal-app

# Named session workflow
termctrl start demo --host opentui --cols 112 --rows 34 -- opencode
termctrl wait demo "/connect" --timeout 5000
termctrl show demo
termctrl send demo text:/connect enter
termctrl show demo
termctrl save demo --format png --out captures/result.png
termctrl stop demo
```

## Essential Commands

### One-Off Capture

```bash
termctrl show -- <command>                    # Print visible screen text
termctrl show --format json -- <command>      # JSON frame output
termctrl show --format svg -- <command>       # SVG render
termctrl save --format png --out file.png -- <command>  # Save PNG
termctrl save --format png --format txt --out base -- <command>  # Multiple formats (writes base.png, base.txt)
```

Options: `--cols N`, `--rows N`, `--wait-for "text"`, `-s <input>` (send before read).

### Named Sessions

```bash
termctrl start <name> [options] -- <command>  # Start persistent session
termctrl status <name>                        # Check state (running/exited)
termctrl show <name>                          # Read visible screen
termctrl save <name> --format png --out f.png # Save artifacts
termctrl send <name> <input>...               # Send input
termctrl wait <name> "text" --timeout N       # Wait for text to appear
termctrl resize <name> --cols N --rows N      # Resize viewport
termctrl logs <name>                          # Print terminal output/logs
termctrl restart <name>                       # Restart with same settings
termctrl stop <name>                          # Terminate session
termctrl list                                 # List all sessions
```

### Input Syntax for `send`

```bash
termctrl send demo text:hello         # Type "hello"
termctrl send demo enter              # Press Enter
termctrl send demo escape             # Press Escape
termctrl send demo tab                # Press Tab
termctrl send demo ctrl-c             # Ctrl+C
termctrl send demo ctrl-z             # Ctrl+Z
termctrl send demo arrow-up           # Arrow keys
termctrl send demo arrow-down
termctrl send demo backspace
termctrl send demo delete
termctrl send demo home end page-up page-down
termctrl send demo shift-tab

# Combine multiple inputs in order
termctrl send demo text:/connect enter
termctrl send demo ctrl-p text:model enter

# Pipe exact bytes
printf '%s' 'Summarize the active view.' | termctrl send demo --stdin
```

### OpenTUI Applications

Apps like OpenCode need the host handshake:

```bash
termctrl start demo --host opentui --cols 112 --rows 34 -- opencode
termctrl show --host opentui --cols 112 --rows 34 --wait-for "/connect" -- opencode
```

### Recording and Video Export

```bash
# Record a session
termctrl start demo --record captures/demo.termctrl --host opentui --cols 112 --rows 34 -- opencode
termctrl wait demo "Ask anything"
termctrl mark demo before-prompt
termctrl send demo --pace-ms 35 'text:Write a short haiku.' enter
termctrl wait demo "DONE" --timeout 60000
termctrl mark demo after-answer
termctrl stop demo

# Inspect markers
termctrl markers captures/demo.termctrl

# View screen at marker
termctrl show --recording captures/demo.termctrl --at-marker after-answer

# Export video
termctrl video captures/demo.termctrl --out captures/demo.mp4

# With edit plan for polished demos
termctrl video captures/demo.termctrl --edit plan.json --tail-ms 0 --out demo.mp4
```

Edit plan JSON:
```json
{
  "clips": [
    {
      "from": "before-prompt",
      "to": "after-answer",
      "speed": 4,
      "caption": "The agent answers"
    }
  ]
}
```

### Logs and ANSI Streams

```bash
termctrl logs <name>                          # Read terminal output
termctrl logs <name> --ansi > output.ansi     # Raw ANSI stream

# Render ANSI from stdin
printf '\033[44;97m hello \033[0m\n' | termctrl show --input -
printf '\033[44;97m hello \033[0m\n' | termctrl save --input - --format png --out cap.png
```

### Pipe Mode (Non-Interactive Commands)

```bash
termctrl save --pipe --format png --format txt --cols 100 --rows 16 --out captures/log -- my-command
```

## Artifact Formats

| Format | Description |
|--------|-------------|
| `png`  | Screenshot image |
| `txt`  | Plain text of visible screen |
| `json` | Structured Frame object (version 1) |
| `svg`  | SVG render of terminal |
| `ansi` | Raw ANSI/VT byte stream (sensitive - opt-in only) |

## Sensitivity Warning

- ANSI streams and recordings can contain **secrets and prompts**.
- Only produce `--format ansi` when explicitly requested.
- Treat `.termctrl` recordings as sensitive artifacts.
- Environment variable values are redacted in metadata.

## Driver Mode (For External Tooling)

```bash
termctrl driver
```

Serves isolated sessions over JSON Lines stdin/stdout for programmatic control:

```json
{"type":"hello","protocolVersion":1,"terminalControlVersion":"<version>"}
{"id":1,"method":"launch","sessionId":"app","params":{"command":["my-app"],"cols":100,"rows":30}}
{"id":2,"method":"waitForText","sessionId":"app","params":{"text":"Ready","timeoutMs":5000}}
{"id":3,"method":"send","sessionId":"app","params":{"input":[{"type":"text","value":"help"},{"type":"key","value":"enter"}]}}
{"id":4,"method":"capture","sessionId":"app","params":{"settleMs":250,"deadlineMs":5000}}
```

## npm Package

```bash
bun add -d @kitlangton/terminal-control vitest
```

```typescript
import { TerminalControl } from "@kitlangton/terminal-control"

await using terminal = await TerminalControl.make({ artifacts: { directory: ".termctrl-artifacts" } })
await using session = await terminal.launch({
  command: ["/path/to/app"],
  viewport: { cols: 100, rows: 30 },
})
await session.screen.waitForText(/Ready/)
await session.keyboard.type("help")
await session.keyboard.press("Enter")
const text = await session.screen.text()
```
