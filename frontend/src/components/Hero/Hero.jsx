import "./Hero.css";
import { Link } from "react-router-dom";
function Hero() {
    return (
        <section className="hero">
            <div className="hero-content">
                
                {/* Main Heading and Subheading wrapper */}
                <div className="hero-header-group">
                    <h1>
                        Smart Computer <span className="text-gradient">Institute</span>
                    </h1>
                    <span className="hero-subheading">
                        Build Skills, Build Futures.
                    </span>
                </div>

                {/* Centered Badge right under the heading */}
                <div className="hero-badge-container">
                    <span className="hero-badge">
                        ISO 9001 : 2015 Certified Institute
                    </span>
                </div>

                {/* Clean Description */}
                <p className="hero-description">
                    Learn modern computer skills with practical training and <br className="desktop-only" /> 
                    expert guidance from industry professionals.
                </p>

                {/* Action Buttons */}
                <div className="hero-buttons">
                    <Link
                        to="/courses"
                        className="primary-btn"
                    >
                        Explore Courses
                    </Link>
                    <Link
                        to="/login"
                        className="secondary-btn"
                    >
                        Student Login
                    </Link>
                </div>

            </div>
        </section>
    );
}

export default Hero;