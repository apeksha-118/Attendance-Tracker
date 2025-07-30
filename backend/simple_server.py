#!/usr/bin/env python3
"""
Simplified Flask Backend for Attendance Tracker
This version creates a basic HTTP server using Python's built-in modules
since Flask package installation is facing network issues.
"""

import json
import sqlite3
import datetime
import urllib.parse
from http.server import HTTPServer, BaseHTTPRequestHandler
import os

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

def add_cors_headers(handler):
    """Add CORS headers to response"""
    handler.send_header('Access-Control-Allow-Origin', '*')
    handler.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
    handler.send_header('Access-Control-Allow-Headers', 'Content-Type')

class AttendanceHandler(BaseHTTPRequestHandler):
    
    def do_OPTIONS(self):
        """Handle preflight CORS requests"""
        self.send_response(200)
        add_cors_headers(self)
        self.end_headers()
    
    def do_GET(self):
        """Handle GET requests"""
        try:
            if self.path == '/attendance':
                self.get_attendance()
            elif self.path.startswith('/attendance/percentage/'):
                student_name = self.path.split('/')[-1]
                student_name = urllib.parse.unquote(student_name)
                self.get_attendance_percentage(student_name)
            elif self.path == '/attendance/summary':
                self.get_attendance_summary()
            elif self.path == '/health':
                self.health_check()
            else:
                self.send_error(404, "Endpoint not found")
        except Exception as e:
            self.send_error(500, str(e))
    
    def do_POST(self):
        """Handle POST requests"""
        try:
            if self.path == '/attendance':
                self.add_attendance()
            else:
                self.send_error(404, "Endpoint not found")
        except Exception as e:
            self.send_error(500, str(e))
    
    def get_attendance(self):
        """Get all attendance records"""
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
        
        self.send_response(200)
        add_cors_headers(self)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(attendance_data).encode())
    
    def add_attendance(self):
        """Add new attendance record"""
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        data = json.loads(post_data.decode())
        
        if not data or 'student_name' not in data or 'status' not in data:
            self.send_error(400, 'Missing required fields: student_name, status')
            return
        
        student_name = data['student_name'].strip()
        status = data['status'].lower()
        
        if not student_name:
            self.send_error(400, 'Student name cannot be empty')
            return
        
        if status not in ['present', 'absent']:
            self.send_error(400, 'Status must be either "present" or "absent"')
            return
        
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
        
        response_data = {
            'message': 'Attendance recorded successfully',
            'id': record_id,
            'student_name': student_name,
            'status': status,
            'date': date
        }
        
        self.send_response(201)
        add_cors_headers(self)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(response_data).encode())
    
    def get_attendance_percentage(self, student_name):
        """Calculate attendance percentage for a specific student"""
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
        
        response_data = {
            'student_name': student_name,
            'present': present_count,
            'absent': absent_count,
            'total': total_count,
            'percentage': percentage
        }
        
        self.send_response(200)
        add_cors_headers(self)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(response_data).encode())
    
    def get_attendance_summary(self):
        """Get attendance summary for all students"""
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
        
        self.send_response(200)
        add_cors_headers(self)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(summary_data).encode())
    
    def health_check(self):
        """Health check endpoint"""
        response_data = {
            'status': 'healthy',
            'message': 'Attendance Tracker API is running'
        }
        
        self.send_response(200)
        add_cors_headers(self)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(response_data).encode())

def main():
    # Initialize database
    init_db()
    print("Attendance Tracker API starting...")
    print("Database initialized successfully")
    
    # Start server
    server_address = ('', 5000)
    httpd = HTTPServer(server_address, AttendanceHandler)
    print("Server running on http://localhost:5000")
    print("Endpoints available:")
    print("  GET  /health")
    print("  GET  /attendance")
    print("  POST /attendance")
    print("  GET  /attendance/percentage/<student_name>")
    print("  GET  /attendance/summary")
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down server...")
        httpd.shutdown()

if __name__ == '__main__':
    main()