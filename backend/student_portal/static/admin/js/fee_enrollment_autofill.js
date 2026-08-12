console.log("Enrollment AutoFill JS Loaded");

(function () {

    function attachListener() {

        const enrollmentField = document.querySelector('select[name="enrollment"]');
        const amountField = document.getElementById("id_amount");
        const dueField = document.getElementById("id_due_date");

        if (!enrollmentField || !amountField || !dueField) {
            setTimeout(attachListener, 300);
            return;
        }

        // ✅ Detect ADD page only
        const isAddPage = window.location.pathname.endsWith("/add/");

        if (!isAddPage) {
            console.log("Edit page detected — AutoFill disabled.");
            return;
        }

        enrollmentField.addEventListener("change", function () {

            if (!this.value) return;

            const paymentField =
                document.getElementById("id_payment_date");

            const paymentDate =
                paymentField?.value || "";

            console.log(
                "GET MONTHLY FEE DATE =",
                paymentDate
            );

            fetch(
                `/admin/student_portal/fee/get-monthly-fee/?enrollment_id=${this.value}&payment_date=${paymentDate}`
            )
                .then(response => response.json())
                .then(data => {
                    console.log("API DATA:", data);
                    // ✅ Monthly fee autofill
                    

                    // ✅ Next due date from backend
                    if (data.due_date) {
                        dueField.value = data.due_date;
                    }

                })
                .catch(error => console.error("Fetch error:", error));
        });
        // ✅ Auto trigger if enrollment already selected
        // if (enrollmentField.value) {
        //     setTimeout(() => {
        //         enrollmentField.dispatchEvent(new Event("change"));
        //     }, 500);
        // }


    }

    document.addEventListener("DOMContentLoaded", attachListener);

})();