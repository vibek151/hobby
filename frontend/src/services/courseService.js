import api from "./api";

export const getCourseHistory = async () => {
    return await api.get(
        "/student/course-history/"
    );
};

export const getCourses = async () => {
    return await api.get(
        "/api/website/courses/"
    );
};

export const getCourseDetail = async (code) => {
    return await api.get(
        `/api/website/courses/${code}/`
    );
};

export const getPopularCourses = async () => {
    return await api.get(
        "/api/website/popular-courses/"
    );
};