document.addEventListener("DOMContentLoaded", function () {

    /* ================= PREMIUM STYLING ================= */
    const style = document.createElement("style");
    style.innerHTML = `
        input[type="file"] { font-size: 13px; color: #495057; background: #f8f9fa; border: 1px solid #dee2e6; border-radius: 8px; padding: 4px; }
        input[type="file"]::file-selector-button { background: #2c7be5; color: white; border: none; padding: 8px 16px; border-radius: 6px; cursor: pointer; font-weight: 600; margin-right: 12px; transition: all 0.2s; }
        input[type="file"]::file-selector-button:hover { background: #1a68d1; transform: translateY(-1px); }
        
        .v-badge { display: inline-flex; align-items: center; padding: 4px 12px; border-radius: 20px; font-size: 11px; font-weight: 700; margin-left: 10px; text-transform: uppercase; border: 1px solid transparent; }
        .v-verified { background: #d2f4ea; color: #02a06d; border-color: #02a06d; }
        .v-unverified { background: #fff5f5; color: #e53e3e; border-color: #e53e3e; }
        .needs-verify { animation: pulse-red 1.5s infinite; }
        @keyframes pulse-red { 0% { opacity: 1; } 50% { opacity: 0.6; } 100% { opacity: 1; } }
    `;
    document.head.appendChild(style);

    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    /* ================= EMAIL VERIFICATION FETCH ================= */
    const emailInput = document.getElementById("id_email");
    if (emailInput) {
        const isVerifiedInitial = emailInput.getAttribute("data-verified") === "true";
        const badge = document.createElement("span");
        badge.className = isVerifiedInitial ? "v-badge v-verified" : "v-badge v-unverified needs-verify";
        badge.innerHTML = isVerifiedInitial ? "✓ Verified" : "✕ Unverified";
        emailInput.parentElement.appendChild(badge);

        document.body.addEventListener("click", function(e) {
            // MATCH THIS ID to your "Verify" button in the portal
            if (e.target && e.target.classList.contains("verify-otp-btn")) {
                const otpInput = document.querySelector(".otp-input-field"); // Match your OTP text box class
                
                if (!otpInput || !otpInput.value) return alert("Please enter the OTP.");

                fetch("/verify-email-otp/", {
                    method: "POST",
                    headers: { 
                        "X-CSRFToken": getCookie("csrftoken"), 
                        "Content-Type": "application/x-www-form-urlencoded" 
                    },
                    body: new URLSearchParams({ 
                        "otp": otpInput.value, 
                        "email": emailInput.value 
                    })
                })
                .then(res => res.json())
                .then(data => {
                    if (data.status === "verified") {
                        badge.className = "v-badge v-verified";
                        badge.innerHTML = "✓ Verified";
                        badge.classList.remove("needs-verify");

                        // ✅ ADD THIS BLOCK
                        let hidden = document.getElementById("email_verified_input");

                        if (!hidden) {
                            hidden = document.createElement("input");
                            hidden.type = "hidden";
                            hidden.name = "email_verified_flag";
                            hidden.id = "email_verified_input";
                            document.querySelector("form").appendChild(hidden);
                        }

                        hidden.value = "true";

                        alert("Verification complete! You can now SAVE.");
                    } else if (data.status === "expired") {
                        alert("OTP has expired. Please request a new one.");
                    } else {
                        alert("Invalid OTP code.");
                    }
                });
            }
        });

        emailInput.addEventListener("input", () => {
            badge.className = "v-badge v-unverified needs-verify";
            badge.innerHTML = "✕ Re-verify Needed";
        });
    }

    /* ================= PHOTO & FILE PREVIEWS ================= */
    const passportInput = document.getElementById("id_passport_photo");
    if (passportInput) {
        const box = document.createElement("div");
        box.style.cssText = "position: absolute; top: 140px; right: 120px; width: 140px; height: 170px; border: 2px solid #999; display: flex; align-items: center; justify-content: center; background: #fff; box-shadow: 0 4px 10px rgba(0,0,0,0.1); overflow: hidden;";
        const img = document.createElement("img");
        img.style.cssText = "max-width: 100%; max-height: 100%;";
        box.appendChild(img);
        document.body.appendChild(box);

        const current = passportInput.closest(".field-passport_photo")?.querySelector("a");
        if (current) img.src = current.href;

        passportInput.addEventListener("change", function () {
            const file = this.files[0];
            if (file) {
                const reader = new FileReader();
                reader.onload = (e) => img.src = e.target.result;
                reader.readAsDataURL(file);
            }
        });
    }

    const idNum = document.getElementById("id_id_proof_number");
    if (idNum) idNum.addEventListener("input", function() { this.value = this.value.replace(/\D/g, "").slice(0, 12); });

    const instName = document.getElementById("id_institute_name");
    if (instName) instName.addEventListener("input", function() { this.value = this.value.toUpperCase(); });

    const idFile = document.getElementById("id_id_proof_file");
    if (idFile) {
        const pBtn = document.createElement("div");
        pBtn.style.cssText = "display: inline-flex; align-items: center; justify-content: center; width: 42px; height: 42px; margin-left: 10px; border-radius: 10px; background: #e9ecef; cursor: pointer; font-size: 20px;";
        idFile.parentElement.appendChild(pBtn);

        const updatePreview = (url, type) => {
            pBtn.innerHTML = type.includes("pdf") ? "📄" : "🖼️";
            pBtn.onclick = () => window.open(url);
        };

        const currentFile = idFile.closest(".field-id_proof_file")?.querySelector("a");
        if (currentFile) updatePreview(currentFile.href, currentFile.href);

        idFile.addEventListener("change", function () {
            const file = this.files[0];
            if (file) updatePreview(URL.createObjectURL(file), file.type);
        });
    }
    /* ================= SIGNATURE PREVIEW ================= */
    /* ================= SIGNATURE FILE PREVIEW (LIKE ID PROOF) ================= */
    /* ================= SIGNATURE FILE PREVIEW ================= */
    /* ================= SIGNATURE FILE PREVIEW ================= */
    const signFile = document.getElementById("id_signature");

    if (signFile) {
        const sBtn = document.createElement("div");
        sBtn.style.cssText = "display: inline-flex; align-items: center; justify-content: center; width: 42px; height: 42px; margin-left: 10px; border-radius: 10px; background: #e9ecef; cursor: pointer; font-size: 20px;";
        
        // ✅ SAME AS ID PROOF → no flex hacks, no hiding
        signFile.parentElement.appendChild(sBtn);

        const updatePreview = (url, type) => {
            sBtn.innerHTML = type.includes("pdf") ? "📄" : "✍️";
            sBtn.onclick = () => window.open(url);
        };

        // ❌ NO DEFAULT ICON
        sBtn.innerHTML = "";

        // existing file (edit mode)
        const currentFile = signFile.closest(".field-signature")?.querySelector("a");
        if (currentFile) updatePreview(currentFile.href, currentFile.href);

        // new file preview
        signFile.addEventListener("change", function () {
            const file = this.files[0];
            if (file) updatePreview(URL.createObjectURL(file), file.type);
        });
    }
    
});