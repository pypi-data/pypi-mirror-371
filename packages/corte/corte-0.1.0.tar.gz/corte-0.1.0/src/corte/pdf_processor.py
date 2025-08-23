"""PDF processing functionality for splitting and extracting content."""

from typing import List, Optional, Tuple
import PyPDF2
from pathlib import Path


class PDFProcessor:
    """Handles PDF splitting and content extraction."""
    
    def __init__(self, chunk_size: int = 5):
        """
        Initialize PDF processor.
        
        Args:
            chunk_size: Number of pages per chunk
        """
        self.chunk_size = chunk_size
    
    def split_pdf(self, pdf_path: Path, output_dir: Optional[Path] = None) -> List[Path]:
        """
        Split PDF into chunks.
        
        Args:
            pdf_path: Path to input PDF file
            output_dir: Directory to save chunks (defaults to same as input)
            
        Returns:
            List of paths to created chunk files
        """
        if output_dir is None:
            output_dir = pdf_path.parent
        
        output_dir.mkdir(exist_ok=True)
        chunk_paths = []
        
        with open(pdf_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            total_pages = len(reader.pages)
            
            for start_page in range(0, total_pages, self.chunk_size):
                end_page = min(start_page + self.chunk_size, total_pages)
                
                writer = PyPDF2.PdfWriter()
                for page_num in range(start_page, end_page):
                    writer.add_page(reader.pages[page_num])
                
                chunk_filename = f"{pdf_path.stem}_chunk_{start_page+1}-{end_page}.pdf"
                chunk_path = output_dir / chunk_filename
                
                with open(chunk_path, 'wb') as output_file:
                    writer.write(output_file)
                
                chunk_paths.append(chunk_path)
        
        return chunk_paths
    
    def extract_text(self, pdf_path: Path) -> str:
        """
        Extract text content from PDF.
        
        Args:
            pdf_path: Path to PDF file
            
        Returns:
            Extracted text content
        """
        text_content = ""
        
        with open(pdf_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            
            for page in reader.pages:
                text_content += page.extract_text() + "\n"
        
        return text_content.strip()
    
    def get_pdf_info(self, pdf_path: Path) -> dict:
        """
        Get basic information about PDF.
        
        Args:
            pdf_path: Path to PDF file
            
        Returns:
            Dictionary with PDF metadata
        """
        with open(pdf_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            
            return {
                "pages": len(reader.pages),
                "title": reader.metadata.title if reader.metadata else None,
                "author": reader.metadata.author if reader.metadata else None,
                "subject": reader.metadata.subject if reader.metadata else None,
                "creator": reader.metadata.creator if reader.metadata else None,
            }