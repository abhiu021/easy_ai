from main import *

print(create_stock_item("Mobile Phone", "Nos"))

# Create required ledgers first
print("Creating Sales ledger...")
print(create_ledger("Sales", "Sales Accounts"))

print("Creating ABC Enterprises ledger...")
print(create_ledger("ABC Enterprises", "Sundry Debtors"))

# Now create the voucher
print("Creating Sales voucher...")
print(import_voucher({
    "vchtype": "Sales",
    "date": "20250701",
    "party": "ABC Enterprises",
    "ledger_name": "Sales",
    "is_deemed_positive": "No",
    "amount": "10000"
}))

print(export_trial_balance("20250401", "20250630"))
print(export_voucher_xml("1"))  # Export voucher as XML instead of PDF
print(get_ledgers())
print(get_vouchers("Sales"))