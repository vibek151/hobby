import { useEffect, useState } from "react";
import { getProfile } from "../services/profileService";
import "./PersonalDetails.css";
function PersonalDetails() {

    const [student, setStudent] = useState(null);

    useEffect(() => {

        async function fetchProfile() {

            try {

                const response = await getProfile();
                console.log(response.data); 
                setStudent(response.data);

            }

            catch (error) {

                console.log(error);

            }

        }

        fetchProfile();

    }, []);

    if (!student) {

        return <h1>Loading...</h1>;

    }

    
    return (
    <>
        {/* PERSONAL INFORMATION */}
        <div className="profile-card">

            <div className="profile-left">

                <h1>Personal Information</h1>

                <div className="detail-row">
                    <span>Name</span>
                    <span>{student.name}</span>
                </div>

                <div className="detail-row">
                    <span>Guardian Name</span>
                    <span>{student.guardian_name}</span>
                </div>

                <div className="detail-row">
                    <span>Gender</span>
                    <span>{student.gender}</span>
                </div>

                <div className="detail-row">
                    <span>Qualification</span>
                    <span>{student.qualification}</span>
                </div>

                <div className="detail-row">
                    <span>Email</span>
                    <span>{student.email}</span>
                </div>

                <div className="detail-row">
                    <span>Phone</span>
                    <span>{student.phone}</span>
                </div>

                <div className="detail-row">
                    <span>Date of Birth</span>
                    <span>{student.dob}</span>
                </div>

            </div>

            <div className="profile-right">

                <img
                    src={student.passport_photo}
                    alt="Student"
                    className="student-photo"
                />

                <h3>{student.name}</h3>

                <p>{student.student_id}</p>

                <span
                    className={
                        student.is_suspended
                            ? "status-suspended"
                            : student.is_active
                            ? "status-active"
                            : "status-inactive"
                    }
                >
                    {
                        student.is_suspended
                            ? "Suspended"
                            : student.is_active
                            ? "Active"
                            : "Inactive"
                    }
                </span>
                
                <a
                    href={student.form_pdf}
                    target="_blank"
                    rel="noreferrer"
                    className="pdf-button"
                >
                    📄 Download PDF
                </a>



            </div>

        </div>


        {/* ADDRESS & DOCUMENTS */}
        <div className="info-section">

            <h2>Address & Documents</h2>

            <div className="detail-row">
                <span>Address</span>
                <span>{student.address}</span>
            </div>

            <div className="detail-row">
                <span>Document Type</span>
                <span>{student.document_type}</span>
            </div>

            <div className="detail-row">
                <span>Document Number</span>
                <span>{student.document_number}</span>
            </div>

        </div>


        {/* COURSE DETAILS */}
        <div className="info-section">

            <h2>Course Details</h2>
            <div className="detail-row">
                    <span>Course</span>
                    <span>{student.course}</span>
                </div>
            <div className="detail-row">
                <span>Course Type</span>
                <span>{student.course_type}</span>
            </div>

            <div className="detail-row">
                <span>Duration</span>
                <span>{student.course_duration} Months</span>
            </div>

            <div className="detail-row">
                <span>Monthly Fee</span>
                <span>₹{student.monthly_fee}</span>
            </div>

            <div className="detail-row">
                <span>Admission Date</span>
                <span>{student.admission_date}</span>
            </div>

        </div>


        {/* PAYMENT INFORMATION */}
        <div className="info-section">

            <h2>Payment Information</h2>

            <div className="detail-row">
                <span>Admission Amount</span>
                <span>₹{student.admission_amount}</span>
            </div>

            {
                student.advance_fees > 0 && (
                    <div className="detail-row">
                        <span>Advance Fees</span>
                        <span>₹{student.advance_fees}</span>
                    </div>
                )
            }
    
            {
                student.discount_percent > 0 && (
                    <div className="detail-row">
                        <span>Discount</span>
                        <span>{student.discount_percent}%</span>
                    </div>
                )
            }

            {
                student.discount_percent > 0 && (
                    <div className="detail-row">
                        <span>Final Amount</span>
                        <span>₹{student.final_amount}</span>
                    </div>
                )
            }

            <div className="detail-row">
                <span>Payment Method</span>
                <span>{student.admission_pay_via}</span>
            </div>

            <div className="detail-row">
                <span>Receipt Number</span>
                <span>{student.receipt_no}</span>
            </div>

        </div>


        {/* SYSTEM INFORMATION */}
        <div className="info-section">

            <h2>System Information</h2>

            <div className="detail-row">
                <span>Suspended</span>
                <span>{student.is_suspended ? "Yes" : "No"}</span>
            </div>

            <div className="detail-row">
                <span>Course Completed</span>
                <span>{student.course_completed ? "Yes" : "No"}</span>
            </div>

            <div className="detail-row">
                <span>Freeze Status</span>
                <span>{student.is_freezed ? "Yes" : "No"}</span>
            </div>

        </div>

    </>
    );
    


}

export default PersonalDetails;