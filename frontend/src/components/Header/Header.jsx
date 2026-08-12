import { useEffect, useState } from "react";
import { getProfile } from "../../services/profileService";
import "./Header.css";

function Header() {

    const [profile, setProfile] = useState({});

    useEffect(() => {

        async function fetchProfile() {

            try {

                const response = await getProfile();

                console.log(response.data);

                setProfile(response.data);

            }

            catch(error){

                console.log(error);

            }

        }

        fetchProfile();

    }, []);

    useEffect(() => {

        console.log(profile.passport_photo);

    }, [profile]);

    return (

        <div className="header">

            <div className="header-left">

                <div className="header-title">

                    Welcome to {profile.franchise_name}

                </div>

                <div className="header-subtitle">

                    Smart Computer Institute Student Portal

                </div>

            </div>

            <div className="profile-card">

                <div className="student-info">

                    <div className="student-name">

                        {profile.name}

                    </div>

                    <div className="student-id">

                        {profile.student_id}

                    </div>

                </div>

                <img
                    src={profile.passport_photo}
                    className="student-avatar"
                    alt=""
                />

            </div>

        </div>

    );

}

export default Header;