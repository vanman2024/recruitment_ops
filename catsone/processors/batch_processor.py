#!/usr/bin/env python3
"""
Batch process multiple questionnaire pages using Gemini's batch capabilities
Much faster than processing one by one
"""

import json
import asyncio
from pathlib import Path
from datetime import datetime
import logging
from typing import List, Dict

from config import GEMINI_BATCH_MODEL, OUTPUT_DIR

logger = logging.getLogger(__name__)


class BatchQuestionnaireProcessor:
    """Process multiple questionnaire pages in parallel using Gemini"""
    
    def __init__(self):
        self.model = GEMINI_BATCH_MODEL
        self.prompts_dir = Path(__file__).parent / "prompts"
        
    def load_prompt(self):
        """Load the questionnaire analyzer prompt"""
        prompt_path = self.prompts_dir / "questionnaire_analyzer.txt"
        with open(prompt_path, 'r') as f:
            return f.read()
    
    def create_batch_analysis_script(self, image_paths: List[Path], candidate_name: str = "Candidate"):
        """Create a Python script that processes all pages using Gemini batch"""
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        script_path = OUTPUT_DIR / f"batch_analysis_{candidate_name}_{timestamp}.py"
        
        script_content = [
            "#!/usr/bin/env python3",
            '"""',
            f'Batch analysis for {candidate_name}',
            f'Generated: {datetime.now().isoformat()}',
            '"""',
            '',
            'import json',
            'from pathlib import Path',
            '',
            '# Results will be collected here',
            'all_results = []',
            '',
            '# Prompt for questionnaire analysis',
            f'prompt_path = r"{self.prompts_dir / "questionnaire_analyzer.txt"}"',
            'with open(prompt_path, "r") as f:',
            '    prompt = f.read()',
            '',
            '# Process all pages using Gemini 2.5 Flash for speed',
            f'print("Processing {len(image_paths)} pages with Gemini 2.5 Flash...")',
            ''
        ]
        
        # Add batch processing using Gemini
        script_content.extend([
            '# Use mcp__gemini__batch_generate for parallel processing',
            'image_prompts = [',
        ])
        
        for idx, image_path in enumerate(image_paths):
            script_content.append(f'    {{')
            script_content.append(f'        "page": {idx + 1},')
            script_content.append(f'        "image_path": r"{image_path}",')
            script_content.append(f'        "prompt": f"Analyze this questionnaire page (Page {idx + 1}): {{prompt}}"')
            script_content.append(f'    }},')
        
        script_content.extend([
            ']',
            '',
            '# Process in batches of 5 for optimal performance',
            'batch_size = 5',
            'for i in range(0, len(image_prompts), batch_size):',
            '    batch = image_prompts[i:i+batch_size]',
            '    print(f"Processing batch {i//batch_size + 1}...")',
            '    ',
            '    # For each image in batch, analyze with Gemini',
            '    for item in batch:',
            '        result = mcp__gemini__analyze_image(',
            '            image_path=item["image_path"],',
            '            prompt=item["prompt"],',
            '            model="gemini-2.5-flash"  # Fast model for batch',
            '        )',
            '        all_results.append({',
            '            "page": item["page"],',
            '            "result": result',
            '        })',
            '',
            '# Merge all results',
            'merged_data = {',
            '    "equipment_brands": [],',
            '    "equipment_experience": {},',
            '    "certifications": {},',
            '    "skills": []',
            '}',
            '',
            'for page_result in all_results:',
            '    try:',
            '        result = page_result["result"]',
            '        if "analysis" in result:',
            '            json_str = result["analysis"]',
            '            if "```json" in json_str:',
            '                json_str = json_str.split("```json")[1].split("```")[0]',
            '            data = json.loads(json_str)',
            '            print(f"Page {page_result[\'page\']}: {list(data.keys())}")',
            '            # Merge logic here based on data structure',
            '    except Exception as e:',
            '        print(f"Error on page {page_result[\'page\']}: {e}")',
            '',
            '# Save results',
            f'output_file = r"{OUTPUT_DIR / f"{candidate_name}_batch_results_{timestamp}.json"}"',
            'with open(output_file, "w") as f:',
            '    json.dump({',
            f'        "candidate": "{candidate_name}",',
            '        "pages_processed": len(all_results),',
            '        "merged_data": merged_data,',
            '        "raw_results": all_results',
            '    }, f, indent=2)',
            '',
            'print(f"\\nResults saved to: {output_file}")'
        ])
        
        # Write the script
        with open(script_path, 'w') as f:
            f.write('\n'.join(script_content))
        
        return script_path
    
    def create_gemini_batch_request(self, image_paths: List[Path]) -> Dict:
        """Create a batch request for Gemini API"""
        prompt = self.load_prompt()
        
        requests = []
        for idx, image_path in enumerate(image_paths):
            requests.append({
                "contents": [{
                    "parts": [
                        {"text": f"Page {idx + 1} of questionnaire:\n{prompt}"},
                        {"file_data": {"file_uri": str(image_path)}}
                    ]
                }],
                "model": self.model
            })
        
        return {
            "requests": requests,
            "output_config": {
                "response_mime_type": "application/json"
            }
        }


def process_questionnaire_batch(image_dir: str, candidate_name: str = "Candidate"):
    """Main function to batch process questionnaire"""
    
    # Get all image files
    image_dir_path = Path(image_dir)
    image_files = sorted(image_dir_path.glob("page_*.jpg"))
    if not image_files:
        image_files = sorted(image_dir_path.glob("*.jpg"))
    
    print(f"Found {len(image_files)} images to process")
    
    # Create batch processor
    processor = BatchQuestionnaireProcessor()
    
    # Generate batch processing script
    script_path = processor.create_batch_analysis_script(image_files, candidate_name)
    
    print(f"\nBatch processing script created: {script_path}")
    print("\nTo process all pages at once, run the generated script in Claude Code")
    print("This will be MUCH faster than processing pages one by one")
    
    # Also create direct Gemini batch request
    batch_request = processor.create_gemini_batch_request(image_files)
    batch_file = OUTPUT_DIR / f"{candidate_name}_gemini_batch_request_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    
    with open(batch_file, 'w') as f:
        json.dump(batch_request, f, indent=2)
    
    print(f"\nGemini batch request saved to: {batch_file}")
    
    return script_path, batch_file


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python batch_processor.py <image_directory> [candidate_name]")
        sys.exit(1)
    
    image_dir = sys.argv[1]
    candidate_name = sys.argv[2] if len(sys.argv) > 2 else "Candidate"
    
    process_questionnaire_batch(image_dir, candidate_name)