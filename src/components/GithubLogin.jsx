import axios from "axios";

const GithubLogin = () => {

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
            }
          }, false);

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
