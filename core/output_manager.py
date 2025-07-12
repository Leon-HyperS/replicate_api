"""
Output management and organization
"""

import json
import shutil
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
import csv


class OutputManager:
    """Manage and organize generated outputs"""
    
    def __init__(self, base_dir: Path = Path("outputs")):
        """
        Initialize the output manager
        
        Args:
            base_dir: Base directory for all outputs
        """
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)
        self.history_file = self.base_dir / "generation_history.json"
        self.history = self._load_history()
    
    def get_output_dir(self, model_type: str, config_name: Optional[str] = None) -> Path:
        """
        Get the output directory for a specific model and config
        
        Args:
            model_type: Type of model (e.g., 'veo3', 'flux')
            config_name: Optional config name for organization
            
        Returns:
            Path to output directory
        """
        if config_name:
            output_dir = self.base_dir / model_type / config_name
        else:
            output_dir = self.base_dir / model_type / "misc"
        
        output_dir.mkdir(parents=True, exist_ok=True)
        return output_dir
    
    def record_generation(
        self,
        model_type: str,
        config_name: str,
        metadata: Dict[str, Any],
        output_files: List[Path]
    ) -> str:
        """
        Record a generation in history
        
        Args:
            model_type: Type of model used
            config_name: Name of config used
            metadata: Generation metadata
            output_files: List of generated files
            
        Returns:
            Generation ID
        """
        generation_id = f"{model_type}_{config_name}_{metadata['timestamp']}"
        
        record = {
            "id": generation_id,
            "model_type": model_type,
            "config_name": config_name,
            "timestamp": metadata['timestamp'],
            "metadata": metadata,
            "output_files": [str(f) for f in output_files]
        }
        
        self.history[generation_id] = record
        self._save_history()
        
        return generation_id
    
    def get_latest_outputs(self, model_type: Optional[str] = None, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get the latest generated outputs
        
        Args:
            model_type: Filter by model type
            limit: Maximum number of results
            
        Returns:
            List of generation records
        """
        records = list(self.history.values())
        
        # Filter by model type if specified
        if model_type:
            records = [r for r in records if r['model_type'] == model_type]
        
        # Sort by timestamp (newest first)
        records.sort(key=lambda x: x['timestamp'], reverse=True)
        
        return records[:limit]
    
    def get_outputs_by_config(self, config_name: str) -> List[Dict[str, Any]]:
        """
        Get all outputs generated with a specific config
        
        Args:
            config_name: Configuration name
            
        Returns:
            List of generation records
        """
        records = []
        for record in self.history.values():
            if record.get('config_name') == config_name:
                records.append(record)
        
        records.sort(key=lambda x: x['timestamp'], reverse=True)
        return records
    
    def organize_by_date(self):
        """Reorganize outputs into date-based folders"""
        for record in self.history.values():
            timestamp = record['timestamp']
            date_str = timestamp[:8]  # YYYYMMDD
            
            for file_path_str in record['output_files']:
                file_path = Path(file_path_str)
                if file_path.exists():
                    # Create date-based directory
                    model_type = record['model_type']
                    date_dir = self.base_dir / model_type / date_str
                    date_dir.mkdir(parents=True, exist_ok=True)
                    
                    # Move file
                    new_path = date_dir / file_path.name
                    if not new_path.exists():
                        shutil.move(str(file_path), str(new_path))
                        print(f"Moved {file_path.name} to {date_dir}")
    
    def export_history(self, format: str = "json", output_path: Optional[Path] = None) -> Path:
        """
        Export generation history
        
        Args:
            format: Export format ('json' or 'csv')
            output_path: Optional output path
            
        Returns:
            Path to exported file
        """
        if not output_path:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = self.base_dir / f"history_export_{timestamp}.{format}"
        
        if format == "csv":
            self._export_csv(output_path)
        else:
            self._export_json(output_path)
        
        return output_path
    
    def cleanup_old_outputs(self, days: int = 30, dry_run: bool = True) -> List[Path]:
        """
        Clean up outputs older than specified days
        
        Args:
            days: Age threshold in days
            dry_run: If True, only show what would be deleted
            
        Returns:
            List of deleted/would-be-deleted files
        """
        from datetime import datetime, timedelta
        
        threshold = datetime.now() - timedelta(days=days)
        threshold_str = threshold.strftime("%Y%m%d")
        
        files_to_delete = []
        
        for record in self.history.values():
            if record['timestamp'][:8] < threshold_str:
                for file_path_str in record['output_files']:
                    file_path = Path(file_path_str)
                    if file_path.exists():
                        files_to_delete.append(file_path)
                        if not dry_run:
                            file_path.unlink()
                            print(f"Deleted: {file_path}")
        
        if dry_run and files_to_delete:
            print(f"Would delete {len(files_to_delete)} files older than {days} days")
        
        return files_to_delete
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get statistics about generations
        
        Returns:
            Dictionary with statistics
        """
        stats = {
            "total_generations": len(self.history),
            "by_model": {},
            "by_config": {},
            "by_date": {},
            "total_files": 0
        }
        
        for record in self.history.values():
            # By model
            model = record['model_type']
            stats['by_model'][model] = stats['by_model'].get(model, 0) + 1
            
            # By config
            config = record['config_name']
            stats['by_config'][config] = stats['by_config'].get(config, 0) + 1
            
            # By date
            date = record['timestamp'][:8]
            stats['by_date'][date] = stats['by_date'].get(date, 0) + 1
            
            # Total files
            stats['total_files'] += len(record['output_files'])
        
        return stats
    
    def _load_history(self) -> Dict[str, Any]:
        """Load generation history from file"""
        if self.history_file.exists():
            with open(self.history_file, 'r') as f:
                return json.load(f)
        return {}
    
    def _save_history(self):
        """Save generation history to file"""
        with open(self.history_file, 'w') as f:
            json.dump(self.history, f, indent=2)
    
    def _export_json(self, output_path: Path):
        """Export history as JSON"""
        with open(output_path, 'w') as f:
            json.dump(self.history, f, indent=2)
    
    def _export_csv(self, output_path: Path):
        """Export history as CSV"""
        with open(output_path, 'w', newline='') as f:
            writer = csv.writer(f)
            
            # Header
            writer.writerow([
                'ID', 'Model', 'Config', 'Timestamp', 
                'Prompt', 'Output Files'
            ])
            
            # Data
            for record in self.history.values():
                prompt = record['metadata'].get('generated_prompt', '')
                files = ', '.join(record['output_files'])
                
                writer.writerow([
                    record['id'],
                    record['model_type'],
                    record['config_name'],
                    record['timestamp'],
                    prompt[:100] + '...' if len(prompt) > 100 else prompt,
                    files
                ])