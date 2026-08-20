window.addEventListener("load", function () {

    const classTime = document.getElementById("id_class_time");
    const selectedDays = document.getElementById("id_class_day_to");
    const availableDays = document.getElementById("id_class_day_from");

    function showError(msg) {
        let error = document.getElementById("batch-capacity-error");
        if (!error) {
            error = document.createElement("div");
            error.id = "batch-capacity-error";
            error.style.color = "red";
            error.style.fontWeight = "bold";
            error.style.marginTop = "5px";
            selectedDays.parentNode.appendChild(error);
        }
        error.innerText = msg;
    }

    function clearError() {
        const error = document.getElementById("batch-capacity-error");
        if (error) { error.remove(); }
    }

    function checkCapacity() {
        console.log("CHECK CAPACITY CALLED");
        if (!selectedDays || selectedDays.options.length === 0) {
            return;
        }
        
        if (!classTime.value) {
            clearError();
            return;
        }

        // Always check against the latest added option (the last item in the select box)
        const totalOptions = selectedDays.options.length;
        const currentDay = selectedDays.options[totalOptions - 1];

        console.log("Checking combination -> TIME ID:", classTime.value, "| DAY ID:", currentDay?.value);

        fetch(
            "/admin/student_portal/studentadmission/check-batch-capacity/?" +
            new URLSearchParams({
                class_time: classTime.value,
                batch_day: currentDay?.value,
                capacity: localStorage.getItem("batchCount")
            })
        )
        .then(r => r.json())
        .then(data => {
            console.log("FULL =", data.full);
            console.log("CURRENT DAY =", currentDay);
            if (data.full) {
                // Get display names before wiping them out
                const batchTime = classTime.options[classTime.selectedIndex]?.text || "";
                const batchDay = currentDay?.text || "Selected day group";

                // Revert only the offending option back to available pool
                currentDay.selected = false;
                availableDays.appendChild(currentDay);
                SelectBox.init("id_class_day_from");
                SelectBox.init("id_class_day_to");

                SelectFilter.refresh_icons("id_class_day");

                showError(`${batchDay} (${batchTime}) is already full.`);
            } else {
                clearError();
            }
        })
        .catch(err => console.error("Error validation capacity:", err));
    }

    // Listen for changes on Time dropdown
    if (classTime) {
        classTime.addEventListener("change", function () {
            if (selectedDays.options.length > 0) {
                checkCapacity();
            }
        });
    }

    // Handle both standard selection and common UI click movements
    selectedDays.addEventListener("change", checkCapacity);
    
    // Safety check for Django's filter widgets: intercepting UI movements
    document.addEventListener("click", function (e) {

    console.log("CLICKED:", e.target);

    if (
        e.target.tagName === "OPTION"
    ) {

        console.log("OPTION CLICKED");

        setTimeout(checkCapacity, 100);

    }

});
});