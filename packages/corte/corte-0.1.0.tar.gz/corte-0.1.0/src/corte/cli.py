"""Command-line interface for the corte package."""

import click
from pathlib import Path
from typing import Optional
import json

from .pdf_processor import PDFProcessor
from .llm_client import LLMClientFactory
from .batch_processor import BatchProcessor


@click.group()
@click.version_option(version="0.1.0")
def cli():
    """Corte - Cut PDFs into pieces and process them with LLMs in batches."""
    pass


@cli.command()
@click.argument('pdf_path', type=click.Path(exists=True, path_type=Path))
@click.option('--chunk-size', '-c', default=5, help='Number of pages per chunk')
@click.option('--output-dir', '-o', type=click.Path(path_type=Path), help='Output directory for chunks')
def split(pdf_path: Path, chunk_size: int, output_dir: Optional[Path]):
    """Split a PDF into chunks."""
    processor = PDFProcessor(chunk_size=chunk_size)
    
    if output_dir:
        output_dir.mkdir(parents=True, exist_ok=True)
    
    chunk_paths = processor.split_pdf(pdf_path, output_dir)
    
    click.echo(f"Split {pdf_path} into {len(chunk_paths)} chunks:")
    for chunk_path in chunk_paths:
        click.echo(f"  {chunk_path}")


@cli.command()
@click.argument('pdf_path', type=click.Path(exists=True, path_type=Path))
@click.option('--provider', '-p', required=True, 
              help='LLM provider to use (openai, anthropic, langchain_openai, langchain_anthropic, langchain_google, ollama)')
@click.option('--model', '-m', help='Model name (optional)')
@click.option('--prompt', required=True, help='Processing prompt for the LLM')
@click.option('--chunk-size', '-c', default=5, help='Number of pages per chunk')
@click.option('--output', '-o', type=click.Path(path_type=Path), 
              help='Output file for results (JSON format)')
@click.option('--max-workers', default=3, help='Maximum concurrent workers')
@click.option('--delay', default=1.0, help='Delay between requests (seconds)')
@click.option('--combine', is_flag=True, help='Combine results into single text file')
def process(
    pdf_path: Path,
    provider: str,
    model: Optional[str],
    prompt: str,
    chunk_size: int,
    output: Optional[Path],
    max_workers: int,
    delay: float,
    combine: bool
):
    """Process a PDF with an LLM by splitting into chunks."""
    
    # Create LLM client
    client_kwargs = {}
    if model:
        client_kwargs['model'] = model
    
    try:
        llm_client = LLMClientFactory.create_client(provider, **client_kwargs)
    except Exception as e:
        click.echo(f"Error creating LLM client: {e}", err=True)
        return
    
    # Create processors
    pdf_processor = PDFProcessor(chunk_size=chunk_size)
    batch_processor = BatchProcessor(
        llm_client=llm_client,
        pdf_processor=pdf_processor,
        max_workers=max_workers,
        delay_between_requests=delay
    )
    
    # Progress callback
    def progress_callback(completed: int, total: int):
        click.echo(f"Progress: {completed}/{total} chunks processed")
    
    click.echo(f"Processing {pdf_path} with {provider}...")
    click.echo(f"Chunk size: {chunk_size} pages")
    click.echo(f"Prompt: {prompt}")
    
    try:
        # Process PDF
        results = batch_processor.process_pdf_batch(
            pdf_path=pdf_path,
            prompt=prompt,
            progress_callback=progress_callback
        )
        
        # Display summary
        successful = sum(1 for r in results if r.success)
        failed = len(results) - successful
        total_time = sum(r.processing_time for r in results)
        
        click.echo(f"\nProcessing complete!")
        click.echo(f"Successful: {successful}")
        click.echo(f"Failed: {failed}")
        click.echo(f"Total processing time: {total_time:.2f} seconds")
        
        # Save results
        if output:
            if combine:
                # Save combined text
                combined_text = batch_processor.combine_results(results)
                output_text_path = output.with_suffix('.txt')
                with open(output_text_path, 'w', encoding='utf-8') as f:
                    f.write(combined_text)
                click.echo(f"Combined results saved to: {output_text_path}")
            
            # Save detailed JSON results
            batch_processor.save_results(results, output)
            click.echo(f"Detailed results saved to: {output}")
        
        # Display any errors
        if failed > 0:
            click.echo("\nErrors encountered:")
            for result in results:
                if not result.success:
                    click.echo(f"  {result.chunk_path}: {result.error}")
    
    except Exception as e:
        click.echo(f"Error during processing: {e}", err=True)


@cli.command()
@click.argument('pdf_path', type=click.Path(exists=True, path_type=Path))
def info(pdf_path: Path):
    """Display information about a PDF file."""
    processor = PDFProcessor()
    
    try:
        pdf_info = processor.get_pdf_info(pdf_path)
        
        click.echo(f"PDF Information for: {pdf_path}")
        click.echo(f"Pages: {pdf_info['pages']}")
        click.echo(f"Title: {pdf_info['title'] or 'N/A'}")
        click.echo(f"Author: {pdf_info['author'] or 'N/A'}")
        click.echo(f"Subject: {pdf_info['subject'] or 'N/A'}")
        click.echo(f"Creator: {pdf_info['creator'] or 'N/A'}")
        
    except Exception as e:
        click.echo(f"Error reading PDF: {e}", err=True)


@cli.command()
def providers():
    """List available LLM providers."""
    available = LLMClientFactory.get_available_providers()
    langchain_status = LLMClientFactory.get_langchain_status()
    
    click.echo("Available LLM providers:")
    
    # Direct providers
    direct_providers = ["openai", "anthropic"]
    click.echo("\nDirect integrations:")
    for provider in direct_providers:
        if provider in available:
            click.echo(f"  ✓ {provider}")
    
    # LangChain providers
    click.echo(f"\nLangChain integrations (LangChain available: {'✓' if langchain_status['available'] else '✗'}):")
    if langchain_status['available']:
        for provider in langchain_status['providers']:
            click.echo(f"  ✓ {provider}")
    else:
        click.echo(f"  Install LangChain to enable these providers:")
        for provider in langchain_status['providers']:
            click.echo(f"    - {provider}")
        click.echo(f"\n  Installation command:")
        click.echo(f"    {langchain_status['installation_command']}")


@cli.command()
def langchain():
    """Show LangChain integration status and information."""
    status = LLMClientFactory.get_langchain_status()
    
    click.echo("LangChain Integration Status")
    click.echo("=" * 30)
    
    if status['available']:
        click.echo("✓ LangChain is installed and available")
        click.echo(f"\nSupported LangChain providers:")
        for provider in status['providers']:
            click.echo(f"  • {provider}")
        
        click.echo(f"\nExample usage:")
        click.echo(f"  # Use OpenAI via LangChain")
        click.echo(f"  corte process doc.pdf -p langchain_openai -m gpt-4 --prompt 'Summarize this'")
        click.echo(f"  ")
        click.echo(f"  # Use local Ollama model")
        click.echo(f"  corte process doc.pdf -p ollama -m llama2 --prompt 'Extract key points'")
        
    else:
        click.echo("✗ LangChain is not installed")
        click.echo(f"\nTo enable LangChain support, run:")
        click.echo(f"  {status['installation_command']}")
        click.echo(f"\nThis will add support for:")
        for provider in status['providers']:
            click.echo(f"  • {provider}")


def main():
    """Entry point for the CLI."""
    cli()


if __name__ == '__main__':
    main()