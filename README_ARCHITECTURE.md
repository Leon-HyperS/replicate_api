# Video Generation System Architecture

## Overview

This is a scalable, modular video generation system designed for easy integration of multiple AI models and prompt configurations.

## Directory Structure

```
replicate_api/
├── config/
│   └── prompts/          # Prompt configuration files
│       ├── yeti.json
│       ├── template.json
│       └── ...
├── modules/              # Model-specific modules
│   ├── __init__.py
│   ├── base.py          # BaseModule abstract class
│   └── veo3.py          # Veo3 implementation
├── core/                 # Core utilities
│   ├── __init__.py
│   ├── config_loader.py  # Configuration management
│   ├── output_manager.py # Output organization
│   └── prompt_builder.py # Prompt construction
├── outputs/              # Generated outputs
│   └── veo3/
│       └── ...
├── main.py              # Main entry point
└── generate.py          # Enhanced CLI interface
```

## Quick Start

### 1. Basic Usage

```bash
# Generate with existing config
python generate.py --model veo3 --config yeti

# Interactive mode
python generate.py --interactive

# Create new config with wizard
python generate.py --create-config
```

### 2. List Available Resources

```bash
# List models
python generate.py --list-models

# List configs
python generate.py --list-configs

# Show config details
python generate.py --show-config yeti
```

### 3. View History and Stats

```bash
# View generation history
python generate.py --history

# View statistics
python generate.py --stats
```

## Configuration Format

Configurations are JSON files with the following structure:

```json
{
  "shot": {
    "composition": "Shot type and framing",
    "camera_motion": "Camera movement",
    "frame_rate": "Frame rate",
    "film_grain": "Film grain effect"
  },
  "subject": {
    "description": "Main subject description",
    "wardrobe": "Clothing/appearance"
  },
  "scene": {
    "location": "Setting",
    "time_of_day": "Time",
    "environment": "Environmental details"
  },
  "visual_details": {
    "action": "What's happening",
    "props": "Props in scene"
  },
  "cinematography": {
    "lighting": "Lighting setup",
    "tone": "Visual tone"
  },
  "audio": {
    "dialogue": {
      "character": "Speaker",
      "line": "What they say"
    },
    "ambient": "Background sounds",
    "effects": "Sound effects"
  },
  "color_palette": "Color scheme description"
}
```

## Adding New Models

1. Create a new module in `modules/`:

```python
from .base import BaseModule

class NewModelModule(BaseModule):
    @property
    def model_type(self):
        return "newmodel"
    
    def get_model_name(self):
        return "provider/model-name"
    
    def build_prompt(self, config):
        # Convert config to prompt
        pass
    
    def get_model_params(self, config):
        # Extract model parameters
        pass
```

2. Register in `main.py`:

```python
self.modules = {
    'veo3': Veo3Module(self.client),
    'newmodel': NewModelModule(self.client)
}
```

## Features

- **Modular Architecture**: Easy to add new models
- **Flexible Configs**: JSON-based prompt configurations
- **Organized Outputs**: Automatic output organization by model/date/config
- **Generation History**: Track all generations with metadata
- **Interactive Mode**: User-friendly command interface
- **Config Wizard**: Create configs interactively
- **Batch Processing**: Generate multiple videos at once
- **Statistics**: View generation statistics

## Example Configs

- `yeti.json` - The Yeti character you specified
- `cyberpunk_city.json` - Noir cityscape
- `nature_meditation.json` - Peaceful nature scene
- `template.json` - Basic template to start from

## Advanced Usage

### Batch Generation

```bash
# Generate all configs in a directory
python generate.py --model veo3 --config ./my-configs/ --batch
```

### Custom Output Directory

```bash
python main.py --model veo3 --config yeti --output-dir ./my-outputs
```

### Dry Run (Preview Prompt)

```bash
python generate.py --model veo3 --config yeti --dry-run
```

## API Integration

```python
from main import VideoGenerator

# Initialize
generator = VideoGenerator()

# Generate
result = generator.generate('veo3', 'yeti')

# Check result
if result['success']:
    print(f"Output: {result['output_files']}")
```