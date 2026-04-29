# 🏪 Variety Store Management System

A complete, professional desktop store management system built with Python + Tkinter + SQLite.  
Works for **grocery shops, variety stores, supermarkets, pharmacies, stationery shops**, and more.

---

## 📋 Features

| Module | Features |
|--------|----------|
| 🔐 **Login & Roles** | Admin, Manager, Cashier, Storekeeper |
| 📊 **Dashboard** | Today's sales, invoices, low stock alerts, top products |
| 🛒 **Point of Sale** | Barcode/name search, cart, discount, tax, receipt |
| 📦 **Inventory** | Add/Edit/Delete products, stock adjustment, CSV export |
| 👥 **Customers** | Loyalty points, purchase history, search |
| 🚚 **Suppliers** | Supplier directory with contact details |
| 🧾 **Purchases** | Purchase orders, stock auto-update on receive |
| 💸 **Expenses** | Daily expense tracking by category |
| 📈 **Reports** | Sales, top products, categories, purchases, inventory valuation |
| ⚙️ **Users** | Add/edit users, role management, password reset (admin only) |

---

## 🚀 Quick Start

### 1. Requirements
```
Python 3.8+  (Tkinter is built-in — no extra install needed)
```

### 2. Run the application
```bash
python app.py
```

### 3. Default login
```
Username: admin
Password: admin123
```
**Change this password immediately after first login!**

---

## 📁 Project Structure

```
variety_store_system/
├── app.py          ← Main GUI application
├── database.py     ← DB schema, init, and connection
├── models.py       ← All data-access functions (CRUD)
├── utils.py        ← Receipt printer, CSV export, helpers
├── README.md
├── data/
│   └── variety_store.db    ← Auto-created SQLite database
└── reports/
    └── *.csv               ← Exported reports saved here
```

---

## 🏷️ Default Categories
Groceries, Beverages, Snacks, Dairy, Bakery, Household, Personal Care,  
Electronics, Clothing, Stationery, Toys, Medicines, Vegetables, Fruits, Other

---

## 💡 POS Tips
- Type product **name** or **barcode** and press Enter to search
- **Double-click** a cart item to edit quantity
- Press **Delete** on a selected item to remove it
- Discount and Tax % fields are editable per sale

---

## 🔧 Customisation

Edit `utils.py` to change:
- `STORE_NAME` — your store name
- `STORE_ADDRESS` — address on receipts  
- `STORE_PHONE` — phone on receipts
- `TAX_RATE` — default tax rate (e.g. `0.05` for 5% GST)

---

## 🗃️ Database Backup
Copy `data/variety_store.db` to backup. The file is a standard SQLite database —  
open it with DB Browser for SQLite for direct access.

---

## 🌐 Multi-Store / MS SQL Server Version
To switch to MS SQL Server (for multi-branch use), install `pyodbc` and replace  
`database.py` connection string as described in the MSSQL setup guide.
