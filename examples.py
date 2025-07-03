"""
Replicate API Examples
Demonstrates various use cases for the ReplicateClient
"""

import os
from pathlib import Path
from replicate_client import ReplicateClient, create_client


def example_text_generation():
    """Example: Generate text using an LLM"""
    print("\n=== Text Generation Example ===")
    
    client = create_client()
    
    # Using Meta's Llama model
    prompt = "Write a haiku about artificial intelligence"
    
    try:
        output = client.run_model(
            "meta/llama-2-70b-chat:02e509c789964a7ea8736978a43525956ef40397be9033abf9fd2badfe68c9e3",
            input_data={
                "prompt": prompt,
                "temperature": 0.75,
                "top_p": 0.9,
                "max_new_tokens": 200
            }
        )
        
        print(f"Prompt: {prompt}")
        print(f"Response: {''.join(output)}")
        
    except Exception as e:
        print(f"Error: {e}")


def example_image_generation():
    """Example: Generate images using Stable Diffusion"""
    print("\n=== Image Generation Example ===")
    
    client = create_client()
    
    prompt = "A serene Japanese garden with cherry blossoms, koi pond, and Mt. Fuji in the background, studio ghibli style"
    
    try:
        # Using SDXL
        output = client.run_model(
            "stability-ai/sdxl:39ed52f2a78e934b3ba6e2a89f5b1c712de7dfea535525255b1aa35c5565e08b",
            input_data={
                "prompt": prompt,
                "negative_prompt": "ugly, blurry, low quality",
                "width": 1024,
                "height": 1024,
                "num_outputs": 1,
                "scheduler": "K_EULER",
                "num_inference_steps": 25,
                "guidance_scale": 7.5
            }
        )
        
        # Save the generated image
        output_dir = Path("outputs")
        saved_files = client.save_image_output(output, output_dir, "japanese_garden")
        
        print(f"Prompt: {prompt}")
        print(f"Generated image saved to: {saved_files}")
        
    except Exception as e:
        print(f"Error: {e}")


def example_flux_image_generation():
    """Example: Generate images using FLUX"""
    print("\n=== FLUX Image Generation Example ===")
    
    client = create_client()
    
    prompt = "A cyberpunk cat hacker in a neon-lit server room, highly detailed, 8k"
    
    try:
        # Using FLUX Schnell (fast version)
        output = client.run_model(
            "black-forest-labs/flux-schnell",
            input_data={
                "prompt": prompt,
                "num_outputs": 1,
                "aspect_ratio": "1:1",
                "output_format": "webp",
                "output_quality": 80
            }
        )
        
        # Save the generated image
        output_dir = Path("outputs")
        saved_files = client.save_image_output(output, output_dir, "cyberpunk_cat")
        
        print(f"Prompt: {prompt}")
        print(f"Generated image saved to: {saved_files}")
        
    except Exception as e:
        print(f"Error: {e}")


def example_image_to_image():
    """Example: Transform an image using img2img"""
    print("\n=== Image-to-Image Example ===")
    
    client = create_client()
    
    # Note: You'll need to provide an actual image URL
    input_image_url = "https://example.com/your-image.jpg"  # Replace with actual image URL
    
    try:
        output = client.run_model(
            "tencentarc/gfpgan:9283608cc6b7be6b65a8e44983db012355fde4132009bf99d976b2f0896856a3",
            input_data={
                "img": input_image_url,
                "version": "v1.4",
                "scale": 2
            }
        )
        
        # Save the enhanced image
        output_dir = Path("outputs")
        saved_files = client.save_image_output(output, output_dir, "enhanced_image")
        
        print(f"Enhanced image saved to: {saved_files}")
        
    except Exception as e:
        print(f"Error: {e}")
        print("Note: Make sure to provide a valid input image URL")


def example_streaming():
    """Example: Stream output from a model"""
    print("\n=== Streaming Example ===")
    
    client = create_client()
    
    prompt = "Tell me a story about a robot learning to paint"
    
    try:
        print(f"Prompt: {prompt}")
        print("Streaming response:")
        
        # Stream tokens from an LLM
        for token in client.stream_model(
            "meta/llama-2-70b-chat:02e509c789964a7ea8736978a43525956ef40397be9033abf9fd2badfe68c9e3",
            input_data={
                "prompt": prompt,
                "temperature": 0.75,
                "top_p": 0.9,
                "max_new_tokens": 500
            }
        ):
            print(token, end='', flush=True)
        
        print("\n")
        
    except Exception as e:
        print(f"Error: {e}")


def example_async_prediction():
    """Example: Run a model asynchronously"""
    print("\n=== Async Prediction Example ===")
    
    client = create_client()
    
    try:
        # Start an async prediction
        prediction = client.run_model_async(
            "stability-ai/stable-diffusion:db21e45d3f7023abc2a46ee38a23973f6dce16bb082a930b0c49861f96d1e5bf",
            input_data={
                "prompt": "A futuristic city on Mars with glass domes and flying vehicles",
                "width": 512,
                "height": 512
            }
        )
        
        print(f"Started prediction: {prediction.id}")
        print(f"Status: {prediction.status}")
        
        # You can check the prediction status later
        # In a real application, you might poll this or use webhooks
        
    except Exception as e:
        print(f"Error: {e}")


def example_model_info():
    """Example: Get information about a model"""
    print("\n=== Model Information Example ===")
    
    client = create_client()
    
    model_name = "stability-ai/stable-diffusion"
    
    try:
        info = client.get_model_info(model_name)
        
        print(f"Model: {model_name}")
        print(f"Description: {info['description']}")
        print(f"Visibility: {info['visibility']}")
        print(f"GitHub: {info['github_url']}")
        print(f"Latest Version: {info['latest_version']}")
        
    except Exception as e:
        print(f"Error: {e}")


def example_batch_processing():
    """Example: Process multiple predictions"""
    print("\n=== Batch Processing Example ===")
    
    client = create_client()
    
    prompts = [
        "A peaceful mountain landscape at sunrise",
        "An underwater coral reef teeming with colorful fish",
        "A cozy coffee shop on a rainy day"
    ]
    
    try:
        output_dir = Path("outputs/batch")
        output_dir.mkdir(parents=True, exist_ok=True)
        
        for i, prompt in enumerate(prompts):
            print(f"\nGenerating image {i+1}/{len(prompts)}: {prompt}")
            
            output = client.run_model(
                "stability-ai/stable-diffusion:db21e45d3f7023abc2a46ee38a23973f6dce16bb082a930b0c49861f96d1e5bf",
                input_data={
                    "prompt": prompt,
                    "width": 512,
                    "height": 512,
                    "num_inference_steps": 20
                }
            )
            
            # Save each image
            client.save_image_output(output, output_dir, f"batch_{i+1}")
        
        print(f"\nBatch processing complete! Images saved to {output_dir}")
        
    except Exception as e:
        print(f"Error: {e}")


def main():
    """Run all examples"""
    print("Replicate API Examples")
    print("=" * 50)
    
    # Check for API token
    if not os.getenv('REPLICATE_API_TOKEN'):
        print("\nError: REPLICATE_API_TOKEN not set!")
        print("Please set your API token in the .env file or as an environment variable")
        print("Get your token from: https://replicate.com/account/api-tokens")
        return
    
    # Create output directory
    Path("outputs").mkdir(exist_ok=True)
    
    # Run examples (comment out any you don't want to run)
    try:
        example_text_generation()
        example_image_generation()
        example_flux_image_generation()
        # example_image_to_image()  # Requires a valid input image URL
        example_streaming()
        example_async_prediction()
        example_model_info()
        example_batch_processing()
        
    except KeyboardInterrupt:
        print("\n\nExamples interrupted by user")
    except Exception as e:
        print(f"\nUnexpected error: {e}")


if __name__ == "__main__":
    main()