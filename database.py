import hashlib
from datetime import datetime
import pyodbc


# connection 
def get_connection():
    return pyodbc.connect(
       'DRIVER={ODBC Driver 17 for SQL Server};'
        'SERVER=localhost\\MSSQL;'
        'DATABASE=VarietyStoreDB;'
         'Trusted_Connection=yes;' 
    )


# ✅ PASSWORD HASH
def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()


def init_db():
    try:
        conn = get_connection()
        cursor = conn.cursor()

        _seed_defaults(cursor, conn)

        conn.close()
        print("Database initialized successfully")

    except Exception as e:
        print("Database init error:", e)


# ✅ SEED DEFAULT DATA
def _seed_defaults(c, conn):

    # Admin user
    c.execute("SELECT Id FROM Users WHERE Username = ?", ("admin",))
    if not c.fetchone():
        c.execute("""
            INSERT INTO Users (Username, Password, FullName, Role)
            VALUES (?, ?, ?, ?)
        """, ("admin", hash_password("admin123"), "System Administrator", "admin"))

    # Branch
    c.execute("SELECT Id FROM Branches")
    if not c.fetchone():
        c.execute("""
            INSERT INTO Branches (Name, Address)
            VALUES (?, ?)
        """, ("Main Branch", "Store Address"))

    # Categories
    categories = [
        "Groceries", "Beverages", "Snacks", "Dairy", "Bakery",
        "Household", "Personal Care", "Electronics", "Clothing",
        "Stationery", "Toys", "Medicines", "Vegetables", "Fruits", "Other"
    ]

    for cat in categories:
        c.execute("""
            IF NOT EXISTS (SELECT 1 FROM Categories WHERE Name = ?)
            INSERT INTO Categories (Name) VALUES (?)
        """, (cat, cat))

    # Walk-in customer
    c.execute("SELECT Id FROM Customers WHERE Name = ?", ("Walk-in Customer",))
    if not c.fetchone():
        c.execute("""
            INSERT INTO Customers (Name, Phone)
            VALUES (?, ?)
        """, ("Walk-in Customer", "0000000000"))

    conn.commit()


# ✅ GENERATE INVOICE NUMBER
def generate_invoice_no():
    conn = get_connection()
    cursor = conn.cursor()

    today = datetime.now().strftime("%Y%m%d")
    like_pattern = f"INV{today}%"

    cursor.execute(
        "SELECT COUNT(*) FROM Sales WHERE Invoice_No LIKE ?",
        (like_pattern,)
    )

    count = cursor.fetchone()[0] + 1
    conn.close()

    return f"INV{today}{count:04d}"


# ✅ GENERATE PO NUMBER
def generate_po_number():
    conn = get_connection()
    cursor = conn.cursor()

    today = datetime.now().strftime("%Y%m%d")
    like_pattern = f"PO{today}%"

    cursor.execute(
        "SELECT COUNT(*) FROM Purchases WHERE PO_Number LIKE ?",
        (like_pattern,)
    )

    count = cursor.fetchone()[0] + 1
    conn.close()

    return f"PO{today}{count:04d}"