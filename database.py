"""
database.py - SQLite database layer for Variety Store Management System
Handles all DB init, migrations, and connection management
"""

import sqlite3
import os
import hashlib
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), "data", "variety_store.db")

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

def init_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = get_connection()
    c = conn.cursor()

    # ── Users & Roles ──────────────────────────────────────────────
    c.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id          INTEGER PRIMARY KEY AUTOINCREMENT,
        username    TEXT UNIQUE NOT NULL,
        password    TEXT NOT NULL,
        full_name   TEXT NOT NULL,
        role        TEXT NOT NULL DEFAULT 'cashier',
        email       TEXT,
        phone       TEXT,
        active      INTEGER DEFAULT 1,
        created_at  TEXT DEFAULT (datetime('now'))
    )""")

    # ── Store branches ─────────────────────────────────────────────
    c.execute("""
    CREATE TABLE IF NOT EXISTS branches (
        id          INTEGER PRIMARY KEY AUTOINCREMENT,
        name        TEXT NOT NULL,
        address     TEXT,
        phone       TEXT,
        manager     TEXT,
        active      INTEGER DEFAULT 1
    )""")

    # ── Suppliers ──────────────────────────────────────────────────
    c.execute("""
    CREATE TABLE IF NOT EXISTS suppliers (
        id          INTEGER PRIMARY KEY AUTOINCREMENT,
        name        TEXT NOT NULL,
        contact     TEXT,
        phone       TEXT,
        email       TEXT,
        address     TEXT,
        balance     REAL DEFAULT 0.0,
        created_at  TEXT DEFAULT (datetime('now'))
    )""")

    # ── Categories ─────────────────────────────────────────────────
    c.execute("""
    CREATE TABLE IF NOT EXISTS categories (
        id          INTEGER PRIMARY KEY AUTOINCREMENT,
        name        TEXT UNIQUE NOT NULL,
        description TEXT
    )""")

    # ── Products ───────────────────────────────────────────────────
    c.execute("""
    CREATE TABLE IF NOT EXISTS products (
        id              INTEGER PRIMARY KEY AUTOINCREMENT,
        barcode         TEXT UNIQUE,
        name            TEXT NOT NULL,
        description     TEXT,
        category_id     INTEGER REFERENCES categories(id),
        supplier_id     INTEGER REFERENCES suppliers(id),
        unit            TEXT DEFAULT 'pcs',
        cost_price      REAL DEFAULT 0.0,
        selling_price   REAL NOT NULL,
        stock_qty       REAL DEFAULT 0.0,
        min_stock       REAL DEFAULT 5.0,
        max_stock       REAL DEFAULT 1000.0,
        branch_id       INTEGER REFERENCES branches(id),
        active          INTEGER DEFAULT 1,
        created_at      TEXT DEFAULT (datetime('now')),
        updated_at      TEXT DEFAULT (datetime('now'))
    )""")

    # ── Customers ──────────────────────────────────────────────────
    c.execute("""
    CREATE TABLE IF NOT EXISTS customers (
        id          INTEGER PRIMARY KEY AUTOINCREMENT,
        name        TEXT NOT NULL,
        phone       TEXT,
        email       TEXT,
        address     TEXT,
        points      REAL DEFAULT 0.0,
        total_spent REAL DEFAULT 0.0,
        created_at  TEXT DEFAULT (datetime('now'))
    )""")

    # ── Sales / Invoices ───────────────────────────────────────────
    c.execute("""
    CREATE TABLE IF NOT EXISTS sales (
        id              INTEGER PRIMARY KEY AUTOINCREMENT,
        invoice_no      TEXT UNIQUE NOT NULL,
        customer_id     INTEGER REFERENCES customers(id),
        user_id         INTEGER REFERENCES users(id),
        branch_id       INTEGER REFERENCES branches(id),
        subtotal        REAL DEFAULT 0.0,
        discount        REAL DEFAULT 0.0,
        tax             REAL DEFAULT 0.0,
        total           REAL DEFAULT 0.0,
        paid_amount     REAL DEFAULT 0.0,
        change_amount   REAL DEFAULT 0.0,
        payment_method  TEXT DEFAULT 'cash',
        status          TEXT DEFAULT 'completed',
        notes           TEXT,
        sale_date       TEXT DEFAULT (datetime('now'))
    )""")

    # ── Sale Items ─────────────────────────────────────────────────
    c.execute("""
    CREATE TABLE IF NOT EXISTS sale_items (
        id          INTEGER PRIMARY KEY AUTOINCREMENT,
        sale_id     INTEGER REFERENCES sales(id) ON DELETE CASCADE,
        product_id  INTEGER REFERENCES products(id),
        quantity    REAL NOT NULL,
        unit_price  REAL NOT NULL,
        discount    REAL DEFAULT 0.0,
        total       REAL NOT NULL
    )""")

    # ── Purchase Orders ────────────────────────────────────────────
    c.execute("""
    CREATE TABLE IF NOT EXISTS purchases (
        id              INTEGER PRIMARY KEY AUTOINCREMENT,
        po_number       TEXT UNIQUE NOT NULL,
        supplier_id     INTEGER REFERENCES suppliers(id),
        user_id         INTEGER REFERENCES users(id),
        total_amount    REAL DEFAULT 0.0,
        paid_amount     REAL DEFAULT 0.0,
        status          TEXT DEFAULT 'received',
        notes           TEXT,
        purchase_date   TEXT DEFAULT (datetime('now'))
    )""")

    c.execute("""
    CREATE TABLE IF NOT EXISTS purchase_items (
        id          INTEGER PRIMARY KEY AUTOINCREMENT,
        purchase_id INTEGER REFERENCES purchases(id) ON DELETE CASCADE,
        product_id  INTEGER REFERENCES products(id),
        quantity    REAL NOT NULL,
        unit_cost   REAL NOT NULL,
        total       REAL NOT NULL
    )""")

    # ── Stock Adjustments ──────────────────────────────────────────
    c.execute("""
    CREATE TABLE IF NOT EXISTS stock_adjustments (
        id          INTEGER PRIMARY KEY AUTOINCREMENT,
        product_id  INTEGER REFERENCES products(id),
        user_id     INTEGER REFERENCES users(id),
        adj_type    TEXT NOT NULL,
        quantity    REAL NOT NULL,
        reason      TEXT,
        adj_date    TEXT DEFAULT (datetime('now'))
    )""")

    # ── Expenses ───────────────────────────────────────────────────
    c.execute("""
    CREATE TABLE IF NOT EXISTS expenses (
        id          INTEGER PRIMARY KEY AUTOINCREMENT,
        category    TEXT NOT NULL,
        description TEXT,
        amount      REAL NOT NULL,
        user_id     INTEGER REFERENCES users(id),
        branch_id   INTEGER REFERENCES branches(id),
        exp_date    TEXT DEFAULT (datetime('now'))
    )""")

    conn.commit()
    _seed_defaults(c, conn)
    conn.close()

def _seed_defaults(c, conn):
    # Default admin user
    c.execute("SELECT id FROM users WHERE username='admin'")
    if not c.fetchone():
        c.execute("""INSERT INTO users (username,password,full_name,role)
                     VALUES (?,?,?,?)""",
                  ("admin", hash_password("admin123"), "System Administrator", "admin"))

    # Default branch
    c.execute("SELECT id FROM branches")
    if not c.fetchone():
        c.execute("INSERT INTO branches (name,address) VALUES (?,?)",
                  ("Main Branch", "Store Address"))

    # Default categories
    default_cats = [
        "Groceries", "Beverages", "Snacks", "Dairy", "Bakery",
        "Household", "Personal Care", "Electronics", "Clothing",
        "Stationery", "Toys", "Medicines", "Vegetables", "Fruits", "Other"
    ]
    for cat in default_cats:
        c.execute("INSERT OR IGNORE INTO categories (name) VALUES (?)", (cat,))

    # Default walk-in customer
    c.execute("SELECT id FROM customers WHERE name='Walk-in Customer'")
    if not c.fetchone():
        c.execute("INSERT INTO customers (name,phone) VALUES (?,?)",
                  ("Walk-in Customer", "0000000000"))

    conn.commit()

def generate_invoice_no():
    conn = get_connection()
    c = conn.cursor()
    today = datetime.now().strftime("%Y%m%d")
    c.execute("SELECT COUNT(*) FROM sales WHERE invoice_no LIKE ?", (f"INV{today}%",))
    count = c.fetchone()[0] + 1
    conn.close()
    return f"INV{today}{count:04d}"

def generate_po_number():
    conn = get_connection()
    c = conn.cursor()
    today = datetime.now().strftime("%Y%m%d")
    c.execute("SELECT COUNT(*) FROM purchases WHERE po_number LIKE ?", (f"PO{today}%",))
    count = c.fetchone()[0] + 1
    conn.close()
    return f"PO{today}{count:04d}"
