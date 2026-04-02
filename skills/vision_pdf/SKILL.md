---
name: vision_pdf
description: Reads and analyzes PDF files by extracting pages as images and using vision analysis
---

# Vision PDF Reader Skill

Extract PDF pages as images and analyze with vision using the current model.

## Workflow

1. **Extract pages as images:**
   ```bash
   output_dir="/tmp/pdf_vision_$(date +%Y%m%d_%H%M%S)"
   mkdir -p "$output_dir"
   pdftoppm -jpeg -jpegopt quality=100 -r 500 <file.pdf> "$output_dir/filename"
   ```

   Options: `-f <page>` first page, `-l <page>` last page

2. **Get image paths:**
   ```bash
   ls "$output_dir"/filename-*.jpg | sort -V
   ```

3. **Analyze** directly with current model - only read 2 images at a time. For multiple pages, process in batches of 2.

4. **Present findings** with page references

## Notes

- Default output: `/tmp/pdf_vision_<timestamp>`
- High DPI (500) produces better quality
- For large PDFs, warn about processing time and suggest page ranges
- Clean up temp files after unless user wants to keep them