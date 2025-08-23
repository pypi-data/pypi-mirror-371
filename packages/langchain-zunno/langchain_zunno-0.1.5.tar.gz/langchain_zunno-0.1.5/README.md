# LangChain Zunno Integration

A LangChain integration for Zunno LLM and Embeddings, providing easy-to-use wrappers for text generation and embeddings.

## Installation

```bash
pip install langchain-zunno
```

## Quick Start

### Text Generation (LLM)

#### Basic Usage (Returns only response text)
```python
from langchain_zunno import ZunnoLLM

# Create an LLM instance
llm = ZunnoLLM(model_name="mistral:latest")

# Generate text
response = llm.invoke("Hello, how are you?")
print(response)
```

#### Full Response Mode (Returns complete API response)
```python
from langchain_zunno import ZunnoLLM

# Create an LLM instance with full response
llm = ZunnoLLM(
    model_name="mistral:latest",
    return_full_response=True
)

# Get complete API response
full_response = llm.invoke("Hello, how are you?")
print(full_response)
# Returns: {"response": "...", "model_used": "...", "tokens_used": 123, ...}
```

### Embeddings

#### Basic Usage (Returns only embeddings vector)
```python
from langchain_zunno import ZunnoLLMEmbeddings

# Create an embeddings instance
embeddings = ZunnoLLMEmbeddings(model_name="mistral:latest")

# Get embeddings for a single text
embedding = embeddings.embed_query("Hello, how are you?")
print(f"Embedding dimension: {len(embedding)}")

# Get embeddings for multiple texts
texts = ["Hello world", "How are you?", "Good morning"]
embeddings_list = embeddings.embed_documents(texts)
print(f"Number of embeddings: {len(embeddings_list)}")
```

#### Full Response Mode (Returns complete API response)
```python
from langchain_zunno import ZunnoLLMEmbeddings

# Create an embeddings instance with full response
embeddings = ZunnoLLMEmbeddings(
    model_name="mistral:latest",
    return_full_response=True
)

# Get complete API response
full_response = embeddings.embed_query("Hello, how are you?")
print(full_response)
# Returns: {"embeddings": [...], "model_used": "...", "embedding_dimension": 4096, ...}
```

### Async Usage

```python
import asyncio
from langchain_zunno import ZunnoLLM, ZunnoLLMEmbeddings

async def main():
    # Async LLM
    llm = ZunnoLLM(model_name="mistral:latest")
    response = await llm.ainvoke("Hello, how are you?")
    print(response)
    
    # Async embeddings
    embeddings = ZunnoLLMEmbeddings(model_name="mistral:latest")
    embedding = await embeddings.aembed_query("Hello, how are you?")
    print(f"Embedding dimension: {len(embedding)}")

asyncio.run(main())
```

## Factory Functions

For convenience, you can use factory functions to create instances:

```python
from langchain_zunno import create_zunno_llm, create_zunno_embeddings

# Create LLM with full response
llm = create_zunno_llm(
    model_name="mistral:latest",
    temperature=0.7,
    max_tokens=100,
    return_full_response=True
)

# Create embeddings with full response
embeddings = create_zunno_embeddings(
    model_name="mistral:latest",
    return_full_response=True
)
```

## Configuration

### LLM Configuration

- `model_name`: The name of the model to use
- `base_url`: API endpoint (default: "http://15.206.124.44/v1/prompt-response")
- `temperature`: Controls randomness in generation (default: 0.7)
- `max_tokens`: Maximum number of tokens to generate (optional)
- `timeout`: Request timeout in seconds (default: 300)
- `return_full_response`: Return complete API response instead of just text (default: False)

### Embeddings Configuration

- `model_name`: The name of the embedding model to use
- `base_url`: API endpoint (default: "http://15.206.124.44/v1/text-embeddings")
- `timeout`: Request timeout in seconds (default: 300)
- `return_full_response`: Return complete API response instead of just embeddings (default: False)

## Response Modes

### Basic Mode (Default)
- **LLM**: Returns only the generated text
- **Embeddings**: Returns only the embeddings vector

### Full Response Mode
- **LLM**: Returns complete JSON response with all API fields
- **Embeddings**: Returns complete JSON response with all API fields

Example full response for LLM:
```json
{
  "response": "Hello! I'm doing well, thank you for asking.",
  "model_used": "mistral:latest",
  "tokens_used": 15,
  "prompt_tokens": 5,
  "completion_tokens": 10,
  "total_tokens": 15
}
```

Example full response for embeddings:
```json
{
  "embeddings": [0.123, -0.456, 0.789, ...],
  "model_used": "mistral:latest",
  "embedding_dimension": 4096,
  "normalized": true
}
```

## API Endpoints

The package connects to the following Zunno API endpoints:

- **Text Generation**: `http://15.206.124.44/v1/prompt-response`
- **Embeddings**: `http://15.206.124.44/v1/text-embeddings`

## Error Handling

The package includes comprehensive error handling:

```python
try:
    response = llm.invoke("Hello")
except Exception as e:
    print(f"Error: {e}")
```

## Development

### Installation for Development

```bash
git clone https://github.com/zunno/langchain-zunno.git
cd langchain-zunno
pip install -e ".[dev]"
```

### Running Tests

```bash
pytest
```

### Code Formatting

```bash
black .
isort .
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## Support

For support, please open an issue on GitHub or contact us at support@zunno.ai. 