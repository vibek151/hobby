document.addEventListener("DOMContentLoaded", function () {

    function updateDuration() {
        let courseSelect = document.querySelector("#id_course");
        let typeSelect = document.querySelector("#id_course_type");
        let durationField = document.querySelector("#id_course_duration");

        if (!courseSelect || !typeSelect || !durationField) return;

        let selected = courseSelect.options[courseSelect.selectedIndex].text;

        // Extract duration from course name if you show it
        // OR manually define durations here

        let baseDuration = 6; // default months

        if (selected.includes("3")) baseDuration = 3;
        if (selected.includes("6")) baseDuration = 6;
        if (selected.includes("12")) baseDuration = 12;

        if (typeSelect.value === "TYPE2") {
            durationField.value = baseDuration / 2;
        } else {
            durationField.value = baseDuration;
        }
    }

    document.querySelector("#id_course")?.addEventListener("change", updateDuration);
    document.querySelector("#id_course_type")?.addEventListener("change", updateDuration);
});
