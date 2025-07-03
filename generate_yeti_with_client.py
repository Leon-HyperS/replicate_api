#!/usr/bin/env python3
"""
Generate Yeti video using the replicate_client.py
"""

from replicate_client import create_client
import json
import os
from datetime import datetime

# Your provided configuration
config = {
    "shot": {
        "composition": "Medium shot, vertical format, handheld camera",
        "camera_motion": "slight natural shake",
        "frame_rate": "30fps",
        "film_grain": "none"
    },
    "subject": {
        "description": "A towering, snow-white Yeti with shaggy fur and expressive blue eyes",
        "wardrobe": "slightly oversized white T-shirt with the name 'Emily' in bold, blood-red letters across the chest"
    },
    "scene": {
        "location": "lush forest clearing",
        "time_of_day": "daytime",
        "environment": "soft sunlight, haze from smoke lingering in the forest air"
    },
    "visual_details": {
        "action": "Yeti exhales smoke, stares into camera, critiques Veo3's performance at fantasy/anime content",
        "props": "loosely rolled joint"
    },
    "cinematography": {
        "lighting": "natural sunlight with mild haze",
        "tone": "comedic, irreverent, satirical"
    },
    "audio": {
        "ambient": "forest quiet, faint birds, soft breeze",
        "dialogue": {
            "character": "Yeti",
            "line": "Hey Google… Veo3 is very bad at fantasy and anime. Fix that with Veo4… soon.",
            "subtitles": False
        },
        "effects": "exhale puff, faint cough"
    },
    "color_palette": "naturalistic forest tones, red shirt text providing strong contrast"
}

def create_prompt_from_config(config):
    """Convert the structured config into a natural language prompt."""
    prompt_parts = []
    
    # Shot composition
    shot = config['shot']
    prompt_parts.append(f"{shot['composition']} with {shot['camera_motion']}")
    
    # Subject description
    subject = config['subject']
    prompt_parts.append(f"{subject['description']} wearing {subject['wardrobe']}")
    
    # Scene setting
    scene = config['scene']
    prompt_parts.append(f"in a {scene['location']} during {scene['time_of_day']}, {scene['environment']}")
    
    # Visual action
    visual = config['visual_details']
    prompt_parts.append(f"The Yeti {visual['action']}")
    if 'props' in visual:
        prompt_parts.append(f"holding a {visual['props']}")
    
    # Cinematography
    cinema = config['cinematography']
    prompt_parts.append(f"Shot with {cinema['lighting']}, {cinema['tone']} tone")
    
    # Audio and dialogue
    audio = config['audio']
    if 'dialogue' in audio:
        dialogue = audio['dialogue']
        prompt_parts.append(f'The {dialogue["character"]} says: "{dialogue["line"]}"')
    
    # Visual style
    prompt_parts.append(f"Color palette: {config['color_palette']}")
    prompt_parts.append(f"{shot['frame_rate']}, {shot['film_grain']} film grain")
    
    return ". ".join(prompt_parts)

if __name__ == "__main__":
    # Initialize client
    client = create_client()
    
    # Create prompt
    prompt = create_prompt_from_config(config)
    
    # Save prompt for reference
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    os.makedirs("prompts", exist_ok=True)
    os.makedirs("outputs", exist_ok=True)
    
    prompt_filename = f"prompts/yeti_prompt_{timestamp}.json"
    prompt_data = {
        "config": config,
        "generated_prompt": prompt,
        "timestamp": timestamp
    }
    
    with open(prompt_filename, "w") as f:
        json.dump(prompt_data, f, indent=2)
    
    print(f"Saved prompt configuration to: {prompt_filename}")
    print(f"\nGenerated prompt:\n{prompt}\n")
    
    # Run the model
    print("Generating video with Replicate...")
    try:
        output = client.run_model(
            "google/veo-3",
            input_data={"prompt": prompt}
        )
        
        # The output should be a URL or list of URLs
        if output:
            # Save the video
            saved_files = client.save_image_output(
                output, 
                "outputs", 
                f"yeti_video_{timestamp}"
            )
            print(f"\n✅ Success!")
            print(f"Video saved to: {saved_files[0] if saved_files else 'outputs/'}")
        else:
            print("No output received from the model")
            
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\nMake sure you have:")
        print("1. Installed dependencies: pip install -r requirements.txt")
        print("2. Set your API token in .env file")