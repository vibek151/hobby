document.addEventListener("DOMContentLoaded", function () {

    const input = document.querySelector('input[type="file"][name="passport_photo"]');

    if (!input) return;

    // create preview box
    const previewBox = document.createElement("div");
    previewBox.style.position = "fixed";
    previewBox.style.right = "120px";
    previewBox.style.top = "150px";
    previewBox.style.width = "130px";
    previewBox.style.height = "160px";
    previewBox.style.border = "1px solid #ccc";
    previewBox.style.background = "#fafafa";
    previewBox.style.display = "flex";
    previewBox.style.alignItems = "center";
    previewBox.style.justifyContent = "center";

    const img = document.createElement("img");
    img.style.maxWidth = "120px";
    img.style.maxHeight = "150px";
    img.style.objectFit = "cover";

    previewBox.appendChild(img);
    document.body.appendChild(previewBox);

    input.addEventListener("change", function (event) {

        const file = event.target.files[0];

        if (!file) return;

        const reader = new FileReader();

        reader.onload = function (e) {
            img.src = e.target.result;
        };

        reader.readAsDataURL(file);
    });

});