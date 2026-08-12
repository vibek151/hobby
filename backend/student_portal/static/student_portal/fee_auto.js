document.addEventListener("DOMContentLoaded", function () {
    const studentField = document.querySelector("#id_student");
    const monthlyField = document.querySelector("#id_monthly_fee");

    studentField.addEventListener("change", function () {
        fetch(`/admin/student_portal/studentadmission/get-course-data/?student_id=${this.value}`)
            .then(res => res.json())
            .then(data => {
                if(data.monthly_fee){
                    monthlyField.value = data.monthly_fee;
                }
            });
    });
});
