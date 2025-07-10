"""
MCP-Aware Slack Client
Wraps MCP Slack server calls for project-specific use
"""

import os
import json
import httpx
import logging
from typing import Dict, Optional, Any
from ..slack_config import slack_config

logger = logging.getLogger(__name__)

class MCPSlackClient:
    """Client for interacting with Slack via MCP server"""
    
    def __init__(self):
        self.mcp_url = "http://localhost:8017"
        self.headers = {"Content-Type": "application/json"}
        
    async def _call_mcp_tool(self, tool_name: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Call an MCP tool via HTTP"""
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.mcp_url}/tools/{tool_name}",
                headers=self.headers,
                json=params,
                timeout=30.0
            )
            
        if response.status_code != 200:
            raise Exception(f"MCP call failed: {response.text}")
            
        return response.json()
    
    async def post_message(self, text: str, channel: Optional[str] = None, 
                          job_type: Optional[str] = None, urgency: str = "normal") -> Dict[str, Any]:
        """Post a message, automatically routing to appropriate channel"""
        
        # Determine channel if not specified
        if not channel:
            if job_type:
                channel = slack_config.get_channel_for_job(job_type, urgency)
            else:
                channel = slack_config.channels["recruitment"]["notifications"]
        
        # Format channel
        channel = slack_config.format_channel_id(channel)
        
        try:
            result = await self._call_mcp_tool("slack_post_message", {
                "channel_id": channel,
                "text": text
            })
            
            logger.info(f"Posted message to {channel}")
            return result
            
        except Exception as e:
            logger.error(f"Failed to post to Slack: {e}")
            # Fallback to webhook if available
            return await self._fallback_webhook(text, channel)
    
    async def post_candidate_notification(self, candidate_info: Dict, 
                                        analysis_result: Dict, 
                                        job_info: Dict) -> Optional[str]:
        """Post candidate notification to appropriate channel based on score and job type"""
        
        match_score = analysis_result.get('match_score', 0)
        job_type = job_info.get('type', job_info.get('title', ''))
        
        # Route to appropriate channel
        channel = slack_config.get_channel_by_match_score(match_score, job_type)
        
        # Format the message
        from ..utils.slack_notifier import SlackNotifier
        notifier = SlackNotifier()
        message = notifier.format_manager_notification(candidate_info, analysis_result, job_info)
        
        try:
            # Post main message
            result = await self.post_message(message, channel=channel)
            
            if result.get('success'):
                thread_ts = result.get('timestamp')
                
                # Add reactions based on score
                if match_score >= 90:
                    await self.add_reaction(channel, thread_ts, "fire")
                elif match_score >= 75:
                    await self.add_reaction(channel, thread_ts, "thumbsup")
                
                # Add detailed analysis in thread
                detailed = notifier.format_analysis_summary(analysis_result)
                await self.reply_to_thread(channel, thread_ts, detailed)
                
                return thread_ts
                
        except Exception as e:
            logger.error(f"Failed to post candidate notification: {e}")
            return None
    
    async def reply_to_thread(self, channel: str, thread_ts: str, text: str) -> Dict[str, Any]:
        """Reply to a thread"""
        
        channel = slack_config.format_channel_id(channel)
        
        return await self._call_mcp_tool("slack_reply_to_thread", {
            "channel_id": channel,
            "thread_ts": thread_ts,
            "text": text
        })
    
    async def add_reaction(self, channel: str, timestamp: str, reaction: str) -> Dict[str, Any]:
        """Add a reaction to a message"""
        
        channel = slack_config.format_channel_id(channel)
        
        return await self._call_mcp_tool("slack_add_reaction", {
            "channel_id": channel,
            "timestamp": timestamp,
            "reaction": reaction
        })
    
    async def _fallback_webhook(self, text: str, channel: str) -> Dict[str, Any]:
        """Fallback to webhook if MCP fails"""
        
        webhook_url = os.getenv("SLACK_WEBHOOK_URL")
        if not webhook_url or webhook_url == "your_slack_webhook_url_here":
            return {"success": False, "error": "No webhook URL configured"}
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    webhook_url,
                    json={
                        "text": text,
                        "channel": channel
                    }
                )
                
            return {
                "success": response.status_code == 200,
                "fallback": True,
                "channel": channel
            }
            
        except Exception as e:
            logger.error(f"Webhook fallback failed: {e}")
            return {"success": False, "error": str(e)}


# Singleton instance
mcp_slack_client = MCPSlackClient()