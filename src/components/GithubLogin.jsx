import axios from "axios";
import { useEffect, useState } from 'react';

const GithubLogin = () => {
  // Get return code to get token form GitHub.
  const urlParams = new URLSearchParams(window.location.search);
  const code = urlParams.get("code");
  const [data, setData] = useState(null);
  const [isDisabled, setIsDisabled] = useState(false);

  // useEffect(() => {
  //   console.log("useEffect() for 'code' variable.");
  //   const token = sessionStorage.getItem("githubToken");


  //   if (token) {
  //     console.log("Has token, getting authorization.");
  //     const token = sessionStorage.getItem("githubToken");
  //     axios.get("https://api.github.com/user", {
  //       headers: { Authorization: token },
  //     }).then((response) => {
  //       console.log(response.data);
  //     }).catch((error) => {
  //       console.error(error);
  //       console.log("token didn't work")
  //     });
  //   } else if (code) {
  //     console.log("Code: " + code);
  //     axios.get(`/api/exchange-code-for-token`, {
  //       params: {
  //         code: code,
  //         state: "YOUR_RANDOMLY_GENERATED_STATE",
  //       },
  //     }).then((response) => {
  //       const data = response.data;
  //       setData(data);
  //       sessionStorage.setItem("githubToken", `${data.token_type} ${data.access_token}`);
  //     }).catch((error) => {
  //       console.error("Axios Error:", error);
  //     })
  //   }
  // }, [code]);

  function githubLoginRedirect() {
    console.log("Clicked GitHub login button, sending GitHub login request.");

    axios.get(`/api/login/github`)
      .then((response) => {
        if (response.data.status === "Successful") {
          console.log(response.data.github_auth_code_url);
          // window.location.href = response.data.github_auth_code_url; // Redirects.
          const popup = window.open(response.data.github_auth_code_url, "_blank", "width=500,height=800"); // Open login in popup.

          let codeReceived = false;

          // Check to see if the code was successfully received by the backend.
          window.addEventListener("message", async (event) => {
            if (event.origin !== "http://localhost:5000") return; // Ensure the event is from our backend

            const { code } = event.data;
            if (code) {
              codeReceived = true;
              console.log("Received OAuth Code:", code);
              popup.close(); // Auto-close the popup

              // Exchange the code for an access token
              // fetchGitHubUser(code);
            }
          }, false);

          // Check to see if the 

        } else {
          console.log("Error within backend function /login/github")
        }
      })
      .catch((error) => {
        console.error("Axios error with request to /login/github");
      });
  }

  return (
    <>
      {/* Send request to backend to check if we're already logged in (ie. have token in this session.) */}
      <button onClick={githubLoginRedirect} className="github-login">Login Using GitHub</button>
    </>
  )
}

export default GithubLogin;
