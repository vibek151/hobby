import { useEffect, useState } from "react";
import { useParams, Link } from "react-router-dom";
import { Helmet } from "react-helmet-async";
import { getCourseDetail } from "../../services/courseService";
import LeadForm from "../../components/LeadForm/LeadForm";
import "./CourseDetailPage.css";

function CourseDetailPage() {
    const { code } = useParams();
    const [course, setCourse] = useState(null);
    const [isLoading, setIsLoading] = useState(true);
    const [error, setError] = useState(null);
    const [showLeadForm, setShowLeadForm] = useState(false);
    useEffect(() => {
        async function fetchCourse() {
            try {
                setIsLoading(true);
                const response = await getCourseDetail(code);
                console.log(response.data);
                setCourse(response.data);
                setError(null);
            } catch (err) {
                console.error("Error fetching course details:", err);
                setError("Unable to retrieve course data at this time.");
            } finally {
                setIsLoading(false);
            }
        }
        fetchCourse();
    }, [code]);

    if (isLoading) {
        return (
            <div className="course-detail-status">
                <div className="shimmer-loader-circle"></div>
                <p>Loading course dashboard...</p>
            </div>
        );
    }

    if (error || !course) {
        return (
            <div className="course-detail-status error-wrapper">
                <p>{error || "Course not found."}</p>
                <Link to="/courses" className="back-btn">← Back to All Courses</Link>
            </div>
        );
    }
    <Helmet>
        <title>
            {course.name} Course in Siliguri | SMART COMPUTER INSTITUTE
        </title>

        <meta
            name="description"
            content={`${course.name} course in Siliguri at SMART COMPUTER INSTITUTE. Learn practical computer skills with structured training, course curriculum, fees and admission information.`}
        />

        <link
            rel="canonical"
            href={`https://smartci.in/courses/${encodeURIComponent(course.code)}`}
        />

        <meta
            property="og:title"
            content={`${course.name} Course in Siliguri | SMART COMPUTER INSTITUTE`}
        />

        <meta
            property="og:description"
            content={`Learn ${course.name} at SMART COMPUTER INSTITUTE, Siliguri. View curriculum, duration, fees and admission information.`}
        />

        <meta
            property="og:type"
            content="website"
        />

        <meta
            property="og:url"
            content={`https://smartci.in/courses/${encodeURIComponent(course.code)}`}
        />

        <script type="application/ld+json">
            {JSON.stringify({
                "@context": "https://schema.org",
                "@type": "Course",

                "name": course.name,

                "description":
                    `${course.name} course in Siliguri at SMART COMPUTER INSTITUTE. ` +
                    `Learn practical computer skills through structured professional training.`,

                "courseCode": course.code,

                "url": `https://smartci.in/courses/${encodeURIComponent(course.code)}`,

                "inLanguage": "en-IN",

                "educationalLevel": "Professional",

                "provider": {
                    "@type": "EducationalOrganization",
                    "name": "SMART COMPUTER INSTITUTE",
                    "url": "https://smartci.in/",
                    "address": {
                        "@type": "PostalAddress",
                        "addressLocality": "Siliguri",
                        "addressRegion": "West Bengal",
                        "addressCountry": "IN"
                    }
                },

                "offers": {
                    "@type": "Offer",
                    "price": String(course.monthly_fee),
                    "priceCurrency": "INR",
                    "url": `https://smartci.in/courses/${encodeURIComponent(course.code)}`,
                    "availability": "https://schema.org/InStock"
                }
            })}
        </script>
    </Helmet>

    // Dynamic Syllabus Module Parsing
    const syllabusLines = course.syllabus ? course.syllabus.split("\n") : [];
    const syllabusModules = [];
    let currentModule = null;

    syllabusLines.forEach((line) => {
        const trimmed = line.trim();
        if (!trimmed) return;

        const isHeader = line.startsWith(trimmed) && 
                         !line.startsWith("    ") && 
                         !line.startsWith("\t") &&
                         (trimmed.length < 25 || !trimmed.includes("2007")); 

        if (isHeader || syllabusModules.length === 0) {
            currentModule = { title: trimmed, topics: [] };
            syllabusModules.push(currentModule);
        } else {
            currentModule.topics.push(trimmed);
        }
    });

    const isLargeSyllabus = syllabusModules.length > 2;

    return (
        <>
        <div className="course-detail-container">
            {/* MAIN DASHBOARD MATRIX GRID (Breadcrumb nav removed directly from here) */}
            <div className="course-dashboard-grid">
                
                {/* LEFT MAIN COLUMN Content */}
                <main className="dashboard-main-content">
                    
                    {/* HERO HEADER SECTION CARD */}
                    <header className="course-hero-card">
                        <span className="course-code-badge">{course.code}</span>
                        <h1>{course.name}</h1>
                        <p>Industry-oriented professional training blueprint meticulously structured to build practical computational capacity and execution expertise.</p>
                        
                        {/* CORE QUICK METRICS BAR UPGRADED */}
                        <div className="hero-metrics-row">
                            <div className="metric-pill pill-duration">
                                <div className="metric-icon-box">
                                    <svg fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                                    </svg>
                                </div>
                                <div className="metric-text-wrapper">
                                    <span className="metric-tagline">DURATION</span>
                                    <span className="metric-hero-value">{course.duration} Months</span>
                                </div>
                            </div>

                            <div className="metric-pill pill-registration">
                                <div className="metric-icon-box">
                                    <svg fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
                                    </svg>
                                </div>
                                <div className="metric-text-wrapper">
                                    <span className="metric-tagline">ADMISSION</span>
                                    <span className="metric-hero-value">₹{course.admission_fee}</span>
                                </div>
                            </div>
                        </div>
                    </header>

                    {/* DYNAMIC SCROLLABLE CURRICULUM SECTION CARD */}
                    <section className="dashboard-section-card syllabus-wrapper">
                        <div className="section-header">
                            <div className="title-indicator"></div>
                            <h2>Course Curriculum Breakdown</h2>
                        </div>
                        
                        <div className="scrollable-curriculum-viewport">
                            <div className="syllabus-modules-matrix">
                                {syllabusModules.map((module, idx) => (
                                    <div key={idx} className="curriculum-module-item">
                                        <div className="module-item-header">
                                            <span className="module-tag">M{idx + 1}</span>
                                            <h4>{module.title}</h4>
                                        </div>
                                        {module.topics.length > 0 ? (
                                            <ul className="module-subtopics-list">
                                                {module.topics.map((topic, tIdx) => (
                                                    <li key={tIdx}>
                                                        <span className="subtopic-dot"></span>
                                                        <span className="subtopic-name">{topic}</span>
                                                    </li>
                                                ))}
                                            </ul>
                                        ) : (
                                            <p className="empty-module-fallback">Core Fundamental Foundations</p>
                                        )}
                                    </div>
                                ))}
                            </div>
                        </div>

                        {/* INTERACTIVE SCROLL PROMPT HELP CUE */}
                        {isLargeSyllabus && (
                            <div className="scroll-hint-badge">
                                <span>Scroll to explore modules</span>
                                <div className="hint-arrow">
                                    <svg fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M19 14l-7 7m0 0l-7-7m7 7V3" /></svg>
                                </div>
                            </div>
                        )}
                    </section>

                    {/* ACQUIRED EXAMS SECTION CARD */}
                    <section className="dashboard-section-card">
                        <div className="section-header">
                            <div className="title-indicator green-accent"></div>
                            <h2>Required System Certifications</h2>
                        </div>
                        <div className="certifications-flex-row">
                            {course.exams.map((exam, index) => (
                                <div className="cert-badge" key={index}>
                                    <svg fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M5 13l4 4L19 7" />
                                    </svg>
                                    <span>{exam}</span>
                                </div>
                            ))}
                        </div>
                    </section>
                </main>

                {/* RIGHT COLUMN STICKY CONTEXT BLOCK CARD */}
                <aside className="dashboard-sidebar-column">
                    <div className="premium-action-sidebar-card">
                        <div className="sidebar-pricing-display">
                            <span className="pricing-label">Tuition Rate</span>
                            <div className="pricing-digits-row">
                                <span className="currency">₹</span>
                                <span className="amount">{course.monthly_fee}</span>
                                <span className="interval">/ mo</span>
                            </div>
                        </div>

                        <div className="sidebar-perks-list">
                            <div className="perk-item">
                                <svg fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M5 13l4 4L19 7" /></svg>
                                <span>1-on-1 Practical Labs</span>
                            </div>
                            <div className="perk-item">
                                <svg fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M5 13l4 4L19 7" /></svg>
                                <span>Live Capstone Demos</span>
                            </div>
                            <div className="perk-item">
                                <svg fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M5 13l4 4L19 7" /></svg>
                                <span>Placement Assistance</span>
                            </div>
                        </div>

                        <div className="sidebar-actions-group">
                            <button
                                className="primary-enroll-btn"
                                onClick={() => setShowLeadForm(true)}
                            >
                                Apply For Program
                            </button>
                            
                            <a
                                href="https://wa.me/918514956985?text=Hello!%20I%20have%20a%20query%20regarding%20your%20courses."
                                target="_blank"
                                rel="noopener noreferrer"
                                className="secondary-consult-btn"
                            >
                                Speak with Advisor
                            </a>
                        </div>
                    </div>
                </aside>

            </div>
        </div>
        {showLeadForm && (
            <LeadForm
                course={course}
                onClose={() => setShowLeadForm(false)}
            />
        )}
        </>
    );
}

export default CourseDetailPage;