import api from "./api";

export const sendOTP = async (data) => {
    return await api.post(
        "/student/send-otp/",
        data
    );
};
export const verifyOTP = async (otp) => {
    return await api.post(
        "/student/verify-otp/",
        {
            otp: otp
        }
    );
};