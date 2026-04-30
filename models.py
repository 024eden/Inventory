"""
models.py - All data-access functions for the Variety Store System
Fully compatible with SQL Server + pyodbc
"""

from database import get_connection, hash_password
from datetime import datetime


# ═══════════════════════════════════════════════════════════════
#  HELPER - convert pyodbc Row → dict
# ═══════════════════════════════════════════════════════════════
def _fix_keys(d):
    """Normalize column names and convert datetime objects to strings."""
    if d is None:
        return None
    result = {}
    remap = {
        "fullname":     "full_name",
        "createdat":    "created_at",
        "updatedat":    "updated_at",
        "saledate":     "sale_date",
        "purchasedate": "purchase_date",
        "expdate":      "exp_date",
        "stockqty":     "stock_qty",
        "minstock":     "min_stock",
        "maxstock":     "max_stock",
        "costprice":    "cost_price",
        "sellingprice": "selling_price",
        "categoryid":   "category_id",
        "supplierid":   "supplier_id",
        "invoiceno":    "invoice_no",
        "ponumber":     "po_number",
        "saleid":       "sale_id",
        "productid":    "product_id",
        "purchaseid":   "purchase_id",
        "userid":       "user_id",
        "branchid":     "branch_id",
        "customerid":   "customer_id",
        "paidamount":   "paid_amount",
        "changeamount": "change_amount",
        "paymentmethod":"payment_method",
        "totalamount":  "total_amount",
        "totalspent":   "total_spent",
        "adjtype":      "adj_type",
        "unitprice":    "unit_price",
        "unitcost":     "unit_cost",
        "categoryname": "category_name",
        "suppliername": "supplier_name",
        "username_":    "user_name",
        "customername": "customer_name",
        "productname":  "product_name",
        "soldqty":      "sold_qty",
        "lowstockcount":"low_stock_count",
    }
    for k, v in d.items():
        key = remap.get(k, k)
        # Convert datetime objects to string
        if hasattr(v, "strftime"):
            v = v.strftime("%Y-%m-%d %H:%M:%S")
        result[key] = v
    return result

def _row(cursor, row):
    if row is None:
        return None
    raw = dict(zip([col[0].lower() for col in cursor.description], row))
    return _fix_keys(raw)

def _rows(cursor, rows):
    cols = [col[0].lower() for col in cursor.description]
    return [_fix_keys(dict(zip(cols, r))) for r in rows]

def _normalize_user(u):
    return u  # _fix_keys already handles this


# ═══════════════════════════════════════════════════════════════
#  AUTH
# ═══════════════════════════════════════════════════════════════
def login(username, password):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM Users WHERE Username=? AND Password=? AND Active=1",
        (username, hash_password(password))
    )
    row = cursor.fetchone()
    result = _row(cursor, row)
    conn.close()
    if result and 'fullname' in result:
        result['full_name'] = result.pop('fullname')
    return result

def get_all_users():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Users ORDER BY FullName")
    result = [_normalize_user(r) for r in _rows(cursor, cursor.fetchall())]
    conn.close()
    return result

def add_user(username, password, full_name, role, email="", phone=""):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO Users (Username, Password, FullName, Role, Email, Phone)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (username, hash_password(password), full_name, role, email, phone))
        conn.commit()
        return True, "User added successfully"
    except Exception as e:
        return False, str(e)
    finally:
        conn.close()

def update_user(user_id, full_name, role, email, phone, active):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE Users SET FullName=?, Role=?, Email=?, Phone=?, Active=?
        WHERE Id=?
    """, (full_name, role, email, phone, active, user_id))
    conn.commit()
    conn.close()

def change_password(user_id, new_password):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE Users SET Password=? WHERE Id=?",
                   (hash_password(new_password), user_id))
    conn.commit()
    conn.close()


# ═══════════════════════════════════════════════════════════════
#  CATEGORIES
# ═══════════════════════════════════════════════════════════════
def get_categories():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Categories ORDER BY Name")
    result = _rows(cursor, cursor.fetchall())
    conn.close()
    return result

def add_category(name, description=""):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO Categories (Name, Description) VALUES (?, ?)", (name, description))
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
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Suppliers ORDER BY Name")
    result = _rows(cursor, cursor.fetchall())
    conn.close()
    return result

def add_supplier(name, contact, phone, email, address):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO Suppliers (Name, Contact, Phone, Email, Address)
            VALUES (?, ?, ?, ?, ?)
        """, (name, contact, phone, email, address))
        conn.commit()
        return True, "Supplier added"
    except Exception as e:
        return False, str(e)
    finally:
        conn.close()

def update_supplier(sup_id, name, contact, phone, email, address):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE Suppliers SET Name=?, Contact=?, Phone=?, Email=?, Address=?
        WHERE Id=?
    """, (name, contact, phone, email, address, sup_id))
    conn.commit()
    conn.close()


# ═══════════════════════════════════════════════════════════════
#  PRODUCTS / INVENTORY
# ═══════════════════════════════════════════════════════════════
def get_all_products(search="", category_id=None, low_stock=False):
    conn = get_connection()
    cursor = conn.cursor()
    sql = """
        SELECT p.*, c.Name as category_name, s.Name as supplier_name
        FROM Products p
        LEFT JOIN Categories c ON p.Category_Id = c.Id
        LEFT JOIN Suppliers s  ON p.Supplier_Id = s.Id
        WHERE p.Active = 1
    """
    params = []
    if search:
        sql += " AND (p.Name LIKE ? OR p.Barcode LIKE ?)"
        params += [f"%{search}%", f"%{search}%"]
    if category_id:
        sql += " AND p.Category_Id = ?"
        params.append(category_id)
    if low_stock:
        sql += " AND p.Stock_Qty <= p.Min_Stock"
    sql += " ORDER BY p.Name"
    cursor.execute(sql, params)
    result = _rows(cursor, cursor.fetchall())
    conn.close()
    return result

def get_product_by_barcode(barcode):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT p.*, c.Name as category_name
        FROM Products p LEFT JOIN Categories c ON p.Category_Id = c.Id
        WHERE p.Barcode = ? AND p.Active = 1
    """, (barcode,))
    row = cursor.fetchone()
    result = _row(cursor, row)
    conn.close()
    return result

def get_product_by_id(pid):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Products WHERE Id = ?", (pid,))
    row = cursor.fetchone()
    result = _row(cursor, row)
    conn.close()
    return result

def add_product(barcode, name, description, category_id, supplier_id,
                unit, cost_price, selling_price, stock_qty, min_stock, max_stock):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO Products
            (Barcode, Name, Description, Category_Id, Supplier_Id, Unit,
             Cost_Price, Selling_Price, Stock_Qty, Min_Stock, Max_Stock)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (barcode, name, description, category_id, supplier_id, unit,
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
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE Products SET Barcode=?, Name=?, Description=?, Category_Id=?,
        Supplier_Id=?, Unit=?, Cost_Price=?, Selling_Price=?,
        Min_Stock=?, Max_Stock=?, Updated_At=GETDATE()
        WHERE Id=?
    """, (barcode, name, description, category_id, supplier_id, unit,
          cost_price, selling_price, min_stock, max_stock, pid))
    conn.commit()
    conn.close()

def update_stock(product_id, qty_change, cursor_ext=None, conn_ext=None):
    own = conn_ext is None
    conn = get_connection() if own else conn_ext
    cursor = conn.cursor() if cursor_ext is None else cursor_ext
    cursor.execute(
        "UPDATE Products SET Stock_Qty = Stock_Qty + ?, Updated_At = GETDATE() WHERE Id = ?",
        (qty_change, product_id)
    )
    if own:
        conn.commit()
        conn.close()

def delete_product(pid):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE Products SET Active = 0 WHERE Id = ?", (pid,))
    conn.commit()
    conn.close()

def adjust_stock(product_id, user_id, adj_type, quantity, reason):
    conn = get_connection()
    cursor = conn.cursor()
    delta = quantity if adj_type == "add" else -quantity
    cursor.execute("UPDATE Products SET Stock_Qty = Stock_Qty + ? WHERE Id = ?", (delta, product_id))
    cursor.execute("""
        INSERT INTO Stock_Adjustments (Product_Id, User_Id, Adj_Type, Quantity, Reason)
        VALUES (?, ?, ?, ?, ?)
    """, (product_id, user_id, adj_type, quantity, reason))
    conn.commit()
    conn.close()


# ═══════════════════════════════════════════════════════════════
#  CUSTOMERS
# ═══════════════════════════════════════════════════════════════
def get_all_customers(search=""):
    conn = get_connection()
    cursor = conn.cursor()
    sql = "SELECT * FROM Customers WHERE 1=1"
    params = []
    if search:
        sql += " AND (Name LIKE ? OR Phone LIKE ?)"
        params += [f"%{search}%", f"%{search}%"]
    sql += " ORDER BY Name"
    cursor.execute(sql, params)
    result = _rows(cursor, cursor.fetchall())
    conn.close()
    return result

def add_customer(name, phone, email, address):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO Customers (Name, Phone, Email, Address) VALUES (?, ?, ?, ?)",
            (name, phone, email, address)
        )
        conn.commit()
        return True, "Customer added"
    except Exception as e:
        return False, str(e)
    finally:
        conn.close()

def update_customer(cid, name, phone, email, address):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE Customers SET Name=?, Phone=?, Email=?, Address=? WHERE Id=?",
        (name, phone, email, address, cid)
    )
    conn.commit()
    conn.close()


# ═══════════════════════════════════════════════════════════════
#  SALES / POS
# ═══════════════════════════════════════════════════════════════
def save_sale(invoice_no, customer_id, user_id, branch_id,
              subtotal, discount, tax, total, paid, change, method, items, notes=""):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO Sales
            (Invoice_No, Customer_Id, User_Id, Branch_Id, Subtotal, Discount,
             Tax, Total, Paid_Amount, Change_Amount, Payment_Method, Notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (invoice_no, customer_id, user_id, branch_id, subtotal, discount,
              tax, total, paid, change, method, notes))

        cursor.execute("SELECT SCOPE_IDENTITY()")
        sale_id = int(cursor.fetchone()[0])

        for item in items:
            cursor.execute("""
                INSERT INTO Sale_Items (Sale_Id, Product_Id, Quantity, Unit_Price, Discount, Total)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (sale_id, item["product_id"], item["qty"], item["price"],
                  item.get("discount", 0), item["total"]))
            update_stock(item["product_id"], -item["qty"], cursor_ext=cursor, conn_ext=conn)

        if customer_id:
            cursor.execute(
                "UPDATE Customers SET Total_Spent = Total_Spent + ?, Points = Points + ? WHERE Id = ?",
                (total, int(total / 100), customer_id)
            )

        conn.commit()
        return True, sale_id
    except Exception as e:
        conn.rollback()
        return False, str(e)
    finally:
        conn.close()

def get_sales(date_from=None, date_to=None, search="", limit=200):
    conn = get_connection()
    cursor = conn.cursor()
    sql = """
        SELECT TOP (?) s.*, u.FullName as cashier, c.Name as customer_name
        FROM Sales s
        LEFT JOIN Users u ON s.User_Id = u.Id
        LEFT JOIN Customers c ON s.Customer_Id = c.Id
        WHERE 1=1
    """
    params = [limit]
    if date_from:
        sql += " AND CAST(s.Sale_Date AS DATE) >= ?"
        params.append(date_from)
    if date_to:
        sql += " AND CAST(s.Sale_Date AS DATE) <= ?"
        params.append(date_to)
    if search:
        sql += " AND s.Invoice_No LIKE ?"
        params.append(f"%{search}%")
    sql += " ORDER BY s.Sale_Date DESC"
    cursor.execute(sql, params)
    result = _rows(cursor, cursor.fetchall())
    conn.close()
    return result

def get_sale_items(sale_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT si.*, p.Name as product_name, p.Unit
        FROM Sale_Items si LEFT JOIN Products p ON si.Product_Id = p.Id
        WHERE si.Sale_Id = ?
    """, (sale_id,))
    result = _rows(cursor, cursor.fetchall())
    conn.close()
    return result


# ═══════════════════════════════════════════════════════════════
#  PURCHASES
# ═══════════════════════════════════════════════════════════════
def save_purchase(po_number, supplier_id, user_id, total, paid, items, notes=""):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO Purchases (PO_Number, Supplier_Id, User_Id, Total_Amount, Paid_Amount, Notes)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (po_number, supplier_id, user_id, total, paid, notes))

        cursor.execute("SELECT SCOPE_IDENTITY()")
        po_id = int(cursor.fetchone()[0])

        for item in items:
            cursor.execute("""
                INSERT INTO Purchase_Items (Purchase_Id, Product_Id, Quantity, Unit_Cost, Total)
                VALUES (?, ?, ?, ?, ?)
            """, (po_id, item["product_id"], item["qty"], item["cost"], item["total"]))
            update_stock(item["product_id"], item["qty"], cursor_ext=cursor, conn_ext=conn)

        conn.commit()
        return True, po_id
    except Exception as e:
        conn.rollback()
        return False, str(e)
    finally:
        conn.close()

def get_purchases(date_from=None, date_to=None):
    conn = get_connection()
    cursor = conn.cursor()
    sql = """
        SELECT p.*, s.Name as supplier_name, u.FullName as user_name
        FROM Purchases p
        LEFT JOIN Suppliers s ON p.Supplier_Id = s.Id
        LEFT JOIN Users u ON p.User_Id = u.Id
        WHERE 1=1
    """
    params = []
    if date_from:
        sql += " AND CAST(p.Purchase_Date AS DATE) >= ?"
        params.append(date_from)
    if date_to:
        sql += " AND CAST(p.Purchase_Date AS DATE) <= ?"
        params.append(date_to)
    sql += " ORDER BY p.Purchase_Date DESC"
    cursor.execute(sql, params)
    result = _rows(cursor, cursor.fetchall())
    conn.close()
    return result


# ═══════════════════════════════════════════════════════════════
#  EXPENSES
# ═══════════════════════════════════════════════════════════════
def add_expense(category, description, amount, user_id, branch_id=1):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO Expenses (Category, Description, Amount, User_Id, Branch_Id)
        VALUES (?, ?, ?, ?, ?)
    """, (category, description, amount, user_id, branch_id))
    conn.commit()
    conn.close()

def get_expenses(date_from=None, date_to=None):
    conn = get_connection()
    cursor = conn.cursor()
    sql = """
        SELECT e.*, u.FullName as user_name
        FROM Expenses e LEFT JOIN Users u ON e.User_Id = u.Id
        WHERE 1=1
    """
    params = []
    if date_from:
        sql += " AND CAST(e.Exp_Date AS DATE) >= ?"
        params.append(date_from)
    if date_to:
        sql += " AND CAST(e.Exp_Date AS DATE) <= ?"
        params.append(date_to)
    sql += " ORDER BY e.Exp_Date DESC"
    cursor.execute(sql, params)
    result = _rows(cursor, cursor.fetchall())
    conn.close()
    return result


# ═══════════════════════════════════════════════════════════════
#  REPORTS / DASHBOARD
# ═══════════════════════════════════════════════════════════════
def get_dashboard_stats():
    conn = get_connection()
    cursor = conn.cursor()
    today = datetime.now().strftime("%Y-%m-%d")
    stats = {}

    cursor.execute("SELECT ISNULL(SUM(Total), 0) FROM Sales WHERE CAST(Sale_Date AS DATE) = ?", (today,))
    stats["today_sales"] = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM Sales WHERE CAST(Sale_Date AS DATE) = ?", (today,))
    stats["today_invoices"] = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM Products WHERE Active = 1")
    stats["total_products"] = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM Products WHERE Active = 1 AND Stock_Qty <= Min_Stock")
    stats["low_stock_count"] = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM Customers")
    stats["total_customers"] = cursor.fetchone()[0]

    cursor.execute("""
        SELECT ISNULL(SUM(Total), 0) FROM Sales
        WHERE YEAR(Sale_Date) = YEAR(GETDATE()) AND MONTH(Sale_Date) = MONTH(GETDATE())
    """)
    stats["month_sales"] = cursor.fetchone()[0]

    cursor.execute("""
        SELECT ISNULL(SUM(Amount), 0) FROM Expenses
        WHERE YEAR(Exp_Date) = YEAR(GETDATE()) AND MONTH(Exp_Date) = MONTH(GETDATE())
    """)
    stats["month_expenses"] = cursor.fetchone()[0]

    cursor.execute("SELECT ISNULL(SUM(Stock_Qty * Selling_Price), 0) FROM Products WHERE Active = 1")
    stats["total_stock_value"] = cursor.fetchone()[0]

    conn.close()
    return stats

def get_sales_by_day(days=30):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT CAST(Sale_Date AS DATE) as day, SUM(Total) as total, COUNT(*) as invoices
        FROM Sales
        WHERE Sale_Date >= DATEADD(DAY, ?, GETDATE())
        GROUP BY CAST(Sale_Date AS DATE)
        ORDER BY day
    """, (-days,))
    result = _rows(cursor, cursor.fetchall())
    conn.close()
    return result

def get_top_products(limit=10):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT TOP (?) p.Name, SUM(si.Quantity) as sold_qty, SUM(si.Total) as revenue
        FROM Sale_Items si JOIN Products p ON si.Product_Id = p.Id
        GROUP BY p.Id, p.Name
        ORDER BY sold_qty DESC
    """, (limit,))
    result = _rows(cursor, cursor.fetchall())
    conn.close()
    return result

def get_category_sales():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT c.Name, SUM(si.Total) as total
        FROM Sale_Items si
        JOIN Products p ON si.Product_Id = p.Id
        JOIN Categories c ON p.Category_Id = c.Id
        GROUP BY c.Id, c.Name
        ORDER BY total DESC
    """)
    result = _rows(cursor, cursor.fetchall())
    conn.close()
    return result
