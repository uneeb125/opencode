---
name: pdf_to_jpeg
description: Extracts pages from PDF files into high-quality JPEG images using pdftoppm
---

# PDF to JPEG Extraction Skill

You help users extract pages from PDF files into high-quality JPEG images using the `pdftoppm` utility.

## When to Use

- User asks to extract pages from a PDF as images
- User wants to convert a PDF document to JPEG format
- User needs to extract specific pages from a PDF
- User references pdftoppm or PDF page extraction

## Workflow

### Step 1: Verify PDF File

Check that the provided PDF file exists and is readable:
```bash
ls -lh <filename.pdf>
```

### Step 2: Determine Output Directory

**Default**: Use `/tmp` as the output directory for extracted JPEG files.

**Exception**: Only use the current directory or a custom location if the user explicitly specifies it (e.g., "extract to current folder" or "put in ~/output/").

```bash
# Default - use /tmp
output_dir="/tmp/pdf_extract_$(date +%Y%m%d_%H%M%S)"

# OR - user specified location (only if explicitly requested)
# output_dir="<user_specified_directory>"
```

Create the output directory:
```bash
mkdir -p "$output_dir"
```

### Step 3: Run PDF to JPEG Conversion

Execute the pdftoppm command with the specified options:

```bash
pdftoppm -jpeg -jpegopt quality=100 -r 500 <filename.pdf> "$output_dir/filename"
```

**Command Options:**
- `-jpeg`: Output as JPEG format
- `-jpegopt quality=100`: Maximum JPEG quality (0-100 scale)
- `-r 500`: Resolution at 500 DPI for high-quality images
- `<filename.pdf>`: Path to the input PDF file
- `<output_directory>/filename`: Output directory and base filename

### Step 4: Verify Output Files

Check that the JPEG files were created successfully:
```bash
ls -lh <output_directory>/
```

The output files will be named with a page number suffix:
- `filename-1.jpg`, `filename-2.jpg`, `filename-3.jpg`, etc.

## Important Notes

- `pdftoppm` is part of the `poppler-utils` package (on Linux) or installed via Homebrew (macOS)
- **Default output directory**: `/tmp/pdf_extract_<timestamp>` to avoid cluttering the current directory
- **User-specified directories**: Only use the current directory or custom paths when the user explicitly requests them
- Higher DPI values (like 500) produce larger, higher-quality images but take more time and disk space
- The base filename in the output path is a prefix - pdftoppm automatically appends `-<page>.jpg`
- JPEG quality of 100 is the maximum; lower values (50-90) produce smaller files with slight quality loss
- The output files will be numbered sequentially starting from page 1
- If the output directory doesn't exist, create it first to avoid errors
- The timestamp in the default directory name prevents conflicts when extracting multiple PDFs

## Examples

**Example 1: Basic PDF to JPEG conversion (default /tmp)**

User request: "extract document.pdf to jpeg images"

1. Check file: `ls -lh document.pdf`
2. Create output directory: `output_dir="/tmp/pdf_extract_$(date +%Y%m%d_%H%M%S)" && mkdir -p "$output_dir"`
3. Run extraction:
```bash
pdftoppm -jpeg -jpegopt quality=100 -r 500 document.pdf "$output_dir/document"
```
4. Verify output: `ls -lh "$output_dir"/`

Output files: `$output_dir/document-1.jpg`, `$output_dir/document-2.jpg`, etc.

**Example 2: Extract to current directory (user specified)**

User request: "extract document.pdf to the current folder"

1. Check file: `ls -lh document.pdf`
2. Use current directory: `output_dir="." && mkdir -p "$output_dir"`
3. Run extraction:
```bash
pdftoppm -jpeg -jpegopt quality=100 -r 500 document.pdf "$output_dir/document"
```
4. Verify output: `ls -lh ./`

**Example 3: Extract with full path to user-specified directory**

User request: "convert ~/Downloads/presentation.pdf to jpeg in output/ folder"

1. Check file: `ls -lh ~/Downloads/presentation.pdf`
2. Use specified directory: `output_dir="output" && mkdir -p "$output_dir"`
3. Run extraction:
```bash
pdftoppm -jpeg -jpegopt quality=100 -r 500 ~/Downloads/presentation.pdf "$output_dir/presentation"
```
4. Verify output: `ls -lh "$output_dir"/`

**Example 4: Extract specific page range (default /tmp)**

User request: "extract pages 1-3 from report.pdf"

1. Check file: `ls -lh report.pdf`
2. Create output directory: `output_dir="/tmp/pdf_extract_$(date +%Y%m%d_%H%M%S)" && mkdir -p "$output_dir"`
3. Run extraction with page range:
```bash
pdftoppm -jpeg -jpegopt quality=100 -r 500 -f 1 -l 3 report.pdf "$output_dir/report"
```
4. Verify output: `ls -lh "$output_dir"/`

**Additional Options for Page Range:**
- `-f <first_page>`: First page to extract (default: 1)
- `-l <last_page>`: Last page to extract (default: last page)
- `-singlefile`: Extract all pages into a single file (not recommended for JPEG)
- `-png`: Output as PNG format instead of JPEG

**Example 5: Lower quality for smaller files (default /tmp)**

User request: "extract document.pdf with medium quality"

1. Check file: `ls -lh document.pdf`
2. Create output directory: `output_dir="/tmp/pdf_extract_$(date +%Y%m%d_%H%M%S)" && mkdir -p "$output_dir"`
3. Run extraction with lower quality:
```bash
pdftoppm -jpeg -jpegopt quality=75 -r 300 document.pdf "$output_dir/document"
```
4. Verify output: `ls -lh "$output_dir"/`
