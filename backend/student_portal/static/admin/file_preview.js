

// // // *******************************************************************************************
// // // FULL WORKING
// // // *******************************************************************************************


// document.addEventListener("DOMContentLoaded", function () {

//     document.querySelectorAll('input[type="file"]').forEach(function (input) {

//         let btn = document.createElement("button");
//         btn.type = "button";
//         btn.innerHTML = "🙈";
//         btn.className = "preview-eye-btn";

//         // Change eye on select
//         input.addEventListener("change", function () {
//             if (input.files.length > 0) {
//                 btn.innerHTML = "👁️";
//                 btn.classList.add("active");
//             }
//         });

//         btn.onclick = function () {

//             let url = null;

//             // NEW FILE
//             if (input.files && input.files.length > 0){
//                 url = URL.createObjectURL(input.files[0]);
//             }
//             // EXISTING FILE
//             else{
//                 let row = input.closest(".form-row, .fieldBox, .form-group") || input.parentElement;

//                 // Find ANY link inside the row
//                 let link = row.querySelector("a[href]");

//                 if (link){
//                     url = link.href;
//                 }

//             }

//             if (!url){
//                 alert("No file available");
//                 return;
//             }

//             // Popup size
//             // let w = screen.width * 0.9;
//             // let h = screen.height * 0.9;
//             // let left = (screen.width - w)/2;
//             // let top = (screen.height - h)/2;

//             // let viewer = window.open(
//             //     "",
//             //     "previewWindow",
//             //     `width=${w},height=${h},top=${top},left=${left},
//             //     resizable=yes,scrollbars=no`
//             // );
//             let w = screen.width * 0.5;
//             let h = screen.height * 0.9;

//             let viewer = window.open(
//             "",
//             "_blank",
//             `width=${w},height=${h},resizable=no,scrollbars=no`
//             );


//             viewer.document.write(`
// <!DOCTYPE html>
// <html>
// <head>
// <title>Preview</title>

// <style>
// *{
//   margin:0;
//   padding:0;
//   box-sizing:border-box;
// }

// html, body{
//   margin:0;
//   padding:0;
//   height:100%;
//   overflow:hidden;
//   background:black;
// }

// .viewer{
//   position:fixed;
//   top:0;
//   left:0;
//   right:0;
//   bottom:0;

//   display:flex;
//   justify-content:center;
//   align-items:center;
//   overflow:hidden;
// }


// .viewer img{
//   max-width:100%;
//   max-height:100%;
//   width:auto;
//   height:auto;
//   object-fit:contain;
//   display:block;
// }

// .viewer iframe{
//   width:100%;
//   height:100%;
//   border:none;
// }

// </style>
// </head>

// <body>
// <div class="viewer">
// ${
// url.match(/(jpg|jpeg|png|gif|webp)$/i)
// ? `<img src="${url}">`
// : `<iframe src="${url}"></iframe>`
// }
// </div>
// </body>
// </html>

// `);
           
//            // These must be outside the backticks
//             viewer.document.close();
//             viewer.focus();
//         };

//         input.after(btn);
//     });
// });


// *******************************************************************************************
// Till
// *******************************************************************************************

document.addEventListener("DOMContentLoaded", function () {

    document.querySelectorAll('input[type="file"]').forEach(function (input) {

        let btn = document.createElement("button");
        btn.type = "button";
        btn.innerHTML = "🙈";
        btn.className = "preview-eye-btn";
        btn.style.marginLeft = "6px";

        input.after(btn);

        // ✅ Find SAME FIELD ROW
        let row = input.closest(".form-row");

        let existingLink = null;
        if (row){
            let links = row.querySelectorAll("a[href]");
            links.forEach(l => {
                if (l.textContent.includes("/") || l.href.includes("/media/")){
                    existingLink = l;
                }
            });
        }

        // If file exists → open eye
        if (existingLink){
            btn.innerHTML = "👁️";
        }

        // On new file select
        input.addEventListener("change", function () {
            if (input.files.length > 0){
                btn.innerHTML = "👁️";
            } else if (!existingLink){
                btn.innerHTML = "🙈";
            }
        });

        // Preview click
        btn.onclick = function () {

            let url = null;

            // New file selected
            if (input.files.length > 0){
                url = URL.createObjectURL(input.files[0]);
            }
            // Existing file
            else{
                let row = input.closest(".form-row");
                let link = row ? row.querySelector("a[href]") : null;

                if (link){
                    url = link.href;
                }
            }

            if (!url){
                alert("No file available");
                return;
            }
        let w = screen.width * 0.5;
        let h = screen.height * 0.9;
        window.open(
                url,
                "_blank",
                `width=${w},height=${h},resizable=yes,scrollbars=yes`
            );

        viewer.document.write(`
        <!DOCTYPE html>
        <html>
        <head>
        <title>Preview</title>
        <style>
        body{
            margin:0;
            background:black;
            display:flex;
            justify-content:center;
            align-items:center;
            height:100vh;
        }
        img, embed{
            max-width:100%;
            max-height:100%;
        }
        </style>
        </head>
        <body>
        ${
        url.match(/\.(jpg|jpeg|png|gif|webp)$/i)
        ? `<img src="${url}">`
        : `<embed src="${url}" type="application/pdf" width="100%" height="100%">`
        }
        </body>
        </html>
        `);
        viewer.document.close();


                };

            });

        });
