# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Architecture Overview

This is a modular video generation system built around the Replicate API that specializes in AI-powered video creation. The system provides:

1. **Two-Layer Architecture**: Base Replicate client for general API access + specialized video generation layer
2. **Plugin-Based Model System**: Extensible architecture for different AI models (currently Veo3)
3. **Configuration-Driven Generation**: JSON configs define structured video parameters
4. **Enhanced CLI Interface**: Interactive mode, config wizard, and comprehensive management commands
5. **Automated Output Management**: Organized file structure with metadata tracking

## Key Components

### Core Architecture Flow
```
generate.py (Enhanced CLI) → main.py (VideoGenerator) → modules/veo3.py → replicate_client.py → Replicate API
```

### Main Entry Points
- `generate.py`: Primary user interface with interactive features
- `main.py`: Core orchestrator, can be used programmatically
- `replicate_client.py`: Low-level API wrapper for direct access
- `examples.py`: Demonstrates various API usage patterns

### Module System
- `modules/base.py`: Abstract base class defining model interface
- `modules/veo3.py`: Google Veo3 implementation
- New models: Inherit from BaseModule, implement required methods, register in VideoGenerator

### Configuration System
- JSON configs in `config/prompts/` with structured video parameters
- Supports inheritance via `_extends` field
- Configs converted to natural language prompts by model modules

## Common Development Commands

### Initial Setup
```bash
pip install -r requirements.txt
cp .env.example .env
# Add REPLICATE_API_TOKEN to .env
```

### Video Generation
```bash
# Standard generation
python generate.py --model veo3 --config yeti

# Interactive mode (guided generation)
python generate.py --interactive

# Create new configuration
python generate.py --create-config

# Preview without generating
python generate.py --model veo3 --config yeti --dry-run

# Custom prompt (bypass config)
python generate.py --model veo3 --prompt "A serene mountain landscape"
```

### Management Commands
```bash
# Resource listing
python generate.py --list-models
python generate.py --list-configs

# Configuration inspection
python generate.py --show-config yeti

# History and analytics
python generate.py --history
python generate.py --stats
```

### Development Usage
```python
# Direct programmatic usage
from main import VideoGenerator
generator = VideoGenerator()
result = generator.generate('veo3', 'yeti')

# Low-level API access
from replicate_client import ReplicateClient
client = ReplicateClient()
result = client.run_model('model_name', input_params)
```

## Adding New Models

1. Create module in `modules/` inheriting from `BaseModule`
2. Implement required methods:
   - `model_type`: Return unique identifier
   - `get_model_name`: Return Replicate model string
   - `build_prompt`: Convert config to natural language
   - `get_model_params`: Return model-specific parameters
3. Register in `VideoGenerator.__init__()`:
   ```python
   self.modules = {
       'veo3': Veo3Module(),
       'your_model': YourModule(),
   }
   ```
4. Test with existing configs

## Configuration Schema

Video configs use structured JSON to define all aspects of generation:
- `shot`: Composition, camera motion, technical settings
- `subject`: Main subject description and appearance
- `scene`: Location, time, environment
- `visual_details`: Action and props
- `cinematography`: Lighting and tone
- `audio`: Dialogue, ambient sounds, effects
- `color_palette`: Visual color scheme

## Output Organization

```
outputs/
├── {model_type}/
│   └── {config_name}_{timestamp}/
│       ├── video_{timestamp}.mp4
│       └── metadata.json
└── generation_history.json
```

Each generation includes:
- Video file (MP4)
- Metadata (config, prompt, parameters, timestamps)
- History tracking for analytics

## Testing and Validation

```bash
# Run all API examples
python examples.py

# Test specific model with dry run
python generate.py --model veo3 --config yeti --dry-run

# Validate configuration
python generate.py --show-config yeti
```

## Important Notes

- All API calls require `REPLICATE_API_TOKEN` environment variable
- Generation is asynchronous - client polls for completion
- Metadata preserved even on failed generations
- Supports both config-based and direct prompt generation
- Output directories created automatically on first use