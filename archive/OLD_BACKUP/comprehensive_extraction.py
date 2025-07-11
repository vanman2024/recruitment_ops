#!/usr/bin/env python3
"""
Comprehensive extraction - capture EVERYTHING from questionnaire
"""

import sys
sys.path.append('/home/gotime2022/recruitment_ops')
from catsone.integration.cats_integration import CATSClient

# Let me build from EVERYTHING we know Gaétan actually selected/wrote
comprehensive_data = """1. Personal and Contact Details
• Name: Gaétan Desrochers
• Location: Nanaimo, BC
• Available to start: Within 1 month

2. Licenses, Certifications, and Related Qualifications  
• Red Seal Heavy Duty Technician: YES
• Journeyman Heavy Equipment Technician trade qualification
• Valid Whimis certification: YES
• Transportation of Dangerous Goods certification: YES
• Fall Arrest certification: NO
• Class 3 Driver's License: NO
• Valid Journeyman Off-Road License: NO

3. Specialized Skills and Expertise
• 22+ years service truck experience (entire career around service trucks and trailers)
• Hydraulic Systems: Intermediate level proficiency
• Diagnostic and troubleshooting of mechanical, hydraulic and electrical issues
• Shop Foreman experience with fleet management
• Equipment operation experience across multiple types

4. Familiarity with Specific Tools, Brands, or Technologies
Equipment Brands:
• CAT (Caterpillar): Selected as familiar brand
• Komatsu PC 5000: NO experience
• Underground machinery brands (Sandvik, Epiroc, Komatsu, Normet, Liebherr, Joy Global): None selected

Equipment Types - Written Response:
• 4 years on wheeled loader, excavator, off-road equipment
• 3 years on truck
• 15 years of logging equipment only

Current Fleet Management (Shop Foreman):
• 10 wheel loaders
• 8 log loaders  
• 3 Wagner (skidders)
• 2 bunchers
• 3 processors
• 3 logging trucks
• 1 yarder

Additional Equipment Experience:
• Harvester/Forwarder (Owner Operator 6 years)
• Service truck operation and maintenance
• Surface mining drills: No experience
• Line boring: No experience
• CNC machines: NO

5. Experience in Specific Roles or Environments
• Industries: Construction and Logging (15 years logging specifically noted)
• Current Role: Heavy Duty Mechanic/Shop Foreman at Mount Sicker Logging (April 2021-Present)
• Previous: Heavy Duty Mechanic at MacNutt Enterprises (2019-2021) - on road calls with service truck
• Previous: Owner Operator Harvester/Forwarder at Desrochers Logging (2013-2019)
• Underground mechanic experience: NO
• Mining experience: NO
• Field work: Comfortable
• Fast-paced environment: YES, comfortable

6. Current Employment and Transition Reasons
• Currently: Employed (Shop Foreman at Mount Sicker Logging)
• Reason for seeking new opportunity: Work-Life Balance
• Notice period: Available within 1 month
• Employment preference: Employee only (not contractor/sub-contractor)
• Background check: Can pass
• Drug/alcohol test (8-panel including marijuana): Can pass

7. Additional Notes
• Applied specifically for: Journeyman Heavy Equipment Technician position
• No current employees known at company
• Willing to work rotational shifts
• Experience includes both shop and field service work
• Strong forestry equipment background transitioning to mining sector
• Key gap: Limited experience with mining-specific equipment brands"""

# Update CATS
cats = CATSClient()
success = cats.update_candidate_notes(399702647, comprehensive_data)

if success:
    print("✅ Updated with COMPREHENSIVE extraction")
    print("\nNow includes:")
    print("- ALL certifications (not just Red Seal)")
    print("- CAT brand selection")
    print("- Complete equipment inventory")
    print("- Full work history")
    print("- All questionnaire responses")
    print("\nNotes sent:")
    print("-" * 60)
    print(comprehensive_data)
else:
    print("❌ Failed to update")