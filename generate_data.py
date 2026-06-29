import mysql.connector

conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="root_password_123",
    database="fitness_center_db",
    port=3306
)

cursor = conn.cursor(dictionary=True, buffered=True)

print("Database connection established successfully.")

branches = [('فرع القاهرة',), ('فرع الجيزة',), ('فرع الإسكندرية',)]
for b in branches:
    cursor.execute("""
        INSERT INTO Branches (branch_name) 
        SELECT %s WHERE NOT EXISTS (SELECT 1 FROM Branches WHERE branch_name = %s)
    """, (b[0], b[0]))

plans = [
    ('الباقة الشهرية', 500.00, 30),
    ('الباقة الربع سنوية', 1200.00, 90),
    ('الباقة السنوية', 400.00, 365)
]
for p in plans:
    cursor.execute("""
        INSERT INTO Plans (plan_name, price, duration_days)
        SELECT %s, %s, %s WHERE NOT EXISTS (SELECT 1 FROM Plans WHERE plan_name = %s)
    """, (p[0], p[1], p[2], p[0]))

conn.commit()
print("Data inserted successfully into Branches and Plans tables.")

cursor.close()
conn.close()