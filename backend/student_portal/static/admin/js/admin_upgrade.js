document.addEventListener("DOMContentLoaded", function () {
    const params = new URLSearchParams(window.location.search);
    if (!params.get("upgrade")) return;

    const sid = params.get("student_id");

    // 1. DATA PRE-FILL LOGIC (HOLDING EVERYTHING)
    fetch(`/admin/student_portal/studentadmission/get-student-data/?student_id=${sid}`)
        .then(res => res.json())
        .then(data => {
            function set(name, val) {
                const f = document.querySelector(`#id_${name}`);
                if (!f) return;
                f.value = val || "";
                f.readOnly = true;
                f.style.backgroundColor = "#f5f5f5";
            }

            function setSelect(name, val) {
                const f = document.querySelector(`#id_${name}`);
                if (!f) return;
                f.value = val;
                f.disabled = true; 
                f.style.backgroundColor = "#f5f5f5";
            }

            // Holding Personal & Documents
            set("student_id", data.student_id);
            set("name", data.name);
            set("guardian_name", data.guardian_name);
            set("phone", data.phone);
            set("dob", data.dob);
            set("qualification", data.qualification);
            set("address", data.address);
            setSelect("gender", data.gender);
            setSelect("document_type", data.document_type);
            set("document_number", data.document_number);

            // Holding Fees & Payment
            set("monthly_fee", data.monthly_fee);
            set("admission_amount", data.admission_amount);
            set("discount_percent", data.discount_percent);
            set("advance_fees", data.advance_fees);
            set("final_amount", data.final_amount);
            set("receipt_no", data.receipt_no);
            set("admission_date", data.admission_date);
            setSelect("admission_pay_via", data.admission_pay_via);
            
            // NOTE: Course Details are NOT set, so they remain empty
        });

    // 2. EYE BUTTON LOGIC (FIXES DOUBLE EYE BUG)
    document.querySelectorAll('input[type="file"]').forEach(input => {
        // Only add a button if one doesn't exist yet
        if (input.nextElementSibling && input.nextElementSibling.classList.contains('preview-eye-btn')) {
            return; 
        }

        let btn = document.createElement("button");
        btn.type = "button";
        btn.innerHTML = "👁️";
        btn.className = "preview-eye-btn";
        btn.style.marginLeft = "5px";

        btn.onclick = function() {
            let row = input.closest(".form-row");
            let link = row.querySelector("a");
            let url = (input.files && input.files[0]) ? URL.createObjectURL(input.files[0]) : (link ? link.href : null);
            
            if (!url) return alert("No file to preview");

            let viewer = window.open("", "_blank", "width=800,height=900");
            viewer.document.write(`
                <html><body style="margin:0;background:black;display:flex;justify-content:center;align-items:center;height:100vh;">
                    <img src="${url}" style="max-width:100%; max-height:100%; object-fit:contain;">
                </body></html>`);
            viewer.document.close();
        };
        input.after(btn);
    });

    // 3. ENABLE FIELDS ON SUBMIT
    const form = document.querySelector('form');
    if (form) {
        form.addEventListener('submit', () => {
            form.querySelectorAll(':disabled').forEach(el => el.disabled = false);
        });
    }
});