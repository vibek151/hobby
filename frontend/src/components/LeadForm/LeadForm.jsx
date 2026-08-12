import { useState } from "react";
import { createLead } from "../../services/leadService";
import "./LeadForm.css";

function LeadForm({ course, onClose }) {
    const [formData, setFormData] = useState({
        name: "",
        phone: "",
        email: "",
        qualification: "",
        message: "",
    });

    const [loading, setLoading] = useState(false);

    const handleChange = (e) => {
        setFormData({
            ...formData,
            [e.target.name]: e.target.value,
        });
    };
        const handleSubmit = async (e) => {
        e.preventDefault();

        try {
            setLoading(true);

            const payload = {
                ...formData,
                course: course.id,
            };

            console.log("Sending payload:", payload);

            await createLead(payload);

            alert("Application submitted successfully!");

            setFormData({
                name: "",
                phone: "",
                email: "",
                qualification: "",
                message: "",
            });

            onClose();
        } catch (err) {
            console.error(err);
            alert("Unable to submit application.");
        } finally {
            setLoading(false);
        }
    };
        return (
        <div className="lead-overlay">
            <div className="lead-modal">

                <button
                    className="lead-close"
                    onClick={onClose}
                >
                    ×
                </button>

                <h2>Apply for Program</h2>
                <p className="lead-subtitle">
                    Complete the form below and our admission team will contact you shortly.
                </p>
                <div className="course-display">
                    <label>Selected Course</label>
                    <input
                        type="text"
                        value={course.name}
                        readOnly
                    />
                </div>

                <form onSubmit={handleSubmit}>

                    <input
                        name="name"
                        placeholder="Full Name"
                        value={formData.name}
                        onChange={handleChange}
                        required
                    />

                    <input
                        type="tel"
                        name="phone"
                        placeholder="Mobile Number"
                        value={formData.phone}
                        onChange={handleChange}
                        maxLength={10}
                        pattern="[0-9]{10}"
                        required
                    />

                    <input
                        name="email"
                        type="email"
                        placeholder="Email Address"
                        value={formData.email}
                        onChange={handleChange}
                    />

                    <input
                        name="qualification"
                        placeholder="Highest Qualification"
                        value={formData.qualification}
                        onChange={handleChange}
                    />

                    <textarea
                        name="message"
                        placeholder="Message (Optional)"
                        rows={4}
                        value={formData.message}
                        onChange={handleChange}
                    />

                    <button
                        type="submit"
                        className="submit-btn"
                        disabled={loading}
                    >
                        {loading ? "Submitting..." : "Submit Application"}
                    </button>

                </form>

            </div>
        </div>
    );
}

export default LeadForm;