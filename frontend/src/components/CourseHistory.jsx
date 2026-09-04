// import { useEffect, useState } from "react";
// import { getCourseHistory } from "../services/courseService";
// import "./CourseHistory.css";

// function CourseHistory() {

//     const [courses, setCourses] = useState([]);

//     useEffect(() => {

//         async function fetchCourses() {

//             const response = await getCourseHistory();

//             console.log(response.data);

//             setCourses(response.data.courses);

//         }

//         fetchCourses();

//     }, []);

//     return (

//         <div className="history-container">

//             <h1 className="history-title">
//                 Course History
//             </h1>

//             <div className="timeline">

//                 {
//                     courses.map((course, index) => (

//                         <div
//                             className="timeline-item"
//                             key={index}
//                         >

//                             <div className="timeline-left">

//                                 <div
//                                     className={
//                                         course.status === "Running"
//                                             ? "timeline-circle running-circle"
//                                             : "timeline-circle completed-circle"
//                                     }
//                                 >
//                                 </div>

//                                 {
//                                     index !== courses.length - 1 &&
//                                     <div className="timeline-line"></div>
//                                 }

//                             </div>

//                             <details className="history-card">

//                                 <summary>

//                                     {course.code}
//                                     {" - "}
//                                     {course.name}

//                                 </summary>

//                                 <div className="course-details">

//                                     <div className="detail-row">
//                                         <span>Course Code</span>
//                                         <span>{course.code}</span>
//                                     </div>

//                                     <div className="detail-row">
//                                         <span>Course Name</span>
//                                         <span>{course.name}</span>
//                                     </div>

//                                     <div className="detail-row">
//                                         <span>Duration</span>
//                                         <span>
//                                             {course.duration} Months
//                                         </span>
//                                     </div>

//                                     <div className="detail-row">
//                                         <span>Start Date</span>
//                                         <span>
//                                             {course.start_date}
//                                         </span>
//                                     </div>

//                                     <div className="detail-row">
//                                         <span>End Date</span>
//                                         <span>
//                                             {
//                                                 course.end_date
//                                                     ? course.end_date
//                                                     : "In Progress"
//                                             }
//                                         </span>
//                                     </div>

//                                     <div className="detail-row">
//                                         <span>Status</span>

//                                         <span
//                                             className={
//                                                 course.status === "Running"
//                                                     ? "status-running"
//                                                     : "status-completed"
//                                             }
//                                         >
//                                             {course.status}
//                                         </span>
//                                     </div>

//                                 </div>

//                             </details>

//                         </div>

//                     ))
//                 }

//             </div>

//         </div>

//     );

// }

// export default CourseHistory;

import { useEffect, useState } from "react";
import { getCourseHistory } from "../services/courseService";
import "./CourseHistory.css";

function CourseHistory() {

    const [courses, setCourses] = useState([]);
    const [expandedIndex, setExpandedIndex] = useState(null);

    useEffect(() => {

        async function fetchCourses() {

            try {

                const response = await getCourseHistory();

                console.log(response.data);

                setCourses(response.data.courses || []);

            } catch (error) {

                console.error("Failed to fetch course history:", error);

            }

        }

        fetchCourses();

    }, []);

    const toggleCourse = (index) => {

        setExpandedIndex(
            expandedIndex === index ? null : index
        );

    };

    return (

        <div className="history-container">

            <h1 className="history-title">
                Course History
            </h1>

            <div className="timeline">

                {courses.map((course, index) => {

                    const isRunning = course.status === "Running";
                    const isExpanded = expandedIndex === index;
                    const isLast = index === courses.length - 1;

                    return (

                        <div
                            className="timeline-item"
                            key={course.id || index}
                        >

                            {/* COURSE NODE */}

                            <div
                                className={`timeline-node ${
                                    isExpanded ? "timeline-node-expanded" : ""
                                }`}
                                onClick={() => toggleCourse(index)}
                            >

                                <div className="timeline-left">

                                    <div
                                        className={
                                            isRunning
                                                ? "timeline-circle running-circle"
                                                : "timeline-circle completed-circle"
                                        }
                                    />

                                </div>


                                <div className="history-card">

                                    <div className="history-card-header">

                                        <span>
                                            {course.code}
                                            {" - "}
                                            {course.name}
                                        </span>

                                        <span className="expand-icon">
                                            {isExpanded ? "▲" : "▼"}
                                        </span>

                                    </div>


                                    {isExpanded && (

                                        <div className="course-details">

                                            <div className="detail-row">
                                                <span>Course Code</span>
                                                <span>{course.code}</span>
                                            </div>

                                            <div className="detail-row">
                                                <span>Course Name</span>
                                                <span>{course.name}</span>
                                            </div>

                                            <div className="detail-row">
                                                <span>Course Type</span>
                                                <span>
                                                    {course.course_type || "—"}
                                                </span>
                                            </div>

                                            <div className="detail-row">
                                                <span>Duration</span>
                                                <span>
                                                    {course.duration} Months
                                                </span>
                                            </div>

                                            <div className="detail-row">
                                                <span>Monthly Fee</span>
                                                <span>
                                                    ₹{course.monthly_fee || "—"}
                                                </span>
                                            </div>

                                            <div className="detail-row">
                                                <span>Start Date</span>
                                                <span>
                                                    {course.start_date || "—"}
                                                </span>
                                            </div>

                                            <div className="detail-row">
                                                <span>End Date</span>
                                                <span>
                                                    {course.end_date
                                                        ? course.end_date
                                                        : "In Progress"}
                                                </span>
                                            </div>

                                            <div className="detail-row">
                                                <span>Status</span>

                                                <span
                                                    className={
                                                        isRunning
                                                            ? "status-running"
                                                            : "status-completed"
                                                    }
                                                >
                                                    {course.status}
                                                </span>

                                            </div>

                                        </div>

                                    )}

                                </div>

                            </div>


                            {/* UPGRADE CONNECTOR */}

                            {!isLast && (

                                <div className="upgrade-connector">

                                    <div className="timeline-line"></div>

                                    <div className="upgrade-label">
                                        Upgraded
                                    </div>

                                </div>

                            )}

                        </div>

                    );

                })}

            </div>

        </div>

    );

}

export default CourseHistory;