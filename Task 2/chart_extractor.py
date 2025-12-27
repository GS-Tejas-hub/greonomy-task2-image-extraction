"""
================================================================================
CHART/GRAPH EXTRACTOR - Task 2
================================================================================
Developer: Developer 2 (Image Extraction Owner)
Goal: Extract charts, graphs, diagrams that are vector graphics (not embedded images)

How it works:
- Renders PDF pages as high-resolution images
- Detects pages that contain charts/graphs (pages with vector content)
- Saves rendered page images in 'charts (pdf_name)/' folder

Dependencies:
- PyMuPDF (fitz)
- Pillow

Output:
- charts (pdf_name)/ folder with rendered chart images
- charts_metadata (pdf_name).json with metadata
================================================================================
"""

import fitz  # PyMuPDF
import json
import sys
from pathlib import Path
from datetime import datetime
from PIL import Image
import io


class ChartExtractor:
    """
    Extract charts, graphs, and diagrams from PDFs.
    These are vector graphics that aren't detected as embedded images.
    """
    
    def __init__(self, pdf_path: str, dpi: int = 150):
        """
        Initialize the Chart Extractor.
        
        Args:
            pdf_path: Path to the PDF file
            dpi: Resolution for rendering (higher = better quality, larger files)
        """
        self.pdf_path = Path(pdf_path).resolve()
        self.dpi = dpi
        self.zoom = dpi / 72  # PDF default is 72 DPI
        
        if not self.pdf_path.exists():
            raise FileNotFoundError(f"PDF file not found: {pdf_path}")
        
        if not self.pdf_path.suffix.lower() == '.pdf':
            raise ValueError(f"File is not a PDF: {pdf_path}")
        
        # Get PDF name without extension
        self.pdf_name = self.pdf_path.stem
        
        # Set output directory (same as script location)
        self.script_dir = Path(__file__).parent.resolve()
        
        # Create charts folder with PDF name
        self.charts_dir = self.script_dir / f"charts ({self.pdf_name})"
        self.charts_dir.mkdir(parents=True, exist_ok=True)
        
        # Metadata filename
        self.metadata_filename = f"charts_metadata ({self.pdf_name}).json"
        
        # Metadata storage
        self.metadata = {
            "pdf_name": self.pdf_path.name,
            "pdf_path": str(self.pdf_path),
            "extraction_date": datetime.now().isoformat(),
            "dpi": dpi,
            "total_pages": 0,
            "chart_pages": 0,
            "charts": []
        }
    
    def _has_vector_content(self, page) -> bool:
        """
        Check if a page has vector graphics (potential charts).
        Uses multiple heuristics to detect chart/graph pages.
        
        Args:
            page: PyMuPDF page object
            
        Returns:
            True if page likely contains charts/graphs
        """
        try:
            # Get page drawings (vector paths - lines, curves, shapes)
            drawings = page.get_drawings()
            
            # Get embedded images
            images = page.get_images()
            
            # Get text
            text = page.get_text()
            text_length = len(text)
            
            # Count drawing elements
            num_drawings = len(drawings)
            num_images = len(images)
            
            # Get page dimensions
            rect = page.rect
            page_area = rect.width * rect.height
            
            # Heuristic 1: Many vector drawings suggest charts
            # Charts typically have lots of lines, rectangles, paths
            many_drawings = num_drawings > 50
            
            # Heuristic 2: Check for chart keywords in text
            chart_keywords = [
                'chart', 'graph', 'figure', 'fig.', 'source:', 'note:',
                '%', 'growth', 'trend', 'forecast', 'projection',
                'fy', 'cy', 'q1', 'q2', 'q3', 'q4', 'yoy', 'cagr',
                '2020', '2021', '2022', '2023', '2024', '2025',
                'mn', 'bn', 'cr', 'lakh', 'million', 'billion',
                'units', 'rs', 'inr', 'usd', '$', '₹'
            ]
            text_lower = text.lower()
            has_chart_keywords = sum(1 for kw in chart_keywords if kw in text_lower) >= 3
            
            # Heuristic 3: Moderate text with many drawings = likely chart page
            # Full text pages have high text density, pure image pages have low
            text_density = text_length / page_area if page_area > 0 else 0
            moderate_text = 0.05 < text_density < 0.5
            
            # Heuristic 4: Drawing density
            drawing_density = num_drawings / (page_area / 10000) if page_area > 0 else 0
            high_drawing_density = drawing_density > 5
            
            # Decision logic
            is_chart_page = (
                (many_drawings and has_chart_keywords) or
                (many_drawings and moderate_text and num_images == 0) or
                (high_drawing_density and has_chart_keywords) or
                (num_drawings > 100)  # Very many drawings = definitely has graphics
            )
            
            return is_chart_page
            
        except Exception as e:
            # If analysis fails, skip this page
            return False
    
    def _find_chart_regions(self, page) -> list:
        """
        Find bounding boxes of chart regions on a page.
        Uses vector drawing clusters to identify chart areas.
        
        Args:
            page: PyMuPDF page object
            
        Returns:
            List of fitz.Rect objects representing chart regions
        """
        drawings = page.get_drawings()
        
        if not drawings:
            return []
        
        # Collect all drawing coordinates
        all_rects = []
        for d in drawings:
            if "rect" in d:
                all_rects.append(fitz.Rect(d["rect"]))
            elif "items" in d:
                for item in d["items"]:
                    if len(item) >= 2 and hasattr(item[1], '__iter__'):
                        try:
                            # Try to create rect from points
                            points = item[1]
                            if len(points) >= 2:
                                x_coords = [p.x if hasattr(p, 'x') else p[0] for p in points if hasattr(p, 'x') or (isinstance(p, (list, tuple)) and len(p) >= 2)]
                                y_coords = [p.y if hasattr(p, 'y') else p[1] for p in points if hasattr(p, 'y') or (isinstance(p, (list, tuple)) and len(p) >= 2)]
                                if x_coords and y_coords:
                                    all_rects.append(fitz.Rect(min(x_coords), min(y_coords), max(x_coords), max(y_coords)))
                        except:
                            pass
        
        if not all_rects:
            return []
        
        # Find clusters of drawings (chart regions)
        # Merge overlapping or nearby rectangles
        page_rect = page.rect
        margin = 10  # Points margin
        
        # Calculate overall bounding box of all drawings
        combined = all_rects[0]
        for r in all_rects[1:]:
            combined = combined | r  # Union of rectangles
        
        # Expand slightly for padding
        combined.x0 = max(0, combined.x0 - margin)
        combined.y0 = max(0, combined.y0 - margin)
        combined.x1 = min(page_rect.x1, combined.x1 + margin)
        combined.y1 = min(page_rect.y1, combined.y1 + margin)
        
        # If the region is too small or too large relative to page, return page-level crop
        region_area = combined.width * combined.height
        page_area = page_rect.width * page_rect.height
        
        if region_area < page_area * 0.05:  # Less than 5% - too small
            return []
        
        if region_area > page_area * 0.95:  # More than 95% - basically full page
            # Try to find a more specific region by excluding header/footer
            header_height = page_rect.height * 0.1
            footer_height = page_rect.height * 0.1
            content_rect = fitz.Rect(
                page_rect.x0, 
                page_rect.y0 + header_height,
                page_rect.x1,
                page_rect.y1 - footer_height
            )
            return [content_rect]
        
        return [combined]
    
    def _render_chart_region(self, page, page_num: int, region: fitz.Rect, chart_idx: int) -> tuple:
        """
        Render a specific region of a page as a cropped chart image.
        
        Args:
            page: PyMuPDF page object
            page_num: Page number (1-indexed)
            region: fitz.Rect of the chart region
            chart_idx: Chart index for naming
            
        Returns:
            Tuple of (image_path, width, height, size_bytes, image_name, bbox)
        """
        # Create transformation matrix for zoom
        mat = fitz.Matrix(self.zoom, self.zoom)
        
        # Render only the specified region (clip)
        pix = page.get_pixmap(matrix=mat, clip=region, alpha=False)
        
        # Convert to PIL Image
        img_data = pix.tobytes("png")
        img = Image.open(io.BytesIO(img_data))
        
        # Save image
        image_name = f"page{page_num}_chart{chart_idx}.png"
        image_path = self.charts_dir / image_name
        img.save(image_path, "PNG", optimize=True)
        
        # Get file size
        size_bytes = image_path.stat().st_size
        
        # Create bbox dict
        bbox = {
            "x0": round(region.x0, 2),
            "y0": round(region.y0, 2),
            "x1": round(region.x1, 2),
            "y1": round(region.y1, 2)
        }
        
        return str(image_path), pix.width, pix.height, size_bytes, image_name, bbox
    
    def _render_page(self, page, page_num: int) -> tuple:
        """
        Render a page as a high-resolution image (fallback for full page).
        
        Args:
            page: PyMuPDF page object
            page_num: Page number (1-indexed)
            
        Returns:
            Tuple of (image_path, width, height, size_bytes)
        """
        # Create transformation matrix for zoom
        mat = fitz.Matrix(self.zoom, self.zoom)
        
        # Render page to pixmap
        pix = page.get_pixmap(matrix=mat, alpha=False)
        
        # Convert to PIL Image
        img_data = pix.tobytes("png")
        img = Image.open(io.BytesIO(img_data))
        
        # Save image
        image_name = f"page{page_num}_chart.png"
        image_path = self.charts_dir / image_name
        img.save(image_path, "PNG", optimize=True)
        
        # Get file size
        size_bytes = image_path.stat().st_size
        
        return str(image_path), pix.width, pix.height, size_bytes, image_name
    
    def extract_charts(self, pages: list = None, force_all: bool = False) -> dict:
        """
        Extract charts from PDF pages.
        
        Args:
            pages: List of specific page numbers to extract (1-indexed)
                   If None, auto-detect pages with charts
            force_all: If True, extract all pages (not just chart pages)
            
        Returns:
            Metadata dictionary with chart information
        """
        print(f"\n{'='*60}")
        print(f"📊 CHART/GRAPH EXTRACTOR - Task 2")
        print(f"{'='*60}")
        print(f"📁 PDF: {self.pdf_path.name}")
        print(f"📂 Output: {self.charts_dir}")
        print(f"🔍 DPI: {self.dpi}")
        print(f"{'='*60}\n")
        
        # Open PDF
        doc = fitz.open(self.pdf_path)
        self.metadata["total_pages"] = len(doc)
        
        chart_count = 0
        
        for page_num in range(len(doc)):
            page = doc[page_num]
            page_number = page_num + 1  # 1-indexed
            
            # Determine if we should extract this page
            should_extract = False
            
            if pages:
                # User specified pages
                should_extract = page_number in pages
            elif force_all:
                # Extract all pages
                should_extract = True
            else:
                # Auto-detect: check for vector content
                should_extract = self._has_vector_content(page)
            
            if should_extract:
                print(f"📊 Analyzing page {page_number}...", end=" ")
                
                try:
                    # Find chart regions on this page
                    regions = self._find_chart_regions(page)
                    
                    if regions:
                        # Extract each chart region
                        for idx, region in enumerate(regions, 1):
                            image_path, width, height, size_bytes, image_name, bbox = self._render_chart_region(
                                page, page_number, region, idx
                            )
                            
                            chart_count += 1
                            
                            # Add to metadata
                            chart_info = {
                                "page_number": page_number,
                                "chart_index": chart_count,
                                "image_name": image_name,
                                "width": width,
                                "height": height,
                                "size_bytes": size_bytes,
                                "format": "png",
                                "bbox": bbox,
                                "cropped": True
                            }
                            self.metadata["charts"].append(chart_info)
                            
                            print(f"✅ Cropped chart saved as {image_name} ({width}x{height})")
                    else:
                        # Fallback: render full page if no specific regions found
                        image_path, width, height, size_bytes, image_name = self._render_page(page, page_number)
                        
                        chart_count += 1
                        
                        # Add to metadata
                        chart_info = {
                            "page_number": page_number,
                            "chart_index": chart_count,
                            "image_name": image_name,
                            "width": width,
                            "height": height,
                            "size_bytes": size_bytes,
                            "format": "png",
                            "cropped": False
                        }
                        self.metadata["charts"].append(chart_info)
                        
                        print(f"✅ Full page saved as {image_name} ({width}x{height})")
                    
                except Exception as e:
                    print(f"❌ Error: {e}")
        
        # Close document
        doc.close()
        
        # Update counts
        self.metadata["chart_pages"] = chart_count
        
        # Save metadata
        self._save_metadata()
        
        # Print summary
        self._print_summary()
        
        return self.metadata
    
    def _save_metadata(self):
        """Save chart metadata to JSON file."""
        metadata_path = self.script_dir / self.metadata_filename
        
        with open(metadata_path, 'w', encoding='utf-8') as f:
            json.dump(self.metadata, f, indent=2, ensure_ascii=False)
        
        print(f"\n💾 Metadata saved: {metadata_path}")
    
    def _print_summary(self):
        """Print extraction summary."""
        print(f"\n{'='*60}")
        print(f"✅ CHART EXTRACTION COMPLETE")
        print(f"{'='*60}")
        print(f"📄 PDF: {self.metadata['pdf_name']}")
        print(f"📖 Total Pages: {self.metadata['total_pages']}")
        print(f"📊 Charts Extracted: {self.metadata['chart_pages']}")
        print(f"📂 Saved to: {self.charts_dir}")
        print(f"📋 Metadata: {self.metadata_filename}")
        print(f"{'='*60}\n")


def main():
    """Main function to run chart extraction."""
    
    print(f"\n{'='*60}")
    print(f"📊 CHART/GRAPH EXTRACTOR - Task 2")
    print(f"{'='*60}\n")
    
    # Check command line arguments
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python chart_extractor.py <pdf_path> [options]")
        print("\nOptions:")
        print("  --pages 1,3,5,9    Extract specific pages (comma-separated)")
        print("  --all              Extract ALL pages (not just chart pages)")
        print("  --dpi 150          Set resolution (default: 150)")
        print("\nExamples:")
        print('  python chart_extractor.py "..\\pdfs\\Report.pdf"')
        print('  python chart_extractor.py "..\\pdfs\\Report.pdf" --pages 3,9,20')
        print('  python chart_extractor.py "..\\pdfs\\Report.pdf" --all --dpi 200')
        sys.exit(0)
    
    pdf_path = sys.argv[1]
    pages = None
    force_all = False
    dpi = 150
    
    # Parse additional arguments
    i = 2
    while i < len(sys.argv):
        arg = sys.argv[i]
        
        if arg == "--pages" and i + 1 < len(sys.argv):
            # Parse page numbers
            pages_str = sys.argv[i + 1]
            pages = [int(p.strip()) for p in pages_str.split(",")]
            i += 2
        elif arg == "--all":
            force_all = True
            i += 1
        elif arg == "--dpi" and i + 1 < len(sys.argv):
            dpi = int(sys.argv[i + 1])
            i += 2
        else:
            i += 1
    
    # Run extraction
    try:
        extractor = ChartExtractor(pdf_path, dpi=dpi)
        extractor.extract_charts(pages=pages, force_all=force_all)
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
