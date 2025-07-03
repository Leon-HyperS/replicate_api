"""
Google Veo3 video generation module
"""

from typing import Dict, Any, List, Optional
from .base import BaseModule


class Veo3Module(BaseModule):
    """Module for Google Veo3 video generation"""
    
    @property
    def model_type(self) -> str:
        return "veo3"
    
    def get_model_name(self) -> str:
        return "google/veo-3"
    
    def build_prompt(self, config: Dict[str, Any]) -> str:
        """
        Build a natural language prompt from structured config
        
        Config structure expected:
        {
            "shot": {...},
            "subject": {...},
            "scene": {...},
            "visual_details": {...},
            "cinematography": {...},
            "audio": {...},
            "color_palette": "..."
        }
        """
        prompt_parts = []
        
        # Shot composition
        if 'shot' in config:
            shot = config['shot']
            shot_desc = []
            if 'composition' in shot:
                shot_desc.append(shot['composition'])
            if 'camera_motion' in shot:
                shot_desc.append(f"with {shot['camera_motion']}")
            if shot_desc:
                prompt_parts.append(" ".join(shot_desc))
        
        # Subject description
        if 'subject' in config:
            subject = config['subject']
            subject_parts = []
            if 'description' in subject:
                subject_parts.append(subject['description'])
            if 'wardrobe' in subject:
                subject_parts.append(f"wearing {subject['wardrobe']}")
            if subject_parts:
                prompt_parts.append(" ".join(subject_parts))
        
        # Scene setting
        if 'scene' in config:
            scene = config['scene']
            scene_parts = []
            if 'location' in scene:
                scene_parts.append(f"in a {scene['location']}")
            if 'time_of_day' in scene:
                scene_parts.append(f"during {scene['time_of_day']}")
            if 'environment' in scene:
                scene_parts.append(scene['environment'])
            if scene_parts:
                prompt_parts.append(" ".join(scene_parts))
        
        # Visual action and details
        if 'visual_details' in config:
            visual = config['visual_details']
            if 'action' in visual:
                action_desc = visual['action']
                # Ensure proper subject reference
                if 'subject' in config and 'description' in config['subject']:
                    # Extract subject type (e.g., "Yeti" from "A towering, snow-white Yeti...")
                    subject_desc = config['subject']['description']
                    subject_type = self._extract_subject_type(subject_desc)
                    if subject_type and not action_desc.lower().startswith(('the', 'a', 'an')):
                        action_desc = f"The {subject_type} {action_desc}"
                prompt_parts.append(action_desc)
            
            if 'props' in visual:
                prompt_parts.append(f"holding a {visual['props']}")
        
        # Cinematography
        if 'cinematography' in config:
            cinema = config['cinematography']
            cinema_parts = []
            if 'lighting' in cinema:
                cinema_parts.append(f"Shot with {cinema['lighting']}")
            if 'tone' in cinema:
                cinema_parts.append(f"{cinema['tone']} tone")
            if cinema_parts:
                prompt_parts.append(", ".join(cinema_parts))
        
        # Audio and dialogue
        if 'audio' in config:
            audio = config['audio']
            if 'dialogue' in audio and isinstance(audio['dialogue'], dict):
                dialogue = audio['dialogue']
                if 'character' in dialogue and 'line' in dialogue:
                    character = dialogue['character']
                    line = dialogue['line']
                    prompt_parts.append(f'The {character} says: "{line}"')
            
            # Add ambient audio description if provided
            if 'ambient' in audio:
                prompt_parts.append(f"Ambient sound: {audio['ambient']}")
            
            if 'effects' in audio:
                prompt_parts.append(f"Sound effects: {audio['effects']}")
        
        # Visual style and color palette
        style_parts = []
        if 'color_palette' in config:
            style_parts.append(f"Color palette: {config['color_palette']}")
        
        # Technical specifications from shot
        if 'shot' in config:
            shot = config['shot']
            if 'frame_rate' in shot:
                style_parts.append(shot['frame_rate'])
            if 'film_grain' in shot:
                style_parts.append(f"{shot['film_grain']} film grain")
        
        if style_parts:
            prompt_parts.append(". ".join(style_parts))
        
        # Join all parts with proper punctuation
        prompt = ". ".join(prompt_parts)
        
        # Clean up any double periods or spaces
        prompt = prompt.replace("..", ".")
        prompt = prompt.replace("  ", " ")
        
        return prompt
    
    def get_model_params(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract Veo3-specific parameters from config
        
        Currently Veo3 only takes a prompt parameter, but this method
        allows for future expansion if more parameters are added.
        """
        params = {}
        
        # Add any model-specific parameters here
        # For now, Veo3 only needs the prompt which is added in generate()
        
        # Example of potential future parameters:
        # if 'generation_params' in config:
        #     gen_params = config['generation_params']
        #     if 'duration' in gen_params:
        #         params['duration'] = gen_params['duration']
        #     if 'resolution' in gen_params:
        #         params['resolution'] = gen_params['resolution']
        
        return params
    
    def _extract_subject_type(self, description: str) -> Optional[str]:
        """
        Extract the main subject type from a description
        e.g., "A towering, snow-white Yeti" -> "Yeti"
        """
        # Common subject words to look for
        subject_words = ['yeti', 'person', 'character', 'creature', 'animal', 
                        'robot', 'alien', 'monster', 'being', 'figure']
        
        description_lower = description.lower()
        for word in subject_words:
            if word in description_lower:
                # Capitalize properly
                return word.capitalize()
        
        # If no common subject found, try to extract the last noun
        words = description.split()
        for word in reversed(words):
            # Simple heuristic: capitalized words might be proper nouns/subjects
            if word[0].isupper() and len(word) > 2:
                return word
        
        return None
    
    def get_output_extension(self) -> str:
        """Veo3 generates MP4 videos"""
        return '.mp4'