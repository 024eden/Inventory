import pyodbc

conn = pyodbc.connect(
    'DRIVER={ODBC Driver 17 for SQL Server};'
    'SERVER=localhost\\MSSQL;'
    'DATABASE=VarietyStoreDB;'
    'Trusted_Connection=yes;'
)

cursor = conn.cursor()

# Drop and recreate with all columns
cursor.execute("DROP TABLE Branches")

cursor.execute("""
    CREATE TABLE Branches (
        Id INT IDENTITY(1,1) PRIMARY KEY,
        Name NVARCHAR(100) NOT NULL,
        Address NVARCHAR(255),
        Location NVARCHAR(255),
        Phone NVARCHAR(20),
        Email NVARCHAR(100),
        Manager NVARCHAR(100),
        Active BIT DEFAULT 1,
        CreatedAt DATETIME DEFAULT GETDATE()
    )
""")

conn.commit()
print("Branches table recreated successfully!")

cursor.close()
conn.close()