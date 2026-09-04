// import { useEffect, useState } from "react";
// import { getMarks } from "../services/marksService";
// import "./Exam.css";

// function Exams() {

//     const [marks, setMarks] = useState([]);

//     useEffect(() => {

//         async function fetchMarks() {

//             try {

//                 const response = await getMarks();

//                 console.log(response.data);

//                 setMarks(response.data.marks);

//             }

//             catch (error) {

//                 console.log(error);

//             }

//         }

//         fetchMarks();

//     }, []);

//     return (

//         <div>

//             <h1>
//                 Exams & Marks
//             </h1>

//             {

//                 marks.map((mark, index) => (

//                     <div
//                         className="exam-card"
//                         key={index}
//                     >

//                         <div className="exam-header">

//                             <div>

//                                 <h2>
//                                     {mark.exam_name}
//                                 </h2>

//                                 <p>
//                                     Examination Result
//                                 </p>

//                             </div>

//                             <div
//                                 className={
//                                     mark.result === "Pass"
//                                         ? "result-pass"
//                                         : "result-fail"
//                                 }
//                             >

//                                 {mark.result}

//                             </div>

//                         </div>

//                         <div className="exam-row">

//                             <span>
//                                 Exam
//                             </span>

//                             <span>
//                                 {mark.exam_name}
//                             </span>

//                         </div>

//                         <div className="exam-row">

//                             <span>
//                                 Total Marks
//                             </span>

//                             <span>
//                                 {mark.total_marks}
//                             </span>

//                         </div>

//                         <div className="exam-row">

//                             <span>
//                                 Obtained Marks
//                             </span>

//                             <span>
//                                 {mark.marks}
//                             </span>

//                         </div>

//                         <div className="exam-row">

//                             <span>
//                                 Percentage
//                             </span>

//                             <span>

//                                 {
//                                     (
//                                         mark.marks /
//                                         mark.total_marks *
//                                         100
//                                     ).toFixed(1)
//                                 }%

//                             </span>

//                         </div>

//                     </div>

//                 ))

//             }

//         </div>

//     );

// }

// export default Exams;


// import { useEffect, useState } from "react";
// import { getMarks } from "../services/marksService";
// import "./Exam.css";

// function Exams() {
//     const [marks, setMarks] = useState([]);

//     useEffect(() => {
//         async function fetchMarks() {
//             try {
//                 const response = await getMarks();
//                 setMarks(response.data.marks);
//             } catch (error) {
//                 console.log(error);
//             }
//         }

//         fetchMarks();
//     }, []);

//     // Group exams by course
//     const groupedCourses = marks.reduce((groups, mark) => {
//         if (!groups[mark.course_id]) {
//             groups[mark.course_id] = {
//                 course_code: mark.course_code,
//                 course_name: mark.course_name,
//                 course_status: mark.course_status,
//                 exams: []
//             };
//         }

//         groups[mark.course_id].exams.push(mark);

//         return groups;
//     }, {});

//     return (
//         <div className="exams-container">

//             <h1 className="exams-title">Exams & Marks</h1>

//             {Object.values(groupedCourses).map((course) => (

//                 <div className="course-exam-section" key={course.course_code}>

//                     {/* Course Header */}
//                     <div className="course-exam-header">

//                         <div>
//                             <div className="course-title">
//                                 {course.course_code} - {course.course_name}
//                             </div>

//                             <div
//                                 className={
//                                     course.course_status === "Running"
//                                         ? "course-status running"
//                                         : "course-status completed"
//                                 }
//                             >
//                                 {course.course_status === "Running"
//                                     ? "🟢 Running Course"
//                                     : "🔴 Completed Course"}
//                             </div>
//                         </div>

//                     </div>

//                     {/* Exams */}
//                     <div className="exam-list">

//                         {course.exams.map((mark, index) => {

//                             const percentage =
//                                 (mark.marks / mark.total_marks) * 100;

//                             return (
//                                 <div className="exam-card" key={index}>

//                                     <div className="exam-header">

//                                         <div>
//                                             <h2>{mark.exam_name}</h2>
//                                             <p>Examination Result</p>
//                                         </div>

//                                         <div
//                                             className={
//                                                 mark.result === "Pass"
//                                                     ? "result-pass"
//                                                     : "result-fail"
//                                             }
//                                         >
//                                             {mark.result}
//                                         </div>

//                                     </div>

//                                     <div className="exam-details">

//                                         <div className="exam-detail">
//                                             <span>Total Marks</span>
//                                             <strong>{mark.total_marks}</strong>
//                                         </div>

//                                         <div className="exam-detail">
//                                             <span>Obtained Marks</span>
//                                             <strong>{mark.marks}</strong>
//                                         </div>

//                                         <div className="exam-detail">
//                                             <span>Percentage</span>
//                                             <strong>
//                                                 {percentage.toFixed(1)}%
//                                             </strong>
//                                         </div>

//                                     </div>

//                                 </div>
//                             );
//                         })}

//                     </div>

//                 </div>
//             ))}
//         </div>
//     );
// }

// export default Exams;


















import { useEffect, useState } from "react";
import { getMarks } from "../services/marksService";
import "./Exam.css";

function Exams() {
    const [marks, setMarks] = useState([]);
    const [expandedCourses, setExpandedCourses] = useState({});

    useEffect(() => {
        async function fetchMarks() {
            try {
                const response = await getMarks();
                setMarks(response.data.marks);
            } catch (error) {
                console.log(error);
            }
        }

        fetchMarks();
    }, []);

    const groupedCourses = marks.reduce((groups, mark) => {
        if (!groups[mark.course_id]) {
            groups[mark.course_id] = {
                course_code: mark.course_code,
                course_name: mark.course_name,
                course_status: mark.course_status,
                exams: []
            };
        }

        groups[mark.course_id].exams.push(mark);

        return groups;
    }, {});

    const toggleCourse = (courseId) => {
        setExpandedCourses((prev) => ({
            ...prev,
            [courseId]: !prev[courseId]
        }));
    };

    return (
        <div className="exams-container">

            <h1 className="exams-title">Exams & Marks</h1>

            {Object.entries(groupedCourses).map(([courseId, course]) => {

                const isRunning = course.course_status === "Running";

                // Running course is open by default.
                // Completed course is closed by default.
                const isExpanded =
                    isRunning || expandedCourses[courseId];

                return (
                    <div className="course-exam-section" key={courseId}>

                        {/* COURSE HEADER */}
                        <div
                            className="course-exam-header"
                            onClick={() => {
                                if (!isRunning) {
                                    toggleCourse(courseId);
                                }
                            }}
                        >
                            <div>
                                <div className="course-title">
                                    {course.course_code} - {course.course_name}
                                </div>

                                <div
                                    className={
                                        course.course_status === "Running"
                                            ? "course-status running"
                                            : "course-status completed"
                                    }
                                >
                                    {course.course_status === "Running"
                                        ? "🟢 Running Course"
                                        : "🔴 Completed Course"}
                                </div>
                            </div>

                            {/* Arrow only for completed courses */}
                            {!isRunning && (
                                <div className="course-arrow">
                                    {isExpanded ? "▲" : "▼"}
                                </div>
                            )}
                        </div>

                        {/* EXAMS */}
                        {isExpanded && (
                            <div className="exam-list">

                                {course.exams.map((mark, index) => {

                                    const percentage =
                                        (mark.marks / mark.total_marks) * 100;

                                    return (
                                        <div
                                            className="exam-card"
                                            key={index}
                                        >

                                            <div className="exam-header">

                                                <div>
                                                    <h2>
                                                        {mark.exam_name}
                                                    </h2>

                                                    <p>
                                                        Examination Result
                                                    </p>
                                                </div>

                                                <div
                                                    className={
                                                        mark.result === "Pass"
                                                            ? "result-pass"
                                                            : "result-fail"
                                                    }
                                                >
                                                    {mark.result}
                                                </div>

                                            </div>

                                            <div className="exam-details">

                                                <div className="exam-detail">
                                                    <span>
                                                        Total Marks
                                                    </span>

                                                    <strong>
                                                        {mark.total_marks}
                                                    </strong>
                                                </div>

                                                <div className="exam-detail">
                                                    <span>
                                                        Obtained Marks
                                                    </span>

                                                    <strong>
                                                        {mark.marks}
                                                    </strong>
                                                </div>

                                                <div className="exam-detail">
                                                    <span>
                                                        Percentage
                                                    </span>

                                                    <strong>
                                                        {percentage.toFixed(1)}%
                                                    </strong>
                                                </div>

                                            </div>

                                        </div>
                                    );
                                })}

                            </div>
                        )}

                    </div>
                );
            })}

        </div>
    );
}

export default Exams;