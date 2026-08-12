document.addEventListener("DOMContentLoaded", function () {

    const admission = document.getElementById("id_admission_amount");
    const advance = document.getElementById("id_advance_fees");
    const discount = document.getElementById("id_discount_percent");
    const finalAmt = document.getElementById("id_final_amount");

    function calculate() {
        let a = parseFloat(admission.value) || 0;
        let adv = parseFloat(advance.value) || 0;
        let d = parseFloat(discount.value) || 0;

        let result = a - (a * d / 100) - adv;
        finalAmt.value = result.toFixed(2);
    }

    admission.addEventListener("input", calculate);
    advance.addEventListener("input", calculate);
    discount.addEventListener("input", calculate);
});
