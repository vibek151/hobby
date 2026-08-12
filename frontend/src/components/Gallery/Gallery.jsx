import { useEffect, useState } from "react";
import api from "../../services/api";
import "./Gallery.css";

function Gallery() {

    const [images, setImages] = useState([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {

        async function fetchGallery() {

            try {

                const response = await api.get(
                    "/api/website/gallery/"
                );

                setImages(response.data);

            } catch (error) {

                console.error(
                    "Error fetching gallery:",
                    error
                );

            } finally {

                setLoading(false);

            }
        }

        fetchGallery();

    }, []);

    // Hide entire section if no images exist
    if (!loading && images.length === 0) {
        return null;
    }

    // Optional loading state
    if (loading) {
        return (
            <section className="gallery">

                <h2>
                    Our Gallery
                </h2>

                <div className="gallery-grid">

                    {[1, 2, 3].map((item) => (
                        <div
                            className="gallery-card skeleton"
                            key={item}
                        >
                        </div>
                    ))}

                </div>

            </section>
        );
    }

    return (

        <section className="gallery">

            <h2>
                Our Gallery
            </h2>

            <div className="gallery-grid">

                {images.map((item) => (

                    <div
                        className="gallery-card"
                        key={item.id}
                    >

                        <img
                            src={`${import.meta.env.VITE_API_URL}${item.image}`}
                            alt={item.title}
                        />

                    </div>

                ))}

            </div>

        </section>

    );

}

export default Gallery;