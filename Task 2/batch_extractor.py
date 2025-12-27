"""
================================================================================
BATCH IMAGE EXTRACTOR - Task 2
================================================================================
Process multiple PDFs from the pdfs folder and extract all images.
Creates organized output with per-PDF folders and consolidated metadata.
================================================================================
"""

import json
import sys
from pathlib import Path
from datetime import datetime
from image_extractor import ImageExtractor


def process_all_pdfs():
    """Process all PDFs in the pdfs folder."""
    
    # Get paths
    script_dir = Path(__file__).parent.resolve()
    project_dir = script_dir.parent
    pdfs_folder = project_dir / "pdfs"
    
    print(f"\n{'='*60}")
    print(f"📁 BATCH IMAGE EXTRACTOR - Task 2")
    print(f"{'='*60}")
    print(f"📂 PDFs folder: {pdfs_folder}")
    print(f"{'='*60}\n")
    
    # Find all PDFs
    if not pdfs_folder.exists():
        print(f"❌ PDFs folder not found: {pdfs_folder}")
        return
    
    pdf_files = list(pdfs_folder.glob("*.pdf"))
    
    if not pdf_files:
        print(f"❌ No PDF files found in: {pdfs_folder}")
        return
    
    print(f"📄 Found {len(pdf_files)} PDF(s):\n")
    for pdf in pdf_files:
        print(f"   • {pdf.name}")
    
    # Process each PDF
    all_metadata = {
        "extraction_date": datetime.now().isoformat(),
        "total_pdfs": len(pdf_files),
        "total_images": 0,
        "pdfs": []
    }
    
    for pdf_path in pdf_files:
        print(f"\n{'='*60}")
        print(f"🔄 Processing: {pdf_path.name}")
        print(f"{'='*60}")
        
        try:
            # Create extractor - it will automatically create the correct folder structure
            # images (pdf_name)/ and metadata (pdf_name).json
            extractor = ImageExtractor(str(pdf_path))
            
            # Extract images
            metadata = extractor.extract_images()
            
            # Add to consolidated metadata
            all_metadata["pdfs"].append(metadata)
            all_metadata["total_images"] += metadata["total_images"]
            
        except Exception as e:
            print(f"❌ Error processing {pdf_path.name}: {e}")
            import traceback
            traceback.print_exc()
    
    # Save consolidated metadata
    consolidated_path = script_dir / "all_images_metadata.json"
    with open(consolidated_path, 'w', encoding='utf-8') as f:
        json.dump(all_metadata, f, indent=2, ensure_ascii=False)
    
    # Print summary
    print(f"\n{'='*60}")
    print(f"✅ BATCH EXTRACTION COMPLETE")
    print(f"{'='*60}")
    print(f"📄 PDFs Processed: {all_metadata['total_pdfs']}")
    print(f"🖼️  Total Images: {all_metadata['total_images']}")
    print(f"📋 Consolidated Metadata: {consolidated_path}")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    process_all_pdfs()
