import React, { useState } from "react";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import Profile from "./pages/Profile/Profile";
import Home from "./pages/Home/Home";
import StudentLogin from "./pages/StudentLogin/StudentLogin";
import OtpVerification from "./pages/OtpVerification/OtpVerification";
import Dashboard from "./pages/Dashboard/Dashboard";
import Verify from "./pages/Verify/Verify";
import CoursesPage from "./pages/CoursesPage/CoursesPage";
import CourseDetailPage from "./pages/CourseDetailPage/CourseDetailPage";

// Import your components
import AIChatbot from "./components/AIChatbot/AIChatbot";
import Contact from "./components/Contact/Contact";

function App() {
  // Starts hidden (false) so it doesn't block the screen on page load
  const [isChatOpen, setIsChatOpen] = useState(false);

  return (
    <BrowserRouter>
      {/* 1. Conditional Chat Window Layer */}
      {isChatOpen && <AIChatbot onClose={() => setIsChatOpen(false)} />}

      {/* 2. Floating Action Button to Open Chat (Always visible in bottom-right) */}
      {!isChatOpen && (
        <button 
          className="sipa-floating-trigger"
          onClick={(e) => {
            e.stopPropagation(); // Prevents layout click conflicts
            setIsChatOpen(true);
          }}
          aria-label="Open SIPA AI Assistant"
        >
          <span className="sipa-trigger-icon">💬</span>
          <span className="sipa-trigger-badge">SIPA</span>
        </button>
      )}

      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/login" element={<StudentLogin />} />
        <Route path="/verify-otp" element={<OtpVerification />} />
        <Route path="/dashboard" element={<Dashboard />} />
        <Route path="/profile" element={<Profile />} />
        <Route path="/verify" element={<Verify />} />
        <Route path="/courses" element={<CoursesPage />} />
        <Route path="/courses/:code" element={<CourseDetailPage />} />
      </Routes>

      {/* 3. Global Footer */}
      {/* <Contact /> */}
    </BrowserRouter>
  );
}

export default App;