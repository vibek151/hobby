
// document.addEventListener("DOMContentLoaded", function () {

//     document.querySelectorAll('input[type="file"]').forEach(function (input) {

//         let btn = document.createElement("button");
//         btn.type = "button";
//         btn.innerHTML = "🙈";
//         btn.className = "preview-eye-btn";
//         btn.style.marginLeft = "6px";

//         input.after(btn);

//         // ✅ Find SAME FIELD ROW
//         let row = input.closest(".form-row");

//         let existingLink = null;
//         if (row){
//             let links = row.querySelectorAll("a[href]");
//             links.forEach(l => {
//                 if (l.textContent.includes("/") || l.href.includes("/media/")){
//                     existingLink = l;
//                 }
//             });
//         }

//         // If file exists → open eye
//         if (existingLink){
//             btn.innerHTML = "👁️";
//         }

//         // On new file select
//         input.addEventListener("change", function () {
//             if (input.files.length > 0){
//                 btn.innerHTML = "👁️";
//             } else if (!existingLink){
//                 btn.innerHTML = "🙈";
//             }
//         });

//         // Preview click
//         btn.onclick = function () {

//             let url = null;

//             // New file selected
//             if (input.files.length > 0){
//                 url = URL.createObjectURL(input.files[0]);
//             }
//             // Existing file
//             else{
//                 let row = input.closest(".form-row");
//                 let link = row ? row.querySelector("a[href]") : null;

//                 if (link){
//                     url = link.href;
//                 }
//             }

//             if (!url){
//                 alert("No file available");
//                 return;
//             }
//         let w = screen.width * 0.5;
//         let h = screen.height * 0.9;
//         window.open(
//                 url,
//                 "_blank",
//                 `width=${w},height=${h},resizable=yes,scrollbars=yes`
//             );

//         viewer.document.write(`
//         <!DOCTYPE html>
//         <html>
//         <head>
//         <title>Preview</title>
//         <style>
//         body{
//             margin:0;
//             background:black;
//             display:flex;
//             justify-content:center;
//             align-items:center;
//             height:100vh;
//         }
//         img, embed{
//             max-width:100%;
//             max-height:100%;
//         }
//         </style>
//         </head>
//         <body>
//         ${
//         url.match(/\.(jpg|jpeg|png|gif|webp)$/i)
//         ? `<img src="${url}">`
//         : `<embed src="${url}" type="application/pdf" width="100%" height="100%">`
//         }
//         </body>
//         </html>
//         `);
//         viewer.document.close();


//                 };

//             });

//         });






document.addEventListener("DOMContentLoaded", function () {

    // ============================================================
    // FILE INPUTS
    // ============================================================

    document.querySelectorAll('input[type="file"]').forEach(function (input) {

        // --------------------------------------------------------
        // PREVIEW BUTTON
        // --------------------------------------------------------

        let btn = document.createElement("button");

        btn.type = "button";
        btn.innerHTML = "🙈";
        btn.className = "preview-eye-btn";
        btn.style.marginLeft = "6px";

        input.after(btn);


        // --------------------------------------------------------
        // EXISTING FILE
        // --------------------------------------------------------

        let row = input.closest(".form-row");
        let existingLink = null;

        if (row) {

            let links = row.querySelectorAll("a[href]");

            links.forEach(function (l) {

                if (
                    l.textContent.includes("/") ||
                    l.href.includes("/media/")
                ) {
                    existingLink = l;
                }

            });
        }


        if (existingLink) {
            btn.innerHTML = "👁️";
        }


        // --------------------------------------------------------
        // NEW FILE SELECTED
        // --------------------------------------------------------

        input.addEventListener("change", function () {

            if (!input.files.length) {

                if (!existingLink) {
                    btn.innerHTML = "🙈";
                }

                return;
            }

            btn.innerHTML = "👁️";

            const file = input.files[0];

            // Crop only images
            if (file.type.startsWith("image/")) {
                openCropEditor(input, file, btn);
            }

        });


        // --------------------------------------------------------
        // PREVIEW
        // --------------------------------------------------------

        btn.onclick = function () {

            let url = null;

            if (input.files.length > 0) {

                url = URL.createObjectURL(
                    input.files[0]
                );

            } else {

                let currentRow =
                    input.closest(".form-row");

                let link =
                    currentRow
                        ? currentRow.querySelector("a[href]")
                        : null;

                if (link) {
                    url = link.href;
                }

            }


            if (!url) {

                alert("No file available");

                return;

            }


            let w = screen.width * 0.5;
            let h = screen.height * 0.9;


            let viewer = window.open(
                "",
                "_blank",
                `width=${w},height=${h},resizable=yes,scrollbars=yes`
            );


            if (!viewer) {

                alert(
                    "Popup blocked. Please allow popups for this site."
                );

                return;

            }


            viewer.document.write(`
                <!DOCTYPE html>

                <html>

                <head>

                    <title>Preview</title>

                    <style>

                        body {
                            margin: 0;
                            background: black;
                            display: flex;
                            justify-content: center;
                            align-items: center;
                            height: 100vh;
                        }

                        img,
                        embed {
                            max-width: 100%;
                            max-height: 100%;
                        }

                    </style>

                </head>

                <body>

                    ${
                        url.match(
                            /\.(jpg|jpeg|png|gif|webp)$/i
                        )
                        ?
                        `<img src="${url}">`
                        :
                        `<embed
                            src="${url}"
                            type="application/pdf"
                            width="100%"
                            height="100%"
                        >`
                    }

                </body>

                </html>
            `);

            viewer.document.close();

        };

    });



    // ============================================================
    // CROP EDITOR
    // ============================================================

    function openCropEditor(input, file, previewButton) {

        const imageURL =
            URL.createObjectURL(file);


        const overlay =
            document.createElement("div");

        overlay.className =
            "smart-crop-overlay";


        overlay.innerHTML = `

            <div class="smart-crop-modal">

                <div class="smart-crop-header">

                    <strong>Crop Image</strong>

                    <button
                        type="button"
                        class="smart-crop-close"
                    >
                        ×
                    </button>

                </div>


                <div class="smart-crop-workspace">

                    <div class="smart-crop-image-area">

                        <img
                            class="smart-crop-image"
                            src="${imageURL}"
                        >

                        <div class="smart-crop-box">

                            <div
                                class="crop-resize-handle"
                            ></div>

                        </div>

                    </div>

                </div>


                <div class="smart-crop-controls">

                    <!-- TARGET FILE SIZE -->

                    <div class="smart-control-row">

                        <label>
                            Target file size
                        </label>

                        <input
                            type="number"
                            class="smart-target-size"
                            value="500"
                            min="10"
                            max="10000"
                        >

                        <select
                            class="smart-target-unit"
                        >

                            <option value="KB">
                                KB
                            </option>

                            <option value="MB">
                                MB
                            </option>

                        </select>

                    </div>


                    <!-- RENAME -->

                    <div class="smart-control-row">

                        <label>
                            Rename
                        </label>

                        <input
                            type="text"
                            class="smart-file-name"
                        >

                    </div>

                </div>


                <div class="smart-crop-footer">

                    <button
                        type="button"
                        class="smart-cancel"
                    >
                        Cancel
                    </button>

                    <button
                        type="button"
                        class="smart-crop-upload"
                    >
                        Crop & Upload
                    </button>

                </div>

            </div>

        `;


        document.body.appendChild(overlay);


        // ========================================================
        // ELEMENTS
        // ========================================================

        const img =
            overlay.querySelector(
                ".smart-crop-image"
            );

        const cropBox =
            overlay.querySelector(
                ".smart-crop-box"
            );

        const resizeHandle =
            overlay.querySelector(
                ".crop-resize-handle"
            );

        const targetInput =
            overlay.querySelector(
                ".smart-target-size"
            );

        const targetUnit =
            overlay.querySelector(
                ".smart-target-unit"
            );

        const nameInput =
            overlay.querySelector(
                ".smart-file-name"
            );

        const closeButton =
            overlay.querySelector(
                ".smart-crop-close"
            );

        const cancelButton =
            overlay.querySelector(
                ".smart-cancel"
            );

        const cropButton =
            overlay.querySelector(
                ".smart-crop-upload"
            );


        // ========================================================
        // DEFAULT FILE NAME
        // ========================================================

        let originalName =
            file.name.replace(
                /\.[^/.]+$/,
                ""
            );

        nameInput.value =
            originalName;


        // ========================================================
        // CROP VARIABLES
        // ========================================================

        let imageWidth = 0;
        let imageHeight = 0;

        // IMPORTANT:
        // Width and height are completely independent.

        let cropWidth = 200;
        let cropHeight = 200;

        let cropX = 0;
        let cropY = 0;


        // Moving
        let dragging = false;

        let dragStartX = 0;
        let dragStartY = 0;

        let initialCropX = 0;
        let initialCropY = 0;


        // Resizing
        let resizing = false;

        let resizeStartX = 0;
        let resizeStartY = 0;

        let initialCropWidth = 0;
        let initialCropHeight = 0;


        // ========================================================
        // IMAGE LOADED
        // ========================================================

        img.onload = function () {

            imageWidth =
                img.clientWidth;

            imageHeight =
                img.clientHeight;


            cropWidth =
                Math.min(
                    imageWidth,
                    imageHeight
                ) * 0.65;


            cropHeight =
                Math.min(
                    imageWidth,
                    imageHeight
                ) * 0.65;


            cropX =
                (imageWidth - cropWidth) / 2;


            cropY =
                (imageHeight - cropHeight) / 2;


            updateCropBox();

        };


        // ========================================================
        // UPDATE CROP BOX
        // ========================================================

        function updateCropBox() {

            cropBox.style.width =
                cropWidth + "px";

            cropBox.style.height =
                cropHeight + "px";

            cropBox.style.left =
                cropX + "px";

            cropBox.style.top =
                cropY + "px";

        }


        // ========================================================
        // KEEP CROP INSIDE IMAGE
        // ========================================================

        function keepInside() {

            cropX =
                Math.max(
                    0,
                    Math.min(
                        cropX,
                        imageWidth - cropWidth
                    )
                );


            cropY =
                Math.max(
                    0,
                    Math.min(
                        cropY,
                        imageHeight - cropHeight
                    )
                );


            updateCropBox();

        }


        // ========================================================
        // MOVE CROP
        // ========================================================

        cropBox.addEventListener(
            "mousedown",
            function (e) {

                if (
                    e.target === resizeHandle
                ) {
                    return;
                }


                e.preventDefault();


                dragging = true;


                dragStartX =
                    e.clientX;

                dragStartY =
                    e.clientY;


                initialCropX =
                    cropX;

                initialCropY =
                    cropY;

            }
        );


        document.addEventListener(
            "mousemove",
            function (e) {

                if (!dragging) {
                    return;
                }


                cropX =
                    initialCropX +
                    (e.clientX - dragStartX);


                cropY =
                    initialCropY +
                    (e.clientY - dragStartY);


                keepInside();

            }
        );


        document.addEventListener(
            "mouseup",
            function () {

                dragging = false;

            }
        );


        // ========================================================
        // RESIZE CROP
        // WIDTH & HEIGHT INDEPENDENTLY
        // ========================================================

        resizeHandle.addEventListener(
            "mousedown",
            function (e) {

                e.preventDefault();

                e.stopPropagation();


                resizing = true;


                resizeStartX =
                    e.clientX;

                resizeStartY =
                    e.clientY;


                initialCropWidth =
                    cropWidth;

                initialCropHeight =
                    cropHeight;

            }
        );


        document.addEventListener(
            "mousemove",
            function (e) {

                if (!resizing) {
                    return;
                }


                const dx =
                    e.clientX - resizeStartX;

                const dy =
                    e.clientY - resizeStartY;


                let newWidth =
                    initialCropWidth + dx;


                let newHeight =
                    initialCropHeight + dy;


                // Minimum
                newWidth =
                    Math.max(
                        80,
                        newWidth
                    );


                newHeight =
                    Math.max(
                        80,
                        newHeight
                    );


                // Maximum
                newWidth =
                    Math.min(
                        newWidth,
                        imageWidth - cropX
                    );


                newHeight =
                    Math.min(
                        newHeight,
                        imageHeight - cropY
                    );


                cropWidth =
                    newWidth;

                cropHeight =
                    newHeight;


                updateCropBox();

            }
        );


        document.addEventListener(
            "mouseup",
            function () {

                resizing = false;

            }
        );


        // ========================================================
        // TARGET FILE SIZE
        // ========================================================

        targetInput.addEventListener(
            "input",
            function () {

                let value =
                    parseFloat(
                        targetInput.value
                    );


                if (
                    isNaN(value) ||
                    value < 10
                ) {

                    targetInput.value = 10;

                }

            }
        );


        // ========================================================
        // CLOSE
        // ========================================================

        function closeEditor() {

            URL.revokeObjectURL(
                imageURL
            );

            overlay.remove();

            input.value = "";

        }


        closeButton.onclick =
            closeEditor;

        cancelButton.onclick =
            closeEditor;


        // ========================================================
        // GET TARGET BYTES
        // ========================================================

        function getTargetBytes() {

            let value =
                parseFloat(
                    targetInput.value
                );


            if (
                isNaN(value) ||
                value <= 0
            ) {

                value = 500;

            }


            if (
                targetUnit.value === "MB"
            ) {

                return value *
                    1024 *
                    1024;

            }


            return value * 1024;

        }


        // ========================================================
        // CREATE JPEG
        // ========================================================

        function createBlob(
            canvas,
            quality
        ) {

            return new Promise(
                function (resolve) {

                    canvas.toBlob(
                        function (blob) {

                            resolve(blob);

                        },
                        "image/jpeg",
                        quality
                    );

                }
            );

        }


        // ========================================================
        // CROP & UPLOAD
        // ========================================================

        cropButton.addEventListener(
            "click",
            async function () {

                if (
                    !img.naturalWidth ||
                    !img.naturalHeight
                ) {

                    alert(
                        "Image is not ready yet."
                    );

                    return;

                }


                cropButton.disabled =
                    true;

                cropButton.textContent =
                    "Processing...";


                try {

                    // ------------------------------------------------
                    // ORIGINAL IMAGE SCALE
                    // ------------------------------------------------

                    const scaleX =
                        img.naturalWidth /
                        img.clientWidth;


                    const scaleY =
                        img.naturalHeight /
                        img.clientHeight;


                    // ------------------------------------------------
                    // SOURCE CROP
                    // ------------------------------------------------

                    const sourceX =
                        cropX * scaleX;


                    const sourceY =
                        cropY * scaleY;


                    const sourceWidth =
                        cropWidth * scaleX;


                    const sourceHeight =
                        cropHeight * scaleY;


                    // ------------------------------------------------
                    // OUTPUT DIMENSIONS
                    //
                    // Keep the actual cropped dimensions.
                    // Target size controls FILE SIZE,
                    // not image dimensions.
                    // ------------------------------------------------

                    let outputWidth =
                        Math.max(
                            1,
                            Math.round(
                                sourceWidth
                            )
                        );


                    let outputHeight =
                        Math.max(
                            1,
                            Math.round(
                                sourceHeight
                            )
                        );


                    const canvas =
                        document.createElement(
                            "canvas"
                        );


                    canvas.width =
                        outputWidth;

                    canvas.height =
                        outputHeight;


                    const ctx =
                        canvas.getContext(
                            "2d"
                        );


                    ctx.imageSmoothingEnabled =
                        true;

                    ctx.imageSmoothingQuality =
                        "high";


                    // ------------------------------------------------
                    // DRAW CROP
                    // ------------------------------------------------

                    ctx.drawImage(

                        img,

                        sourceX,
                        sourceY,
                        sourceWidth,
                        sourceHeight,

                        0,
                        0,
                        outputWidth,
                        outputHeight

                    );


                    // ------------------------------------------------
                    // TARGET FILE SIZE
                    // ------------------------------------------------

                    const targetBytes =
                        getTargetBytes();


                    // ------------------------------------------------
                    // TRY QUALITY FIRST
                    // ------------------------------------------------

                    let quality = 0.92;

                    let blob =
                        await createBlob(
                            canvas,
                            quality
                        );


                    while (
                        blob.size > targetBytes &&
                        quality > 0.10
                    ) {

                        quality -= 0.05;


                        blob =
                            await createBlob(
                                canvas,
                                quality
                            );

                    }


                    // ------------------------------------------------
                    // IF STILL TOO LARGE:
                    // REDUCE RESOLUTION
                    // ------------------------------------------------

                    if (
                        blob.size > targetBytes
                    ) {

                        let scale = 0.90;


                        while (
                            blob.size > targetBytes &&
                            outputWidth > 300 &&
                            outputHeight > 300
                        ) {

                            outputWidth =
                                Math.max(
                                    300,
                                    Math.round(
                                        outputWidth *
                                        scale
                                    )
                                );


                            outputHeight =
                                Math.max(
                                    300,
                                    Math.round(
                                        outputHeight *
                                        scale
                                    )
                                );


                            canvas.width =
                                outputWidth;

                            canvas.height =
                                outputHeight;


                            ctx.drawImage(

                                img,

                                sourceX,
                                sourceY,
                                sourceWidth,
                                sourceHeight,

                                0,
                                0,
                                outputWidth,
                                outputHeight

                            );


                            quality = 0.75;


                            blob =
                                await createBlob(
                                    canvas,
                                    quality
                                );


                            scale -= 0.05;

                        }

                    }


                    // ------------------------------------------------
                    // NAME
                    // ------------------------------------------------

                    let newName =
                        nameInput.value.trim();


                    if (!newName) {

                        newName =
                            "cropped_image";

                    }


                    newName =
                        newName.replace(
                            /[^a-zA-Z0-9_\- ]/g,
                            ""
                        );


                    newName =
                        newName.replace(
                            /\s+/g,
                            "_"
                        );


                    if (!newName) {

                        newName =
                            "cropped_image";

                    }


                    newName += ".jpg";


                    // ------------------------------------------------
                    // CREATE FINAL FILE
                    // ------------------------------------------------

                    const croppedFile =
                        new File(
                            [blob],
                            newName,
                            {
                                type:
                                    "image/jpeg",

                                lastModified:
                                    Date.now()
                            }
                        );


                    // ------------------------------------------------
                    // PUT FILE INTO DJANGO INPUT
                    // ------------------------------------------------

                    const dataTransfer =
                        new DataTransfer();


                    dataTransfer.items.add(
                        croppedFile
                    );


                    input.files =
                        dataTransfer.files;


                    // ------------------------------------------------
                    // UPDATE PREVIEW
                    // ------------------------------------------------

                    previewButton.innerHTML =
                        "👁️";


                    // ------------------------------------------------
                    // CLOSE
                    // ------------------------------------------------

                    URL.revokeObjectURL(
                        imageURL
                    );

                    overlay.remove();


                    console.log(
                        "Final file:",
                        croppedFile.name,
                        Math.round(
                            croppedFile.size / 1024
                        ) + " KB"
                    );


                } catch (error) {

                    console.error(
                        "Crop error:",
                        error
                    );


                    alert(
                        "Could not process the image. Check the browser console for details."
                    );


                    cropButton.disabled =
                        false;

                    cropButton.textContent =
                        "Crop & Upload";

                }

            }
        );

    }



    // ============================================================
    // CSS
    // ============================================================

    const style =
        document.createElement("style");


    style.textContent = `

        .smart-crop-overlay {

            position: fixed;

            inset: 0;

            z-index: 999999;

            background:
                rgba(0,0,0,.72);

            display: flex;

            align-items: center;

            justify-content: center;

            padding: 20px;

            box-sizing: border-box;

        }


        .smart-crop-modal {

            width: min(900px, 96vw);

            max-height: 95vh;

            background: white;

            border-radius: 12px;

            overflow: hidden;

            box-shadow:
                0 20px 60px
                rgba(0,0,0,.45);

            display: flex;

            flex-direction: column;

        }


        .smart-crop-header {

            height: 55px;

            padding:
                0 18px;

            display: flex;

            align-items: center;

            justify-content:
                space-between;

            border-bottom:
                1px solid #ddd;

            font-size: 17px;

        }


        .smart-crop-close {

            border: none;

            background: transparent;

            font-size: 30px;

            cursor: pointer;

            color: #555;

            line-height: 1;

        }


        .smart-crop-workspace {

            background: #222;

            padding: 20px;

            display: flex;

            justify-content: center;

            align-items: center;

            overflow: auto;

        }


        .smart-crop-image-area {

            position: relative;

            display: inline-block;

            line-height: 0;

        }


        .smart-crop-image {

            display: block;

            max-width: 80vw;

            max-height: 58vh;

            width: auto;

            height: auto;

            user-select: none;

            -webkit-user-drag: none;

        }


        .smart-crop-box {

            position: absolute;

            border:
                3px solid white;

            box-shadow:
                0 0 0 9999px
                rgba(0,0,0,.55);

            cursor: move;

            box-sizing: border-box;

            min-width: 80px;

            min-height: 80px;

        }


        .crop-resize-handle {

            position: absolute;

            width: 18px;

            height: 18px;

            right: -10px;

            bottom: -10px;

            background: white;

            border:
                2px solid #333;

            border-radius: 50%;

            cursor: nwse-resize;

            box-sizing: border-box;

        }


        .smart-crop-controls {

            padding: 16px 20px;

            border-top:
                1px solid #ddd;

        }


        .smart-control-row {

            display: flex;

            align-items: center;

            gap: 8px;

            margin-bottom: 12px;

        }


        .smart-control-row:last-child {

            margin-bottom: 0;

        }


        .smart-control-row label {

            width: 125px;

            font-weight: 600;

            color: #444;

        }


        .smart-target-size {

            width: 90px;

            padding: 8px;

            border:
                1px solid #bbb;

            border-radius: 5px;

            box-sizing: border-box;

        }


        .smart-target-unit {

            padding: 8px;

            border:
                1px solid #bbb;

            border-radius: 5px;

            background: white;

        }


        .smart-file-name {

            flex: 1;

            padding: 8px;

            border:
                1px solid #bbb;

            border-radius: 5px;

            box-sizing: border-box;

        }


        .smart-crop-footer {

            padding:
                14px 20px;

            display: flex;

            justify-content:
                flex-end;

            gap: 10px;

            border-top:
                1px solid #ddd;

        }


        .smart-cancel,
        .smart-crop-upload {

            border: none;

            border-radius: 6px;

            padding:
                9px 18px;

            cursor: pointer;

            font-weight: 600;

        }


        .smart-cancel {

            background: #eee;

            color: #333;

        }


        .smart-crop-upload {

            background: #1677ff;

            color: white;

        }


        .smart-crop-upload:hover {

            background: #095dcc;

        }


        .smart-crop-upload:disabled {

            opacity: .6;

            cursor: wait;

        }


        @media (max-width: 600px) {

            .smart-crop-modal {

                width: 100%;

                max-height: 100vh;

                border-radius: 0;

            }


            .smart-crop-workspace {

                padding: 10px;

            }


            .smart-crop-image {

                max-width: 94vw;

                max-height: 55vh;

            }


            .smart-control-row label {

                width: 125px;

            }

        }

    `;


    document.head.appendChild(style);

});