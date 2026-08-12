import api from "./api";

export const getProfile = async () => {

    return await api.get(
        "/student/profile/"
    );

};