/**
 * Session Edits Browser Plugin.
 * Tracks AI modifications and allows jumping to them in a remote Neovim instance.
 */
import { Plugin, tool } from '@opencode-ai/plugin';
import { readFileSync, writeFileSync, existsSync } from 'fs';

interface EditRecord {
  filePath: string;
  lineNumber: number;
  timeLabel: string;
  summary: string;
}

function getFileName(fullPath: string): string {
  return fullPath.split(/[\\/]/).pop() || fullPath;
}

function getHistoryFile(dir: string, sessionTag: string): string {
  const basename = dir.split('/').pop() || 'default';
  return `/tmp/opencode-edits-${basename}-${sessionTag}.json`;
}

function loadHistory(dir: string, sessionTag: string): EditRecord[] {
  const file = getHistoryFile(dir, sessionTag);
  if (existsSync(file)) {
    try {
      return JSON.parse(readFileSync(file, 'utf-8'));
    } catch {
      return [];
    }
  }
  return [];
}

function saveHistory(dir: string, sessionTag: string, history: EditRecord[]): void {
  const file = getHistoryFile(dir, sessionTag);
  writeFileSync(file, JSON.stringify(history, null, 2));
}

export const EditBrowserPlugin: Plugin = async (ctx) => {
  const rootDir = ctx.directory;
  
  // Get tmux session name for session-specific history
  const sessionResult = await ctx.$`tmux display-message -p '#S' 2>/dev/null || echo "default"`;
  const sessionTag = sessionResult.stdout.trim().replace(/[^a-zA-Z0-9]/g, '_');
  
  let history: EditRecord[] = loadHistory(rootDir, sessionTag);

  const neovimRemoteCommand = "nvr";
  
  const folderName = getFileName(rootDir);
  const sessionIdentity = `opencode-${folderName}-${sessionTag}`;
  const socketAddress = `/tmp/nvim-${sessionIdentity}.pipe`;

  const triggerEditor = async (targetFile: string, line: number) => {
    const checkSession = await ctx.$`tmux has-session -t ${sessionIdentity}`;
    const exists = checkSession.exitCode === 0;

    if (!exists) {
      const nvimStart = `nvim --listen ${socketAddress} +${line} ${targetFile}`;
      const tmuxStart = `tmux new-session -s ${sessionIdentity} "${nvimStart}"`;
      await ctx.$`kitty --detach sh -c "${tmuxStart}"`;
    } else {
      await ctx.$`${neovimRemoteCommand} --servername ${socketAddress} --remote +${line} ${targetFile}`;
    }
  };

  const formatList = (): string => {
    if (history.length === 0) {
      return "No edits have been recorded in this session.";
    }
    return history
      .map((item, i) => {
        const name = getFileName(item.filePath);
        return `${i + 1}. [${item.timeLabel}] ${name} (Line ${item.lineNumber})\n   └─ ${item.summary}`;
      })
      .join('\n');
  };

  return {
    'tool.execute.after': async ({ tool: toolName, args: toolArguments }) => {
      const editTools = ['write_file', 'edit_file', 'patch_file', 'insert_code'];
      
      if (editTools.includes(toolName)) {
        const file = toolArguments.path || toolArguments.filename || toolArguments.filepath;
        const line = toolArguments.line || toolArguments.start_line || 1;
        
        if (file) {
          const absolutePath = file.startsWith('/') ? file : `${rootDir}/${file}`;
          const time = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
          
          history.unshift({
            filePath: absolutePath,
            lineNumber: line,
            timeLabel: time,
            summary: toolArguments.explanation || `Modified ${getFileName(file)}`
          });
          saveHistory(rootDir, sessionTag, history);
        }
      }
    },

    'command.execute.before': async (input, output) => {
      if (input.command === '/edits' || input.command.startsWith('/edits')) {
        const idStr = input.command.split(' ').slice(1).join(' ').trim();
        let text: string;

        if (idStr) {
          const index = parseInt(idStr, 10) - 1;
          const record = history[index];
          if (record) {
            await triggerEditor(record.filePath, record.lineNumber);
            text = `Opened ${getFileName(record.filePath)} at line ${record.lineNumber}`;
          } else {
            text = "Edit ID not found.";
          }
        } else {
          text = `**Edit History Browser**\n${formatList()}`;
        }

        (output as any).parts = [{ type: 'text', text }];
      }
    },

    tool: {
      edits: tool({
        description: 'Browse and jump to session edits. Usage: edits [id]. Without an id, lists all edits. With an id, opens that file in Neovim.',
        args: {
          id: tool.schema.string().describe('Edit ID number from the list').optional(),
        },
        async execute(args) {
          if (history.length === 0) {
            return "No edits have been recorded in this session.";
          }

          if (args.id !== undefined) {
            const index = parseInt(args.id, 10) - 1;
            const record = history[index];
            if (record) {
              await triggerEditor(record.filePath, record.lineNumber);
              return `Opened ${getFileName(record.filePath)} at line ${record.lineNumber}`;
            }
            return "Edit ID not found.";
          }

          const listOutput = history
            .map((item, i) => {
              const name = getFileName(item.filePath);
              return `${i + 1}. [${item.timeLabel}] ${name} (Line ${item.lineNumber})\n   └─ ${item.summary}`;
            })
            .join('\n');

          return `**Edit History Browser**\n${listOutput}\n\nCall edits with an ID number to jump to that edit in Neovim.`;
        },
      }),
    },
  };
};
