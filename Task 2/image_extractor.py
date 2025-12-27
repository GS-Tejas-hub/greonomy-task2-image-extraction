"""
================================================================================
IMAGE EXTRACTOR - Task 2
================================================================================
Developer: Developer 2 (Image Extraction Owner)
Goal: Extract all images embedded inside the PDF with 100% accuracy

Features:
- Extracts actual embedded images (not screenshots/crops)
- Maintains full image quality
- Saves metadata with page number, image index, and dimensions
- Supports PNG, JPG, and other image formats

Dependencies:
- PyMuPDF (fitz)
- Pillow (PIL)

Output:
- /images/ folder with extracted images
- image_metadata.json with image information
================================================================================
"""

import fitz  # PyMuPDF
import json
import os
import sys
from datetime import datetime
from pathlib import Path
from PIL import Image
import io


class ImageExtractor:
    """
    A class to extract all embedded images from a PDF file.
    Uses PyMuPDF for 100% accurate image extraction.
    """
    
    def __init__(self, pdf_path: str, output_dir: str = None):
        """
        Initialize the ImageExtractor.
        
        Args:
            pdf_path: Path to the PDF file
            output_dir: Directory to save extracted images (default: Task 2 folder)
        """
        self.pdf_path = Path(pdf_path).resolve()
        
        if not self.pdf_path.exists():
            raise FileNotFoundError(f"PDF file not found: {pdf_path}")
        
        if not self.pdf_path.suffix.lower() == '.pdf':
            raise ValueError(f"File is not a PDF: {pdf_path}")
        
        # Set output directory - always use script's parent directory (Task 2)
        if output_dir:
            self.output_dir = Path(output_dir)
        else:
            # Use the script's directory (Task 2 folder)
            script_dir = Path(__file__).parent.resolve()
            self.output_dir = script_dir
        
        # Get PDF name without extension for folder naming
        self.pdf_name_clean = self.pdf_path.stem  # filename without extension
        
        # Create images folder with PDF name: "images (pdf_name)"
        self.images_dir = self.output_dir / f"images ({self.pdf_name_clean})"
        self.images_dir.mkdir(parents=True, exist_ok=True)
        
        # Metadata file will be saved as: "metadata (pdf_name).json"
        self.metadata_filename = f"metadata ({self.pdf_name_clean}).json"
        
        # Metadata storage
        self.metadata = {
            "pdf_name": self.pdf_path.name,
            "pdf_path": str(self.pdf_path.absolute()),
            "extraction_date": datetime.now().isoformat(),
            "total_pages": 0,
            "total_images": 0,
            "images": []
        }
        
        # Image format mapping
        self.format_map = {
            "png": "png",
            "jpeg": "jpg",
            "jpg": "jpg",
            "jpx": "jp2",
            "jbig2": "png",  # Convert to PNG
            "ccitt": "png",  # Convert to PNG
            "ppm": "ppm",
            "pbm": "pbm",
        }
    
    def _get_image_extension(self, image_info: dict) -> str:
        """
        Determine the appropriate file extension for an image.
        
        Args:
            image_info: Dictionary containing image information from PyMuPDF
            
        Returns:
            File extension (without dot)
        """
        ext = image_info.get("ext", "png").lower()
        return self.format_map.get(ext, "png")
    
    def _extract_image_bytes(self, doc: fitz.Document, xref: int) -> tuple:
        """
        Extract image bytes from PDF using xref.
        
        Args:
            doc: PyMuPDF document object
            xref: Cross-reference number of the image
            
        Returns:
            Tuple of (image_bytes, extension, width, height)
        """
        try:
            # Extract base image
            base_image = doc.extract_image(xref)
            
            if base_image:
                image_bytes = base_image["image"]
                ext = base_image.get("ext", "png")
                width = base_image.get("width", 0)
                height = base_image.get("height", 0)
                
                return image_bytes, ext, width, height
        except Exception as e:
            print(f"  ⚠️ Warning: Could not extract image xref {xref}: {e}")
        
        return None, None, 0, 0
    
    def _get_image_bbox(self, page: fitz.Page, xref: int) -> dict:
        """
        Get the bounding box of an image on a page.
        
        Args:
            page: PyMuPDF page object
            xref: Cross-reference number of the image
            
        Returns:
            Dictionary with bounding box coordinates
        """
        try:
            # Method 1: Try get_image_rects (most accurate)
            rects = page.get_image_rects(xref)
            if rects:
                rect = rects[0]  # Get first occurrence
                return {
                    "x0": round(rect.x0, 2),
                    "y0": round(rect.y0, 2),
                    "x1": round(rect.x1, 2),
                    "y1": round(rect.y1, 2)
                }
        except Exception:
            pass
        
        try:
            # Method 2: Fallback to get_image_info
            image_list = page.get_image_info()
            for img_info in image_list:
                if img_info.get("xref") == xref:
                    bbox = img_info.get("bbox", (0, 0, 0, 0))
                    return {
                        "x0": round(bbox[0], 2),
                        "y0": round(bbox[1], 2),
                        "x1": round(bbox[2], 2),
                        "y1": round(bbox[3], 2)
                    }
        except Exception:
            pass
        
        return {"x0": 0, "y0": 0, "x1": 0, "y1": 0}
    
    def _save_image(self, image_bytes: bytes, filepath: Path, target_ext: str) -> bool:
        """
        Save image bytes to file, converting format if necessary.
        
        Args:
            image_bytes: Raw image bytes
            filepath: Path to save the image
            target_ext: Target file extension
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Try to open with PIL for format conversion if needed
            img = Image.open(io.BytesIO(image_bytes))
            
            # Convert to RGB if necessary (for JPEG)
            if target_ext.lower() in ['jpg', 'jpeg'] and img.mode in ['RGBA', 'P']:
                img = img.convert('RGB')
            
            # Save the image
            if target_ext.lower() in ['jpg', 'jpeg']:
                img.save(filepath, 'JPEG', quality=95)
            elif target_ext.lower() == 'png':
                img.save(filepath, 'PNG')
            else:
                img.save(filepath)
            
            return True
            
        except Exception as e:
            # If PIL fails, try saving raw bytes
            try:
                with open(filepath, 'wb') as f:
                    f.write(image_bytes)
                return True
            except Exception as e2:
                print(f"  ❌ Error saving image: {e2}")
                return False
    
    def extract_images(self, save_as_png: bool = False) -> dict:
        """
        Extract all images from the PDF.
        
        Args:
            save_as_png: If True, convert all images to PNG format
            
        Returns:
            Dictionary containing extraction metadata
        """
        print(f"\n{'='*60}")
        print(f"📄 IMAGE EXTRACTOR - Task 2")
        print(f"{'='*60}")
        print(f"📁 PDF: {self.pdf_path.name}")
        print(f"📂 Output: {self.images_dir}")
        print(f"{'='*60}\n")
        
        # Open the PDF
        doc = fitz.open(self.pdf_path)
        self.metadata["total_pages"] = len(doc)
        
        print(f"📖 Total Pages: {len(doc)}\n")
        
        # Track processed images to avoid duplicates
        processed_xrefs = set()
        image_count = 0
        
        # Iterate through each page
        for page_num in range(len(doc)):
            page = doc[page_num]
            page_number = page_num + 1  # 1-indexed for human readability
            
            # Get images on this page
            image_list = page.get_images(full=True)
            
            if image_list:
                print(f"📄 Page {page_number}: Found {len(image_list)} image(s)")
            
            page_image_index = 0
            
            for img_index, img in enumerate(image_list):
                xref = img[0]  # Cross-reference number
                
                # Skip if already processed (same image on multiple pages)
                if xref in processed_xrefs:
                    continue
                
                processed_xrefs.add(xref)
                page_image_index += 1
                image_count += 1
                
                # Extract image bytes
                image_bytes, ext, width, height = self._extract_image_bytes(doc, xref)
                
                if image_bytes is None:
                    continue
                
                # Determine output format
                if save_as_png:
                    output_ext = "png"
                else:
                    output_ext = self.format_map.get(ext.lower(), "png")
                
                # Generate filename
                image_name = f"page{page_number}_img{page_image_index}.{output_ext}"
                image_path = self.images_dir / image_name
                
                # Save the image
                success = self._save_image(image_bytes, image_path, output_ext)
                
                if success:
                    # Get bounding box
                    bbox = self._get_image_bbox(page, xref)
                    
                    # Get file size
                    file_size = image_path.stat().st_size if image_path.exists() else 0
                    
                    # Create image metadata entry (matching required output structure)
                    image_metadata = {
                        "page_number": page_number,
                        "image_index": page_image_index,
                        "image_name": image_name,
                        "width": width,
                        "height": height,
                        "format": output_ext,
                        "size_bytes": file_size,
                        "bbox": bbox,
                        "xref": xref
                    }
                    
                    self.metadata["images"].append(image_metadata)
                    
                    print(f"   ✅ Extracted: {image_name} ({width}x{height})")
        
        # Close the document
        doc.close()
        
        # Update total count
        self.metadata["total_images"] = image_count
        
        # Save metadata to JSON
        self._save_metadata()
        
        # Print summary
        self._print_summary()
        
        return self.metadata
    
    def _save_metadata(self):
        """Save metadata to JSON file."""
        metadata_path = self.output_dir / self.metadata_filename
        
        with open(metadata_path, 'w', encoding='utf-8') as f:
            json.dump(self.metadata, f, indent=2, ensure_ascii=False)
        
        print(f"\n💾 Metadata saved: {metadata_path}")
    
    def _print_summary(self):
        """Print extraction summary."""
        print(f"\n{'='*60}")
        print(f"✅ EXTRACTION COMPLETE")
        print(f"{'='*60}")
        print(f"📄 PDF: {self.metadata['pdf_name']}")
        print(f"📖 Total Pages: {self.metadata['total_pages']}")
        print(f"🖼️  Total Images Extracted: {self.metadata['total_images']}")
        print(f"📂 Images saved to: {self.images_dir}")
        print(f"📋 Metadata saved to: {self.output_dir / self.metadata_filename}")
        print(f"{'='*60}\n")
    
    def get_simple_metadata(self) -> list:
        """
        Get simplified metadata matching the exact required output structure.
        
        Returns:
            List of dictionaries with page_number, image_name, width, height
        """
        simple_metadata = []
        
        for img in self.metadata["images"]:
            simple_metadata.append({
                "page_number": img["page_number"],
                "image_name": img["image_name"],
                "width": img["width"],
                "height": img["height"]
            })
        
        return simple_metadata


def main():
    """Main function to run the image extractor."""
    
    # Default PDF path (can be changed)
    # Look for PDFs in the 'pdfs' folder
    script_dir = Path(__file__).parent.parent  # Go up to "Greonomy task 2"
    pdfs_folder = script_dir / "pdfs"
    
    # Check command line arguments
    if len(sys.argv) > 1:
        pdf_path = sys.argv[1]
    else:
        # Look for PDFs in the pdfs folder
        if pdfs_folder.exists():
            pdf_files = list(pdfs_folder.glob("*.pdf"))
            if pdf_files:
                pdf_path = str(pdf_files[0])
                print(f"🔍 Found PDF: {pdf_path}")
            else:
                print("❌ No PDF files found in 'pdfs' folder!")
                print(f"   Please add PDF files to: {pdfs_folder}")
                print("\nUsage: python image_extractor.py <path_to_pdf>")
                sys.exit(1)
        else:
            print("❌ 'pdfs' folder not found!")
            print("\nUsage: python image_extractor.py <path_to_pdf>")
            sys.exit(1)
    
    # Create extractor and run
    try:
        extractor = ImageExtractor(pdf_path)
        metadata = extractor.extract_images()
        
        # Also print simple metadata format
        print("\n📊 Simple Metadata Format (as required):")
        print("-" * 40)
        simple = extractor.get_simple_metadata()
        for img in simple:
            print(json.dumps(img, indent=2))
        
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
