import { useEffect, useState } from "react";
import { getMarks } from "../../services/marksService";
import "../../components/Exams.css";

function Marks() {

    const [marks, setMarks] = useState([]);

    useEffect(() => {

        async function fetchMarks() {

            const response = await getMarks();

            setMarks(response.data.marks);

        }

        fetchMarks();

    }, []);

    return (

        <div className="exam-container">

            <h1>Exams & Marks</h1>

            {

                marks.map((mark, index) => (

                    <div
                        className="marks-card"
                        key={index}
                    >

                        <div className="marks-header">

                            <div>

                                <h2>
                                    {mark.exam}
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

                        <div className="marks-body">

                            <div className="marks-row">

                                <span>
                                    Total Marks
                                </span>

                                <span>
                                    {mark.total_marks}
                                </span>

                            </div>

                            <div className="marks-row">

                                <span>
                                    Obtained Marks
                                </span>

                                <span>
                                    {mark.obtained_marks}
                                </span>

                            </div>

                            <div className="marks-row">

                                <span>
                                    Percentage
                                </span>

                                <span>

                                    {
                                        (
                                            mark.obtained_marks /
                                            mark.total_marks *
                                            100
                                        ).toFixed(1)
                                    }%

                                </span>

                            </div>

                        </div>

                    </div>

                ))

            }

        </div>

    );

}

export default Marks;