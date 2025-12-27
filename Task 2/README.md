# 📊 Task 2: Advanced Image & Chart Extraction

---

## 🎯 **Objective**

Extract **ALL visual content** from PDF documents with **100% accuracy**, including:

| Type | Description | Tool |
|------|-------------|------|
| 📷 **Embedded Images** | Logos, photos, icons, graphics | `image_extractor.py` |
| 📊 **Charts & Graphs** | Bar charts, line graphs, pie charts (vector graphics) | `chart_extractor.py` |
| 🔤 **OCR Text** | Text within images (logos, infographics, diagrams) | `ocr_extractor.py` |

---

## ✨ **Features**

### 🖼️ Image Extraction (`image_extractor.py`)
- ✅ Extracts **ALL embedded images** (JPG, PNG, TIFF, etc.)
- ✅ Preserves **100% original quality** (direct byte extraction)
- ✅ Captures **bounding box coordinates** for each image
- ✅ Generates **comprehensive metadata** (page, size, dimensions, format)
- ✅ Organized output: `images (PDF_NAME)/` folder per PDF

### 📊 Chart Extraction (`chart_extractor.py`)
- ✅ **Auto-detects** pages containing charts/graphs/diagrams
- ✅ Uses **vector graphics analysis** to identify chart regions
- ✅ **Crops only the chart area** (not full page!)
- ✅ High-resolution output (configurable DPI)
- ✅ Organized output: `charts (PDF_NAME)/` folder per PDF

### 🔤 OCR Extraction (`ocr_extractor.py`)
- ✅ Uses **PaddleOCR** (95-98% accuracy)
- ✅ Extracts text from **ALL extracted images**
- ✅ Handles logos, infographics, rotated text, stylized fonts
- ✅ **Sorts output**: images WITH text first, then images WITHOUT text
- ✅ Creates **separate metadata file** (preserves original)

---

## 🏗️ **Architecture**

```
┌─────────────────────────────────────────────────────────────────────┐
│                         📄 PDF DOCUMENT                             │
└─────────────────────────────────────────────────────────────────────┘
                                    │
                    ┌───────────────┼───────────────┐
                    ▼               ▼               ▼
        ┌───────────────┐  ┌───────────────┐  ┌───────────────┐
        │ 🖼️ EMBEDDED    │  │ 📊 VECTOR      │  │ 📄 TEXT       │
        │ IMAGES        │  │ GRAPHICS      │  │ CONTENT       │
        │ (Photos,      │  │ (Charts,      │  │ (Paragraphs,  │
        │  Logos, etc.) │  │  Graphs, etc.)│  │  Tables, etc.)│
        └───────┬───────┘  └───────┬───────┘  └───────────────┘
                │                  │                   │
                ▼                  ▼                   │
        ┌───────────────┐  ┌───────────────┐          │
        │ image_        │  │ chart_        │          │
        │ extractor.py  │  │ extractor.py  │      (Task 1)
        └───────┬───────┘  └───────┬───────┘
                │                  │
                ▼                  ▼
        ┌───────────────┐  ┌───────────────┐
        │ images (PDF)/ │  │ charts (PDF)/ │
        │ └── *.png/jpg │  │ └── *_chart.png│
        └───────┬───────┘  └───────────────┘
                │
                ▼
        ┌───────────────┐
        │ ocr_          │
        │ extractor.py  │
        └───────┬───────┘
                │
                ▼
        ┌───────────────────────────────────┐
        │ metadata_with_ocr (PDF_NAME).json │
        │ └── Images sorted by text content │
        └───────────────────────────────────┘
```

---

## 📦 **Installation**

### 1. Prerequisites
- Python 3.8 or higher
- pip (Python package manager)

### 2. Install Dependencies

```bash
cd "c:\Users\gudur\Desktop\Greonomy task 2\Task 2"
pip install -r requirements.txt
```

### 3. Dependencies Installed
| Package | Purpose |
|---------|---------|
| `PyMuPDF` (fitz) | PDF parsing, image extraction, page rendering |
| `Pillow` | Image processing and optimization |
| `PaddlePaddle` | Deep learning framework for OCR |
| `PaddleOCR` | High-accuracy text extraction from images |

---

## 🚀 **Quick Start**

### Step 1: Place your PDFs
```
📁 Greonomy task 2/
├── 📁 pdfs/
│   ├── YourDocument1.pdf  ← Place PDFs here
│   └── YourDocument2.pdf
└── 📁 Task 2/
    └── (scripts here)
```

### Step 2: Extract Images
```bash
cd "c:\Users\gudur\Desktop\Greonomy task 2\Task 2"

# Single PDF
python image_extractor.py "..\pdfs\YourDocument.pdf"

# OR all PDFs at once
python batch_extractor.py
```

### Step 3: Extract Charts
```bash
# Auto-detect and crop charts from all pages
python chart_extractor.py "..\pdfs\YourDocument.pdf"

# OR specific pages only
python chart_extractor.py "..\pdfs\YourDocument.pdf" --pages 3,9,20,45

# OR higher resolution
python chart_extractor.py "..\pdfs\YourDocument.pdf" --dpi 200
```

### Step 4: Run OCR on Images
```bash
python ocr_extractor.py YourDocument
# Note: Just the PDF name, NO path, NO .pdf extension!
```

---

## 📁 **Output Structure**

After running all extractors:

```
📁 Task 2/
│
├── 📁 images (YourDocument)/           ← Extracted embedded images
│   ├── page1_img1.jpg
│   ├── page1_img2.png
│   ├── page3_img1.jpg
│   └── ...
│
├── 📁 charts (YourDocument)/           ← Cropped chart images
│   ├── page5_chart1.png
│   ├── page9_chart1.png
│   ├── page20_chart1.png
│   └── ...
│
├── 📄 metadata (YourDocument).json     ← Image metadata
├── 📄 charts_metadata (YourDocument).json  ← Chart metadata
└── 📄 metadata_with_ocr (YourDocument).json  ← Metadata + OCR text
```

---

## 📋 **Metadata Format**

### Image Metadata (`metadata (PDF_NAME).json`)
```json
{
  "pdf_name": "YourDocument.pdf",
  "total_pages": 160,
  "total_images": 25,
  "images": [
    {
      "page_number": 1,
      "image_index": 1,
      "image_name": "page1_img1.jpg",
      "width": 360,
      "height": 169,
      "format": "jpg",
      "size_bytes": 18091,
      "bbox": {
        "x0": 85.08,
        "y0": 592.8,
        "x1": 258.0,
        "y1": 674.04
      },
      "xref": 33
    }
  ]
}
```

### Chart Metadata (`charts_metadata (PDF_NAME).json`)
```json
{
  "pdf_name": "YourDocument.pdf",
  "dpi": 150,
  "chart_pages": 48,
  "charts": [
    {
      "page_number": 5,
      "image_name": "page5_chart1.png",
      "width": 1106,
      "height": 651,
      "size_bytes": 107097,
      "bbox": {
        "x0": 32.48,
        "y0": 119.98,
        "x1": 562.96,
        "y1": 431.97
      },
      "cropped": true
    }
  ]
}
```

### OCR Metadata (`metadata_with_ocr (PDF_NAME).json`)
```json
{
  "images": [
    {
      "page_number": 1,
      "image_name": "page1_img1.jpg",
      "text": "SAMADHAN Nurturing Dreams - Innovative Solutions"
    },
    {
      "page_number": 2,
      "image_name": "page2_img1.jpg",
      "text": ""
    }
  ],
  "images_with_text_count": 4,
  "images_without_text_count": 21,
  "ocr_engine": "PaddleOCR"
}
```

---

## 📊 **Command Reference**

### image_extractor.py
```bash
# Basic usage
python image_extractor.py "..\pdfs\Document.pdf"

# Output:
# - images (Document)/       ← Image files
# - metadata (Document).json ← Metadata
```

### batch_extractor.py
```bash
# Process ALL PDFs in pdfs folder
python batch_extractor.py

# No arguments needed!
```

### chart_extractor.py
```bash
# Auto-detect chart pages
python chart_extractor.py "..\pdfs\Document.pdf"

# Specific pages only
python chart_extractor.py "..\pdfs\Document.pdf" --pages 3,9,20

# All pages (for debugging)
python chart_extractor.py "..\pdfs\Document.pdf" --all

# Higher quality
python chart_extractor.py "..\pdfs\Document.pdf" --dpi 200
```

### ocr_extractor.py
```bash
# Run OCR on extracted images
python ocr_extractor.py DocumentName

# Show available PDFs with extracted images
python ocr_extractor.py
```

---

## 🔧 **Technical Details**

### Why PyMuPDF?
| Feature | PyMuPDF | pdfplumber | pdf2image |
|---------|---------|------------|-----------|
| Image Quality | **100% Original** | Rendered | Rendered |
| Speed | **Fast** | Medium | Slow |
| Vector Graphics | **Yes** | Limited | Rendered only |
| Memory Usage | **Low** | Medium | High |

### Why PaddleOCR?
| Feature | PaddleOCR | Tesseract | EasyOCR |
|---------|-----------|-----------|---------|
| Accuracy | **95-98%** | 85-90% | 90-95% |
| Complex Layouts | **Excellent** | Poor | Good |
| Stylized Fonts | **Excellent** | Poor | Good |
| CPU Performance | **Good** | Good | Slow |
| Model Size | ~100 MB | ~15 MB | ~300 MB |

### Chart Detection Algorithm
1. **Vector Analysis**: Counts drawing paths (lines, curves, shapes)
2. **Keyword Detection**: Checks for chart-related keywords (%, FY, growth, etc.)
3. **Text Density**: Analyzes text vs. graphics ratio
4. **Bounding Box Calculation**: Combines all vector drawings to find chart region
5. **Smart Cropping**: Extracts only the chart area, not full page

---

## 🛠️ **Troubleshooting**

### PaddleOCR Import Error
```bash
# Make sure to use correct pip
python -m pip install paddlepaddle paddleocr
```

### Charts Not Detected
```bash
# Force extract all pages to check
python chart_extractor.py "..\pdfs\Document.pdf" --all
```

### Images Not Found
```bash
# Run image extractor first!
python image_extractor.py "..\pdfs\Document.pdf"
```

---

## 📈 **Performance**

Tested on: **Lenovo IdeaPad Slim 3 (Ryzen 5, 8GB RAM, No GPU)**

| Document Size | Image Extraction | Chart Extraction | OCR |
|---------------|------------------|------------------|-----|
| 20 pages | ~2 seconds | ~10 seconds | ~30 seconds |
| 160 pages | ~10 seconds | ~60 seconds | ~3 minutes |

---

## 👨‍💻 **Developer Info**

- **Developer**: Developer 2 (Image Extraction Owner)
- **Task**: Task 2 - Image Extraction
- **Status**: ✅ Complete

---

## 📜 **License**

This project is part of the Greonomy Document Processing Pipeline.

---

<div align="center">

### 🚀 Ready to Extract!

```
python batch_extractor.py && python chart_extractor.py "..\pdfs\*.pdf"
```

</div>
