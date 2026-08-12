import api from "./api";

export const getMarks = async () => {

    return await api.get(
        "/student/marks/"
    );

};