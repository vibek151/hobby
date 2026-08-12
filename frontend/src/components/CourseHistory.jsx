import { useEffect, useState } from "react";
import { getCourseHistory } from "../services/courseService";
import "./CourseHistory.css";

function CourseHistory() {

    const [courses, setCourses] = useState([]);

    useEffect(() => {

        async function fetchCourses() {

            const response = await getCourseHistory();

            console.log(response.data);

            setCourses(response.data.courses);

        }

        fetchCourses();

    }, []);

    return (

        <div className="history-container">

            <h1 className="history-title">
                Course History
            </h1>

            <div className="timeline">

                {
                    courses.map((course, index) => (

                        <div
                            className="timeline-item"
                            key={index}
                        >

                            <div className="timeline-left">

                                <div
                                    className={
                                        course.status === "Running"
                                            ? "timeline-circle running-circle"
                                            : "timeline-circle completed-circle"
                                    }
                                >
                                </div>

                                {
                                    index !== courses.length - 1 &&
                                    <div className="timeline-line"></div>
                                }

                            </div>

                            <details className="history-card">

                                <summary>

                                    {course.code}
                                    {" - "}
                                    {course.name}

                                </summary>

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
                                        <span>Duration</span>
                                        <span>
                                            {course.duration} Months
                                        </span>
                                    </div>

                                    <div className="detail-row">
                                        <span>Start Date</span>
                                        <span>
                                            {course.start_date}
                                        </span>
                                    </div>

                                    <div className="detail-row">
                                        <span>End Date</span>
                                        <span>
                                            {
                                                course.end_date
                                                    ? course.end_date
                                                    : "In Progress"
                                            }
                                        </span>
                                    </div>

                                    <div className="detail-row">
                                        <span>Status</span>

                                        <span
                                            className={
                                                course.status === "Running"
                                                    ? "status-running"
                                                    : "status-completed"
                                            }
                                        >
                                            {course.status}
                                        </span>
                                    </div>

                                </div>

                            </details>

                        </div>

                    ))
                }

            </div>

        </div>

    );

}

export default CourseHistory;