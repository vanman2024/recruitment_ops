#!/usr/bin/env python3
"""
Specific test for Micheal Hennigar's questionnaire - validate Red Seal detection
"""

import os
import sys
import logging
import json
from datetime import datetime

# Add project root to path
sys.path.append('/home/gotime2022/recruitment_ops')

from catsone.processors.pillow_form_enhancer import PillowFormEnhancer
from catsone.processors.pdf_form_extractor import PDFFormExtractor
from catsone.processors.comprehensive_attachment_processor import ComprehensiveAttachmentProcessor
from catsone.processors.claude_vision_analyzer import ClaudeVisionAnalyzer

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class MichealHennigarTester:
    """Test enhanced extraction specifically against Micheal Hennigar's known questionnaire"""
    
    def __init__(self):
        self.form_enhancer = PillowFormEnhancer()
        self.pdf_extractor = PDFFormExtractor()
        self.claude_key = os.getenv('ANTHROPIC_API_KEY')
        
        if self.claude_key and self.claude_key != 'your-api-key-here':
            self.vision_analyzer = ClaudeVisionAnalyzer(self.claude_key)
        else:
            logger.warning("Claude API key not available - vision tests will be skipped")
            self.vision_analyzer = None
        
        # Expected results for Micheal Hennigar based on manual review
        self.expected_results = {
            'red_seal_status': 'Yes',  # This was incorrectly detected as "No" before
            'trade_licenses': [
                'Truck and Transport Mechanic',
                'Transport Trailer Technician'
            ],
            'years_experience': 25,  # Approximately
            'willing_to_travel': True,
            'available_start': 'ASAP'  # Or similar
        }
        
        logger.info("Expected results for Micheal Hennigar:")
        for key, value in self.expected_results.items():
            logger.info(f"  {key}: {value}")
    
    def find_questionnaire_files(self) -> list:
        """Find Micheal Hennigar's questionnaire files"""
        
        # Common locations where questionnaire might be stored
        search_locations = [
            '/tmp/questionnaire_debug',
            '/tmp/micheal_hennigar',
            '/home/gotime2022/recruitment_ops/test_data',
            '/tmp/attachments',
            '/tmp/enhanced_questionnaires'
        ]
        
        found_files = []
        
        for location in search_locations:
            if os.path.exists(location):
                for file in os.listdir(location):
                    # Look for files that might be Micheal's questionnaire
                    if any(keyword in file.lower() for keyword in ['micheal', 'hennigar', 'questionnaire', 'page']):
                        file_path = os.path.join(location, file)
                        if file.endswith(('.pdf', '.png', '.jpg')):
                            found_files.append(file_path)
                            logger.info(f"Found potential questionnaire file: {file_path}")
        
        if not found_files:
            logger.warning("No Micheal Hennigar questionnaire files found")
            logger.info("Searched locations:")
            for location in search_locations:
                logger.info(f"  {location}")
        
        return found_files
    
    def test_pdf_extraction(self, pdf_path: str) -> dict:
        """Test PDF extraction on questionnaire"""
        
        logger.info(f"Testing PDF extraction on: {pdf_path}")
        
        try:
            # Extract form fields
            pdf_data = self.pdf_extractor.extract_all_fields(pdf_path)
            
            # Validate against expected results
            validation = self._validate_results(pdf_data.get('questionnaire_data', {}), 'PDF')
            
            return {
                'method': 'pdf_extraction',
                'success': pdf_data.get('has_form_fields', False),
                'raw_data': pdf_data,
                'validation': validation
            }
            
        except Exception as e:
            logger.error(f"Error in PDF extraction: {e}")
            return {'method': 'pdf_extraction', 'success': False, 'error': str(e)}
    
    def test_vision_analysis(self, image_path: str, enhancement_type: str = 'original') -> dict:
        """Test vision analysis on questionnaire image"""
        
        if not self.vision_analyzer:
            return {'error': 'Claude Vision analyzer not available'}
        
        logger.info(f"Testing vision analysis ({enhancement_type}) on: {image_path}")
        
        try:
            # Create temp directory with image
            import tempfile
            import shutil
            
            temp_dir = tempfile.mkdtemp()
            dest_path = os.path.join(temp_dir, 'page_1.png')
            
            # If this is an enhancement test, create enhanced version first
            if enhancement_type != 'original':
                enhanced_versions = self.form_enhancer.create_enhanced_versions(image_path)
                enhanced_img = enhanced_versions.get(enhancement_type)
                
                if enhanced_img:
                    enhanced_img.save(dest_path, 'PNG')
                else:
                    logger.error(f"Could not create {enhancement_type} enhancement")
                    return {'error': f'Enhancement {enhancement_type} not available'}
            else:
                shutil.copy2(image_path, dest_path)
            
            # Run vision analysis
            vision_result = self.vision_analyzer.analyze_questionnaire_images(temp_dir)
            
            # Clean up
            shutil.rmtree(temp_dir)
            
            # Extract data from vision result
            extracted_data = {}
            if 'candidate_profile' in vision_result:
                profile = vision_result['candidate_profile']
                
                # Extract certifications
                if 'certifications' in profile:
                    certs = profile['certifications']
                    if 'red_seal' in certs:
                        extracted_data['red_seal_status'] = certs['red_seal']
                    if 'journeyman_licenses' in certs:
                        extracted_data['trade_licenses'] = certs['journeyman_licenses']
                
                # Extract other data from all_responses
                for response in profile.get('all_responses', []):
                    question_text = (response.get('question_text') or '').lower()
                    selections = response.get('actual_selections', [])
                    
                    if 'years' in question_text and 'experience' in question_text:
                        if selections and selections[0].isdigit():
                            extracted_data['years_experience'] = int(selections[0])
                    elif 'travel' in question_text:
                        if selections:
                            extracted_data['willing_to_travel'] = selections[0].lower() == 'yes'
            
            # Validate against expected results
            validation = self._validate_results(extracted_data, f'Vision ({enhancement_type})')
            
            return {
                'method': f'vision_{enhancement_type}',
                'success': bool(extracted_data),
                'raw_data': vision_result,
                'extracted_data': extracted_data,
                'validation': validation
            }
            
        except Exception as e:
            logger.error(f"Error in vision analysis: {e}")
            return {'method': f'vision_{enhancement_type}', 'success': False, 'error': str(e)}
    
    def test_hybrid_extraction(self, pdf_path: str) -> dict:
        """Test hybrid extraction system"""
        
        logger.info(f"Testing hybrid extraction on: {pdf_path}")
        
        try:
            # Create mock questionnaire info
            questionnaire_info = {
                'type': 'single',
                'attachments': [
                    {
                        'id': 'test_micheal',
                        'filename': 'micheal_hennigar_questionnaire.pdf'
                    }
                ]
            }
            
            # Mock the attachment download
            processor = ComprehensiveAttachmentProcessor()
            original_download = processor._download_attachment
            
            def mock_download(attachment_id):
                if attachment_id == 'test_micheal':
                    return pdf_path
                return original_download(attachment_id)
            
            processor._download_attachment = mock_download
            
            try:
                # Run hybrid extraction
                hybrid_result = processor._process_questionnaire(questionnaire_info)
                
                # Extract final data
                extracted_data = {}
                if 'hybrid_result' in hybrid_result:
                    final_data = hybrid_result['hybrid_result'].get('final_data', {})
                    extracted_data = final_data
                
                # Validate against expected results
                validation = self._validate_results(extracted_data, 'Hybrid')
                
                return {
                    'method': 'hybrid_extraction',
                    'success': bool(extracted_data),
                    'raw_data': hybrid_result,
                    'extracted_data': extracted_data,
                    'validation': validation,
                    'confidence_score': hybrid_result.get('confidence_score', 0.0)
                }
                
            finally:
                processor._download_attachment = original_download
            
        except Exception as e:
            logger.error(f"Error in hybrid extraction: {e}")
            return {'method': 'hybrid_extraction', 'success': False, 'error': str(e)}
    
    def _validate_results(self, extracted_data: dict, method_name: str) -> dict:
        """Validate extracted data against expected results"""
        
        validation = {
            'method': method_name,
            'total_fields': len(self.expected_results),
            'correct_fields': 0,
            'incorrect_fields': 0,
            'missing_fields': 0,
            'field_results': {},
            'accuracy_percentage': 0.0
        }
        
        for field, expected_value in self.expected_results.items():
            extracted_value = extracted_data.get(field)
            
            if extracted_value is None:
                validation['missing_fields'] += 1
                validation['field_results'][field] = {
                    'status': 'missing',
                    'expected': expected_value,
                    'extracted': None
                }
                logger.warning(f"{method_name} - Missing field: {field}")
                
            elif self._values_match(extracted_value, expected_value):
                validation['correct_fields'] += 1
                validation['field_results'][field] = {
                    'status': 'correct',
                    'expected': expected_value,
                    'extracted': extracted_value
                }
                logger.info(f"{method_name} - Correct: {field} = {extracted_value}")
                
            else:
                validation['incorrect_fields'] += 1
                validation['field_results'][field] = {
                    'status': 'incorrect',
                    'expected': expected_value,
                    'extracted': extracted_value
                }
                logger.error(f"{method_name} - Incorrect: {field} expected '{expected_value}', got '{extracted_value}'")
        
        # Calculate accuracy
        total_fields = validation['total_fields']
        if total_fields > 0:
            validation['accuracy_percentage'] = (validation['correct_fields'] / total_fields) * 100
        
        logger.info(f"{method_name} Accuracy: {validation['accuracy_percentage']:.1f}% "
                   f"({validation['correct_fields']}/{total_fields})")
        
        return validation
    
    def _values_match(self, extracted_value, expected_value) -> bool:
        """Check if extracted value matches expected value"""
        
        # Handle different types of comparisons
        if isinstance(expected_value, str) and isinstance(extracted_value, str):
            # Case-insensitive string comparison
            return extracted_value.lower().strip() == expected_value.lower().strip()
        
        elif isinstance(expected_value, list) and isinstance(extracted_value, list):
            # List comparison - check if all expected items are present
            expected_lower = [item.lower() for item in expected_value]
            extracted_lower = [item.lower() for item in extracted_value]
            
            # Check if all expected items are in extracted
            return all(item in extracted_lower for item in expected_lower)
        
        elif isinstance(expected_value, bool):
            # Boolean comparison
            if isinstance(extracted_value, str):
                return extracted_value.lower() in ['yes', 'true'] if expected_value else extracted_value.lower() in ['no', 'false']
            return bool(extracted_value) == expected_value
        
        elif isinstance(expected_value, (int, float)):
            # Numeric comparison with tolerance
            try:
                extracted_num = float(extracted_value)
                expected_num = float(expected_value)
                return abs(extracted_num - expected_num) <= 2  # 2-unit tolerance
            except (ValueError, TypeError):
                return False
        
        else:
            # Default exact comparison
            return extracted_value == expected_value
    
    def run_comprehensive_test(self) -> dict:
        """Run comprehensive test on Micheal Hennigar's questionnaire"""
        
        logger.info("=== Testing Enhanced Extraction on Micheal Hennigar's Questionnaire ===")
        
        # Find questionnaire files
        questionnaire_files = self.find_questionnaire_files()
        
        if not questionnaire_files:
            return {
                'error': 'No questionnaire files found for Micheal Hennigar',
                'searched_locations': [
                    '/tmp/questionnaire_debug',
                    '/tmp/micheal_hennigar',
                    '/home/gotime2022/recruitment_ops/test_data'
                ]
            }
        
        results = {
            'timestamp': datetime.now().isoformat(),
            'questionnaire_files': questionnaire_files,
            'expected_results': self.expected_results,
            'method_results': {},
            'best_method': None,
            'best_accuracy': 0.0
        }
        
        pdf_files = [f for f in questionnaire_files if f.endswith('.pdf')]
        image_files = [f for f in questionnaire_files if f.endswith(('.png', '.jpg'))]
        
        # Test PDF extraction
        if pdf_files:
            pdf_result = self.test_pdf_extraction(pdf_files[0])
            results['method_results']['pdf_extraction'] = pdf_result
            
            if pdf_result.get('validation', {}).get('accuracy_percentage', 0) > results['best_accuracy']:
                results['best_accuracy'] = pdf_result['validation']['accuracy_percentage']
                results['best_method'] = 'pdf_extraction'
        
        # Test vision analysis with different enhancements
        if image_files and self.vision_analyzer:
            test_image = image_files[0]
            
            # Test original image
            original_result = self.test_vision_analysis(test_image, 'original')
            results['method_results']['vision_original'] = original_result
            
            if original_result.get('validation', {}).get('accuracy_percentage', 0) > results['best_accuracy']:
                results['best_accuracy'] = original_result['validation']['accuracy_percentage']
                results['best_method'] = 'vision_original'
            
            # Test enhanced versions
            enhancement_types = ['checkbox_binary', 'radio_enhanced', 'combined', 'high_contrast']
            
            for enhancement in enhancement_types:
                enhanced_result = self.test_vision_analysis(test_image, enhancement)
                results['method_results'][f'vision_{enhancement}'] = enhanced_result
                
                if enhanced_result.get('validation', {}).get('accuracy_percentage', 0) > results['best_accuracy']:
                    results['best_accuracy'] = enhanced_result['validation']['accuracy_percentage']
                    results['best_method'] = f'vision_{enhancement}'
        
        # Test hybrid extraction
        if pdf_files:
            hybrid_result = self.test_hybrid_extraction(pdf_files[0])
            results['method_results']['hybrid_extraction'] = hybrid_result
            
            if hybrid_result.get('validation', {}).get('accuracy_percentage', 0) > results['best_accuracy']:
                results['best_accuracy'] = hybrid_result['validation']['accuracy_percentage']
                results['best_method'] = 'hybrid_extraction'
        
        logger.info(f"Best method: {results['best_method']} with {results['best_accuracy']:.1f}% accuracy")
        
        return results


def main():
    """Main test runner"""
    
    tester = MichealHennigarTester()
    
    # Run comprehensive test
    results = tester.run_comprehensive_test()
    
    # Save results
    output_file = f'/tmp/micheal_hennigar_test_results_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2, default=str)
    
    logger.info(f"Test results saved to: {output_file}")
    
    # Print summary
    print("\n" + "="*70)
    print("MICHEAL HENNIGAR QUESTIONNAIRE TEST RESULTS")
    print("="*70)
    
    if 'error' in results:
        print(f"❌ ERROR: {results['error']}")
        if 'searched_locations' in results:
            print("\nSearched locations:")
            for location in results['searched_locations']:
                print(f"  - {location}")
        return
    
    print(f"\nFiles tested: {len(results.get('questionnaire_files', []))}")
    for file in results.get('questionnaire_files', []):
        print(f"  - {file}")
    
    print(f"\nBest method: {results.get('best_method', 'None')} ({results.get('best_accuracy', 0):.1f}% accuracy)")
    
    print(f"\nMethod Results:")
    for method, result in results.get('method_results', {}).items():
        if 'validation' in result:
            accuracy = result['validation'].get('accuracy_percentage', 0)
            correct = result['validation'].get('correct_fields', 0)
            total = result['validation'].get('total_fields', 0)
            
            status = "✅" if accuracy >= 80 else "⚠️" if accuracy >= 60 else "❌"
            print(f"  {status} {method}: {accuracy:.1f}% ({correct}/{total})")
            
            # Show specific field results for critical issues
            if accuracy < 100:
                field_results = result['validation'].get('field_results', {})
                for field, field_result in field_results.items():
                    if field_result['status'] != 'correct':
                        expected = field_result['expected']
                        extracted = field_result['extracted']
                        print(f"    ❌ {field}: expected '{expected}', got '{extracted}'")
        else:
            print(f"  ❌ {method}: Failed - {result.get('error', 'Unknown error')}")
    
    # Highlight critical Red Seal issue
    print(f"\n🎯 RED SEAL STATUS VERIFICATION:")
    red_seal_results = []
    for method, result in results.get('method_results', {}).items():
        if 'validation' in result:
            field_results = result['validation'].get('field_results', {})
            if 'red_seal_status' in field_results:
                red_seal_result = field_results['red_seal_status']
                expected = red_seal_result['expected']
                extracted = red_seal_result['extracted']
                status = "✅" if red_seal_result['status'] == 'correct' else "❌"
                red_seal_results.append(f"  {status} {method}: {extracted} (expected: {expected})")
    
    for result in red_seal_results:
        print(result)
    
    print(f"\nFull results: {output_file}")
    print("="*70)


if __name__ == "__main__":
    main()