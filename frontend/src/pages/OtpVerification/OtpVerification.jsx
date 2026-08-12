import { useState } from "react";
import { verifyOTP } from "../../services/authService";
import { useNavigate } from "react-router-dom";
function OtpVerification() {
    const navigate = useNavigate();
    const [otp, setOtp] = useState("");
    
    async function handleSubmit(e) {

        e.preventDefault();

        const response = await verifyOTP(otp);

        console.log(response.data);

        if (response.data.success) {
            navigate("/dashboard");
        }

    }

    return (
        <div>

            <h1>OTP Verification</h1>

            <form onSubmit={handleSubmit}>

                <input
                    type="text"
                    value={otp}
                    onChange={(e) => setOtp(e.target.value)}
                    placeholder="Enter OTP"
                />

                <button type="submit">
                    Verify OTP
                </button>

            </form>

        </div>
    );
}

export default OtpVerification;