<div align="center">

# 📊 GREONOMY - Task 2: Image Extraction

### Advanced PDF Image & Chart Extraction with OCR

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org)
[![PyMuPDF](https://img.shields.io/badge/PyMuPDF-Latest-green.svg)](https://pymupdf.readthedocs.io/)
[![PaddleOCR](https://img.shields.io/badge/PaddleOCR-High%20Accuracy-orange.svg)](https://github.com/PaddlePaddle/PaddleOCR)
[![Status](https://img.shields.io/badge/Status-Complete-success.svg)]()

---

**Extract ALL visual content from PDF documents with 100% accuracy**

*Developed by* **GS Tejas**

</div>

---

## 📌 Table of Contents

1. [❓ The Problem](#-the-problem)
2. [💡 The Solution](#-the-solution)
3. [📦 What You Get (Output)](#-what-you-get-output)
4. [🛠️ Setup & Installation](#️-setup--installation)
5. [📁 Project Structure](#-project-structure)
6. [🚀 How to Execute](#-how-to-execute)
7. [📋 Scripts Overview](#-scripts-overview)
8. [📊 Output Examples](#-output-examples)
9. [🔧 Technical Details](#-technical-details)
10. [👨‍💻 Author](#-author)

---

## ❓ The Problem

### Challenges with PDF Visual Content Extraction:

| Problem | Description |
|---------|-------------|
| 🖼️ **Embedded Images** | PDFs contain logos, photos, icons that are hard to extract programmatically |
| 📊 **Charts & Graphs** | Vector graphics (bar charts, line graphs, pie charts) are NOT stored as images - they're drawing commands |
| 🔤 **Text in Images** | Logos and infographics contain text that's invisible to standard text extraction |
| 📍 **Location Data** | Need to know WHERE each image appears on the page (bounding box) |
| 📁 **Organization** | Multiple PDFs need organized, separate output folders |

### Real-World Use Cases:
- 📈 **Financial Reports**: Extract charts showing market trends, growth projections
- 🏢 **Company Documents**: Extract logos, product images, organizational charts
- 📊 **Research Papers**: Extract figures, diagrams, data visualizations
- 📋 **Presentations**: Extract embedded images and infographics

---

## 💡 The Solution

### Our 4-Script Pipeline:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              📄 PDF DOCUMENT                                │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                    ┌─────────────────┼─────────────────┐
                    ▼                 ▼                 ▼
         ┌──────────────────┐ ┌──────────────────┐ ┌──────────────────┐
         │ 🖼️ EMBEDDED       │ │ 📊 VECTOR         │ │ 📄 TEXT          │
         │ IMAGES           │ │ GRAPHICS         │ │ CONTENT          │
         │ (Photos, Logos)  │ │ (Charts, Graphs) │ │ (Paragraphs)     │
         └────────┬─────────┘ └────────┬─────────┘ └──────────────────┘
                  │                    │                    
                  ▼                    ▼                    
┌─────────────────────────────┐ ┌─────────────────────────────┐
│   📜 image_extractor.py     │ │   📜 chart_extractor.py     │
│   ─────────────────────     │ │   ─────────────────────     │
│   • Extracts embedded imgs  │ │   • Auto-detects charts     │
│   • 100% original quality   │ │   • Crops chart regions     │
│   • Saves bounding boxes    │ │   • High-res rendering      │
└────────────┬────────────────┘ └────────────┬────────────────┘
             │                               │
             ▼                               ▼
┌─────────────────────────────┐ ┌─────────────────────────────┐
│   📁 images (PDF_NAME)/     │ │   📁 charts (PDF_NAME)/     │
│   └── page1_img1.jpg        │ │   └── page5_chart1.png      │
│   └── page2_img1.png        │ │   └── page9_chart1.png      │
└────────────┬────────────────┘ └─────────────────────────────┘
             │
             ▼
┌─────────────────────────────┐
│   📜 ocr_extractor.py       │
│   ─────────────────────     │
│   • PaddleOCR (95-98% acc)  │
│   • Extracts text from imgs │
│   • Sorts by text presence  │
└────────────┬────────────────┘
             │
             ▼
┌─────────────────────────────┐
│  📄 metadata_with_ocr.json  │
│  └── Images with "text"     │
└─────────────────────────────┘
```

### Key Technologies:
| Technology | Purpose | Why Chosen |
|------------|---------|------------|
| **PyMuPDF** | PDF parsing & image extraction | 100% original quality, fast, low memory |
| **PaddleOCR** | Text extraction from images | 95-98% accuracy, handles complex layouts |
| **Pillow** | Image processing | Optimization and format handling |

---

## 📦 What You Get (Output)

### For Each PDF, You Get:

#### 1. **Embedded Images** (`images (PDF_NAME)/`)
```
📁 images (AutomobileGear)/
├── page1_img1.jpg      ← Logo
├── page1_img2.jpg      ← Banner image
├── page3_img1.jpg      ← Product photo
├── page6_img1.jpg      ← Icon
└── ... (all embedded images)
```

#### 2. **Cropped Charts** (`charts (PDF_NAME)/`)
```
📁 charts (Industry-Report...)/
├── page5_chart1.png    ← Bar chart (cropped!)
├── page9_chart1.png    ← Line graph (cropped!)
├── page33_chart1.png   ← Pie chart (cropped!)
└── ... (48 total charts detected!)
```

#### 3. **Metadata Files**
```
📄 metadata (AutomobileGear).json           ← Image info + bounding boxes
📄 charts_metadata (Industry-Report...).json ← Chart info + crop coordinates
📄 metadata_with_ocr (AutomobileGear).json  ← Images + extracted text
📄 all_images_metadata.json                 ← Consolidated for all PDFs
```

### Sample Metadata Output:

```json
{
  "pdf_name": "AutomobileGear.pdf",
  "total_images": 25,
  "images": [
    {
      "page_number": 1,
      "image_name": "page1_img1.jpg",
      "width": 360,
      "height": 169,
      "format": "jpg",
      "bbox": { "x0": 85.08, "y0": 592.8, "x1": 258.0, "y1": 674.04 },
      "text": "SAMADHAN Nurturing Dreams - Innovative Solutions"
    }
  ],
  "images_with_text_count": 2,
  "images_without_text_count": 23
}
```

---

## 🛠️ Setup & Installation

### Prerequisites
- ✅ Python 3.8 or higher
- ✅ pip (Python package manager)
- ✅ Windows / Linux / macOS

### Step 1: Clone or Download
```bash
git clone https://github.com/GS-Tejas-hub/greonomy-task2-image-extraction.git
cd greonomy-task2-image-extraction
```

### Step 2: Install Dependencies
```bash
cd "Task 2"
pip install -r requirements.txt
```

### Step 3: Verify Installation
```bash
python -c "import fitz; print('PyMuPDF OK')"
python -c "from paddleocr import PaddleOCR; print('PaddleOCR OK')"
```

### Dependencies List (`requirements.txt`):
| Package | Version | Purpose |
|---------|---------|---------|
| `PyMuPDF` | Latest | PDF parsing, rendering, image extraction |
| `Pillow` | Latest | Image processing |
| `paddlepaddle` | Latest | Deep learning framework (CPU) |
| `paddleocr` | Latest | OCR engine |

---

## 📁 Project Structure

```
📁 Greonomy task 2/
│
├── 📁 pdfs/                                    ← PLACE YOUR PDFs HERE
│   ├── AutomobileGear.pdf
│   └── Industry-Report-on-the-Passenger-Vehicle-Industry-in-India-CRISIL.pdf
│
├── 📁 Task 2/                                  ← SCRIPTS & OUTPUT
│   │
│   ├── 📜 image_extractor.py                   ← Extract embedded images
│   ├── 📜 batch_extractor.py                   ← Process ALL PDFs at once
│   ├── 📜 chart_extractor.py                   ← Extract & crop charts
│   ├── 📜 ocr_extractor.py                     ← OCR on extracted images
│   │
│   ├── 📄 requirements.txt                     ← Dependencies
│   ├── 📄 README.md                            ← This file
│   │
│   │   ─────────── OUTPUT (generated) ───────────
│   │
│   ├── 📁 images (AutomobileGear)/             ← Extracted images
│   ├── 📁 images (Industry-Report...)/         ← Extracted images
│   │
│   ├── 📁 charts (Industry-Report...)/         ← Cropped charts
│   │
│   ├── 📄 metadata (AutomobileGear).json       ← Image metadata
│   ├── 📄 metadata (Industry-Report...).json   ← Image metadata
│   ├── 📄 charts_metadata (...).json           ← Chart metadata
│   ├── 📄 metadata_with_ocr (...).json         ← OCR results
│   └── 📄 all_images_metadata.json             ← Consolidated
│
└── 📄 .gitignore                               ← Excludes PDFs & outputs from git
```

---

## 🚀 How to Execute

### ⚠️ IMPORTANT: First navigate to Task 2 folder!
```powershell
cd "c:\Users\gudur\Desktop\Greonomy task 2\Task 2"
```

---

### 1️⃣ Extract Images from ALL PDFs
```powershell
python batch_extractor.py
```
**What it does:** Scans `pdfs/` folder, extracts all embedded images from every PDF, creates separate `images (PDF_NAME)/` folder for each.

---

### 2️⃣ Extract Images from SINGLE PDF
```powershell
python image_extractor.py "..\pdfs\AutomobileGear.pdf"
```
**What it does:** Extracts embedded images from one specific PDF.

---

### 3️⃣ Extract Charts/Graphs from PDF
```powershell
python chart_extractor.py "..\pdfs\Industry-Report-on-the-Passenger-Vehicle-Industry-in-India-CRISIL.pdf"
```
**What it does:** Auto-detects pages with charts, crops just the chart region (not full page!).

**Options:**
```powershell
# Extract specific pages only
python chart_extractor.py "..\pdfs\Document.pdf" --pages 3,9,20,45

# Higher resolution (default is 150 DPI)
python chart_extractor.py "..\pdfs\Document.pdf" --dpi 200

# Force extract ALL pages
python chart_extractor.py "..\pdfs\Document.pdf" --all
```

---

### 4️⃣ Run OCR on Extracted Images
```powershell
python ocr_extractor.py AutomobileGear
```
**⚠️ NOTE:** Just the PDF name - NO path, NO `.pdf` extension!

**What it does:** Reads extracted images, runs PaddleOCR, adds `"text"` field to metadata, sorts images (text first, no-text last).

---

### 📋 Command Quick Reference

| Task | Command |
|------|---------|
| Extract ALL images from ALL PDFs | `python batch_extractor.py` |
| Extract images from ONE PDF | `python image_extractor.py "..\pdfs\File.pdf"` |
| Extract charts from PDF | `python chart_extractor.py "..\pdfs\File.pdf"` |
| Run OCR on extracted images | `python ocr_extractor.py FileName` |

---

## 📋 Scripts Overview

### 1. `image_extractor.py`
| Feature | Description |
|---------|-------------|
| **Purpose** | Extract embedded images (logos, photos, icons) |
| **Input** | PDF file path |
| **Output** | `images (PDF_NAME)/` folder + `metadata (PDF_NAME).json` |
| **Quality** | 100% original (direct byte extraction) |

### 2. `batch_extractor.py`
| Feature | Description |
|---------|-------------|
| **Purpose** | Process all PDFs in `pdfs/` folder at once |
| **Input** | None (auto-scans folder) |
| **Output** | Separate folder for each PDF + `all_images_metadata.json` |

### 3. `chart_extractor.py`
| Feature | Description |
|---------|-------------|
| **Purpose** | Detect & extract charts, graphs, diagrams |
| **Input** | PDF file path |
| **Output** | `charts (PDF_NAME)/` folder + `charts_metadata (PDF_NAME).json` |
| **Special** | Auto-crops chart region (not full page!) |

### 4. `ocr_extractor.py`
| Feature | Description |
|---------|-------------|
| **Purpose** | Extract text from images using PaddleOCR |
| **Input** | PDF name (without extension) |
| **Output** | `metadata_with_ocr (PDF_NAME).json` |
| **Accuracy** | 95-98% (handles complex layouts, stylized fonts) |

---

## 📊 Output Examples

### Extracted Image (Full Quality)
```
📷 page1_img1.jpg
├── Size: 18,091 bytes
├── Dimensions: 360 x 169 px
├── Format: JPEG
├── Location: Page 1, bbox(85.08, 592.8, 258.0, 674.04)
└── OCR Text: "SAMADHAN Nurturing Dreams - Innovative Solutions"
```

### Cropped Chart (Auto-Detected)
```
📊 page5_chart1.png
├── Size: 107,097 bytes
├── Dimensions: 1106 x 651 px (cropped, not 1241x1755!)
├── Format: PNG
├── Location: Page 5, bbox(32.48, 119.98, 562.96, 431.97)
└── Cropped: ✅ Yes
```

### OCR Results (Sorted)
```json
{
  "images": [
    { "text": "CRISIL Market Intelligence & Analytics" },  ← WITH text (first)
    { "text": "Units Thousand" },                          ← WITH text
    { "text": "" },                                        ← No text (last)
    { "text": "" }                                         ← No text
  ],
  "images_with_text_count": 4,
  "images_without_text_count": 3
}
```

---

## 🔧 Technical Details

### Why PyMuPDF over alternatives?
| Feature | PyMuPDF ✅ | pdfplumber | pdf2image |
|---------|-----------|------------|-----------|
| Image Quality | **100% Original** | Rendered | Rendered |
| Speed | **Fast** | Medium | Slow |
| Vector Graphics | **Yes** | Limited | Rendered only |
| Memory Usage | **Low** | Medium | High |

### Why PaddleOCR over alternatives?
| Feature | PaddleOCR ✅ | Tesseract | EasyOCR |
|---------|-------------|-----------|---------|
| Accuracy | **95-98%** | 85-90% | 90-95% |
| Complex Layouts | **Excellent** | Poor | Good |
| Stylized Fonts | **Excellent** | Poor | Good |
| CPU Performance | **Good** | Good | Slow |

### Chart Detection Algorithm
1. **Vector Analysis** - Count drawing paths (lines, curves, shapes)
2. **Keyword Detection** - Check for %, FY, growth, chart, source
3. **Text Density Analysis** - Compare text vs graphics ratio
4. **Bounding Box Merge** - Combine all drawing coordinates
5. **Smart Cropping** - Extract only the chart region

---

## 🛠️ Troubleshooting

### PaddleOCR Import Error
```bash
python -m pip install paddlepaddle paddleocr
```

### "PDF not found" Error
Make sure you're using the correct path:
```bash
# ✅ Correct
python chart_extractor.py "..\pdfs\Document.pdf"

# ❌ Wrong
python chart_extractor.py "Document.pdf"
python chart_extractor.py "Document"
```

### Charts Not Detected
Try forcing all pages:
```bash
python chart_extractor.py "..\pdfs\Document.pdf" --all
```

---

## 📈 Performance

Tested on: **Lenovo IdeaPad Slim 3 (Ryzen 5, 8GB RAM, No GPU)**

| Document | Image Extraction | Chart Extraction | OCR |
|----------|------------------|------------------|-----|
| 20 pages | ~2 seconds | ~10 seconds | ~30 seconds |
| 160 pages | ~10 seconds | ~60 seconds | ~3 minutes |

---

## 👨‍💻 Author

<div align="center">

### **GS Tejas**

*Task 2 - Image Extraction*

[![GitHub](https://img.shields.io/badge/GitHub-GS--Tejas--hub-black?logo=github)](https://github.com/GS-Tejas-hub)

---

**Greonomy Document Processing Pipeline**

*Part of the larger document processing ecosystem*

| Task | Description | Status |
|------|-------------|--------|
| Task 1 | Text Extraction | 🔄 |
| **Task 2** | **Image Extraction** | ✅ **Complete** |
| Task 3 | Table Extraction | 🔄 |

</div>

---

<div align="center">

### 🚀 Ready to Extract!

```powershell
cd "Task 2"
python batch_extractor.py
python chart_extractor.py "..\pdfs\YourDocument.pdf"
python ocr_extractor.py YourDocument
```

**Star ⭐ this repo if it helped you!**

</div>
