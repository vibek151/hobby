document.addEventListener("DOMContentLoaded", function () {

    const params = new URLSearchParams(window.location.search);

    if (!params.get("upgrade")) return;

    const sid = params.get("student_id");

    fetch(`/admin/student_portal/studentadmission/get-student-data/?student_id=${sid}`)
        .then(res => res.json())
        .then(data => {

            function set(name,val){
                const f = document.querySelector(`#id_${name}`);
                if (!f) return;

                f.value = val || "";
                f.readOnly = true;
            }

            set("student_id",data.student_id);
            set("name",data.name);
            set("guardian_name",data.guardian_name);
            set("phone",data.phone);
            set("dob",data.dob);
            set("qualification",data.qualification);
            set("address",data.address);
            
            const gender = document.querySelector("#id_gender");
            if (gender){
                gender.value = data.gender;
                gender.disabled = true;
            }

        });
});


// // fine worked

