import api from "./api";

export const getCertificates = async () => {

    return await api.get(
        "/student/certificates-api/"
    );

};
export const verifyCertificate = async (
    certificateNo
) => {

    return await api.get(
        "/student/verify-certificate/",
        {
            params: {
                certificate_no: certificateNo
            }
        }
    );

};