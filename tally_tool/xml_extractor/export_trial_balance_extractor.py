import sys
import xml.etree.ElementTree as ET

# Usage: python export_trial_balance_extractor.py <xml_file>
if len(sys.argv) < 2:
    print("Usage: python export_trial_balance_extractor.py <xml_file>")
    sys.exit(1)

xml_file = sys.argv[1]

tree = ET.parse(xml_file)
root = tree.getroot()

print("Trial Balance:")
for ledger in root.findall('.//LEDGER'):
    name = ledger.get('NAME')
    closing = ledger.findtext('CLOSINGBALANCE')
    print(f"- {name}: Closing Balance = {closing}") 