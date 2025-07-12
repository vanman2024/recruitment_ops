#!/usr/bin/env python3
"""
Test script for enhanced Pillow-based questionnaire extraction
"""

import os
import sys
import logging
import json
import tempfile
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

class EnhancedExtractionTester:
    """Test the enhanced extraction system components"""
    
    def __init__(self):
        self.form_enhancer = PillowFormEnhancer()
        self.pdf_extractor = PDFFormExtractor()
        self.claude_key = os.getenv('ANTHROPIC_API_KEY')
        
        if self.claude_key and self.claude_key != 'your-api-key-here':
            self.vision_analyzer = ClaudeVisionAnalyzer(self.claude_key)
        else:
            logger.warning("Claude API key not available - vision tests will be skipped")
            self.vision_analyzer = None
        
        self.attachment_processor = ComprehensiveAttachmentProcessor()
    
    def test_pillow_enhancement(self, test_image_path: str) -> dict:
        """Test Pillow-based image enhancement"""
        
        logger.info("Testing Pillow form enhancement...")
        
        try:
            if not os.path.exists(test_image_path):
                return {'error': f'Test image not found: {test_image_path}'}
            
            # Create enhanced versions
            enhanced_versions = self.form_enhancer.create_enhanced_versions(test_image_path)
            
            # Save enhanced versions to temp directory
            temp_dir = tempfile.mkdtemp()
            saved_paths = self.form_enhancer.save_enhanced_versions(test_image_path, temp_dir)
            
            results = {
                'success': True,
                'versions_created': list(enhanced_versions.keys()),
                'saved_paths': saved_paths,
                'temp_directory': temp_dir
            }
            
            logger.info(f"Created {len(enhanced_versions)} enhanced versions")
            for version_name in enhanced_versions.keys():
                logger.info(f"  - {version_name}")
            
            return results
            
        except Exception as e:
            logger.error(f"Error in Pillow enhancement test: {e}")
            return {'error': str(e)}
    
    def test_pdf_extraction(self, test_pdf_path: str) -> dict:
        """Test direct PDF form extraction"""
        
        logger.info("Testing PDF form extraction...")
        
        try:
            if not os.path.exists(test_pdf_path):
                return {'error': f'Test PDF not found: {test_pdf_path}'}
            
            # Extract form fields
            pdf_data = self.pdf_extractor.extract_all_fields(test_pdf_path)
            
            results = {
                'success': True,
                'has_form_fields': pdf_data.get('has_form_fields', False),
                'extraction_data': pdf_data
            }
            
            if pdf_data.get('has_form_fields'):
                text_fields = pdf_data.get('text_fields', {})
                checkboxes = pdf_data.get('checkboxes', {})
                radio_buttons = pdf_data.get('radio_buttons', {})
                questionnaire_data = pdf_data.get('questionnaire_data', {})
                
                logger.info(f"PDF extraction results:")
                logger.info(f"  - Text fields: {len(text_fields)}")
                logger.info(f"  - Checkboxes: {len(checkboxes)}")
                logger.info(f"  - Radio buttons: {len(radio_buttons)}")
                
                # Log key questionnaire data
                if questionnaire_data:
                    logger.info(f"Key questionnaire data extracted:")
                    for key, value in questionnaire_data.items():
                        logger.info(f"    {key}: {value}")
            else:
                logger.info("No form fields found in PDF")
            
            return results
            
        except Exception as e:
            logger.error(f"Error in PDF extraction test: {e}")
            return {'error': str(e)}
    
    def test_vision_analysis(self, test_image_path: str) -> dict:
        """Test enhanced Claude vision analysis"""
        
        if not self.vision_analyzer:
            return {'error': 'Claude Vision analyzer not available'}
        
        logger.info("Testing enhanced Claude vision analysis...")
        
        try:
            if not os.path.exists(test_image_path):
                return {'error': f'Test image not found: {test_image_path}'}
            
            # Create temp directory with test image
            temp_dir = tempfile.mkdtemp()
            import shutil
            dest_path = os.path.join(temp_dir, 'page_1.png')
            shutil.copy2(test_image_path, dest_path)
            
            # Run vision analysis
            vision_result = self.vision_analyzer.analyze_questionnaire_images(temp_dir)
            
            # Clean up
            shutil.rmtree(temp_dir)
            
            results = {
                'success': True,
                'vision_result': vision_result
            }
            
            # Log key results
            if 'candidate_profile' in vision_result:
                profile = vision_result['candidate_profile']
                logger.info("Vision analysis results:")
                
                if 'certifications' in profile:
                    certs = profile['certifications']
                    logger.info(f"  Certifications:")
                    for cert, value in certs.items():
                        logger.info(f"    {cert}: {value}")
                
                if 'confidence_metadata' in profile:
                    conf = profile['confidence_metadata']
                    logger.info(f"  Confidence: {conf.get('overall_confidence', 0):.2f}")
                    logger.info(f"  Enhancement levels: {conf.get('enhancement_levels', [])}")
                    logger.info(f"  High confidence selections: {len(conf.get('high_confidence_selections', []))}")
                    logger.info(f"  Questionable selections: {len(conf.get('questionable_selections', []))}")
            
            return results
            
        except Exception as e:
            logger.error(f"Error in vision analysis test: {e}")
            return {'error': str(e)}
    
    def test_hybrid_extraction(self, test_pdf_path: str) -> dict:
        """Test the complete hybrid extraction system"""
        
        logger.info("Testing hybrid extraction system...")
        
        try:
            # Create mock questionnaire info structure
            questionnaire_info = {
                'type': 'single',
                'attachments': [
                    {
                        'id': 'test',
                        'filename': 'test_questionnaire.pdf'
                    }
                ]
            }
            
            # Mock the attachment download to use our test file
            original_download = self.attachment_processor._download_attachment
            
            def mock_download(attachment_id):
                if attachment_id == 'test':
                    return test_pdf_path
                return original_download(attachment_id)
            
            # Temporarily replace download method
            self.attachment_processor._download_attachment = mock_download
            
            try:
                # Run hybrid extraction
                hybrid_result = self.attachment_processor._process_questionnaire(questionnaire_info)
                
                results = {
                    'success': True,
                    'hybrid_result': hybrid_result
                }
                
                # Log key results
                if 'hybrid_result' in hybrid_result:
                    hybrid_data = hybrid_result['hybrid_result']
                    logger.info("Hybrid extraction results:")
                    logger.info(f"  Method: {hybrid_data.get('extraction_method')}")
                    logger.info(f"  Primary source: {hybrid_data.get('primary_source')}")
                    logger.info(f"  PDF available: {hybrid_data.get('pdf_available')}")
                    
                    final_data = hybrid_data.get('final_data', {})
                    if final_data:
                        logger.info("  Final extracted data:")
                        for key, value in final_data.items():
                            logger.info(f"    {key}: {value}")
                
                confidence = hybrid_result.get('confidence_score', 0)
                logger.info(f"  Overall confidence: {confidence:.2f}")
                
                return results
                
            finally:
                # Restore original method
                self.attachment_processor._download_attachment = original_download
            
        except Exception as e:
            logger.error(f"Error in hybrid extraction test: {e}")
            return {'error': str(e)}
    
    def test_accuracy_comparison(self, test_files: list) -> dict:
        """Compare accuracy across different extraction methods"""
        
        logger.info("Testing accuracy comparison across methods...")
        
        comparison_results = {
            'test_files': len(test_files),
            'file_results': [],
            'summary': {
                'pdf_successful': 0,
                'vision_successful': 0,
                'hybrid_successful': 0
            }
        }
        
        for test_file in test_files:
            if not os.path.exists(test_file):
                logger.warning(f"Test file not found: {test_file}")
                continue
            
            file_result = {
                'file': test_file,
                'pdf_extraction': {},
                'vision_analysis': {},
                'hybrid_extraction': {}
            }
            
            # Test PDF extraction
            if test_file.endswith('.pdf'):
                pdf_result = self.test_pdf_extraction(test_file)
                file_result['pdf_extraction'] = pdf_result
                if pdf_result.get('success') and pdf_result.get('has_form_fields'):
                    comparison_results['summary']['pdf_successful'] += 1
            
            # Test vision analysis (convert PDF to image first if needed)
            if self.vision_analyzer:
                if test_file.endswith('.pdf'):
                    # Convert first page to image for vision test
                    try:
                        import fitz
                        doc = fitz.open(test_file)
                        page = doc[0]
                        pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))
                        
                        temp_image = tempfile.mktemp(suffix='.png')
                        pix.save(temp_image)
                        doc.close()
                        
                        vision_result = self.test_vision_analysis(temp_image)
                        file_result['vision_analysis'] = vision_result
                        
                        os.unlink(temp_image)
                        
                        if vision_result.get('success'):
                            comparison_results['summary']['vision_successful'] += 1
                            
                    except Exception as e:
                        logger.error(f"Error converting PDF to image: {e}")
                        file_result['vision_analysis'] = {'error': str(e)}
                else:
                    # Direct image analysis
                    vision_result = self.test_vision_analysis(test_file)
                    file_result['vision_analysis'] = vision_result
                    if vision_result.get('success'):
                        comparison_results['summary']['vision_successful'] += 1
            
            # Test hybrid extraction
            if test_file.endswith('.pdf'):
                hybrid_result = self.test_hybrid_extraction(test_file)
                file_result['hybrid_extraction'] = hybrid_result
                if hybrid_result.get('success'):
                    comparison_results['summary']['hybrid_successful'] += 1
            
            comparison_results['file_results'].append(file_result)
        
        # Log summary
        logger.info("Accuracy comparison summary:")
        logger.info(f"  Files tested: {comparison_results['test_files']}")
        logger.info(f"  PDF extraction successful: {comparison_results['summary']['pdf_successful']}")
        logger.info(f"  Vision analysis successful: {comparison_results['summary']['vision_successful']}")
        logger.info(f"  Hybrid extraction successful: {comparison_results['summary']['hybrid_successful']}")
        
        return comparison_results
    
    def run_comprehensive_test(self, test_files: list = None) -> dict:
        """Run comprehensive test suite"""
        
        logger.info("=== Starting Enhanced Extraction Test Suite ===")
        
        if not test_files:
            # Look for test files in common locations
            test_files = []
            test_locations = [
                '/tmp/questionnaire_debug',
                '/tmp/test_forms',
                '/home/gotime2022/recruitment_ops/test_data'
            ]
            
            for location in test_locations:
                if os.path.exists(location):
                    for file in os.listdir(location):
                        if file.endswith(('.pdf', '.png', '.jpg')):
                            test_files.append(os.path.join(location, file))
        
        if not test_files:
            logger.warning("No test files found - creating sample test")
            # Create a simple test image for Pillow enhancement
            from PIL import Image, ImageDraw
            test_img = Image.new('RGB', (800, 600), 'white')
            draw = ImageDraw.Draw(test_img)
            
            # Draw some mock form elements
            draw.rectangle([100, 100, 130, 130], outline='black', width=2)  # Checkbox
            draw.text((140, 105), "Red Seal Certification", fill='black')
            
            draw.ellipse([100, 200, 130, 230], outline='black', width=2)  # Radio button
            draw.text((140, 205), "Yes", fill='black')
            
            temp_test_file = tempfile.mktemp(suffix='.png')
            test_img.save(temp_test_file)
            test_files = [temp_test_file]
        
        # Run all tests
        results = {
            'timestamp': datetime.now().isoformat(),
            'test_files_used': test_files,
            'component_tests': {},
            'accuracy_comparison': {}
        }
        
        # Test individual components
        if test_files:
            test_file = test_files[0]
            
            # Test Pillow enhancement
            if test_file.endswith(('.png', '.jpg')):
                results['component_tests']['pillow_enhancement'] = self.test_pillow_enhancement(test_file)
            
            # Test PDF extraction
            if test_file.endswith('.pdf'):
                results['component_tests']['pdf_extraction'] = self.test_pdf_extraction(test_file)
            
            # Test vision analysis
            if self.vision_analyzer:
                results['component_tests']['vision_analysis'] = self.test_vision_analysis(test_file)
            
            # Test hybrid extraction
            if test_file.endswith('.pdf'):
                results['component_tests']['hybrid_extraction'] = self.test_hybrid_extraction(test_file)
        
        # Run accuracy comparison
        pdf_files = [f for f in test_files if f.endswith('.pdf')]
        if pdf_files:
            results['accuracy_comparison'] = self.test_accuracy_comparison(pdf_files[:3])  # Limit to 3 files
        
        logger.info("=== Test Suite Complete ===")
        
        return results


def main():
    """Main test runner"""
    
    tester = EnhancedExtractionTester()
    
    # Run comprehensive test
    results = tester.run_comprehensive_test()
    
    # Save results
    output_file = f'/tmp/enhanced_extraction_test_results_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2, default=str)
    
    logger.info(f"Test results saved to: {output_file}")
    
    # Print summary
    print("\n" + "="*60)
    print("ENHANCED EXTRACTION TEST SUMMARY")
    print("="*60)
    
    if 'component_tests' in results:
        print("\nComponent Tests:")
        for component, result in results['component_tests'].items():
            status = "✅ PASS" if result.get('success') else "❌ FAIL"
            print(f"  {component}: {status}")
            if not result.get('success') and 'error' in result:
                print(f"    Error: {result['error']}")
    
    if 'accuracy_comparison' in results and results['accuracy_comparison']:
        print("\nAccuracy Comparison:")
        summary = results['accuracy_comparison'].get('summary', {})
        total = results['accuracy_comparison'].get('test_files', 0)
        
        if total > 0:
            pdf_rate = (summary.get('pdf_successful', 0) / total) * 100
            vision_rate = (summary.get('vision_successful', 0) / total) * 100
            hybrid_rate = (summary.get('hybrid_successful', 0) / total) * 100
            
            print(f"  PDF Extraction: {summary.get('pdf_successful', 0)}/{total} ({pdf_rate:.1f}%)")
            print(f"  Vision Analysis: {summary.get('vision_successful', 0)}/{total} ({vision_rate:.1f}%)")
            print(f"  Hybrid Extraction: {summary.get('hybrid_successful', 0)}/{total} ({hybrid_rate:.1f}%)")
    
    print(f"\nFull results: {output_file}")
    print("="*60)


if __name__ == "__main__":
    main()