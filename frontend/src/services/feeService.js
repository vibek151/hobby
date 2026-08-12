import api from "./api";

export const getPayments = async () => {

    return await api.get(
        "/student/payments-api/"
    );

};