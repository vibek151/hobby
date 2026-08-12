import { useEffect, useState } from "react";
import api from "../services/api";
import "./Certificates.css";
import { FiAward, FiFileText } from "react-icons/fi";

function Certificates() {

    const [certificates, setCertificates] = useState([]);

    useEffect(() => {
        fetchCertificates();
    }, []);

    async function fetchCertificates() {

        try {

            const res = await api.get("/student/certificates-api/");

            if (res.data.success) {
                setCertificates(res.data.certificates);
            }

        } catch (err) {
            console.error(err);
        }

    }

    return (

        <div>

            <h1 className="certificate-title">
                Certificates
            </h1>

            {certificates.length === 0 ? (

                <p>No certificates available.</p>

            ) : (

                certificates.map((certificate) => (

                    <div
                        className="certificate-card"
                        key={certificate.certificate_no}
                    >

                        <div className="certificate-header">

                            <div>

                                <h2>
                                    {certificate.course}
                                </h2>

                                <p>
                                    Certificate No : {certificate.certificate_no}
                                </p>

                                <p>
                                    Uploaded On : {new Date(certificate.upload_date).toLocaleDateString("en-GB")}
                                </p>

                            </div>

                        </div>

                        <div className="certificate-buttons">

                            {certificate.certificate_file && (
                                <button
                                    className="certificate-btn"
                                    onClick={() =>
                                        window.open(
                                            `${import.meta.env.VITE_API_URL}${certificate.certificate_file}`,
                                            "_blank"
                                        )
                                    }
                                >
                                    <FiAward />
                                    <span>Download Certificate</span>
                                </button>
                            )}

                            {certificate.marksheet_file && (
                                <button
                                    className="marksheet-btn"
                                    onClick={() =>
                                        window.open(
                                            `${import.meta.env.VITE_API_URL}${certificate.marksheet_file}`,
                                            "_blank"
                                        )
                                    }
                                >
                                    <FiFileText />
                                    <span>Download Marksheet</span>
                                </button>
                            )}

                        </div>

                    </div>

                ))

            )}

        </div>

    );

}

export default Certificates;