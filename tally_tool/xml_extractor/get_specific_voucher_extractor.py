import sys
import xml.etree.ElementTree as ET

# Usage: python get_specific_voucher_extractor.py <xml_file>
if len(sys.argv) < 2:
    print("Usage: python get_specific_voucher_extractor.py <xml_file>")
    sys.exit(1)

xml_file = sys.argv[1]

tree = ET.parse(xml_file)
root = tree.getroot()

voucher = root.find('.//VOUCHER')
if voucher is not None:
    vch_no = voucher.findtext('VOUCHERNUMBER')
    date = voucher.findtext('DATE')
    vch_type = voucher.findtext('VOUCHERTYPENAME')
    party = voucher.findtext('PARTYLEDGERNAME')
    print(f"Voucher No: {vch_no}\nDate: {date}\nType: {vch_type}\nParty: {party}")
    print("Inventory Items:")
    for inv in voucher.findall('.//ALLINVENTORYENTRIES.LIST'):
        item = inv.findtext('STOCKITEMNAME')
        qty = inv.findtext('BILLEDQTY')
        rate = inv.findtext('RATE')
        amount = inv.findtext('AMOUNT')
        print(f"- {item}: Qty={qty}, Rate={rate}, Amount={amount}")
else:
    print("No voucher found in XML.") 