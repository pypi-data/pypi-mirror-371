"""
Cutter - A tool to cut PDFs into pieces and process them with LLMs in batches.
"""

__version__ = "0.1.0"
__author__ = "Your Name"
__email__ = "your.email@example.com"

from .pdf_processor import PDFProcessor
from .llm_client import LLMClient
from .batch_processor import BatchProcessor

__all__ = ["PDFProcessor", "LLMClient", "BatchProcessor"]