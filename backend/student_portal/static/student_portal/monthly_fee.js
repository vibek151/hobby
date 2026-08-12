// // document.addEventListener("DOMContentLoaded", function () {

// //     console.log("JS Loaded ✅");

// //     const course = document.getElementById("id_course");
// //     const type = document.getElementById("id_course_type");
// //     const monthly = document.getElementById("id_monthly_fee");

// //     let baseFee = 0;

// //     function fetchFee() {
// //         if (!course.value) return;

// //         fetch(`/admin/student_portal/studentadmission/get-course-data/?course_id=${course.value}`)
// //             .then(res => res.json())
// //             .then(data => {
// //                 console.log("API Data:", data);

// //                 baseFee = data.monthly_fee || 0;
// //                 applyType();
// //             });
// //     }

// //     function applyType() {
// //         let fee = baseFee;

// //         if (type.value === "TYPE 2") {
// //             fee = baseFee * 2;
// //         }

// //         monthly.value = fee.toFixed(2);
// //     }

// //     course.addEventListener("change", fetchFee);
// //     type.addEventListener("change", applyType);

// // });
// document.addEventListener("DOMContentLoaded", function () {

//     const course = document.getElementById("id_course");
//     const type = document.getElementById("id_course_type");
//     const monthly = document.getElementById("id_monthly_fee");
//     const admission = document.getElementById("id_admission_amount");
//     const finalAmt = document.getElementById("id_final_amount");

//     let baseFee = 0;

//     function clearFields() {
//         monthly.value = "";
//         admission.value = "";
//         finalAmt.value = "";
//     }

//     function fetchFee() {

//         // 🚨 NO COURSE SELECTED
//         if (!course.value) {
//             clearFields();
//             return;
//         }

//         fetch(`/admin/student_portal/studentadmission/get-course-data/?course_id=${course.value}`)
//             .then(res => res.json())
//             .then(data => {

//                 baseFee = parseFloat(data.monthly_fee) || 0;

//                 let fee = baseFee;

//                 if (type.value === "TYPE 2") {
//                     fee = baseFee * 2;
//                 }

//                 monthly.value = fee.toFixed(2);

//                 // fill admission fee
//                 if (data.admission_fee) {
//                     admission.value = data.admission_fee;
//                 }
//             });
//     }

//     course.addEventListener("change", fetchFee);
//     type.addEventListener("change", fetchFee);

//     // ⭐ RUN ON PAGE LOAD
//     fetchFee();
// });
document.addEventListener("DOMContentLoaded", function () {

    const course = document.getElementById("id_course");
    const type = document.getElementById("id_course_type");
    const monthly = document.getElementById("id_monthly_fee");
    const admission = document.getElementById("id_admission_amount");

    let baseFee = 0;

    // ⭐ detect ADD page
    const isAddPage = window.location.href.includes("/add/");

    function fetchFee() {

        if (!course.value) return;

        fetch(`/admin/student_portal/studentadmission/get-course-data/?course_id=${course.value}`)
            .then(res => res.json())
            .then(data => {

                baseFee = parseFloat(data.monthly_fee) || 0;

                let fee = baseFee;

                if (type.value === "TYPE 2") {
                    fee = baseFee * 2;
                }

                monthly.value = fee.toFixed(2);

                if (data.admission_fee) {
                    admission.value = data.admission_fee;
                }
            });
    }

    // ONLY auto-run on ADD page
    if (isAddPage) {
        monthly.value = "";
        admission.value = "";
    }

    course.addEventListener("change", fetchFee);
    type.addEventListener("change", fetchFee);

});

