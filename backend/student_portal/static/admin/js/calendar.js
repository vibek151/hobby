document.addEventListener("DOMContentLoaded", function () {

    document.querySelectorAll(".litepicker").forEach(function(el){

        new Litepicker({
            element: el,
            format: "YYYY-MM-DD",
            dropdowns: {
                minYear: 1980,
                maxYear: 2050,
                months: true,
                years: true
            }
        });

        // IMPORTANT: show textbox
        el.style.display = "block";
        el.style.visibility = "visible";
        el.removeAttribute("hidden");

    });

});
