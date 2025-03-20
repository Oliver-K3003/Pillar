import axios from "axios";
import { useNavigate } from "react-router-dom";

const GithubLogin = ({ setUser }) => {
    const navigate = useNavigate();

    function githubLoginRedirect() {
        console.log("Clicked GitHub login button, sending GitHub login request.");

        axios.get(`/api/login/github`)
            .then((response) => {
                if (response.data.status === "Successful") {
                    console.log(response.data.github_auth_code_url);
                    const popup = window.open(response.data.github_auth_code_url, "_blank", "width=500,height=800"); // Open login in popup.

                    const timer = setInterval(() => {
                        if (popup.closed) {
                            clearInterval(timer);

                            // Fetch user info on on successful login.
                            axios.get(`/api/github/user-info`)
                                .then((response) => {
                                    console.log(response.data.login);
                                    setUser(response.data.login);
                                })
                                .catch((error) => {
                                    console.log("Error getting user info. FETCH");
                                });
                        }
                    }, 500);

                } else {
                    console.log("Error within backend function /login/github")
                }
            })
            .catch((error) => {
                console.error("Axios error with request to /login/github");
            });
    }

    return (
        <div className="github-content">
            <p>Please login to begin using Pillar!</p>
            {/* Send request to backend to check if we're already logged in (ie. have token in this session.) */}
            <button onClick={githubLoginRedirect} className="github-login">Login Using GitHub</button>
        </div>
    )
}

export default GithubLogin;
