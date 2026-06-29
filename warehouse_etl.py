import mysql.connector


read_conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="root_password_123",
    database="fitness_center_db",
    port=3306
)

write_conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="root_password_123",
    database="fitness_center_db",
    port=3306
)

read_cursor = read_conn.cursor(dictionary=True, buffered=True)
write_cursor = write_conn.cursor(dictionary=True, buffered=True)

print("Running the ETL via fully isolted connections")

read_cursor.execute("SELECT plan_id, plan_name, price FROM Plans")
plans = read_cursor.fetchall()
for p in plans:
    write_cursor.execute("""
        INSERT INTO Dim_Plans_Analytical (plan_id, plan_name, price)
        SELECT %s, %s, %s WHERE NOT EXISTS (SELECT 1 FROM Dim_Plans_Analytical WHERE plan_id = %s)
    """, (p['plan_id'], p['plan_name'], p['price'], p['plan_id']))


read_cursor.execute("""
    SELECT m.member_id, m.first_name, m.last_name, m.gender, m.join_date, b.branch_name 
    FROM Members m JOIN Branches b ON m.branch_id = b.branch_id
""")
members = read_cursor.fetchall()
for m in members:
    full_name = f"{m['first_name']} {m['last_name']}"
    write_cursor.execute("""
        INSERT INTO Dim_Members_Analytical (member_id, full_name, gender, join_date, branch_name)
        SELECT %s, %s, %s, %s, %s WHERE NOT EXISTS (SELECT 1 FROM Dim_Members_Analytical WHERE member_id = %s)
    """, (m['member_id'], full_name, m['gender'], m['join_date'], m['branch_name'], m['member_id']))


read_cursor.execute("""
    SELECT s.staff_id, s.first_name, s.last_name, s.role, s.salary, b.branch_name 
    FROM Staff s JOIN Branches b ON s.branch_id = b.branch_id
""")
staff_members = read_cursor.fetchall()
for s in staff_members:
    full_name = f"{s['first_name']} {s['last_name']}"
    write_cursor.execute("""
        INSERT INTO Dim_Staff_Analytical (staff_id, full_name, role, salary, branch_name)
        SELECT %s, %s, %s, %s, %s WHERE NOT EXISTS (SELECT 1 FROM Dim_Staff_Analytical WHERE staff_id = %s)
    """, (s['staff_id'], full_name, s['role'], s['salary'], s['branch_name'], s['staff_id']))

write_conn.commit()
print("All dimension tables have been updated successfully.")

read_cursor.execute("""
    SELECT dm.member_key, dp.plan_key, a.attendance_date FROM Attendance a
    JOIN Members m ON a.member_id = m.member_id
    JOIN Dim_Members_Analytical dm ON m.member_id = dm.member_id
    JOIN Dim_Plans_Analytical dp ON m.plan_id = dp.plan_id
""")
attendance_records = read_cursor.fetchall()

write_cursor.execute("SET FOREIGN_KEY_CHECKS = 0;")
write_cursor.execute("TRUNCATE TABLE Fact_Attendance_Analytics;")
write_cursor.execute("SET FOREIGN_KEY_CHECKS = 1;")

for row in attendance_records:
    write_cursor.execute("INSERT INTO Fact_Attendance_Analytics (member_key, plan_key, attendance_date) VALUES (%s, %s, %s)", 
                         (row['member_key'], row['plan_key'], row['attendance_date']))

write_cursor.execute("SET FOREIGN_KEY_CHECKS = 0;")
write_cursor.execute("TRUNCATE TABLE Fact_Financial_Costs;")
write_cursor.execute("SET FOREIGN_KEY_CHECKS = 1;")

read_cursor.execute("""
    SELECT b.branch_name, s.salary FROM Staff s 
    JOIN Branches b ON s.branch_id = b.branch_id
""")
salaries = read_cursor.fetchall()
for sal in salaries:
    write_cursor.execute("""
        INSERT INTO Fact_Financial_Costs (branch_name, cost_type, amount, record_date)
        VALUES (%s, 'Salary', %s, CURDATE())
    """, (sal['branch_name'], sal['salary']))

read_cursor.execute("""
    SELECT b.branch_name, ml.cost, ml.maintenance_date FROM Maintenance_Logs ml
    JOIN Equipment e ON ml.equipment_id = e.equipment_id
    JOIN Branches b ON e.branch_id = b.branch_id
""")
maintenances = read_cursor.fetchall()
for maint in maintenances:
    write_cursor.execute("""
        INSERT INTO Fact_Financial_Costs (branch_name, cost_type, amount, record_date)
        VALUES (%s, 'Equipment Maintenance', %s, %s)
    """, (maint['branch_name'], maint['cost'], maint['maintenance_date']))

write_conn.commit()
print("All fact tables have been updated successfully.")

read_cursor.close()
write_cursor.close()
read_conn.close()
write_conn.close()