


document.addEventListener("DOMContentLoaded", function () {

    console.log("🔥 JS LOADED");

    const isEditPage = window.location.pathname.includes("/change/");

    const courseSelect = document.querySelector("#id_course");
    const typeSelect = document.querySelector("#id_course_type");

    const admissionInput = document.querySelector("#id_admission_amount");
    const discountInput = document.querySelector("#id_discount_percent");
    const advanceInput = document.querySelector("#id_advance_fees");

    const durationInput = document.querySelector("#id_course_duration");
    const monthlyInput = document.querySelector("#id_monthly_fee");
    const finalInput = document.querySelector("#id_final_amount");

    let baseDuration = null;
    let baseMonthly = null;

    // =========================
    // MAKE ADMISSION READONLY
    // =========================
    if (admissionInput){
        admissionInput.setAttribute("readonly", true);
        admissionInput.style.backgroundColor = "#eee";
        admissionInput.style.cursor = "not-allowed";
    }

    // =========================
    // UPDATE UI
    // =========================
    function updateUI() {

        // 🔥 fallback if fetch not completed yet
        if (baseDuration === null || baseMonthly === null) {
            return;
        }

        const type = typeSelect?.value || "TYPE 1";

        const adm = parseFloat(admissionInput?.value) || 0;
        const disc = parseFloat(discountInput?.value) || 0;
        const adv = parseFloat(advanceInput?.value) || 0;

        let currentDuration = baseDuration;
        let currentMonthly = baseMonthly;

        if (type === "TYPE 2" || type === "Type 2") {
            currentDuration = Math.floor(baseDuration / 2);
            currentMonthly = baseMonthly * 2;
        }

        const discountAmt = adm * (disc / 100);
        const finalVal = (adm - discountAmt) - adv;

        if (durationInput) durationInput.value = currentDuration;
        if (monthlyInput) monthlyInput.value = currentMonthly.toFixed(2);
        if (finalInput) finalInput.value = finalVal.toFixed(2);

        // readonly display update
        const durationDisp = document.querySelector(".field-course_duration .readonly");
        const monthlyDisp = document.querySelector(".field-monthly_fee .readonly");
        const finalDisp = document.querySelector(".field-final_amount .readonly");

        if (durationDisp) durationDisp.textContent = currentDuration;
        if (monthlyDisp) monthlyDisp.textContent = currentMonthly.toFixed(2);
        if (finalDisp) finalDisp.textContent = finalVal.toFixed(2);
    }

    // =========================
    // LOAD COURSE DATA (SOURCE OF TRUTH)
    // =========================
    function loadCourseData(courseId){

        fetch(`/admin/student_portal/studentadmission/get-course-data/?course_id=${courseId}`)
            .then(res => res.json())
            .then(data => {

                if (!data.duration) return;

                baseDuration = parseInt(data.duration) || 0;
                baseMonthly = parseFloat(data.monthly_fee) || 0;

                // Set admission fee
                if (admissionInput){
                    admissionInput.value = data.admission_fee || 0;
                }

                console.log("📥 Loaded Base:", baseDuration, baseMonthly);

                updateUI();
            })
            .catch(()=>console.log("❌ Course load failed"));
    }

    // =========================
    // COURSE CHANGE
    // =========================
    if (courseSelect){
        courseSelect.addEventListener("change", function (){
            if (!this.value) return;
            loadCourseData(this.value);
        });
    }

    // =========================
    // TYPE + LIVE INPUT LISTENERS
    // =========================
    [typeSelect, admissionInput, discountInput, advanceInput].forEach(el=>{
        if (el){
            el.addEventListener("change", updateUI);
            el.addEventListener("input", updateUI);
        }
    });

    // =========================
    // INITIAL LOAD (ADD + EDIT FIX)
    // =========================
    if (courseSelect && courseSelect.value){

        if (isEditPage) {
            // Try to fetch fresh base (best & consistent)
            loadCourseData(courseSelect.value);
        } else {
            loadCourseData(courseSelect.value);
        }
    }

});

