"""
Replicate API Client
A comprehensive Python client for interacting with Replicate.com models
"""

import os
import time
import json
from typing import Dict, Any, List, Optional, Union, Iterator
from pathlib import Path
import requests
from PIL import Image
from io import BytesIO

import replicate
from replicate.client import Client
from dotenv import load_dotenv


class ReplicateClient:
    """Enhanced Replicate API client with additional utilities and error handling"""
    
    def __init__(self, api_token: Optional[str] = None, user_agent: Optional[str] = None):
        """
        Initialize the Replicate client
        
        Args:
            api_token: Optional API token. If not provided, will use REPLICATE_API_TOKEN env var
            user_agent: Optional custom user agent string
        """
        load_dotenv()
        
        # Get API token from parameter or environment
        self.api_token = api_token or os.getenv('REPLICATE_API_TOKEN')
        if not self.api_token:
            raise ValueError(
                "API token not found. Please set REPLICATE_API_TOKEN environment variable "
                "or pass api_token parameter"
            )
        
        # Initialize client with custom headers if provided
        headers = {}
        if user_agent or os.getenv('APP_USER_AGENT'):
            headers['User-Agent'] = user_agent or os.getenv('APP_USER_AGENT')
        
        self.client = Client(api_token=self.api_token, headers=headers) if headers else replicate
        
        # Initialize with token if using default client
        if not headers:
            os.environ['REPLICATE_API_TOKEN'] = self.api_token
    
    def run_model(
        self,
        model_name: str,
        input_data: Dict[str, Any],
        wait_for_completion: bool = True,
        webhook: Optional[str] = None,
        webhook_events_filter: Optional[List[str]] = None
    ) -> Union[Any, 'replicate.prediction.Prediction']:
        """
        Run a model on Replicate
        
        Args:
            model_name: Model identifier (e.g., "stability-ai/stable-diffusion")
            input_data: Dictionary of input parameters for the model
            wait_for_completion: Whether to wait for the prediction to complete
            webhook: Optional webhook URL for async notifications
            webhook_events_filter: List of events to send to webhook
            
        Returns:
            Model output or Prediction object if wait_for_completion is False
        """
        try:
            # Run the model
            if webhook:
                prediction = self.client.predictions.create(
                    version=model_name,
                    input=input_data,
                    webhook=webhook,
                    webhook_events_filter=webhook_events_filter or ["completed"]
                )
                if not wait_for_completion:
                    return prediction
                
                # Wait for completion
                prediction = self._wait_for_prediction(prediction)
                return prediction.output
            else:
                # Use the simpler run method for synchronous execution
                output = self.client.run(model_name, input=input_data)
                return output
                
        except Exception as e:
            print(f"Error running model {model_name}: {str(e)}")
            raise
    
    def run_model_async(
        self,
        model_name: str,
        input_data: Dict[str, Any],
        webhook: Optional[str] = None
    ) -> 'replicate.prediction.Prediction':
        """
        Run a model asynchronously
        
        Args:
            model_name: Model identifier
            input_data: Input parameters
            webhook: Optional webhook URL
            
        Returns:
            Prediction object
        """
        return self.run_model(
            model_name,
            input_data,
            wait_for_completion=False,
            webhook=webhook
        )
    
    def stream_model(
        self,
        model_name: str,
        input_data: Dict[str, Any]
    ) -> Iterator[Any]:
        """
        Stream output from a model that supports streaming
        
        Args:
            model_name: Model identifier
            input_data: Input parameters
            
        Yields:
            Streamed output chunks
        """
        try:
            for event in self.client.stream(model_name, input=input_data):
                yield event
        except Exception as e:
            print(f"Error streaming from model {model_name}: {str(e)}")
            raise
    
    def get_prediction(self, prediction_id: str) -> 'replicate.prediction.Prediction':
        """
        Get a prediction by ID
        
        Args:
            prediction_id: The prediction ID
            
        Returns:
            Prediction object
        """
        return self.client.predictions.get(prediction_id)
    
    def cancel_prediction(self, prediction_id: str) -> 'replicate.prediction.Prediction':
        """
        Cancel a running prediction
        
        Args:
            prediction_id: The prediction ID to cancel
            
        Returns:
            Cancelled prediction object
        """
        prediction = self.client.predictions.get(prediction_id)
        return prediction.cancel()
    
    def list_predictions(
        self,
        cursor: Optional[str] = None
    ) -> List['replicate.prediction.Prediction']:
        """
        List recent predictions
        
        Args:
            cursor: Optional cursor for pagination
            
        Returns:
            List of Prediction objects
        """
        return list(self.client.predictions.list(cursor=cursor))
    
    def save_image_output(
        self,
        output_url: Union[str, List[str]],
        output_path: Union[str, Path],
        filename_prefix: str = "output"
    ) -> List[Path]:
        """
        Save image outputs to disk
        
        Args:
            output_url: URL or list of URLs of generated images
            output_path: Directory to save images
            filename_prefix: Prefix for saved files
            
        Returns:
            List of saved file paths
        """
        output_path = Path(output_path)
        output_path.mkdir(parents=True, exist_ok=True)
        
        urls = output_url if isinstance(output_url, list) else [output_url]
        saved_files = []
        
        for idx, url in enumerate(urls):
            try:
                response = requests.get(url)
                response.raise_for_status()
                
                # Determine file extension from content type
                content_type = response.headers.get('content-type', '')
                ext = '.png'
                if 'jpeg' in content_type:
                    ext = '.jpg'
                elif 'webp' in content_type:
                    ext = '.webp'
                
                # Save the file
                filename = f"{filename_prefix}_{idx}{ext}" if len(urls) > 1 else f"{filename_prefix}{ext}"
                file_path = output_path / filename
                
                with open(file_path, 'wb') as f:
                    f.write(response.content)
                
                saved_files.append(file_path)
                print(f"Saved image to: {file_path}")
                
            except Exception as e:
                print(f"Error saving image from {url}: {str(e)}")
        
        return saved_files
    
    def process_output(self, output: Any, output_type: str = "auto") -> Any:
        """
        Process model output based on type
        
        Args:
            output: Raw model output
            output_type: Type of output ("auto", "text", "image", "json")
            
        Returns:
            Processed output
        """
        if output_type == "auto":
            # Auto-detect output type
            if isinstance(output, str):
                if output.startswith(('http://', 'https://')) and any(
                    ext in output for ext in ['.png', '.jpg', '.jpeg', '.webp']
                ):
                    output_type = "image"
                else:
                    output_type = "text"
            elif isinstance(output, list):
                output_type = "list"
            elif isinstance(output, dict):
                output_type = "json"
        
        if output_type == "image" and isinstance(output, str):
            # For image URLs, optionally download and display
            return {"type": "image", "url": output}
        elif output_type == "json":
            return json.dumps(output, indent=2) if isinstance(output, dict) else output
        else:
            return output
    
    def _wait_for_prediction(
        self,
        prediction: 'replicate.prediction.Prediction',
        polling_interval: float = 1.0,
        timeout: Optional[float] = None
    ) -> 'replicate.prediction.Prediction':
        """
        Wait for a prediction to complete
        
        Args:
            prediction: Prediction object
            polling_interval: Seconds between status checks
            timeout: Maximum seconds to wait
            
        Returns:
            Completed prediction
        """
        start_time = time.time()
        
        while prediction.status not in ["succeeded", "failed", "canceled"]:
            if timeout and (time.time() - start_time) > timeout:
                raise TimeoutError(f"Prediction {prediction.id} timed out after {timeout} seconds")
            
            time.sleep(polling_interval)
            prediction = self.client.predictions.get(prediction.id)
        
        if prediction.status == "failed":
            raise RuntimeError(f"Prediction {prediction.id} failed: {prediction.error}")
        elif prediction.status == "canceled":
            raise RuntimeError(f"Prediction {prediction.id} was canceled")
        
        return prediction
    
    def get_model_info(self, model_name: str) -> Dict[str, Any]:
        """
        Get information about a model
        
        Args:
            model_name: Model identifier
            
        Returns:
            Model information dictionary
        """
        try:
            model = self.client.models.get(model_name)
            return {
                "name": model.name,
                "description": model.description,
                "visibility": model.visibility,
                "github_url": model.github_url,
                "paper_url": model.paper_url,
                "license_url": model.license_url,
                "latest_version": model.latest_version.id if model.latest_version else None
            }
        except Exception as e:
            print(f"Error getting model info for {model_name}: {str(e)}")
            raise


def create_client(api_token: Optional[str] = None) -> ReplicateClient:
    """
    Factory function to create a ReplicateClient instance
    
    Args:
        api_token: Optional API token
        
    Returns:
        ReplicateClient instance
    """
    return ReplicateClient(api_token=api_token)