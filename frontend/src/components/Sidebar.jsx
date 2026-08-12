import {
    Home,
    UserCircle,
    BookOpen,
    ClipboardList,
    CreditCard,
    FileBadge,
    BellRing,
    LogOut
} from "lucide-react";

import "./Sidebar.css";

function Sidebar({ page, setPage }) {

    return (

        <div className="sidebar">

            <div className="menu">

                <div
                    className={`menu-item ${page === "home" ? "active" : ""}`}
                    onClick={() => setPage("home")}
                >
                    <Home size={18}/>
                    Home
                </div>

                <div
                    className={`menu-item ${page === "personal" ? "active" : ""}`}
                    onClick={() => setPage("personal")}
                >
                    <UserCircle size={18}/>
                    Personal Details
                </div>

                <div
                    className={`menu-item ${page === "course" ? "active" : ""}`}
                    onClick={() => setPage("course")}
                >
                    <BookOpen size={18}/>
                    Course History
                </div>

                <div
                    className={`menu-item ${page === "exam" ? "active" : ""}`}
                    onClick={() => setPage("exam")}
                >
                    <ClipboardList size={18}/>
                    Exams & Marks
                </div>

                <div
                    className={`menu-item ${page === "payment" ? "active" : ""}`}
                    onClick={() => setPage("payment")}
                >
                    <CreditCard size={18}/>
                    Payments
                </div>

                <div
                    className={`menu-item ${page === "certificate" ? "active" : ""}`}
                    onClick={() => setPage("certificate")}
                >
                    <FileBadge size={18}/>
                    Certificates
                </div>

                <div
                    className={`menu-item ${page === "notice" ? "active" : ""}`}
                    onClick={() => setPage("notice")}
                >
                    <BellRing size={18}/>
                    Notices
                </div>

            </div>

            <div className="logout">

                <div
                    className="menu-item"
                    onClick={() => {
                        localStorage.clear();
                        sessionStorage.clear();
                        window.location.href = "/";
                    }}
                >
                    <LogOut size={18}/>
                    Logout
                </div>

            </div>

        </div>

    );

}

export default Sidebar;