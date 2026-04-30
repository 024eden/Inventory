"""
utils.py - Receipt printing, PDF reports, export utilities
"""

import os
import csv
from datetime import datetime


STORE_NAME    = "VARIETY STORE"
STORE_ADDRESS = "Main Branch - Your City"
STORE_PHONE   = "+91-XXXXXXXXXX"
STORE_TAGLINE = "Thank You - Visit Again!"
TAX_RATE      = 0.0          # set to e.g. 0.05 for 5% GST


def format_currency(amount):
    return f"₹{amount:,.2f}"


def print_receipt(invoice_no, items, subtotal, discount, tax, total,
                  paid, change, method, customer_name="Walk-in", cashier=""):
    """Print receipt to console (thermal-printer style)"""
    width = 42
    line  = "─" * width
    dline = "═" * width

    print(dline)
    print(STORE_NAME.center(width))
    print(STORE_ADDRESS.center(width))
    print(STORE_PHONE.center(width))
    print(dline)
    print(f"Invoice : {invoice_no}")
    print(f"Date    : {datetime.now().strftime('%d-%m-%Y %H:%M')}")
    print(f"Customer: {customer_name}")
    print(f"Cashier : {cashier}")
    print(line)
    print(f"{'Item':<20} {'Qty':>4} {'Price':>8} {'Total':>8}")
    print(line)
    for item in items:
        name = item["name"][:20]
        print(f"{name:<20} {item['qty']:>4} {item['price']:>8.2f} {item['total']:>8.2f}")
    print(line)
    print(f"{'Subtotal':>32} {subtotal:>8.2f}")
    if discount:
        print(f"{'Discount':>32} -{discount:>7.2f}")
    if tax:
        print(f"{'Tax':>32} {tax:>8.2f}")
    print(dline)
    print(f"{'TOTAL':>32} {total:>8.2f}")
    print(f"{'Paid (' + method + ')':>32} {paid:>8.2f}")
    print(f"{'Change':>32} {change:>8.2f}")
    print(dline)
    print(STORE_TAGLINE.center(width))
    print(dline)
    print()


def get_receipt_text(invoice_no, items, subtotal, discount, tax, total,
                     paid, change, method, customer_name="Walk-in", cashier=""):
    """Return receipt as a string for GUI display"""
    width = 44
    line  = "─" * width
    dline = "═" * width
    lines = []

    lines.append(dline)
    lines.append(STORE_NAME.center(width))
    lines.append(STORE_ADDRESS.center(width))
    lines.append(STORE_PHONE.center(width))
    lines.append(dline)
    lines.append(f"Invoice : {invoice_no}")
    lines.append(f"Date    : {datetime.now().strftime('%d-%m-%Y %H:%M')}")
    lines.append(f"Customer: {customer_name}")
    lines.append(f"Cashier : {cashier}")
    lines.append(line)
    lines.append(f"{'Item':<22} {'Qty':>4} {'Rate':>7} {'Total':>8}")
    lines.append(line)
    for item in items:
        name = item["name"][:22]
        lines.append(f"{name:<22} {item['qty']:>4} {item['price']:>7.2f} {item['total']:>8.2f}")
    lines.append(line)
    lines.append(f"{'Subtotal':>34} {subtotal:>8.2f}")
    if discount:
        lines.append(f"{'Discount':>34} -{discount:>7.2f}")
    if tax:
        lines.append(f"{'Tax':>34} {tax:>8.2f}")
    lines.append(dline)
    lines.append(f"{'TOTAL':>34} {total:>8.2f}")
    lines.append(f"{'Paid':>34} {paid:>8.2f}")
    lines.append(f"{'Change':>34} {change:>8.2f}")
    lines.append(f"{'Method':>34} {method:>8}")
    lines.append(dline)
    lines.append(STORE_TAGLINE.center(width))
    lines.append(dline)
    return "\n".join(lines)


def export_to_csv(data, filename, folder="reports"):
    """Export list of dicts to CSV"""
    os.makedirs(folder, exist_ok=True)
    path = os.path.join(folder, filename)
    if not data:
        return None
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=data[0].keys())
        writer.writeheader()
        writer.writerows(data)
    return path


def validate_number(value, allow_negative=False):
    try:
        num = float(value)
        if not allow_negative and num < 0:
            return False, "Value cannot be negative"
        return True, num
    except ValueError:
        return False, "Invalid number"


def validate_required(value, field_name="Field"):
    if not str(value).strip():
        return False, f"{field_name} is required"
    return True, value.strip()
