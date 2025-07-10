# Candidate Processor

A simple application to process recruitment documents using Gemini LLM. Extracts only checked/filled information from questionnaires and creates clean email summaries.

## Features

- Converts PDF questionnaires to images for accurate checkbox detection
- Uses Gemini AI to identify only checked boxes and filled fields
- Merges data from multiple pages into a single summary
- Generates clean email format for managers
- Prepares data for CATS API integration

## Directory Structure

```
candidate-processor/
├── config.py                    # Configuration settings
├── prompts/                     # Prompt templates
│   └── questionnaire_analyzer.txt
├── process_candidate.py         # Main processing script
├── gemini_helper.py            # Gemini MCP helper
├── test_questionnaire_page.py  # Single page tester
├── process_jeff_miller.py      # Example workflow
├── temp/                       # Temporary image storage
└── output/                     # Generated summaries
```

## Setup

1. Ensure you have the required dependencies:
   ```bash
   pip install PyMuPDF python-dotenv
   ```

2. Create a `.env` file with your API keys:
   ```
   GEMINI_API_KEY=your_key_here
   CATS_API_KEY=your_key_here
   CATS_COMPANY_ID=your_company_id
   ```

## Usage

### Quick Test - Single Page

Test the questionnaire analyzer on a single page:

```bash
python test_questionnaire_page.py /path/to/questionnaire_page.jpg
```

### Process Complete Candidate

Process both resume and questionnaire:

```bash
python process_candidate.py resume.pdf questionnaire.pdf "Candidate Name"
```

### Using with Gemini MCP in Claude Code

Since we're leveraging the existing Gemini MCP setup, use these commands in Claude Code:

```python
# Load the analyzer prompt
prompt_path = '/home/gotime2022/mcp_test/candidate-processor/prompts/questionnaire_analyzer.txt'
with open(prompt_path, 'r') as f:
    prompt = f.read()

# Analyze a questionnaire page
result = mcp__gemini__analyze_image(
    image_path="/path/to/questionnaire_page.jpg",
    prompt=prompt,
    model="gemini-1.5-pro"
)
```

## How It Works

1. **PDF Conversion**: Uses PyMuPDF to convert PDF pages to high-quality images (300 DPI)
2. **Smart Analysis**: Custom prompt ensures Gemini only extracts checked/filled items
3. **Data Merging**: Combines results from multiple pages into structured data
4. **Email Formatting**: Creates manager-friendly summaries with only relevant information

## Key Innovation

The `questionnaire_analyzer.txt` prompt is specifically designed to:
- Identify visual checkmarks (✓, ✗, X, filled boxes)
- Distinguish between checked and unchecked items
- Extract only entered text, not field labels
- Return clean JSON with just the filled data

## Example Output

```
CANDIDATE SUMMARY - Jeff Miller
==================================================

EQUIPMENT EXPERIENCE:
--------------------
Surface Drill Equipment:
  - Brands: CAT, Sandvik
  - Years Experience: 10+
  - Types: Rotary Blast Hole Drills

CERTIFICATIONS:
--------------
  ✗ Qualitative Fit Test Certification: No

==================================================
```

## Next Steps

1. Complete CATS API integration
2. Add resume parsing with better structure extraction
3. Create web interface using MCP client
4. Add batch processing for multiple candidates
5. Implement interview notes integration

## Notes

- Always verify Gemini is using the correct model (gemini-1.5-pro works best)
- High DPI (300) is crucial for accurate checkbox detection
- The system only reports what's actually filled in, not all options