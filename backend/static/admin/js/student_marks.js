document.addEventListener(
    "DOMContentLoaded",
    function () {

        let franchise =
            document.querySelector(
                "#id_franchise"
            );

        let student =
            document.querySelector(
                "#id_student"
            );

        if (
            !franchise ||
            !student
        ) {
            return;
        }

        student.innerHTML =
            '<option value="">---------</option>';

        student.disabled = true;   // ← ADD THIS


        franchise.addEventListener(
            "change",
            function () {

                let id =
                    this.value;

                if (!id) {

                    student.innerHTML =
                        '<option value="">---------</option>';

                    student.disabled = true;   // ← KEEP THIS

                    return;
                }

                student.innerHTML =
                    '<option>Loading...</option>';

                fetch(
                    "/admin/management_portal/studentmarks/students-by-franchise/?franchise=" + id
                )

                .then(
                    response => response.json()
                )

                .then(
                    data => {

                        student.innerHTML =
                            '<option value="">---------</option>';

                        data.forEach(
                            function (s) {

                                student.innerHTML +=
                                    `<option value="${s.id}">
                                        ${s.name}
                                    </option>`;
                            }
                        );

                        student.disabled = false;   // ← ADD THIS

                    }
                );

            }
        );

    }
);