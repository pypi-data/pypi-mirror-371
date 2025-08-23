# Corte

A tool to cut PDFs into pieces and process them with LLMs in batches.

## Features

- Split PDFs into manageable chunks
- Process chunks with various LLM providers (OpenAI, Anthropic, LangChain models)
- Support for local models via Ollama and cloud providers via LangChain
- Batch processing with configurable concurrency
- Rate limiting for API calls
- Command-line interface
- Combine results from multiple chunks

## Installation

```bash
# Basic installation
pip install corte

# With LangChain support for additional providers
pip install corte[langchain]

# Full installation with all optional dependencies
pip install corte[all]
```

## Usage

### Command Line Interface

#### Split a PDF into chunks
```bash
corte split document.pdf --chunk-size 5 --output-dir ./chunks
```

#### Process a PDF with an LLM
```bash
# Using OpenAI directly
corte process document.pdf --provider openai --prompt "Summarize this content" --output results.json

# Using Anthropic via LangChain
corte process document.pdf --provider langchain_anthropic --model claude-3-opus-20240229 --prompt "Summarize this content" --output results.json

# Using local Ollama model
corte process document.pdf --provider ollama --model llama3 --prompt "Summarize this content" --output results.json

# Using Google Gemini via LangChain
corte process document.pdf --provider langchain_google --model gemini-1.5-pro --prompt "Summarize this content" --output results.json
```

#### Get PDF information
```bash
corte info document.pdf
```

#### List available providers
```bash
corte providers
```

#### Check LangChain integration status
```bash
corte langchain
```

### Python API

```python
from corte import PDFProcessor, LLMClientFactory, BatchProcessor

# Create processors
pdf_processor = PDFProcessor(chunk_size=5)

# Use direct OpenAI integration
llm_client = LLMClientFactory.create_client("openai")

# Or use LangChain providers
llm_client = LLMClientFactory.create_client("langchain_anthropic", model="claude-3-opus-20240229")

# Or use local Ollama model
llm_client = LLMClientFactory.create_client("ollama", model="llama3")

batch_processor = BatchProcessor(llm_client, pdf_processor)

# Process PDF
results = batch_processor.process_pdf_batch(
    pdf_path="document.pdf",
    prompt="Summarize this content"
)

# Combine results
combined_text = batch_processor.combine_results(results)
```

## Configuration

Set your API keys as environment variables:

```bash
# For direct integrations
export OPENAI_API_KEY="your-openai-key"
export ANTHROPIC_API_KEY="your-anthropic-key"

# For LangChain integrations (same keys work)
export GOOGLE_API_KEY="your-google-key"  # For Google Gemini

# Ollama runs locally, no API key needed
```

Or use a `.env` file in your project directory.

## Requirements

- Python 3.8+
- PyPDF2 for PDF processing
- OpenAI Python client
- Anthropic Python client
- Click for CLI interface
- LangChain (optional, for additional provider support)

### LangChain Providers

When you install `corte[langchain]`, you get access to:

- **langchain_openai**: OpenAI models via LangChain (alternative to direct integration)
- **langchain_anthropic**: Anthropic Claude models via LangChain
- **langchain_google**: Google Gemini models
- **ollama**: Local models via Ollama (requires Ollama to be running)

## License

MIT License