---
name: vision_pdf
description: Reads and analyzes PDF files by extracting pages as images and using the visor subagent for vision analysis
---

# Vision PDF Reader Skill

You help users read and analyze PDF files by converting pages to images and using the `visor` subagent for vision-based analysis.

## When to Use

- User asks to read or analyze a PDF with vision capabilities
- User wants to extract text or information from scanned PDFs
- User needs to understand visual content in PDF documents (charts, diagrams, layouts)
- User mentions "vision" or "see" in relation to PDF analysis
- Traditional text extraction (pdftotext) is insufficient for the PDF content

## Workflow

### Step 1: Verify PDF File

Check that the provided PDF file exists and is readable:
```bash
ls -lh <filename.pdf>
```

### Step 2: Determine Output Directory

**Default**: Use `/tmp` as the output directory for extracted JPEG files.

**Exception**: Only use the current directory or a custom location if the user explicitly specifies it.

```bash
# Default - use /tmp
output_dir="/tmp/pdf_vision_$(date +%Y%m%d_%H%M%S)"

# OR - user specified location (only if explicitly requested)
# output_dir="<user_specified_directory>"
```

Create the output directory:
```bash
mkdir -p "$output_dir"
```

### Step 3: Extract PDF Pages as Images

Execute the pdftoppm command to convert PDF pages to JPEG images:

```bash
pdftoppm -jpeg -jpegopt quality=100 -r 500 <filename.pdf> "$output_dir/filename"
```

**Command Options:**
- `-jpeg`: Output as JPEG format
- `-jpegopt quality=100`: Maximum JPEG quality (0-100 scale)
- `-r 500`: Resolution at 500 DPI for high-quality images
- `-f <first_page>`: First page to extract (optional, default: 1)
- `-l <last_page>`: Last page to extract (optional, default: last page)
- `<filename.pdf>`: Path to the input PDF file
- `<output_directory>/filename`: Output directory and base filename

### Step 4: Verify Extracted Images

Check that the JPEG files were created successfully:
```bash
ls -lh "$output_dir"/
```

The output files will be named with a page number suffix:
- `filename-1.jpg`, `filename-2.jpg`, `filename-3.jpg`, etc.

### Step 5: Analyze with Visor Subagent

Use the `task` tool to invoke the `visor` subagent for vision analysis. The visor subagent is configured to use GLM-4.6v with multimodal capabilities.

**For single page analysis:**
```typescript
task(
  subagent_type="visor",
  load_skills=[],
  description="Analyze PDF page",
  prompt="Analyze the image at <image_path>. <user_question_or_task>",
  run_in_background=false
)
```

**For multiple page analysis (batch):**
Extract all image paths and pass them to visor with context about page order:
```typescript
task(
  subagent_type="visor",
  load_skills=[],
  description="Analyze multi-page PDF",
  prompt="Analyze these PDF pages in order. Page 1: <image_path1>, Page 2: <image_path2>, etc. <user_question_or_task>",
  run_in_background=false
)
```

**For specific page ranges:**
If user specified a page range, only extract those pages and analyze accordingly:
```bash
pdftoppm -jpeg -jpegopt quality=100 -r 500 -f 1 -l 3 report.pdf "$output_dir/report"
```
Then analyze only the extracted pages.

### Step 6: Present Findings

Synthesize the visor subagent's analysis and present findings to the user in a clear, organized manner. Include:
- Summary of what was found
- Specific details from the images (text, charts, diagrams)
- Page references for multi-page documents
- Any relevant observations or insights

## Important Notes

- The visor subagent uses `zai-coding-plan/glm-4.6v` with multimodal vision capabilities
- Extracting all pages from a large PDF can be time-consuming; consider page ranges for large documents
- High DPI (500) produces better OCR accuracy for vision analysis
- Default output directory is `/tmp/pdf_vision_<timestamp>` to avoid cluttering the workspace
- The visor subagent is designed for vision analysis tasks only - it can see and understand images
- Always clean up temporary files after analysis if the user doesn't need them preserved
- For multi-page documents, consider whether to analyze all pages or focus on specific ones based on user needs

## Examples

**Example 1: Basic PDF vision analysis**

User request: "read this pdf with vision and tell me what's in it"

1. Check file: `ls -lh document.pdf`
2. Create output directory: `output_dir="/tmp/pdf_vision_$(date +%Y%m%d_%H%M%S)" && mkdir -p "$output_dir"`
3. Extract pages: `pdftoppm -jpeg -jpegopt quality=100 -r 500 document.pdf "$output_dir/document"`
4. Get image list: `ls "$output_dir"/document-*.jpg | sort -V`
5. Call visor subagent with all images and context
6. Present findings to user

**Example 2: Analyze specific page range**

User request: "look at pages 5-8 of the pdf and extract the charts"

1. Check file: `ls -lh report.pdf`
2. Create output directory: `output_dir="/tmp/pdf_vision_$(date +%Y%m%d_%H%M%S)" && mkdir -p "$output_dir"`
3. Extract specific pages: `pdftoppm -jpeg -jpegopt quality=100 -r 500 -f 5 -l 8 report.pdf "$output_dir/report"`
4. Call visor subagent: "Analyze these PDF pages and extract all charts, graphs, and diagrams. Provide descriptions of what each shows."
5. Present extracted chart information with page references

**Example 3: Extract specific information from scanned PDF**

User request: "read this scanned pdf and get me the contact information"

1. Check file: `ls -lh scan.pdf`
2. Extract pages: `pdftoppm -jpeg -jpegopt quality=100 -r 500 scan.pdf "$output_dir/scan"`
3. Call visor subagent: "Scan through these images and extract all contact information (names, emails, phone numbers, addresses). Organize by page number."
4. Present structured contact information

**Example 4: Understand diagrams and technical drawings**

User request: "analyze the architecture diagrams in this pdf"

1. Extract pages: `pdftoppm -jpeg -jpegopt quality=100 -r 500 architecture.pdf "$output_dir/architecture"`
2. Call visor subagent: "Analyze the diagrams and technical drawings in these images. Describe the architecture, components, and relationships shown. Identify any labels, arrows, or annotations."
3. Provide detailed analysis of each diagram with context

**Example 5: Extract tables and structured data**

User request: "extract all tables from the pdf using vision"

1. Extract pages: `pdftoppm -jpeg -jpegopt quality=100 -r 500 financial.pdf "$output_dir/financial"`
2. Call visor subagent: "Extract all tables from these images. For each table, provide: column headers, row data, and the page number where it appears. Format the data in a readable structure."
3. Present extracted tables in organized format

## Common Analysis Tasks

- **Text Extraction**: "Extract all text from these images"
- **Chart Analysis**: "Describe the charts and graphs in these images"
- **Diagram Understanding**: "Explain the diagrams and their components"
- **Table Extraction**: "Extract table data from these images"
- **Layout Analysis**: "Describe the layout and structure of these pages"
- **Content Summarization**: "Summarize the content of these pages"
- **Specific Information**: "Find and extract <specific information> from these images"

## Error Handling

- If pdftoppm is not installed, inform the user: "pdftoppm is required. Install with: apt-get install poppler-utils (Linux) or brew install poppler (macOS)"
- If PDF is corrupted or unreadable, report the error to the user
- If visor subagent fails to analyze images, check that the images were created correctly
- For large PDFs, warn the user about processing time and suggest page ranges
