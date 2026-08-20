console.log("Fee JS Loaded");

document.addEventListener("DOMContentLoaded", function () {

    const enrollmentField = document.getElementById("id_enrollment");
    const amountField = document.getElementById("id_amount");
    const dueField = document.getElementById("id_due_date");
    const paymentField = document.getElementById("id_payment_date");
    const fineField = document.getElementById("id_fine");
    const totalField = document.getElementById("id_total_amount");

    if (!enrollmentField || !amountField || !paymentField || !dueField || !fineField) {
        console.log("Required fields not found");
        return;
    }

    fineField.readOnly = true;
    
    if (totalField) totalField.readOnly = true;
    amountField.addEventListener("input", function () {
        amountField.dataset.manualEdit = "true";
    });
    // =========================================
    // Enrollment Change → Load Monthly Fee + Due Date
    // =========================================
    function handleEnrollmentChange() {

        const enrollmentId = enrollmentField.value;
        const paymentDate = paymentField.value;

        if (!enrollmentId) return;

        console.log(
            "GET MONTHLY FEE DATE =",
            paymentDate
        );

        fetch(
            `/admin/student_portal/fee/get-monthly-fee/?enrollment_id=${enrollmentId}&payment_date=${paymentDate}`
        )
            .then(response => response.json())
            .then(data => {

                if (data.monthly_fee !== undefined && !amountField.dataset.manualEdit) {
                    amountField.value = parseFloat(data.monthly_fee || 0).toFixed(2);
                }

                // if (data.next_due_date) {
                //     dueField.value = data.next_due_date;
                // }

                if (data.due_date) {
                    dueField.value = data.due_date;
                }

                console.log("RUNNING BACKEND FEE API");
                calculateFine();
            })
            .catch(error => {
                console.error("Enrollment Fetch Error:", error);
            });
    }

    enrollmentField.addEventListener("change", handleEnrollmentChange);

    if (window.django && django.jQuery) {
        django.jQuery("#id_enrollment").on("select2:select", handleEnrollmentChange);
    }

    // =========================================
    // Fine Calculation
    // =========================================
    function calculateFine() {

        console.log("CALCULATE FINE RUNNING");
        console.log("NEW JS VERSION RUNNING");

        const enrollmentId = enrollmentField.value;
        const paymentDate = paymentField.value;

        console.log(
            "FETCH URL:",
            `/student/calculate-fee/?enrollment_id=${enrollmentId}&payment_date=${paymentDate}`
        );

        if (!enrollmentId || !paymentDate) return;

        fetch(`/student/calculate-fee/?enrollment_id=${enrollmentId}&payment_date=${paymentDate}`)

            .then(response => {
                console.log("API STATUS:", response.status);
                return response.json();
            })

            .then(data => {

                console.log("API DATA:", data);

                if (!amountField.dataset.manualEdit) {
                    amountField.value = parseFloat(
                        data.monthly_fee || data.amount || 0
                    ).toFixed(2);
                }
                
                fineField.value = parseFloat(data.fine || 0).toFixed(2);
                updateTotal();
              
                if (data.due_date) {
                    dueField.value = data.due_date;
                }
            })

            .catch(error => {
                console.error("Fee Calculation Error:", error);
            });
    }

    // =========================================
    // Total Calculation
    // =========================================
    function updateTotal() {

        if (!totalField) return;

        const amount = parseFloat(amountField.value || 0);
        const fine = parseFloat(fineField.value || 0);

        totalField.value = (amount + fine).toFixed(2);
    }

    // =========================================
    // Real-time Watchers
    // =========================================
    function refreshFee() {

        console.log(
            "PAYMENT DATE CHANGED:",
            paymentField.value
        );

        fineField.value = "";

        handleEnrollmentChange();
    }

    paymentField.addEventListener(
        "input",
        refreshFee
    );

    paymentField.addEventListener(
        "change",
        refreshFee
    );
    
    paymentField.addEventListener("change", () => {

        console.log(
            "PAYMENT DATE CHANGED:",
            paymentField.value
        );

        amountField.dataset.manualEdit = "";

        handleEnrollmentChange();

    });

    let lastDate = paymentField.value;

    setInterval(() => {

        if (paymentField.value !== lastDate) {

            lastDate = paymentField.value;

            console.log(
                "DATE WATCHER:",
                lastDate
            );

            handleEnrollmentChange();
        }

    }, 500);
    

    // Fallback watcher (Django-safe)
    // setInterval(calculateFine, 500);

    // Run once on load
    // Run once after admin fully loads
    setTimeout(() => {
        if (enrollmentField.value) {
            handleEnrollmentChange();
        } else {
            calculateFine();
        }
    }, 800);
});
