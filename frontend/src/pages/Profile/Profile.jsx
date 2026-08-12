import { useEffect, useState } from "react";
import { getProfile } from "../../services/profileService";

function Profile() {

    const [student, setStudent] = useState(null);

    useEffect(() => {

        async function fetchProfile() {

            try {

                const response = await getProfile();

                setStudent(
                    response.data
                );

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

        <div>

            <h1>Profile</h1>

            <hr />

            <p>
                Name : {student.name}
            </p>

            <p>
                Student ID : {student.student_id}
            </p>

            <p>
                Course : {student.course}
            </p>

            <p>
                Email : {student.email}
            </p>

            <p>
                Phone : {student.phone}
            </p>

            <p>
                Date of Birth : {student.dob}
            </p>

        </div>

    );

}

export default Profile;