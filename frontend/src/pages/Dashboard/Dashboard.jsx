
import { useState } from "react";
import Sidebar from "../../components/Sidebar";
import PersonalDetails from "../../components/PersonalDetails";
import CourseHistory from "../../components/CourseHistory";
import Exams from "../../components/Exams";
import Payments from "../../components/Payments";
import Certificates from "../../components/Certificates";
import Notices from "../../components/Notices";
import Home from "../../components/Home";
import Header from "../../components/Header/Header";

function Dashboard() {
    const [page, setPage] = useState("home");

    return (
        <>
            <Header />

            <div
                style={{
                    display: "flex",
                    height: "calc(100vh - 80px)"
                }}
            >

                <Sidebar setPage={setPage} />

                <div
                    style={{
                        flex: 1,
                        padding: "30px",
                        overflowY: "auto"
                    }}
                >

                    {
                        page === "home" ?

                        <Home /> :

                        page === "personal" ?
                        <PersonalDetails /> :

                        page === "course" ?
                        <CourseHistory /> :

                        page === "exam" ?
                        <Exams /> :

                        page === "payment" ?
                        <Payments /> :

                        page === "certificate" ?
                        <Certificates /> :

                        page === "notice" ?
                        <Notices /> :

                        <PersonalDetails />
                    }

                </div>

            </div>
        </>
    );
}

export default Dashboard;