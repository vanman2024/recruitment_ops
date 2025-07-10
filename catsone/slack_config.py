"""
Slack Configuration for Recruitment Ops
Maps project-specific channels and settings
"""

import os
from typing import Dict, Optional

class SlackConfig:
    """Project-specific Slack configuration"""
    
    def __init__(self):
        # Get from environment or use defaults
        self.workspace_id = os.getenv("SLACK_TEAM_ID", "")
        
        # Project-specific channel mappings
        self.channels = {
            "recruitment": {
                "notifications": os.getenv("SLACK_CHANNEL_RECRUITMENT", "#recruitment-notifications"),
                "managers": os.getenv("SLACK_CHANNEL_MANAGERS", "#hiring-managers"),
                "urgent": os.getenv("SLACK_CHANNEL_URGENT", "#urgent-hires")
            },
            "skilled_trades": {
                "notifications": os.getenv("SLACK_CHANNEL_TRADES", "#skilled-trades-jobs"),
                "equipment": os.getenv("SLACK_CHANNEL_EQUIPMENT", "#equipment-operators"),
                "certifications": os.getenv("SLACK_CHANNEL_CERTS", "#certifications-alerts")
            }
        }
        
        # Notification preferences by job type
        self.job_type_channels = {
            "heavy_equipment": self.channels["skilled_trades"]["equipment"],
            "skilled_trades": self.channels["skilled_trades"]["notifications"],
            "management": self.channels["recruitment"]["managers"],
            "urgent": self.channels["recruitment"]["urgent"]
        }
        
    def get_channel_for_job(self, job_type: str, urgency: str = "normal") -> str:
        """Get appropriate channel based on job type and urgency"""
        
        if urgency == "urgent":
            return self.channels["recruitment"]["urgent"]
        
        # Map job types to channels
        job_type_lower = job_type.lower()
        
        if "equipment" in job_type_lower or "operator" in job_type_lower:
            return self.channels["skilled_trades"]["equipment"]
        elif "manager" in job_type_lower or "supervisor" in job_type_lower:
            return self.channels["recruitment"]["managers"]
        elif any(trade in job_type_lower for trade in ["mechanic", "technician", "electrician"]):
            return self.channels["skilled_trades"]["notifications"]
        else:
            return self.channels["recruitment"]["notifications"]
    
    def get_channel_by_match_score(self, match_score: int, job_type: str) -> str:
        """Route to different channels based on match quality"""
        
        if match_score >= 95:
            # High-priority candidates go to managers
            return self.channels["recruitment"]["managers"]
        elif match_score >= 80:
            # Good matches to appropriate category
            return self.get_channel_for_job(job_type)
        else:
            # Lower matches to general notifications
            return self.channels["recruitment"]["notifications"]
    
    def format_channel_id(self, channel_name: str) -> str:
        """Ensure channel name is properly formatted"""
        
        # If it's already a channel ID (starts with C), return as-is
        if channel_name.startswith('C') and len(channel_name) > 8:
            return channel_name
        
        # Ensure it starts with #
        if not channel_name.startswith('#'):
            channel_name = f"#{channel_name}"
            
        return channel_name


# Global instance
slack_config = SlackConfig()