"""
app.py - Main Tkinter GUI for Variety Store Management System
Modules: Login, Dashboard, POS, Inventory, Customers, Suppliers, Purchases, Expenses, Reports, Users
"""

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from datetime import datetime, date
import os, sys

# ── bootstrap path ────────────────────────────────────────────
sys.path.insert(0, os.path.dirname(__file__))
from database import init_db, generate_invoice_no, generate_po_number
import models as M
from utils import (get_receipt_text, format_currency, TAX_RATE,
                   export_to_csv, validate_number, validate_required)

# ── Colour palette ────────────────────────────────────────────
C = {
    "bg":       "#F0F4F8",
    "sidebar":  "#1A2B4A",
    "sidebar2": "#243554",
    "accent":   "#2563EB",
    "accent2":  "#1D4ED8",
    "success":  "#16A34A",
    "danger":   "#DC2626",
    "warning":  "#D97706",
    "white":    "#FFFFFF",
    "text":     "#1E293B",
    "subtext":  "#64748B",
    "border":   "#CBD5E1",
    "card":     "#FFFFFF",
    "header":   "#1E3A5F",
}
FONT      = ("Segoe UI", 10)
FONT_B    = ("Segoe UI", 10, "bold")
FONT_H    = ("Segoe UI", 16, "bold")
FONT_MONO = ("Courier New", 9)


# ═══════════════════════════════════════════════════════════════
#  HELPER WIDGETS
# ═══════════════════════════════════════════════════════════════
def card(parent, **kw):
    return tk.Frame(parent, bg=C["card"], relief="flat",
                    highlightbackground=C["border"], highlightthickness=1, **kw)

def lbl(parent, text, font=FONT, fg=None, bg=None, **kw):
    return tk.Label(parent, text=text, font=font,
                    fg=fg or C["text"], bg=bg or C["card"], **kw)

def btn(parent, text, command=None, color=None, fg="white", width=12, **kw):
    color = color or C["accent"]
    b = tk.Button(parent, text=text, command=command,
                  bg=color, fg=fg, font=FONT_B, relief="flat",
                  cursor="hand2", width=width, pady=6, **kw)
    b.bind("<Enter>", lambda e: b.config(bg=_darken(color)))
    b.bind("<Leave>", lambda e: b.config(bg=color))
    return b

def _darken(hex_color):
    r = max(0, int(hex_color[1:3], 16) - 20)
    g = max(0, int(hex_color[3:5], 16) - 20)
    b = max(0, int(hex_color[5:7], 16) - 20)
    return f"#{r:02x}{g:02x}{b:02x}"

def entry_row(parent, label, row, col=0, width=24, show=None):
    tk.Label(parent, text=label, font=FONT, bg=C["card"], fg=C["text"]).grid(
        row=row, column=col, sticky="e", padx=6, pady=4)
    var = tk.StringVar()
    e = ttk.Entry(parent, textvariable=var, width=width, show=show or "")
    e.grid(row=row, column=col+1, sticky="w", padx=6, pady=4)
    return var

def combo_row(parent, label, row, values, col=0, width=22):
    tk.Label(parent, text=label, font=FONT, bg=C["card"], fg=C["text"]).grid(
        row=row, column=col, sticky="e", padx=6, pady=4)
    var = tk.StringVar()
    cb = ttk.Combobox(parent, textvariable=var, values=values, width=width, state="readonly")
    cb.grid(row=row, column=col+1, sticky="w", padx=6, pady=4)
    return var, cb

def make_tree(parent, columns, heights=15, show="headings"):
    frame = tk.Frame(parent, bg=C["bg"])
    frame.pack(fill="both", expand=True)
    vsb = ttk.Scrollbar(frame, orient="vertical")
    hsb = ttk.Scrollbar(frame, orient="horizontal")
    tree = ttk.Treeview(frame, columns=columns, show=show,
                        height=heights, yscrollcommand=vsb.set,
                        xscrollcommand=hsb.set)
    vsb.config(command=tree.yview)
    hsb.config(command=tree.xview)
    vsb.pack(side="right", fill="y")
    hsb.pack(side="bottom", fill="x")
    tree.pack(fill="both", expand=True)
    return tree

def tree_style():
    s = ttk.Style()
    s.theme_use("clam")
    s.configure("Treeview", background=C["white"], fieldbackground=C["white"],
                 foreground=C["text"], rowheight=26, font=FONT)
    s.configure("Treeview.Heading", background=C["header"], foreground="white",
                 font=FONT_B, relief="flat")
    s.map("Treeview", background=[("selected", C["accent"])])


# ═══════════════════════════════════════════════════════════════
#  LOGIN
# ═══════════════════════════════════════════════════════════════
class LoginWindow(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Variety Store — Login")
        self.resizable(False, False)
        self.configure(bg=C["sidebar"])
        self.user = None
        self._center(400, 480)
        self._build()

    def _center(self, w, h):
        sw, sh = self.winfo_screenwidth(), self.winfo_screenheight()
        self.geometry(f"{w}x{h}+{(sw-w)//2}+{(sh-h)//2}")

    def _build(self):
        top = tk.Frame(self, bg=C["sidebar"], pady=30)
        top.pack(fill="x")
        tk.Label(top, text="🏪", font=("Segoe UI", 36), bg=C["sidebar"], fg="white").pack()
        tk.Label(top, text="VARIETY STORE", font=("Segoe UI", 18, "bold"),
                 bg=C["sidebar"], fg="white").pack()
        tk.Label(top, text="Management System", font=("Segoe UI", 11),
                 bg=C["sidebar"], fg="#94A3B8").pack()

        frm = tk.Frame(self, bg=C["white"], padx=30, pady=30)
        frm.pack(fill="both", expand=True, padx=30, pady=20)

        tk.Label(frm, text="Username", font=FONT_B, bg=C["white"], fg=C["text"]).pack(anchor="w")
        self.user_var = tk.StringVar(value="admin")
        ttk.Entry(frm, textvariable=self.user_var, width=32, font=FONT).pack(fill="x", pady=(2,12))

        tk.Label(frm, text="Password", font=FONT_B, bg=C["white"], fg=C["text"]).pack(anchor="w")
        self.pass_var = tk.StringVar(value="admin123")
        ttk.Entry(frm, textvariable=self.pass_var, width=32, show="●", font=FONT).pack(fill="x", pady=(2,20))

        tk.Button(frm, text="LOG IN", command=self._login,
                  bg=C["accent"], fg="white", font=("Segoe UI", 12, "bold"),
                  relief="flat", pady=10, cursor="hand2").pack(fill="x")

        self.err_lbl = tk.Label(frm, text="", fg=C["danger"], bg=C["white"], font=FONT)
        self.err_lbl.pack(pady=6)
        self.bind("<Return>", lambda e: self._login())

    def _login(self):
        user = M.login(self.user_var.get().strip(), self.pass_var.get())
        if user:
            self.user = user
            self.destroy()
        else:
            self.err_lbl.config(text="❌  Invalid username or password")


# ═══════════════════════════════════════════════════════════════
#  MAIN APPLICATION WINDOW
# ═══════════════════════════════════════════════════════════════
class App(tk.Tk):
    def __init__(self, user):
        super().__init__()
        self.current_user = user
        self.title(f"Variety Store MS — {user['full_name']} ({user['role'].title()})")
        self.state("zoomed")
        self.configure(bg=C["bg"])
        tree_style()
        self._build()
        self._show_module("dashboard")

    def _build(self):
        # ── Sidebar ──────────────────────────────────────────
        self.sidebar = tk.Frame(self, bg=C["sidebar"], width=210)
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)

        tk.Label(self.sidebar, text="🏪 VARIETY\nSTORE MS",
                 font=("Segoe UI", 13, "bold"), bg=C["sidebar"],
                 fg="white", pady=16).pack(fill="x")
        ttk.Separator(self.sidebar, orient="horizontal").pack(fill="x")

        nav = [
            ("📊 Dashboard",   "dashboard"),
            ("🛒 Point of Sale","pos"),
            ("📦 Inventory",   "inventory"),
            ("👥 Customers",   "customers"),
            ("🚚 Suppliers",   "suppliers"),
            ("🧾 Purchases",   "purchases"),
            ("💸 Expenses",    "expenses"),
            ("📈 Reports",     "reports"),
        ]
        if self.current_user["role"] == "admin":
            nav.append(("⚙️  Users",       "users"))

        self.nav_btns = {}
        for label, key in nav:
            b = tk.Button(self.sidebar, text=f"  {label}", anchor="w",
                          bg=C["sidebar"], fg="#CBD5E1", font=FONT,
                          relief="flat", pady=10, padx=10,
                          command=lambda k=key: self._show_module(k),
                          cursor="hand2")
            b.pack(fill="x")
            b.bind("<Enter>", lambda e, b=b: b.config(bg=C["sidebar2"]))
            b.bind("<Leave>", lambda e, b=b: b.config(
                bg=C["accent"] if b["text"].strip() in [f"  {l}" for l,_ in nav if _ == self._current] else C["sidebar"]))
            self.nav_btns[key] = b

        # logout
        tk.Button(self.sidebar, text="  🚪 Logout", anchor="w",
                  bg=C["sidebar"], fg="#F87171", font=FONT,
                  relief="flat", pady=10, padx=10,
                  command=self._logout, cursor="hand2").pack(fill="x", side="bottom")
        tk.Label(self.sidebar, text=f"  {self.current_user['full_name']}\n  {self.current_user['role'].title()}",
                 bg=C["sidebar"], fg="#94A3B8", font=("Segoe UI", 9),
                 anchor="w", justify="left").pack(side="bottom", fill="x", pady=4)

        # ── Main content ────────────────────────────────────
        self.content = tk.Frame(self, bg=C["bg"])
        self.content.pack(side="left", fill="both", expand=True)
        self._current = None
        self._frames  = {}

    def _show_module(self, key):
        self._current = key
        for k, b in self.nav_btns.items():
            b.config(bg=C["accent"] if k == key else C["sidebar"],
                     fg="white" if k == key else "#CBD5E1")
        for f in self.content.winfo_children():
            f.destroy()
        modules = {
            "dashboard": DashboardFrame,
            "pos":       POSFrame,
            "inventory": InventoryFrame,
            "customers": CustomerFrame,
            "suppliers": SupplierFrame,
            "purchases": PurchaseFrame,
            "expenses":  ExpenseFrame,
            "reports":   ReportsFrame,
            "users":     UserFrame,
        }
        cls = modules.get(key, DashboardFrame)
        cls(self.content, self.current_user).pack(fill="both", expand=True)

    def _logout(self):
        self.destroy()
        main()


# ═══════════════════════════════════════════════════════════════
#  DASHBOARD
# ═══════════════════════════════════════════════════════════════
class DashboardFrame(tk.Frame):
    def __init__(self, parent, user):
        super().__init__(parent, bg=C["bg"])
        self.user = user
        self._build()

    def _build(self):
        # Header
        hdr = tk.Frame(self, bg=C["header"], pady=14, padx=20)
        hdr.pack(fill="x")
        tk.Label(hdr, text="📊  Dashboard", font=FONT_H,
                 bg=C["header"], fg="white").pack(side="left")
        tk.Label(hdr, text=datetime.now().strftime("%A, %d %B %Y"),
                 font=FONT, bg=C["header"], fg="#94A3B8").pack(side="right")

        # Stat cards
        stats = M.get_dashboard_stats()
        cards_data = [
            ("Today's Sales",    format_currency(stats["today_sales"]),   "💰", C["success"]),
            ("Today's Invoices", str(stats["today_invoices"]),             "🧾", C["accent"]),
            ("Total Products",   str(stats["total_products"]),             "📦", C["header"]),
            ("Low Stock Items",  str(stats["low_stock_count"]),            "⚠️",  C["warning"]),
            ("Total Customers",  str(stats["total_customers"]),            "👥", C["accent2"]),
            ("Month Sales",      format_currency(stats["month_sales"]),    "📈", C["success"]),
            ("Month Expenses",   format_currency(stats["month_expenses"]), "📉", C["danger"]),
            ("Stock Value",      format_currency(stats["total_stock_value"]),"🏪", C["header"]),
        ]
        cards_frame = tk.Frame(self, bg=C["bg"])
        cards_frame.pack(fill="x", padx=20, pady=16)
        for i, (title, value, icon, color) in enumerate(cards_data):
            c_frame = tk.Frame(cards_frame, bg=color, padx=16, pady=14, width=200)
            c_frame.grid(row=i//4, column=i%4, padx=6, pady=6, sticky="ew")
            c_frame.grid_propagate(False)
            tk.Label(c_frame, text=f"{icon}  {title}", font=("Segoe UI", 9),
                     bg=color, fg="white").pack(anchor="w")
            tk.Label(c_frame, text=value, font=("Segoe UI", 16, "bold"),
                     bg=color, fg="white").pack(anchor="w")
        for col in range(4):
            cards_frame.grid_columnconfigure(col, weight=1)

        # Bottom: top products + low stock
        bottom = tk.Frame(self, bg=C["bg"])
        bottom.pack(fill="both", expand=True, padx=20, pady=6)
        bottom.columnconfigure(0, weight=1)
        bottom.columnconfigure(1, weight=1)

        # Top Products
        tp = card(bottom)
        tp.grid(row=0, column=0, sticky="nsew", padx=(0,8))
        tk.Label(tp, text="🏆  Top Selling Products (This Month)",
                 font=FONT_B, bg=C["card"], fg=C["header"], pady=8).pack(anchor="w", padx=12)
        ttk.Separator(tp).pack(fill="x")
        cols = ("Product", "Qty Sold", "Revenue")
        tree = ttk.Treeview(tp, columns=cols, show="headings", height=8)
        for col in cols:
            tree.heading(col, text=col)
            tree.column(col, width=120)
        tree.pack(fill="both", padx=6, pady=6)
        for row in M.get_top_products(8):
            tree.insert("", "end", values=(
                row["name"], f"{row['sold_qty']:.0f}",
                format_currency(row["revenue"])))

        # Low Stock
        ls = card(bottom)
        ls.grid(row=0, column=1, sticky="nsew", padx=(8,0))
        tk.Label(ls, text="⚠️  Low Stock Alert",
                 font=FONT_B, bg=C["card"], fg=C["danger"], pady=8).pack(anchor="w", padx=12)
        ttk.Separator(ls).pack(fill="x")
        cols2 = ("Product", "Stock", "Min")
        tree2 = ttk.Treeview(ls, columns=cols2, show="headings", height=8)
        for col in cols2:
            tree2.heading(col, text=col)
            tree2.column(col, width=120)
        tree2.pack(fill="both", padx=6, pady=6)
        for p in M.get_all_products(low_stock=True)[:10]:
            tree2.insert("", "end", values=(
                p["name"], f"{p['stock_qty']:.1f} {p['unit']}", f"{p['min_stock']:.1f}"),
                tags=("low",))
        tree2.tag_configure("low", foreground=C["danger"])


# ═══════════════════════════════════════════════════════════════
#  POINT OF SALE
# ═══════════════════════════════════════════════════════════════
class POSFrame(tk.Frame):
    def __init__(self, parent, user):
        super().__init__(parent, bg=C["bg"])
        self.user = user
        self.cart = []
        self.customer_id = None
        self._build()

    def _build(self):
        hdr = tk.Frame(self, bg=C["header"], pady=12, padx=20)
        hdr.pack(fill="x")
        tk.Label(hdr, text="🛒  Point of Sale", font=FONT_H,
                 bg=C["header"], fg="white").pack(side="left")
        tk.Label(hdr, text=f"Invoice: {generate_invoice_no()}",
                 font=FONT, bg=C["header"], fg="#94A3B8").pack(side="right")

        body = tk.Frame(self, bg=C["bg"])
        body.pack(fill="both", expand=True, padx=12, pady=10)
        body.columnconfigure(0, weight=2)
        body.columnconfigure(1, weight=1)
        body.rowconfigure(0, weight=1)

        # ── LEFT: product search + cart ──────────────────────
        left = card(body)
        left.grid(row=0, column=0, sticky="nsew", padx=(0,6))
        left.rowconfigure(1, weight=1)
        left.columnconfigure(0, weight=1)

        # Search bar
        sbar = tk.Frame(left, bg=C["card"])
        sbar.grid(row=0, column=0, sticky="ew", padx=10, pady=10)
        tk.Label(sbar, text="🔍 Barcode / Product:", font=FONT_B, bg=C["card"]).pack(side="left")
        self.search_var = tk.StringVar()
        self.search_entry = ttk.Entry(sbar, textvariable=self.search_var, width=28, font=FONT)
        self.search_entry.pack(side="left", padx=6)
        self.search_entry.bind("<Return>", self._search_product)
        btn(sbar, "Add", self._search_product, width=8).pack(side="left")

        # Product suggestion list
        self.suggest_frame = tk.Frame(left, bg=C["card"])
        self.suggest_frame.grid(row=1, column=0, sticky="ew", padx=10)

        # Cart table
        cart_label = tk.Frame(left, bg=C["card"])
        cart_label.grid(row=2, column=0, sticky="ew", padx=10, pady=(6,0))
        tk.Label(cart_label, text="🛒 Cart Items", font=FONT_B, bg=C["card"], fg=C["header"]).pack(side="left")
        btn(cart_label, "🗑 Clear Cart", self._clear_cart, color=C["danger"], width=12).pack(side="right")

        cols = ("Product", "Qty", "Price", "Disc%", "Total")
        tree_frame = tk.Frame(left, bg=C["card"])
        tree_frame.grid(row=3, column=0, sticky="nsew", padx=10, pady=4)
        left.rowconfigure(3, weight=1)
        vsb = ttk.Scrollbar(tree_frame)
        vsb.pack(side="right", fill="y")
        self.cart_tree = ttk.Treeview(tree_frame, columns=cols, show="headings",
                                       height=12, yscrollcommand=vsb.set)
        vsb.config(command=self.cart_tree.yview)
        widths = [200, 60, 80, 60, 90]
        for col, w in zip(cols, widths):
            self.cart_tree.heading(col, text=col)
            self.cart_tree.column(col, width=w)
        self.cart_tree.pack(fill="both", expand=True)
        self.cart_tree.bind("<Delete>", self._remove_item)
        self.cart_tree.bind("<Double-1>", self._edit_qty)

        tip = tk.Label(left, text="Del = remove item | Double-click = edit qty",
                       font=("Segoe UI", 8), bg=C["card"], fg=C["subtext"])
        tip.grid(row=4, column=0, sticky="w", padx=12, pady=2)

        # ── RIGHT: customer + totals + payment ───────────────
        right = card(body)
        right.grid(row=0, column=1, sticky="nsew", padx=(6,0))
        right.columnconfigure(0, weight=1)

        # Customer selector
        cust_frame = tk.Frame(right, bg=C["card"])
        cust_frame.pack(fill="x", padx=10, pady=10)
        tk.Label(cust_frame, text="👥 Customer", font=FONT_B, bg=C["card"]).pack(anchor="w")
        self.cust_var = tk.StringVar(value="Walk-in Customer")
        ttk.Entry(cust_frame, textvariable=self.cust_var, width=26).pack(side="left", padx=(0,4))
        btn(cust_frame, "Find", self._find_customer, width=6).pack(side="left")

        ttk.Separator(right).pack(fill="x", padx=10)

        # Totals
        tot = tk.Frame(right, bg=C["card"], padx=10, pady=10)
        tot.pack(fill="x")
        self.subtotal_var = tk.StringVar(value="0.00")
        self.discount_var = tk.StringVar(value="0")
        self.tax_var      = tk.StringVar(value=f"{TAX_RATE*100:.0f}")
        self.total_var    = tk.StringVar(value="0.00")
        self.paid_var     = tk.StringVar(value="0")

        for label, var, editable in [
            ("Subtotal (₹)", self.subtotal_var, False),
            ("Discount (%)", self.discount_var, True),
            ("Tax (%)",      self.tax_var,      True),
        ]:
            row = tk.Frame(tot, bg=C["card"])
            row.pack(fill="x", pady=2)
            tk.Label(row, text=label, font=FONT, bg=C["card"], width=14, anchor="w").pack(side="left")
            e = ttk.Entry(row, textvariable=var, width=12,
                          state="normal" if editable else "readonly")
            e.pack(side="right")
            if editable:
                var.trace_add("write", lambda *a: self._recalculate())

        ttk.Separator(tot).pack(fill="x", pady=6)
        total_row = tk.Frame(tot, bg=C["card"])
        total_row.pack(fill="x")
        tk.Label(total_row, text="TOTAL (₹)", font=("Segoe UI", 12, "bold"),
                 bg=C["card"], fg=C["accent"]).pack(side="left")
        tk.Label(total_row, textvariable=self.total_var,
                 font=("Segoe UI", 16, "bold"), bg=C["card"], fg=C["success"]).pack(side="right")

        ttk.Separator(right).pack(fill="x", padx=10, pady=6)

        # Payment
        pay = tk.Frame(right, bg=C["card"], padx=10)
        pay.pack(fill="x")
        tk.Label(pay, text="💵 Payment Method", font=FONT_B, bg=C["card"]).pack(anchor="w")
        self.method_var = tk.StringVar(value="cash")
        for m in [("Cash", "cash"), ("Card", "card"), ("UPI", "upi"), ("Credit", "credit")]:
            tk.Radiobutton(pay, text=m[0], variable=self.method_var, value=m[1],
                           bg=C["card"], font=FONT).pack(anchor="w")

        tk.Label(pay, text="Amount Paid (₹)", font=FONT_B, bg=C["card"]).pack(anchor="w", pady=(8,0))
        ttk.Entry(pay, textvariable=self.paid_var, width=20, font=FONT).pack(anchor="w")
        self.change_lbl = tk.Label(pay, text="Change: ₹ 0.00",
                                   font=FONT_B, bg=C["card"], fg=C["success"])
        self.change_lbl.pack(anchor="w", pady=4)
        self.paid_var.trace_add("write", lambda *a: self._show_change())

        ttk.Separator(right).pack(fill="x", padx=10, pady=8)

        btn(right, "✅  COMPLETE SALE", self._complete_sale,
            color=C["success"], width=22).pack(padx=10, pady=4, fill="x")
        btn(right, "🖨  Print Last Receipt", self._show_last_receipt,
            color=C["header"], width=22).pack(padx=10, pady=2, fill="x")

        self.last_receipt = None
        self.invoice_no = generate_invoice_no()

    # ── POS helpers ────────────────────────────────────────────
    def _search_product(self, event=None):
        q = self.search_var.get().strip()
        if not q:
            return
        # Try barcode first
        prod = M.get_product_by_barcode(q)
        if prod:
            self._add_to_cart(prod)
            self.search_var.set("")
            return
        # Search by name
        results = M.get_all_products(search=q)
        for w in self.suggest_frame.winfo_children():
            w.destroy()
        if not results:
            tk.Label(self.suggest_frame, text="No product found", fg=C["danger"],
                     bg=C["card"], font=FONT).pack()
            return
        if len(results) == 1:
            self._add_to_cart(results[0])
            self.search_var.set("")
            return
        for prod in results[:6]:
            b = tk.Button(self.suggest_frame,
                          text=f"{prod['name']} — {format_currency(prod['selling_price'])} ({prod['stock_qty']:.0f} left)",
                          anchor="w", relief="flat", bg=C["white"], font=FONT, cursor="hand2",
                          command=lambda p=prod: self._pick_product(p))
            b.pack(fill="x", pady=1)

    def _pick_product(self, prod):
        for w in self.suggest_frame.winfo_children():
            w.destroy()
        self._add_to_cart(prod)
        self.search_var.set("")

    def _add_to_cart(self, prod):
        if prod["stock_qty"] <= 0:
            messagebox.showwarning("Out of Stock", f"'{prod['name']}' is out of stock!")
            return
        for item in self.cart:
            if item["product_id"] == prod["id"]:
                if item["qty"] >= prod["stock_qty"]:
                    messagebox.showwarning("Stock Limit", "Not enough stock!")
                    return
                item["qty"] += 1
                item["total"] = item["qty"] * item["price"] * (1 - item["discount"]/100)
                self._refresh_cart()
                return
        self.cart.append({
            "product_id": prod["id"],
            "name":       prod["name"],
            "qty":        1,
            "price":      prod["selling_price"],
            "discount":   0,
            "total":      prod["selling_price"],
            "unit":       prod.get("unit", "pcs"),
            "stock":      prod["stock_qty"],
        })
        self._refresh_cart()

    def _refresh_cart(self):
        for row in self.cart_tree.get_children():
            self.cart_tree.delete(row)
        for item in self.cart:
            self.cart_tree.insert("", "end", values=(
                item["name"], f"{item['qty']} {item['unit']}",
                f"{item['price']:.2f}", f"{item['discount']:.0f}%",
                f"{item['total']:.2f}"))
        self._recalculate()

    def _recalculate(self):
        subtotal = float(sum(i["total"] for i in self.cart))
        try:
            disc_pct = float((self.discount_var.get() or '0').replace('%', ''))
            tax_pct  = float((self.tax_var.get() or '0').replace('%', ''))
        except ValueError:
            disc_pct = tax_pct = 0
        disc_amt = subtotal * disc_pct / 100
        tax_amt  = (subtotal - disc_amt) * tax_pct / 100
        total    = subtotal - disc_amt + tax_amt
        self.subtotal_var.set(f"{subtotal:.2f}")
        self.total_var.set(f"{total:.2f}")
        self._show_change()
    def _show_change(self):
        try:
            total = float(self.total_var.get())
            paid  = float(self.paid_var.get() or 0)
            change = paid - total
            self.change_lbl.config(text=f"Change: ₹ {change:.2f}",
                                   fg=C["success"] if change >= 0 else C["danger"])
        except ValueError:
            pass

    def _remove_item(self, event=None):
        sel = self.cart_tree.selection()
        if not sel:
            return
        idx = self.cart_tree.index(sel[0])
        self.cart.pop(idx)
        self._refresh_cart()

    def _edit_qty(self, event=None):
        sel = self.cart_tree.selection()
        if not sel:
            return
        idx = self.cart_tree.index(sel[0])
        item = self.cart[idx]
        new_qty = simpledialog.askfloat("Edit Qty", f"Qty for {item['name']}:",
                                         initialvalue=item["qty"], minvalue=0.1,
                                         maxvalue=item["stock"])
        if new_qty:
            item["qty"]   = new_qty
            item["total"] = new_qty * item["price"] * (1 - item["discount"]/100)
            self._refresh_cart()

    def _clear_cart(self):
        if self.cart and messagebox.askyesno("Clear Cart", "Clear all items?"):
            self.cart.clear()
            self._refresh_cart()

    def _find_customer(self):
        q = self.cust_var.get().strip()
        results = M.get_all_customers(search=q)
        if not results:
            messagebox.showinfo("Not Found", "Customer not found.")
            return
        if len(results) == 1:
            self.customer_id = results[0]["id"]
            self.cust_var.set(results[0]["name"])
            return
        # Popup chooser
        win = tk.Toplevel(self)
        win.title("Select Customer")
        win.geometry("340x300")
        win.configure(bg=C["bg"])
        tree = ttk.Treeview(win, columns=("Name", "Phone"), show="headings", height=10)
        tree.heading("Name", text="Name")
        tree.heading("Phone", text="Phone")
        tree.pack(fill="both", expand=True, padx=10, pady=10)
        for r in results:
            tree.insert("", "end", values=(r["name"], r["phone"]))
        def pick():
            sel = tree.selection()
            if sel:
                idx = tree.index(sel[0])
                self.customer_id = results[idx]["id"]
                self.cust_var.set(results[idx]["name"])
                win.destroy()
        btn(win, "Select", pick).pack(pady=4)

    def _complete_sale(self):
        if not self.cart:
            messagebox.showwarning("Empty Cart", "Add items to cart first!")
            return
        subtotal = float(self.subtotal_var.get())
        disc_pct = float((self.discount_var.get() or '0').replace('%', ''))
        tax_pct  = float((self.tax_var.get() or '0').replace('%', ''))
        disc_amt = subtotal * disc_pct / 100
        tax_amt  = (subtotal - disc_amt) * tax_pct / 100
        total    = subtotal - disc_amt + tax_amt

        try:
            paid = float(self.paid_var.get() or 0)
        except ValueError:
            paid = 0

        method = self.method_var.get()
        if method == "cash" and paid < total:
            messagebox.showerror("Insufficient", "Paid amount is less than total!")
            return

        change = paid - total
        ok, result = M.save_sale(
            invoice_no=self.invoice_no,
            customer_id=self.customer_id,
            user_id=self.user["id"],
            branch_id=1,
            subtotal=subtotal, discount=disc_amt, tax=tax_amt,
            total=total, paid=paid, change=change,
            method=method, items=self.cart
        )
        if not ok:
            messagebox.showerror("Error", result)
            return

        receipt = get_receipt_text(
            self.invoice_no, self.cart, subtotal, disc_amt, tax_amt,
            total, paid, change, method,
            self.cust_var.get(), self.user["full_name"])
        self.last_receipt = receipt

        # Show receipt popup
        self._show_receipt_popup(receipt)

        # Reset
        self.cart.clear()
        self.customer_id = None
        self.cust_var.set("Walk-in Customer")
        self.paid_var.set("0")
        self.discount_var.set("0")
        self.invoice_no = generate_invoice_no()
        self._refresh_cart()

    def _show_receipt_popup(self, receipt):
        win = tk.Toplevel(self)
        win.title("Receipt")
        win.geometry("420x520")
        win.configure(bg=C["bg"])
        txt = tk.Text(win, font=FONT_MONO, bg="white", width=46, height=30)
        txt.pack(padx=10, pady=10, fill="both", expand=True)
        txt.insert("end", receipt)
        txt.config(state="disabled")
        btn(win, "Close", win.destroy, color=C["danger"]).pack(pady=6)

    def _show_last_receipt(self):
        if self.last_receipt:
            self._show_receipt_popup(self.last_receipt)
        else:
            messagebox.showinfo("No Receipt", "No receipt available yet.")


# ═══════════════════════════════════════════════════════════════
#  INVENTORY
# ═══════════════════════════════════════════════════════════════
class InventoryFrame(tk.Frame):
    def __init__(self, parent, user):
        super().__init__(parent, bg=C["bg"])
        self.user = user
        self._build()
        self._load()

    def _build(self):
        # Header
        hdr = tk.Frame(self, bg=C["header"], pady=12, padx=20)
        hdr.pack(fill="x")
        tk.Label(hdr, text="📦  Inventory Management", font=FONT_H,
                 bg=C["header"], fg="white").pack(side="left")

        # Toolbar
        tb = tk.Frame(self, bg=C["bg"], pady=8, padx=12)
        tb.pack(fill="x")
        tk.Label(tb, text="Search:", font=FONT, bg=C["bg"]).pack(side="left")
        self.search_var = tk.StringVar()
        ttk.Entry(tb, textvariable=self.search_var, width=22).pack(side="left", padx=4)
        btn(tb, "🔍 Search", self._load, width=10).pack(side="left", padx=2)

        cats = ["All"] + [c["name"] for c in M.get_categories()]
        tk.Label(tb, text="Category:", font=FONT, bg=C["bg"]).pack(side="left", padx=(10,2))
        self.cat_var = tk.StringVar(value="All")
        self.cat_cb  = ttk.Combobox(tb, textvariable=self.cat_var, values=cats, width=14, state="readonly")
        self.cat_cb.pack(side="left")
        self.cat_cb.bind("<<ComboboxSelected>>", lambda e: self._load())

        self.low_var = tk.BooleanVar()
        tk.Checkbutton(tb, text="Low Stock Only", variable=self.low_var,
                       bg=C["bg"], command=self._load).pack(side="left", padx=10)

        btn(tb, "➕ Add Product", self._add_product, color=C["success"]).pack(side="right", padx=2)
        btn(tb, "📤 Export CSV",  self._export,      color=C["header"]).pack(side="right", padx=2)

        # Table
        cols = ("ID", "Barcode", "Name", "Category", "Unit", "Cost", "Price", "Stock", "Min", "Supplier")
        self.tree = make_tree(self, cols)
        widths = [40, 100, 200, 100, 50, 70, 70, 70, 50, 120]
        for col, w in zip(cols, widths):
            self.tree.heading(col, text=col)
            self.tree.column(col, width=w, anchor="center")
        self.tree.column("Name", anchor="w")
        self.tree.bind("<Double-1>", self._edit_product)
        self.tree.tag_configure("low", foreground=C["danger"])

        # Bottom action bar
        bar = tk.Frame(self, bg=C["bg"], pady=6, padx=12)
        bar.pack(fill="x")
        btn(bar, "✏️ Edit",          self._edit_product,  color=C["accent"]).pack(side="left", padx=2)
        btn(bar, "🔄 Adjust Stock",  self._adjust_stock,  color=C["warning"]).pack(side="left", padx=2)
        btn(bar, "🗑 Delete",        self._delete_product, color=C["danger"]).pack(side="left", padx=2)
        self.status_lbl = tk.Label(bar, text="", font=FONT, bg=C["bg"], fg=C["subtext"])
        self.status_lbl.pack(side="right")

    def _load(self, *a):
        search = self.search_var.get()
        cat    = self.cat_var.get()
        cats   = M.get_categories()
        cat_id = next((c["id"] for c in cats if c["name"]==cat), None)
        rows   = M.get_all_products(search, cat_id if cat != "All" else None, self.low_var.get())
        for r in self.tree.get_children():
            self.tree.delete(r)
        for p in rows:
            tag = "low" if p["stock_qty"] <= p["min_stock"] else ""
            self.tree.insert("", "end", values=(
                p["id"], p.get("barcode",""), p["name"],
                p.get("category_name",""), p["unit"],
                f"{p['cost_price']:.2f}", f"{p['selling_price']:.2f}",
                f"{p['stock_qty']:.2f}", f"{p['min_stock']:.1f}",
                p.get("supplier_name","")), tags=(tag,))
        self.status_lbl.config(text=f"{len(rows)} products")

    def _add_product(self):
        ProductDialog(self, None, self.user).grab_set()

    def _edit_product(self, event=None):
        sel = self.tree.selection()
        if not sel:
            return
        pid = self.tree.item(sel[0])["values"][0]
        prod = M.get_product_by_id(pid)
        ProductDialog(self, prod, self.user).grab_set()

    def _delete_product(self):
        sel = self.tree.selection()
        if not sel:
            return
        pid  = self.tree.item(sel[0])["values"][0]
        name = self.tree.item(sel[0])["values"][2]
        if messagebox.askyesno("Delete", f"Delete '{name}'?"):
            M.delete_product(pid)
            self._load()

    def _adjust_stock(self):
        sel = self.tree.selection()
        if not sel:
            return
        pid  = int(self.tree.item(sel[0])["values"][0])
        name = self.tree.item(sel[0])["values"][2]
        StockAdjDialog(self, pid, name, self.user).grab_set()

    def _export(self):
        rows = M.get_all_products()
        path = export_to_csv(rows, f"inventory_{datetime.now().strftime('%Y%m%d')}.csv")
        messagebox.showinfo("Exported", f"Saved to:\n{path}")

    def refresh(self):
        self._load()


class ProductDialog(tk.Toplevel):
    def __init__(self, parent_frame, product, user):
        super().__init__()
        self.parent_frame = parent_frame
        self.product = product
        self.user    = user
        self.title("Edit Product" if product else "Add Product")
        self.configure(bg=C["card"])
        self.resizable(False, False)
        self._center(520, 540)
        self._build()
        if product:
            self._populate()

    def _center(self, w, h):
        sw, sh = self.winfo_screenwidth(), self.winfo_screenheight()
        self.geometry(f"{w}x{h}+{(sw-w)//2}+{(sh-h)//2}")

    def _build(self):
        frm = tk.Frame(self, bg=C["card"], padx=20, pady=16)
        frm.pack(fill="both", expand=True)
        tk.Label(frm, text="Product Details", font=FONT_H, bg=C["card"],
                 fg=C["header"]).grid(row=0, column=0, columnspan=4, pady=(0,12), sticky="w")

        self.barcode_var = entry_row(frm, "Barcode",       1, 0)
        self.name_var    = entry_row(frm, "Name *",        2, 0, width=28)
        self.desc_var    = entry_row(frm, "Description",   3, 0, width=28)

        cats   = M.get_categories()
        cat_nm = [c["name"] for c in cats]
        self.cat_var, self.cat_cb = combo_row(frm, "Category", 4, cat_nm)
        self._cats = cats

        sups   = M.get_all_suppliers()
        sup_nm = [""] + [s["name"] for s in sups]
        self.sup_var, self.sup_cb = combo_row(frm, "Supplier", 5, sup_nm)
        self._sups = sups

        units = ["pcs", "kg", "g", "litre", "ml", "box", "dozen", "pair", "set", "roll"]
        self.unit_var, _ = combo_row(frm, "Unit", 6, units)

        self.cost_var  = entry_row(frm, "Cost Price *", 1, 2)
        self.price_var = entry_row(frm, "Sale Price *", 2, 2)
        self.stock_var = entry_row(frm, "Opening Stock", 3, 2)
        self.min_var   = entry_row(frm, "Min Stock",    4, 2)
        self.max_var   = entry_row(frm, "Max Stock",    5, 2)

        btns = tk.Frame(frm, bg=C["card"])
        btns.grid(row=9, column=0, columnspan=4, pady=14)
        btn(btns, "💾 Save", self._save, color=C["success"]).pack(side="left", padx=8)
        btn(btns, "Cancel",  self.destroy, color=C["danger"]).pack(side="left")

    def _populate(self):
        p = self.product
        self.barcode_var.set(p.get("barcode") or "")
        self.name_var.set(p["name"])
        self.desc_var.set(p.get("description") or "")
        self.cost_var.set(str(p["cost_price"]))
        self.price_var.set(str(p["selling_price"]))
        self.stock_var.set(str(p["stock_qty"]))
        self.min_var.set(str(p["min_stock"]))
        self.max_var.set(str(p["max_stock"]))
        self.unit_var.set(p.get("unit", "pcs"))
        if p.get("category_id"):
            cat = next((c for c in self._cats if c["id"]==p["category_id"]), None)
            if cat:
                self.cat_var.set(cat["name"])
        if p.get("supplier_id"):
            sup = next((s for s in self._sups if s["id"]==p["supplier_id"]), None)
            if sup:
                self.sup_var.set(sup["name"])

    def _save(self):
        name = self.name_var.get().strip()
        if not name:
            messagebox.showerror("Error", "Name is required"); return
        try:
            cost  = float(self.cost_var.get() or 0)
            price = float(self.price_var.get())
            stock = float(self.stock_var.get() or 0)
            mn    = float(self.min_var.get() or 5)
            mx    = float(self.max_var.get() or 1000)
        except ValueError:
            messagebox.showerror("Error", "Invalid number in numeric fields"); return

        cat_name = self.cat_var.get()
        cat_id   = next((c["id"] for c in self._cats if c["name"]==cat_name), None)
        sup_name = self.sup_var.get()
        sup_id   = next((s["id"] for s in self._sups if s["name"]==sup_name), None)

        if self.product:
            M.update_product(self.product["id"], self.barcode_var.get().strip(),
                             name, self.desc_var.get().strip(), cat_id, sup_id,
                             self.unit_var.get(), cost, price, mn, mx)
        else:
            ok, msg = M.add_product(
                self.barcode_var.get().strip(), name, self.desc_var.get().strip(),
                cat_id, sup_id, self.unit_var.get(), cost, price, stock, mn, mx)
            if not ok:
                messagebox.showerror("Error", msg); return

        self.parent_frame.refresh()
        self.destroy()


class StockAdjDialog(tk.Toplevel):
    def __init__(self, parent_frame, product_id, product_name, user):
        super().__init__()
        self.parent_frame = parent_frame
        self.product_id   = product_id
        self.user         = user
        self.title(f"Adjust Stock — {product_name}")
        self.configure(bg=C["card"])
        self.resizable(False, False)
        self.geometry("360x260")
        self._build()

    def _build(self):
        frm = tk.Frame(self, bg=C["card"], padx=20, pady=20)
        frm.pack(fill="both", expand=True)
        self.type_var = tk.StringVar(value="add")
        tk.Label(frm, text="Adjustment Type", font=FONT_B, bg=C["card"]).pack(anchor="w")
        for text, val in [("Add Stock ✅", "add"), ("Remove Stock ❌", "remove")]:
            tk.Radiobutton(frm, text=text, variable=self.type_var, value=val,
                           bg=C["card"], font=FONT).pack(anchor="w")
        tk.Label(frm, text="Quantity", font=FONT_B, bg=C["card"]).pack(anchor="w", pady=(8,0))
        self.qty_var = tk.StringVar()
        ttk.Entry(frm, textvariable=self.qty_var, width=20, font=FONT).pack(anchor="w")
        tk.Label(frm, text="Reason", font=FONT_B, bg=C["card"]).pack(anchor="w", pady=(8,0))
        self.reason_var = tk.StringVar()
        ttk.Entry(frm, textvariable=self.reason_var, width=30, font=FONT).pack(anchor="w")

        row = tk.Frame(frm, bg=C["card"])
        row.pack(pady=14)
        btn(row, "✅ Apply", self._apply, color=C["success"]).pack(side="left", padx=6)
        btn(row, "Cancel",  self.destroy, color=C["danger"]).pack(side="left")

    def _apply(self):
        ok, qty = validate_number(self.qty_var.get())
        if not ok:
            messagebox.showerror("Error", qty); return
        M.adjust_stock(self.product_id, self.user["id"],
                       self.type_var.get(), qty, self.reason_var.get())
        self.parent_frame.refresh()
        self.destroy()


# ═══════════════════════════════════════════════════════════════
#  CUSTOMERS
# ═══════════════════════════════════════════════════════════════
class CustomerFrame(tk.Frame):
    def __init__(self, parent, user):
        super().__init__(parent, bg=C["bg"])
        self.user = user
        self._build()
        self._load()

    def _build(self):
        hdr = tk.Frame(self, bg=C["header"], pady=12, padx=20)
        hdr.pack(fill="x")
        tk.Label(hdr, text="👥  Customer Management", font=FONT_H,
                 bg=C["header"], fg="white").pack(side="left")

        tb = tk.Frame(self, bg=C["bg"], pady=8, padx=12)
        tb.pack(fill="x")
        self.search_var = tk.StringVar()
        ttk.Entry(tb, textvariable=self.search_var, width=22).pack(side="left", padx=4)
        btn(tb, "🔍 Search", self._load, width=10).pack(side="left")
        btn(tb, "➕ Add Customer", self._add, color=C["success"]).pack(side="right", padx=4)

        cols = ("ID", "Name", "Phone", "Email", "Address", "Points", "Total Spent", "Since")
        self.tree = make_tree(self, cols)
        widths = [40, 160, 110, 160, 180, 60, 90, 90]
        for col, w in zip(cols, widths):
            self.tree.heading(col, text=col)
            self.tree.column(col, width=w)
        self.tree.bind("<Double-1>", self._edit)

        bar = tk.Frame(self, bg=C["bg"], pady=6, padx=12)
        bar.pack(fill="x")
        btn(bar, "✏️ Edit", self._edit, color=C["accent"]).pack(side="left", padx=2)
        btn(bar, "📋 History", self._history, color=C["header"]).pack(side="left", padx=2)

    def _load(self, *a):
        rows = M.get_all_customers(self.search_var.get())
        for r in self.tree.get_children():
            self.tree.delete(r)
        for c in rows:
            self.tree.insert("", "end", values=(
                c["id"], c["name"], c.get("phone",""), c.get("email",""),
                c.get("address",""), f"{c['points']:.0f}",
                format_currency(c["total_spent"]),
              (c["created_at"] or "")[:10]))

    def _add(self):
        CustomerDialog(self, None).grab_set()

    def _edit(self, event=None):
        sel = self.tree.selection()
        if not sel: return
        cid = self.tree.item(sel[0])["values"][0]
        rows = M.get_all_customers()
        cust = next((c for c in rows if c["id"]==cid), None)
        if cust:
            CustomerDialog(self, cust).grab_set()

    def _history(self):
        sel = self.tree.selection()
        if not sel: return
        cid  = self.tree.item(sel[0])["values"][0]
        name = self.tree.item(sel[0])["values"][1]
        sales = M.get_sales(search="", limit=500)
        sales = [s for s in sales if s.get("customer_id")==cid]
        win = tk.Toplevel(self)
        win.title(f"Purchase History — {name}")
        win.geometry("560x380")
        win.configure(bg=C["bg"])
        cols = ("Invoice", "Date", "Total", "Method")
        tree = ttk.Treeview(win, columns=cols, show="headings", height=14)
        for col in cols:
            tree.heading(col, text=col); tree.column(col, width=120)
        tree.pack(fill="both", expand=True, padx=10, pady=10)
        for s in sales:
            tree.insert("", "end", values=(
                s["invoice_no"], s["sale_date"][:16],
                format_currency(s["total"]), s["payment_method"]))

    def refresh(self):
        self._load()


class CustomerDialog(tk.Toplevel):
    def __init__(self, parent_frame, customer):
        super().__init__()
        self.parent_frame = parent_frame
        self.customer = customer
        self.title("Edit Customer" if customer else "Add Customer")
        self.configure(bg=C["card"])
        self.resizable(False, False)
        self.geometry("380x300")
        self._build()
        if customer:
            self._populate()

    def _build(self):
        frm = tk.Frame(self, bg=C["card"], padx=20, pady=16)
        frm.pack(fill="both", expand=True)
        self.name_var    = entry_row(frm, "Name *",  0, 0, width=26)
        self.phone_var   = entry_row(frm, "Phone",   1, 0, width=26)
        self.email_var   = entry_row(frm, "Email",   2, 0, width=26)
        self.address_var = entry_row(frm, "Address", 3, 0, width=26)
        row = tk.Frame(frm, bg=C["card"])
        row.grid(row=5, column=0, columnspan=2, pady=12)
        btn(row, "💾 Save", self._save, color=C["success"]).pack(side="left", padx=8)
        btn(row, "Cancel",  self.destroy, color=C["danger"]).pack(side="left")

    def _populate(self):
        c = self.customer
        self.name_var.set(c["name"]); self.phone_var.set(c.get("phone",""))
        self.email_var.set(c.get("email","")); self.address_var.set(c.get("address",""))

    def _save(self):
        name = self.name_var.get().strip()
        if not name:
            messagebox.showerror("Error", "Name is required"); return
        if self.customer:
            M.update_customer(self.customer["id"], name, self.phone_var.get(),
                              self.email_var.get(), self.address_var.get())
        else:
            M.add_customer(name, self.phone_var.get(), self.email_var.get(), self.address_var.get())
        self.parent_frame.refresh()
        self.destroy()


# ═══════════════════════════════════════════════════════════════
#  SUPPLIERS
# ═══════════════════════════════════════════════════════════════
class SupplierFrame(tk.Frame):
    def __init__(self, parent, user):
        super().__init__(parent, bg=C["bg"])
        self.user = user
        self._build()
        self._load()

    def _build(self):
        hdr = tk.Frame(self, bg=C["header"], pady=12, padx=20)
        hdr.pack(fill="x")
        tk.Label(hdr, text="🚚  Supplier Management", font=FONT_H,
                 bg=C["header"], fg="white").pack(side="left")
        btn(hdr, "➕ Add Supplier", self._add, color=C["success"]).pack(side="right")

        cols = ("ID", "Name", "Contact", "Phone", "Email", "Address")
        self.tree = make_tree(self, cols)
        for col in cols:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=140)
        self.tree.column("ID", width=40)
        self.tree.bind("<Double-1>", self._edit)

        bar = tk.Frame(self, bg=C["bg"], pady=6, padx=12)
        bar.pack(fill="x")
        btn(bar, "✏️ Edit", self._edit, color=C["accent"]).pack(side="left", padx=2)

    def _load(self):
        for r in self.tree.get_children(): self.tree.delete(r)
        for s in M.get_all_suppliers():
            self.tree.insert("", "end", values=(
                s["id"], s["name"], s.get("contact",""), s.get("phone",""),
                s.get("email",""), s.get("address","")))

    def _add(self):
        SupplierDialog(self, None).grab_set()

    def _edit(self, event=None):
        sel = self.tree.selection()
        if not sel: return
        sid  = self.tree.item(sel[0])["values"][0]
        sups = M.get_all_suppliers()
        sup  = next((s for s in sups if s["id"]==sid), None)
        if sup:
            SupplierDialog(self, sup).grab_set()

    def refresh(self):
        self._load()


class SupplierDialog(tk.Toplevel):
    def __init__(self, parent_frame, supplier):
        super().__init__()
        self.parent_frame = parent_frame
        self.supplier = supplier
        self.title("Edit Supplier" if supplier else "Add Supplier")
        self.configure(bg=C["card"])
        self.geometry("380x320")
        self._build()
        if supplier:
            self._populate()

    def _build(self):
        frm = tk.Frame(self, bg=C["card"], padx=20, pady=16)
        frm.pack(fill="both", expand=True)
        self.name_var    = entry_row(frm, "Name *",     0, 0, width=26)
        self.contact_var = entry_row(frm, "Contact",    1, 0, width=26)
        self.phone_var   = entry_row(frm, "Phone",      2, 0, width=26)
        self.email_var   = entry_row(frm, "Email",      3, 0, width=26)
        self.address_var = entry_row(frm, "Address",    4, 0, width=26)
        row = tk.Frame(frm, bg=C["card"])
        row.grid(row=6, column=0, columnspan=2, pady=12)
        btn(row, "💾 Save", self._save, color=C["success"]).pack(side="left", padx=8)
        btn(row, "Cancel",  self.destroy, color=C["danger"]).pack(side="left")

    def _populate(self):
        s = self.supplier
        self.name_var.set(s["name"]); self.contact_var.set(s.get("contact",""))
        self.phone_var.set(s.get("phone","")); self.email_var.set(s.get("email",""))
        self.address_var.set(s.get("address",""))

    def _save(self):
        name = self.name_var.get().strip()
        if not name:
            messagebox.showerror("Error", "Name is required"); return
        if self.supplier:
            M.update_supplier(self.supplier["id"], name, self.contact_var.get(),
                              self.phone_var.get(), self.email_var.get(), self.address_var.get())
        else:
            M.add_supplier(name, self.contact_var.get(), self.phone_var.get(),
                           self.email_var.get(), self.address_var.get())
        self.parent_frame.refresh()
        self.destroy()


# ═══════════════════════════════════════════════════════════════
#  PURCHASES
# ═══════════════════════════════════════════════════════════════
class PurchaseFrame(tk.Frame):
    def __init__(self, parent, user):
        super().__init__(parent, bg=C["bg"])
        self.user  = user
        self.items = []
        self._build()
        self._load_orders()

    def _build(self):
        hdr = tk.Frame(self, bg=C["header"], pady=12, padx=20)
        hdr.pack(fill="x")
        tk.Label(hdr, text="🧾  Purchase Orders", font=FONT_H,
                 bg=C["header"], fg="white").pack(side="left")
        btn(hdr, "➕ New Purchase", self._new_purchase, color=C["success"]).pack(side="right")

        cols = ("PO#", "Date", "Supplier", "Total", "Paid", "Status")
        self.tree = make_tree(self, cols, heights=18)
        widths = [120, 120, 180, 90, 90, 80]
        for col, w in zip(cols, widths):
            self.tree.heading(col, text=col)
            self.tree.column(col, width=w)

    def _load_orders(self):
        for r in self.tree.get_children(): self.tree.delete(r)
        for p in M.get_purchases():
            self.tree.insert("", "end", values=(
                p["po_number"], p["purchase_date"][:16],
                p.get("supplier_name",""), format_currency(p["total_amount"]),
                format_currency(p["paid_amount"]), p["status"]))

    def _new_purchase(self):
        NewPurchaseDialog(self, self.user).grab_set()

    def refresh(self):
        self._load_orders()


class NewPurchaseDialog(tk.Toplevel):
    def __init__(self, parent_frame, user):
        super().__init__()
        self.parent_frame = parent_frame
        self.user  = user
        self.items = []
        self.title("New Purchase Order")
        self.configure(bg=C["bg"])
        self.geometry("720x580")
        self._build()

    def _build(self):
        top = tk.Frame(self, bg=C["card"], padx=16, pady=10)
        top.pack(fill="x")
        tk.Label(top, text=f"PO: {generate_po_number()}", font=FONT_B, bg=C["card"]).pack(side="left")
        sups = M.get_all_suppliers()
        sup_names = [s["name"] for s in sups]
        self._sups = sups
        tk.Label(top, text="Supplier:", font=FONT_B, bg=C["card"]).pack(side="left", padx=(16,4))
        self.sup_var = tk.StringVar()
        ttk.Combobox(top, textvariable=self.sup_var, values=sup_names, width=20, state="readonly").pack(side="left")

        # Product adder
        mid = tk.Frame(self, bg=C["card"], padx=16, pady=8)
        mid.pack(fill="x")
        tk.Label(mid, text="Product:", font=FONT, bg=C["card"]).pack(side="left")
        self.prod_var = tk.StringVar()
        prods = M.get_all_products()
        self._prods = prods
        prod_names = [p["name"] for p in prods]
        ttk.Combobox(mid, textvariable=self.prod_var, values=prod_names, width=22).pack(side="left", padx=4)
        tk.Label(mid, text="Qty:", font=FONT, bg=C["card"]).pack(side="left")
        self.qty_var = tk.StringVar(value="1")
        ttk.Entry(mid, textvariable=self.qty_var, width=6).pack(side="left", padx=4)
        tk.Label(mid, text="Cost:", font=FONT, bg=C["card"]).pack(side="left")
        self.cost_var = tk.StringVar()
        ttk.Entry(mid, textvariable=self.cost_var, width=8).pack(side="left", padx=4)
        btn(mid, "Add", self._add_item, color=C["accent"], width=6).pack(side="left")

        # Items table
        cols = ("Product", "Qty", "Unit Cost", "Total")
        self.tree = ttk.Treeview(self, columns=cols, show="headings", height=10)
        for col in cols:
            self.tree.heading(col, text=col); self.tree.column(col, width=160)
        self.tree.pack(fill="both", expand=True, padx=10, pady=4)
        self.tree.bind("<Delete>", self._remove_item)

        # Footer
        foot = tk.Frame(self, bg=C["card"], padx=16, pady=10)
        foot.pack(fill="x")
        self.total_lbl = tk.Label(foot, text="Total: ₹ 0.00", font=FONT_H, bg=C["card"], fg=C["success"])
        self.total_lbl.pack(side="left")
        tk.Label(foot, text="Paid:", font=FONT_B, bg=C["card"]).pack(side="left", padx=(20,4))
        self.paid_var = tk.StringVar(value="0")
        ttk.Entry(foot, textvariable=self.paid_var, width=12).pack(side="left")
        btn(foot, "✅ Save", self._save, color=C["success"]).pack(side="right", padx=4)
        btn(foot, "Cancel", self.destroy, color=C["danger"]).pack(side="right")

    def _add_item(self):
        prod_name = self.prod_var.get()
        prod = next((p for p in self._prods if p["name"]==prod_name), None)
        if not prod:
            messagebox.showerror("Error", "Select a valid product"); return
        try:
            qty  = float(self.qty_var.get())
            cost = float(self.cost_var.get() or prod["cost_price"])
        except ValueError:
            messagebox.showerror("Error", "Invalid qty/cost"); return
        self.items.append({"product_id": prod["id"], "name": prod_name,
                           "qty": qty, "cost": cost, "total": qty*cost})
        self._refresh()

    def _refresh(self):
        for r in self.tree.get_children(): self.tree.delete(r)
        total = 0
        for item in self.items:
            self.tree.insert("", "end", values=(item["name"], item["qty"],
                                                  f"{item['cost']:.2f}", f"{item['total']:.2f}"))
            total += item["total"]
        self.total_lbl.config(text=f"Total: ₹ {total:.2f}")

    def _remove_item(self, event=None):
        sel = self.tree.selection()
        if sel:
            idx = self.tree.index(sel[0])
            self.items.pop(idx)
            self._refresh()

    def _save(self):
        if not self.items:
            messagebox.showwarning("Empty", "Add items first"); return
        sup_name = self.sup_var.get()
        sup = next((s for s in self._sups if s["name"]==sup_name), None)
        if not sup:
            messagebox.showerror("Error", "Select a supplier"); return
        total = sum(i["total"] for i in self.items)
        try:
            paid = float(self.paid_var.get() or 0)
        except ValueError:
            paid = 0
        ok, result = M.save_purchase(generate_po_number(), sup["id"], self.user["id"],
                                     total, paid, self.items)
        if ok:
            self.parent_frame.refresh()
            messagebox.showinfo("Success", "Purchase order saved!")
            self.destroy()
        else:
            messagebox.showerror("Error", str(result))


# ═══════════════════════════════════════════════════════════════
#  EXPENSES
# ═══════════════════════════════════════════════════════════════
class ExpenseFrame(tk.Frame):
    def __init__(self, parent, user):
        super().__init__(parent, bg=C["bg"])
        self.user = user
        self._build()
        self._load()

    def _build(self):
        hdr = tk.Frame(self, bg=C["header"], pady=12, padx=20)
        hdr.pack(fill="x")
        tk.Label(hdr, text="💸  Expense Tracker", font=FONT_H,
                 bg=C["header"], fg="white").pack(side="left")

        # Add form
        form = card(self)
        form.pack(fill="x", padx=12, pady=10)
        inner = tk.Frame(form, bg=C["card"])
        inner.pack(padx=16, pady=10)
        tk.Label(inner, text="Category:", font=FONT, bg=C["card"]).grid(row=0, column=0, sticky="e", padx=4)
        cats = ["Rent","Utilities","Salaries","Transport","Maintenance",
                "Marketing","Packaging","Miscellaneous"]
        self.cat_var = tk.StringVar(value=cats[0])
        ttk.Combobox(inner, textvariable=self.cat_var, values=cats, width=16, state="readonly"
                     ).grid(row=0, column=1, padx=4)
        tk.Label(inner, text="Description:", font=FONT, bg=C["card"]).grid(row=0, column=2, sticky="e", padx=4)
        self.desc_var = tk.StringVar()
        ttk.Entry(inner, textvariable=self.desc_var, width=22).grid(row=0, column=3, padx=4)
        tk.Label(inner, text="Amount (₹):", font=FONT, bg=C["card"]).grid(row=0, column=4, sticky="e", padx=4)
        self.amt_var = tk.StringVar()
        ttk.Entry(inner, textvariable=self.amt_var, width=10).grid(row=0, column=5, padx=4)
        btn(inner, "➕ Add", self._add, color=C["success"], width=8).grid(row=0, column=6, padx=8)

        cols = ("Date", "Category", "Description", "Amount", "Added By")
        self.tree = make_tree(self, cols, heights=18)
        widths = [110, 110, 240, 90, 140]
        for col, w in zip(cols, widths):
            self.tree.heading(col, text=col)
            self.tree.column(col, width=w)

        bar = tk.Frame(self, bg=C["bg"], pady=6, padx=12)
        bar.pack(fill="x")
        self.total_lbl = tk.Label(bar, text="", font=FONT_B, bg=C["bg"], fg=C["danger"])
        self.total_lbl.pack(side="right")
        btn(bar, "📤 Export", self._export, color=C["header"]).pack(side="left")

    def _load(self):
        for r in self.tree.get_children(): self.tree.delete(r)
        rows = M.get_expenses()
        total = 0
        for e in rows:
            self.tree.insert("", "end", values=(
                e["exp_date"][:16], e["category"], e.get("description",""),
                format_currency(e["amount"]), e.get("user_name","")))
            total += e["amount"]
        self.total_lbl.config(text=f"Total Expenses: {format_currency(total)}")

    def _add(self):
        ok, amt = validate_number(self.amt_var.get())
        if not ok:
            messagebox.showerror("Error", amt); return
        M.add_expense(self.cat_var.get(), self.desc_var.get(),
                      amt, self.user["id"])
        self.amt_var.set(""); self.desc_var.set("")
        self._load()

    def _export(self):
        rows = M.get_expenses()
        path = export_to_csv(rows, f"expenses_{datetime.now().strftime('%Y%m%d')}.csv")
        messagebox.showinfo("Exported", f"Saved to:\n{path}")


# ═══════════════════════════════════════════════════════════════
#  REPORTS
# ═══════════════════════════════════════════════════════════════
class ReportsFrame(tk.Frame):
    def __init__(self, parent, user):
        super().__init__(parent, bg=C["bg"])
        self.user = user
        self._build()

    def _build(self):
        hdr = tk.Frame(self, bg=C["header"], pady=12, padx=20)
        hdr.pack(fill="x")
        tk.Label(hdr, text="📈  Reports & Analytics", font=FONT_H,
                 bg=C["header"], fg="white").pack(side="left")

        # Date filter
        flt = tk.Frame(self, bg=C["bg"], pady=8, padx=12)
        flt.pack(fill="x")
        tk.Label(flt, text="From:", font=FONT, bg=C["bg"]).pack(side="left")
        self.from_var = tk.StringVar(value=datetime.now().strftime("%Y-%m-01"))
        ttk.Entry(flt, textvariable=self.from_var, width=12).pack(side="left", padx=4)
        tk.Label(flt, text="To:", font=FONT, bg=C["bg"]).pack(side="left")
        self.to_var   = tk.StringVar(value=datetime.now().strftime("%Y-%m-%d"))
        ttk.Entry(flt, textvariable=self.to_var, width=12).pack(side="left", padx=4)

        report_types = [
            ("Sales Summary",      self._sales_summary),
            ("Top Products",       self._top_products),
            ("Category Analysis",  self._category_report),
            ("Purchase Report",    self._purchase_report),
            ("Expense Report",     self._expense_report),
            ("Inventory Report",   self._inventory_report),
        ]
        for label, cmd in report_types:
            btn(flt, label, cmd, color=C["accent"], width=14).pack(side="left", padx=3)

        btn(flt, "📤 Export", self._export_current, color=C["header"], width=10).pack(side="right")

        # Results
        results = tk.Frame(self, bg=C["bg"])
        results.pack(fill="both", expand=True, padx=12, pady=6)

        self.report_title = tk.Label(results, text="Select a report above",
                                     font=FONT_H, bg=C["bg"], fg=C["header"])
        self.report_title.pack(pady=8)

        self.tree_frame = tk.Frame(results, bg=C["bg"])
        self.tree_frame.pack(fill="both", expand=True)
        self.current_tree = None
        self.current_data = []

    def _clear(self, title):
        for w in self.tree_frame.winfo_children():
            w.destroy()
        self.report_title.config(text=title)
        self.current_data = []

    def _make_tree(self, cols, widths):
        vsb = ttk.Scrollbar(self.tree_frame)
        vsb.pack(side="right", fill="y")
        tree = ttk.Treeview(self.tree_frame, columns=cols, show="headings",
                             height=18, yscrollcommand=vsb.set)
        vsb.config(command=tree.yview)
        for col, w in zip(cols, widths):
            tree.heading(col, text=col)
            tree.column(col, width=w)
        tree.pack(fill="both", expand=True)
        self.current_tree = tree
        return tree

    def _sales_summary(self):
        self._clear("📊 Sales Summary")
        sales = M.get_sales(self.from_var.get(), self.to_var.get())
        cols = ("Invoice", "Date", "Customer", "Subtotal", "Discount", "Tax", "Total", "Method", "Cashier")
        widths = [110, 120, 120, 80, 70, 60, 80, 70, 110]
        tree = self._make_tree(cols, widths)
        total_sum = 0
        for s in sales:
            tree.insert("", "end", values=(
                s["invoice_no"], s["sale_date"][:16], s.get("customer_name",""),
                f"{s['subtotal']:.2f}", f"{s['discount']:.2f}", f"{s['tax']:.2f}",
                f"{s['total']:.2f}", s["payment_method"], s.get("cashier","")))
            total_sum += s["total"]
        tree.insert("", "end", values=("─"*8, "", "TOTAL", "", "", "", f"{total_sum:.2f}", "", ""),
                    tags=("total",))
        tree.tag_configure("total", background=C["header"], foreground="white", font=FONT_B)
        self.current_data = sales

    def _top_products(self):
        self._clear("🏆 Top Products")
        rows = M.get_top_products(20)
        cols = ("Rank", "Product", "Qty Sold", "Revenue")
        tree = self._make_tree(cols, [50, 280, 100, 120])
        for i, r in enumerate(rows, 1):
            tree.insert("", "end", values=(i, r["name"],
                                           f"{r['sold_qty']:.1f}",
                                           format_currency(r["revenue"])))
        self.current_data = rows

    def _category_report(self):
        self._clear("🗂️ Sales by Category")
        rows = M.get_category_sales()
        cols = ("Category", "Total Revenue")
        tree = self._make_tree(cols, [280, 160])
        total = sum(r["total"] for r in rows)
        for r in rows:
            pct = r["total"] / total * 100 if total else 0
            tree.insert("", "end", values=(r["name"],
                                           f"{format_currency(r['total'])} ({pct:.1f}%)"))
        self.current_data = rows

    def _purchase_report(self):
        self._clear("🧾 Purchase Report")
        rows = M.get_purchases(self.from_var.get(), self.to_var.get())
        cols = ("PO#", "Date", "Supplier", "Total", "Paid", "Balance", "Status")
        tree = self._make_tree(cols, [110, 120, 160, 90, 90, 90, 80])
        for r in rows:
            balance = r["total_amount"] - r["paid_amount"]
            tree.insert("", "end", values=(
                r["po_number"], r["purchase_date"][:16], r.get("supplier_name",""),
                format_currency(r["total_amount"]), format_currency(r["paid_amount"]),
                format_currency(balance), r["status"]))
        self.current_data = rows

    def _expense_report(self):
        self._clear("💸 Expense Report")
        rows = M.get_expenses(self.from_var.get(), self.to_var.get())
        cols = ("Date", "Category", "Description", "Amount", "Added By")
        tree = self._make_tree(cols, [110, 110, 240, 90, 130])
        total = 0
        for r in rows:
            tree.insert("", "end", values=(
                r["exp_date"][:16], r["category"],
                r.get("description",""), format_currency(r["amount"]),
                r.get("user_name","")))
            total += r["amount"]
        tree.insert("", "end", values=("", "TOTAL", "", format_currency(total), ""),
                    tags=("total",))
        tree.tag_configure("total", background=C["danger"], foreground="white", font=FONT_B)
        self.current_data = rows

    def _inventory_report(self):
        self._clear("📦 Inventory Valuation Report")
        prods = M.get_all_products()
        cols = ("Name", "Category", "Stock", "Unit", "Cost", "Sale Price", "Stock Value")
        tree = self._make_tree(cols, [200, 100, 70, 50, 70, 80, 100])
        total_val = 0
        for p in prods:
            val = p["stock_qty"] * p["selling_price"]
            total_val += val
            tree.insert("", "end", values=(
                p["name"], p.get("category_name",""),
                f"{p['stock_qty']:.2f}", p["unit"],
                f"{p['cost_price']:.2f}", f"{p['selling_price']:.2f}",
                format_currency(val)))
        tree.insert("", "end", values=("", "", "", "", "", "TOTAL VALUE",
                                       format_currency(total_val)), tags=("total",))
        tree.tag_configure("total", background=C["success"], foreground="white", font=FONT_B)
        self.current_data = prods

    def _export_current(self):
        if not self.current_data:
            messagebox.showinfo("No Data", "Run a report first"); return
        path = export_to_csv(self.current_data,
                             f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv")
        messagebox.showinfo("Exported", f"Saved to:\n{path}")


# ═══════════════════════════════════════════════════════════════
#  USER MANAGEMENT (admin only)
# ═══════════════════════════════════════════════════════════════
class UserFrame(tk.Frame):
    def __init__(self, parent, user):
        super().__init__(parent, bg=C["bg"])
        self.user = user
        self._build()
        self._load()

    def _build(self):
        hdr = tk.Frame(self, bg=C["header"], pady=12, padx=20)
        hdr.pack(fill="x")
        tk.Label(hdr, text="⚙️  User Management", font=FONT_H,
                 bg=C["header"], fg="white").pack(side="left")
        btn(hdr, "➕ Add User", self._add, color=C["success"]).pack(side="right")

        cols = ("ID", "Username", "Full Name", "Role", "Email", "Phone", "Active", "Created")
        self.tree = make_tree(self, cols, heights=18)
        widths = [40, 110, 160, 80, 160, 110, 50, 100]
        for col, w in zip(cols, widths):
            self.tree.heading(col, text=col)
            self.tree.column(col, width=w)
        self.tree.bind("<Double-1>", self._edit)

        bar = tk.Frame(self, bg=C["bg"], pady=6, padx=12)
        bar.pack(fill="x")
        btn(bar, "✏️ Edit",           self._edit,          color=C["accent"]).pack(side="left", padx=2)
        btn(bar, "🔑 Reset Password", self._reset_password, color=C["warning"]).pack(side="left", padx=2)

    def _load(self):
        for r in self.tree.get_children(): self.tree.delete(r)
        for u in M.get_all_users():
            self.tree.insert("", "end", values=(
                u["id"], u["username"], u["full_name"], u["role"],
                u.get("email",""), u.get("phone",""),
                "✅" if u["active"] else "❌", u["created_at"][:10]))

    def _add(self):
        UserDialog(self, None).grab_set()

    def _edit(self, event=None):
        sel = self.tree.selection()
        if not sel: return
        uid = self.tree.item(sel[0])["values"][0]
        users = M.get_all_users()
        user = next((u for u in users if u["id"]==uid), None)
        if user:
            UserDialog(self, user).grab_set()

    def _reset_password(self):
        sel = self.tree.selection()
        if not sel: return
        uid  = self.tree.item(sel[0])["values"][0]
        name = self.tree.item(sel[0])["values"][2]
        new_pass = simpledialog.askstring("Reset Password",
                                          f"New password for {name}:", show="●")
        if new_pass:
            M.change_password(uid, new_pass)
            messagebox.showinfo("Done", "Password updated!")

    def refresh(self):
        self._load()


class UserDialog(tk.Toplevel):
    def __init__(self, parent_frame, user):
        super().__init__()
        self.parent_frame = parent_frame
        self.user = user
        self.title("Edit User" if user else "Add User")
        self.configure(bg=C["card"])
        self.geometry("380x380")
        self._build()
        if user:
            self._populate()

    def _build(self):
        frm = tk.Frame(self, bg=C["card"], padx=20, pady=16)
        frm.pack(fill="both", expand=True)
        self.username_var  = entry_row(frm, "Username *",  0, 0, width=24)
        self.fullname_var  = entry_row(frm, "Full Name *", 1, 0, width=24)
        self.email_var     = entry_row(frm, "Email",       2, 0, width=24)
        self.phone_var     = entry_row(frm, "Phone",       3, 0, width=24)
        roles = ["admin", "manager", "cashier", "storekeeper"]
        self.role_var, _   = combo_row(frm, "Role",        4, roles)
        self.active_var    = tk.BooleanVar(value=True)
        tk.Checkbutton(frm, text="Active", variable=self.active_var,
                       bg=C["card"], font=FONT).grid(row=5, column=1, sticky="w", pady=4)
        if not self.user:
            self.pass_var = entry_row(frm, "Password *", 6, 0, width=24, show="●")
        row = tk.Frame(frm, bg=C["card"])
        row.grid(row=8, column=0, columnspan=2, pady=12)
        btn(row, "💾 Save", self._save, color=C["success"]).pack(side="left", padx=8)
        btn(row, "Cancel",  self.destroy, color=C["danger"]).pack(side="left")

    def _populate(self):
        u = self.user
        self.username_var.set(u["username"]); self.fullname_var.set(u["full_name"])
        self.email_var.set(u.get("email","")); self.phone_var.set(u.get("phone",""))
        self.role_var.set(u["role"]); self.active_var.set(bool(u["active"]))

    def _save(self):
        full_name = self.fullname_var.get().strip()
        username  = self.username_var.get().strip()
        if not full_name or not username:
            messagebox.showerror("Error", "Username and Full Name are required"); return
        if self.user:
            M.update_user(self.user["id"], full_name, self.role_var.get(),
                          self.email_var.get(), self.phone_var.get(),
                          1 if self.active_var.get() else 0)
        else:
            password = self.pass_var.get()
            if not password:
                messagebox.showerror("Error", "Password required"); return
            ok, msg = M.add_user(username, password, full_name, self.role_var.get(),
                                  self.email_var.get(), self.phone_var.get())
            if not ok:
                messagebox.showerror("Error", msg); return
        self.parent_frame.refresh()
        self.destroy()


# ═══════════════════════════════════════════════════════════════
#  ENTRY POINT
# ═══════════════════════════════════════════════════════════════
def main():
    init_db()
    login_win = LoginWindow()
    login_win.mainloop()
    if login_win.user:
        app = App(login_win.user)
        app.mainloop()

if __name__ == "__main__":
    main()
