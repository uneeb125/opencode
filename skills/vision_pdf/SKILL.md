---
name: vision_pdf
description: Reads and analyzes PDF files by extracting pages as images and using vision analysis
---

# Vision PDF Reader Skill

Extract PDF pages as images and analyze with vision using the current model.

## Workflow

1. **Extract pages as images:**
   ```bash
   output_dir="$(pwd)/pdf_vision"
   mkdir -p "$output_dir"
   pdftoppm -jpeg -jpegopt quality=100 -r 500 <file.pdf> "$output_dir/filename"
   ```

   Options: `-f <page>` first page, `-l <page>` last page

2. **Get image paths:**
   ```bash
   ls "$output_dir"/filename-*.jpg | sort -V
   ```

3. **Analyze** - CRITICAL: Only read 1 image per prompt. The model WILL FAIL if multiple images are sent in the same call. For multiple pages:
   - Read image 1, wait for response
   - Then read image 2, wait for response
   - Continue one at a time

4. **Present findings** with page references

## Notes

- Default output: `/tmp/pdf_vision_<timestamp>`
- High DPI (500) produces better quality
- For large PDFs, warn about processing time and suggest page ranges
- Clean up temp files after unless user wants to keep them