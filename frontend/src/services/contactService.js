import api from "./api";

// 1. Fetch institute details for the contact component / footer
export const getWebsiteContact = async () => {
    return await api.get("/api/website/contact/");
};

// 2. Fetch responses from your local database keyword matching advisor
export const askAIAdvisor = async (message) => {
    return await api.post("/api/ai-advisor/", { message });
};