import { useEffect, useState } from "react";
import { getRecentNotices } from "../services/noticeService";
import "./RecentNoticeBar.css";

function RecentNoticeBar() {

    const [notices, setNotices] = useState([]);

    useEffect(() => {

        async function fetchNotices() {

            try {

                const response = await getRecentNotices();
                console.log(response.data);
                setNotices(
                    response.data.notices || []
                );

            }

            catch (error) {

                console.log(error);

                setNotices([]);

            }

        }

        fetchNotices();

    }, []);

    if (notices.length === 0) {

        return (
            <div>
                No recent notices
            </div>
        );

    }

    return (

        <div className="recent-notices">
        {
            notices.slice(0,3).map((notice,index)=>(
                <div
                    className="notice-row"
                    key={index}
                >
                    <div className="notice-date">
                        {notice.created_at}
                    </div>

                    <div className="notice-content">
                        <div
                            className="notice-text"
                            style={{
                                animationDuration: `${Math.max(
                                    20,
                                    ((notice.title || "").length + (notice.body || "").length) * 0.3
                                )}s`
                            }}
                        >
                            <span className="notice-title">
                                {notice.title}
                            </span>

                            {" | "}

                            <span className="notice-body">
                                {notice.body}
                            </span>
                        </div>
                    </div>
                </div>
            ))
        }

        {
            notices.length > 3 &&
            (
                <div className="more-row">
                    +{notices.length-3} more
                </div>
            )
        }
        </div>

    );

}

export default RecentNoticeBar;