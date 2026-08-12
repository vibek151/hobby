django.jQuery(document).ready(function(){

    console.log("Auto Duration Running ✅");

    let baseDuration = 0;
    let baseFees = 0;

    function loadCourseData(){

        let courseId = django.jQuery("#id_course").val();
        if(!courseId) return;

        fetch("/admin/student_portal/studentadmission/get-course-data/?course_id=" + courseId)
        .then(response => response.json())
        .then(data => {

            baseDuration = parseFloat(data.duration) || 0;
            baseFees = (parseFloat(data.monthly_fee) || 0) * baseDuration;

            applyCalculation();
        });
    }

    function applyCalculation(){

        if(!baseDuration) return;

        let type = django.jQuery("#id_course_type").val();
        let duration = baseDuration;

        if(type === "TYPE 2"){
            duration = baseDuration / 2;
        }

        let monthly = baseFees / duration;

        django.jQuery("#id_course_duration").val(duration);
        django.jQuery("#id_monthly_fee").val(monthly.toFixed(2));
    }

    django.jQuery(document).on("change", "#id_course", loadCourseData);
    django.jQuery(document).on("change", "#id_course_type", applyCalculation);

});
