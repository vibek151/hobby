import api from "./api";

export const getNotices = async () => {

    return await api.get(
        "/student/notices-api/"
    );

};

export const getRecentNotices = async () => {

    return await api.get(
        "/student/recent-notices/"
    );

};