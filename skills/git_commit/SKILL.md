---
name: git_commit
description: Commits current changes with a structured message describing intent and code changes
---

# Git Commit Skill

You help users commit their current git changes with a well-structured commit message that describes the intent and provides a bullet-point summary of actual code changes.

## When to Use

- User explicitly asks to commit changes
- User wants to stage and commit current work
- User requests creating a git commit with a descriptive message

## Workflow

### Step 1: Check Git Status

Run `git status` to see:
- Modified files
- Untracked files
- Staged changes

### Step 2: Analyze Changes

Run `git diff` for unstaged changes and `git diff --staged` for staged changes to understand what was modified. Also run `git log -5 --oneline` to understand the repository's commit message style.

### Step 3: Draft Commit Message

Create a commit message with two parts:

**Part 1: Intent (1-2 sentences)**
- Describes WHY the changes were made
- Focuses on the purpose/goal of the changes
- Example: "Fix authentication bug causing login failures on mobile devices" or "Add user profile image upload functionality"

**Part 2: Code Changes (bullet points)**
- Short, specific bullet points of WHAT changed
- Focus on actual code modifications
- Example:
  ```
  
  - Update auth service to handle mobile token refresh
  - Fix null pointer exception in user session manager
  ```

### Step 4: Stage and Commit

Add relevant files to staging area and create the commit:

```bash
git add <relevant_files>
git commit -m "<intent_message>

<bullet_point_1>
<bullet_point_2>"
```

The commit message should be formatted as:
```
<intent line>

<blank line>
<bullet point 1>
<bullet point 2>
```

## Examples

**Example 1: Bug Fix**

Git status shows: `src/auth/login.ts` modified

Git diff shows: Added retry logic for failed token refresh

Commit message:
```
Fix authentication failures on network errors

- Add retry logic for token refresh in login service
- Improve error handling for network timeouts
```

**Example 2: New Feature**

Git status shows: `src/components/UserProfile.tsx` new file, `src/api/user.ts` modified

Git diff shows: Added user profile component and API endpoints

Commit message:
```
Add user profile image upload functionality

- Create UserProfile component with image upload UI
- Add user avatar endpoint to user API
- Implement image compression before upload
```

**Example 3: Refactoring**

Git status shows: `src/utils/helpers.ts` modified, `src/utils/format.ts` modified

Git diff shows: Extracted common formatting logic into separate utility module

Commit message:
```
Refactor formatting utilities for better code organization

- Extract date formatting functions to format.ts
- Consolidate currency formatting in helpers.ts
- Update imports across affected modules
```

## Important Notes

- Always analyze the actual changes before drafting the message
- Match the existing commit message style in the repository
- Keep bullet points concise and specific
- Never commit files containing secrets (.env, credentials.json, etc.)
- Only use this skill when explicitly asked to commit changes
