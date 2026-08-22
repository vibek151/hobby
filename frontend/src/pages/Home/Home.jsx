import { useEffect, useState } from "react";
import { Helmet } from "react-helmet-async";
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
        <Helmet>
            <title>
                SMART COMPUTER INSTITUTE | Computer Courses in Siliguri
            </title>

            <meta
                name="description"
                content="SMART COMPUTER INSTITUTE in Siliguri offers professional computer courses including Office Applications, Advanced Excel, Tally, Accounting, Python, Web Development and more."
            />

            <meta
                name="keywords"
                content="SMART COMPUTER INSTITUTE, computer institute in Siliguri, computer courses in Siliguri, computer training Siliguri, Tally course Siliguri, Python course Siliguri, Excel course Siliguri"
            />

            <link
                rel="canonical"
                href="https://smartci.in/"
            />

            {/* Open Graph */}
            <meta
                property="og:title"
                content="SMART COMPUTER INSTITUTE | Computer Courses in Siliguri"
            />

            <meta
                property="og:description"
                content="Professional computer courses and practical training at SMART COMPUTER INSTITUTE, Siliguri."
            />

            <meta
                property="og:type"
                content="website"
            />

            <meta
                property="og:url"
                content="https://smartci.in/"
            />

            <meta
                property="og:site_name"
                content="SMART COMPUTER INSTITUTE"
            />

            {/* Twitter */}
            <meta
                name="twitter:card"
                content="summary"
            />

            <meta
                name="twitter:title"
                content="SMART COMPUTER INSTITUTE | Computer Courses in Siliguri"
            />

            <meta
                name="twitter:description"
                content="Professional computer courses and practical training at SMART COMPUTER INSTITUTE, Siliguri."
            />

            <script type="application/ld+json">
                {JSON.stringify({
                    "@context": "https://schema.org",
                    "@type": "EducationalOrganization",
                    "@id": "https://smartci.in/#organization",

                    "name": "SMART COMPUTER INSTITUTE",

                    "url": "https://smartci.in/",

                    "logo": "https://smartci.in/logo.png",

                    "description":
                        "SMART COMPUTER INSTITUTE is a computer training institute in Siliguri offering professional computer courses and practical training.",

                    "telephone": [
                        "+91-8514956985",
                        "+91-8388047150"
                    ],

                    "address": {
                        "@type": "PostalAddress",
                        "streetAddress":
                            "Beside Sriguru Vidyamandir, Champasari Anchal",
                        "addressLocality": "Siliguri",
                        "addressRegion": "West Bengal",
                        "addressCountry": "IN"
                    },

                    "sameAs": [
                        "https://www.facebook.com/share/1HdtNNpK3K/",
                        "https://www.instagram.com/smart_computer_institute_2022?igsi=bGxscnh3Z3p1bjA2"
                    ],

                    "hasMap":
                        "https://maps.app.goo.gl/57e79mYhtSdkKtiq9"
                })}
            </script>



        </Helmet>
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