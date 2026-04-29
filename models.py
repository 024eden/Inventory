"""
models.py - All data-access functions for the Variety Store System
"""

from database import get_connection, hash_password
from datetime import datetime


# ═══════════════════════════════════════════════════════════════
#  AUTH
# ═══════════════════════════════════════════════════════════════
def login(username, password):
    conn = get_connection()
    c = conn.cursor()
    c.execute("""SELECT * FROM users WHERE username=? AND password=? AND active=1""",
              (username, hash_password(password)))
    user = c.fetchone()
    conn.close()
    return dict(user) if user else None

def get_all_users():
    conn = get_connection()
    rows = conn.execute("SELECT * FROM users ORDER BY full_name").fetchall()
    conn.close()
    return [dict(r) for r in rows]

def add_user(username, password, full_name, role, email="", phone=""):
    conn = get_connection()
    try:
        conn.execute("""INSERT INTO users (username,password,full_name,role,email,phone)
                        VALUES (?,?,?,?,?,?)""",
                     (username, hash_password(password), full_name, role, email, phone))
        conn.commit()
        return True, "User added successfully"
    except Exception as e:
        return False, str(e)
    finally:
        conn.close()

def update_user(user_id, full_name, role, email, phone, active):
    conn = get_connection()
    conn.execute("""UPDATE users SET full_name=?,role=?,email=?,phone=?,active=?
                    WHERE id=?""", (full_name, role, email, phone, active, user_id))
    conn.commit()
    conn.close()

def change_password(user_id, new_password):
    conn = get_connection()
    conn.execute("UPDATE users SET password=? WHERE id=?",
                 (hash_password(new_password), user_id))
    conn.commit()
    conn.close()


# ═══════════════════════════════════════════════════════════════
#  CATEGORIES
# ═══════════════════════════════════════════════════════════════
def get_categories():
    conn = get_connection()
    rows = conn.execute("SELECT * FROM categories ORDER BY name").fetchall()
    conn.close()
    return [dict(r) for r in rows]

def add_category(name, description=""):
    conn = get_connection()
    try:
        conn.execute("INSERT INTO categories (name,description) VALUES (?,?)", (name, description))
        conn.commit()
        return True, "Category added"
    except Exception as e:
        return False, str(e)
    finally:
        conn.close()


# ═══════════════════════════════════════════════════════════════
#  SUPPLIERS
# ═══════════════════════════════════════════════════════════════
def get_all_suppliers():
    conn = get_connection()
    rows = conn.execute("SELECT * FROM suppliers ORDER BY name").fetchall()
    conn.close()
    return [dict(r) for r in rows]

def add_supplier(name, contact, phone, email, address):
    conn = get_connection()
    try:
        conn.execute("""INSERT INTO suppliers (name,contact,phone,email,address)
                        VALUES (?,?,?,?,?)""", (name, contact, phone, email, address))
        conn.commit()
        return True, "Supplier added"
    except Exception as e:
        return False, str(e)
    finally:
        conn.close()

def update_supplier(sup_id, name, contact, phone, email, address):
    conn = get_connection()
    conn.execute("""UPDATE suppliers SET name=?,contact=?,phone=?,email=?,address=?
                    WHERE id=?""", (name, contact, phone, email, address, sup_id))
    conn.commit()
    conn.close()


# ═══════════════════════════════════════════════════════════════
#  PRODUCTS / INVENTORY
# ═══════════════════════════════════════════════════════════════
def get_all_products(search="", category_id=None, low_stock=False):
    conn = get_connection()
    sql = """SELECT p.*, c.name as category_name, s.name as supplier_name
             FROM products p
             LEFT JOIN categories c ON p.category_id=c.id
             LEFT JOIN suppliers s  ON p.supplier_id=s.id
             WHERE p.active=1"""
    params = []
    if search:
        sql += " AND (p.name LIKE ? OR p.barcode LIKE ?)"
        params += [f"%{search}%", f"%{search}%"]
    if category_id:
        sql += " AND p.category_id=?"
        params.append(category_id)
    if low_stock:
        sql += " AND p.stock_qty <= p.min_stock"
    sql += " ORDER BY p.name"
    rows = conn.execute(sql, params).fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_product_by_barcode(barcode):
    conn = get_connection()
    row = conn.execute("""SELECT p.*, c.name as category_name
                          FROM products p LEFT JOIN categories c ON p.category_id=c.id
                          WHERE p.barcode=? AND p.active=1""", (barcode,)).fetchone()
    conn.close()
    return dict(row) if row else None

def get_product_by_id(pid):
    conn = get_connection()
    row = conn.execute("SELECT * FROM products WHERE id=?", (pid,)).fetchone()
    conn.close()
    return dict(row) if row else None

def add_product(barcode, name, description, category_id, supplier_id,
                unit, cost_price, selling_price, stock_qty, min_stock, max_stock):
    conn = get_connection()
    try:
        conn.execute("""INSERT INTO products
                        (barcode,name,description,category_id,supplier_id,unit,
                         cost_price,selling_price,stock_qty,min_stock,max_stock)
                        VALUES (?,?,?,?,?,?,?,?,?,?,?)""",
                     (barcode, name, description, category_id, supplier_id, unit,
                      cost_price, selling_price, stock_qty, min_stock, max_stock))
        conn.commit()
        return True, "Product added successfully"
    except Exception as e:
        return False, str(e)
    finally:
        conn.close()

def update_product(pid, barcode, name, description, category_id, supplier_id,
                   unit, cost_price, selling_price, min_stock, max_stock):
    conn = get_connection()
    conn.execute("""UPDATE products SET barcode=?,name=?,description=?,category_id=?,
                    supplier_id=?,unit=?,cost_price=?,selling_price=?,
                    min_stock=?,max_stock=?,updated_at=datetime('now')
                    WHERE id=?""",
                 (barcode, name, description, category_id, supplier_id, unit,
                  cost_price, selling_price, min_stock, max_stock, pid))
    conn.commit()
    conn.close()

def update_stock(product_id, qty_change, conn_ext=None):
    """Add qty_change to product stock (negative = reduce)"""
    own = conn_ext is None
    conn = get_connection() if own else conn_ext
    conn.execute("UPDATE products SET stock_qty=stock_qty+?, updated_at=datetime('now') WHERE id=?",
                 (qty_change, product_id))
    if own:
        conn.commit()
        conn.close()

def delete_product(pid):
    conn = get_connection()
    conn.execute("UPDATE products SET active=0 WHERE id=?", (pid,))
    conn.commit()
    conn.close()

def adjust_stock(product_id, user_id, adj_type, quantity, reason):
    conn = get_connection()
    delta = quantity if adj_type == "add" else -quantity
    conn.execute("UPDATE products SET stock_qty=stock_qty+? WHERE id=?", (delta, product_id))
    conn.execute("""INSERT INTO stock_adjustments (product_id,user_id,adj_type,quantity,reason)
                    VALUES (?,?,?,?,?)""", (product_id, user_id, adj_type, quantity, reason))
    conn.commit()
    conn.close()


# ═══════════════════════════════════════════════════════════════
#  CUSTOMERS
# ═══════════════════════════════════════════════════════════════
def get_all_customers(search=""):
    conn = get_connection()
    sql = "SELECT * FROM customers WHERE 1=1"
    params = []
    if search:
        sql += " AND (name LIKE ? OR phone LIKE ?)"
        params += [f"%{search}%", f"%{search}%"]
    sql += " ORDER BY name"
    rows = conn.execute(sql, params).fetchall()
    conn.close()
    return [dict(r) for r in rows]

def add_customer(name, phone, email, address):
    conn = get_connection()
    try:
        conn.execute("INSERT INTO customers (name,phone,email,address) VALUES (?,?,?,?)",
                     (name, phone, email, address))
        conn.commit()
        return True, "Customer added"
    except Exception as e:
        return False, str(e)
    finally:
        conn.close()

def update_customer(cid, name, phone, email, address):
    conn = get_connection()
    conn.execute("UPDATE customers SET name=?,phone=?,email=?,address=? WHERE id=?",
                 (name, phone, email, address, cid))
    conn.commit()
    conn.close()


# ═══════════════════════════════════════════════════════════════
#  SALES / POS
# ═══════════════════════════════════════════════════════════════
def save_sale(invoice_no, customer_id, user_id, branch_id,
              subtotal, discount, tax, total, paid, change, method, items, notes=""):
    conn = get_connection()
    try:
        conn.execute("""INSERT INTO sales
                        (invoice_no,customer_id,user_id,branch_id,subtotal,discount,
                         tax,total,paid_amount,change_amount,payment_method,notes)
                        VALUES (?,?,?,?,?,?,?,?,?,?,?,?)""",
                     (invoice_no, customer_id, user_id, branch_id, subtotal, discount,
                      tax, total, paid, change, method, notes))
        sale_id = conn.execute("SELECT last_insert_rowid()").fetchone()[0]
        for item in items:
            conn.execute("""INSERT INTO sale_items (sale_id,product_id,quantity,unit_price,discount,total)
                            VALUES (?,?,?,?,?,?)""",
                         (sale_id, item["product_id"], item["qty"], item["price"],
                          item.get("discount", 0), item["total"]))
            update_stock(item["product_id"], -item["qty"], conn)
        # Update customer stats
        if customer_id:
            conn.execute("UPDATE customers SET total_spent=total_spent+?, points=points+? WHERE id=?",
                         (total, int(total / 100), customer_id))
        conn.commit()
        return True, sale_id
    except Exception as e:
        conn.rollback()
        return False, str(e)
    finally:
        conn.close()

def get_sales(date_from=None, date_to=None, search="", limit=200):
    conn = get_connection()
    sql = """SELECT s.*, u.full_name as cashier, c.name as customer_name
             FROM sales s
             LEFT JOIN users u ON s.user_id=u.id
             LEFT JOIN customers c ON s.customer_id=c.id
             WHERE 1=1"""
    params = []
    if date_from:
        sql += " AND date(s.sale_date)>=?"
        params.append(date_from)
    if date_to:
        sql += " AND date(s.sale_date)<=?"
        params.append(date_to)
    if search:
        sql += " AND s.invoice_no LIKE ?"
        params.append(f"%{search}%")
    sql += " ORDER BY s.sale_date DESC LIMIT ?"
    params.append(limit)
    rows = conn.execute(sql, params).fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_sale_items(sale_id):
    conn = get_connection()
    rows = conn.execute("""SELECT si.*, p.name as product_name, p.unit
                           FROM sale_items si LEFT JOIN products p ON si.product_id=p.id
                           WHERE si.sale_id=?""", (sale_id,)).fetchall()
    conn.close()
    return [dict(r) for r in rows]


# ═══════════════════════════════════════════════════════════════
#  PURCHASES
# ═══════════════════════════════════════════════════════════════
def save_purchase(po_number, supplier_id, user_id, total, paid, items, notes=""):
    conn = get_connection()
    try:
        conn.execute("""INSERT INTO purchases (po_number,supplier_id,user_id,total_amount,paid_amount,notes)
                        VALUES (?,?,?,?,?,?)""",
                     (po_number, supplier_id, user_id, total, paid, notes))
        po_id = conn.execute("SELECT last_insert_rowid()").fetchone()[0]
        for item in items:
            conn.execute("""INSERT INTO purchase_items (purchase_id,product_id,quantity,unit_cost,total)
                            VALUES (?,?,?,?,?)""",
                         (po_id, item["product_id"], item["qty"], item["cost"], item["total"]))
            update_stock(item["product_id"], item["qty"], conn)
        conn.commit()
        return True, po_id
    except Exception as e:
        conn.rollback()
        return False, str(e)
    finally:
        conn.close()

def get_purchases(date_from=None, date_to=None):
    conn = get_connection()
    sql = """SELECT p.*, s.name as supplier_name, u.full_name as user_name
             FROM purchases p
             LEFT JOIN suppliers s ON p.supplier_id=s.id
             LEFT JOIN users u ON p.user_id=u.id WHERE 1=1"""
    params = []
    if date_from:
        sql += " AND date(p.purchase_date)>=?"
        params.append(date_from)
    if date_to:
        sql += " AND date(p.purchase_date)<=?"
        params.append(date_to)
    sql += " ORDER BY p.purchase_date DESC"
    rows = conn.execute(sql, params).fetchall()
    conn.close()
    return [dict(r) for r in rows]


# ═══════════════════════════════════════════════════════════════
#  EXPENSES
# ═══════════════════════════════════════════════════════════════
def add_expense(category, description, amount, user_id, branch_id=1):
    conn = get_connection()
    conn.execute("""INSERT INTO expenses (category,description,amount,user_id,branch_id)
                    VALUES (?,?,?,?,?)""", (category, description, amount, user_id, branch_id))
    conn.commit()
    conn.close()

def get_expenses(date_from=None, date_to=None):
    conn = get_connection()
    sql = "SELECT e.*, u.full_name as user_name FROM expenses e LEFT JOIN users u ON e.user_id=u.id WHERE 1=1"
    params = []
    if date_from:
        sql += " AND date(e.exp_date)>=?"
        params.append(date_from)
    if date_to:
        sql += " AND date(e.exp_date)<=?"
        params.append(date_to)
    sql += " ORDER BY e.exp_date DESC"
    rows = conn.execute(sql, params).fetchall()
    conn.close()
    return [dict(r) for r in rows]


# ═══════════════════════════════════════════════════════════════
#  REPORTS / DASHBOARD
# ═══════════════════════════════════════════════════════════════
def get_dashboard_stats():
    conn = get_connection()
    today = datetime.now().strftime("%Y-%m-%d")
    stats = {}
    stats["today_sales"] = conn.execute(
        "SELECT COALESCE(SUM(total),0) FROM sales WHERE date(sale_date)=?", (today,)).fetchone()[0]
    stats["today_invoices"] = conn.execute(
        "SELECT COUNT(*) FROM sales WHERE date(sale_date)=?", (today,)).fetchone()[0]
    stats["total_products"] = conn.execute("SELECT COUNT(*) FROM products WHERE active=1").fetchone()[0]
    stats["low_stock_count"] = conn.execute(
        "SELECT COUNT(*) FROM products WHERE active=1 AND stock_qty<=min_stock").fetchone()[0]
    stats["total_customers"] = conn.execute("SELECT COUNT(*) FROM customers").fetchone()[0]
    stats["month_sales"] = conn.execute(
        "SELECT COALESCE(SUM(total),0) FROM sales WHERE strftime('%Y-%m',sale_date)=strftime('%Y-%m','now')"
    ).fetchone()[0]
    stats["month_expenses"] = conn.execute(
        "SELECT COALESCE(SUM(amount),0) FROM expenses WHERE strftime('%Y-%m',exp_date)=strftime('%Y-%m','now')"
    ).fetchone()[0]
    stats["total_stock_value"] = conn.execute(
        "SELECT COALESCE(SUM(stock_qty*selling_price),0) FROM products WHERE active=1").fetchone()[0]
    conn.close()
    return stats

def get_sales_by_day(days=30):
    conn = get_connection()
    rows = conn.execute("""
        SELECT date(sale_date) as day, SUM(total) as total, COUNT(*) as invoices
        FROM sales WHERE sale_date >= date('now', ?)
        GROUP BY day ORDER BY day
    """, (f"-{days} days",)).fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_top_products(limit=10):
    conn = get_connection()
    rows = conn.execute("""
        SELECT p.name, SUM(si.quantity) as sold_qty, SUM(si.total) as revenue
        FROM sale_items si JOIN products p ON si.product_id=p.id
        GROUP BY p.id ORDER BY sold_qty DESC LIMIT ?
    """, (limit,)).fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_category_sales():
    conn = get_connection()
    rows = conn.execute("""
        SELECT c.name, SUM(si.total) as total
        FROM sale_items si
        JOIN products p ON si.product_id=p.id
        JOIN categories c ON p.category_id=c.id
        GROUP BY c.id ORDER BY total DESC
    """).fetchall()
    conn.close()
    return [dict(r) for r in rows]
