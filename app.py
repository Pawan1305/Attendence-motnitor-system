from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from database import init_db, get_db
from datetime import date, datetime
import sqlite3

app = Flask(__name__)
app.secret_key = 'attendance_secret_key_2024'

@app.before_request
def setup():
    init_db()

# ──────────────────────────── DASHBOARD ────────────────────────────
@app.route('/')
def index():
    db = get_db()
    total_students  = db.execute('SELECT COUNT(*) FROM students').fetchone()[0]
    total_subjects  = db.execute('SELECT COUNT(*) FROM subjects').fetchone()[0]
    today           = date.today().isoformat()
    present_today   = db.execute(
        "SELECT COUNT(*) FROM attendance WHERE date=? AND status='Present'", (today,)
    ).fetchone()[0]

    # Overall attendance %
    total_records = db.execute('SELECT COUNT(*) FROM attendance').fetchone()[0]
    present_records = db.execute(
        "SELECT COUNT(*) FROM attendance WHERE status='Present'"
    ).fetchone()[0]
    overall_pct = round((present_records / total_records * 100), 1) if total_records else 0

    # Recent attendance (last 7 unique dates)
    recent_dates = db.execute(
        "SELECT DISTINCT date FROM attendance ORDER BY date DESC LIMIT 7"
    ).fetchall()
    trend = []
    for row in recent_dates:
        d = row[0]
        p = db.execute(
            "SELECT COUNT(*) FROM attendance WHERE date=? AND status='Present'", (d,)
        ).fetchone()[0]
        t = db.execute(
            "SELECT COUNT(*) FROM attendance WHERE date=?", (d,)
        ).fetchone()[0]
        trend.append({'date': d, 'pct': round(p/t*100, 1) if t else 0})
    trend.reverse()

    return render_template('index.html',
                           total_students=total_students,
                           total_subjects=total_subjects,
                           present_today=present_today,
                           overall_pct=overall_pct,
                           trend=trend,
                           today=today)

# ──────────────────────────── STUDENTS ─────────────────────────────
@app.route('/students')
def students():
    db = get_db()
    rows = db.execute('SELECT * FROM students ORDER BY name').fetchall()
    return render_template('students.html', students=rows)

@app.route('/students/add', methods=['POST'])
def add_student():
    name      = request.form['name'].strip()
    roll_no   = request.form['roll_no'].strip()
    branch    = request.form['branch'].strip()
    semester  = request.form['semester'].strip()

    if not name or not roll_no:
        flash('Name and Roll No are required.', 'danger')
        return redirect(url_for('students'))

    db = get_db()
    try:
        db.execute('INSERT INTO students (name, roll_no, branch, semester) VALUES (?,?,?,?)',
                   (name, roll_no, branch, semester))
        db.commit()
        flash(f'Student "{name}" added successfully.', 'success')
    except sqlite3.IntegrityError:
        flash('Roll No already exists.', 'danger')
    return redirect(url_for('students'))

@app.route('/students/delete/<int:student_id>', methods=['POST'])
def delete_student(student_id):
    db = get_db()
    db.execute('DELETE FROM students WHERE id=?', (student_id,))
    db.execute('DELETE FROM attendance WHERE student_id=?', (student_id,))
    db.commit()
    flash('Student deleted.', 'success')
    return redirect(url_for('students'))

# ──────────────────────────── SUBJECTS ─────────────────────────────
@app.route('/subjects')
def subjects():
    db = get_db()
    rows = db.execute('SELECT * FROM subjects ORDER BY name').fetchall()
    return render_template('subjects.html', subjects=rows)

@app.route('/subjects/add', methods=['POST'])
def add_subject():
    name = request.form['name'].strip()
    code = request.form['code'].strip()
    if not name or not code:
        flash('Name and Code are required.', 'danger')
        return redirect(url_for('subjects'))
    db = get_db()
    try:
        db.execute('INSERT INTO subjects (name, code) VALUES (?,?)', (name, code))
        db.commit()
        flash(f'Subject "{name}" added.', 'success')
    except sqlite3.IntegrityError:
        flash('Subject code already exists.', 'danger')
    return redirect(url_for('subjects'))

@app.route('/subjects/delete/<int:subject_id>', methods=['POST'])
def delete_subject(subject_id):
    db = get_db()
    db.execute('DELETE FROM subjects WHERE id=?', (subject_id,))
    db.execute('DELETE FROM attendance WHERE subject_id=?', (subject_id,))
    db.commit()
    flash('Subject deleted.', 'success')
    return redirect(url_for('subjects'))

# ──────────────────────────── ATTENDANCE ───────────────────────────
@app.route('/attendance')
def attendance():
    db = get_db()
    students_list = db.execute('SELECT * FROM students ORDER BY name').fetchall()
    subjects_list = db.execute('SELECT * FROM subjects ORDER BY name').fetchall()

    selected_subject = request.args.get('subject_id', '')
    selected_date    = request.args.get('date', date.today().isoformat())

    records = []
    if selected_subject:
        records = db.execute(
            '''SELECT a.id, s.name, s.roll_no, a.status
               FROM attendance a JOIN students s ON a.student_id=s.id
               WHERE a.subject_id=? AND a.date=?
               ORDER BY s.name''',
            (selected_subject, selected_date)
        ).fetchall()

    return render_template('attendance.html',
                           students=students_list,
                           subjects=subjects_list,
                           records=records,
                           selected_subject=selected_subject,
                           selected_date=selected_date)

@app.route('/attendance/mark', methods=['POST'])
def mark_attendance():
    subject_id   = request.form['subject_id']
    att_date     = request.form['date']
    student_ids  = request.form.getlist('student_ids')
    statuses     = request.form.getlist('statuses')

    db = get_db()
    # delete existing records for that subject+date, then re-insert
    db.execute('DELETE FROM attendance WHERE subject_id=? AND date=?',
               (subject_id, att_date))
    for sid, status in zip(student_ids, statuses):
        db.execute(
            'INSERT INTO attendance (student_id, subject_id, date, status) VALUES (?,?,?,?)',
            (sid, subject_id, att_date, status)
        )
    db.commit()
    flash(f'Attendance saved for {att_date}.', 'success')
    return redirect(url_for('attendance', subject_id=subject_id, date=att_date))

# ──────────────────────────── PERFORMANCE ──────────────────────────
@app.route('/performance')
def performance():
    db = get_db()
    students_list = db.execute('SELECT * FROM students ORDER BY name').fetchall()
    subjects_list = db.execute('SELECT * FROM subjects ORDER BY name').fetchall()

    selected_subject = request.args.get('subject_id', '')
    report = []

    if selected_subject:
        rows = db.execute(
            '''SELECT s.id, s.name, s.roll_no,
                      COUNT(a.id) as total,
                      SUM(CASE WHEN a.status='Present' THEN 1 ELSE 0 END) as present
               FROM students s
               LEFT JOIN attendance a ON s.id=a.student_id AND a.subject_id=?
               GROUP BY s.id ORDER BY s.name''',
            (selected_subject,)
        ).fetchall()
        for r in rows:
            pct = round(r['present'] / r['total'] * 100, 1) if r['total'] else 0
            grade = compute_grade(pct)
            report.append({
                'id': r['id'],
                'name': r['name'],
                'roll_no': r['roll_no'],
                'total': r['total'],
                'present': r['present'],
                'absent': r['total'] - r['present'],
                'pct': pct,
                'grade': grade,
                'status': 'Safe' if pct >= 75 else ('Warning' if pct >= 60 else 'Critical')
            })

    # Overall report across all subjects
    overall = []
    if not selected_subject:
        rows = db.execute(
            '''SELECT s.id, s.name, s.roll_no,
                      COUNT(a.id) as total,
                      SUM(CASE WHEN a.status='Present' THEN 1 ELSE 0 END) as present
               FROM students s
               LEFT JOIN attendance a ON s.id=a.student_id
               GROUP BY s.id ORDER BY s.name'''
        ).fetchall()
        for r in rows:
            pct = round(r['present'] / r['total'] * 100, 1) if r['total'] else 0
            grade = compute_grade(pct)
            overall.append({
                'id': r['id'],
                'name': r['name'],
                'roll_no': r['roll_no'],
                'total': r['total'],
                'present': r['present'],
                'absent': r['total'] - r['present'],
                'pct': pct,
                'grade': grade,
                'status': 'Safe' if pct >= 75 else ('Warning' if pct >= 60 else 'Critical')
            })

    return render_template('performance.html',
                           students=students_list,
                           subjects=subjects_list,
                           selected_subject=selected_subject,
                           report=report,
                           overall=overall)

def compute_grade(pct):
    if pct >= 90: return 'A+'
    if pct >= 80: return 'A'
    if pct >= 70: return 'B'
    if pct >= 60: return 'C'
    if pct >= 50: return 'D'
    return 'F'

# ──────────────────────────── REPORTS API ──────────────────────────
@app.route('/api/trend')
def api_trend():
    db = get_db()
    subject_id = request.args.get('subject_id', '')
    if subject_id:
        rows = db.execute(
            '''SELECT date,
                      SUM(CASE WHEN status='Present' THEN 1 ELSE 0 END)*100.0/COUNT(*) as pct
               FROM attendance WHERE subject_id=?
               GROUP BY date ORDER BY date''', (subject_id,)
        ).fetchall()
    else:
        rows = db.execute(
            '''SELECT date,
                      SUM(CASE WHEN status='Present' THEN 1 ELSE 0 END)*100.0/COUNT(*) as pct
               FROM attendance GROUP BY date ORDER BY date'''
        ).fetchall()
    return jsonify([{'date': r['date'], 'pct': round(r['pct'], 1)} for r in rows])

if __name__ == '__main__':
    app.run(debug=True)
