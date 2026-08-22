import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { getCourses } from "../../services/courseService";
import { Helmet } from "react-helmet-async";
import "./CoursesPage.css";

function CoursesPage() {
    const [courses, setCourses] = useState([]);
    const [isLoading, setIsLoading] = useState(true);
    const [error, setError] = useState(null);

    useEffect(() => {
        async function fetchCourses() {
            try {
                setIsLoading(true);
                const response = await getCourses();
                setCourses(response.data || []);
            } catch (err) {
                console.error("Failed to fetch courses:", err);
                setError("Failed to load courses. Please try again later.");
            } finally {
                setIsLoading(false);
            }
        }

        fetchCourses();
    }, []);

    return (
        <>
        <Helmet>
            <title>Computer Courses in Siliguri | SMART COMPUTER INSTITUTE</title>

            <meta
                name="description"
                content="Explore professional computer courses at SMART COMPUTER INSTITUTE in Siliguri. Learn Office Applications, Advanced Excel, Tally, Accounting, Python, Web Development and more."
            />

            <meta
                name="keywords"
                content="computer courses in Siliguri, computer institute in Siliguri, computer training Siliguri, Tally course Siliguri, Python course Siliguri, Excel course Siliguri"
            />

            <link
                rel="canonical"
                href="https://smartci.in/courses"
            />

            <meta
                property="og:title"
                content="Computer Courses in Siliguri | SMART COMPUTER INSTITUTE"
            />

            <meta
                property="og:description"
                content="Explore professional computer courses and practical training programs at SMART COMPUTER INSTITUTE."
            />

            <meta
                property="og:type"
                content="website"
            />

            <meta
                property="og:url"
                content="https://smartci.in/courses"
            />
        </Helmet>
        <section className="courses-page">
            <div className="courses-header">
                <span className="subtitle-badge">Our Programs</span>
                <h1>Explore Professional Courses</h1>
                <p>
                    Advance your career with industry-mapped computer courses designed 
                    to build practical expertise and real-world skills.
                </p>
            </div>

            {isLoading && (
                <div className="courses-status">
                    <div className="spinner"></div>
                    <p>Loading curated courses...</p>
                </div>
            )}

            {error && (
                <div className="courses-status error-message">
                    <p>{error}</p>
                </div>
            )}

            {!isLoading && !error && (
                <div className="courses-grid">
                    {courses.map((course) => (
                        <article className="all-course-card" key={course.code}>
                            <div className="card-accent-line"></div>
                            
                            <div className="card-top">
                                <span className="course-code">{course.code}</span>
                                <h2 className="course-name">{course.name}</h2>
                            </div>

                            <div className="all-course-info">
                                <div className="info-item">
                                    <svg className="info-icon" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                                    </svg>
                                    <span><strong>Duration:</strong> {course.duration} Months</span>
                                </div>

                                <div className="info-item-price">
                                    <span className="price-label">Investment</span>
                                    <span className="price-amount">₹{course.monthly_fee}<small>/ month</small></span>
                                </div>
                            </div>

                            <Link className="all-course-btn" to={`/courses/${course.code}`}>
                                <span>View Details</span>
                                <svg className="btn-icon" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M14 5l7 7m0 0l-7 7m7-7H3" />
                                </svg>
                            </Link>
                        </article>
                    ))}
                </div>
            )}
        </section>
    </>
    );
}

export default CoursesPage;