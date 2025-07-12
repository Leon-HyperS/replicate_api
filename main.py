"""
Main entry point for the video generation system
"""

import sys
from pathlib import Path
from typing import Dict, Any, Optional

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from replicate_client import create_client
from modules.veo3 import Veo3Module
from core import ConfigLoader, OutputManager


class VideoGenerator:
    """Main video generation orchestrator"""
    
    def __init__(self, api_token: Optional[str] = None):
        """
        Initialize the video generator
        
        Args:
            api_token: Optional Replicate API token
        """
        self.client = create_client(api_token)
        self.config_loader = ConfigLoader()
        self.output_manager = OutputManager()
        
        # Initialize available modules
        self.modules = {
            'veo3': Veo3Module(self.client)
        }
    
    def generate(
        self,
        model: str,
        config_name: str,
        save_output: bool = True
    ) -> Dict[str, Any]:
        """
        Generate content using specified model and config
        
        Args:
            model: Model type to use
            config_name: Configuration name or path
            save_output: Whether to save outputs
            
        Returns:
            Generation results
        """
        # Validate model
        if model not in self.modules:
            raise ValueError(f"Unknown model: {model}. Available: {list(self.modules.keys())}")
        
        # Load configuration
        try:
            config = self.config_loader.load(config_name)
        except FileNotFoundError:
            # If not found, try as direct path
            if Path(config_name).exists():
                config = self.config_loader._load_file(Path(config_name))
            else:
                raise
        
        # Validate configuration
        self.config_loader.validate(config)
        
        # Get the module
        module = self.modules[model]
        
        # Generate
        print(f"\n🎬 Generating {model} content with config: {config_name}")
        result = module.generate(config, config_name, save_output)
        
        # Record in history if successful
        if result['success'] and save_output:
            generation_id = self.output_manager.record_generation(
                model,
                config_name,
                result['metadata'],
                [Path(f) for f in result.get('output_files', [])]
            )
            result['generation_id'] = generation_id
        
        return result
    
    def batch_generate(
        self,
        model: str,
        config_names: list,
        save_output: bool = True
    ) -> list:
        """
        Generate multiple videos in batch
        
        Args:
            model: Model type to use
            config_names: List of configuration names
            save_output: Whether to save outputs
            
        Returns:
            List of generation results
        """
        results = []
        
        for config_name in config_names:
            try:
                result = self.generate(model, config_name, save_output)
                results.append(result)
            except Exception as e:
                print(f"❌ Failed to generate with {config_name}: {e}")
                results.append({
                    'success': False,
                    'config_name': config_name,
                    'error': str(e)
                })
        
        return results
    
    def list_models(self) -> list:
        """List available models"""
        return list(self.modules.keys())
    
    def list_configs(self) -> list:
        """List available configurations"""
        return self.config_loader.list_configs()
    
    def get_history(self, model: Optional[str] = None, limit: int = 10) -> list:
        """Get generation history"""
        return self.output_manager.get_latest_outputs(model, limit)
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get generation statistics"""
        return self.output_manager.get_statistics()


def main():
    """Command line interface"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Video Generation System")
    parser.add_argument('--model', '-m', default='veo3', help='Model to use')
    parser.add_argument('--config', '-c', required=True, help='Config name or path')
    parser.add_argument('--batch', '-b', action='store_true', help='Batch mode')
    parser.add_argument('--list-models', action='store_true', help='List available models')
    parser.add_argument('--list-configs', action='store_true', help='List available configs')
    parser.add_argument('--history', action='store_true', help='Show generation history')
    parser.add_argument('--stats', action='store_true', help='Show statistics')
    
    args = parser.parse_args()
    
    # Initialize generator
    generator = VideoGenerator()
    
    # Handle commands
    if args.list_models:
        print("Available models:")
        for model in generator.list_models():
            print(f"  - {model}")
    
    elif args.list_configs:
        print("Available configurations:")
        for config in generator.list_configs():
            print(f"  - {config}")
    
    elif args.history:
        print("Recent generations:")
        for record in generator.get_history(limit=10):
            print(f"  - {record['id']} ({record['timestamp']})")
    
    elif args.stats:
        stats = generator.get_statistics()
        print("Generation Statistics:")
        print(f"  Total generations: {stats['total_generations']}")
        print(f"  Total files: {stats['total_files']}")
        print(f"  By model: {stats['by_model']}")
    
    elif args.config:
        if args.batch:
            # Batch mode - config should be a directory
            config_dir = Path(args.config)
            if config_dir.is_dir():
                configs = [f.stem for f in config_dir.glob("*.json")]
                results = generator.batch_generate(args.model, configs)
                print(f"\nBatch complete: {len([r for r in results if r['success']])} succeeded")
            else:
                print("Error: In batch mode, --config should be a directory")
        else:
            # Single generation
            result = generator.generate(args.model, args.config)
            if result['success']:
                print("✅ Generation successful!")
                if 'output_files' in result:
                    print(f"Output files: {result['output_files']}")
            else:
                print(f"❌ Generation failed: {result.get('error', 'Unknown error')}")


if __name__ == "__main__":
    main()