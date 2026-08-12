// document.addEventListener("DOMContentLoaded", function () {

//     const courseField = document.getElementById("id_course");
//     const admissionField = document.getElementById("id_admission_amount");

//     function fillAdmissionFee() {

//         const selected = courseField.options[courseField.selectedIndex];

//         // Django admin stores data-value in option text
//         const text = selected.text;

//         // Format: CODE - NAME (₹FEE)
//         const match = text.match(/\((\d+(\.\d+)?)\)$/);

//         if (match) {
//             admissionField.value = match[1];
//         }
//     }

//     courseField.addEventListener("change", fillAdmissionFee);
// });

document.addEventListener("DOMContentLoaded", function () {

    const course = document.getElementById("id_course");
    const admission = document.getElementById("id_admission_amount");

    function handleAdmission() {

        // If no course → clear field
        if (!course.value) {
            admission.value = "";
            return;
        }

        // If course selected → fetch fee
        fetch(`/admin/student_portal/studentadmission/get-course-data/?course_id=${course.value}`)
            .then(res => res.json())
            .then(data => {
                if (data.admission_fee) {
                    admission.value = data.admission_fee;
                }
            });
    }

    // Run when dropdown changes
    course.addEventListener("change", handleAdmission);

    // ⭐ IMPORTANT: Run once on page load
    handleAdmission();

});

