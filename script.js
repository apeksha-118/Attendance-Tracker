document.addEventListener("DOMContentLoaded", loadSubjects);

function addSubject() {
    let subjectInput = document.getElementById("subjectInput");
    let subjectName = subjectInput.value.trim();

    if (subjectName === "") {
        alert("Please enter a subject name.");
        return;
    }

    let subjects = JSON.parse(localStorage.getItem("subjects")) || [];

    // Check if subject already exists
    let existingSubject = subjects.find(sub => sub.name.toLowerCase() === subjectName.toLowerCase());

    if (existingSubject) {
        alert("Subject already exists.");
        return;
    }

    subjects.push({ name: subjectName, present: 0, absent: 0 });
    localStorage.setItem("subjects", JSON.stringify(subjects));

    subjectInput.value = "";
    loadSubjects();
}

function loadSubjects() {
    let subjects = JSON.parse(localStorage.getItem("subjects")) || [];
    let tableBody = document.getElementById("attendanceTable");
    tableBody.innerHTML = "";

    subjects.forEach((subject, index) => {
        let totalClasses = subject.present + subject.absent;
        let attendancePercentage = totalClasses > 0
            ? ((subject.present / totalClasses) * 100).toFixed(2) + "%"
            : "0%";

        let row = `<tr>
            <td>${subject.name}</td>
            <td>${subject.present}</td>
            <td>${subject.absent}</td>
            <td>${totalClasses}</td>
            <td>${attendancePercentage}</td>
            <td>
                <button class="action-btn present" onclick="markAttendance(${index}, 'present')">✅</button>
                <button class="action-btn absent" onclick="markAttendance(${index}, 'absent')">❌</button>
                <button class="action-btn delete" onclick="deleteSubject(${index})">🗑</button>
            </td>
        </tr>`;

        tableBody.innerHTML += row;
    });
}

function markAttendance(index, type) {
    let subjects = JSON.parse(localStorage.getItem("subjects")) || [];

    let today = new Date().toISOString().split('T')[0]; // Get current date (YYYY-MM-DD)
    let attendanceLog = JSON.parse(localStorage.getItem("attendanceLog")) || {};

    if (!attendanceLog[today]) {
        attendanceLog[today] = {};
    }

    if (!attendanceLog[today][index]) {
        attendanceLog[today][index] = { present: 0, absent: 0 };
    }

    if (type === "present") {
        subjects[index].present += 1;
        attendanceLog[today][index].present += 1;
    } else {
        subjects[index].absent += 1;
        attendanceLog[today][index].absent += 1;
    }

    localStorage.setItem("subjects", JSON.stringify(subjects));
    localStorage.setItem("attendanceLog", JSON.stringify(attendanceLog));
    loadSubjects();
}

function deleteSubject(index) {
    let subjects = JSON.parse(localStorage.getItem("subjects")) || [];
    subjects.splice(index, 1);
    localStorage.setItem("subjects", JSON.stringify(subjects));
    loadSubjects();
}
