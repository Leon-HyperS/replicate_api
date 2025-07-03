"""
Base module for all video/image generation models
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, Union, List
from pathlib import Path
import json
from datetime import datetime


class BaseModule(ABC):
    """Abstract base class for all generation modules"""
    
    def __init__(self, client, output_base_dir: Path = Path("outputs")):
        """
        Initialize the module
        
        Args:
            client: ReplicateClient instance
            output_base_dir: Base directory for outputs
        """
        self.client = client
        self.output_base_dir = output_base_dir
        self.model_name = self.get_model_name()
        self.output_dir = output_base_dir / self.model_type
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    @property
    @abstractmethod
    def model_type(self) -> str:
        """Return the model type identifier (e.g., 'veo3', 'flux')"""
        pass
    
    @abstractmethod
    def get_model_name(self) -> str:
        """Return the full model name for Replicate API"""
        pass
    
    @abstractmethod
    def build_prompt(self, config: Dict[str, Any]) -> str:
        """
        Build a natural language prompt from structured config
        
        Args:
            config: Structured configuration dictionary
            
        Returns:
            Natural language prompt string
        """
        pass
    
    @abstractmethod
    def get_model_params(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract model-specific parameters from config
        
        Args:
            config: Full configuration dictionary
            
        Returns:
            Model-specific parameters
        """
        pass
    
    def generate(
        self, 
        config: Dict[str, Any], 
        config_name: Optional[str] = None,
        save_output: bool = True
    ) -> Dict[str, Any]:
        """
        Generate content using the model
        
        Args:
            config: Configuration dictionary
            config_name: Optional name for the config
            save_output: Whether to save outputs to disk
            
        Returns:
            Dictionary with generation results
        """
        # Build prompt
        prompt = self.build_prompt(config)
        
        # Get model parameters
        model_params = self.get_model_params(config)
        model_params['prompt'] = prompt
        
        # Create metadata
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        metadata = {
            "timestamp": timestamp,
            "model": self.model_name,
            "config_name": config_name,
            "config": config,
            "generated_prompt": prompt,
            "model_params": model_params
        }
        
        try:
            # Run the model
            print(f"Generating with {self.model_type}...")
            print(f"Prompt: {prompt[:200]}..." if len(prompt) > 200 else f"Prompt: {prompt}")
            
            output = self.client.run_model(self.model_name, input_data=model_params)
            
            # Save outputs if requested
            if save_output:
                output_files = self.save_output(output, config_name, timestamp, metadata)
                metadata["output_files"] = [str(f) for f in output_files]
            
            # Save metadata
            self.save_metadata(metadata, config_name, timestamp)
            
            return {
                "success": True,
                "output": output,
                "metadata": metadata,
                "output_files": metadata.get("output_files", [])
            }
            
        except Exception as e:
            print(f"Error during generation: {e}")
            return {
                "success": False,
                "error": str(e),
                "metadata": metadata
            }
    
    def save_output(
        self, 
        output: Union[str, List[str]], 
        config_name: Optional[str],
        timestamp: str,
        metadata: Dict[str, Any]
    ) -> List[Path]:
        """
        Save output files
        
        Args:
            output: Output URL(s) from the model
            config_name: Name of the config used
            timestamp: Timestamp string
            metadata: Generation metadata
            
        Returns:
            List of saved file paths
        """
        # Create subdirectory for this generation
        prefix = config_name or "output"
        gen_dir = self.output_dir / f"{prefix}_{timestamp}"
        gen_dir.mkdir(parents=True, exist_ok=True)
        
        # Determine file extension based on model type
        ext = self.get_output_extension()
        
        # Handle video outputs differently from images
        if ext == '.mp4':
            # For video, save directly
            output_path = gen_dir / f"{prefix}_{timestamp}{ext}"
            if isinstance(output, list):
                output = output[0]  # Take first output for video
            
            import requests
            response = requests.get(output)
            response.raise_for_status()
            
            with open(output_path, 'wb') as f:
                f.write(response.content)
            
            print(f"Saved {self.model_type} output to: {output_path}")
            return [output_path]
        else:
            # For images, use the client's save method
            saved_files = self.client.save_image_output(
                output,
                gen_dir,
                f"{prefix}_{timestamp}"
            )
            return [Path(f) for f in saved_files]
    
    def save_metadata(
        self,
        metadata: Dict[str, Any],
        config_name: Optional[str],
        timestamp: str
    ):
        """Save generation metadata"""
        prefix = config_name or "output"
        metadata_path = self.output_dir / f"{prefix}_{timestamp}" / "metadata.json"
        
        with open(metadata_path, 'w') as f:
            json.dump(metadata, f, indent=2)
        
        print(f"Saved metadata to: {metadata_path}")
    
    def get_output_extension(self) -> str:
        """Get the expected output file extension"""
        return '.mp4' if 'video' in self.model_type else '.png'