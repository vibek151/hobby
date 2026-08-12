import { useEffect, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { getPopularCourses } from "../../services/courseService";
import "./Courses.css";

function Courses() {
    const [courses, setCourses] = useState([]);
    const navigate = useNavigate();

    useEffect(() => {
        async function fetchCourses() {
            try {
                const response = await getPopularCourses();
                setCourses(response.data);
            } catch (error) {
                console.error("Error fetching popular courses:", error);
            }
        }
        fetchCourses();
    }, []);

    return (
        <section className="courses">
            <div className="courses-header-section">
                <h2>Popular Courses</h2>
                <div className="section-subtitle-line"></div>
            </div>

            <div className="course-grid">
                {courses.map((course) => (
                    /* Main card click redirects to the global all courses catalog view */
                    <div
                        className="course-card"
                        key={course.code}
                    >
                        {/* Course Image Wrapper */}
                        {course.course_image && (
                            <div className="course-image-container">
                                <img
                                    className="course-image"
                                    src={`${import.meta.env.VITE_API_URL}${course.course_image}`}
                                    alt={course.name}
                                />
                                <div className="image-overlay-shade"></div>
                            </div>
                        )}

                        {/* Content Area */}
                        <div className="course-card-body">
                            <span className="course-card-badge">{course.code}</span>
                            <p className="course-card-title">{course.name}</p>
                        </div>

                        {/* Bottom Bar: Explore Course*/}
                        <Link
                            to="/courses" 
                            className="card-action-trigger"
                        >
                            <span>Explore Course</span>
                            <svg fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M14 5l7 7m0 0l-7 7m7-7H3" />
                            </svg>
                        </Link>

                        {/* Corner Slide Element: Redirects to the explicit course detail blueprint */}
                        <button 
                            className="dashboard-slide-trigger"
                            onClick={(e) => {
                                e.preventDefault();  // Stops link navigation to /courses
                                e.stopPropagation(); // Prevents event bubbling up to the card
                                navigate(`/courses/${course.code}`); // Routes to specific single course template
                            }}
                            
                        >
                            <span className="slide-text">Know More →</span>
                        </button>
                    </div>
                ))}
            </div>
        </section>
    );
}

export default Courses;