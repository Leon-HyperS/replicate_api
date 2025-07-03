#!/usr/bin/env python3
"""
Enhanced CLI interface for video generation
"""

import argparse
import sys
import json
from pathlib import Path
from typing import Optional

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from main import VideoGenerator
from core import ConfigLoader


def interactive_mode(generator: VideoGenerator):
    """Run in interactive mode"""
    print("🎬 Video Generation System - Interactive Mode")
    print("Type 'help' for commands, 'exit' to quit\n")
    
    while True:
        try:
            command = input("> ").strip().lower()
            
            if command == 'exit':
                break
            
            elif command == 'help':
                print("""
Commands:
  generate <model> <config>  - Generate video
  list models               - List available models
  list configs              - List available configs
  show config <name>        - Show config details
  history [model]           - Show generation history
  stats                     - Show statistics
  help                      - Show this help
  exit                      - Exit
                """)
            
            elif command.startswith('generate'):
                parts = command.split()
                if len(parts) >= 3:
                    model = parts[1]
                    config = parts[2]
                    result = generator.generate(model, config)
                    if result['success']:
                        print("✅ Generation successful!")
                    else:
                        print(f"❌ Failed: {result.get('error')}")
                else:
                    print("Usage: generate <model> <config>")
            
            elif command == 'list models':
                print("Available models:")
                for model in generator.list_models():
                    print(f"  - {model}")
            
            elif command == 'list configs':
                print("Available configurations:")
                for config in generator.list_configs():
                    print(f"  - {config}")
            
            elif command.startswith('show config'):
                parts = command.split()
                if len(parts) >= 3:
                    config_name = parts[2]
                    try:
                        config = generator.config_loader.load(config_name)
                        print(json.dumps(config, indent=2))
                    except Exception as e:
                        print(f"Error: {e}")
                else:
                    print("Usage: show config <name>")
            
            elif command.startswith('history'):
                parts = command.split()
                model = parts[1] if len(parts) > 1 else None
                for record in generator.get_history(model, limit=5):
                    print(f"  {record['timestamp']} - {record['model_type']} - {record['config_name']}")
            
            elif command == 'stats':
                stats = generator.get_statistics()
                print(f"Total generations: {stats['total_generations']}")
                print(f"By model: {stats['by_model']}")
            
            else:
                print("Unknown command. Type 'help' for commands.")
        
        except KeyboardInterrupt:
            print("\nUse 'exit' to quit")
        except Exception as e:
            print(f"Error: {e}")


def create_config_wizard():
    """Interactive config creation wizard"""
    print("\n🎨 Config Creation Wizard")
    print("Let's create a new video configuration!\n")
    
    config = {}
    
    # Shot composition
    print("📷 Shot Composition:")
    config['shot'] = {
        'composition': input("  Composition (e.g., 'Medium shot, vertical format'): ") or "Medium shot",
        'camera_motion': input("  Camera motion (e.g., 'slight natural shake'): ") or "static",
        'frame_rate': input("  Frame rate (e.g., '30fps'): ") or "30fps",
        'film_grain': input("  Film grain (e.g., 'none', 'light', 'heavy'): ") or "none"
    }
    
    # Subject
    print("\n👤 Subject:")
    config['subject'] = {
        'description': input("  Description: ") or "A person",
        'wardrobe': input("  Wardrobe (optional): ") or ""
    }
    if not config['subject']['wardrobe']:
        del config['subject']['wardrobe']
    
    # Scene
    print("\n🌍 Scene:")
    config['scene'] = {
        'location': input("  Location: ") or "indoor studio",
        'time_of_day': input("  Time of day: ") or "daytime",
        'environment': input("  Environment details: ") or ""
    }
    if not config['scene']['environment']:
        del config['scene']['environment']
    
    # Visual details
    print("\n🎭 Visual Details:")
    action = input("  Action/What's happening: ")
    if action:
        config['visual_details'] = {'action': action}
        props = input("  Props (optional): ")
        if props:
            config['visual_details']['props'] = props
    
    # Cinematography
    print("\n🎬 Cinematography:")
    lighting = input("  Lighting: ") or "natural light"
    tone = input("  Tone (e.g., 'comedic', 'dramatic', 'neutral'): ") or "neutral"
    config['cinematography'] = {
        'lighting': lighting,
        'tone': tone
    }
    
    # Audio
    print("\n🔊 Audio (optional):")
    has_dialogue = input("  Include dialogue? (y/n): ").lower() == 'y'
    if has_dialogue:
        config['audio'] = {
            'dialogue': {
                'character': input("    Character name: ") or "Person",
                'line': input("    Dialogue line: ") or ""
            }
        }
    
    # Color palette
    print("\n🎨 Visual Style:")
    config['color_palette'] = input("  Color palette description: ") or "natural colors"
    
    # Save config
    print("\n💾 Save Configuration:")
    config_name = input("  Config name (without extension): ")
    
    if config_name:
        loader = ConfigLoader()
        path = loader.save(config, config_name)
        print(f"\n✅ Config saved to: {path}")
        
        # Show preview
        print("\n📝 Preview of generated prompt:")
        from modules.veo3 import Veo3Module
        module = Veo3Module(None)  # We just need the prompt builder
        prompt = module.build_prompt(config)
        print(f"  {prompt}")
        
        return config_name
    
    return None


def main():
    """Enhanced CLI interface"""
    parser = argparse.ArgumentParser(
        description="Video Generation System",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --model veo3 --config yeti
  %(prog)s --interactive
  %(prog)s --create-config
  %(prog)s --list-configs
        """
    )
    
    # Mode selection
    mode_group = parser.add_mutually_exclusive_group()
    mode_group.add_argument('--interactive', '-i', action='store_true',
                           help='Run in interactive mode')
    mode_group.add_argument('--create-config', action='store_true',
                           help='Create new config with wizard')
    
    # Generation options
    parser.add_argument('--model', '-m', default='veo3',
                       help='Model to use (default: veo3)')
    parser.add_argument('--config', '-c',
                       help='Config name or path')
    parser.add_argument('--output-dir', '-o',
                       help='Custom output directory')
    
    # List options
    parser.add_argument('--list-models', action='store_true',
                       help='List available models')
    parser.add_argument('--list-configs', action='store_true',
                       help='List available configs')
    parser.add_argument('--show-config', metavar='NAME',
                       help='Show config details')
    
    # History and stats
    parser.add_argument('--history', nargs='?', const='all', metavar='MODEL',
                       help='Show generation history')
    parser.add_argument('--stats', action='store_true',
                       help='Show statistics')
    
    # Batch operations
    parser.add_argument('--batch', '-b', action='store_true',
                       help='Batch mode (config should be directory)')
    parser.add_argument('--dry-run', action='store_true',
                       help='Show what would be generated without running')
    
    args = parser.parse_args()
    
    # Initialize generator
    generator = VideoGenerator()
    
    # Handle different modes
    if args.interactive:
        interactive_mode(generator)
    
    elif args.create_config:
        config_name = create_config_wizard()
        if config_name and input("\nGenerate video now? (y/n): ").lower() == 'y':
            result = generator.generate('veo3', config_name)
            if result['success']:
                print("✅ Generation successful!")
    
    elif args.list_models:
        print("Available models:")
        for model in generator.list_models():
            print(f"  - {model}")
    
    elif args.list_configs:
        configs = generator.list_configs()
        if configs:
            print("Available configurations:")
            for config in configs:
                print(f"  - {config}")
        else:
            print("No configurations found. Create one with --create-config")
    
    elif args.show_config:
        try:
            config = generator.config_loader.load(args.show_config)
            print(json.dumps(config, indent=2))
        except Exception as e:
            print(f"Error: {e}")
    
    elif args.history is not None:
        model = None if args.history == 'all' else args.history
        history = generator.get_history(model, limit=10)
        if history:
            print("Recent generations:")
            for record in history:
                print(f"  {record['timestamp']} - {record['model_type']} - {record['config_name']}")
        else:
            print("No generation history found")
    
    elif args.stats:
        stats = generator.get_statistics()
        print("Generation Statistics:")
        print(f"  Total generations: {stats['total_generations']}")
        print(f"  Total files: {stats['total_files']}")
        print("\nBy model:")
        for model, count in stats['by_model'].items():
            print(f"    {model}: {count}")
        print("\nBy config:")
        for config, count in list(stats['by_config'].items())[:5]:
            print(f"    {config}: {count}")
    
    elif args.config:
        if args.dry_run:
            # Show what would be generated
            config = generator.config_loader.load(args.config)
            from modules.veo3 import Veo3Module
            module = Veo3Module(None)
            prompt = module.build_prompt(config)
            print(f"Would generate with prompt:\n{prompt}")
        else:
            # Generate
            result = generator.generate(args.model, args.config)
            if result['success']:
                print("✅ Generation successful!")
                if 'output_files' in result:
                    print(f"Output: {result['output_files'][0]}")
            else:
                print(f"❌ Failed: {result.get('error')}")
    
    else:
        parser.print_help()


if __name__ == "__main__":
    main()