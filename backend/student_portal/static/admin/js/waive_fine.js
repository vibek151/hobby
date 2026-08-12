document.addEventListener("DOMContentLoaded", function () {
    const waiveCheckbox = document.querySelector("#id_waive_fine");
    const fineInput = document.querySelector("#id_fine");
    const amountInput = document.querySelector("#id_amount");
    const totalField = document.getElementById("id_total_amount");

    if (!waiveCheckbox || !fineInput || !totalField) return;

    const descriptor = Object.getOwnPropertyDescriptor(HTMLInputElement.prototype, "value");
    const originalSetter = descriptor.set;
    const originalGetter = descriptor.get;

    function updateTotal() {
        const amount = parseFloat(amountInput?.value) || 0;
        const fine = parseFloat(fineInput?.value) || 0;
        // Use the original setter to avoid infinite loops
        originalSetter.call(totalField, (amount + fine).toFixed(2));
    }

    // Define property for Fine Input
    Object.defineProperty(fineInput, "value", {
        get: function() { return originalGetter.call(this); },
        set: function (val) {
            const finalVal = waiveCheckbox.checked ? 0 : val;
            originalSetter.call(this, finalVal);
            updateTotal();
        },
        configurable: true
    });

    function handleWaive() {
        if (waiveCheckbox.checked) {
            fineInput.value = 0; // Trigger the custom setter
            fineInput.readOnly = true;
            fineInput.style.backgroundColor = "#eee";
            fineInput.style.cursor = "not-allowed";
        } else {
            fineInput.readOnly = false;
            fineInput.style.backgroundColor = "";
            fineInput.style.cursor = "auto";
            if (typeof calculateFine === "function") calculateFine();
        }
        updateTotal();
    }

    waiveCheckbox.addEventListener("change", handleWaive);
    amountInput?.addEventListener("input", updateTotal);
    fineInput.addEventListener("input", updateTotal);

    // Initial Sync
    handleWaive();
});