# Fitness Center Management & Business Intelligence (BI) Platform

A comprehensive, end-to-end Data Engineering and Business Intelligence project. This platform features a robust Operational Database (OLTP) for daily gym management, an automated enterprise ETL pipeline, a dimensional Data Warehouse (OLAP), and an interactive BI Dashboard for advanced financial and behavioral analytics.

## 🚀 Key Features

### 1. Operational System (OLTP)
* **Member Management:** Full CRUD operations for member registration, plans, and subscription lifecycle tracking.
* **Live Attendance & Gate Control:** Live attendance logging with integrated database constraints.
* **Staff & Payroll Management:** Operational module to manage gym staff, roles (Managers, Trainers, Receptionists), and dynamic salary payouts.
* **Smart Equipment Maintenance:** Tracking gym assets and machinery condition with dynamic status auditing.

### 2. Database Automation & Triggers
* **Automated Status Correction:** Built-in MySQL Database Triggers that instantly switch equipment status from `Under Maintenance` to `Functional` once a maintenance log and repair cost are submitted.
* **Data Integrity:** Strict foreign key constraints and transactional integrity across all operational tables.

### 3. Enterprise ETL Pipeline (`warehouse_etl.py`)
* **Isolated Database Connections:** Designed with completely separate Read and Write database connections (`read_conn` & `write_conn`) using `buffered=True` to eliminate multi-statement synchronization bottlenecks (`Commands out of sync` errors) in high-concurrency environments.
* **Incremental & Full Reloads:** Syncs operational dimensions and truncates/reloads complex analytical facts smoothly.

### 4. Data Warehouse (OLAP) & Analytics
* **Dimensional Modeling:** Organized using a optimized Star Schema design with dedicated analytical dimensions (`Dim_Members_Analytical`, `Dim_Plans_Analytical`, `Dim_Staff_Analytical`).
* **Behavioral Analysis (Fact_Attendance_Analytics):** Aggregates gym check-ins to monitor user activity patterns.
* **Financial Cost Tracking (Fact_Financial_Costs):** Consolidating operational salaries and machine maintenance expenses into a centralized ledger for net profit calculation.

### 5. Interactive BI Dashboard
* **RFM Customer Segmentation:** Automatically groups members based on *Recency* and *Frequency* of attendance into behavioral segments (e.g., *Elite Members*, *Highly Active*, *At-Risk*, *Hibernating*) to minimize customer churn.
* **Financial Expenses Analytics:** Dynamic visualizations comparing operational staff payroll vs. technical equipment maintenance costs.
* **Attendance Insights:** Visual representation of check-in density across different membership plans.

---

## 🛠 Tech Stack

* **Backend Framework:** Python 3.14 + Flask
* **Data Processing:** Pandas
* **Database Engine:** MySQL (Hosted via Docker)
* **Database Driver:** MySQL Connector/Python (C-Extension)
* **Frontend UI:** HTML5, CSS3, Bootstrap 5 (RTL Support)
* **Data Visualization:** Chart.js

---

## 📁 Project Structure

```text
├── app.py                     # Main Flask Application & BI Dashboard Controller
├── warehouse_etl.py           # Production ETL Pipeline (Isolated Connections Architecture)
├── generate_data.py           # Database Initial Seeding & Core Setup Script
├── etl_process.py             # Historical/Basic ETL Process Script
├── requirements.txt           # Python Project Dependencies
├── index.html             # Homepage & High-Level KPI Summary Card
├── register.html          # New Member Registration Screen
├── attendance.html        # Live Attendance Checking Portal
├── staff.html             # Staff Administration & Payroll System
├── equipment.html         # Equipment Logs & Instant Repair Trigger Portal
└── dashboard.html         # Main Analytical BI Dashboard (Chart.js Integration)
