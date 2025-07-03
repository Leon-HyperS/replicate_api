# Replicate API Python Client

A comprehensive Python client for interacting with [Replicate.com](https://replicate.com) models via API token. This client provides an enhanced wrapper around the official Replicate Python SDK with additional utilities, error handling, and convenience features.

## Features

- 🔐 **Secure Authentication**: Support for environment variables and direct token passing
- 🚀 **Multiple Execution Modes**: Synchronous, asynchronous, and streaming
- 🖼️ **Built-in Output Handling**: Automatic image saving and output processing
- 🔄 **Comprehensive Error Handling**: Retry logic and detailed error messages
- 📊 **Batch Processing**: Process multiple predictions efficiently
- 🎯 **Type Hints**: Full type annotations for better IDE support
- 🛠️ **Utility Functions**: Helper methods for common tasks

## Installation

1. Clone this repository:
```bash
git clone <your-repo-url>
cd replicate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up your API token:
   - Copy `.env.example` to `.env`
   - Add your Replicate API token (get it from [replicate.com/account/api-tokens](https://replicate.com/account/api-tokens))

```bash
cp .env.example .env
# Edit .env and add your token
```

## Quick Start

```python
from replicate_client import create_client

# Initialize client (uses REPLICATE_API_TOKEN from environment)
client = create_client()

# Generate an image
output = client.run_model(
    "stability-ai/stable-diffusion:db21e45d3f7023abc2a46ee38a23973f6dce16bb082a930b0c49861f96d1e5bf",
    input_data={
        "prompt": "A serene mountain landscape at sunset",
        "width": 512,
        "height": 512
    }
)

# Save the generated image
client.save_image_output(output, "outputs", "mountain_sunset")
```

## Usage Examples

### Text Generation (LLM)

```python
# Generate text using Llama 2
output = client.run_model(
    "meta/llama-2-70b-chat:02e509c789964a7ea8736978a43525956ef40397be9033abf9fd2badfe68c9e3",
    input_data={
        "prompt": "Explain quantum computing in simple terms",
        "temperature": 0.75,
        "max_new_tokens": 500
    }
)
print(''.join(output))
```

### Image Generation

```python
# Generate images with FLUX
output = client.run_model(
    "black-forest-labs/flux-schnell",
    input_data={
        "prompt": "A futuristic city with flying cars",
        "aspect_ratio": "16:9",
        "output_format": "webp"
    }
)

# Automatically save the image
saved_files = client.save_image_output(output, "outputs", "futuristic_city")
```

### Streaming Responses

```python
# Stream tokens from an LLM
for token in client.stream_model(
    "meta/llama-2-70b-chat:02e509c789964a7ea8736978a43525956ef40397be9033abf9fd2badfe68c9e3",
    input_data={
        "prompt": "Write a short story about AI",
        "max_new_tokens": 1000
    }
):
    print(token, end='', flush=True)
```

### Asynchronous Predictions

```python
# Start a prediction without waiting
prediction = client.run_model_async(
    "stability-ai/stable-diffusion:db21e45d3f7023abc2a46ee38a23973f6dce16bb082a930b0c49861f96d1e5bf",
    input_data={"prompt": "A beautiful landscape"}
)

print(f"Prediction ID: {prediction.id}")
print(f"Status: {prediction.status}")

# Check status later
prediction = client.get_prediction(prediction.id)
if prediction.status == "succeeded":
    print(f"Output: {prediction.output}")
```

### Batch Processing

```python
prompts = ["Scene 1", "Scene 2", "Scene 3"]

for i, prompt in enumerate(prompts):
    output = client.run_model(
        "stability-ai/stable-diffusion:db21e45d3f7023abc2a46ee38a23973f6dce16bb082a930b0c49861f96d1e5bf",
        input_data={"prompt": prompt, "width": 512, "height": 512}
    )
    client.save_image_output(output, "outputs/batch", f"scene_{i+1}")
```

## Running Examples

Run all examples:
```bash
python examples.py
```

The examples demonstrate:
- Text generation with LLMs
- Image generation with Stable Diffusion and FLUX
- Image-to-image transformation
- Streaming responses
- Asynchronous predictions
- Model information retrieval
- Batch processing

## API Reference

### ReplicateClient

#### `__init__(api_token: Optional[str] = None, user_agent: Optional[str] = None)`
Initialize the client with optional API token and user agent.

#### `run_model(model_name: str, input_data: Dict, wait_for_completion: bool = True) -> Any`
Run a model and optionally wait for completion.

#### `run_model_async(model_name: str, input_data: Dict) -> Prediction`
Run a model asynchronously without waiting.

#### `stream_model(model_name: str, input_data: Dict) -> Iterator`
Stream output from models that support streaming.

#### `save_image_output(output_url: Union[str, List[str]], output_path: Union[str, Path], filename_prefix: str = "output") -> List[Path]`
Save image outputs to disk with automatic format detection.

#### `get_prediction(prediction_id: str) -> Prediction`
Get a prediction by its ID.

#### `cancel_prediction(prediction_id: str) -> Prediction`
Cancel a running prediction.

#### `get_model_info(model_name: str) -> Dict`
Get information about a model.

## Finding Models

Browse available models at [replicate.com/explore](https://replicate.com/explore). Each model page shows:
- Model identifier (e.g., `owner/model-name:version`)
- Input parameters and their types
- Example code
- API schema

## Error Handling

The client includes comprehensive error handling:

```python
try:
    output = client.run_model("model-name", input_data={...})
except ValueError as e:
    print(f"Invalid input: {e}")
except RuntimeError as e:
    print(f"Prediction failed: {e}")
except TimeoutError as e:
    print(f"Prediction timed out: {e}")
```

## Environment Variables

- `REPLICATE_API_TOKEN`: Your Replicate API token (required)
- `APP_USER_AGENT`: Custom user agent for API requests (optional)

## Requirements

- Python 3.8+
- Dependencies listed in `requirements.txt`

## License

This project is provided as-is for educational and development purposes.

## Contributing

Feel free to submit issues, fork the repository, and create pull requests for any improvements.

## Security

- Never commit your API token to version control
- Use environment variables or secure secret management
- The `.env` file is gitignored by default

## Support

For issues with:
- This client: Open an issue in this repository
- Replicate API: Visit [replicate.com/docs](https://replicate.com/docs)
- Specific models: Check the model's page on Replicate