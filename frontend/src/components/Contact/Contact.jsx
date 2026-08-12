import { useEffect, useState } from "react";
import { getWebsiteContact } from "../../services/contactService";
import "./Contact.css";
import {
    FaMapMarkerAlt,
    FaPhoneAlt,
    FaEnvelope,
    FaWhatsapp
} from "react-icons/fa";

function Contact() {
    const [contact, setContact] = useState(null);

    useEffect(() => {
        async function fetchContact() {
            try {
                const response = await getWebsiteContact();
                setContact(response.data);
            } catch (error) {
                console.error("Error fetching contact information:", error);
            }
        }
        fetchContact();
    }, []);

    const displayData = contact || {
        address: "Champasari Main Road, Siliguri",
        phone_number_1: "+91 XXXXX XXXXX",
        phone_number_2: "",
        phone_number_3: "",
        email_address: "info@smartcomputerinstitute.com",
        whatsapp_number_1: "+91 XXXXX XXXXX",
        whatsapp_number_2: ""
    };

    return (
        <footer className="site-footer">
            <div className="footer-container">

                {/* Address */}
                <div className="footer-card">
                    <h4 className="footer-title">
                        <span className="footer-icon-circle">
                            <FaMapMarkerAlt className="footer-icon" />
                        </span>
                        Address
                    </h4>
                    <p className="footer-text">
                        {displayData.google_maps_link ? (
                            <a 
                                href={displayData.google_maps_link} 
                                target="_blank" 
                                rel="noopener noreferrer"
                                className="footer-address-link"
                            >
                                {displayData.address}
                            </a>
                        ) : (
                            displayData.address
                        )}
                    </p>
                </div>

                {/* Phone Numbers */}
                <div className="footer-card">
                    <h4 className="footer-title">
                        <span className="footer-icon-circle">
                            <FaPhoneAlt className="footer-icon" />
                        </span>
                        Phone
                    </h4>
                    <div className="footer-links-stack">
                        {displayData.phone_number_1 && (
                            <a href={`tel:${displayData.phone_number_1}`} className="footer-link">
                                {displayData.phone_number_1}
                            </a>
                        )}
                        {displayData.phone_number_2 && (
                            <a href={`tel:${displayData.phone_number_2}`} className="footer-link">
                                {displayData.phone_number_2}
                            </a>
                        )}
                        {displayData.phone_number_3 && (
                            <a href={`tel:${displayData.phone_number_3}`} className="footer-link">
                                {displayData.phone_number_3}
                            </a>
                        )}
                    </div>
                </div>

                {/* Email */}
                <div className="footer-card">
                    <h4 className="footer-title">
                        <span className="footer-icon-circle">
                            <FaEnvelope className="footer-icon" />
                        </span>
                        Email
                    </h4>
                    <a href={`mailto:${displayData.email_address}`} className="footer-link">
                        {displayData.email_address}
                    </a>
                </div>

                {/* WhatsApp */}
                <div className="footer-card">
                    <h4 className="footer-title">
                        <span className="footer-icon-circle">
                            <FaWhatsapp className="footer-icon" />
                        </span>
                        WhatsApp
                    </h4>
                    <div className="footer-links-stack">
                        {displayData.whatsapp_number_1 && (
                            <a 
                                href={`https://wa.me/${displayData.whatsapp_number_1.replace(/[^0-9]/g, "")}`} 
                                target="_blank" 
                                rel="noopener noreferrer" 
                                className="footer-link"
                            >
                                {displayData.whatsapp_number_1}
                            </a>
                        )}
                        {displayData.whatsapp_number_2 && (
                            <a 
                                href={`https://wa.me/${displayData.whatsapp_number_2.replace(/[^0-9]/g, "")}`} 
                                target="_blank" 
                                rel="noopener noreferrer" 
                                className="footer-link"
                            >
                                {displayData.whatsapp_number_2}
                            </a>
                        )}
                    </div>
                </div>

            </div>

            <div className="footer-bottom">
                <p>
                    &copy; {new Date().getFullYear()} Smart Computer Institute. All Rights Reserved.
                </p>
            </div>
        </footer>
    );
}

export default Contact;