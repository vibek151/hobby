document.addEventListener("DOMContentLoaded", function () {

    const courseField = document.getElementById("id_course");
    const amountField = document.getElementById("id_admission_amount");

    courseField.addEventListener("change", function () {

        const text = courseField.options[courseField.selectedIndex].text;

        // Example format: "CCA - 5000"
        const match = text.match(/\d+/);

        if (match) {
            amountField.value = match[0];
        }
    });

});
