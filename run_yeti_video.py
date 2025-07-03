#!/usr/bin/env python3
"""
Standalone script to generate the Yeti video.
Run this after installing dependencies: pip install -r requirements.txt
"""

import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from generate_yeti_video import generate_video
except ImportError as e:
    print("Error: Unable to import required modules.")
    print("\nPlease install the required dependencies:")
    print("  pip install -r requirements.txt")
    print("\nOr if using pip3:")
    print("  pip3 install -r requirements.txt")
    sys.exit(1)

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

if __name__ == "__main__":
    try:
        print("Starting Yeti video generation...")
        video_path, prompt_path = generate_video(config)
        print(f"\n✅ Success!")
        print(f"Video saved to: {video_path}")
        print(f"Prompt saved to: {prompt_path}")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\nIf you see authentication errors, make sure your .env file contains:")
        print("REPLICATE_API_TOKEN=your_token_here")
        sys.exit(1)