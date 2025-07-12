"""
Prompt builder for converting structured configs to natural language
"""

from typing import Dict, Any, List, Optional


class PromptBuilder:
    """Generic prompt builder that can be extended for different styles"""
    
    def __init__(self, style: str = "descriptive"):
        """
        Initialize the prompt builder
        
        Args:
            style: Prompt style ('descriptive', 'narrative', 'technical')
        """
        self.style = style
    
    def build(self, config: Dict[str, Any], template: Optional[Dict[str, Any]] = None) -> str:
        """
        Build a prompt from config using the specified style
        
        Args:
            config: Configuration dictionary
            template: Optional template for prompt structure
            
        Returns:
            Natural language prompt
        """
        if self.style == "narrative":
            return self._build_narrative(config, template)
        elif self.style == "technical":
            return self._build_technical(config, template)
        else:  # descriptive (default)
            return self._build_descriptive(config, template)
    
    def _build_descriptive(self, config: Dict[str, Any], template: Optional[Dict[str, Any]] = None) -> str:
        """Build a descriptive prompt (default style)"""
        parts = []
        
        # Process each section in a logical order
        section_order = [
            'shot', 'subject', 'scene', 'visual_details', 
            'cinematography', 'audio', 'style', 'color_palette'
        ]
        
        for section in section_order:
            if section in config:
                section_text = self._process_section(section, config[section])
                if section_text:
                    parts.append(section_text)
        
        # Handle any additional fields not in standard order
        for key, value in config.items():
            if key not in section_order and isinstance(value, (str, dict)):
                section_text = self._process_section(key, value)
                if section_text:
                    parts.append(section_text)
        
        return ". ".join(parts)
    
    def _build_narrative(self, config: Dict[str, Any], template: Optional[Dict[str, Any]] = None) -> str:
        """Build a narrative-style prompt"""
        # Create a story-like description
        narrative_parts = []
        
        # Opening with scene
        if 'scene' in config:
            scene = config['scene']
            opening = f"The scene opens {self._format_scene(scene)}"
            narrative_parts.append(opening)
        
        # Introduce subject
        if 'subject' in config:
            subject = config['subject']
            intro = self._format_subject_narrative(subject)
            narrative_parts.append(intro)
        
        # Describe action
        if 'visual_details' in config and 'action' in config['visual_details']:
            action = config['visual_details']['action']
            narrative_parts.append(f"We see {action}")
        
        # Add remaining elements
        remaining = self._build_descriptive(
            {k: v for k, v in config.items() if k not in ['scene', 'subject', 'visual_details']}
        )
        if remaining:
            narrative_parts.append(remaining)
        
        return ". ".join(narrative_parts)
    
    def _build_technical(self, config: Dict[str, Any], template: Optional[Dict[str, Any]] = None) -> str:
        """Build a technical specification-style prompt"""
        specs = []
        
        # Format as technical specifications
        for key, value in config.items():
            if isinstance(value, dict):
                spec_text = self._format_technical_spec(key, value)
            else:
                spec_text = f"{key.upper()}: {value}"
            specs.append(spec_text)
        
        return " | ".join(specs)
    
    def _process_section(self, section_name: str, section_data: Any) -> str:
        """Process a config section into text"""
        if isinstance(section_data, str):
            return section_data
        
        if isinstance(section_data, dict):
            if section_name == 'shot':
                return self._format_shot(section_data)
            elif section_name == 'subject':
                return self._format_subject(section_data)
            elif section_name == 'scene':
                return self._format_scene(section_data)
            elif section_name == 'visual_details':
                return self._format_visual_details(section_data)
            elif section_name == 'cinematography':
                return self._format_cinematography(section_data)
            elif section_name == 'audio':
                return self._format_audio(section_data)
            else:
                # Generic dict formatting
                return self._format_generic_dict(section_data)
        
        return str(section_data)
    
    def _format_shot(self, shot: Dict[str, Any]) -> str:
        """Format shot composition details"""
        parts = []
        if 'composition' in shot:
            parts.append(shot['composition'])
        if 'camera_motion' in shot:
            parts.append(f"with {shot['camera_motion']}")
        return " ".join(parts)
    
    def _format_subject(self, subject: Dict[str, Any]) -> str:
        """Format subject description"""
        parts = []
        if 'description' in subject:
            parts.append(subject['description'])
        if 'wardrobe' in subject:
            parts.append(f"wearing {subject['wardrobe']}")
        return " ".join(parts)
    
    def _format_scene(self, scene: Dict[str, Any]) -> str:
        """Format scene setting"""
        parts = []
        if 'location' in scene:
            parts.append(f"in a {scene['location']}")
        if 'time_of_day' in scene:
            parts.append(f"during {scene['time_of_day']}")
        if 'environment' in scene:
            parts.append(scene['environment'])
        return " ".join(parts)
    
    def _format_visual_details(self, visual: Dict[str, Any]) -> str:
        """Format visual details and actions"""
        parts = []
        if 'action' in visual:
            parts.append(visual['action'])
        if 'props' in visual:
            parts.append(f"with {visual['props']}")
        return " ".join(parts)
    
    def _format_cinematography(self, cinema: Dict[str, Any]) -> str:
        """Format cinematography details"""
        parts = []
        if 'lighting' in cinema:
            parts.append(f"Shot with {cinema['lighting']}")
        if 'tone' in cinema:
            parts.append(f"{cinema['tone']} tone")
        return ", ".join(parts)
    
    def _format_audio(self, audio: Dict[str, Any]) -> str:
        """Format audio details"""
        parts = []
        if 'dialogue' in audio and isinstance(audio['dialogue'], dict):
            dialogue = audio['dialogue']
            if 'character' in dialogue and 'line' in dialogue:
                parts.append(f'{dialogue["character"]} says: "{dialogue["line"]}"')
        if 'ambient' in audio:
            parts.append(f"Ambient: {audio['ambient']}")
        if 'effects' in audio:
            parts.append(f"SFX: {audio['effects']}")
        return ". ".join(parts)
    
    def _format_generic_dict(self, data: Dict[str, Any]) -> str:
        """Format a generic dictionary"""
        parts = []
        for key, value in data.items():
            if isinstance(value, dict):
                parts.append(self._format_generic_dict(value))
            else:
                parts.append(f"{key}: {value}")
        return ", ".join(parts)
    
    def _format_subject_narrative(self, subject: Dict[str, Any]) -> str:
        """Format subject for narrative style"""
        desc = subject.get('description', 'The subject')
        wardrobe = subject.get('wardrobe', '')
        if wardrobe:
            return f"{desc}, dressed in {wardrobe}, enters the frame"
        return f"{desc} appears"
    
    def _format_technical_spec(self, key: str, value: Dict[str, Any]) -> str:
        """Format as technical specification"""
        specs = [f"{key.upper()}:"]
        for k, v in value.items():
            specs.append(f"{k}={v}")
        return " ".join(specs)