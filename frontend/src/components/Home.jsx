import "./Home.css";
import RecentNoticeBar from "./RecentNoticeBar";
import {
    BookOpen,
    ClipboardList,
    CreditCard,
    FileBadge,
    BellRing
} from "lucide-react";

function Home() {
    return (
        <div className="home-container">

            <RecentNoticeBar />

            <div className="dashboard-cards">

                <div className="card">

                    <BookOpen size={28}/>

                    <h3>
                        Current Course
                    </h3>

                    <p>
                        DCOA88
                    </p>

                </div>

                <div className="card">

                    <ClipboardList size={28}/>

                    <h3>
                        Exams Completed
                    </h3>

                    <p>
                        1
                    </p>

                </div>

                <div className="card">

                    <CreditCard size={28}/>

                    <h3>
                        Total Payments
                    </h3>

                    <p>
                        ₹1500
                    </p>

                </div>

                <div className="card">

                    <FileBadge size={28}/>

                    <h3>
                        Certificates
                    </h3>

                    <p>
                        1
                    </p>

                </div>

                <div className="card">

                    <BellRing size={28}/>

                    <h3>
                        Notices
                    </h3>

                    <p>
                        17
                    </p>

                </div>

            </div>

        </div>

    );

}

export default Home;