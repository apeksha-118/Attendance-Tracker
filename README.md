# Attendance Tracker

An Attendance Tracker application designed to help students follow up on their attendance. The project features a React frontend along with a Python Flask backend that uses SQLite to store attendance records.

## Features

- **Student Management**: Add students to the attendance system
- **Attendance Tracking**: Mark students as present or absent
- **Real-time Calculations**: View attendance percentages calculated dynamically
- **Data Persistence**: All records are stored in SQLite database
- **RESTful API**: Backend provides clean API endpoints for attendance management
- **Responsive Design**: Modern, mobile-friendly user interface

## Project Structure

```
attendance-tracker/
├── README.md                 # Project overview and setup instructions
├── package.json             # React app dependencies and scripts
├── public/
│   └── index.html           # Base HTML file for React frontend
├── src/
│   ├── index.js             # Entry point for React app
│   ├── App.js               # Main component with attendance functionality
│   └── App.css              # Styling for the React components
└── backend/
    ├── app.py               # Flask backend with SQLite setup and API endpoints
    └── requirements.txt     # Python dependencies
```

## Technology Stack

### Frontend
- **React 18**: Modern JavaScript library for building user interfaces
- **Axios**: HTTP client for API communication
- **CSS3**: Custom styling with responsive design

### Backend
- **Flask**: Lightweight Python web framework
- **SQLite**: Embedded database for data persistence
- **Flask-CORS**: Cross-Origin Resource Sharing support

## Setup Instructions

### Prerequisites
- Node.js (v14 or higher)
- Python 3.7 or higher
- npm or yarn package manager

### Backend Setup

1. Navigate to the backend directory:
   ```bash
   cd backend
   ```

2. Create a virtual environment (recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Start the Flask backend:
   ```bash
   python app.py
   ```

   The backend will be available at `http://localhost:5000`

### Frontend Setup

1. In a new terminal, navigate to the project root directory:
   ```bash
   cd attendance-tracker
   ```

2. Install Node.js dependencies:
   ```bash
   npm install
   ```

3. Start the React development server:
   ```bash
   npm start
   ```

   The frontend will be available at `http://localhost:3000`

## API Endpoints

### GET /attendance
Retrieve all attendance records
```json
[
  {
    "student_name": "John Doe",
    "status": "present",
    "date": "2024-01-15",
    "timestamp": "2024-01-15 10:30:00"
  }
]
```

### POST /attendance
Add a new attendance record
```json
{
  "student_name": "John Doe",
  "status": "present",
  "date": "2024-01-15"
}
```

### GET /attendance/percentage/{student_name}
Get attendance percentage for a specific student
```json
{
  "student_name": "John Doe",
  "present": 18,
  "absent": 2,
  "total": 20,
  "percentage": 90.0
}
```

### GET /attendance/summary
Get attendance summary for all students
```json
[
  {
    "student_name": "John Doe",
    "present": 18,
    "absent": 2,
    "total": 20,
    "percentage": 90.0
  }
]
```

### GET /health
Health check endpoint
```json
{
  "status": "healthy",
  "message": "Attendance Tracker API is running"
}
```

## Usage

1. **Adding Students**: Enter a student name in the input field and click "Add Student"
2. **Marking Attendance**: Use the "Present" (✅) or "Absent" (❌) buttons for each student
3. **Viewing Statistics**: Attendance percentages are calculated and displayed in real-time
4. **Data Persistence**: All records are automatically saved to the SQLite database

## Database Schema

The application uses a single `attendance` table with the following structure:

```sql
CREATE TABLE attendance (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_name TEXT NOT NULL,
    status TEXT NOT NULL CHECK (status IN ('present', 'absent')),
    date TEXT NOT NULL,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

## Development

### Running Tests
```bash
npm test
```

### Building for Production
```bash
npm run build
```

### Code Style
The project follows standard React and Python conventions. The React app uses functional components with hooks.

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/new-feature`)
3. Commit your changes (`git commit -am 'Add new feature'`)
4. Push to the branch (`git push origin feature/new-feature`)
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

If you encounter any issues or have questions, please open an issue on GitHub.