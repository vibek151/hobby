import { useEffect, useState } from "react";
import { getPayments } from "../services/feeService";
import "./Payments.css";
function Payments() {
    const [payments, setPayments] = useState([]);
    useEffect(() => {
        async function fetchPayments() {
            try {
                const response = await getPayments();
                console.log("FULL RESPONSE =", response);
                console.log("DATA =", response.data);
                console.log("PAYMENTS =", response.data.payments);
                setPayments(
                    response.data.payments || []
                );
            }
            catch (error) {
                console.log(error);
            }
        }
        fetchPayments();
    }, []);
    return (
        <div>

            <div className="payment-title-row">

                <h1>
                    Payment History
                </h1>

                <button
                    className="statement-btn"
                    onClick={() =>
                        window.open(
                            `${import.meta.env.VITE_API_URL}/student/download-statement/`,
                            "_blank"
                        )
                    }
                >
                    Download Statement
                </button>

            </div>

            {

                payments.map(
                    (payment, index) => (

                        <div
                            className="payment-card"
                            key={index}
                        >

                            <div className="payment-header">

                                <h2>
                                    Payment #
                                    {payment.receipt_no}
                                </h2>

                                <div className="payment-status">
                                    Completed
                                </div>

                            </div>
                            <div className="payment-details">
                            <div className="payment-row">

                                <span>
                                    Due Date
                                </span>

                                <span>
                                    {payment.due_date}
                                </span>

                            </div>

                            <div className="payment-row">

                                <span>
                                    Payment Date
                                </span>

                                <span>
                                    {payment.date}
                                </span>

                            </div>

                            <div className="payment-row">

                                <span>
                                    Receipt No
                                </span>

                                <span>
                                    {payment.receipt_no}
                                </span>

                            </div>

                            <div className="payment-row">

                                <span>
                                    Type
                                </span>

                                <span>
                                    {payment.fee_type}
                                </span>

                            </div>

                            <div className="payment-row">

                                <span>
                                    Amount
                                </span>

                                <span>
                                    ₹{payment.amount}
                                </span>

                            </div>

                            <div className="payment-row">

                                <span>
                                    Fine
                                </span>

                                <span>
                                    ₹{payment.fine}
                                </span>

                            </div>

                            <div className="payment-row">

                                <span>
                                    Fine Waived
                                </span>

                                <span>
                                    {
                                        payment.fine_waived
                                            ? "Yes"
                                            : "No"
                                    }
                                </span>

                            </div>

                            <div className="payment-row">

                                <span>
                                    Total Amount
                                </span>

                                <span>

                                    ₹
                                    {
                                        payment.amount
                                        +
                                        payment.fine
                                    }

                                </span>

                            </div>

                            <div className="payment-row">

                                <span>
                                    Paid Via
                                </span>

                                <span>
                                    {payment.pay_via}
                                </span>

                            </div>
                            </div>
                        </div>

                    )

)

            }

        </div>

    );

}

export default Payments;