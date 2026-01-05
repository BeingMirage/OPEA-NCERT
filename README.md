# NCERT Multi-Modal RAG — Extraction Environment (ncert-extract)

This README describes how to recreate the **ncert-extract** environment (Windows-focused instructions) and run the extraction pipeline that converts NCERT PDFs/images into `.md`, `.txt`, and `chunks.jsonl` outputs suitable for later chunking/embedding/RAG.

---

## 1. Overview

This environment focuses on document ingestion and extraction:
- PDF (native + scanned)
- Images (JPEG/PNG/HEIC)
- Tables
- Multilingual OCR (Hindi, Bengali, Tamil, etc.)
- Math/formula image extraction (saved as image; optional future LaTeX OCR)

Outputs per-file (under `output/<grade>/<subject>/<file>/`):
- `document.md` — markdown with frontmatter (metadata + converted content)
- `document.txt` — plain raw text
- `chunks.jsonl` — one JSON chunk per logical element (ready for embedding)

---

## 2. System requirements (binaries)

Install these system-level tools before Python dependencies.

### Windows
1. **Tesseract OCR**  
   - Download installer (UB Mannheim builds recommended):  
     https://github.com/UB-Mannheim/tesseract/wiki  
   - Install and add to PATH (e.g., `C:\Program Files\Tesseract-OCR\`)
   - Install language packs you need: copy `*.traineddata` into `tessdata` folder (e.g., `hin.traineddata`, `ben.traineddata`).

2. **Poppler** (for `pdf2image` / `pdftoppm`)  
   - Download (oschwartz10612/poppler-windows) releases:  
     https://github.com/oschwartz10612/poppler-windows/releases  
   - Extract and add `...\poppler\Library\bin` to PATH.

3. **qpdf** (recommended for `pikepdf`)  
   - On Windows you can install QPDF from: https://qpdf.sourceforge.io/ or via packages. Ensure `qpdf.exe` available.

4. (Optional) **Ghostscript** — required by some PDF → image or PDF table tools if needed.

_Verify binaries accessible from terminal:_
```bash
tesseract --version
pdftoppm -h
qpdf --version
