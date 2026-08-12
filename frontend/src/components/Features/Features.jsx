import { useEffect, useState } from "react";
import api from "../../services/api";
import "./Features.css";

function Features() {

    const [features, setFeatures] = useState([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {

        async function fetchFeatures() {

            try {

                const response = await api.get(
                    "/api/website/why-choose-us/"
                );

                setFeatures(response.data);

            } catch (error) {

                console.error(
                    "Error fetching features:",
                    error
                );

            } finally {

                setLoading(false);

            }
        }

        fetchFeatures();

    }, []);

    // Hide entire section if no records exist
    if (!loading && features.length === 0) {
        return null;
    }

    // Optional loading state
    if (loading) {
        return (
            <section className="features">
                <h2>Why Choose Us</h2>

                <div className="features-grid">

                    {[1, 2, 3].map((item) => (
                        <div
                            className="feature-card skeleton"
                            key={item}
                        >
                        </div>
                    ))}

                </div>
            </section>
        );
    }

    return (

        <section className="features">

            <h2>
                Why Choose Us
            </h2>

            <div className="features-grid">

                {features.map((item) => (

                    <div
                        className="feature-card"
                        key={item.id}
                    >

                        <h3>
                            {item.title}
                        </h3>

                        <p>
                            {item.body}
                        </p>

                    </div>

                ))}

            </div>

        </section>

    );

}

export default Features;