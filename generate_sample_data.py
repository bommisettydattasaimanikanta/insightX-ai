import os
import sqlite3
import pandas as pd
import numpy as np
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment

os.makedirs("sample_data", exist_ok=True)

# 1. Create messy_sales_data.xlsx with intentional errors
wb = openpyxl.Workbook()
ws = wb.active
ws.title = "Sales Transactions"

# Title banner row
ws.merge_cells("A1:G1")
ws["A1"] = "REGIONAL SALES AUDIT & TRANSACTION REPORT (FY 2025-2026)"
ws["A1"].font = Font(bold=True, size=14, color="FFFFFF")
ws["A1"].fill = PatternFill(start_color="1E3A8A", end_color="1E3A8A", fill_type="solid")
ws["A1"].alignment = Alignment(horizontal="center")

# Secondary header row (merged category headers)
ws.merge_cells("A2:B2")
ws["A2"] = "Customer Identification"
ws.merge_cells("C2:E2")
ws["C2"] = "Order & Financial Metrics"
ws.merge_cells("F2:G2")
ws["F2"] = "Geographical Region"

# Main column headers on row 3
headers = ["Customer Name", "Order Date", "Sales Amount", "Discount Rate", "Quantity", "Region", "Category"]
for col_idx, h in enumerate(headers, start=1):
    cell = ws.cell(row=3, column=col_idx, value=h)
    cell.font = Font(bold=True)
    cell.fill = PatternFill(start_color="E2E8F0", end_color="E2E8F0", fill_type="solid")

# Raw messy rows with mixed dates, currency symbols, Indian number formats, merged cells
raw_records = [
    # Customer, Date (mixed), Sales (currency/Indian), Discount (%), Qty, Region, Category
    ["Aarav Sharma (आरव)", "2025-01-15", "$1,450.00", "5%", 4, "North", "Electronics"],
    ["Priya Patel", "16/01/2025", "₹2,50,000", "10%", 12, "West", "Furniture"],
    ["TechSolutions Ltd", "01-18-2025", "$3,200.50", "0%", 8, "South", "Technology"],
    ["Ananya Iyer", "2025-01-20", "1.5 Lakh", "12%", 5, "South", "Electronics"],
    ["Vikram Malhotra", "22/01/2025", "₹85,000", "8%", 3, "North", "Office Supplies"],
    # Subtotal row (intentional noise)
    ["Subtotal North", "", "₹3,35,000", "", 7, "North", ""],
    ["Deepak Verma", "2025-02-01", "$5,100.00", "15%", 10, "East", "Furniture"],
    ["Meera Joshi", "02/05/2025", "₹1,20,000", "5%", 6, "West", "Office Supplies"],
    ["Global Logistics", "2025-02-10", "$8,450.00", "20%", 25, "East", "Technology"],
    ["Rohan Roy", "14/02/2025", "₹75,000", "10%", 2, "North", "Electronics"],
    ["Kavita Nair", "2025-02-18", "2.1 Lakh", "7%", 14, "South", "Furniture"],
    ["Siddharth Sen", "20/02/2025", "$2,900.00", "5%", 5, "East", "Technology"],
    # Grand Total row (intentional noise)
    ["Grand Total", "", "₹18,50,000", "", 88, "", ""]
]

for r_idx, row in enumerate(raw_records, start=4):
    for c_idx, val in enumerate(row, start=1):
        ws.cell(row=r_idx, column=c_idx, value=val)

wb.save("sample_data/messy_sales_data.xlsx")
print("Saved messy_sales_data.xlsx")

# 2. Create retail_operations.sqlite (Multi-table relational DB)
conn = sqlite3.connect("sample_data/retail_operations.sqlite")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS customers (
    customer_id INTEGER PRIMARY KEY,
    name TEXT,
    email TEXT,
    region TEXT,
    segment TEXT
);
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS products (
    product_id INTEGER PRIMARY KEY,
    product_name TEXT,
    category TEXT,
    unit_price REAL,
    unit_cost REAL
);
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS orders (
    order_id INTEGER PRIMARY KEY,
    customer_id INTEGER,
    order_date TEXT,
    status TEXT,
    FOREIGN KEY(customer_id) REFERENCES customers(customer_id)
);
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS order_items (
    item_id INTEGER PRIMARY KEY,
    order_id INTEGER,
    product_id INTEGER,
    quantity INTEGER,
    discount REAL,
    FOREIGN KEY(order_id) REFERENCES orders(order_id),
    FOREIGN KEY(product_id) REFERENCES products(product_id)
);
""")

# Seed Customers
customers_data = [
    (1, "Apex Retailers", "contact@apex.com", "North", "Enterprise"),
    (2, "Beacon Systems", "beacon@systems.com", "West", "Mid-Market"),
    (3, "Crestline Corp", "info@crestline.org", "South", "Enterprise"),
    (4, "Delta Dynamics", "hello@deltadyn.com", "East", "SMB"),
    (5, "Echo Ventures", "team@echo.io", "West", "SMB")
]
cursor.executemany("INSERT INTO customers VALUES (?, ?, ?, ?, ?)", customers_data)

# Seed Products
products_data = [
    (101, "UltraBook Pro 15", "Laptops", 1299.99, 850.00),
    (102, "4K Ergonomic Monitor", "Monitors", 449.50, 275.00),
    (103, "Mechanical Office Keyboard", "Accessories", 89.99, 42.00),
    (104, "Enterprise Cloud Gateway", "Networking", 899.00, 520.00),
    (105, "Wireless Precision Mouse", "Accessories", 49.99, 21.00)
]
cursor.executemany("INSERT INTO products VALUES (?, ?, ?, ?, ?)", products_data)

# Seed Orders
orders_data = [
    (1001, 1, "2025-01-10", "Completed"),
    (1002, 2, "2025-01-12", "Completed"),
    (1003, 3, "2025-01-15", "Completed"),
    (1004, 4, "2025-01-18", "Shipped"),
    (1005, 1, "2025-02-01", "Completed"),
    (1006, 5, "2025-02-05", "Pending")
]
cursor.executemany("INSERT INTO orders VALUES (?, ?, ?, ?)", orders_data)

# Seed Order Items
order_items_data = [
    (1, 1001, 101, 3, 0.05),
    (2, 1001, 103, 5, 0.00),
    (3, 1002, 102, 4, 0.10),
    (4, 1003, 104, 2, 0.00),
    (5, 1004, 105, 10, 0.15),
    (6, 1005, 101, 2, 0.00),
    (7, 1006, 102, 1, 0.00)
]
cursor.executemany("INSERT INTO order_items VALUES (?, ?, ?, ?, ?)", order_items_data)

conn.commit()
conn.close()
print("Saved retail_operations.sqlite")

# 3. Create web_traffic_timeseries.csv
dates = pd.date_range(start="2024-01-01", end="2024-06-30", freq="D")
np.random.seed(42)
base_trend = np.linspace(5000, 15000, len(dates))
seasonality = 1500 * np.sin(2 * np.pi * np.arange(len(dates)) / 7) # weekly seasonality
noise = np.random.normal(0, 400, len(dates))
visitors = np.maximum(1000, (base_trend + seasonality + noise).astype(int))

pageviews = (visitors * np.random.uniform(2.8, 4.2, len(dates))).astype(int)
bounce_rate = np.round(np.random.uniform(35.0, 52.0, len(dates)), 2)
conversions = (visitors * np.random.uniform(0.02, 0.05, len(dates))).astype(int)
revenue = np.round(conversions * np.random.uniform(45.0, 95.0, len(dates)), 2)

traffic_df = pd.DataFrame({
    "date": dates.strftime("%Y-%m-%d"),
    "visitors": visitors,
    "pageviews": pageviews,
    "bounce_rate_pct": bounce_rate,
    "conversions": conversions,
    "revenue": revenue
})
traffic_df.to_csv("sample_data/web_traffic_timeseries.csv", index=False)
print("Saved web_traffic_timeseries.csv")
