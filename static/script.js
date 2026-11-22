const subjectSelect = document.getElementById("subject");
const statusSelect = document.getElementById("status");
const preview = document.getElementById("attendance-preview");

function showAttendancePreview() {
    const subject = subjectSelect.selectedOptions[0];
    const attended = Number(subject.dataset.attended);
    const total = Number(subject.dataset.total);
    const present = Number(statusSelect.value);

    const percentage = ((attended + present) / (total + 1)) * 100;
    preview.textContent = "With one more class: " + percentage.toFixed(1) + "%";
}

if (subjectSelect && statusSelect && preview) {
    subjectSelect.addEventListener("change", showAttendancePreview);
    statusSelect.addEventListener("change", showAttendancePreview);
    showAttendancePreview();
}

