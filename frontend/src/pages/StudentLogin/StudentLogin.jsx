import React, { useState } from "react";
import { sendOTP } from "../../services/authService";
import { useNavigate } from "react-router-dom";
import { verifyOTP } from "../../services/authService";

function StudentLogin() {
    const navigate = useNavigate();
    const [loginMode, setLoginMode] = useState("email");
    const [loginValue, setLoginValue] = useState("");
    const [dob, setDob] = useState("");
    const [otpSent, setOtpSent] = useState(false);
    const [resendTimer, setResendTimer] = useState(0);
    const [sendingOTP, setSendingOTP] = useState(false);
    const [otp, setOtp] = useState("");

    const showToast = (message) => {
        const toast = document.createElement("div");
        toast.className = "auth-toast";
        toast.textContent = message;

        document.body.appendChild(toast);

        setTimeout(() => {
            toast.remove();
        }, 5000);
    };


    async function handleSubmit(e) {
        e.preventDefault();

        setSendingOTP(true);

        let finalLoginValue = loginValue;

        if (loginMode === "student") {
            const parts = loginValue.trim().split("/");

            if (parts.length === 3 && /^\d+$/.test(parts[2])) {
                parts[0] = parts[0].toUpperCase();
                parts[1] = parts[1].toUpperCase();
                parts[2] = parts[2].padStart(4, "0");

                finalLoginValue = parts.join("/");
            }
        }

        try {
            const response = await sendOTP({
                mode: loginMode,
                value: finalLoginValue,
                dob: dob
            });

            if (response.data.success) {
                setOtpSent(true);
                startResendTimer();
            } else {
                showToast("Invalid Login Credentials");
            }

        } catch (error) {
            console.error(error);
            showToast("Unable to connect to server.");
        }

        setSendingOTP(false);
    }
    function startResendTimer() {

        setResendTimer(30);

        const interval = setInterval(() => {

            setResendTimer(prev => {

                if (prev <= 1) {

                    clearInterval(interval);

                    return 0;

                }

                return prev - 1;

            });

        }, 1000);

    }
    async function handleVerifyOTP(e) {

        e.preventDefault();

        const response = await verifyOTP(otp);

        console.log(response.data);

        if (response.data.success) {
            navigate("/dashboard");
        }

    }
    return (
        <div
        style={{
            display: "flex",
            justifyContent: "center",
            alignItems: "center",
            minHeight: "100vh",
            // Swapped out the old blue for a premium, sleek slate-charcoal gradient
            background: "linear-gradient(135deg, #1e293b 0%, #0f172a 100%)",
            fontFamily: "'Segoe UI', Roboto, Helvetica, Arial, sans-serif",
            padding: "20px",
            boxSizing: "border-box",
        }}
        >
        <div
            style={{
            width: "100%",
            maxWidth: "400px",
            // Premium Glassmorphism Properties
            background: "rgba(255, 255, 255, 0.06)",
            backdropFilter: "blur(20px)",
            WebkitBackdropFilter: "blur(20px)", // Safari support
            padding: "40px 30px",
            borderRadius: "24px",
            border: "1px solid rgba(255, 255, 255, 0.1)",
            boxShadow: "0 20px 40px rgba(0, 0, 0, 0.25)",
            }}
        >
            <h1
            style={{
                textAlign: "center",
                color: "#ffffff",
                fontSize: "26px",
                fontWeight: "600",
                letterSpacing: "-0.5px",
                margin: "0 0 8px 0",
            }}
            >
            Student Portal
            </h1>
            <p
            style={{
                textAlign: "center",
                color: "rgba(255, 255, 255, 0.55)",
                fontSize: "14px",
                margin: "0 0 32px 0",
            }}
            >
            Select your preferred verification method
            </p>

            {/* Segmented Toggle Control */}
            <div
            style={{
                background: "rgba(255, 255, 255, 0.04)",
                borderRadius: "12px",
                padding: "4px",
                display: "flex",
                position: "relative",
                marginBottom: "32px",
                border: "1px solid rgba(255, 255, 255, 0.06)",
            }}
            >
            {/* Animated Background Slider */}
            <div
                style={{
                position: "absolute",
                top: "4px",
                bottom: "4px",
                left: "4px",
                width: "calc(50% - 4px)",
                background: "rgba(255, 255, 255, 0.12)",
                backdropFilter: "blur(4px)",
                borderRadius: "8px",
                border: "1px solid rgba(255, 255, 255, 0.1)",
                transform: loginMode === "email" ? "translateX(0)" : "translateX(100%)",
                transition: "transform 0.3s cubic-bezier(0.4, 0, 0.2, 1)",
                pointerEvents: "none",
                }}
            />

            <button
                type="button"
                onClick={() => setLoginMode("email")}
                style={{
                flex: 1,
                border: "none",
                background: "transparent",
                color: loginMode === "email" ? "#ffffff" : "rgba(255, 255, 255, 0.4)",
                padding: "12px 0",
                borderRadius: "8px",
                fontSize: "14px",
                fontWeight: "600",
                cursor: "pointer",
                zIndex: 1,
                transition: "color 0.2s ease",
                }}
            >
                Email
            </button>

            <button
                type="button"
                onClick={() => setLoginMode("student")}
                style={{
                flex: 1,
                border: "none",
                background: "transparent",
                color: loginMode === "student" ? "#ffffff" : "rgba(255, 255, 255, 0.4)",
                padding: "12px 0",
                borderRadius: "8px",
                fontSize: "14px",
                fontWeight: "600",
                cursor: "pointer",
                zIndex: 1,
                transition: "color 0.2s ease",
                }}
            >
                Student ID
            </button>
            </div>

            <form onSubmit={handleSubmit}>
            {/* Dynamic Input Field */}
            <div style={{ marginBottom: "24px" }}>
                <label
                style={{
                    display: "block",
                    marginBottom: "8px",
                    fontWeight: "500",
                    fontSize: "13px",
                    color: "rgba(255, 255, 255, 0.75)",
                    letterSpacing: "0.3px",
                }}
                >
                {loginMode === "email" ? "Email Address" : "Student ID"}
                </label>

                <input
                type={loginMode === "email" ? "email" : "text"}
                value={loginValue}
                onChange={(e) => setLoginValue(e.target.value)}
                // Your custom twisted placeholders applied seamlessly below:
                placeholder={
                    loginMode === "email" ? "name@smartCi.com" : "MG/SLG/0000"
                }
                style={{
                    width: "100%",
                    padding: "14px 16px",
                    borderRadius: "10px",
                    border: "1px solid rgba(255, 255, 255, 0.12)",
                    background: "rgba(255, 255, 255, 0.03)",
                    color: "#ffffff",
                    fontSize: "15px",
                    boxSizing: "border-box",
                    outline: "none",
                    transition: "all 0.25s ease",
                }}
                onFocus={(e) => {
                    e.target.style.borderColor = "rgba(255, 255, 255, 0.35)";
                    e.target.style.background = "rgba(255, 255, 255, 0.07)";
                    e.target.style.boxShadow = "0 0 0 4px rgba(255, 255, 255, 0.04)";
                }}
                onBlur={(e) => {
                    e.target.style.borderColor = "rgba(255, 255, 255, 0.12)";
                    e.target.style.background = "rgba(255, 255, 255, 0.03)";
                    e.target.style.boxShadow = "none";
                }}
                />
            </div>

            {/* Date of Birth Field */}
            <div style={{ marginBottom: "32px" }}>
                <label
                style={{
                    display: "block",
                    marginBottom: "8px",
                    fontWeight: "500",
                    fontSize: "13px",
                    color: "rgba(255, 255, 255, 0.75)",
                    letterSpacing: "0.3px",
                }}
                >
                Date of Birth
                </label>

                <input
                type="date"
                value={dob}
                onChange={(e) => setDob(e.target.value)}
                style={{
                    width: "100%",
                    padding: "14px 16px",
                    borderRadius: "10px",
                    border: "1px solid rgba(255, 255, 255, 0.12)",
                    background: "rgba(255, 255, 255, 0.03)",
                    color: "#ffffff",
                    fontSize: "15px",
                    boxSizing: "border-box",
                    outline: "none",
                    transition: "all 0.25s ease",
                }}
                onFocus={(e) => {
                    e.target.style.borderColor = "rgba(255, 255, 255, 0.35)";
                    e.target.style.background = "rgba(255, 255, 255, 0.07)";
                    e.target.style.boxShadow = "0 0 0 4px rgba(255, 255, 255, 0.04)";
                }}
                onBlur={(e) => {
                    e.target.style.borderColor = "rgba(255, 255, 255, 0.12)";
                    e.target.style.background = "rgba(255, 255, 255, 0.03)";
                    e.target.style.boxShadow = "none";
                }}
                />
            </div>

            {/* Glowing Action Button */}
            {
                !otpSent ? (
                    <button
                        type="submit"
                        disabled={sendingOTP}
                        style={{
                            width: "100%",
                            padding: "15px",
                            background: "#ffffff",
                            color: "#0f172a",
                            border: "none",
                            borderRadius: "12px",
                            fontSize: "15px",
                            fontWeight: "600",
                            cursor: "pointer"
                        }}
                    >
                        {sendingOTP ? "Sending..." : "Send OTP"}
                    </button>
                ) : (
                    
                        resendTimer > 0 ? (

                            <div
                                style={{
                                    marginTop: "10px",
                                    marginBottom: "20px",
                                    textAlign: "center",
                                    color: "rgba(255,255,255,.55)",
                                    fontSize: "14px"
                                }}
                            >
                                Resend OTP in {resendTimer}s
                            </div>

                        ) : (

                            <div
                                onClick={handleSubmit}
                                style={{
                                    marginTop: "10px",
                                    marginBottom: "20px",
                                    textAlign: "center",
                                    color: "rgba(255,255,255,.55)",
                                    fontSize: "14px",
                                    cursor: "pointer"
                                }}
                            >
                                Resend OTP
                            </div>

                        )
                    
                )
            }
            {otpSent && (
                <>
                    <div style={{ marginTop: "20px" }}>
                        <input
                            type="text"
                            value={otp}
                            onChange={(e) => setOtp(e.target.value)}
                            placeholder="Enter OTP"
                            style={{
                                width: "100%",
                                padding: "14px 16px",
                                borderRadius: "10px",
                                border: "1px solid rgba(255,255,255,0.12)",
                                background: "rgba(255,255,255,0.03)",
                                color: "#ffffff",
                                fontSize: "15px",
                                boxSizing: "border-box"
                            }}
                        />
                    </div>

                    <button
                        type="button"
                        onClick={handleVerifyOTP}
                        style={{
                            width: "100%",
                            marginTop: "20px",
                            padding: "15px",
                            background: "#ffffff",
                            color: "#0f172a",
                            border: "none",
                            borderRadius: "12px",
                            fontSize: "15px",
                            fontWeight: "600",
                            cursor: "pointer"
                        }}
                    >
                        Verify OTP
                    </button>
                </>
            )}
            </form>
        </div>
        </div>
    );
    }

export default StudentLogin;
const style = document.createElement("style");
style.innerHTML = `
.auth-toast {
    position: fixed;
    top: 25px;
    right: 25px;
    background: #fff;
    color: #222;
    padding: 14px 20px;
    border-radius: 10px;
    border-left: 4px solid #e53935;
    box-shadow: 0 8px 25px rgba(0, 0, 0, 0.2);
    font-size: 14px;
    font-weight: 500;
    z-index: 9999;
    animation: toastIn 0.3s ease;
}

@keyframes toastIn {
    from {
        transform: translateX(120%);
        opacity: 0;
    }
    to {
        transform: translateX(0);
        opacity: 1;
    }
}
`;

document.head.appendChild(style);