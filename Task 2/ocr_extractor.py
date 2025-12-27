"""
================================================================================
OCR EXTRACTOR - Task 2
================================================================================
Developer: Developer 2 (Image Extraction Owner)
Goal: Extract text from extracted images using PaddleOCR

Features:
- Reads existing metadata file
- Runs OCR on all extracted images
- Creates NEW metadata file with "text" field added
- Does NOT modify original metadata
- Handles logos, infographics, flowcharts, diagrams

Dependencies:
- PaddleOCR
- PaddlePaddle

Output:
- metadata_with_ocr (pdf_name).json - New metadata with OCR text
================================================================================
"""

import json
import sys
import os
from datetime import datetime
from pathlib import Path

# Suppress PaddlePaddle warnings
os.environ['GLOG_minloglevel'] = '2'

try:
    from paddleocr import PaddleOCR
except ImportError:
    print("❌ PaddleOCR not installed!")
    print("   Run: pip install paddlepaddle paddleocr")
    sys.exit(1)


class OCRExtractor:
    """
    A class to extract text from images using PaddleOCR.
    Creates a new metadata file with OCR text added.
    """
    
    def __init__(self, pdf_name: str = None, metadata_path: str = None):
        """
        Initialize the OCR Extractor.
        
        Args:
            pdf_name: Name of the PDF (without extension) to process
            metadata_path: Direct path to metadata file (alternative to pdf_name)
        """
        self.script_dir = Path(__file__).parent.resolve()
        
        # Find metadata file
        if metadata_path:
            self.metadata_path = Path(metadata_path)
        elif pdf_name:
            self.metadata_path = self.script_dir / f"metadata ({pdf_name}).json"
        else:
            raise ValueError("Either pdf_name or metadata_path must be provided")
        
        if not self.metadata_path.exists():
            raise FileNotFoundError(f"Metadata file not found: {self.metadata_path}")
        
        # Load existing metadata
        with open(self.metadata_path, 'r', encoding='utf-8') as f:
            self.metadata = json.load(f)
        
        # Get PDF name from metadata
        self.pdf_name = Path(self.metadata.get("pdf_name", "unknown")).stem
        
        # Find images folder
        self.images_dir = self.script_dir / f"images ({self.pdf_name})"
        
        if not self.images_dir.exists():
            raise FileNotFoundError(f"Images folder not found: {self.images_dir}")
        
        # Initialize PaddleOCR
        print("🔄 Initializing PaddleOCR (this may take a moment on first run)...")
        self.ocr = PaddleOCR(
            lang='en'  # English (change as needed)
        )
        print("✅ PaddleOCR initialized!\n")
    
    def _extract_text_from_image(self, image_path: Path) -> str:
        """
        Extract text from a single image using PaddleOCR.
        
        Args:
            image_path: Path to the image file
            
        Returns:
            Extracted text as a single string, or empty string if no text found
        """
        try:
            # Use predict() for newer PaddleOCR versions (3.3+)
            result = self.ocr.predict(str(image_path))
            
            if result is None or len(result) == 0:
                return ""
            
            # Extract all text from results
            text_parts = []
            
            # Handle different result formats
            for page_result in result:
                if page_result is None:
                    continue
                    
                # Check if it's the new format (dict with 'rec_texts')
                if isinstance(page_result, dict):
                    if 'rec_texts' in page_result:
                        texts = page_result.get('rec_texts', [])
                        scores = page_result.get('rec_scores', [])
                        for i, text in enumerate(texts):
                            score = scores[i] if i < len(scores) else 1.0
                            if score > 0.5:  # Only include high-confidence text
                                text_parts.append(text)
                    elif 'text' in page_result:
                        text_parts.append(page_result['text'])
                # Old format (list of tuples)
                elif isinstance(page_result, list):
                    for item in page_result:
                        if item is None:
                            continue
                        if isinstance(item, dict):
                            if 'rec_texts' in item:
                                text_parts.extend(item['rec_texts'])
                        elif isinstance(item, (list, tuple)) and len(item) >= 2:
                            text = item[1][0] if isinstance(item[1], (list, tuple)) else item[1]
                            confidence = item[1][1] if isinstance(item[1], (list, tuple)) and len(item[1]) > 1 else 1.0
                            if confidence > 0.5:
                                text_parts.append(str(text))
            
            # Join all text with spaces
            full_text = " ".join(text_parts)
            return full_text.strip()
            
        except Exception as e:
            print(f"   ⚠️ OCR error: {e}")
            return ""
    
    def run_ocr(self) -> dict:
        """
        Run OCR on all images and create new metadata with text.
        
        Returns:
            New metadata dictionary with OCR text added
        """
        print(f"\n{'='*60}")
        print(f"🔍 OCR EXTRACTOR - Task 2")
        print(f"{'='*60}")
        print(f"📄 PDF: {self.metadata.get('pdf_name', 'Unknown')}")
        print(f"📂 Images: {self.images_dir}")
        print(f"🖼️  Total Images: {len(self.metadata.get('images', []))}")
        print(f"{'='*60}\n")
        
        # Create new metadata (deep copy to not modify original)
        new_metadata = json.loads(json.dumps(self.metadata))
        new_metadata["ocr_extraction_date"] = datetime.now().isoformat()
        new_metadata["ocr_engine"] = "PaddleOCR"
        
        images_with_text = 0
        images_without_text = 0
        
        # Process each image
        for i, img_info in enumerate(new_metadata.get("images", [])):
            image_name = img_info.get("image_name", "")
            image_path = self.images_dir / image_name
            
            print(f"🔄 Processing [{i+1}/{len(new_metadata['images'])}]: {image_name}...", end=" ")
            
            if not image_path.exists():
                print("❌ File not found!")
                img_info["text"] = ""
                images_without_text += 1
                continue
            
            # Extract text
            text = self._extract_text_from_image(image_path)
            
            # Add text field to image info
            img_info["text"] = text
            
            if text:
                images_with_text += 1
                # Truncate for display
                display_text = text[:50] + "..." if len(text) > 50 else text
                print(f"✅ Found: \"{display_text}\"")
            else:
                images_without_text += 1
                print("📷 No text found (image only)")
        
        # Sort images: ones with text first, then ones without text
        # Within each group, maintain original order (by page_number, then image_index)
        new_metadata["images"] = sorted(
            new_metadata["images"],
            key=lambda x: (
                0 if x.get("text", "") else 1,  # Text first (0), no text second (1)
                x.get("page_number", 0),         # Then by page number
                x.get("image_index", 0)          # Then by image index
            )
        )
        
        # Add counts to metadata for easy reference
        new_metadata["images_with_text_count"] = images_with_text
        new_metadata["images_without_text_count"] = images_without_text
        
        # Save new metadata with OCR
        self._save_ocr_metadata(new_metadata)
        
        # Print summary
        self._print_summary(images_with_text, images_without_text)
        
        return new_metadata
    
    def _save_ocr_metadata(self, metadata: dict):
        """Save metadata with OCR to new file."""
        output_filename = f"metadata_with_ocr ({self.pdf_name}).json"
        output_path = self.script_dir / output_filename
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False)
        
        print(f"\n💾 OCR Metadata saved: {output_path}")
    
    def _print_summary(self, with_text: int, without_text: int):
        """Print OCR extraction summary."""
        total = with_text + without_text
        print(f"\n{'='*60}")
        print(f"✅ OCR EXTRACTION COMPLETE")
        print(f"{'='*60}")
        print(f"📄 PDF: {self.metadata.get('pdf_name', 'Unknown')}")
        print(f"🖼️  Total Images Processed: {total}")
        print(f"📝 Images WITH text: {with_text}")
        print(f"📷 Images WITHOUT text: {without_text}")
        print(f"📋 Output: metadata_with_ocr ({self.pdf_name}).json")
        print(f"{'='*60}\n")


def find_available_pdfs():
    """Find all PDFs with existing metadata."""
    script_dir = Path(__file__).parent.resolve()
    metadata_files = list(script_dir.glob("metadata (*).json"))
    
    # Filter out OCR metadata files
    metadata_files = [f for f in metadata_files if "with_ocr" not in f.name]
    
    return metadata_files


def main():
    """Main function to run OCR extraction."""
    
    script_dir = Path(__file__).parent.resolve()
    
    print(f"\n{'='*60}")
    print(f"🔍 OCR EXTRACTOR - Task 2")
    print(f"{'='*60}\n")
    
    # Check command line arguments
    if len(sys.argv) > 1:
        # PDF name provided
        pdf_name = sys.argv[1]
        
        # Remove extension if provided
        if pdf_name.endswith('.pdf'):
            pdf_name = pdf_name[:-4]
        
        # Check if it's a path to metadata file
        if pdf_name.endswith('.json'):
            metadata_path = pdf_name
            extractor = OCRExtractor(metadata_path=metadata_path)
        else:
            extractor = OCRExtractor(pdf_name=pdf_name)
    else:
        # Find available metadata files
        metadata_files = find_available_pdfs()
        
        if not metadata_files:
            print("❌ No metadata files found!")
            print("   Run image_extractor.py first to extract images.")
            sys.exit(1)
        
        print("📋 Available PDFs with extracted images:\n")
        for i, mf in enumerate(metadata_files, 1):
            # Extract PDF name from filename
            name = mf.stem.replace("metadata (", "").replace(")", "")
            print(f"   {i}. {name}")
        
        print(f"\nUsage: python ocr_extractor.py <pdf_name>")
        print(f"Example: python ocr_extractor.py AutomobileGear")
        sys.exit(0)
    
    # Run OCR extraction
    try:
        extractor.run_ocr()
    except FileNotFoundError as e:
        print(f"❌ Error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
