import sys
import xml.etree.ElementTree as ET

# Usage: python create_ledger_extractor.py <xml_file>
if len(sys.argv) < 2:
    print("Usage: python create_ledger_extractor.py <xml_file>")
    sys.exit(1)

xml_file = sys.argv[1]

tree = ET.parse(xml_file)
root = tree.getroot()

resp = root.find('.//RESPONSE')
if resp is not None:
    created = resp.findtext('CREATED')
    altered = resp.findtext('ALTERED')
    deleted = resp.findtext('DELETED')
    errors = resp.findtext('ERRORS')
    exceptions = resp.findtext('EXCEPTIONS')
    print(f"Created: {created}, Altered: {altered}, Deleted: {deleted}, Errors: {errors}, Exceptions: {exceptions}")
else:
    print("No <RESPONSE> found in XML.") 