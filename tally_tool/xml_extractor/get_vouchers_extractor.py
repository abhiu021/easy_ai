import sys
import xml.etree.ElementTree as ET

# Usage: python get_vouchers_extractor.py <xml_file>
if len(sys.argv) < 2:
    print("Usage: python get_vouchers_extractor.py <xml_file>")
    sys.exit(1)

xml_file = sys.argv[1]

tree = ET.parse(xml_file)
root = tree.getroot()

vouchers = []
for voucher in root.findall('.//VOUCHER'):
    vch_no = voucher.findtext('VOUCHERNUMBER')
    date = voucher.findtext('DATE')
    vch_type = voucher.findtext('VOUCHERTYPENAME')
    party = voucher.findtext('PARTYLEDGERNAME')
    amount = voucher.findtext('AMOUNT')
    vouchers.append({'number': vch_no, 'date': date, 'type': vch_type, 'party': party, 'amount': amount})

print("Extracted Vouchers:")
for v in vouchers:
    print(f"- No: {v['number']}, Date: {v['date']}, Type: {v['type']}, Party: {v['party']}, Amount: {v['amount']}") 