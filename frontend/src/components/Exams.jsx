import { useEffect, useState } from "react";
import { getMarks } from "../services/marksService";
import "./Exam.css";

function Exams() {

    const [marks, setMarks] = useState([]);

    useEffect(() => {

        async function fetchMarks() {

            try {

                const response = await getMarks();

                console.log(response.data);

                setMarks(response.data.marks);

            }

            catch (error) {

                console.log(error);

            }

        }

        fetchMarks();

    }, []);

    return (

        <div>

            <h1>
                Exams & Marks
            </h1>

            {

                marks.map((mark, index) => (

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

                        <div className="exam-row">

                            <span>
                                Exam
                            </span>

                            <span>
                                {mark.exam_name}
                            </span>

                        </div>

                        <div className="exam-row">

                            <span>
                                Total Marks
                            </span>

                            <span>
                                {mark.total_marks}
                            </span>

                        </div>

                        <div className="exam-row">

                            <span>
                                Obtained Marks
                            </span>

                            <span>
                                {mark.marks}
                            </span>

                        </div>

                        <div className="exam-row">

                            <span>
                                Percentage
                            </span>

                            <span>

                                {
                                    (
                                        mark.marks /
                                        mark.total_marks *
                                        100
                                    ).toFixed(1)
                                }%

                            </span>

                        </div>

                    </div>

                ))

            }

        </div>

    );

}

export default Exams;