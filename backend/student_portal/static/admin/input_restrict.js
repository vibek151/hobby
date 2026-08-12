document.addEventListener("DOMContentLoaded", function () {

    // =========================
    // LETTERS ONLY
    // =========================
    function lettersOnly(fieldId) {
        const field = document.getElementById(fieldId);
        if (!field) return;

        field.addEventListener("keypress", function (e) {
            const char = String.fromCharCode(e.which);
            if (!/[a-zA-Z\s]/.test(char)) {
                e.preventDefault();
            }
        });
    }

    // =========================
    // PHONE VALIDATION
    // =========================
    function phoneValidation(fieldId) {
        const field = document.getElementById(fieldId);
        if (!field) return;

        field.addEventListener("input", function () {
            this.value = this.value.replace(/\D/g, "").slice(0, 10);
        });
    }
    
    

    // Apply
    lettersOnly("id_name");
    lettersOnly("id_guardian_name");
    phoneValidation("id_phone");

});

document.addEventListener("DOMContentLoaded", function () {

    const docType = document.getElementById("id_document_type");
    const docNumber = document.getElementById("id_document_number");
    const receipt = document.getElementById("id_receipt_no");

    // ==============================
    // Aadhaar Restriction
    // ==============================
    function applyAadhaarRestriction() {

        if (!docType || !docNumber) return;

        if (docType.value === "AADHAAR") {

            docNumber.setAttribute("maxlength", "12");

            docNumber.addEventListener("input", function () {
                // remove non-numbers
                this.value = this.value.replace(/\D/g, "");

                // limit to 12 digits
                if (this.value.length > 12) {
                    this.value = this.value.slice(0, 12);
                }
            });

        } else {
            docNumber.removeAttribute("maxlength");
        }
    }

    if (docType) {
        docType.addEventListener("change", applyAadhaarRestriction);
        applyAadhaarRestriction(); // run on page load
    }

    // ==============================
    // Receipt Number Restriction
    // ==============================
    if (receipt) {
        receipt.addEventListener("input", function () {
            this.value = this.value.replace(/\D/g, "");
        });
    }

});


document.addEventListener("DOMContentLoaded", function () {

    const receiptField = document.getElementById("id_receipt_no");

    if (receiptField) {

        receiptField.addEventListener("input", function () {
            // Remove anything that is not a number
            this.value = this.value.replace(/\D/g, "");
        });

    }

});
