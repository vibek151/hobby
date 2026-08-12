// document.addEventListener('DOMContentLoaded', function() {
//     // Select all relevant fields
//     const courseSelect = document.querySelector('#id_course');
//     const courseTypeSelect = document.querySelector('#id_course_type');
//     const durationInput = document.querySelector('#id_course_duration');
//     const monthlyFeeInput = document.querySelector('#id_monthly_fee');
//     const admissionAmountInput = document.querySelector('#id_admission_amount');
//     const advanceFeesInput = document.querySelector('#id_advance_fees');
//     const discountInput = document.querySelector('#id_discount_percent');
//     const finalAmountInput = document.querySelector('#id_final_amount');

//     function updateCalculations() {
//         const courseId = courseSelect.value;
//         if (!courseId) return;

//         // Fetch using the exact API path
//         fetch(`/admin/student_portal/studentadmission/get-course-data/?course_id=${courseId}`)
//             .then(response => response.json())
//             .then(data => {
//                 // MATCHING YOUR CONSOLE DATA
//                 // data.duration = 8, data.monthly_fee = 450, data.admission_fee = 1000
//                 const baseDuration = parseInt(data.duration) || 0;
//                 const baseMonthly = parseFloat(data.monthly_fee) || 0; // Fixed key name
//                 const baseAdmission = parseFloat(data.admission_fee) || 0;

//                 // 1. Duration Logic (Halve if Type 2)
//                 let finalDuration = baseDuration;
//                 if (courseTypeSelect.value === "TYPE 2") {
//                     finalDuration = Math.floor(baseDuration / 2);
//                 }
//                 durationInput.value = finalDuration;

//                 // 2. Monthly Fee Logic (Double if Type 2)
//                 let finalMonthly = baseMonthly;
//                 if (courseTypeSelect.value === "TYPE 2") {
//                     finalMonthly = baseMonthly * 2;
//                 }
//                 monthlyFeeInput.value = finalMonthly.toFixed(2);

//                 // 3. Final Amount Logic (Admission - Discount - Advance)
//                 let currentAdmission = parseFloat(admissionAmountInput.value) || 0;
//                 if (currentAdmission === 0) {
//                     currentAdmission = baseAdmission;
//                     admissionAmountInput.value = baseAdmission.toFixed(2);
//                 }

//                 const discountPct = parseFloat(discountInput.value) || 0;
//                 const advance = parseFloat(advanceFeesInput.value) || 0;
//                 const discountVal = (currentAdmission * discountPct) / 100;
                
//                 const finalCalc = currentAdmission - discountVal - advance;
//                 finalAmountInput.value = finalCalc.toFixed(2);

//                 console.log(`Updated UI: Monthly=${finalMonthly}, Duration=${finalDuration}`);
//             })
//             .catch(err => console.error("Error:", err));
//     }

//     if (courseSelect) {
//         courseSelect.addEventListener('change', updateCalculations);
//         courseTypeSelect.addEventListener('change', updateCalculations);
//         [admissionAmountInput, advanceFeesInput, discountInput].forEach(el => {
//             if (el) el.addEventListener('input', updateCalculations);
//         });
//     }
// });

// from here
// document.addEventListener('DOMContentLoaded', function() {
//     const courseSelect = document.querySelector('#id_course');
//     const courseTypeSelect = document.querySelector('#id_course_type');
//     const durationInput = document.querySelector('#id_course_duration');
//     const monthlyFeeInput = document.querySelector('#id_monthly_fee');
//     const admissionAmountInput = document.querySelector('#id_admission_amount');
//     const advanceFeesInput = document.querySelector('#id_advance_fees');
//     const discountInput = document.querySelector('#id_discount_percent');
//     const finalAmountInput = document.querySelector('#id_final_amount');

//     function updateCalculations() {
//         const courseId = courseSelect.value;

//         // --- NEW RESET LOGIC ---
//         // If no course is selected, clear all numeric fields and stop
//         if (!courseId || courseId === "" || courseId === "---------") {
//             durationInput.value = "";
//             monthlyFeeInput.value = "";
//             admissionAmountInput.value = "";
//             finalAmountInput.value = "";
//             console.log("Course cleared. Fields reset to blank.");
//             return; 
//         }

//         // Proceed with fetch if a course is selected
//         fetch(`/admin/student_portal/studentadmission/get-course-data/?course_id=${courseId}`)
//             .then(response => response.json())
//             .then(data => {
//                 const baseDuration = parseInt(data.duration) || 0;
//                 const baseMonthly = parseFloat(data.monthly_fee) || 0;
//                 const baseAdmission = parseFloat(data.admission_fee) || 0;

//                 // 1. Duration Logic (Halve if Type 2)
//                 let finalDuration = baseDuration;
//                 if (courseTypeSelect.value === "TYPE 2") {
//                     finalDuration = Math.floor(baseDuration / 2);
//                 }
//                 durationInput.value = finalDuration;

//                 // 2. Monthly Fee Logic (Double if Type 2)
//                 let finalMonthly = baseMonthly;
//                 if (courseTypeSelect.value === "TYPE 2") {
//                     finalMonthly = baseMonthly * 2;
//                 }
//                 monthlyFeeInput.value = finalMonthly.toFixed(2);

//                 // 3. Final Amount Logic
//                 let currentAdmission = parseFloat(admissionAmountInput.value) || 0;
//                 if (currentAdmission === 0 || isNaN(currentAdmission)) {
//                     currentAdmission = baseAdmission;
//                     admissionAmountInput.value = baseAdmission.toFixed(2);
//                 }

//                 const discountPct = parseFloat(discountInput.value) || 0;
//                 const advance = parseFloat(advanceFeesInput.value) || 0;
//                 const discountVal = (currentAdmission * discountPct) / 100;
                
//                 finalAmountInput.value = (currentAdmission - discountVal - advance).toFixed(2);
//             })
//             .catch(err => console.error("Error:", err));
//     }

//     if (courseSelect) {
//         courseSelect.addEventListener('change', updateCalculations);
//         courseTypeSelect.addEventListener('change', updateCalculations);
//         [admissionAmountInput, advanceFeesInput, discountInput].forEach(el => {
//             if (el) el.addEventListener('input', updateCalculations);
//         });
//     }
// });

// // 22.02.2026

document.addEventListener('DOMContentLoaded', function() {

    // Detect which page we are on
    const isUpgradePage = document.querySelector('#id_new_course') !== null;

    const courseSelect = isUpgradePage
        ? document.querySelector('#id_new_course')
        : document.querySelector('#id_course');

    const oldCourseSelect = document.querySelector('#id_old_course');

    const courseTypeSelect = document.querySelector('#id_course_type');
    const durationInput = document.querySelector('#id_course_duration');
    const monthlyFeeInput = document.querySelector('#id_monthly_fee');

    const admissionAmountInput = document.querySelector('#id_admission_amount');
    const advanceFeesInput = document.querySelector('#id_advance_fees');
    const discountInput = document.querySelector('#id_discount_percent');
    const finalAmountInput = document.querySelector('#id_final_amount');

    if (!courseSelect || !courseTypeSelect) return;

    function updateCalculations() {

        const courseId = courseSelect.value;

        // Prevent same course in Upgrade page
        if (isUpgradePage && oldCourseSelect && oldCourseSelect.value === courseId) {
            alert("New course cannot be the same as old course.");
            courseSelect.value = "";
            return;
        }

        if (!courseId || courseId === "" || courseId === "---------") {
            if (durationInput) durationInput.value = "";
            if (monthlyFeeInput) monthlyFeeInput.value = "";
            if (!isUpgradePage) {
                if (admissionAmountInput) admissionAmountInput.value = "";
                if (finalAmountInput) finalAmountInput.value = "";
            }
            return;
        }

        fetch(`/admin/student_portal/studentadmission/get-course-data/?course_id=${courseId}`)
            .then(response => response.json())
            .then(data => {

                const baseDuration = parseInt(data.duration) || 0;
                const baseMonthly = parseFloat(data.monthly_fee) || 0;
                const baseAdmission = parseFloat(data.admission_fee) || 0;

                // TYPE LOGIC
                let finalDuration = baseDuration;
                let finalMonthly = baseMonthly;

                if (courseTypeSelect.value === "TYPE 2") {
                    finalDuration = Math.floor(baseDuration / 2);
                    finalMonthly = baseMonthly * 2;
                }

                if (durationInput) durationInput.value = finalDuration;
                if (monthlyFeeInput) monthlyFeeInput.value = finalMonthly.toFixed(2);

                // Only run admission logic on StudentAdmission page
                if (!isUpgradePage && admissionAmountInput && finalAmountInput) {

                    let currentAdmission = parseFloat(admissionAmountInput.value) || 0;

                    if (currentAdmission === 0 || isNaN(currentAdmission)) {
                        currentAdmission = baseAdmission;
                        admissionAmountInput.value = baseAdmission.toFixed(2);
                    }

                    const discountPct = parseFloat(discountInput?.value) || 0;
                    const advance = parseFloat(advanceFeesInput?.value) || 0;
                    const discountVal = (currentAdmission * discountPct) / 100;

                    finalAmountInput.value =
                        (currentAdmission - discountVal - advance).toFixed(2);
                }

            })
            .catch(err => console.error("Error:", err));
    }

    courseSelect.addEventListener('change', updateCalculations);
    courseTypeSelect.addEventListener('change', updateCalculations);

    if (!isUpgradePage) {
        [admissionAmountInput, advanceFeesInput, discountInput].forEach(el => {
            if (el) el.addEventListener('input', updateCalculations);
        });
    }

});