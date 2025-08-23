"""Batch processing functionality for handling multiple PDF chunks with LLMs."""

from typing import List, Dict, Optional, Callable
from pathlib import Path
import json
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass

from .pdf_processor import PDFProcessor
from .llm_client import LLMClient, LLMClientFactory


@dataclass
class ProcessingResult:
    """Result of processing a single PDF chunk."""
    chunk_path: Path
    original_text: str
    processed_text: str
    success: bool
    error: Optional[str] = None
    processing_time: float = 0.0


class BatchProcessor:
    """Handles batch processing of PDF chunks with LLMs."""
    
    def __init__(
        self,
        llm_client: LLMClient,
        pdf_processor: Optional[PDFProcessor] = None,
        max_workers: int = 3,
        delay_between_requests: float = 1.0
    ):
        """
        Initialize batch processor.
        
        Args:
            llm_client: LLM client for processing
            pdf_processor: PDF processor instance
            max_workers: Maximum number of concurrent workers
            delay_between_requests: Delay between LLM requests (rate limiting)
        """
        self.llm_client = llm_client
        self.pdf_processor = pdf_processor or PDFProcessor()
        self.max_workers = max_workers
        self.delay_between_requests = delay_between_requests
    
    def process_pdf_batch(
        self,
        pdf_path: Path,
        prompt: str,
        output_dir: Optional[Path] = None,
        progress_callback: Optional[Callable[[int, int], None]] = None
    ) -> List[ProcessingResult]:
        """
        Process entire PDF by splitting into chunks and processing each with LLM.
        
        Args:
            pdf_path: Path to input PDF
            prompt: Processing prompt for LLM
            output_dir: Directory for temporary chunks
            progress_callback: Optional callback for progress updates
            
        Returns:
            List of processing results for each chunk
        """
        # Split PDF into chunks
        chunk_paths = self.pdf_processor.split_pdf(pdf_path, output_dir)
        
        # Process chunks in batch
        results = self.process_chunks(chunk_paths, prompt, progress_callback)
        
        # Clean up chunk files
        for chunk_path in chunk_paths:
            chunk_path.unlink(missing_ok=True)
        
        return results
    
    def process_chunks(
        self,
        chunk_paths: List[Path],
        prompt: str,
        progress_callback: Optional[Callable[[int, int], None]] = None
    ) -> List[ProcessingResult]:
        """
        Process list of PDF chunks with LLM.
        
        Args:
            chunk_paths: List of PDF chunk file paths
            prompt: Processing prompt for LLM
            progress_callback: Optional callback for progress updates
            
        Returns:
            List of processing results
        """
        results = []
        completed = 0
        total = len(chunk_paths)
        
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Submit all tasks
            future_to_chunk = {
                executor.submit(self._process_single_chunk, chunk_path, prompt): chunk_path
                for chunk_path in chunk_paths
            }
            
            # Process completed tasks
            for future in as_completed(future_to_chunk):
                chunk_path = future_to_chunk[future]
                try:
                    result = future.result()
                    results.append(result)
                except Exception as e:
                    results.append(ProcessingResult(
                        chunk_path=chunk_path,
                        original_text="",
                        processed_text="",
                        success=False,
                        error=str(e)
                    ))
                
                completed += 1
                if progress_callback:
                    progress_callback(completed, total)
                
                # Rate limiting
                if completed < total:
                    time.sleep(self.delay_between_requests)
        
        # Sort results by chunk path to maintain order
        results.sort(key=lambda r: str(r.chunk_path))
        return results
    
    def _process_single_chunk(self, chunk_path: Path, prompt: str) -> ProcessingResult:
        """
        Process a single PDF chunk.
        
        Args:
            chunk_path: Path to PDF chunk
            prompt: Processing prompt
            
        Returns:
            Processing result
        """
        start_time = time.time()
        
        try:
            # Extract text from chunk
            original_text = self.pdf_processor.extract_text(chunk_path)
            
            if not original_text.strip():
                return ProcessingResult(
                    chunk_path=chunk_path,
                    original_text=original_text,
                    processed_text="",
                    success=False,
                    error="No text content found in chunk",
                    processing_time=time.time() - start_time
                )
            
            # Process with LLM
            processed_text = self.llm_client.process_text(original_text, prompt)
            
            return ProcessingResult(
                chunk_path=chunk_path,
                original_text=original_text,
                processed_text=processed_text,
                success=True,
                processing_time=time.time() - start_time
            )
            
        except Exception as e:
            return ProcessingResult(
                chunk_path=chunk_path,
                original_text="",
                processed_text="",
                success=False,
                error=str(e),
                processing_time=time.time() - start_time
            )
    
    def save_results(self, results: List[ProcessingResult], output_path: Path) -> None:
        """
        Save processing results to JSON file.
        
        Args:
            results: List of processing results
            output_path: Path to output JSON file
        """
        serializable_results = []
        for result in results:
            serializable_results.append({
                "chunk_path": str(result.chunk_path),
                "original_text": result.original_text,
                "processed_text": result.processed_text,
                "success": result.success,
                "error": result.error,
                "processing_time": result.processing_time
            })
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(serializable_results, f, indent=2, ensure_ascii=False)
    
    def combine_results(self, results: List[ProcessingResult]) -> str:
        """
        Combine processed text from all successful results.
        
        Args:
            results: List of processing results
            
        Returns:
            Combined processed text
        """
        combined_text = []
        for result in results:
            if result.success and result.processed_text:
                combined_text.append(result.processed_text)
        
        return "\n\n".join(combined_text)