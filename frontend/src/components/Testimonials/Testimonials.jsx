import { useEffect, useState } from "react";
import api from "../../services/api";
import "./Testimonials.css";

function Testimonials() {

    const [testimonials, setTestimonials] = useState([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {

        async function fetchTestimonials() {

            try {

                const response = await api.get(
                    "/api/website/testimonials/"
                );

                setTestimonials(response.data);

            } catch (error) {

                console.error(
                    "Error fetching testimonials:",
                    error
                );

            } finally {

                setLoading(false);

            }
        }

        fetchTestimonials();

    }, []);

    // Hide entire section if no testimonials exist
    if (!loading && testimonials.length === 0) {
        return null;
    }

    // Loading state
    if (loading) {
        return (
            <section className="testimonials">

                <h2>
                    What Our Students Say
                </h2>

                <div className="testimonial-grid">

                    {[1, 2, 3].map((item) => (
                        <div
                            className="testimonial-card skeleton"
                            key={item}
                        >
                        </div>
                    ))}

                </div>

            </section>
        );
    }

    return (

        <section className="testimonials">

            <h2>
                What Our Students Say
            </h2>

            <div className="testimonial-grid">

                {testimonials.map((item) => (

                    <div
                        className="testimonial-card"
                        key={item.id}
                    >

                        <div className="stars">
                            {"★".repeat(item.rating)}
                        </div>

                        <p>
                            {item.review}
                        </p>

                        <h4>
                            {item.name}
                        </h4>

                        {item.place && (
                            <span className="review-source">
                                {item.place}
                            </span>
                        )}

                    </div>

                ))}

            </div>

        </section>

    );

}

export default Testimonials;