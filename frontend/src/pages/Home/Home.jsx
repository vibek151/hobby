import { useEffect, useState } from "react";
import Hero from "../../components/Hero/Hero";
import Stats from "../../components/Stats/Stats";
import Courses from "../../components/Courses/Courses";
import Features from "../../components/Features/Features";
import Testimonials from "../../components/Testimonials/Testimonials";
import Gallery from "../../components/Gallery/Gallery";
import Contact from "../../components/Contact/Contact";
import { Link } from "react-router-dom";
import "./Home.css";

function Home() {
    const [showNav, setShowNav] = useState(false);

    useEffect(() => {
        const handleScroll = () => {
        if (
            window.scrollY >
            window.innerHeight - 150
        ) {
            setShowNav(true);
        } else {
            setShowNav(false);
        }
    };

        window.addEventListener(
            "scroll",
            handleScroll
        );

        return () =>
            window.removeEventListener(
                "scroll",
                handleScroll
            );
    }, []);

    return (
        <>
            <div
                className={`floating-nav ${
                    showNav ? "show" : ""
                }`}
            >
                <Link to="/courses">
                    All Courses
                </Link>

                <Link to="/about">
                    About Us
                </Link>

                <Link to="/franchises">
                    All Franchise
                </Link>

                <Link to="/verify">
                    Verify Certificate
                </Link>
            </div>

            <Hero />
            <Stats />
            <Courses />
            <Features />
            <Testimonials />
            <Gallery />
            <Contact />
        </>
    );
}

export default Home;