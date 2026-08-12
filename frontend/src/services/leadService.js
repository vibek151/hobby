
import api from "./api";

export const createLead = (data) => {
    return api.post("/api/management/create-lead/", data);
};
