#!/usr/bin/env python3
"""
Manages candidate documents in organized structure
"""

import os
import shutil
from typing import Dict, List
from datetime import datetime

class CandidateDocumentManager:
    """Organize candidate documents properly"""
    
    def __init__(self, base_path: str = "/tmp/candidate_docs"):
        self.base_path = base_path
        os.makedirs(base_path, exist_ok=True)
    
    def store_questionnaire(self, candidate_id: int, pdf_path: str) -> str:
        """Store questionnaire in organized structure"""
        
        # Create candidate folder
        candidate_folder = os.path.join(self.base_path, f"candidate_{candidate_id}")
        os.makedirs(candidate_folder, exist_ok=True)
        
        # Create questionnaire subfolder with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        quest_folder = os.path.join(candidate_folder, f"questionnaire_{timestamp}")
        os.makedirs(quest_folder, exist_ok=True)
        
        # Extract PDF pages here (using existing logic)
        # ... 
        
        return quest_folder
    
    def get_latest_questionnaire(self, candidate_id: int) -> str:
        """Get the latest questionnaire folder for a candidate"""
        
        candidate_folder = os.path.join(self.base_path, f"candidate_{candidate_id}")
        if not os.path.exists(candidate_folder):
            return None
        
        # Find latest questionnaire folder
        quest_folders = [f for f in os.listdir(candidate_folder) if f.startswith('questionnaire_')]
        if quest_folders:
            quest_folders.sort()
            return os.path.join(candidate_folder, quest_folders[-1])
        
        return None
    
    def cleanup_old_files(self, days_to_keep: int = 7):
        """Clean up old candidate files"""
        # Implementation to remove old files
        pass