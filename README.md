# OpenCode Configuration

This directory contains configuration files for the OpenCode AI coding assistant framework.

## Overview

OpenCode is an AI-powered coding assistant that uses multiple specialized agents for different tasks. This configuration directory manages agent definitions, model selections, LSP integration, and plugin settings.

## Structure

```
opencode/
├── oh-my-opencode.json      # Agent configurations and LSP settings
├── opencode.json             # Core OpenCode settings (models, modes, plugins)
├── package.json              # Plugin dependencies
├── agent/
│   └── nemotron.md          # Custom subagent definition
└── README.md                # This file
```

## Configuration Files

### `oh-my-opencode.json`

Main configuration file for the oh-my-opencode plugin. Contains:

- **Agent definitions**: Model assignments and permissions for each agent
- **LSP configuration**: Language Server Protocol settings for various languages
- **Agent permissions**: Fine-grained control over what agents can do (edit, bash commands)

#### Key Agents

| Agent | Purpose | Model | Permissions |
|-------|---------|-------|-------------|
| **Sisyphus** | Main orchestration | `zai-coding-plan/glm-4.7` | Full access |
| **librarian** | External research, documentation | `zai-coding-plan/glm-4.7` | Full access |
| **explore** | Codebase search & discovery | `zai-coding-plan/glm-4.7` | Read-only bash |
| **oracle** | Senior engineering advisor | `zai-coding-plan/glm-4.7` | Full access |
| **frontend-ui-ux-engineer** | Visual/styling changes | `zai-coding-plan/glm-4.7` | Full access |
| **document-writer** | Technical documentation | `zai-coding-plan/glm-4.7` | Full access |
| **multimodal-looker** | PDF/image analysis | `zai-coding-plan/glm-4.7` | Full access |
| **Prometheus (Planner)** | Task planning | `zai-coding-plan/glm-4.7` | Read-only bash |
| **Metis (Plan Consultant)** | Plan consultation | `zai-coding-plan/glm-4.7` | Read-only bash |

### `opencode.json`

Core OpenCode configuration containing:

- **Model selection**: Primary and small model settings
- **Provider configuration**: API endpoints and model mappings
- **Operating modes**: YOLO mode and question-only mode settings
- **Plugin list**: Enabled plugins for OpenCode

#### Current Models

| Model | Purpose |
|-------|---------|
| `zai-coding-plan/glm-4.7` | Primary model (high quality) |
| `zai-coding-plan/glm-4.5-flash` | Small model (fast, low-latency) |
| `nvidia/nemotron-3-nano-30b-a3b:free` | Free model (for specialized agents) |

#### Operating Modes

- **yolo_mode**: Disabled by default. When enabled, allows all actions without confirmation.
- **question_only**: Disabled by default. When enabled, restricts to read-only operations.

#### Plugins

1. **oh-my-opencode**: Main plugin providing agent orchestration
2. **@franlol/opencode-md-table-formatter@0.0.3**: Markdown table formatting

### `package.json`

Dependencies for OpenCode plugins:

```json
{
  "dependencies": {
    "@opencode-ai/plugin": "1.1.21"
  }
}
```

### `agent/nemotron.md`

Custom subagent definition for code analysis:

- **Model**: `nvidia/nemotron-3-nano-30b-a3b:free` (free tier)
- **Capabilities**: Code logic analysis, security checks, performance analysis
- **Restrictions**: Read-only (no write or edit permissions)

## LSP Configuration

Currently configured for Rust:

```json
"lsp": {
  "rust": {
    "command": ["/home/uneeb/.cargo/bin/lspmux"],
    "extensions": [".rs"]
  }
}
```

To add LSP for other languages, add entries following the same pattern in `oh-my-opencode.json` and `opencode.json`.

## Agent Permissions

Agents can have restricted permissions to ensure safe operation:

### `explore` Agent
- **Edit**: Denied
- **Bash**: Read-only commands only (ls, find, grep, cat, head, tail, wc, file, stat, tree, which, whereis, pwd, echo)

### `Prometheus` and `Metis` Agents
- **Edit**: Denied
- **Bash**: Same read-only restrictions as explore

## Workflow

### Making Changes

1. **Edit configuration files** (`oh-my-opencode.json`, `opencode.json`)
2. **Test changes** by running OpenCode
3. **Commit changes** with descriptive messages

Example:

```bash
git add oh-my-opencode.json opencode.json
git commit -m "Update agent models to zai-coding-plan/glm-4.7"
```

### Updating Models

To change the model for an agent:

1. Edit `oh-my-opencode.json`
2. Update the `model` field for the target agent
3. Commit the change

```json
"oracle": {
  "model": "your-new-model-here"
}
```

### Adding Custom Agents

1. Create a new agent definition file in `agent/` (e.g., `agent/myagent.md`)
2. Add agent configuration to `oh-my-opencode.json`
3. Test the agent functionality
4. Commit the changes

## Git Repository

This directory is version-controlled. Recent history:

- `cff1e96` Post update oh-my-opencode.json
- `acb50fc` Added oh-my-opencode and question-only mode
- `562bf76` Added Yolo mode
- `ff333fb` Initial

## Model Migration

**Recent Migration** (January 2026):
- Old: `opencode/glm-4.7-free`
- New: `zai-coding-plan/glm-4.7`

All agents migrated to the new paid model for improved performance and capabilities.

## Troubleshooting

### Agent Not Responding

Check the model assignment in `oh-my-opencode.json`:
```bash
grep -A 3 '"agent-name"' oh-my-opencode.json
```

### LSP Not Working

Verify the LSP binary exists:
```bash
ls -la /home/uneeb/.cargo/bin/lspmux
```

Check that file extensions are correctly mapped:
```bash
grep -A 5 '"lsp"' oh-my-opencode.json
```

### Permission Issues

Review agent permissions in `oh-my-opencode.json`:
```bash
grep -A 20 '"permission"' oh-my-opencode.json
```

## Resources

- [OpenCode Documentation](https://opencode.ai)
- [Oh-My-OpenCode Repository](https://github.com/code-yeongyu/oh-my-opencode)
- [GLM Models](https://zhipuai.cn/en/glm-4)

## Notes

- Configuration changes require restarting OpenCode to take effect
- Some changes (like model migrations) may affect cost or rate limits
- Always test configuration changes in a controlled environment first
- This configuration is designed for production use with disciplined agent permissions
