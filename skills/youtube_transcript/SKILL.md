---
name: youtube_transcript
description: Fetches YouTube video transcripts, writes organized markdown summaries, and converts to EPUB
---

# YouTube Transcript to EPUB Skill

You fetch YouTube video transcripts using the `transcript` script, write a well-organized markdown file, and convert it to EPUB.

## When to Use

- User provides a YouTube URL and wants a transcript
- User wants a video's content organized into a readable markdown or EPUB document
- User mentions `transcript` command with a YouTube URL
- User wants to save video content for offline reading

## Prerequisites

- `transcript` script at `~/.local/bin/transcript` (installed via `pip install youtube-transcript-api`)
- `pandoc` for EPUB conversion (install via `apt install pandoc` or `brew install pandoc`)

## Workflow

### Step 1: Fetch Transcript

Run the transcript script with the provided YouTube URL:

```bash
transcript "https://www.youtube.com/watch?v=VIDEO_ID"
```

The output is timestamped lines:
```
[0.08s] First line of transcript
[2.72s] Second line of transcript
...
```

### Step 2: Write Organized Markdown

Based on the transcript content, write a well-organized markdown file. Structure it to remove duplication and group related ideas:

- **Title**: Use the video title from context (or a descriptive title if unknown)
- **Sections**: Group related content into logical sections with headings
- **Key points**: Extract and summarize important concepts
- **Clean prose**: Remove filler words, repetition, and verbal stumbles
- **Timestamps**: Optionally include timestamps for key transitions

Save the file to the current directory with a descriptive filename derived from the video title.

### Step 3: Convert to EPUB

Convert the markdown file to EPUB using pandoc:

```bash
pandoc -o "output.epub" "input.md" --metadata title="Video Title"
```

Metadata options:
- `--metadata title="..."` - Set the book title
- `--metadata author="..."` - Set the author (default: YouTube channel name if known)
- `--metadata date="..."` - Set publication date

### Step 4: Clean Up (Optional)

Remove the intermediate markdown file if the user only wants the EPUB.

## Important Notes

- The `transcript` script reads from `youtube-transcript-api` and may fail on age-restricted, private, or deleted videos
- For long videos, the transcript can be very large — organize into manageable sections
- Do not include the raw timestamped transcript verbatim; reorganize into readable prose
- Remove duplicate information and conversational filler
- The markdown file is intermediate; the EPUB is the final deliverable unless the user asks otherwise

## Examples

**User request:** "get the transcript of https://www.youtube.com/watch?v=PtbZY9HCatE and make an epub"

1. Fetch transcript:
   ```bash
   transcript "https://www.youtube.com/watch?v=PtbZY9HCatE" > /tmp/transcript_raw.txt
   ```

2. Read the transcript content, analyze structure, write organized markdown to current directory (e.g., `the-business-of-ai.md`)

3. Convert to EPUB:
   ```bash
   pandoc -o "the-business-of-ai.epub" "the-business-of-ai.md" --metadata title="The Business of AI"
   ```

4. Verify the EPUB exists in the current directory
