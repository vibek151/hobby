document.addEventListener("DOMContentLoaded", function(){

    const input = document.querySelector('input[name="passport_photo"]');
    if(!input) return;

    const box = document.createElement("div");
    box.className = "passport-preview-box";
    box.innerHTML = "Upload Photo";

    input.after(box);

    input.addEventListener("change", function(){
        if(input.files && input.files[0]){
            const url = URL.createObjectURL(input.files[0]);
            box.innerHTML = `<img src="${url}">`;
        }
    });
});
