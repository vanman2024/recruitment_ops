#!/usr/bin/env python3
"""
Slack Notification Module for Recruitment
Sends formatted notifications to hiring managers via Slack
"""

import json
import logging
from typing import Dict, Optional, List
from datetime import datetime

# Import Slack MCP tools
# These are available in your environment as shown in the MCP tools list
# We'll use them via function calls in the actual implementation

logger = logging.getLogger(__name__)


class SlackNotifier:
    """Handle Slack notifications for recruitment workflow"""
    
    def __init__(self):
        self.default_channel = None
        
    def format_manager_notification(self, 
                                  candidate_info: Dict, 
                                  analysis_result: Dict,
                                  job_info: Dict) -> str:
        """Format a notification message for managers"""
        
        candidate_name = f"{candidate_info.get('first_name', '')} {candidate_info.get('last_name', '')}".strip()
        job_title = job_info.get('title', 'Unknown Position')
        company = job_info.get('company', 'Unknown Company')
        match_score = analysis_result.get('match_score', 'N/A')
        
        # Build message blocks
        message = f"""
🔔 *New Candidate Ready for Manager Review*

*Candidate:* {candidate_name}
*Position:* {job_title} at {company}
*Match Score:* {match_score}% 
*Status:* Manager Review Needed

📊 *Key Highlights:*
"""
        
        # Add key qualifications
        if 'key_qualifications' in analysis_result:
            for qual in analysis_result['key_qualifications'][:5]:
                message += f"• {qual}\n"
        
        # Add equipment experience
        if 'equipment_brands' in analysis_result:
            brands = ", ".join(analysis_result['equipment_brands'])
            message += f"\n*Equipment Experience:* {brands}"
        
        # Add years of experience
        if 'total_experience_years' in analysis_result:
            message += f"\n*Years of Experience:* {analysis_result['total_experience_years']}"
        
        # Add certifications
        if 'certifications' in analysis_result:
            certs = ", ".join(analysis_result['certifications'][:3])
            message += f"\n*Key Certifications:* {certs}"
        
        # Add action items
        message += f"""

📋 *Next Steps:*
1. Review full analysis in CATS
2. Schedule screening call if interested
3. Provide feedback in thread below

🔗 *Links:*
• <https://cats.example.com/candidates/{candidate_info.get('id')}|View in CATS>
• <https://cats.example.com/jobs/{job_info.get('id')}|View Job Posting>
"""
        
        # Add timestamp
        message += f"\n\n_Analysis completed at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}_"
        
        return message
    
    def format_analysis_summary(self, analysis_result: Dict) -> str:
        """Format detailed analysis for thread reply"""
        
        summary = "📄 *Detailed Analysis Summary*\n\n"
        
        # Resume Analysis
        if 'resume_analysis' in analysis_result:
            summary += "*Resume Highlights:*\n"
            resume = analysis_result['resume_analysis']
            
            if 'current_position' in resume:
                summary += f"• Current: {resume['current_position']}\n"
            
            if 'key_achievements' in resume:
                summary += "\n*Key Achievements:*\n"
                for achievement in resume['key_achievements'][:3]:
                    summary += f"• {achievement}\n"
        
        # Questionnaire Analysis
        if 'questionnaire_analysis' in analysis_result:
            summary += "\n*Questionnaire Responses:*\n"
            quest = analysis_result['questionnaire_analysis']
            
            if 'equipment_operated' in quest:
                summary += f"• Equipment: {', '.join(quest['equipment_operated'])}\n"
            
            if 'specializations' in quest:
                summary += f"• Specializations: {', '.join(quest['specializations'])}\n"
            
            if 'willing_to_relocate' in quest:
                summary += f"• Willing to Relocate: {'Yes' if quest['willing_to_relocate'] else 'No'}\n"
        
        # Match Analysis
        if 'match_analysis' in analysis_result:
            summary += "\n*Job Match Analysis:*\n"
            match = analysis_result['match_analysis']
            
            if 'strengths' in match:
                summary += "\n✅ *Strengths:*\n"
                for strength in match['strengths'][:3]:
                    summary += f"• {strength}\n"
            
            if 'gaps' in match:
                summary += "\n⚠️ *Potential Gaps:*\n"
                for gap in match['gaps'][:2]:
                    summary += f"• {gap}\n"
            
            if 'recommendation' in match:
                summary += f"\n💡 *AI Recommendation:* {match['recommendation']}\n"
        
        return summary
    
    def send_notification(self, channel_id: str, message: str) -> Optional[Dict]:
        """Send notification to Slack channel"""
        
        try:
            # In actual implementation, this would call the Slack MCP tool
            # For now, we'll return a mock response showing what would happen
            
            logger.info(f"Sending Slack notification to channel {channel_id}")
            
            # This would be the actual MCP call:
            # result = mcp__slack__slack_post_message(
            #     channel_id=channel_id,
            #     text=message
            # )
            
            # Mock response for development
            result = {
                'ok': True,
                'channel': channel_id,
                'ts': '1234567890.123456',
                'message': {'text': message}
            }
            
            return result
            
        except Exception as e:
            logger.error(f"Failed to send Slack notification: {str(e)}")
            return None
    
    def send_thread_reply(self, channel_id: str, thread_ts: str, message: str) -> Optional[Dict]:
        """Send a reply to an existing thread"""
        
        try:
            logger.info(f"Sending thread reply to {thread_ts} in channel {channel_id}")
            
            # This would be the actual MCP call:
            # result = mcp__slack__slack_reply_to_thread(
            #     channel_id=channel_id,
            #     thread_ts=thread_ts,
            #     text=message
            # )
            
            # Mock response
            result = {
                'ok': True,
                'channel': channel_id,
                'ts': '1234567890.123457',
                'thread_ts': thread_ts
            }
            
            return result
            
        except Exception as e:
            logger.error(f"Failed to send thread reply: {str(e)}")
            return None
    
    def add_reaction(self, channel_id: str, timestamp: str, reaction: str) -> bool:
        """Add a reaction to a message"""
        
        try:
            # This would be the actual MCP call:
            # result = mcp__slack__slack_add_reaction(
            #     channel_id=channel_id,
            #     timestamp=timestamp,
            #     reaction=reaction
            # )
            
            logger.info(f"Added reaction :{reaction}: to message {timestamp}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to add reaction: {str(e)}")
            return False
    
    def create_recruitment_thread(self, 
                                channel_id: str, 
                                candidate_info: Dict,
                                analysis_result: Dict,
                                job_info: Dict) -> Optional[str]:
        """Create a complete recruitment thread with all information"""
        
        try:
            # Send main notification
            main_message = self.format_manager_notification(
                candidate_info, analysis_result, job_info
            )
            
            main_result = self.send_notification(channel_id, main_message)
            if not main_result:
                return None
            
            thread_ts = main_result.get('ts')
            
            # Add detailed analysis as thread reply
            detailed_summary = self.format_analysis_summary(analysis_result)
            self.send_thread_reply(channel_id, thread_ts, detailed_summary)
            
            # Add initial reaction to indicate AI processing
            self.add_reaction(channel_id, thread_ts, "robot_face")
            
            # Add priority reaction based on match score
            match_score = analysis_result.get('match_score', 0)
            if match_score >= 90:
                self.add_reaction(channel_id, thread_ts, "fire")
            elif match_score >= 75:
                self.add_reaction(channel_id, thread_ts, "thumbsup")
            
            return thread_ts
            
        except Exception as e:
            logger.error(f"Failed to create recruitment thread: {str(e)}")
            return None


# Utility functions for Slack formatting
def format_candidate_summary_for_slack(candidate_data: Dict) -> str:
    """Format candidate data for Slack message"""
    
    summary_parts = []
    
    # Basic info
    if 'name' in candidate_data:
        summary_parts.append(f"*Name:* {candidate_data['name']}")
    
    if 'location' in candidate_data:
        summary_parts.append(f"*Location:* {candidate_data['location']}")
    
    if 'experience_years' in candidate_data:
        summary_parts.append(f"*Experience:* {candidate_data['experience_years']} years")
    
    # Skills
    if 'skills' in candidate_data:
        skills = ", ".join(candidate_data['skills'][:5])
        summary_parts.append(f"*Top Skills:* {skills}")
    
    return "\n".join(summary_parts)


def create_slack_blocks(candidate_info: Dict, analysis_result: Dict) -> List[Dict]:
    """Create rich Slack blocks for better formatting"""
    
    blocks = [
        {
            "type": "header",
            "text": {
                "type": "plain_text",
                "text": "🔔 New Candidate for Review"
            }
        },
        {
            "type": "section",
            "fields": [
                {
                    "type": "mrkdwn",
                    "text": f"*Candidate:*\n{candidate_info.get('first_name')} {candidate_info.get('last_name')}"
                },
                {
                    "type": "mrkdwn",
                    "text": f"*Match Score:*\n{analysis_result.get('match_score')}%"
                }
            ]
        },
        {
            "type": "divider"
        }
    ]
    
    # Add key qualifications
    if 'key_qualifications' in analysis_result:
        qual_text = "\n".join([f"• {q}" for q in analysis_result['key_qualifications'][:5]])
        blocks.append({
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"*Key Qualifications:*\n{qual_text}"
            }
        })
    
    # Add actions
    blocks.append({
        "type": "actions",
        "elements": [
            {
                "type": "button",
                "text": {
                    "type": "plain_text",
                    "text": "View in CATS"
                },
                "url": f"https://cats.example.com/candidates/{candidate_info.get('id')}"
            },
            {
                "type": "button",
                "text": {
                    "type": "plain_text",
                    "text": "Schedule Interview"
                },
                "style": "primary",
                "value": f"schedule_{candidate_info.get('id')}"
            }
        ]
    })
    
    return blocks


# Example usage
if __name__ == "__main__":
    notifier = SlackNotifier()
    
    # Test data
    test_candidate = {
        'id': '12345',
        'first_name': 'Jeff',
        'last_name': 'Miller'
    }
    
    test_analysis = {
        'match_score': 95,
        'key_qualifications': [
            '15 years Heavy Equipment experience',
            'Red Seal certified',
            'CAT & Komatsu specialist'
        ],
        'equipment_brands': ['CAT', 'Komatsu', 'Hitachi'],
        'total_experience_years': 15,
        'certifications': ['Red Seal HET', 'Class 1', 'First Aid']
    }
    
    test_job = {
        'id': '67890',
        'title': 'Shovel Technician',
        'company': 'Big Mining Corp'
    }
    
    # Format message
    message = notifier.format_manager_notification(
        test_candidate, test_analysis, test_job
    )
    
    print("Sample Slack Notification:")
    print("-" * 50)
    print(message)