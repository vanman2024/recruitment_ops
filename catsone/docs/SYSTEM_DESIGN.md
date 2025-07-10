# Recruitment Operations System - Complete Design

## Actual Requirements (Clarified)

### Core Constraints:
- **Manual Triggering**: No automatic processing for all CATS candidates
- **Canadian Only**: Filter for Canadian candidates only (phone, location)
- **Manual CATS Updates**: Importing from another system, manual additions
- **Progressive Analysis**: Start with resume → identify gaps → request more info
- **GitHub Issues**: Template already exists

### Current Focus:
- Manual workflow testing
- Resume-to-job matching as starting point
- Gap analysis and next steps identification

## Core Questions We Need to Answer

### 1. Data Entry Points - How does data get into the system?
- **Questionnaires**: How do PDFs arrive? Email? Upload? CATS attachment?
- **Resumes**: Same question - where do they come from?
- **Interview Notes**: How are DOCX files captured from meetings?
- **Job Postings**: How do we get job requirements for matching?

### 2. Trigger Mechanisms - What starts processing?
- **New Candidate**: CATS webhook `candidate.created`
- **Document Upload**: CATS webhook `candidate.updated` 
- **Status Change**: Pipeline status to "manager review needed"
- **Manual Processing**: API endpoint call
- **Batch Processing**: Scheduled jobs?

### 3. Processing Pipeline - Step by step flow
1. **Document Detection**: Identify document types
2. **Document Processing**: Extract data using appropriate method
3. **Candidate Matching**: Link to correct CATS record
4. **Analysis**: AI processing and job matching
5. **Results Storage**: Where do results go?
6. **Notifications**: Who gets notified when?

### 4. Error Handling - What happens when things fail?
- **Document Processing Fails**: Retry? Manual review?
- **Candidate Not Found**: Manual linking process?
- **API Failures**: Queue for retry?
- **Analysis Errors**: Fallback processing?

### 5. Integration Points - External systems
- **CATS API**: Candidates, jobs, attachments, notes
- **Gemini API**: Document analysis, job matching
- **Slack API**: Notifications to managers
- **Email**: Document delivery? Notifications?
- **File Storage**: Where are documents stored?

## Missing Components Analysis

### What We Have Built:
✅ Vision-based questionnaire analysis  
✅ CATS candidate search with accent handling  
✅ Professional notes formatting  
✅ Webhook server framework  
✅ Manual processing endpoints  

### What's Missing/Unclear:
❓ **Document Intake Process** - How do documents actually arrive?  
❓ **Resume Processing** - PDF text extraction and parsing  
❓ **Interview Notes Processing** - DOCX parsing from meetings  
❓ **Job Matching Engine** - Compare candidates to job requirements  
❓ **Slack Integration** - Actual notification system  
❓ **Error Recovery** - Retry mechanisms, manual review queue  
❓ **Document Storage** - Where files are kept, cleanup  
❓ **Monitoring/Logging** - System health, performance tracking  
❓ **Testing Strategy** - Unit tests, integration tests, end-to-end  
❓ **Deployment Process** - Production setup, scaling  

## Actual Workflow (Manual Process)

### Primary Scenario: Manual Canadian Candidate Processing
```
1. You manually add Canadian candidate to CATS (from other system)
2. You upload resume (and questionnaire if available) to CATS
3. You manually trigger processing via API: 
   POST /manual/process/{candidate_id}
4. System verifies candidate is Canadian (phone +1, location)
5. System processes available documents:
   - Resume: Extract skills, experience, certifications
   - Questionnaire: Extract specific answers (if available)
6. System matches candidate to job requirements
7. System identifies information gaps:
   - Missing certifications?
   - Unclear experience level?
   - Need specific equipment knowledge?
8. System posts analysis to CATS notes:
   - What we know from documents
   - Job match score
   - Missing information needed
   - Recommended next steps
9. System suggests actions:
   - Send questionnaire email
   - Schedule phone screening
   - Request additional documents
```

### Canadian Filtering Logic
```
Identify Canadian candidates by:
- Phone number starts with +1 or 1
- Location contains Canada, Canadian provinces
- Postal code format (A1A 1A1)
- Only process candidates meeting criteria
```

### Document Processing Priority
```
1. Resume (PDF) - Primary source
   - Extract: Skills, experience, education, certifications
   - Parse: Work history, equipment experience
   
2. Questionnaire (PDF) - Enhanced source  
   - Extract: Specific answers, preferences
   - Vision AI: Checkbox selections, text fields
   
3. Gap Analysis
   - Compare extracted info to job requirements
   - Identify missing information
   - Recommend collection methods
```

## Immediate Implementation Plan

### Phase 1: Manual Processing Foundation (Current Focus)
- [ ] **Canadian candidate filtering** - Phone/location validation
- [ ] **Resume PDF processing** - Text extraction and parsing
- [ ] **Manual trigger endpoint** - Enhanced processing API
- [ ] **Job requirements extraction** - From CATS job postings
- [ ] **Basic gap analysis** - Compare resume to job requirements

### Phase 2: Enhanced Analysis (Next Priority)  
- [ ] **Resume-to-job matching engine** - Scoring algorithm
- [ ] **Missing information detection** - Gap identification
- [ ] **Next steps recommendations** - Action suggestions
- [ ] **Enhanced notes formatting** - Include gaps and recommendations
- [ ] **Test with multiple job types** - Heavy equipment, mechanics, etc.

### Phase 3: Questionnaire Integration (If Available)
- [ ] **Questionnaire processing** - Vision AI (already built)
- [ ] **Combined analysis** - Resume + questionnaire insights
- [ ] **Progressive information building** - Layer additional data
- [ ] **Confidence scoring** - Rate completeness of candidate profile

### Phase 4: Workflow Optimization (Future)
- [ ] **Slack notifications** - Manager alerts
- [ ] **Email automation** - Questionnaire requests
- [ ] **Batch processing** - Multiple candidates
- [ ] **Performance monitoring** - Track processing success

## Immediate Next Steps (For Testing)

### 1. Add Canadian Filtering
```python
def is_canadian_candidate(candidate):
    phone = candidate.get('phone', '')
    location = candidate.get('location', '').lower()
    
    # Check phone number
    if phone.startswith('+1') or phone.startswith('1'):
        return True
    
    # Check location
    canadian_indicators = ['canada', 'ontario', 'alberta', 'bc', 'quebec']
    if any(indicator in location for indicator in canadian_indicators):
        return True
        
    return False
```

### 2. Build Resume Parser
```python
def extract_resume_data(resume_pdf):
    # Extract text from PDF
    # Parse sections: experience, skills, education
    # Identify equipment brands, certifications
    # Return structured data
```

### 3. Create Job Matching
```python
def match_resume_to_job(resume_data, job_requirements):
    # Compare skills and experience
    # Calculate match score
    # Identify missing requirements
    # Suggest next steps
```

### 4. Test Workflow
```bash
# Manual test process:
1. Add Gaétan to CATS ✓ (already done)
2. Upload his resume to CATS profile
3. Call: POST /manual/process/399702647
4. Verify Canadian filtering works
5. Test resume parsing
6. Test job matching
7. Check CATS notes output
8. Validate gap analysis
```

## Key Decisions Needed

1. **Document Delivery Method**: 
   - Email parsing vs manual upload vs automated fetch?

2. **Processing Trigger Strategy**:
   - Immediate vs batched vs scheduled?

3. **Storage Architecture**:
   - Local files vs cloud storage vs database?

4. **Notification Strategy**:
   - Real-time vs digest vs on-demand?

5. **Error Recovery Approach**:
   - Automatic retry vs manual queue vs fail-fast?

## Next Steps

1. **Map Complete User Journey** - From candidate application to hiring decision
2. **Define Data Flow Diagrams** - Show every data transformation
3. **Create GitHub Issues** - Break down into specific, testable tasks
4. **Prioritize by Risk/Impact** - Tackle highest-value items first
5. **Build Test Cases** - Define success criteria for each component
6. **Plan Integration Testing** - End-to-end workflow validation

## Questions for Stakeholders

1. How do questionnaires currently arrive? (Email, upload, other?)
2. Who needs to be notified when analysis is complete?
3. What's the current manual process we're automating?
4. What are the most common failure scenarios?
5. How quickly do results need to be available?
6. What level of accuracy is required for auto-processing?

---

**Status**: System design review needed before continuing implementation
**Next Action**: Create detailed GitHub issues for each component