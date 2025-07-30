from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3
import datetime
import os

app = Flask(__name__)
CORS(app)  # Enable CORS for React frontend

# Database setup
DATABASE = 'attendance.db'

def init_db():
    """Initialize the SQLite database with attendance table"""
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    
    # Create attendance table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS attendance (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_name TEXT NOT NULL,
            status TEXT NOT NULL CHECK (status IN ('present', 'absent')),
            date TEXT NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    conn.close()

def get_db_connection():
    """Get database connection"""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/attendance', methods=['GET'])
def get_attendance():
    """Get all attendance records"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT student_name, status, date, timestamp
            FROM attendance
            ORDER BY timestamp DESC
        ''')
        
        records = cursor.fetchall()
        conn.close()
        
        # Convert to list of dictionaries
        attendance_data = []
        for record in records:
            attendance_data.append({
                'student_name': record['student_name'],
                'status': record['status'],
                'date': record['date'],
                'timestamp': record['timestamp']
            })
        
        return jsonify(attendance_data), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/attendance', methods=['POST'])
def add_attendance():
    """Add new attendance record"""
    try:
        data = request.get_json()
        
        if not data or 'student_name' not in data or 'status' not in data:
            return jsonify({'error': 'Missing required fields: student_name, status'}), 400
        
        student_name = data['student_name'].strip()
        status = data['status'].lower()
        
        if not student_name:
            return jsonify({'error': 'Student name cannot be empty'}), 400
        
        if status not in ['present', 'absent']:
            return jsonify({'error': 'Status must be either "present" or "absent"'}), 400
        
        # Use current date if not provided
        date = data.get('date', datetime.date.today().isoformat())
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO attendance (student_name, status, date)
            VALUES (?, ?, ?)
        ''', (student_name, status, date))
        
        conn.commit()
        record_id = cursor.lastrowid
        conn.close()
        
        return jsonify({
            'message': 'Attendance recorded successfully',
            'id': record_id,
            'student_name': student_name,
            'status': status,
            'date': date
        }), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/attendance/percentage/<student_name>', methods=['GET'])
def get_attendance_percentage(student_name):
    """Calculate attendance percentage for a specific student"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get total present and absent count for the student
        cursor.execute('''
            SELECT 
                status,
                COUNT(*) as count
            FROM attendance 
            WHERE student_name = ?
            GROUP BY status
        ''', (student_name,))
        
        results = cursor.fetchall()
        conn.close()
        
        present_count = 0
        absent_count = 0
        
        for result in results:
            if result['status'] == 'present':
                present_count = result['count']
            elif result['status'] == 'absent':
                absent_count = result['count']
        
        total_count = present_count + absent_count
        
        if total_count == 0:
            percentage = 0
        else:
            percentage = round((present_count / total_count) * 100, 2)
        
        return jsonify({
            'student_name': student_name,
            'present': present_count,
            'absent': absent_count,
            'total': total_count,
            'percentage': percentage
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/attendance/summary', methods=['GET'])
def get_attendance_summary():
    """Get attendance summary for all students"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT 
                student_name,
                status,
                COUNT(*) as count
            FROM attendance 
            GROUP BY student_name, status
            ORDER BY student_name
        ''')
        
        results = cursor.fetchall()
        conn.close()
        
        # Organize data by student
        summary = {}
        for result in results:
            student_name = result['student_name']
            if student_name not in summary:
                summary[student_name] = {'present': 0, 'absent': 0}
            
            summary[student_name][result['status']] = result['count']
        
        # Calculate percentages
        summary_data = []
        for student_name, counts in summary.items():
            total = counts['present'] + counts['absent']
            percentage = round((counts['present'] / total) * 100, 2) if total > 0 else 0
            
            summary_data.append({
                'student_name': student_name,
                'present': counts['present'],
                'absent': counts['absent'],
                'total': total,
                'percentage': percentage
            })
        
        return jsonify(summary_data), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'message': 'Attendance Tracker API is running'}), 200

if __name__ == '__main__':
    # Initialize database when app starts
    init_db()
    print("Attendance Tracker API starting...")
    print("Database initialized successfully")
    app.run(debug=True, host='0.0.0.0', port=5000)