# Obsidian Kanban Skill

## Overview

This skill provides instructions for reading, editing, deleting, and adding tasks/subtasks in Obsidian kanban markdown files.

## File Format

Obsidian kanban files use markdown with checkbox syntax:
- Columns are defined as `## ColumnName`
- Tasks: `- [ ] Task Name`
- Subtasks (indented with tab or 2+ spaces): `  - [ ] Subtask Name`
- Completed tasks: `- [x] Task Name`

Example structure:
```markdown
## Backlog

- [ ] Task 1
    - [ ] Subtask A
    - [ ] Subtask B
- [ ] Task 2

## Todo

- [ ] Task 3
```

## Operations

### Reading Tasks

1. Read the file using the Read tool
2. Parse tasks by column:
   - Find `## ColumnName` headers
   - Extract `- [ ]` (incomplete) and `- [x]` (complete) items
   - Note indentation for subtasks

### Adding a Task

To add a task to a column, use the Edit tool with the pattern:
```
oldString: ## ColumnName


newString: ## ColumnName

- [ ] New Task Name
```

### Adding a Subtask

To add a subtask under an existing task:
```
oldString: - [ ] Parent Task
	 - [ ] existing subtask

newString: - [ ] Parent Task
	 - [ ] existing subtask
	 - [ ] New subtask
```

Note: Use tab character for indentation (shown as → in edits).

### Completing a Task/Subtask

Change checkbox state:
```
oldString: - [ ] Task Name
newString: - [x] Task Name
```

### Editing a Task/Subtask

Replace the task text:
```
oldString: - [ ] Old Task Name
newString: - [ ] New Task Name
```

### Deleting a Task (and its subtasks)

Remove the task line and its subtasks:
```
oldString: - [ ] Task to Delete
	 - [ ] Its subtask
	 - [ ] Another subtask

newString: (empty line)
```

### Deleting a Subtask

Remove only the subtask line:
```
oldString: - [ ] Parent Task
	 - [ ] Subtask to Delete

newString: - [ ] Parent Task
```

## Tips

- Always read the file first to understand exact formatting
- Use consistent indentation (tab or spaces)
- Preserve the kanban metadata block at the end of the file
- Test changes by reading the file after editing

### Moving a Task

When moving a task between columns:
1. Read the file to see current structure and verify column headers exist
2. Remove the task from the source location
3. Add it to the destination column that already has the `## ColumnName` header

Example - moving from Backlog to Todo (Todo already exists):
```
oldString: - [ ] Task Name


## Todo

newString: - [ ] Task Name

## Todo
- [ ] Task Name
```

The key is to ensure you're adding UNDER an existing column header, not creating a new one.