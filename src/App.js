import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './App.css';

const API_BASE_URL = 'http://localhost:5000';

function App() {
  const [students, setStudents] = useState([]);
  const [studentName, setStudentName] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  // Fetch attendance records from backend
  const fetchAttendance = async () => {
    try {
      setLoading(true);
      const response = await axios.get(`${API_BASE_URL}/attendance`);
      setStudents(response.data);
      setError('');
    } catch (err) {
      setError('Failed to fetch attendance data. Make sure the backend is running.');
      console.error('Error fetching attendance:', err);
    } finally {
      setLoading(false);
    }
  };

  // Add new student
  const addStudent = async () => {
    if (!studentName.trim()) {
      setError('Please enter a student name');
      return;
    }

    try {
      setLoading(true);
      await axios.post(`${API_BASE_URL}/attendance`, {
        student_name: studentName.trim(),
        status: 'present'
      });
      setStudentName('');
      await fetchAttendance();
      setError('');
    } catch (err) {
      setError('Failed to add student. Please try again.');
      console.error('Error adding student:', err);
    } finally {
      setLoading(false);
    }
  };

  // Mark attendance (present or absent)
  const markAttendance = async (studentName, status) => {
    try {
      setLoading(true);
      await axios.post(`${API_BASE_URL}/attendance`, {
        student_name: studentName,
        status: status
      });
      await fetchAttendance();
      setError('');
    } catch (err) {
      setError('Failed to mark attendance. Please try again.');
      console.error('Error marking attendance:', err);
    } finally {
      setLoading(false);
    }
  };

  // Get attendance percentage for a student
  const getAttendancePercentage = async (studentName) => {
    try {
      const response = await axios.get(`${API_BASE_URL}/attendance/percentage/${studentName}`);
      return response.data.percentage;
    } catch (err) {
      console.error('Error getting attendance percentage:', err);
      return 0;
    }
  };

  useEffect(() => {
    fetchAttendance();
  }, []);

  // Group students by name and calculate stats
  const studentStats = students.reduce((acc, record) => {
    if (!acc[record.student_name]) {
      acc[record.student_name] = {
        name: record.student_name,
        present: 0,
        absent: 0,
        total: 0
      };
    }
    
    if (record.status === 'present') {
      acc[record.student_name].present++;
    } else {
      acc[record.student_name].absent++;
    }
    acc[record.student_name].total++;
    
    return acc;
  }, {});

  const studentList = Object.values(studentStats);

  return (
    <div className="App">
      <div className="container">
        <h1>Attendance Tracker</h1>
        
        {error && <div className="error-message">{error}</div>}
        
        <div className="input-section">
          <input
            type="text"
            value={studentName}
            onChange={(e) => setStudentName(e.target.value)}
            placeholder="Enter Student Name"
            onKeyPress={(e) => e.key === 'Enter' && addStudent()}
          />
          <button onClick={addStudent} disabled={loading}>
            {loading ? 'Adding...' : 'Add Student'}
          </button>
        </div>

        <div className="attendance-section">
          <h2>Student Attendance</h2>
          {loading && <div className="loading">Loading...</div>}
          
          {studentList.length === 0 && !loading ? (
            <p>No students added yet. Add a student to get started!</p>
          ) : (
            <table className="attendance-table">
              <thead>
                <tr>
                  <th>Student Name</th>
                  <th>Present</th>
                  <th>Absent</th>
                  <th>Total Classes</th>
                  <th>Attendance %</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {studentList.map((student) => {
                  const percentage = student.total > 0 
                    ? ((student.present / student.total) * 100).toFixed(2) 
                    : 0;
                  
                  return (
                    <tr key={student.name}>
                      <td>{student.name}</td>
                      <td>{student.present}</td>
                      <td>{student.absent}</td>
                      <td>{student.total}</td>
                      <td>{percentage}%</td>
                      <td>
                        <button
                          className="action-btn present-btn"
                          onClick={() => markAttendance(student.name, 'present')}
                          disabled={loading}
                        >
                          ✅ Present
                        </button>
                        <button
                          className="action-btn absent-btn"
                          onClick={() => markAttendance(student.name, 'absent')}
                          disabled={loading}
                        >
                          ❌ Absent
                        </button>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          )}
        </div>
      </div>
    </div>
  );
}

export default App;