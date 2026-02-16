---
name: docling_pdf_to_md
description: Converts PDF files to Markdown using docling with enriched formula, picture descriptions, and image export
---

# Docling PDF to Markdown Skill

You help users convert PDF files to Markdown format using the docling tool with enhanced processing options.

## When to Use

- User asks to convert a PDF file to Markdown
- User wants to extract content from a PDF document
- User references processing PDFs with docling
- User needs to read PDF content in Markdown format

## Workflow

### Step 1: Verify PDF File

Check that the provided PDF file exists and is readable:
```bash
ls -lh <filename.pdf>
```

### Step 2: Source the Python Environment

The docling command requires a specific Python virtual environment. Source it before running docling:
```bash
source ~/projects/doclinger/.venv/bin/activate
```

### Step 3: Run Docling Conversion

Execute the docling command with the specified enrichment options:

```bash
docling \
  --enrich-formula \
  --enrich-picture-classes \
  --enrich-picture-description \
  --image-export-mode referenced \
  --num-threads 16 \
  <filename.pdf>
```

**Command Options:**
- `--enrich-formula`: Enhances mathematical formulas in the output
- `--enrich-picture-classes`: Adds classification information for images
- `--enrich-picture-description`: Generates AI-powered descriptions for images
- `--image-export-mode referenced`: Exports images only when referenced in text
- `--num-threads 16`: Uses 16 parallel threads for faster processing
- `<filename.pdf>`: Path to the input PDF file

### Step 4: Display the Output

The docling command outputs Markdown to stdout. Capture and display it:
```bash
docling --enrich-formula --enrich-picture-classes --enrich-picture-description --image-export-mode referenced --num-threads 16 <filename.pdf>
```

For better readability, you can also pipe it to a file if requested:
```bash
docling --enrich-formula --enrich-picture-classes --enrich-picture-description --image-export-mode referenced --num-threads 16 <filename.pdf> > output.md
```

## Important Notes

- The docling command is only available after sourcing the virtual environment at `~/projects/doclinger/.venv/bin/activate`
- Large PDFs may take some time to process, especially with `--num-threads 16`
- The command outputs directly to stdout; redirect to a file if saving is needed
- Images referenced in the markdown will be exported alongside the markdown output
- The `--image-export-mode referenced` option means only images referenced in the document will be extracted
- If the virtual environment path is different, the user should provide the correct path
- Always verify the PDF file exists before running the conversion

## Examples

**Example 1: Basic PDF conversion**

User request: "convert document.pdf to markdown"

1. Check file: `ls -lh document.pdf`
2. Source environment: `source ~/projects/doclinger/.venv/bin/activate`
3. Run conversion:
```bash
docling --enrich-formula --enrich-picture-classes --enrich-picture-description --image-export-mode referenced --num-threads 16 document.pdf
```

**Example 2: Convert and save to file**

User request: "convert report.pdf and save as report.md"

1. Check file: `ls -lh report.pdf`
2. Source environment: `source ~/projects/doclinger/.venv/bin/activate`
3. Run conversion and save:
```bash
docling --enrich-formula --enrich-picture-classes --enrich-picture-description --image-export-mode referenced --num-threads 16 report.pdf > report.md
```

**Example 3: Convert with full path**

User request: "convert ~/Downloads/presentation.pdf"

1. Check file: `ls -lh ~/Downloads/presentation.pdf`
2. Source environment: `source ~/projects/doclinger/.venv/bin/activate`
3. Run conversion:
```bash
docling --enrich-formula --enrich-picture-classes --enrich-picture-description --image-export-mode referenced --num-threads 16 ~/Downloads/presentation.pdf
```
