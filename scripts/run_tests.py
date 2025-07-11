#!/usr/bin/env python3
"""
Comprehensive Testing Suite for Recruitment Operations System
Tests the Claude Opus 4 vision analysis and dynamic AI formatting
"""

import os
import sys
import json
import logging
from datetime import datetime
from typing import Dict, Any, Optional

# Add project to path
sys.path.append('/home/gotime2022/recruitment_ops')

from catsone.integration.cats_integration import CATSClient
from catsone.processors.intelligent_candidate_processor import IntelligentCandidateProcessor

# Configure logging to file
LOG_FILE = f"logs/test_run_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
os.makedirs('logs', exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

class RecruitmentTestSuite:
    """Comprehensive test suite for the recruitment system"""
    
    def __init__(self):
        self.cats = CATSClient()
        self.processor = IntelligentCandidateProcessor()
        self.test_results = []
        
    def run_all_tests(self):
        """Run all tests and generate report"""
        logger.info("="*60)
        logger.info("RECRUITMENT OPERATIONS TEST SUITE")
        logger.info("="*60)
        
        # Test 1: API Connectivity
        self.test_api_connectivity()
        
        # Test 2: Find test candidates
        test_candidates = self.find_test_candidates()
        
        # Test 3: Process sample candidate
        if test_candidates:
            self.test_candidate_processing(test_candidates[0])
        
        # Test 4: Test job requirements extraction
        self.test_job_extraction()
        
        # Generate report
        self.generate_report()
        
    def test_api_connectivity(self):
        """Test CATS API connectivity"""
        logger.info("\n--- Test 1: API Connectivity ---")
        try:
            # Test with a simple API call
            result = self.cats.search_candidates(limit=1)
            if result:
                self.test_results.append({
                    'test': 'API Connectivity',
                    'status': 'PASS',
                    'message': 'Successfully connected to CATS API'
                })
                logger.info("✅ CATS API connection successful")
            else:
                self.test_results.append({
                    'test': 'API Connectivity',
                    'status': 'FAIL',
                    'message': 'No response from CATS API'
                })
                logger.error("❌ CATS API connection failed")
        except Exception as e:
            self.test_results.append({
                'test': 'API Connectivity',
                'status': 'ERROR',
                'message': str(e)
            })
            logger.error(f"❌ API Error: {e}")
    
    def find_test_candidates(self):
        """Find candidates with questionnaires for testing"""
        logger.info("\n--- Test 2: Finding Test Candidates ---")
        try:
            # Search for candidates with "Questionnaire Completed" tag
            candidates = self.cats.search_candidates_by_tag("Questionnaire Completed", limit=5)
            
            if candidates:
                logger.info(f"✅ Found {len(candidates)} candidates with questionnaires")
                self.test_results.append({
                    'test': 'Find Test Candidates',
                    'status': 'PASS',
                    'message': f'Found {len(candidates)} candidates'
                })
                
                # Log candidate details
                for candidate in candidates[:3]:  # Show first 3
                    logger.info(f"  - {candidate['name']} (ID: {candidate['id']})")
                
                return candidates
            else:
                logger.warning("⚠️ No candidates found with questionnaires")
                self.test_results.append({
                    'test': 'Find Test Candidates',
                    'status': 'WARN',
                    'message': 'No candidates with questionnaires found'
                })
                return []
                
        except Exception as e:
            logger.error(f"❌ Error finding candidates: {e}")
            self.test_results.append({
                'test': 'Find Test Candidates',
                'status': 'ERROR',
                'message': str(e)
            })
            return []
    
    def test_candidate_processing(self, candidate: Dict):
        """Test processing a specific candidate"""
        logger.info(f"\n--- Test 3: Processing Candidate {candidate['name']} ---")
        
        try:
            # Find a job for this candidate
            job_id = self.find_job_for_candidate(candidate['id'])
            
            if not job_id:
                logger.warning("⚠️ No job found for candidate, using default Heavy Equipment Tech job")
                job_id = 16612581  # Default Heavy Equipment Technician job
            
            # Process the candidate
            result = self.processor.process_candidate_for_job(candidate['id'], job_id)
            
            if result.get('success'):
                logger.info("✅ Candidate processing successful")
                logger.info(f"  - Job: {result.get('job_title')}")
                logger.info(f"  - Attachments: {result.get('attachment_results', {}).get('attachments_found', 0)}")
                
                # Check if questionnaire was found
                if result.get('attachment_results', {}).get('questionnaire_data'):
                    logger.info("  - Questionnaire: ✅ Found and processed")
                    
                    # Check notes quality
                    notes = result.get('notes', '')
                    if len(notes) > 500:
                        logger.info(f"  - Notes: ✅ Generated ({len(notes)} chars)")
                    else:
                        logger.warning(f"  - Notes: ⚠️ Short ({len(notes)} chars)")
                else:
                    logger.warning("  - Questionnaire: ❌ Not found")
                
                self.test_results.append({
                    'test': f'Process Candidate {candidate["name"]}',
                    'status': 'PASS',
                    'message': 'Successfully processed'
                })
            else:
                logger.error(f"❌ Processing failed: {result.get('error')}")
                self.test_results.append({
                    'test': f'Process Candidate {candidate["name"]}',
                    'status': 'FAIL',
                    'message': result.get('error')
                })
                
        except Exception as e:
            logger.error(f"❌ Error processing candidate: {e}")
            self.test_results.append({
                'test': f'Process Candidate {candidate["name"]}',
                'status': 'ERROR',
                'message': str(e)
            })
    
    def find_job_for_candidate(self, candidate_id: int) -> Optional[int]:
        """Find the job associated with a candidate"""
        try:
            candidate = self.cats.get_candidate_details(candidate_id)
            if candidate and 'pipelines' in candidate:
                for pipeline in candidate['pipelines']:
                    if 'job' in pipeline and 'id' in pipeline['job']:
                        return pipeline['job']['id']
        except:
            pass
        return None
    
    def test_job_extraction(self):
        """Test job requirements extraction"""
        logger.info("\n--- Test 4: Job Requirements Extraction ---")
        
        try:
            # Test with a known job
            test_job_id = 16612581  # Heavy Equipment Technician
            job_data = self.cats.get_job_details(test_job_id)
            
            if job_data:
                from catsone.processors.job_requirements_extractor import JobRequirementsExtractor
                extractor = JobRequirementsExtractor()
                requirements = extractor.extract_job_requirements(job_data)
                
                logger.info("✅ Job requirements extracted successfully")
                logger.info(f"  - Job Title: {requirements['source']['job_title']}")
                logger.info(f"  - Required Equipment: {len(requirements.get('required_equipment', []))}")
                logger.info(f"  - Required Certifications: {len(requirements.get('required_certifications', []))}")
                
                self.test_results.append({
                    'test': 'Job Requirements Extraction',
                    'status': 'PASS',
                    'message': f"Extracted requirements for {requirements['source']['job_title']}"
                })
            else:
                logger.error("❌ Failed to get job data")
                self.test_results.append({
                    'test': 'Job Requirements Extraction',
                    'status': 'FAIL',
                    'message': 'Could not retrieve job data'
                })
                
        except Exception as e:
            logger.error(f"❌ Error extracting job requirements: {e}")
            self.test_results.append({
                'test': 'Job Requirements Extraction',
                'status': 'ERROR',
                'message': str(e)
            })
    
    def generate_report(self):
        """Generate test report"""
        logger.info("\n" + "="*60)
        logger.info("TEST SUMMARY")
        logger.info("="*60)
        
        passed = sum(1 for r in self.test_results if r['status'] == 'PASS')
        failed = sum(1 for r in self.test_results if r['status'] == 'FAIL')
        errors = sum(1 for r in self.test_results if r['status'] == 'ERROR')
        warnings = sum(1 for r in self.test_results if r['status'] == 'WARN')
        
        logger.info(f"Total Tests: {len(self.test_results)}")
        logger.info(f"✅ Passed: {passed}")
        logger.info(f"❌ Failed: {failed}")
        logger.info(f"🔥 Errors: {errors}")
        logger.info(f"⚠️ Warnings: {warnings}")
        
        logger.info("\nDetailed Results:")
        for result in self.test_results:
            status_icon = {
                'PASS': '✅',
                'FAIL': '❌',
                'ERROR': '🔥',
                'WARN': '⚠️'
            }.get(result['status'], '❓')
            
            logger.info(f"{status_icon} {result['test']}: {result['message']}")
        
        logger.info(f"\nLog file: {LOG_FILE}")
        
        # Save results to JSON
        results_file = f"logs/test_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(results_file, 'w') as f:
            json.dump({
                'timestamp': datetime.now().isoformat(),
                'summary': {
                    'total': len(self.test_results),
                    'passed': passed,
                    'failed': failed,
                    'errors': errors,
                    'warnings': warnings
                },
                'results': self.test_results
            }, f, indent=2)
        
        logger.info(f"Results saved to: {results_file}")


def main():
    """Run the test suite"""
    # Load environment variables
    from dotenv import load_dotenv
    load_dotenv('/home/gotime2022/recruitment_ops/.env')
    
    # Check environment
    if not os.getenv('ANTHROPIC_API_KEY'):
        logger.error("❌ ANTHROPIC_API_KEY not found in .env")
        return
    
    if not os.getenv('CATS_API_KEY'):
        logger.error("❌ CATS_API_KEY not found in .env")
        return
    
    # Run tests
    suite = RecruitmentTestSuite()
    suite.run_all_tests()


if __name__ == "__main__":
    main()