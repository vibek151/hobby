import { useState } from "react";
import { verifyCertificate } from "../../services/certificateService";
import "./Verify.css";

function Verify() {
    const [certificateNo, setCertificateNo] = useState("");
    const [result, setResult] = useState(null);
    const [loading, setLoading] = useState(false);

    async function handleVerify() {
        if (!certificateNo.trim()) return;
        setLoading(true);
        try {
            const response = await verifyCertificate(certificateNo);
            setResult(response.data);
        } catch {
            setResult({ valid: false });
        } finally {
            setLoading(false);
        }
    }

    return (
        <section className="verify-page">
            <div className="verify-box">
                <h1>Verify Certificate & Marksheet</h1>
                <p className="verify-desc">
                    Enter the certificate or marksheet verification number to authenticate its validity.
                </p>

                <div className="input-group">
                    <input
                        type="text"
                        value={certificateNo}
                        onChange={(e) => setCertificateNo(e.target.value)}
                        placeholder="Enter Certificate / Marksheet Number"
                        disabled={loading}
                    />
                    <button onClick={handleVerify} disabled={loading}>
                        {loading ? "Verifying..." : "Verify"}
                    </button>
                </div>

                {result && (
                    result.valid ? (
                        <div className="verify-result success">
                            <div className="result-card">
                                <div className="result-header">
                                    <div className="header-text">
                                        <span className="verified-badge">✓ VERIFIED</span>
                                        <h2>Verification Successful</h2>
                                        <p className="verify-subtitle">
                                            This document is authentic and officially issued by Smart Computer Institute.
                                        </p>
                                    </div>
                                    <div className="photo-container">
                                        {result.photo ? (
                                            <img
                                                className="student-photo"
                                                src={result.photo}
                                                alt={result.student_name}
                                            />
                                        ) : (
                                            <div className="photo-placeholder">No Photo</div>
                                        )}
                                    </div>
                                </div>

                                <div className="result-grid">
                                    <div className="result-row">
                                        <span className="label">Student Name</span>
                                        <strong className="value">{result.student_name}</strong>
                                    </div>

                                    <div className="result-row">
                                        <span className="label">Course</span>
                                        <strong className="value text-wrap">{result.course}</strong>
                                    </div>

                                    <div className="result-row">
                                        <span className="label">Certificate Number</span>
                                        <strong className="value code-font">{result.certificate_no}</strong>
                                    </div>

                                    <div className="result-row">
                                        <span className="label">Completion Date</span>
                                        <strong className="value">{result.end_date}</strong>
                                    </div>
                                </div>
                            </div>
                        </div>
                    ) : (
                        <div className="verify-result error">
                            <div className="result-card invalid-card">
                                <span className="invalid-badge">✕ INVALID</span>
                                <h2>Record Not Found</h2>
                                <p className="verify-subtitle">
                                    No certificate or marksheet could be identified with the provided registration parameters.
                                </p>
                            </div>
                        </div>
                    )
                )}
            </div>
        </section>
    );
}

export default Verify;