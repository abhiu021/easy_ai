import sys
import xml.etree.ElementTree as ET

# Usage: python get_ledgers_extractor.py <xml_file>
if len(sys.argv) < 2:
    print("Usage: python get_ledgers_extractor.py <xml_file>")
    sys.exit(1)

xml_file = sys.argv[1]

tree = ET.parse(xml_file)
root = tree.getroot()

ledgers = []
for ledger in root.findall('.//LEDGER'):
    name = ledger.get('NAME')
    group = ledger.findtext('PARENT')
    ledgers.append({'name': name, 'group': group})

print("Extracted Ledgers:")
for l in ledgers:
    print(f"- {l['name']} (Group: {l['group']})") 