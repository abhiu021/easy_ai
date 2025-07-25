
from client import TallyClient

tally = TallyClient()

def create_ledger(name, parent="Sundry Debtors"):
    xml = tally.render_template("create_ledger.xml.j2", {"name": name, "parent": parent})
    response = tally.post_xml(xml)
    return response

def export_trial_balance(from_date, to_date):
    xml = tally.render_template("export_trial_balance.xml.j2", {
        "from_date": from_date,
        "to_date": to_date
    })
    response = tally.post_xml(xml)
    with open("trial_balance.xml", "w") as f:
        f.write(response)
    return "Trial Balance saved to trial_balance.xml"

def create_stock_item(name, unit):
    xml = tally.render_template("create_stock_item.xml.j2", {"name": name, "unit": unit})
    return tally.post_xml(xml)

def import_voucher(voucher_dict):
    xml = tally.render_template("import_voucher.xml.j2", voucher_dict)
    return tally.post_xml(xml)

def fetch_report(report_name, from_date, to_date):
    xml = tally.render_template("fetch_report.xml.j2", {
        "report_name": report_name,
        "from_date": from_date,
        "to_date": to_date
    })
    response = tally.post_xml(xml)
    output_file = f"{report_name.replace(' ', '_').lower()}.xml"
    with open(output_file, "w") as f:
        f.write(response)
    return f"{report_name} saved to {output_file}"

def export_invoice_pdf(voucher_no):
    xml = tally.render_template("export_invoice_pdf.xml.j2", {"voucher_no": voucher_no})
    response = tally.post_xml(xml)
    with open(f"invoice_{voucher_no}.pdf", "wb") as f:
        f.write(response.encode())
    return f"Invoice PDF saved as invoice_{voucher_no}.pdf"

def export_voucher_xml(voucher_no, voucher_type="Sales"):
    xml = tally.render_template("export_voucher_xml.xml.j2", {"voucher_no": voucher_no})
    response = tally.post_xml(xml)
    with open(f"voucher_{voucher_no}.xml", "w") as f:
        f.write(response)
    return f"Voucher XML saved as voucher_{voucher_no}.xml"

def get_ledgers():
    xml = tally.render_template("get_ledgers.xml.j2", {})
    return tally.post_xml(xml)

def get_vouchers(voucher_type):
    xml = tally.render_template("get_vouchers.xml.j2", {"voucher_type": voucher_type})
    return tally.post_xml(xml)

def get_specific_voucher(voucher_no, voucher_type="Sales"):
    """Get details of a specific voucher by number and type"""
    xml = tally.render_template("get_specific_voucher.xml.j2", {
        "voucher_no": voucher_no,
        "voucher_type": voucher_type
    })
    response = tally.post_xml(xml)
    with open(f"specific_voucher_{voucher_no}.xml", "w") as f:
        f.write(response)
    return f"Specific voucher {voucher_no} saved to specific_voucher_{voucher_no}.xml"
