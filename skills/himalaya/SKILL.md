---
name: himalaya
description: CLI email client for managing emails, folders, flags, attachments, and sending messages
---

# Himalaya Email Client Skill

You help users manage emails using Himalaya, a CLI email client for IMAP, Maildir, and other backends.

## When to Use

- User wants to list, read, search, or manage emails
- User needs to work with email folders/labels
- User wants to compose, reply to, or forward emails
- User needs to manage email flags (seen, flagged, answered, etc.)
- User wants to download attachments
- User needs to move/copy/delete emails

## Himalaya Basics

**Installation Check:**
```bash
which himalaya  # Should return /usr/bin/himalaya
himalaya --version  # Returns version info
```

**Global Options:**
- `-a, --account <NAME>` - Override default account
- `-f, --folder <NAME>` - Specify folder (default: INBOX)
- `-o, --output <FORMAT>` - Output format: `plain` (default) or `json`
- `-c, --config <PATH>` - Override config file path

**Important Notes:**
- All folder-related commands default to INBOX if not specified
- Use `-o json` for JSON output (must come BEFORE query arguments)
- Some commands may encounter database locks; add `sleep 2` before retrying
- **Always run `mbsync -a` before using himalaya to sync emails from remote servers**

## Account Management

### List Accounts

```bash
himalaya account list
```

**Output format:** Table with NAME, BACKENDS, DEFAULT columns

**JSON Example (verified working):**
```bash
himalaya account list -o json
# Returns: [{"name":"personal","backend":"Maildir, SMTP","default":true},...]
```

## Folder Management

### List Folders

```bash
himalaya folder list
```

**JSON Example (verified working):**
```bash
himalaya folder list -o json
# Returns: [{"name":"Archive","desc":"/home/uneeb/.mail/personal-gmail/Archive"},...]
```

### Create New Folder

```bash
himalaya folder add "NewFolder"
```

### Delete Folder

```bash
himalaya folder delete "FolderName"
```

### Purge Folder

```bash
himalaya folder purge "FolderName"
```

### Expunge Folder (permanently delete marked messages)

```bash
himalaya folder expunge "FolderName"
```

## Envelope Management

### List Envelopes (Emails)

Basic listing:
```bash
himalaya envelope list
```

**JSON Output (verified working):**
```bash
himalaya envelope list -o json
# Returns array of envelope objects with id, flags, subject, from, to, date, has_attachment
```

### Envelope Filtering and Searching

**Syntax:** `himalaya envelope list [OPTIONS] [QUERY]`

**Filter Operators:**
- `not <condition>` - Negate condition
- `<condition> and <condition>` - Match both
- `<condition> or <condition>` - Match either

**Filter Conditions:**
- `date <yyyy-mm-dd>` - Match exact date
- `before <yyyy-mm-dd>` - Before date
- `after <yyyy-mm-dd>` - After date
- `from <pattern>` - From sender matches pattern
- `to <pattern>` - To recipient matches pattern
- `subject <pattern>` - Subject matches pattern
- `body <pattern>` - Body text matches pattern
- `flag <flag>` - Match flag (seen, answered, flagged, deleted, draft)

**Sort Options:**
- `order by date [asc|desc]` - Sort by date
- `order by from [asc|desc]` - Sort by sender
- `order by to [asc|desc]` - Sort by recipient
- `order by subject [asc|desc]` - Sort by subject

### Working Examples (Verified)

**Search by sender (verified working):**
```bash
himalaya envelope list -o json "from Google"
# Returns emails from Google
```

**Search by subject keyword (verified working):**
```bash
himalaya envelope list -o json "subject package"
# Returns emails containing "package" in subject
```

**Sort by date descending (verified working):**
```bash
himalaya envelope list -o json "order by date desc"
# Returns emails sorted by newest first
```

**Advanced Multi-Condition Filtering Examples:**

Search for emails from Google after a specific date:
```bash
himalaya envelope list -o json "from Google and after 2026-03-19"
```

Search for unread emails with "security" in subject:
```bash
himalaya envelope list "not flag seen and subject Security"
```

Complex query: from specific sender, before date, with sorting:
```bash
himalaya envelope list "from Google and before 2026-03-20 order by date desc"
```

Combine multiple conditions with OR:
```bash
himalaya envelope list "subject package or subject delivery"
```

Negation example:
```bash
himalaya envelope list "not from Google and not from spam@example.com"
```

### Thread View

```bash
himalaya envelope thread
```

Show thread containing specific message:
```bash
himalaya envelope thread --id 25
```

Thread view with filter and sorting:
```bash
himalaya envelope thread "from Google order by date desc"
```

JSON output:
```bash
himalaya envelope thread -o json
```

### Pagination

```bash
himalaya envelope list --page 2 --page-size 20
```

### Folder-Specific Listing

```bash
himalaya envelope list --folder Archive
```

## Message Management

### Read Message

Basic read (marks as seen):
```bash
himalaya message read <ID>
```

Preview without marking as seen (verified working):
```bash
himalaya message read <ID> --preview
```

Read without headers:
```bash
himalaya message read <ID> --no-headers
```

Read from specific folder:
```bash
himalaya message read <ID> --folder Archive
```

Read with JSON output:
```bash
himalaya message read <ID> -o json
```

Read multiple messages:
```bash
himalaya message read 1 2 3
```

**Verified Example:**
```bash
himalaya message read 25 --preview
# Shows full message content without marking as seen
```

### Compose New Message

Basic compose (opens in $EDITOR):
```bash
himalaya message write
```

With pre-filled body:
```bash
himalaya message write "This is the body text"
```

With custom headers:
```bash
himalaya message write --header "To:recipient@example.com" --header "Subject:Hello"
```

### Reply to Message

```bash
himalaya message reply <ID>
```

Reply to all recipients:
```bash
himalaya message reply <ID> --all
```

Reply with pre-filled body:
```bash
himalaya message reply <ID> "Thanks for the email!"
```

Reply with custom headers:
```bash
himalaya message reply <ID> --header "Cc:other@example.com"
```

### Forward Message

```bash
himalaya message forward <ID>
```

Forward with custom headers:
```bash
himalaya message forward <ID> --header "To:newrecipient@example.com"
```

### Copy Message to Another Folder

```bash
himalaya message copy <TARGET_FOLDER> <ID>...
```

**Example:**
```bash
himalaya message copy Archive 1 2 3
himalaya message copy Archive 1 --folder INBOX --account personal
```

### Move Message to Another Folder

```bash
himalaya message move <TARGET_FOLDER> <ID>...
```

**Example:**
```bash
himalaya message move Trash 25
himalaya message move Archive 1 2 3 --folder INBOX
```

### Delete Message

Mark as deleted (moves to Trash or adds deleted flag):
```bash
himalaya message delete <ID>...
```

**Example:**
```bash
himalaya message delete 25
himalaya message delete 1 2 3 --folder INBOX
```

**Note:** This doesn't permanently delete; use `himalaya folder expunge Trash` for permanent deletion.

### Export Message

Export raw message format:
```bash
himalaya message export <ID>
```

### Edit Message in Place

Edit a draft or existing message, removing the original after saving:
```bash
himalaya message edit <ID> --on-place
```

### Mailto URL Support

Create a message from a mailto URL:
```bash
himalaya message mailto "mailto:recipient@example.com?subject=Hello&body=Message"
```

### Save Raw Message to Folder

Save a raw email message to a specific folder:
```bash
himalaya message save "From: sender@example.com\nTo: recipient@example.com\nSubject: Test\n\nBody text" --folder Drafts
```

### Send Raw Message

Send a raw email message directly:
```bash
himalaya message send "From: sender@example.com\nTo: recipient@example.com\nSubject: Test\n\nBody text"
```

### Read Message Thread

Read all messages in a thread:
```bash
himalaya message thread <ID>
```

### Message Read with Custom Headers

Show only specific headers:
```bash
himalaya message read <ID> --header From --header Date
```

## Flag Management

### Available Flags

Standard flags: `seen`, `answered`, `flagged`, `deleted`, `draft`
Custom flags may also be supported

### Add Flag to Message

```bash
himalaya flag add <ID> <FLAG>
```

**Verified Example:**
```bash
himalaya flag add 25 seen
# Successfully adds seen flag to message 25
```

Add multiple flags:
```bash
himalaya flag add 25 seen flagged
```

Add flag to multiple messages:
```bash
himalaya flag add 1 2 3 flagged
```

### Set Flag (Replace All Flags)

```bash
himalaya flag set <ID> <FLAG>
```

**Example:**
```bash
himalaya flag set 25 seen
```

### Remove Flag from Message

```bash
himalaya flag remove <ID> <FLAG>
```

**Example:**
```bash
himalaya flag remove 25 seen
```

Remove multiple flags:
```bash
himalaya flag remove 25 seen flagged
```

### Flag from Specific Folder

```bash
himalaya flag add <ID> <FLAG> --folder Archive
himalaya flag remove <ID> seen --folder INBOX
```

## Attachment Management

### Download All Attachments from Message

```bash
himalaya attachment download <ID>
```

Download to specific directory:
```bash
himalaya attachment download <ID> --downloads-dir /path/to/dir
```

Download attachments from multiple messages:
```bash
himalaya attachment download 1 2 3
```

Download from specific folder:
```bash
himalaya attachment download <ID> --folder Archive
```

## Template Management (MML - Message Markup Language)

Himalaya uses MML for message templates with support for attachments and encryption.

### Generate Write Template

```bash
himalaya template write
```

### Generate Reply Template

```bash
himalaya template reply <ID>
```

### Generate Forward Template

```bash
himalaya template forward <ID>
```

### Save Template to Folder

```bash
himalaya template save <FOLDER> <TEMPLATE_FILE>
```

### Send Template

```bash
himalaya template send <TEMPLATE_FILE>
```

## Output Formats

### Plain (Default)

- Tables for listings
- Formatted text for messages
- Human-readable output

### JSON

Structured data for programmatic access:
- Envelopes: `[{id, flags, subject, from, to, date, has_attachment},...]`
- Folders: `[{name, desc},...]`
- Accounts: `[{name, backend, default},...]`
- Messages: Full message as JSON string

**Important:** Always place `-o json` BEFORE query arguments:
```bash
# Correct:
himalaya envelope list -o json "from Google"

# Incorrect (will fail):
himalaya envelope list "from Google" -o json
```

## Common Workflows

### Check for New Emails

```bash
himalaya envelope list
himalaya envelope list -o json | jq '.[0:5]'  # First 5 emails as JSON
```

### Search for Specific Emails

```bash
# From specific sender
himalaya envelope list "from Google"

# With subject keyword
himalaya envelope list "subject urgent"

# From date range
himalaya envelope list "after 2026-03-01 and before 2026-03-31"

# Unread emails
himalaya envelope list "not flag seen"

# Emails with attachments
himalaya envelope list -o json | jq '.[] | select(.has_attachment == true)'
```

### Mark Messages as Read

```bash
# Single message
himalaya flag add 25 seen

# Multiple messages
himalaya flag add 1 2 3 seen

# All unread messages (needs manual ID extraction)
himalaya envelope list -o json "not flag seen" | jq -r '.[].id' | xargs himalaya flag add seen
```

### Archive Processed Emails

```bash
# Move specific emails
himalaya message move Archive 25

# Move emails from search results
himalaya envelope list -o json "from Google" | jq -r '.[].id' | xargs himalaya message move Archive
```

### Process Attachments

```bash
# Download attachments from specific message
himalaya attachment download 25

# Download attachments from messages with attachments
himalaya envelope list -o json | jq -r '.[] | select(.has_attachment == true) | .id' | xargs himalaya attachment download
```

### Multi-Account Operations

```bash
# List emails from specific account
himalaya envelope list --account work

# Copy email between accounts' folders
himalaya message copy Archive 25 --account personal --folder INBOX
```

## Troubleshooting

### Database Lock Error

If you encounter "Resource temporarily unavailable" database lock error:
```bash
sleep 2 && himalaya <command>
```

The lock usually resolves within a few seconds.

### No Output

If a command produces no output, try:
```bash
himalaya <command> --debug
himalaya <command> --trace
```

### Configuration Issues

Check account configuration:
```bash
himalaya account list
himalaya account doctor <ACCOUNT_NAME>
```

Diagnose and fix account issues:
```bash
himalaya account doctor personal --fix
```

## Notes

- Himalaya supports multiple backends: IMAP, Maildir, Notmuch, Sendmail
- Version tested: v1.2.0 with +smtp +pgp-gpg +notmuch +pgp-commands +maildir +sendmail +wizard +imap
- Default folder is INBOX for most operations
- Message IDs are unique per folder, not globally
- Use `--preview` flag when reading messages to avoid marking as seen
- Thread view groups related messages for better context
- JSON output is most reliable for parsing and automation
