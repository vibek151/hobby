import "./Notices.css";

function Notices() {
    return (
        <div>

            <h1 className="notice-page-title">
                Notices
            </h1>

            <div className="notice-card">

                <div className="notice-header">

                    <h2>
                        📢 Fee Reminder
                    </h2>

                    <span className="notice-badge">
                        Important
                    </span>

                </div>

                <p className="notice-message">
                    Monthly fees must be paid before the due date.
                </p>

                <div className="notice-date">
                    08 Jun 2026
                </div>

            </div>


            <div className="notice-card">

                <div className="notice-header">

                    <h2>
                        📝 Examination Notice
                    </h2>

                    <span className="notice-badge">
                        Exam
                    </span>

                </div>

                <p className="notice-message">
                    Practical examination will start next week.
                </p>

                <div className="notice-date">
                    07 Jun 2026
                </div>

            </div>


            <div className="notice-card">

                <div className="notice-header">

                    <h2>
                        🎓 Certificate Notice
                    </h2>

                    <span className="notice-badge">
                        Update
                    </span>

                </div>

                <p className="notice-message">
                    Certificates are available after course completion.
                </p>

                <div className="notice-date">
                    05 Jun 2026
                </div>

            </div>

        </div>
    );
}

export default Notices;