"""
Run this ONCE before anything else.
Creates company.db with employees, products, and sales tables.
Command: python setup_db.py
"""
import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "company.db")
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

cursor.execute('''CREATE TABLE IF NOT EXISTS employees (
    id INTEGER PRIMARY KEY, name TEXT, department TEXT,
    salary INTEGER, city TEXT)''')

cursor.execute('''CREATE TABLE IF NOT EXISTS products (
    id INTEGER PRIMARY KEY, name TEXT, category TEXT,
    price REAL, stock INTEGER)''')

cursor.execute('''CREATE TABLE IF NOT EXISTS sales (
    id INTEGER PRIMARY KEY, product_id INTEGER, employee_id INTEGER,
    quantity INTEGER, sale_date TEXT, total_amount REAL)''')

cursor.executemany('INSERT OR IGNORE INTO employees VALUES (?,?,?,?,?)', [
    (1,'Rahul Sharma','Engineering',95000,'Mumbai'),
    (2,'Priya Patel','Sales',72000,'Delhi'),
    (3,'Amit Singh','Engineering',88000,'Bangalore'),
    (4,'Sneha Gupta','Marketing',68000,'Mumbai'),
    (5,'Vikash Kumar','Sales',75000,'Pune'),
    (6,'Ananya Reddy','Engineering',92000,'Hyderabad'),
    (7,'Rohan Mehta','HR',60000,'Mumbai'),
    (8,'Divya Nair','Marketing',71000,'Bangalore'),
    (9,'Karan Joshi','Sales',78000,'Delhi'),
    (10,'Pooja Iyer','Engineering',85000,'Chennai'),
])

cursor.executemany('INSERT OR IGNORE INTO products VALUES (?,?,?,?,?)', [
    (1,'AI Course','Education',4999,150),
    (2,'Cloud Workshop','Education',2999,200),
    (3,'ML Toolkit','Software',9999,80),
    (4,'Data Dashboard','Software',7499,60),
    (5,'GenAI Bootcamp','Education',8999,120),
])

cursor.executemany('INSERT OR IGNORE INTO sales VALUES (?,?,?,?,?,?)', [
    (1,1,2,10,'2026-05-01',49990),
    (2,2,5,8,'2026-05-03',23992),
    (3,3,9,3,'2026-05-05',29997),
    (4,5,2,15,'2026-05-07',134985),
    (5,1,9,5,'2026-05-10',24995),
    (6,4,5,4,'2026-05-12',29996),
    (7,2,2,6,'2026-05-15',17994),
    (8,5,9,8,'2026-05-18',71992),
    (9,3,5,2,'2026-05-20',19998),
    (10,1,2,12,'2026-05-25',59988),
])

conn.commit()
conn.close()
print(f"Database created: {DB_PATH}")
print("Tables: employees, products, sales")
