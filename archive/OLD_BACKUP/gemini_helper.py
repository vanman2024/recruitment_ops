"""
Helper module to interact with Gemini MCP tool directly
"""

import json
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


class GeminiHelper:
    """Helper class to use Gemini MCP for document analysis"""
    
    def __init__(self, model="gemini-1.5-pro"):
        self.model = model
    
    def analyze_image(self, image_path, prompt):
        """
        Analyze an image using Gemini
        
        Note: This is a placeholder that should be called from Claude Code
        which has access to the MCP tools
        """
        # In actual use, this would be called through the MCP tool
        # For now, return a message indicating manual intervention needed
        return {
            "status": "manual_required",
            "message": f"Please use mcp__gemini__analyze_image with image_path='{image_path}' and prompt from questionnaire_analyzer.txt",
            "model": self.model
        }
    
    def analyze_document(self, document_path, prompt):
        """
        Analyze a document using Gemini
        """
        return {
            "status": "manual_required", 
            "message": f"Please use mcp__gemini__analyze_document with document_path='{document_path}'",
            "model": self.model
        }


# Example usage function for testing with Claude Code
def test_gemini_analysis():
    """
    Example of how to use Gemini MCP for candidate processing
    This should be run within Claude Code environment
    """
    
    # Load the questionnaire prompt
    prompt_path = Path(__file__).parent / "prompts" / "questionnaire_analyzer.txt"
    with open(prompt_path, 'r') as f:
        prompt = f.read()
    
    # Example image path
    image_path = "/mnt/c/Users/angel/Downloads/Jeff_Miller_Images/page_003.jpg"
    
    print(f"To analyze the questionnaire page, use:")
    print(f"mcp__gemini__analyze_image(")
    print(f'  image_path="{image_path}",')
    print(f'  prompt=<questionnaire_analyzer_prompt>,')
    print(f'  model="gemini-1.5-pro"')
    print(f")")