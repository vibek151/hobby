import { useEffect, useState } from "react";
import api from "../../services/api"; // ⚡ Reusing your configured Axios instance
import "./Stats.css";

function Stats() {
    const [stats, setStats] = useState([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        async function fetchStats() {
            try {
                // Axios automatically uses your base URL and env configs
                const response = await api.get("/api/website/stats/");
                setStats(response.data);
            } catch (error) {
                console.error("Error fetching institute statistics:", error);
            } finally {
                setLoading(false);
            }
        }
        fetchStats();
    }, []);

    // 1. Loading State: Renders structural matching cards while waiting for Django
    if (loading) {
        return (
            <section className="stats loading-container">
                {[1, 2, 3, 4].map((n) => (
                    <div className="stat-card skeleton" key={n}>
                        <div className="skeleton-number"></div>
                        <div className="skeleton-text"></div>
                    </div>
                ))}
            </section>
        );
    }

    // 2. Safety Guard: If database is completely empty, don't break or render an empty section box
    if (stats.length === 0) {
        return null;
    }

    // 3. Dynamic Render Layout
    return (
        <section className="stats">
            {stats.map((item, index) => (
                <div className="stat-card" key={item.id || index}>
                    <h1>{item.number}</h1>
                    <p>{item.title}</p>
                </div>
            ))}
        </section>
    );
}

export default Stats;