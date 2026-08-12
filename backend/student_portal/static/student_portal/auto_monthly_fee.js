document.addEventListener("DOMContentLoaded", function () {

    const courseField = document.getElementById("id_course");
    const typeField = document.getElementById("id_course_type");
    const monthlyField = document.getElementById("id_monthly_fee");

    function updateMonthlyFee(){

        const courseId = courseField.value;
        if (!courseId) return;

        fetch(`/admin/student_portal/studentadmission/get-course-data/?course_id=${courseId}`)
        .then(res => res.json())
        .then(data => {

            let fee = data.monthly_fee || 0;

            // TYPE 2 logic
            if (typeField.value === "TYPE 2"){
                fee = fee * 2;
            }

            if (monthlyField){
                monthlyField.value = fee;
            }

        });
    }

    if(courseField){
        courseField.addEventListener("change", updateMonthlyFee);
    }

    if(typeField){
        typeField.addEventListener("change", updateMonthlyFee);
    }

    // 🔥 Trigger once on load
    if(courseField){
        courseField.dispatchEvent(new Event("change"));
    }

});
