// document.addEventListener("DOMContentLoaded", function() {
//     // Check if the URL contains 'upgrade'
//     if (window.location.href.includes('upgrade')) {
        
//         const allRows = document.querySelectorAll('.form-row');

//         allRows.forEach(row => {
//             // Define fields that SHOULD remain editable
//             const isEditableField = row.classList.contains('field-course') || 
//                                     row.classList.contains('field-course_type') || 
//                                     row.classList.contains('field-class_time') || 
//                                     row.classList.contains('field-class_day') ||
//                                     row.classList.contains('field-monthly_fee');

//             if (!isEditableField) {
//                 const inputs = row.querySelectorAll('input, select, textarea');
//                 inputs.forEach(input => {
//                     // Disable File uploads and Dropdowns to prevent changes
//                     if (input.type === 'file' || input.tagName === 'SELECT') {
//                         input.disabled = true; 
//                     } else {
//                         // Use readOnly for text/date to keep them prefilled but locked
//                         input.readOnly = true;
//                     }

//                     // Visual cues for the user
//                     input.style.backgroundColor = "#f0f0f0";
//                     input.style.cursor = "not-allowed";
//                 });
//             }
//         });

//         // CRITICAL FIX: Re-enable fields on Save so Django receives the prefilled data
//         const form = document.querySelector('form'); 
//         if (form) {
//             form.addEventListener('submit', function() {
//                 form.querySelectorAll('select, input').forEach(input => {
//                     input.disabled = false;
//                 });
//             });
//         }
        
//         console.log("Upgrade Mode: Details locked except Course Info and Monthly Fee.");
//     }
// });





document.addEventListener("DOMContentLoaded", function() {
    if (window.location.href.includes('upgrade')) {
        
        // Target all rows
        const allRows = document.querySelectorAll('.form-row');

        allRows.forEach(row => {
            // Fields we want to keep EDITABLE
            const isEditable = row.classList.contains('field-course') || 
                              row.classList.contains('field-course_type') || 
                              row.classList.contains('field-class_time') || 
                              row.classList.contains('field-class_day') ||
                              row.classList.contains('field-monthly_fee');

            if (!isEditable) {
                const inputs = row.querySelectorAll('input, select, textarea');
                inputs.forEach(input => {
                    // Lock dropdowns and file pickers
                    if (input.tagName === 'SELECT' || input.type === 'file') {
                        input.disabled = true; 
                    } else {
                        // Lock text and date boxes
                        input.readOnly = true;
                    }
                    
                    // Visual "Locked" style
                    input.style.backgroundColor = "#f0f0f0";
                    input.style.cursor = "not-allowed";
                });
            }
        });

        // This prevents the "This field is required" error on Save
        const form = document.querySelector('form');
        if (form) {
            form.addEventListener('submit', function() {
                form.querySelectorAll(':disabled').forEach(input => {
                    input.disabled = false;
                });
            });
        }
    }
});