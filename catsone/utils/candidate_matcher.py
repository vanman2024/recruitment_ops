#!/usr/bin/env python3
"""
Candidate Matcher - Links questionnaires to CATS candidate records
Handles the critical ID matching problem
"""

import logging
import os
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import re

import sys
sys.path.append('/home/gotime2022/recruitment_ops')
from catsone.integration.cats_integration import CATSClient

logger = logging.getLogger(__name__)

class CandidateMatcher:
    """Match questionnaire data to correct CATS candidate record"""
    
    def __init__(self, cats_client: CATSClient):
        self.cats = cats_client
    
    def find_candidate_by_questionnaire(self, questionnaire_analysis: Dict) -> Optional[Dict]:
        """Find the correct CATS candidate record for a questionnaire"""
        
        candidate_profile = questionnaire_analysis.get('candidate_profile', {})
        candidate_info = candidate_profile.get('candidate_info', {})
        
        # Get name from questionnaire
        full_name = candidate_info.get('name', '')
        if not full_name:
            logger.error("No candidate name found in questionnaire")
            return None
        
        # Parse name components
        name_parts = self._parse_name(full_name)
        if not name_parts:
            logger.error(f"Could not parse name: {full_name}")
            return None
        
        # Search CATS for potential matches
        candidates = self._search_cats_candidates(name_parts)
        if not candidates:
            logger.warning(f"No candidates found in CATS for: {full_name}")
            return None
        
        # Find best match using additional criteria
        best_match = self._find_best_match(candidates, questionnaire_analysis)
        
        if best_match:
            logger.info(f"Matched questionnaire to candidate ID: {best_match['id']}")
            return best_match
        else:
            logger.warning(f"Could not definitively match candidate: {full_name}")
            return None
    
    def _parse_name(self, full_name: str) -> Optional[Dict[str, str]]:
        """Parse full name into components"""
        
        # Clean up the name
        name = full_name.strip()
        
        # Handle common formats
        if ',' in name:
            # "Last, First" format
            parts = name.split(',')
            if len(parts) >= 2:
                return {
                    'first_name': parts[1].strip(),
                    'last_name': parts[0].strip(),
                    'full_name': name
                }
        else:
            # "First Last" format
            parts = name.split()
            if len(parts) >= 2:
                return {
                    'first_name': parts[0].strip(),
                    'last_name': parts[-1].strip(),
                    'full_name': name
                }
        
        return None
    
    def _search_cats_candidates(self, name_parts: Dict[str, str]) -> List[Dict]:
        """Search CATS for candidates matching name with accent handling"""
        
        import unicodedata
        import requests
        
        def normalize_name(name):
            """Normalize accents for better matching"""
            # Convert accented chars to base chars: é -> e, á -> a, etc.
            normalized = unicodedata.normalize('NFD', name)
            ascii_name = normalized.encode('ascii', 'ignore').decode('ascii')
            return ascii_name.lower()
        
        # Get search variations with and without accents
        first_variations = [
            name_parts['first_name'].lower(),
            normalize_name(name_parts['first_name']),
        ]
        last_variations = [
            name_parts['last_name'].lower(), 
            normalize_name(name_parts['last_name'])
        ]
        
        # Remove duplicates
        first_variations = list(set(first_variations))
        last_variations = list(set(last_variations))
        
        logger.info(f"Searching for first name variations: {first_variations}")
        logger.info(f"Searching for last name variations: {last_variations}")
        
        # Search through all candidates since CATS search doesn't work well
        candidates = []
        page = 1
        max_pages = 50  # Search through more candidates
        
        while page <= max_pages:
            try:
                url = f"{self.cats.base_url}/candidates"
                params = {"per_page": 50, "page": page}
                response = requests.get(url, headers=self.cats.headers, params=params)
                
                if response.status_code == 200:
                    data = response.json()
                    
                    if '_embedded' in data:
                        page_candidates = data['_embedded'].get('candidates', [])
                        
                        if not page_candidates:
                            break  # No more candidates
                        
                        # Check each candidate for name matches
                        for candidate in page_candidates:
                            first_name = candidate.get('first_name', '').lower()
                            last_name = candidate.get('last_name', '').lower()
                            
                            # Normalize candidate name too
                            first_norm = normalize_name(candidate.get('first_name', ''))
                            last_norm = normalize_name(candidate.get('last_name', ''))
                            
                            # Check if any variation matches
                            first_match = any(var in first_name or var in first_norm for var in first_variations)
                            last_match = any(var in last_name or var in last_norm for var in last_variations)
                            
                            if first_match and last_match:
                                logger.info(f"Found candidate match: {candidate.get('first_name')} {candidate.get('last_name')} (ID: {candidate.get('id')})")
                                candidates.append(candidate)
                        
                        # If we found matches, we can stop searching
                        if candidates:
                            break
                            
                        # Check if this was the last page
                        if len(page_candidates) < 50:
                            break
                    else:
                        break
                else:
                    logger.error(f"API error on page {page}: {response.status_code}")
                    break
                    
            except Exception as e:
                logger.error(f"Error searching page {page}: {e}")
                break
                
            page += 1
        
        logger.info(f"Found {len(candidates)} matching candidates")
        return candidates
    
    def _find_best_match(self, candidates: List[Dict], questionnaire_analysis: Dict) -> Optional[Dict]:
        """Find the best matching candidate using multiple criteria"""
        
        if len(candidates) == 1:
            # Only one candidate found, use it
            return candidates[0]
        
        # Multiple candidates - use scoring to find best match
        candidate_profile = questionnaire_analysis.get('candidate_profile', {})
        candidate_info = candidate_profile.get('candidate_info', {})
        original_name = candidate_info.get('name', '')
        
        scored_candidates = []
        
        for candidate in candidates:
            score = self._calculate_match_score(candidate, questionnaire_analysis)
            scored_candidates.append((candidate, score))
        
        # Sort by score (highest first)
        scored_candidates.sort(key=lambda x: x[1], reverse=True)
        
        # Return best match if score is high enough
        if scored_candidates and scored_candidates[0][1] > 0.7:  # 70% confidence threshold
            return scored_candidates[0][0]
        
        # If no high-confidence match, log ambiguity
        logger.warning(f"Ambiguous match for '{original_name}'. Found {len(candidates)} candidates:")
        for candidate, score in scored_candidates:
            logger.warning(f"  - ID {candidate.get('id')}: {candidate.get('first_name', '')} {candidate.get('last_name', '')} (score: {score:.2f})")
        
        return None
    
    def _calculate_match_score(self, candidate: Dict, questionnaire_analysis: Dict) -> float:
        """Calculate match confidence score between candidate and questionnaire"""
        
        score = 0.0
        
        # Get questionnaire data
        candidate_profile = questionnaire_analysis.get('candidate_profile', {})
        candidate_info = candidate_profile.get('candidate_info', {})
        actual_responses = candidate_profile.get('actual_responses', {})
        
        # Name matching (most important)
        questionnaire_name = candidate_info.get('name', '').lower()
        cats_name = f"{candidate.get('first_name', '')} {candidate.get('last_name', '')}".lower()
        
        if questionnaire_name in cats_name or cats_name in questionnaire_name:
            score += 0.6  # High weight for name match
        
        # Check for additional matching criteria
        # Employment status
        for key, response in actual_responses.items():
            if 'employment_status' in key:
                selections = response.get('selections', [])
                if 'Employed' in selections:
                    # Check if CATS candidate has current employer
                    if candidate.get('current_employer'):
                        score += 0.1
        
        # Recent activity (prefer recently active candidates)
        if candidate.get('last_modified'):
            try:
                last_modified = datetime.fromisoformat(candidate['last_modified'].replace('Z', '+00:00'))
                days_ago = (datetime.now() - last_modified).days
                if days_ago <= 30:  # Active within last 30 days
                    score += 0.1
            except:
                pass
        
        # Location/contact info (if available)
        if candidate.get('email') and '@' in candidate.get('email', ''):
            score += 0.1  # Has valid email
        
        # Pipeline status (prefer candidates in active pipelines)
        # This would require additional API call to get pipeline info
        
        return min(score, 1.0)  # Cap at 1.0
    
    def get_candidate_for_update(self, questionnaire_analysis: Dict) -> Tuple[Optional[int], Optional[str]]:
        """Get candidate ID and name for notes update"""
        
        candidate = self.find_candidate_by_questionnaire(questionnaire_analysis)
        
        if candidate:
            return candidate.get('id'), f"{candidate.get('first_name', '')} {candidate.get('last_name', '')}"
        
        return None, None
    
    def manual_candidate_link(self, candidate_id: int, questionnaire_analysis: Dict) -> bool:
        """Manually link a questionnaire to a specific candidate ID"""
        
        try:
            # Verify candidate exists
            candidate = self.cats.get_candidate_details(candidate_id)
            if not candidate:
                logger.error(f"Candidate ID {candidate_id} not found in CATS")
                return False
            
            # Store the link for future reference
            # This could be in a database or file system
            logger.info(f"Manually linked questionnaire to candidate ID: {candidate_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error in manual candidate link: {e}")
            return False


# Test the candidate matcher
if __name__ == "__main__":
    
    # Get API credentials
    cats_client = CATSClient()
    matcher = CandidateMatcher(cats_client)
    
    # Sample questionnaire analysis (from our vision processing)
    sample_analysis = {
        'candidate_profile': {
            'candidate_info': {'name': 'Gaétan Desrochers'},
            'actual_responses': {
                'q1_industries_worked': {
                    'selections': ['Construction', 'Other'],
                    'text': ['Logging']
                },
                'q3_employment_status': {
                    'selections': ['Employed']
                }
            }
        }
    }
    
    # Test the matching
    print("=== CANDIDATE MATCHING TEST ===")
    
    candidate_id, candidate_name = matcher.get_candidate_for_update(sample_analysis)
    
    if candidate_id:
        print(f"✓ Found match: {candidate_name} (ID: {candidate_id})")
        print("Ready to update notes in CATS")
    else:
        print("✗ Could not find matching candidate")
        print("Manual linking may be required")
    
    # Show how to manually link if needed
    print("\n=== MANUAL LINKING EXAMPLE ===")
    print("If automatic matching fails, use:")
    print("matcher.manual_candidate_link(12345, questionnaire_analysis)")