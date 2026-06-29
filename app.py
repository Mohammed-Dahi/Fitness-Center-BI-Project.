from flask import Flask, render_template, request, redirect, flash, url_for
from datetime import datetime, timedelta
import mysql.connector
import pandas as pd

app = Flask(__name__)
app.secret_key = 'super_secret_key_for_bi_project'

def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="root_password_123",
        database="fitness_center_db",
        port=3306
    )

@app.route('/')
def index():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True, buffered=True)
    
    cursor.execute("SELECT COUNT(*) AS total_members FROM Members")
    total_members = cursor.fetchone()['total_members']
    
    cursor.execute("SELECT COUNT(*) AS total_attendance FROM Attendance")
    total_attendance = cursor.fetchone()['total_attendance']
    
    cursor.execute("SELECT COUNT(*) AS total_staff FROM Staff")
    total_staff = cursor.fetchone()['total_staff']
    
    cursor.execute("SELECT COUNT(*) AS total_equip FROM Equipment")
    total_equip = cursor.fetchone()['total_equip']
    
    cursor.close()
    conn.close()
    return render_template('index.html', 
                           total_members=total_members, 
                           total_attendance=total_attendance,
                           total_staff=total_staff,
                           total_equip=total_equip)

@app.route('/register', methods=['GET', 'POST'])
def register():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True, buffered=True)
    if request.method == 'POST':
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        gender = request.form['gender']
        plan_id = int(request.form['plan_id'])
        branch_id = int(request.form['branch_id'])
        
        cursor.execute("SELECT duration_days FROM Plans WHERE plan_id = %s", (plan_id,))
        plan = cursor.fetchone()
        
        join_date = datetime.now().date()
        expire_date = join_date + timedelta(days=plan['duration_days'])
        
        cursor.execute("""
            INSERT INTO Members (first_name, last_name, gender, join_date, expire_date, plan_id, branch_id)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (first_name, last_name, gender, join_date, expire_date, plan_id, branch_id))
        conn.commit()
        flash('تم تسجيل العضو الجديد بنجاح!', 'success')
        return redirect(url_for('index'))
        
    cursor.execute("SELECT * FROM Plans")
    plans = cursor.fetchall()
    cursor.execute("SELECT * FROM Branches")
    branches = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('register.html', plans=plans, branches=branches)

@app.route('/attendance', methods=['GET', 'POST'])
def attendance():
    if request.method == 'POST':
        member_id = int(request.form['member_id'])
        branch_id = int(request.form['branch_id'])
        conn = get_db_connection()
        cursor = conn.cursor(buffered=True)
        try:
            cursor.execute("INSERT INTO Attendance (member_id, branch_id) VALUES (%s, %s)", (member_id, branch_id))
            conn.commit()
            flash('تم تسجيل حضور العضو بنجاح تم فتح البوابة!', 'success')
        except mysql.connector.Error as err:
            flash(f'{err.msg}', 'danger')
        finally:
            cursor.close()
            conn.close()
        return redirect(url_for('attendance'))
        
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True, buffered=True)
    cursor.execute("SELECT * FROM Branches")
    branches = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('attendance.html', branches=branches)

@app.route('/staff', methods=['GET', 'POST'])
def staff():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True, buffered=True)
    if request.method == 'POST':
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        role = request.form['role']
        salary = float(request.form['salary'])
        branch_id = int(request.form['branch_id'])
        
        cursor.execute("""
            INSERT INTO Staff (first_name, last_name, role, salary, branch_id)
            VALUES (%s, %s, %s, %s, %s)
        """, (first_name, last_name, role, salary, branch_id))
        conn.commit()
        flash('تم إضافة الموظف بنجاح!', 'success')
        return redirect(url_for('staff'))
        
    cursor.execute("SELECT * FROM Branches")
    branches = cursor.fetchall()
    cursor.execute("SELECT s.*, b.branch_name FROM Staff s JOIN Branches b ON s.branch_id = b.branch_id")
    staff_list = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('staff.html', branches=branches, staff_list=staff_list)

@app.route('/equipment', methods=['GET', 'POST'])
def equipment():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True, buffered=True)
    if request.method == 'POST':
        if 'maintenance_cost' in request.form:
            equipment_id = int(request.form['equipment_id'])
            cost = float(request.form['maintenance_cost'])
            desc = request.form['description']
            cursor.execute("""
                INSERT INTO Maintenance_Logs (equipment_id, maintenance_date, cost, description)
                VALUES (%s, CURDATE(), %s, %s)
            """, (equipment_id, cost, desc))
            conn.commit()
            flash('تم تسجيل الصيانة وتحديث حالة الجهاز تلقائياً عبر الـ Trigger!', 'success')
        else:
            name = request.form['equipment_name']
            status = request.form['status']
            branch_id = int(request.form['branch_id'])
            cursor.execute("INSERT INTO Equipment (equipment_name, status, branch_id) VALUES (%s, %s, %s)", 
                           (name, status, branch_id))
            conn.commit()
            flash('تم إضافة الجهاز الجديد للفرع!', 'success')
        return redirect(url_for('equipment'))
        
    cursor.execute("SELECT * FROM Branches")
    branches = cursor.fetchall()
    cursor.execute("SELECT e.*, b.branch_name FROM Equipment e JOIN Branches b ON e.branch_id = b.branch_id")
    equipment_list = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('equipment.html', branches=branches, equipment_list=equipment_list)

@app.route('/dashboard')
def dashboard():
    conn = get_db_connection()
    
    query_plans = """
        SELECT dp.plan_name, COUNT(fa.fact_id) AS total_attendance
        FROM Fact_Attendance_Analytics fa
        JOIN Dim_Plans_Analytical dp ON fa.plan_key = dp.plan_key
        GROUP BY dp.plan_name
    """
    df_plans = pd.read_sql(query_plans, conn)
    
    query_rfm = """
        SELECT fa.member_key, dm.full_name, fa.attendance_date FROM Fact_Attendance_Analytics fa
        JOIN Dim_Members_Analytical dm ON fa.member_key = dm.member_key
    """
    df_rfm = pd.read_sql(query_rfm, conn)
    segments = {'Elite Member': 0, 'Highly Active': 0, 'Consistent Member': 0, 'At-Risk Member': 0, 'Hibernating': 0, 'Lost Member': 0}
    if not df_rfm.empty:
        current_date = df_rfm['attendance_date'].max()
        rfm = df_rfm.groupby('full_name').agg({'attendance_date': lambda x: (current_date - x.max()).days, 'member_key': 'count'}).reset_index()
        rfm.columns = ['full_name', 'Recency', 'Frequency']
        for _, row in rfm.iterrows():
            if row['Recency'] <= 7 and row['Frequency'] >= 15: segments['Elite Member'] += 1
            elif row['Recency'] <= 7 and row['Frequency'] >= 5: segments['Highly Active'] += 1
            elif row['Recency'] <= 14 and row['Frequency'] >= 2: segments['Consistent Member'] += 1
            elif 14 < row['Recency'] <= 30: segments['At-Risk Member'] += 1
            elif 30 < row['Recency'] <= 60: segments['Hibernating'] += 1
            else: segments['Lost Member'] += 1

    query_costs = "SELECT cost_type, SUM(amount) AS total FROM Fact_Financial_Costs GROUP BY cost_type"
    df_costs = pd.read_sql(query_costs, conn)
    
    conn.close()
   
    plans_labels = df_plans['plan_name'].tolist() if not df_plans.empty else []
    plans_data = df_plans['total_attendance'].tolist() if not df_plans.empty else []
    
    costs_labels = df_costs['cost_type'].tolist() if not df_costs.empty else []
    costs_data = [float(x) for x in df_costs['total'].tolist()] if not df_costs.empty else []
    
    return render_template('dashboard.html', 
                           plans_labels=plans_labels, plans_data=plans_data,
                           rfm_labels=list(segments.keys()), rfm_data=list(segments.values()),
                           costs_labels=costs_labels, costs_data=costs_data)

if __name__ == '__main__':
    app.run(debug=True, port=5000)