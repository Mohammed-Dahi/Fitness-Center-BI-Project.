import mysql.connector

conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="root_password_123",
    database="fitness_center_db",
    port=3306
)

cursor = conn.cursor(dictionary=True, buffered=True)

print("Starting ETL process for Dim_Plans_Analytical table...")

cursor.execute("SELECT plan_id, plan_name, price FROM Plans")
plans = cursor.fetchall()
for p in plans:
    cursor.execute("""
        INSERT INTO Dim_Plans_Analytical (plan_id, plan_name, price)
        SELECT %s, %s, %s WHERE NOT EXISTS (SELECT 1 FROM Dim_Plans_Analytical WHERE plan_id = %s)
    """, (p['plan_id'], p['plan_name'], p['price'], p['plan_id']))

conn.commit()
print("Successfully updated Dim_Plans_Analytical table with new plans.")

cursor.close()
conn.close()