import React, { useState, useRef, useEffect } from "react";
import { askAIAdvisor } from "../../services/contactService";
import "./AIChatbot.css";

const AIChatbot = ({ onClose }) => {
    const [messages, setMessages] = useState([
        {
            id: 1,
            sender: "ai",
            text: "Welcome to Smart Computer Institute! 🎓\nI am SIPA, your assistant. Click an option below to find all the details you need before joining our classes!",
            time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
        }
    ]);
    const [loading, setLoading] = useState(false);
    
    const bodyEndRef = useRef(null);
    const windowRef = useRef(null);

    useEffect(() => {
        bodyEndRef.current?.scrollIntoView({ behavior: "smooth" });
    }, [messages, loading]);

    // Handle outside clicks safely
    const handleOverlayClick = (e) => {
    // Force closure ONLY if the user clicked the dark background backdrop directly
        if (e.target.classList.contains("smart-assistant-backdrop-overlay")) {
            if (onClose) onClose();
        }
    };

    // Dedicated clean closer that isolates the event from the backdrop
    const handleExplicitClose = (e) => {
        e.stopPropagation(); // ⚡ Prevents the click from bubbling up to the backdrop overlay
        if (onClose) onClose();
    };

    const handleOptionClick = async (optionValue, optionLabel) => {
        if (loading) return;

        const userTime = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
        const userMsg = { id: Date.now(), sender: "user", text: optionLabel, time: userTime };
        setMessages((prev) => [...prev, userMsg]);
        
        setLoading(true);

        try {
            const response = await askAIAdvisor(optionValue);
            const aiTime = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
            const aiMsg = { id: Date.now() + 1, sender: "ai", text: response.data.reply, time: aiTime };
            setMessages((prev) => [...prev, aiMsg]);
        } catch (error) {
            const aiTime = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
            const errorMsg = { id: Date.now() + 1, sender: "ai", text: "Unable to load details. Please try again!", time: aiTime };
            setMessages((prev) => [...prev, errorMsg]);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="smart-assistant-backdrop-overlay" onClick={handleOverlayClick}>
            <div className="assistant-window" ref={windowRef} onClick={(e) => e.stopPropagation()}>
                
                {/* Header Section */}
                <div className="assistant-header">
                    <div className="profile-group">
                        <div className="mini-avatar">SIPA</div>
                        <div className="text-group">
                            <h3>SIPA</h3>
                            <div className="status-badge">
                                <span className="green-dot"></span> online
                            </div>
                        </div>
                    </div>
                    {/* Fixed explicit close button execution */}
                    <button className="dismiss-btn" onClick={handleExplicitClose} aria-label="Close Chat">✕</button>
                </div>

                {/* Chat Body */}
                <div className="assistant-body">
                    {messages.map((msg) => (
                        <div key={msg.id} className={`msg-row ${msg.sender}`}>
                            <div className="bubble-card">
                                <p className="bubble-markdown">
                                    {msg.text.split("\n").map((line, lineIdx) => (
                                        <span key={lineIdx} style={{ display: "block" }}>
                                            {line.split(/(\*\*.*?\*\*)/g).map((part, partIdx) => {
                                                if (part.startsWith("**") && part.endsWith("**")) {
                                                    return <strong key={partIdx}>{part.slice(2, -2)}</strong>;
                                                }
                                                return part;
                                            })}
                                        </span>
                                    ))}
                                </p>
                                <span className="bubble-time">{msg.time}</span>
                            </div>
                        </div>
                    ))}
                    {loading && (
                        <div className="msg-row ai">
                            <div className="bubble-card typing-indicator">
                                <span></span><span></span><span></span>
                            </div>
                        </div>
                    )}
                    <div ref={bodyEndRef} />
                </div>

                {/* Footer Option Grid Layout */}
                <div className="chatbot-footer-options">
                    <p className="footer-title">Select a topic to review details:</p>
                    <div className="options-grid">
                        <button disabled={loading} onClick={() => handleOptionClick("1", "🎓 Available Online Courses")}>🎓 View Courses</button>
                        <button disabled={loading} onClick={() => handleOptionClick("2", "💰 Admission & Monthly Fees")}>💰 Check Fees</button>
                        <button disabled={loading} onClick={() => handleOptionClick("3", "📅 Batch Schedule & Timings")}>📅 Class Timings</button>
                        <button disabled={loading} onClick={() => handleOptionClick("4", "💻 System & App Requirements")}>💻 Requirements</button>
                        <button disabled={loading} onClick={() => handleOptionClick("5", "📜 Certificates & Accreditation")}>📜 Certification</button>
                        <button disabled={loading} onClick={() => handleOptionClick("6", "📞 How to Enroll / Contacts")}>📞 How to Join</button>
                    </div>
                </div>

            </div>
        </div>
    );
};

export default AIChatbot; 