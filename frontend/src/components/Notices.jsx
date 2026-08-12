import { useEffect, useState } from "react";
import { getNotices } from "../services/noticeService";
import { FiCalendar, FiClock } from "react-icons/fi";
import "./Notices.css";

function Notices() {
    const [notices, setNotices] = useState([]);
    const [openIndex, setOpenIndex] = useState(null);
    const [readNotices, setReadNotices] = useState(
        JSON.parse(localStorage.getItem("readNotices")) || []
    );
    useEffect(() => {
        async function fetchNotices() {
            try {
                const response = await getNotices();
                setNotices(response.data.notices || []);
            } catch (error) {
                console.log(error);
            }
        }

        fetchNotices();
    }, []);

    return (
        <div>
            <h1 className="notice-page-title">Notices</h1>

            {notices.length === 0 ? (
                <p>No notices available.</p>
            ) : (
                notices.map((notice, index) => (
                    <div
                        className={`notice-card ${openIndex === index ? "opened" : ""}`}
                        key={index}
                        onClick={() => {
                            setOpenIndex(openIndex === index ? null : index);

                            if (!readNotices.includes(index)) {
                                const updated = [...readNotices, index];

                                setReadNotices(updated);

                                localStorage.setItem(
                                    "readNotices",
                                    JSON.stringify(updated)
                                );
                            }
                        }}
                    >
                        <div
                            className={`notice-dot ${
                                readNotices.includes(index) ? "grey" : "green"
                            }`}
                        ></div>
                        <div className="notice-header">
                            <h2>{notice.title}</h2>

                            {/* <div className="notice-badge">
                                {openIndex === index ? "−" : "+"}
                            </div> */}
                        </div>

                        {openIndex === index && (
                            <>  
                            {/* <h4>Body:</h4> */}
                                <div className="notice-message">
                                    {notice.body}
                                </div>

                                <div className="notice-footer">
                                    <FiCalendar className="notice-icon" />
                                    <span>
                                        {new Date(notice.date).toLocaleDateString("en-IN", {
                                            day: "2-digit",
                                            month: "short",
                                            year: "numeric"
                                        })}
                                    </span>

                                    <span className="dot">•</span>

                                    <FiClock className="notice-icon" />
                                    <span>
                                        {new Date(notice.date).toLocaleTimeString("en-IN", {
                                            hour: "2-digit",
                                            minute: "2-digit"
                                        })}
                                    </span>
                                </div>
                            </>
                        )}
                    </div>
                ))
            )}
        </div>
    );
}

export default Notices;