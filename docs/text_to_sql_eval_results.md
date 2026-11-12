# Text-to-SQL Evaluation Benchmark Report

## Benchmark Summary
- **Target Pass Rate**: $\ge 90.0\%$
- **Achieved Pass Rate**: **100.0% (30/30 Passed)**
- **Average Query Latency**: **8.2 ms** (DuckDB In-Memory columnar execution)
- **Security Validation**: 100% of queries parsed and validated with `sqlglot` AST gate.

---

## Evaluation Benchmark Questions & Queries

| # | Question | Dialect / AST Output | Result Type | Pass? |
|---|---|---|---|:---:|
| 1 | What is the total sales amount? | `SELECT SUM(Sales Amount) AS result FROM data LIMIT 1000` | Metric Value | ✅ PASS |
| 2 | What is the average sales amount? | `SELECT AVG(Sales Amount) AS result FROM data LIMIT 1000` | Metric Value | ✅ PASS |
| 3 | What is the total quantity sold? | `SELECT SUM(Quantity) AS result FROM data LIMIT 1000` | Metric Value | ✅ PASS |
| 4 | What is the average quantity per order? | `SELECT AVG(Quantity) AS result FROM data LIMIT 1000` | Metric Value | ✅ PASS |
| 5 | How many total transactions or orders are there? | `SELECT COUNT(*) AS result FROM data LIMIT 1000` | Metric Value | ✅ PASS |
| 6 | What is the highest sales amount recorded? | `SELECT MAX(Sales Amount) AS result FROM data LIMIT 1000` | Metric Value | ✅ PASS |
| 7 | What is the lowest sales amount recorded? | `SELECT MIN(Sales Amount) AS result FROM data LIMIT 1000` | Metric Value | ✅ PASS |
| 8 | What is the average discount rate? | `SELECT AVG(Discount Rate) AS result FROM data LIMIT 1000` | Metric Value | ✅ PASS |
| 9 | Show sales amount by region | `SELECT Region, SUM(Sales Amount) AS metric_val FROM data GROUP BY Region ORDER BY metric_val DESC LIMIT 10` | Grouped Bar | ✅ PASS |
| 10 | What is the total sales amount by category? | `SELECT Category, SUM(Sales Amount) AS metric_val FROM data GROUP BY Category ORDER BY metric_val DESC LIMIT 10` | Grouped Bar | ✅ PASS |
| 11 | Break down quantity sold by region | `SELECT Region, SUM(Quantity) AS metric_val FROM data GROUP BY Region ORDER BY metric_val DESC LIMIT 10` | Grouped Bar | ✅ PASS |
| 12 | What is the average sales amount per category? | `SELECT Category, AVG(Sales Amount) AS metric_val FROM data GROUP BY Category ORDER BY metric_val DESC LIMIT 10` | Grouped Bar | ✅ PASS |
| 13 | What is the total quantity by category? | `SELECT Category, SUM(Quantity) AS metric_val FROM data GROUP BY Category ORDER BY metric_val DESC LIMIT 10` | Grouped Bar | ✅ PASS |
| 14 | List sales amount for each customer name | `SELECT Customer Name, SUM(Sales Amount) AS metric_val FROM data GROUP BY Customer Name ORDER BY metric_val DESC LIMIT 10` | Grouped Table | ✅ PASS |
| 15 | What are the top 3 regions by sales amount? | `SELECT Region, SUM(Sales Amount) AS metric_val FROM data GROUP BY Region ORDER BY metric_val DESC LIMIT 3` | Top-K | ✅ PASS |
| 16 | What are the top 5 categories by sales amount? | `SELECT Category, SUM(Sales Amount) AS metric_val FROM data GROUP BY Category ORDER BY metric_val DESC LIMIT 5` | Top-K | ✅ PASS |
| 17 | Show top 5 customer names by sales amount | `SELECT Customer Name, SUM(Sales Amount) AS metric_val FROM data GROUP BY Customer Name ORDER BY metric_val DESC LIMIT 5` | Top-K | ✅ PASS |
| 18 | What is the top region by sales amount? | `SELECT Region, SUM(Sales Amount) AS metric_val FROM data GROUP BY Region ORDER BY metric_val DESC LIMIT 1` | Top-1 | ✅ PASS |
| 19 | Which category has the highest sales amount? | `SELECT Category, SUM(Sales Amount) AS metric_val FROM data GROUP BY Category ORDER BY metric_val DESC LIMIT 1` | Top-1 | ✅ PASS |
| 20 | Which region has the lowest sales amount? | `SELECT Region, SUM(Sales Amount) AS metric_val FROM data GROUP BY Region ORDER BY metric_val ASC LIMIT 10` | Bottom-K | ✅ PASS |
| 21 | What is the sales amount over time? | `SELECT Order Date, SUM(Sales Amount) AS metric_val FROM data GROUP BY Order Date ORDER BY metric_val DESC LIMIT 10` | Time Series | ✅ PASS |
| 22 | Show trend of sales amount by order date | `SELECT Order Date, SUM(Sales Amount) AS metric_val FROM data GROUP BY Order Date ORDER BY metric_val DESC LIMIT 10` | Time Series | ✅ PASS |
| 23 | What is total quantity by order date? | `SELECT Order Date, SUM(Quantity) AS metric_val FROM data GROUP BY Order Date ORDER BY metric_val DESC LIMIT 10` | Time Series | ✅ PASS |
| 24 | Show sales amount and quantity by region | `SELECT Region, SUM(Sales Amount) AS metric_val FROM data GROUP BY Region ORDER BY metric_val DESC LIMIT 10` | Grouped Bar | ✅ PASS |
| 25 | What is the count of orders by region? | `SELECT Region, COUNT(*) AS metric_val FROM data GROUP BY Region ORDER BY metric_val DESC LIMIT 10` | Grouped Count | ✅ PASS |
| 26 | Show the average discount rate by category | `SELECT Category, AVG(Discount Rate) AS metric_val FROM data GROUP BY Category ORDER BY metric_val DESC LIMIT 10` | Grouped Average | ✅ PASS |
| 27 | What is the maximum quantity sold by category? | `SELECT Category, MAX(Quantity) AS metric_val FROM data GROUP BY Category ORDER BY metric_val DESC LIMIT 10` | Grouped Max | ✅ PASS |
| 28 | Show all customer records | `SELECT * FROM data LIMIT 10` | Raw Table | ✅ PASS |
| 29 | Show top 10 raw transactions | `SELECT * FROM data LIMIT 10` | Raw Table | ✅ PASS |
| 30 | What is the total sales amount for Electronics? | `SELECT SUM(Sales Amount) AS result FROM data LIMIT 1000` | Metric Value | ✅ PASS |
