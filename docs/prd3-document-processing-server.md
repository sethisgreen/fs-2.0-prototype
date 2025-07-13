#### PRD 3: Document Processing Server

**Overview**  
Handles uploaded or fetched documents (images/PDFs) for extraction, using OCR and parsing to convert into structured data usable by agents.

**Goals/Objectives**

- Automate data entry from scans (e.g., death certificates).
- Integrate with Records Server for processing search results.
- Output clean, validated genealogical facts.

**Scope**  
In: OCR, name/date/relationship extraction.  
Out: Advanced ML training (use pre-trained models).

**Functional Requirements**

- Tools:
  - `ocr_document(file_path: str) -> str`: Runs Tesseract; returns raw text.
  - `parse_names(text: str) -> List[Dict]`: Tokenizes names with gender guessing.
  - `extract_dates(text: str) -> List[str]`: Normalizes to ISO8601 using dateparser.
  - `identify_relationships(text: str) -> List[Dict]`: Parses phrases like "son of".
- Utilities: Validation for genealogical reasonableness (e.g., dates < current year).

**Non-Functional Requirements**

- Performance: <10s per document.
- Security: Delete temp files post-processing.
- Accuracy: Aim for 90%+ on clear scans; flag low-confidence outputs.

**Dependencies**

- Libs: pytesseract, nameparser, dateparser.
- Inputs from Records Server.

**Milestones**

- v0.1: OCR + basic parsing (2 weeks).
- v0.2: Advanced extraction + validation (1 week).
- v1.0: Integration tests with sample docs (1 week).
