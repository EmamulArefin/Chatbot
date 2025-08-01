# Bangla PDF Question Answering System

A Streamlit application that processes Bengali PDF documents using OCR and provides question-answering capabilities using OpenAI's GPT-4o.

## Prerequisites

### 1. Install Tesseract OCR

The application requires Tesseract OCR to extract text from PDF images.

**Option A: Using Windows Package Manager (Recommended)**
```powershell
winget install UB-Mannheim.TesseractOCR
```

**Option B: Manual Installation**
1. Download from: https://github.com/UB-Mannheim/tesseract/wiki
2. Install the executable
3. Add to system PATH if needed

### 2. Install Bengali Language Support

After installing Tesseract, you need to add Bengali language support:

**Option A: Run the provided script (As Administrator)**
```powershell
.\install_bengali_lang.ps1
```

**Option B: Manual Installation**
1. Download: https://github.com/tesseract-ocr/tessdata/raw/main/ben.traineddata
2. Place it in: `C:\Program Files\Tesseract-OCR\tessdata\ben.traineddata`

## Installation

1. Clone or download this repository
2. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

1. Place your Bengali PDF file in the `data/` folder as `bangla_document.pdf`
2. Run the application:
   ```bash
   streamlit run app.py
   ```
3. Enter your OpenAI API key in the sidebar
4. Ask questions about the document in Bengali

## Features

- Bengali OCR text extraction from PDF documents
- Text chunking and embedding generation
- FAISS vector search for relevant context
- OpenAI GPT-4o integration for question answering
- Caching system for faster subsequent runs

## Troubleshooting

### Error: "TesseractNotFoundError"
- Install Tesseract OCR using the instructions above
- Restart the application

### Error: "Bengali language data not found"
- Install Bengali language support using the instructions above
- Restart the application

### Alternative for Testing
If you want to test with English documents instead of Bengali:
1. Change `TESSERACT_CONFIG` in `app.py` to: `'--oem 3 --psm 6 -l eng'`
2. Use an English PDF document

## File Structure

```
├── app.py                     # Main Streamlit application
├── install_bengali_lang.ps1   # Script to install Bengali language support
├── requirements.txt           # Python dependencies
├── data/                      # Place your PDF files here
│   └── bangla_document.pdf    # Your Bengali PDF document
└── cache/                     # Cached embeddings (auto-created)
```

## Dependencies

- streamlit
- pytesseract
- pdf2image
- sentence-transformers
- faiss-cpu
- openai
- langchain
- python-dotenv